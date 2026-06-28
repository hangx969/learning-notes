---
title: "当 Istio、Kyverno、Gatekeeper 三个 Webhook 同时存在，你的集群会发生什么？"
source: "https://mp.weixin.qq.com/s/i4RuNLZj5PSGScKpcE3vNQ"
author:
  - "[[AI炼丹踩坑]]"
published:
created: 2026-06-28
description: "不是某一个组件坏了，而是 Istio、Kyverno、Gatekeeper 三条 Admission Webhook 链叠在一起，把 Pod 对象改成了策略无法接受的形态。"
tags:
  - "clippings"
---
AI炼丹踩坑 AI炼丹踩坑 *2026年6月15日 08:15*

一个 Pod 创建失败，报错却指向 Gatekeeper。

业务同学第一反应是合规策略太严；平台同学去看 Kyverno，发现镜像策略也命中了；再往前翻，Istio sidecar 已经注入过一轮。

最后发现：不是某一个组件坏了，而是 **Istio、Kyverno、Gatekeeper 三条 Admission Webhook 链叠在一起** ，把 Pod 对象改成了策略无法接受的形态。

这类问题在企业集群里非常常见。

服务网格要注入 sidecar，策略引擎要改镜像、加标签，合规组件要做准入校验。单独看都合理，放在一条链路里，就开始互相“踩脚”。

---

## 先看请求到底经过了什么

一个创建 Pod 的请求进入 kube-apiserver 后，大致会经过两段 Admission：

![图片](https://mmbiz.qpic.cn/mmbiz_png/rK4MSArUKeeZWMIUyLTCmqlHr9rsF7HKQxVuHxMUyUopvuBqJfVLjq6bU7ep6ZTP6oj1iaJJ2gKzVA8fxNSndDzEw58fBpT2puaEJQXZwNnI/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

关键点在这里：

Mutating Webhook 会修改对象。

Validating Webhook 看到的是 **所有 Mutation 之后的最终对象** 。

所以 Gatekeeper 拒绝 Pod，不一定是业务原始 YAML 有问题。它可能是在拒绝一个已经被 Istio、Kyverno 改过的对象。

这也是排查这类故障最容易走偏的地方。

---

## 三个组件分别会动哪里

先把角色拆开看。

Istio 的 `istio-sidecar-injector` 是 Mutating Webhook。它会给 Pod 加 `istio-init` 、 `istio-proxy` ，还会修改 annotations、volumes、volumeMounts、securityContext 等字段。

Kyverno 同时有 Mutating 和 Validating 能力。它可能改镜像仓库、加 `imagePullSecrets` 、补资源限制、打标签，也可能在后面做策略校验。

Gatekeeper 传统上主要是 Validating Webhook。开启 mutation 后，也可能通过 Assign、AssignMetadata、ModifySet 改对象。

也就是说，一个 Pod 在真正写入 etcd 前，可能已经被改了很多次。

问题不在于“谁改了对象”，而在于 **谁先改、改了哪个路径、后一个组件是否假设对象结构没变** 。

---

## 第一个坑：JSON Patch 的路径太脆

JSON Patch 很强，也很危险。

它操作的是具体路径，比如：

```
[
  { "op": "replace", "path": "/spec/containers/0/image", "value": "registry.k8s.io/pause:3.9" }
]
```

这个片段的含义很直接：替换第 0 个 container 的 image。

但在多 Webhook 链里， `/spec/containers/0` 是一个很脆的假设。

如果前面某个 webhook 改了 containers 数组，后面的 patch 仍然按固定 index 修改，就可能改错容器。

Istio 通常会追加 `istio-proxy` ，其他组件也可能插入 sidecar、init container 或调整数组。只要策略引擎把“容器身份”绑定到数组下标，而不是绑定到 container name，就埋了雷。

比较稳的做法是：

- 镜像策略按 container name 或镜像字段匹配
- 避免直接依赖 `/spec/containers/0`
- 对注入容器设置明确的排除规则
- 把最终 Pod 对象作为校验对象，而不是原始 YAML

很多线上事故不是“策略写错”，而是策略默认了对象结构不会变。

在 Webhook 链里，这个默认通常不成立。

---

## 第二个坑：annotations 被整体覆盖

annotations 是另一个高频冲突点。

Istio 会写入类似 `sidecar.istio.io/status` 的注解，记录注入状态。

Kyverno 可能写入策略处理相关注解。

有些自研 webhook 或策略模板为了省事，会直接 replace 整个 annotations 对象，而不是 add 单个 key。

这会导致一个非常隐蔽的问题：前一个 webhook 写入的状态被后一个 webhook 抹掉。

正确姿势应该是只改自己的 key：

```
[
  { "op": "add", "path": "/metadata/annotations/team", "value": "platform" }
]
```

危险姿势是替换整个对象：

```
[
  { "op": "replace", "path": "/metadata/annotations", "value": { "team": "platform" } }
]
```

后者看起来简单，但会把其他组件写入的 annotations 一起清掉。

在 Istio 场景下，注入状态丢失后，后续排查会非常痛苦：Pod 看起来像注入过，又缺少关键注解；策略引擎看到的对象，也可能和你预期不一致。

**Webhook 只应该管理自己负责的字段。**

这是多组件共存的第一条红线。

---

## 第三个坑：Gatekeeper 拒绝的是“最终对象”

很多人看到错误：

```
admission webhook "validation.gatekeeper.sh" denied the request
```

第一反应是去看业务 YAML。

但在 Istio 注入场景下，Gatekeeper 校验的已经不是业务提交的原始 Pod 了。

它看到的 Pod 里多了 `istio-proxy` 。

如果 Gatekeeper 策略要求所有容器镜像必须来自企业私有仓库，而 `istio-proxy` 使用的是 `docker.io/istio/proxyv2` 或集群里配置的 Istio 镜像仓库，策略没有豁免，就会拒绝所有开启 sidecar 的工作负载。

这类故障的典型表现是：

- 不开 Istio 注入，Pod 正常创建
- 开启 namespace label 后，Pod 全部失败
- 错误信息指向 Gatekeeper
- Kyverno 和 Istio 日志里看不出明显异常

根因其实是策略没有理解“注入容器”的存在。

解决方向不是关掉 Gatekeeper，而是把策略边界写清楚：

- 排除 `istio-system` 命名空间
- 对 `istio-proxy` 单独放行
- 对 Mesh 运行时镜像仓库设置白名单
- 对业务容器和平台注入容器使用不同约束

合规策略不能只看“所有 containers”。

在服务网格集群里，它必须区分业务容器和平台容器。

---

## 先把 Webhook 链拉出来

排查前，别急着改策略。

先把集群里的 Webhook 配置列清楚：

```
kubectl get mutatingwebhookconfigurations
kubectl get validatingwebhookconfigurations
```

再看每个 Webhook 的关键字段：

```
kubectl get mutatingwebhookconfigurations -o json \
| jq '.items[] | {
  name: .metadata.name,
  webhooks: [.webhooks[] | {
    name, failurePolicy, reinvocationPolicy,
    namespaceSelector, objectSelector
  }]
}'
```

这里重点看四个点：

- `name`
	：影响链路里的相对顺序观察
- `namespaceSelector`
	：是否误匹配了系统命名空间
- `objectSelector`
	：是否只作用在必要对象上
- `failurePolicy`
	：组件异常时是 Fail 还是 Ignore

不要只看组件文档里的默认值。

很多集群安装后被 Helm values、Operator 或平台脚本改过，最终以 apiserver 里的配置为准。

---

## 用审计日志看谁改了对象

如果集群开启了 kube-apiserver audit log，可以直接从审计日志里追 Admission 行为。

重点过滤 Pod 创建请求和 admission 相关字段。

常用思路是：

```
grep '"resource":"pods"' /var/log/kubernetes/audit.log \
| grep '"verb":"create"' \
| grep 'admission'
```

不同发行版审计日志路径不一样。

托管集群通常需要在云厂商控制台或日志服务里查。你要找的是同一次 Pod 创建过程中，各个 webhook 返回的 patch、耗时和拒绝信息。

排查时建议记录三份对象：

- 用户提交的原始 YAML
- Mutating 之后的最终 Pod
- Validating 拒绝时的错误信息

如果只看第一份，很容易误判。

---

## 复现时别直接拿业务集群硬试

Admission Webhook 的坑很难靠肉眼判断。

建议准备一个隔离 namespace，只开启你要验证的标签和策略。

```
kubectl create namespace webhook-lab
kubectl label namespace webhook-lab istio-injection=enabled
```

然后逐步打开策略：

1. 只开 Istio 注入，确认 Pod 能创建
2. 打开 Kyverno mutation，看最终镜像和 annotations
3. 打开 Gatekeeper validation，看是否被拒绝
4. 再打开 Gatekeeper mutation，如果集群确实使用了它

每加一层，都抓一次最终对象。

```
kubectl get pod -n webhook-lab -o yaml
```

这一步很笨，但有效。

因为 Webhook 链问题本质上是“对象形态变化问题”，最终 YAML 才是事实。

---

## reinvocationPolicy 不要随便开

Kubernetes 支持 `reinvocationPolicy: IfNeeded` 。

意思是：如果后面的 Mutating Webhook 修改了对象，前面已经执行过的 Webhook 有机会被重新调用。

听起来很好，实际要谨慎。

当 Istio、Kyverno、Gatekeeper mutation 都存在时，重新调用可能让对象经历第二轮修改。虽然 apiserver 不会无限循环，但最终对象会更难预测。

尤其是下面这几类 mutation：

- 根据当前 annotations 决定是否补字段
- 根据 container 列表生成 patch
- 对数组使用固定下标
- replace 整个 map 或 list

如果这类 Webhook 被重新调用，结果可能和第一轮不同。

我的建议是：

**需要 IfNeeded 的组件统一规划，不要让每个组件各自决定。**

如果要开，必须满足两个条件：

- mutation 是幂等的
- patch 只作用于自己负责的字段

否则排查成本会翻倍。

---

## failurePolicy 要分级，不要全 Fail

很多组件默认 `failurePolicy: Fail` 。

安全上没错，但在生产集群里，全 Fail 很容易造成连锁故障。

例如 webhook service 网络不通、证书过期、endpoint 缺失，都会导致 Pod 创建失败。更麻烦的是，如果 kube-system 里的关键组件也被匹配，集群自愈能力会被打断。

建议做分级：

- 强安全边界：Fail
- 辅助标签、默认值、非关键增强：Ignore
- kube-system、istio-system 等系统命名空间：明确排除
- Webhook 后端服务：必须有监控和告警

查看 failurePolicy：

```
kubectl get validatingwebhookconfigurations -o json \
| jq '.items[] | {
  config: .metadata.name,
  webhooks: [.webhooks[] | {name, failurePolicy}]
}'
```

这里没有统一答案。

但有一个原则： **Fail 的 Webhook 必须具备生产级可用性** 。

如果后端只有一个副本，没有 PDB，没有证书过期告警，却拦在所有 Pod 创建路径上，这就是事故预埋点。

---

## 一套比较稳的编排规范

多 Webhook 共存，不靠“大家都小心”。

需要有编排规范。

我在项目里一般按下面几条落地。

第一，namespaceSelector 必须精确。

不要让业务策略扫到 kube-system，也不要让实验策略扫到全集群。Istio 注入、Kyverno mutation、Gatekeeper validation 都要有明确作用域。

第二，Mutation 只改自己的字段。

不要 replace 整个 annotations、labels、containers、volumes。能 add 单 key，就不要覆盖整个 map。

第三，策略里必须识别平台注入容器。

`istio-proxy` 、安全 Agent、日志 sidecar 都不应该和业务容器套同一套镜像规则。否则每引入一个平台组件，就会引爆一次准入策略。

第四，数组字段不要依赖固定 index。

containers、initContainers、volumeMounts 都属于高风险字段。策略逻辑要尽量基于 name 匹配。

第五，Webhook 配置进入变更流程。

新增一个 Admission Webhook，不应该只是安装一个 Helm Chart。它应该像变更网络策略、RBAC 一样，经过评审。

至少要回答：

- 匹配哪些资源？
- 是否修改对象？
- 修改哪些字段？
- failurePolicy 是什么？
- 是否影响系统命名空间？
- 和现有 Webhook 是否有字段重叠？

第六，审计日志保留足够长。

Admission 问题经常是偶发的。没有 audit log，只靠应用报错，很难还原对象被谁改过。

---

## 最后给一份排查清单

遇到 “Istio + Kyverno + Gatekeeper” 场景下 Pod 创建失败，可以按这个顺序走：

1. 看报错来自 Mutating 还是 Validating
2. 列出所有 MutatingWebhookConfiguration
3. 列出所有 ValidatingWebhookConfiguration
4. 检查 namespaceSelector 和 objectSelector
5. 查看 failurePolicy 和 webhook service endpoints
6. 在隔离 namespace 逐个开启组件复现
7. 对比原始 YAML 和最终 Pod YAML
8. 查 audit log 里的 patch 和拒绝原因
9. 检查策略是否误伤 `istio-proxy`
10. 检查是否有 replace 整个 annotations、labels、containers 的行为

如果只能记住一句话：

**Gatekeeper 拒绝的不是原始 Pod，而是所有 Mutating Webhook 改完之后的 Pod。**

这个认知一旦建立，很多“策略误杀”“Istio 注入失败”“Kyverno 镜像规则异常”的问题，都会变得容易定位。

Admission Webhook 是 Kubernetes 扩展能力里非常强的一环，但强扩展意味着强耦合。

当集群里同时存在服务网格、策略引擎、安全扫描、镜像治理时，Webhook 链本身就应该被当成基础设施治理对象。

你们的集群里现在有多少个 Webhook？有没有做过调用链和字段冲突梳理？

---

> 觉得有帮助？点个「在看」让更多人看到。 有类似的经历？欢迎留言区交流。