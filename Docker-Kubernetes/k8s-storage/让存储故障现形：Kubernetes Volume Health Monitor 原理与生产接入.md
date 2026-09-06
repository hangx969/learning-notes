---
title: 让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入
tags:
  - kubernetes
  - storage/volume-health
  - kubernetes/storage
  - observability
aliases:
  - Kubernetes Volume Health Monitor
  - Volume Health Monitor
date: 2026-09-06
sources:
  - "[[0raw/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入]]"
---

# 让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入

## 一、开头：PVC 一直 Bound，但业务已经卡死半小时

存储故障是 Kubernetes 里最「阴险」的一类问题。一个 PV 后端其实是云盘，底层存储节点抖动、卷降级、甚至静默损坏，Kubernetes 侧看到的 `PersistentVolumeClaim` 状态却永远是 `Bound` ——因为 K8s 从来没有任何机制让 CSI 驱动「上报存储健康」。结果就是：应用 I/O 卡住、超时、报错，你却只能去翻云厂商控制台或存储阵列 dashboard 交叉比对，才能定位「哦，是那块盘出问题了」。在一次真实故障里，oncall 在三个系统之间来回切换了半个多小时才锁定根因，而那块卷从头到尾在 K8s 里都显示「正常」。这种黑盒，正是 Volume Health Monitor 要打破的。

这个问题社区盯了很久（KEP-1432 最早在 1.21 就有实现尝试），但在 1.37 它被 **重新推进到 Alpha** ，并带来了 4 个全新的 CSI RPC，让存储健康第一次成为「机器可读、可告警、可联动」的集群一等信号。本文讲清它的原理、如何接入，以及生产落地的注意点。

## 二、原理讲解：四个 CSI RPC 把健康搬进 API 对象

Volume Health Monitor 的设计哲学是：存储健不健康，只有 CSI 驱动（也就是存储后端）最清楚，所以让 **驱动来报** ，kubelet 和控制平面来 **收集并结构化** 。

它定义了 4 个 CSI RPC，分两端：

**控制器侧（Controller 插件上报，写入 PVC 状态）：**

- `ControllerListVolumeHealth` ：列出所有不健康的卷。
- `ControllerGetVolumeHealth` ：查询某个具体卷的健康。

收集结果写入 **`PersistentVolumeClaim.status.healthStatus`** ，字段包含 `status` （如 `Inaccessible` 、 `Degraded` 、 `Healthy` ）、 `reason` 、 `message` 。

**节点侧（kubelet 调用，写入更细粒度状态）：**

- `NodeGetVolumeHealth` ：获取该节点上某个具体卷的健康，写入 **`Pod.status.volumeHealth`** 。
- `NodeGetStorageHealth` ：获取该节点上注册的驱动整体健康，写入 **`CSINode.status.storageHealth`** 。

错误词汇保持简单、可扩展、可机器解析： `Inaccessible` （不可访问）、 `Degraded` （降级但仍可用）等，厂商可在 `reason` / `message` 里给更细的说明。

设计上，控制器侧与节点侧的报告 **相互独立、分开展示** ——这很重要，因为「卷在控制器看来健康，但某个节点上挂载点坏了」是完全可能的，两者视角互补才能拼出完整画面。

## 三、实战配置：启用与读取健康信号

**第一步：在 API Server 与 kubelet 开启 feature gate（1.37 Alpha）。**

```
# kube-apiserver / kube-controller-manager
--feature-gates=VolumeHealthMonitor=true

# kubelet
--feature-gates=VolumeHealthMonitor=true
```

**第二步：CSI 驱动需实现对应 RPC。** 并非所有驱动都支持。确认你的存储驱动版本实现了 `ControllerListVolumeHealth` / `NodeGetVolumeHealth` 等。主流云盘 CSI（如 AWS EBS、GCP PD、Azure Disk 的新版）与部分企业存储已陆续支持；社区 `hostpath` 等示例驱动通常不含此能力。

**第三步：读取健康状态。** 控制器侧结果直接看 PVC：

```
kubectl get pvc data-vol -o jsonpath='{.status.healthStatus}'
# 示例输出：
# {"status":"Degraded","reason":"volume_latency_high","message":"p99 latency > 200ms"}
```

节点侧结果看 Pod：

```
kubectl get pod app-0 -o jsonpath='{.status.volumeHealth}'
```

**第四步：把健康接入监控告警。** 用 Prometheus 抓取 kube-controller-manager / kubelet 暴露的相关指标（或通过自定义 exporter 把 `healthStatus` 转成 gauge），示例告警思路：

```
# PromQL 思路：PVC 健康非 Healthy 即告警
expr: |
  kube_pvc_health_status{status!="Healthy"} == 1
# 或更稳妥：基于 controller 暴露的 volume_health 指标
```

并在 GitOps/ remediation controller 中监听 `healthStatus` ，对 `Inaccessible` 的 PVC 触发自动迁移（如删 Pod 让其调度到健康节点、或触发存储故障切换）。

## 四、生产环境注意事项

1. **Alpha 成熟度预期。** 1.37 是 Alpha，API 字段与行为可能在后续版本变动， **不要把它作为唯一的故障判定依据** ，应与存储厂商自身的监控互为补充。
2. **驱动支持是前提。** 若你的 CSI 驱动没实现这 4 个 RPC，开了 feature gate 也不会有任何 `healthStatus` 出现。上线前务必在测试集群用 `kubectl get pvc -o yaml` 验证字段是否真的被填充。
3. **告警分级。** `Degraded` 不等于 `Inaccessible` 。建议： `Degraded` 走警告级（工单）， `Inaccessible` 走紧急级（电话），避免告警风暴。
4. **与 remediation 联动要谨慎。** 自动把「卷不健康」的 Pod 删掉重调度，有可能把问题转移到别的节点，甚至扩大影响。联动逻辑要带冷却与最大重试次数。
5. **别忘了节点侧视角。** 只看 `PVC.status.healthStatus` （控制器侧）会漏掉「卷本身健康、但某节点挂载点坏了」的情况，务必同时消费 `Pod.status.volumeHealth` 与 `CSINode.status.storageHealth` 。

## 五、踩坑实录

- **坑 1：开了 gate 但 PVC 字段永远是空。** 排查一通发现是 CSI 驱动版本太老，根本没实现 `ControllerListVolumeHealth` 。修复：升级驱动到支持该 RPC 的版本，并在测试集群先验证字段填充。
- **坑 2：Alpha 字段名中途变更导致 exporter 报错。** 1.37 的 Alpha 实现里 `healthStatus` 的结构在早期候选版和 RC 间有过调整，我们的自研 exporter 用硬编码 JSONPath 解析直接挂掉。教训：Alpha 特性不要写死解析，加容错与版本判断。
- **坑 3： `Degraded` 误报告警淹没值班。** 某存储驱动把「轻微延迟抖动」也报成 `Degraded` ，结果每天几百条告警。修复：在告警层对 `reason` 做白名单，只把 `volume_latency_high` 等真正影响业务的 reason 升级为紧急。
- **坑 4：自动 remediation 把问题放大。** 监控到 PVC `Inaccessible` 后，自动化控制器立刻删 Pod，结果新 Pod 调度回同一 degraded 存储后端，循环崩溃。修复：remediation 改为「先隔离该存储后端 + 通知人工确认故障切换」，而非无脑重建。
- **坑 5：只盯 PVC 漏掉节点挂载点故障。** 一次某节点 kubelet 与存储阵列网络分区，PVC 控制器侧显示 Healthy，但 Pod 在该节点上 I/O 全挂。后来补齐 `Pod.status.volumeHealth` 监控才捕获。教训：控制器侧与节点侧必须一起看。

## 七、端到端告警链路搭建

把「存储健康」从 API 对象变成可行动的告警，需要一条完整链路：

1. **采集** ：kube-controller-manager 暴露的 volume 健康指标，或自写 exporter 把 `PVC.status.healthStatus` / `Pod.status.volumeHealth` 转成 Prometheus gauge（如 `kube_volume_health{status="Degraded"}` ）。
2. **分级告警** ： `Degraded` → warning 级工单； `Inaccessible` → critical 级电话。对 `reason` 做白名单，避免厂商把「轻微抖动」也报 Degraded 造成告警风暴。
3. **关联上下文** ：告警里附带 PVC 所属命名空间、挂载它的 Pod、所在节点、底层存储卷 ID，让 oncall 一眼定位，而不是只收到一句「有个卷不健康」。
4. **闭环** ：告警触发 remediation（隔离存储后端 / 通知人工故障切换），并回写状态到 GitOps 或事件系统，形成可追溯的处置记录。

我们落地后，存储类故障的平均定位时间从「跨三个系统翻半小时」降到「告警里直接给卷 ID 和节点」，MTTR 缩短明显。

## 八、与存储故障切换（failover）的联动

`Inaccessible` 出现时，理想的动作不是「删 Pod 重调度」（可能调度回同一坏后端），而是触发存储层的 failover：

- 云盘类：调用云厂商 API 把卷从故障可用区 detachment 并在健康区 re-attach，或由存储类（ `allowVolumeExpansion` + 多副本）自动切换。
- 企业存储：通知存储团队做阵列级切换，K8s 侧暂不盲目重建，避免放大影响。
- 设计原则：remediation 必须带 **冷却时间 + 最大重试次数 + 人工确认开关** ，防止自动化在故障期间反复横跳。

Volume Health Monitor 给 failover 提供了「机器可读的触发信号」，但「怎么切」仍是存储后端的能力，两者要配合而非指望 K8s 单方面解决。

## 九、监控面板建议

Grafana 上至少放三张图：控制器侧 PVC 健康分布（按 status 堆叠）、节点侧 Pod 卷健康、CSINode 驱动整体健康。三者叠加，能直观看到「是单卷问题、单节点问题、还是整个驱动问题」——这正是 Volume Health Monitor 把控制器侧与节点侧分开设计的价值所在。

## 十一、常见疑问 FAQ 与速查

**Q1：所有 CSI 驱动都支持吗？**  
不是。驱动必须实现那 4 个新 RPC（ControllerListVolumeHealth / ControllerGetVolumeHealth / NodeGetVolumeHealth / NodeGetStorageHealth）。上线前在测试集群用 `kubectl get pvc -o yaml` 确认 `status.healthStatus` 真的被填充。

**Q2：Alpha 能上生产吗？**  
谨慎。1.37 是 Alpha，字段与行为可能变，不要作为唯一故障判定依据，与存储厂商自身监控互为补充。建议先在非核心业务试点。

**Q3：健康字段为空是坏了吗？**  
未必。可能是驱动没实现 RPC，或 feature gate 只在 kubelet 侧开启而控制器侧没开。两端 gate 都要开，且驱动版本要对。

**Q4：Degraded 和 Inaccessible 怎么区分处理？**  
`Degraded` =降级但仍可用，走 warning 工单； `Inaccessible` =不可访问，走 critical 电话并触发 remediation。对 `reason` 做白名单，避免轻微抖动刷屏。

**Q5：只看 PVC 状态够吗？**  
不够。PVC 是控制器侧视角，漏掉「卷健康但某节点挂载点坏了」。必须同时消费 `Pod.status.volumeHealth` 与 `CSINode.status.storageHealth` ，两侧互补。

**Q6：自动 remediation 安全吗？**  
要带冷却时间 + 最大重试 + 人工确认开关。无脑删 Pod 重调度可能调度回同一坏后端，反而扩大影响。自动化只负责「隔离 + 通知」，切换交给存储层或人工。

## 十三、Volume Health Monitor 接入清单

把存储健康信号接进生产体系，按此清单推进：

1. API Server、kube-controller-manager、kubelet 均已开启 VolumeHealthMonitor feature gate（1.37 Alpha）。
2. CSI 驱动已升级到实现 4 个新 RPC 的版本，并在测试集群验证字段被真实填充。
3. 控制器侧读取 `PVC.status.healthStatus` ，节点侧读取 `Pod.status.volumeHealth` 与 `CSINode.status.storageHealth` ，两侧都消费。
4. 用 exporter 把健康状态转成 Prometheus gauge，建立 PVC / Pod / CSINode 三张可观测面板。
5. 分级告警： `Degraded` 走 warning， `Inaccessible` 走 critical，并对 `reason` 做白名单防刷屏。
6. 告警携带上下文：命名空间、挂载 Pod、节点、底层卷 ID，让 oncall 一眼定位。
7. remediation 带冷却时间、最大重试、人工确认开关，避免自动化在故障期反复横跳。
8. `Inaccessible` 触发存储层 failover（云盘 detachment / 企业阵列切换），而非盲目重建 Pod。
9. 与存储厂商自身监控互为补充，Alpha 阶段不把 K8s 信号当唯一真相源。
10. 文档化：把「卷不健康」的定级、责任人、处置 SOP 写入存储运维手册。

清单落地后，存储故障从「跨三系统翻半小时」变成「告警直接给卷 ID 与节点」，MTTR 显著缩短。

## 十五、要点回顾

Volume Health Monitor 填补了 Kubernetes 存储可观测性里最大的一块空白——让「存储到底健不健康」第一次成为集群内部可读、可告警、可联动的信号。落地要点三条： **驱动支持是前提** （没实现 4 个 RPC 就无字段）； **Alpha 别当唯一真相源** ，与厂商监控互补； **控制器侧与节点侧视角必须兼看** ，否则漏掉「卷健康但节点挂载点坏」的情况。把这套信号接进告警与 remediation 体系，存储类故障的 MTTR 能显著缩短，从「跨三系统翻半小时」变成「告警直接给卷 ID」。

## 十六、总结与行动建议

Volume Health Monitor 填补了 Kubernetes 存储可观测性里最大的一块空白——让「存储到底健不健康」第一次成为集群内部可读、可告警、可联动的信号。落地要点三条：驱动支持是前提（没实现 4 个 RPC 就无字段）；Alpha 别当唯一真相源，与厂商监控互补；控制器侧与节点侧视角必须兼看，否则漏掉「卷健康但节点挂载点坏」的情况。

给不同风险偏好的建议： **稳健型团队** 先在测试集群验证字段填充，把信号接进 Grafana 观察一个月再谈生产； **激进型团队** 可在非核心业务试点，但 remediation 务必带冷却与人工确认，别让自动化在故障期反复横跳； **存储故障高发的团队** （如跨区云盘、老旧阵列）应优先落地，因为这类环境最能从「机器可读的健康信号」中获益。把这套信号接进告警与 remediation 体系，存储类故障的 MTTR 能从「跨三系统翻半小时」缩短到「告警直接给卷 ID 与节点」。1.37 把它重新推进 Alpha 是个强烈信号：存储健康正在成为一等公民，早接入早受益。

Volume Health Monitor 填补了 Kubernetes 存储可观测性里最大的一块空白——让「存储到底健不健康」第一次成为集群内部可读、可告警、可联动的信号，而不是藏在厂商 dashboard 里的黑盒。1.37 把它重新推进 Alpha 是个强烈信号：存储健康正在成为一等公民。落地时记住三点： **驱动支持是前提、Alpha 别当唯一真相源、控制器侧与节点侧视角必须兼看** 。把这套信号接进你的告警与 remediation 体系，存储类故障的 MTTR 能显著缩短。
