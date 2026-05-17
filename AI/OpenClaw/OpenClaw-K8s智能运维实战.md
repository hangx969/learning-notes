---
title: "用 OpenClaw 智能体网关接管 K8s 日常运维：从只读巡检到低风险变更"
source: "https://mp.weixin.qq.com/s/LYGGzLyVattT_sAmQDUHeQ"
created: 2026-05-17
tags:
  - OpenClaw
  - kubernetes
  - AIOps
  - OPA
---

> 凌晨 2 点，AI 在钉钉上问我："检测到 recommend-engine 内存持续飙升，历史相似案例修复成功率 97%，是否允许我执行 patch？"我迷迷糊糊回了个"同意"，然后翻个身继续睡了。第二天看报告，AI 在 3 分钟内完成了诊断、调整、验证全流程——而我，全程只说了一个词。

2026 年的今天，用 OpenClaw 智能体网关，让 AI 从一个"只读巡检员"变成了能执行低风险变更的运维助手。

## 一、架构全景：OpenClaw 作为 K8s 运维中枢

OpenClaw 的核心价值是充当 AI 与 K8s API 之间的双向桥梁——AI 通过它执行命令，它负责安全护栏、审计日志、权限分级。

四层架构：

1. **交互层**：SRE 通过钉钉、Slack 或 Web 界面与 AI 对话，自然语言进去，结果出来
2. **网关层**：大脑（理解意图、拆解任务、调度 Skill）+ 刹车（OPA 策略、权限检查）。所有 AI 动作必经此层
3. **Skill 层**：封装的运维能力，每个 Skill 有明确的输入输出规范和权限声明
4. **K8s 层**：目标集群，通过专用 ServiceAccount 隔离权限

![image.png](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260517230737431.png)


## 二、三阶段渐进：从"只读"到"变更"

渐进路线：先让 AI 证明"看得懂"，再开放"改得动"。每个阶段持续 3-4 周，经过充分验证后才进入下一阶段。

### 2.1 只读巡检（第 1-4 周）——建立信任

**目标：** 让 AI 学会"看懂"集群状态，不产生任何副作用。

**权限范围：**

- get、list、watch 所有命名空间的 Pod、Deployment、Service、Event
- 查询 Prometheus 指标、Loki 日志的只读 API
- 没有任何写操作权限

Skill 设计示例：

~~~yaml
name: health_check
description: "巡检指定命名空间的健康状态"
permission: READ_ONLY
parameters:
  - namespace: string
  - time_range: string (default: 1h)
prompt: |
  你是一个SRE助手。请查询namespace={namespace}在过去{time_range}内的以下信息：
  1. 非Running状态的Pod及其原因
  2. 重启次数>3的Pod
  3. CPU/内存使用率超过80%的Pod
  4. 最近的Warning级别Event
  
  用表格形式输出结果，并标注需要关注的高风险项。
~~~

效果数据：

| 周次 | 准确率 | 说明 |
| --- | --- | --- |
| 第 1 周 | 78% | 漏报+误报较多 |
| 第 2 周 | 85% | 通过人工纠正优化 |
| 第 4 周 | 92% | 达到上线标准 |

**关键经验：教会 AI 看病的，是 SRE 自己——每次纠正都是训练数据。**

### 2.2 诊断助理（第 5-8 周）——人机协同

**目标：** AI 可以深入排查问题，给出诊断结论和修复建议，但写操作仍需人工确认。

**权限范围：** 保持只读，但增加了复杂数据访问（事件历史、资源趋势图、跨 Pod 关联分析）。

诊断输出示例：

~~~text
【诊断报告】Pod: recommend-engine-7d8f-xyz

【现象】
- 状态: CrashLoopBackOff (已重启8次)
- 最后退出码: 137 (OOMKilled)

【数据摘要】
- 当前memory limit: 512Mi
- 过去7天内存峰值: 687Mi (超出limit 34%)
- 相关Event: "Container was killed due to memory limit"

【根因判断】
✅ 内存限制不足 (置信度: 92%)
❌ 内存泄漏 (置信度: 18% - 无持续增长模式)

【建议操作】
kubectl patch deployment recommend-engine -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","resources":{"limits":{"memory":"1024Mi"}}}]}}}}'
⚠️ 风险等级: 低 (滚动更新，业务无中断)

是否执行？
~~~

效果数据：

- SRE 从"排查者"变为"审核者"
- 平均排查时间：25 分钟 → 5 分钟（下降 80%）
- 诊断准确率：94%（人工复核确认）

### 2.3 低风险变更（第 9 周至今）——审慎开放

**目标：** 对于标准化、低风险的操作，允许 AI 直接执行。

**权限范围：**

- 允许：patch Deployment 的 resources、restart Deployment、scale replicas（限制范围内）
- 禁止：DELETE 操作、修改 NetworkPolicy、修改 RBAC、删除 PVC
- 要求：所有操作必须有审计日志和变更原因

OPA 护栏策略：

~~~rego
# Open Policy Agent 策略示例
package k8s.agent

# 黑名单操作：永远拒绝
deny[msg] {
    input.operation == "DELETE"
    msg = "AI不允许执行DELETE操作"
}

deny[msg] {
    input.resource == "networkpolicy"
    msg = "NetworkPolicy变更需人工操作"
}

deny[msg] {
    input.resource == "persistentvolumeclaim"
    msg = "PVC删除操作需人工操作"
}

# 配额变更需要验证范围
deny[msg] {
    input.resource == "deployment"
    input.field == "resources.limits.memory"
    new_value = input.new_value
    old_value = input.old_value
    new_value > old_value * 2
    msg = sprintf("内存调整幅度过大，需人工审批。当前请求将limit从%v调整至%v", [old_value, new_value])
}

# 副本数变更需要验证上限
deny[msg] {
    input.resource == "deployment"
    input.field == "replicas"
    new_value = input.new_value
    new_value > 5
    msg = sprintf("副本数超过上限(5)，当前请求: %v", [new_value])
}

# 速率限制：同一资源每小时最多操作1次
deny[msg] {
    count(same_resource_ops_in_last_hour) >= 1
    msg = "同一资源1小时内只能操作1次，请稍后再试"
}

# 允许通过的条件
allow {
    input.operation == "PATCH"
    input.resource in {"deployment", "statefulset"}
    input.field in {"resources.limits.memory", "resources.requests.cpu", "replicas"}
    not deny[_]
}
~~~

实际运行数据（3 个月累计）：

| 操作类型 | 执行次数 | 成功率 | 人工介入次数 |
| --- | --- | --- | --- |
| 内存 limit 调整 | 47 | 100% | 0 |
| Deployment 重启 | 23 | 100% | 0 |
| 副本数扩缩容 | 86 | 98.8% | 1（上限触达） |
| 合计 | 156 | 99.4% | 1 |

零安全事故——不是运气，是护栏足够密。

## 三、实战案例：60 秒完成诊断+修复

### 3.1 场景

某核心服务的 Pod 因健康检查失败反复重启，影响约 3% 的请求。

### 3.2 用户触发

SRE 在钉钉群里发了一条：

> /ai diagnose recommend-engine -n production

### 3.3 OpenClaw 意图识别

网关识别关键词 diagnose，匹配到 diagnosis Skill，提取参数 pod=recommend-engine，namespace=production。

### 3.4 AI 自主诊断链执行

| 步骤 | 操作 | 发现 |
| --- | --- | --- |
| 1 | kubectl get pod | 状态 Running 但 RESTARTS=8 |
| 2 | kubectl describe pod | Liveness probe failed 事件 |
| 3 | kubectl logs --previous | 应用启动需 45 秒 |
| 4 | 查看当前探针配置 | initialDelaySeconds=30 |
| 5 | 检索历史案例库 | 过去 30 天 3 次相同问题 |

### 3.5 输出诊断报告

~~~text
【诊断结果】
根因: livenessProbe.initialDelaySeconds=30s，应用实际启动需45s
建议: 将initialDelaySeconds调整为60s
修复命令: kubectl patch deployment recommend-engine --type='strategic' \
  -p='{"spec":{"template":{"spec":{"containers":[{"name":"app","livenessProbe":{"initialDelaySeconds":60}}]}}}}'
风险等级: 低（滚动更新，业务无中断）
是否执行？
~~~

### 3.6 人工确认后执行

SRE 回复"执行" → OpenClaw 调用 K8s API 执行 patch → 滚动更新触发 → 新 Pod 正常启动

耗时统计：

| 环节 | 耗时 |
| --- | --- |
| AI 诊断 | 35 秒 |
| 人工确认 | 10 秒 |
| 执行生效 | 15 秒 |
| **总计** | **60 秒** |

而以前人工排查这个问题大概需要 15 分钟——先怀疑代码、再看配置、最后才发现是探针的问题。效率提升 15 倍。

## 四、总结

AI Agent 不是来抢饭碗的。它把 SRE 从"低价值的重复劳动"中解放出来，让人有机会去做那些真正需要人脑的事情——架构设计、容量规划、故障复盘、知识沉淀。

**渐进式信任建立：**

| 阶段 | 周期 | AI 能力 | 人工角色 |
| --- | --- | --- | --- |
| 只读巡检 | 第 1-4 周 | 看懂集群状态 | 纠正+训练 |
| 诊断助理 | 第 5-8 周 | 排查+建议 | 审核+确认 |
| 低风险变更 | 第 9 周起 | 自主执行标准操作 | 设计护栏+处理复杂问题 |

关键原则：**从只读开始，给 AI 一个月时间证明自己。**
