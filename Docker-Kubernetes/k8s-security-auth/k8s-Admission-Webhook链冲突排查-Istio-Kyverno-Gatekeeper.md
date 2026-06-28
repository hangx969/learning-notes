---
title: "当 Istio、Kyverno、Gatekeeper 三个 Webhook 同时存在，你的集群会发生什么？"
source: "https://mp.weixin.qq.com/s/i4RuNLZj5PSGScKpcE3vNQ"
created: 2026-06-28
tags:
  - kubernetes
  - admission-webhook
  - kyverno
  - gatekeeper
  - istio
  - troubleshooting
---

# Admission Webhook 链冲突排查

## 问题场景

一个 Pod 创建失败，报错却指向 Gatekeeper。

业务同学第一反应是合规策略太严；平台同学去看 Kyverno，发现镜像策略也命中了；再往前翻，Istio sidecar 已经注入过一轮。

最后发现：不是某一个组件坏了，而是 **Istio、Kyverno、Gatekeeper 三条 Admission Webhook 链叠在一起**，把 Pod 对象改成了策略无法接受的形态。

## 请求到底经过了什么

一个创建 Pod 的请求进入 kube-apiserver 后，经过两段 Admission：

```
用户 YAML → Mutating Webhooks（按字母序依次执行）→ Validating Webhooks（看到的是所有 Mutation 之后的最终对象）→ etcd
```

**关键认知**：Gatekeeper（Validating）拒绝的不是业务原始 YAML，而是已经被 Istio、Kyverno 改过的对象。

## 三个组件分别动哪里

| 组件 | Webhook 类型 | 修改内容 |
|------|:----------:|---------|
| **Istio** `istio-sidecar-injector` | Mutating | 加 `istio-init`、`istio-proxy` 容器，修改 annotations、volumes、volumeMounts、securityContext |
| **Kyverno** | Mutating + Validating | 改镜像仓库、加 `imagePullSecrets`、补资源限制、打标签；也做策略校验 |
| **Gatekeeper** | 主要 Validating（开启 mutation 后也可 Mutating） | 通过 Assign/AssignMetadata/ModifySet 改对象；ConstraintTemplate 做准入校验 |

一个 Pod 在真正写入 etcd 前，可能已经被改了很多次。问题不在于"谁改了对象"，而在于**谁先改、改了哪个路径、后一个组件是否假设对象结构没变**。

## 坑 1：JSON Patch 的路径太脆

```json
[{ "op": "replace", "path": "/spec/containers/0/image", "value": "registry.k8s.io/pause:3.9" }]
```

`/spec/containers/0` 是一个很脆的假设。如果前面某个 webhook 改了 containers 数组（Istio 追加了 `istio-proxy`），后面的 patch 仍然按固定 index 修改，就可能改错容器。

**稳妥做法**：
- 镜像策略按 container name 或镜像字段匹配，不依赖数组下标
- 对注入容器设置明确的排除规则
- 把最终 Pod 对象作为校验对象，而不是原始 YAML

## 坑 2：annotations 被整体覆盖

Istio 写入 `sidecar.istio.io/status`，Kyverno 写入策略处理注解。如果某个 webhook 用 `replace` 整个 annotations 对象而不是 `add` 单个 key：

```json
// ❌ 危险：替换整个 annotations，清掉其他组件写入的内容
[{ "op": "replace", "path": "/metadata/annotations", "value": { "team": "platform" } }]

// ✅ 安全：只改自己负责的 key
[{ "op": "add", "path": "/metadata/annotations/team", "value": "platform" }]
```

**红线**：Webhook 只应该管理自己负责的字段。

## 坑 3：Gatekeeper 拒绝的是"最终对象"

典型故障表现：
- 不开 Istio 注入，Pod 正常创建
- 开启 namespace label `istio-injection=enabled` 后，Pod 全部失败
- 错误信息指向 Gatekeeper
- Kyverno 和 Istio 日志里看不出明显异常

**根因**：Gatekeeper 策略要求所有容器镜像必须来自企业私有仓库，但 `istio-proxy` 使用的是 `docker.io/istio/proxyv2`，策略没有豁免，就拒绝了所有开启 sidecar 的工作负载。

**解决方向**：
- 排除 `istio-system` 命名空间
- 对 `istio-proxy` 单独放行
- 对 Mesh 运行时镜像仓库设置白名单
- 对业务容器和平台注入容器使用不同约束

**合规策略不能只看"所有 containers"。在服务网格集群里，它必须区分业务容器和平台容器。**

## 排查流程

### 第一步：列出所有 Webhook 配置

```bash
kubectl get mutatingwebhookconfigurations
kubectl get validatingwebhookconfigurations

# 查看关键字段
kubectl get mutatingwebhookconfigurations -o json \
| jq '.items[] | {
  name: .metadata.name,
  webhooks: [.webhooks[] | {
    name, failurePolicy, reinvocationPolicy,
    namespaceSelector, objectSelector
  }]
}'
```

重点看四个字段：
- `name`：影响链路里的相对顺序
- `namespaceSelector`：是否误匹配了系统命名空间
- `objectSelector`：是否只作用在必要对象上
- `failurePolicy`：组件异常时是 Fail 还是 Ignore

### 第二步：用审计日志追踪谁改了对象

```bash
grep '"resource":"pods"' /var/log/kubernetes/audit.log \
| grep '"verb":"create"' \
| grep 'admission'
```

排查时建议记录三份对象：
1. 用户提交的原始 YAML
2. Mutating 之后的最终 Pod
3. Validating 拒绝时的错误信息

### 第三步：隔离复现

```bash
kubectl create namespace webhook-lab
kubectl label namespace webhook-lab istio-injection=enabled

# 逐步开启组件，每加一层都抓一次最终对象
# 1. 只开 Istio 注入 → 确认 Pod 能创建
# 2. 打开 Kyverno mutation → 看最终镜像和 annotations
# 3. 打开 Gatekeeper validation → 看是否被拒绝
# 4. 再打开 Gatekeeper mutation（如果集群使用了）

kubectl get pod -n webhook-lab -o yaml
```

## reinvocationPolicy：谨慎使用

Kubernetes 支持 `reinvocationPolicy: IfNeeded`——如果后面的 Mutating Webhook 修改了对象，前面已执行过的 Webhook 有机会被重新调用。

当 Istio、Kyverno、Gatekeeper mutation 都存在时，重新调用可能让对象经历第二轮修改，最终对象更难预测。

开启条件：
- mutation 必须是**幂等**的
- patch 只作用于自己负责的字段

否则排查成本翻倍。

## failurePolicy 分级策略

很多组件默认 `failurePolicy: Fail`。安全上没错，但在生产集群里全 Fail 容易造成连锁故障（webhook service 网络不通、证书过期、endpoint 缺失都会导致 Pod 创建失败）。

```bash
# 检查 failurePolicy
kubectl get validatingwebhookconfigurations -o json \
| jq '.items[] | {config: .metadata.name, webhooks: [.webhooks[] | {name, failurePolicy}]}'
```

分级建议：

| 场景 | 建议 failurePolicy |
|------|:------------------:|
| 强安全边界（镜像准入、特权容器拦截） | **Fail** |
| 辅助标签、默认值、非关键增强 | **Ignore** |
| kube-system、istio-system 等系统命名空间 | **明确排除** |

原则：**Fail 的 Webhook 必须具备生产级可用性**（多副本、PDB、证书过期告警）。

## 编排规范（六条铁律）

1. **namespaceSelector 必须精确**：业务策略不扫 kube-system，实验策略不扫全集群
2. **Mutation 只改自己的字段**：不 replace 整个 annotations/labels/containers/volumes，能 add 单 key 就不覆盖整个 map
3. **策略里必须识别平台注入容器**：`istio-proxy`、安全 Agent、日志 sidecar 不套业务容器的镜像规则
4. **数组字段不依赖固定 index**：containers、initContainers、volumeMounts 基于 name 匹配
5. **Webhook 配置进入变更流程**：新增 Webhook 像变更网络策略/RBAC 一样经过评审（匹配哪些资源？改哪些字段？failurePolicy？影响系统命名空间吗？和现有 Webhook 有字段重叠吗？）
6. **审计日志保留足够长**：Admission 问题经常是偶发的，没有 audit log 很难还原

## 排查清单（10 步速查）

1. 看报错来自 Mutating 还是 Validating
2. 列出所有 MutatingWebhookConfiguration
3. 列出所有 ValidatingWebhookConfiguration
4. 检查 namespaceSelector 和 objectSelector
5. 查看 failurePolicy 和 webhook service endpoints
6. 在隔离 namespace 逐个开启组件复现
7. 对比原始 YAML 和最终 Pod YAML
8. 查 audit log 里的 patch 和拒绝原因
9. 检查策略是否误伤 `istio-proxy`
10. 检查是否有 replace 整个 annotations/labels/containers 的行为

> **核心认知**：Gatekeeper 拒绝的不是原始 Pod，而是所有 Mutating Webhook 改完之后的 Pod。
