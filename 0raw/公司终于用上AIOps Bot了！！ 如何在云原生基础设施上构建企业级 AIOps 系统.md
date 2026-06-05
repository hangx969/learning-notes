---
title: 公司终于用上AIOps Bot了！！ 如何在云原生基础设施上构建企业级 AIOps 系统
source: https://mp.weixin.qq.com/s/SVZeFOX-0u1jKmuRCRXNHA
author:
  - "[[HAI]]"
published:
created: 2026-06-05
description:
tags:
  - clippings
---
HAI *2026年4月17日 19:57*

欢迎点击下方👇关注我，记得星标哟~

文末会有 **重磅福利** 赠送

## 一、背景与动机

随着云原生基础设施规模的扩张，运维团队面临的挑战已不再是"能不能监控"，而是"能不能在海量告警和日志中快速找到真正的问题"。当你管理着跨越多个云区域、超过 20 个 Kubernetes 集群、数十个租户的生产环境时，传统的"人盯屏幕"模式已经无法持续。

这篇文章记录了我们团队从零开始设计并落地一套 AIOps 系统的完整历程——它不是一个购买来的产品，而是一套深度融合了 AI 推理、可观测性数据和运维工作流的自研系统。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/JeOXF0KWN2LKz3g6rmXzXyjxYsoRuHbCv7AknKKAsk4pW6GxqX5icXtlIavmnUNEgiawBlOibh2D3yE26Koib2j12227Zic8keLClelxtia1wJdPw/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

---

## 二、核心设计原则

在动手写第一行代码之前，我们确立了几条不可妥协的原则：

**1\. 人始终是决策者**  
AI 提供诊断和证据，但不自主执行任何变更。每一个操作都需要人工确认。这不是技术限制，而是设计选择——在合规审计（HITRUST、SOC2）环境下，可追溯性比自动化更重要。

**2\. 理解优先于自动化**  
系统的目标是提升工程师对问题的理解，而不是绕过他们。AI 应该像一个经验丰富的同事，帮你快速定位问题，而不是一个黑盒子。

**3\. 诊断，不建议修复**  
Claude 的系统提示中有明确的"NEVER"规则：只呈现证据和发现，绝不建议具体的修复操作。这避免了 AI 在不了解完整上下文时给出危险建议。

**4\. 上下文持续验证**  
基础设施在不断变化，AI 的知识库也必须随之更新。所有领域知识文件都是"活文档"，发现偏差时必须更新。

---

## 三、系统架构：两层分布式设计

### 3.1 架构演进

我们最初的设计是一个中心化的单体 Bot，部署在管理集群上，通过 Grafana API Token 跨集群查询各站点的 Prometheus/Loki/Tempo 数据。这个方案很快暴露了问题：

- • 每个站点需要单独管理 Grafana Service Account Token
- • 跨集群认证复杂（Entra ID、kubeconfig 管理）
- • 外部网络延迟影响查询性能
- • 随着站点增加，维护成本线性增长

**最终方案：两层架构**

```
Slack (Socket Mode)
        │
        ▼
┌─────────────────────────────┐
│   Coordinator               │  ← 管理集群
│   - Slack 监听              │
│   - 告警同步 (OnCall API)   │
│   - Claude AI 推理          │
│   - 事件追踪 (PostgreSQL)   │
│   - 路由到站点 Agent        │
└──────────────┬──────────────┘
               │ HTTP API
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 站点 Agent  站点 Agent  站点 Agent
 (集群内部)  (集群内部)  (集群内部)
 - Prometheus  - Prometheus  - Prometheus
 - Loki        - Loki        - Loki
 - Tempo       - Tempo       - Tempo
 - K8s API     - K8s API     - K8s API
```

**关键洞察** ：把 Agent 部署到每个集群内部，就彻底消除了跨集群认证问题。Agent 通过 ServiceAccount RBAC 访问集群内部服务，无需任何外部 Token。

### 3.2 Coordinator（协调器）

部署在管理集群，职责单一且明确：

- • **Slack Socket Mode** ：一个 WebSocket 连接处理所有用户交互（不能有多个实例）
- • **OnCall 同步** ：每 60 秒从告警管理系统拉取当前触发的告警
- • **Claude AI 推理** ：接收用户问题，调用工具，生成诊断报告
- • **事件追踪** ：维护活跃事件列表，关联 Jira 工单
- • **Agent 注册中心** ：维护所有在线站点 Agent 的实时注册表

### 3.3 站点 Agent（Site Agent）

通过 ArgoCD ApplicationSet 部署到每个生产集群，同一个 Docker 镜像，通过环境变量区分模式：

```
# ApplicationSet 模板片段
- name: BOT_AGENT_MODE
  value: "true"
- name: BOT_AGENT_SITE_NAME
  value: "{{ .name }}"
- name: BOT_COORDINATOR_URL
  value: "https://coordinator.internal/api/ai-ops"
```

Agent 启动后每 60 秒向 Coordinator 注册心跳，Coordinator 维护动态注册表，超过 5 分钟未心跳的 Agent 自动下线。这样新增站点时，只需给集群打上标签，ApplicationSet 自动部署 Agent，无需修改 Coordinator 配置。

---

## 四、可观测性数据层

### 4.1 全栈可观测性

每个站点运行完整的可观测性栈：

| 工具 | 用途 | 保留期 |
| --- | --- | --- |
| Prometheus | 实时指标采集 | 5 小时 |
| Thanos | 长期指标存储（Azure Blob） | 数月 |
| Loki | 日志聚合 | 可配置 |
| Tempo | 分布式追踪 | 可配置 |
| Pyroscope | 持续性能剖析 | 可配置 |
| Grafana Alloy | OpenTelemetry 采集器 | N/A |

**一个重要的细节** ：Prometheus 只保留 5 小时数据。所有历史调查必须查询 Thanos，两者使用完全相同的 PromQL 语法，只是端点不同。这个细节如果不在 AI 的上下文中明确说明，Claude 会默认查询 Prometheus 而得到空结果。

### 4.2 调查顺序的重要性

我们在系统提示中强制规定了调查顺序：

```
Exemplars → Tempo Traces → Loki（带 Trace ID，最多 5 分钟窗口）
```

这个顺序不是随意的。Exemplars 提供指标到 Trace 的桥梁，Tempo 给出请求链路，Loki 提供精确的错误日志。直接跳到 Loki 全文搜索往往会超时或返回噪音。

---

## 五、AI 推理层

### 5.1 工具设计

Claude 通过工具调用访问所有数据源，我们定义了 13 个工具：

**告警与事件类**

- • `get_firing_alerts` — 获取当前触发的告警
- • `get_alert_detail` — 告警详情
- • `search_alerts` — 搜索历史告警
- • `acknowledge_alert` — 确认告警
- • `get_active_incidents` — 活跃事件列表
- • `get_incident_detail` — 事件详情

**指标类**

- • `prometheus_query` — 即时 PromQL 查询
- • `prometheus_query_range` — 范围查询
- • `prometheus_exemplars` — 获取 Exemplar 数据

**追踪类**

- • `tempo_search` — 搜索 Trace
- • `tempo_get_trace` — 获取 Trace 详情

**日志类**

- • `loki_query` — LogQL 查询

### 5.2 领域上下文注入

这是整个系统最关键的设计决策之一。Claude 本身不了解我们的业务系统，我们通过"Skills"机制将领域知识注入到系统提示中：

```
bot/context/
├── skills/
│   ├── app-troubleshooting/     # app 系统诊断
│   ├── zeebe-troubleshooting/    # Zeebe 工作流引擎
│   ├── kafka-troubleshooting/    # Kafka 消息队列
│   ├── rabbitmq-troubleshooting/ # RabbitMQ
│   ├── site-troubleshooting/     # 站点健康诊断
│   └── system-capacity-check/   # 容量分析
└── reference/
    ├── promql-patterns.md        # 常用 PromQL 模式
    └── logql-patterns.md         # 常用 LogQL 模式
```

每个 Skill 包含四个文件： `SKILL.md` （概述）、 `methodology.md` （方法论）、 `context.md` （领域知识）、 `troubleshooting.md` （常见问题）。

**关键实践** ：在调用 Claude 之前，系统会自动查询 Jira，将已知问题注入到提示中。这避免了 Claude 重复调查已知问题，也让它能将当前告警与历史事件关联。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

### 5.3 对话历史

每个 Slack 线程维护独立的对话历史，用户可以追问：

```
用户: @AI Ops Bot investigate mt-norway-east 内存告警
Bot: [分析结果，7 步，19 次工具调用，51 秒]

用户: 这个问题上周也发生过吗？
Bot: [基于对话历史，继续查询历史数据]
```

---

## 六、GitOps 与变更管理

### 6.1 所有变更通过 Git

应用配置存储在 Git 仓库中，ArgoCD 监听变更并同步到集群：

```
Git 提交 → ArgoCD 检测（1-3 分钟）→ 开始同步 → Pod 滚动更新（2-5 分钟）
```

这意味着 AI 建议的任何配置变更，都必须经过：Branch → Commit → MR → Review → Merge 的完整流程。没有例外，包括紧急情况。

### 6.2 Workflow 即代码

我们将所有运维操作流程编写为 Markdown 格式的 Workflow 文件，AI 在执行任何操作前必须引用对应的 Workflow：

```
.windsurf/workflows/
├── git.md              # Git 操作规范
├── change-management.md # 变更管理流程
├── scale-application.md # 应用扩缩容
├── scale-nodepool.md   # 节点池扩缩容
├── decommission-site.md # 站点下线
└── jira.md             # Jira 工单操作
```

---

## 七、部署与运维

### 7.1 镜像构建流水线

```
代码提交 → TeamCity CI（Cake 构建）→ Docker 多阶段构建 → ACR
                                      ├── base
                                      ├── unittest-runner (ruff + pytest)
                                      └── app-production
```

多阶段构建确保生产镜像不包含测试依赖，同时 CI 阶段强制运行 lint 和测试。

### 7.2 ArgoCD ApplicationSet 大规模部署

通过 ApplicationSet，一个配置模板覆盖所有站点：

```
generators:
  - clusters:
      selector:
        matchLabels:
          ai-ops-bot: "true"  # 只部署到打了标签的集群
template:
  spec:
    source:
      helm:
        values: |
          config:
            BOT_AGENT_SITE_NAME: "{{ .name }}"
            BOT_COORDINATOR_URL: "https://coordinator.internal"
            BOT_AGENT_MODE: "true"
```

新增站点只需给集群打标签，Agent 自动部署，自动注册到 Coordinator。

### 7.3 Secrets 管理

所有敏感配置通过 SOPS 加密存储在 Git 中，ArgoCD 解密后挂载为 Kubernetes Secret，再以文件形式挂载到 Pod：

```
/etc/secrets/BOT_SLACK_BOT_TOKEN
/etc/secrets/BOT_CLAUDE_API_KEY
/etc/secrets/BOT_ONCALL_TOKEN
```

### 7.4 关键运维细节（踩坑记录）

这些是我们在生产中学到的教训，每一条都有代价：

- • **Loki 查询超时** ：最大窗口 5 分钟。必须先用 Trace ID 缩小范围，再查 Loki
- • **Slack 消息长度限制** ：Claude 的调查报告经常超过 4000 字符，必须拆分为线程回复
- • **存活探针与长时间调查的冲突** ：Claude 调查可能需要 60+ 秒，需要将 `failureThreshold` 设为 10， `periodSeconds` 设为 30，给 5 分钟容忍窗口
- • **OnCall 静默 API** ：不能静默已确认的告警，必须先取消确认
- • **Jira API 变更** ： `/rest/api/3/search` 已废弃，必须使用 `/rest/api/3/search/jql`
- • **不要依赖 Claude 主动调用特定工具** ：Jira 预检查必须在代码层面强制执行，注入到提示中

---

## 八、Slack 交互界面

用户通过 Slack 与系统交互，命令设计简洁直观：

```
@AI Ops Bot status          → 当前触发告警（带图标）
@AI Ops Bot alerts          → 告警列表
@AI Ops Bot incidents       → 活跃事件（带 Jira 链接）
@AI Ops Bot ack <关键词>    → 确认匹配的告警
@AI Ops Bot silence <关键词> <时长>  → 静默告警
@AI Ops Bot investigate <主题>       → 触发 AI 调查
任意自由文本                → 默认触发 AI 调查
```

**频道规则** ： `#incidents` 频道只发简短确认，不发调查详情（这是面向管理层的频道）。详细调查结果发到 `#alerts` 或 `#cloudops` 频道。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

---

## 九、规划中的能力

### Phase 7：Kubernetes API 工具

在站点 Agent 上增加 K8s API 直接访问能力，让 Claude 能查询 Pod 状态、Events、HPA、节点资源等，替代原本计划引入的 k8sgpt（最终因为双重 AI 成本和维护复杂度而放弃）。

### Phase 8：SQL Extended Events

通过 Azure Blob Storage 接入 SQL 扩展事件（死锁、阻塞、错误），让 Claude 在调查数据库相关告警时能直接分析 SQL 层面的证据。

### 持久化上下文

站点 Agent 重启后会丢失对话历史。计划通过 PostgreSQL（由 postgres-operator 管理，与其他 AI Agent 共享）实现跨重启的持久化上下文。

---

## 十、经验总结

**什么有效**

- • **两层架构** 彻底解决了跨集群认证问题，是整个项目最重要的架构决策
- • **领域上下文注入** 让通用 AI 模型具备了专业运维能力，效果远超预期
- • **诊断而非修复** 的设计原则在实际使用中获得了团队的信任
- • **ArgoCD ApplicationSet** 让大规模部署变得可维护

**什么需要注意的**

- • AI 的上下文窗口是有限的，领域知识文件需要精心设计，避免冗余
- • 工具调用的顺序和约束必须在系统提示中明确规定，不能依赖模型自行判断
- • 合规环境下，变更管理流程不能因为有了 AI 而简化，反而需要更严格的审计追踪
- • 从 SQLite 到 PostgreSQL 的迁移应该在早期就规划好，而不是等到规模扩大后再处理

**一个反直觉的发现**

我们最初计划引入 k8sgpt（一个专门用于 Kubernetes 诊断的 AI 工具），最终放弃了。原因是：当 Claude 已经能访问 Prometheus 指标、Loki 日志、Tempo 追踪，并且注入了 15 个领域知识文件时，它对 Kubernetes 问题的诊断能力已经超过了 k8sgpt。引入第二个 AI 工具只会增加成本和复杂度，而不会带来额外价值。

---

## 结语

构建 AIOps 系统不是一个技术问题，更是一个信任问题。工程师需要相信 AI 的诊断是基于真实数据的，管理层需要相信变更管理流程没有被绕过，合规团队需要相信每一个操作都有审计追踪。

我们的系统在设计上把这些约束放在第一位，技术实现反而是相对容易的部分。如果你正在考虑类似的项目，建议从明确"AI 能做什么、不能做什么"开始，而不是从选择技术栈开始。

---

重磅！！

公众号配套学习网站已经上线，欢迎大家体验：https://k8s.sredevops.top/

##### 往期回顾

[K8S工具推荐，Kargo：下一代 GitOps 持续交付工具](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485786&idx=1&sn=2935d0620bb8aabfcf8b228541254345&scene=21#wechat_redirect)

[K8S工具推荐：Bufstream-唯一通过 Jepsen 验证的云原生 Kafka 实现](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485772&idx=1&sn=f07b285db613820003387aae95cedcd1&scene=21#wechat_redirect)

[K8S工具推荐： 使用 Kubemark 进行 Kubernetes 大规模集群模拟实践](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485727&idx=1&sn=65c3d50d36899a805c87c17ca650a010&scene=21#wechat_redirect)

[K8S工具推荐：使用Argo Rollouts实现GitOps自动化测试与回滚](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485755&idx=1&sn=50463bc31bb2610d18a843881b1515ac&scene=21#wechat_redirect)

[K8S工具推荐：资源编排新利器：三大云厂商联合推出 KRO](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485719&idx=1&sn=cc7fe428cb840c21576129d48986b70e&scene=21#wechat_redirect)

[K8S工具推荐：告别复杂认证！Kubernetes登录神器kubelogin指南](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485698&idx=1&sn=47443ce3322a407525cd6ccdffbffb29&scene=21#wechat_redirect)

[K8S工具推荐：Kubernetes资源优化神器KRR：一键诊断集群资源浪费](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485685&idx=1&sn=6ced5d257f3c3e93383a63ef6802edaf&scene=21#wechat_redirect)

[Kubernetes工具推荐：使用 k8s-pod-restart-info-collector简化故障排查](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485663&idx=1&sn=c0f05332e39e5b59793afd2a82326f55&scene=21#wechat_redirect)

[K8S工具推荐：动态无缝的Kubernetes多集群解决方案-Liqo](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485739&idx=1&sn=cd7e35bbf22ca3077fbec318bb714d00&scene=21#wechat_redirect)

[如何落地一个企业级PaaS容器云平台：从规划到实施全流程指南](https://mp.weixin.qq.com/s?__biz=MzkxNzAyMzA3Nw==&mid=2247485778&idx=1&sn=bc4e23d618f19a7656c8540456ff752e&scene=21#wechat_redirect)

收录于AIOps

继续滑动看下一个

云原生SRE

向上滑动看下一个