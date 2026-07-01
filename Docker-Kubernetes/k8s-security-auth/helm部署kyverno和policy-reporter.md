---
title: Helm部署Kyverno和Policy-Reporter
tags:
  - kubernetes
  - security
  - auth
aliases:
  - kyverno策略引擎
---

# kyverno

## 介绍

- 官网：[Kyverno Docs](https://kyverno.io/docs/)

- release page: [Kyverno Releases](https://github.com/kyverno/kyverno/releases)

- artifacthub: [kyverno helm chart](https://artifacthub.io/packages/helm/kyverno/kyverno/)

- kyverno是希腊语的govern之意。是原生为K8s开发的策略引擎。

- kyverno在k8s中是作为admission controller来运行的，架构如下：

  ![image-20241122100328010](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202411221003152.png)

## 下载

~~~sh
helm repo add --force-update kyverno https://kyverno.github.io/kyverno
helm repo update kyverno
helm pull kyverno/kyverno --version 3.2.7
~~~

## 配置

~~~yaml
#仿照ado中的配置稍作调整
~~~

## 安装

~~~sh
helm upgrade -i kyverno -n kyverno --create-namespace . -f values.yaml
~~~

# kyverno policy

## 语法规则

[Kyverno Policy语法规则](https://mp.weixin.qq.com/s/5tANwfzp8C0O2GS8fkXErA)

## 安装policy

~~~sh
export DIRECTORY="$(System.DefaultWorkingDirectory)/${{parameters.folder}}"
kubectl apply -f $DIRECTORY/external/kyverno/policies/common --recursive

if test -d "$DIRECTORY/external/kyverno/policies/${{parameters.region}}"; then
  kubectl apply -f $DIRECTORY/external/kyverno/policies/${{parameters.region}} --recursive
fi
~~~

# kyverno policy reporter

## 介绍

- kyverno自带的一个GUI界面，官网：
  - [Kyverno Policy Reporter](https://kyverno.io/docs/kyverno-policy-reporter/)
  - [Policy Reporter Docs](https://kyverno.github.io/policy-reporter/)
- release page: [Policy Reporter Releases](https://github.com/kyverno/policy-reporter/releases)
- artifact hub: [policy-reporter helm chart](https://artifacthub.io/packages/helm/policy-reporter/policy-reporter)

## 下载

~~~sh
helm repo add --force-update policy-reporter https://kyverno.github.io/policy-reporter
helm repo update policy-reporter
helm pull policy-reporter/policy-reporter --version 2.24.2
~~~

## 配置

- 创建policy-reporter的certificate

~~~yaml
kubectl create ns policy-reporter

tee certificate-policy-reporter.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-policy-reporter
  namespace: policy-reporter
spec:
  secretName: policy-reporter-tls-cert-secret
  privateKey:
    rotationPolicy: Always
  commonName: kyverno.hanxux.local
  dnsNames:
    - kyverno.hanxux.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: selfsigned
    kind: ClusterIssuer
EOF
~~~

- 配置UI的ingress、oauth和https

~~~yaml
# Settings for the Policy Reporter UI subchart (see subchart's values.yaml)
ui:
  enabled: true
  create: true
  plugins:
    kyverno: true
  resources:
    limits:
      memory: 256Mi
      cpu: 300m
    requests:
      memory: 50Mi
      cpu: 100m
  ingress:
    enabled: true
    ingressClassName: nginx-default
    annotations:
      nginx.ingress.kubernetes.io/auth-url: "http://oauth2-proxy.oauth2-proxy.svc.cluster.local/oauth2/auth"
      nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fkyverno.hanxux.local"
    hosts:
    - host: kyverno.hanxux.local
      paths:
      - path: /
        pathType: Prefix
    tls:
      - secretName: policy-reporter-tls-cert-secret
        hosts:
          - kyverno.hanxux.local
~~~

## 安装

~~~sh
helm upgrade -i policy-reporter -n policy-reporter . -f values.yaml
~~~

## 配置告警

- 可以配置往loki和slack发消息：[Enable Targets Notification](https://kyverno.github.io/policy-reporter/guide/helm-chart-core#enable-targets-notification)

## 访问

https://kyverno.hanxux.local

# 实战--策略强制pod使用harbor中的镜像

安装harbor和kyverno完成后，可以定义一个Policy，使得某个namespace下的所有pod都必须使用harbor中的pod，否则请求会被拒绝。(假设harbor的URL为`registry.local.harbor`)

~~~yaml
cat disallow_any_repo.yaml <<'EOF'
apiVersion: kyverno.io/v1
kind: ClusterPolicy # 该策略的类型为ClusterPolicy，意思是在集群范围内部署
metadata:
  name: check-images
spec:
  validationFailureAction: Enforce #阻止任何不符合规则的请求。与之相对的是Audit，会将审计信息发送给审计工具，而不阻止。
  background: false
  rules:
  - name: check-registry
    match:
      any:
      - resources: #只检查app-namespace中的pod
          kinds:
          - Pod
          namespaces:
          - app-namespace

    preconditions:
      any:
      - key: "{{request.operation}}" #检查请求是否非删除操作，非删除操作的话才继续后续评估。
        operator: NotEquals
        value: DELETE
    validate:
      message: "unknown registry other than harbor"
      foreach:
      - list: "request.object.spec.initContainers"
        pattern:
          image: "registry.local.harbor/*"
      - list: "request.object.spec.containers"
        pattern:
          image: "registry.local.harbor/*"
EOF
~~~

# 实战 -- 自动修改pod的image repo

## 项目背景

在跨国企业中，海外 Artifactory（如 `artifactory.example.com`）经常作为统一镜像源，代理 DockerHub、GHCR、Quay 等公共仓库。当业务扩展到中国区时，由于跨境网络延迟，Pod 拉取镜像速度很慢甚至超时。

解决方案：在中国区 Artifactory（如 `artifactory.example.cn`）上配置 Smart Remote Repository，将海外 Artifactory 作为上游源进行缓存加速。然后利用 Kyverno 在 Pod 创建时自动将镜像路径从 `.com` 替换为 `.cn`，实现对业务 manifest 的零侵入改造。

**核心需求：**

- 自动替换 Pod 中 containers 和 initContainers 的镜像路径
- 仅替换特定仓库（有 Smart Remote 配置的）的镜像，跳过没有 `.cn` 缓存的仓库
- 仅在指定 namespace 中生效，避免影响系统组件
- Kyverno 宕机时不阻塞 Pod 创建（`failurePolicy: Ignore`）

## 为什么选择 MutatingPolicy（CEL）而非 ClusterPolicy（JMESPath）

Kyverno 1.18 引入了 `MutatingPolicy`（API Group: `policies.kyverno.io/v1`），使用 CEL（Common Expression Language）替代 JMESPath。在实际落地中，我们发现 MutatingPolicy 有以下优势：

### 1. CEL 表达力更强

ClusterPolicy 的 JMESPath `AnyIn` 通配符不支持多级路径匹配。例如 `artifactory.example.com/my-repo/*` 无法匹配 `artifactory.example.com/my-repo/datadog/agent:7.68.3-jmx`（多级子路径）。

CEL 的 `startsWith()` + `exists()` 可以轻松实现：

```cel
variables.allowedRepos.exists(repo,
  c.image.startsWith("artifactory.example.com/" + repo + "/")
)
```

### 2. Webhook 机制独立

ClusterPolicy 共享一套 webhook，而 MutatingPolicy 使用独立的 admission 机制（`kyverno-resource-mutating-webhook-cfg` 中的 `mpol.validate.kyverno.svc-ignore`）。在实测中，ClusterPolicy 偶尔出现 webhook 不接收请求的问题，切换到 MutatingPolicy 后立即生效。

### 3. 更好的错误处理

CEL 表达式在编译期即可发现语法错误，而 JMESPath 的错误往往在运行时才暴露。MutatingPolicy 的 `READY` 状态可以直观反映策略是否编译通过。

## 最终 Policy 设计

### 关键设计决策：单一 Policy + matchExpressions In

**踩坑经历：** 最初尝试为每个 namespace 生成一个 MutatingPolicy（通过 Helm `range` 循环），但发现所有 MutatingPolicy 共享同一个 webhook（`kyverno-resource-mutating-webhook-cfg`），最后一个 policy 的 `namespaceSelector` 会覆盖之前所有 policy 的 selector。导致只有最后一个 namespace 的 policy 生效。

**解决方案：** 使用单一 MutatingPolicy，通过 `matchExpressions` + `operator: In` 列出所有目标 namespace。

### Policy YAML（Helm 模板）

```yaml
{{- if .Values.kyvernoPolicy }}
{{- if .Values.kyvernoPolicy.targetNamespaces }}
---
apiVersion: policies.kyverno.io/v1
kind: MutatingPolicy
metadata:
  name: mutate-image-registry-cn
spec:
  # Kyverno 宕机时不阻塞 Pod 创建，Pod 会使用原始 .com 路径作为 fallback
  failurePolicy: Ignore
  matchConstraints:
    # 单一 Policy + In 操作符，避免多 policy 的 webhook selector 冲突
    namespaceSelector:
      matchExpressions:
        - key: kubernetes.io/metadata.name
          operator: In
          values:
          {{- range .Values.kyvernoPolicy.targetNamespaces }}
            - {{ . }}
          {{- end }}
    resourceRules:
      - apiGroups: ['']
        apiVersions: ['v1']
        operations: ['CREATE', 'UPDATE']
        resources: ['pods']
  # 仓库白名单：仅替换有 Smart Remote 配置的仓库
  variables:
    - name: allowedRepos
      expression: >-
        [{{- range $i, $repo := .Values.kyvernoPolicy.allowedRepos -}}
        {{ if $i }}, {{ end }}"{{ $repo }}"
        {{- end }}]
  mutations:
    # 替换 containers 中的镜像路径
    - patchType: JSONPatch
      jsonPatch:
        expression: |
          object.spec.containers.map(c,
            c.image.startsWith("artifactory.example.com/") &&
            variables.allowedRepos.exists(repo,
              c.image.startsWith("artifactory.example.com/" + repo + "/")) ?
            JSONPatch{
              op: "replace",
              path: "/spec/containers/" + string(object.spec.containers.indexOf(c)) + "/image",
              value: c.image.replace("artifactory.example.com", "artifactory.example.cn")
            } : null
          ).filter(p, p != null)
    # 替换 initContainers 中的镜像路径（需先判断是否存在）
    - patchType: JSONPatch
      jsonPatch:
        expression: |
          has(object.spec.initContainers) ?
          object.spec.initContainers.map(c,
            c.image.startsWith("artifactory.example.com/") &&
            variables.allowedRepos.exists(repo,
              c.image.startsWith("artifactory.example.com/" + repo + "/")) ?
            JSONPatch{
              op: "replace",
              path: "/spec/initContainers/" + string(object.spec.initContainers.indexOf(c)) + "/image",
              value: c.image.replace("artifactory.example.com", "artifactory.example.cn")
            } : null
          ).filter(p, p != null)
          : []
{{- end }}
{{- end }}
```

### Values 配置

```yaml
kyvernoPolicy:
  # 分阶段 rollout：先基础设施，再业务 namespace
  targetNamespaces:
    - tools

  # 仅替换有 Smart Remote 缓存的仓库，跳过无缓存的（如 docker-local-sandbox）
  allowedRepos:
    - my-dockerhub-docker-remote
    - my-ghcr-docker-remote
    - my-quay-docker-remote
```

## 验证方法

```bash
# 检查 policy 状态（READY 应为 true）
kubectl get mutatingpolicy
# NAME                       AGE   READY
# mutate-image-registry-cn   1m    true

# 检查 webhook selector 是否正确包含所有目标 namespace
kubectl get mutatingwebhookconfiguration kyverno-resource-mutating-webhook-cfg \
  -o jsonpath='{.webhooks[0].namespaceSelector}' | jq .

# dry-run 测试：目标 namespace 中的白名单 repo（应被替换）
kubectl run test -n tools \
  --image=artifactory.example.com/my-dockerhub-docker-remote/datadog/agent:7.68.3 \
  --dry-run=server -o jsonpath='{.spec.containers[0].image}'
# 输出: artifactory.example.cn/my-dockerhub-docker-remote/datadog/agent:7.68.3

# dry-run 测试：目标 namespace 中的非白名单 repo（不应被替换）
kubectl run test -n tools \
  --image=artifactory.example.com/my-docker-local-sandbox/some-image:latest \
  --dry-run=server -o jsonpath='{.spec.containers[0].image}'
# 输出: artifactory.example.com/my-docker-local-sandbox/some-image:latest

# dry-run 测试：非目标 namespace（不应被替换）
kubectl run test -n default \
  --image=artifactory.example.com/my-dockerhub-docker-remote/datadog/agent:7.68.3 \
  --dry-run=server -o jsonpath='{.spec.containers[0].image}'
# 输出: artifactory.example.com/my-dockerhub-docker-remote/datadog/agent:7.68.3

# rollout restart 后检查 Pod 镜像是否已替换
kubectl rollout restart deployment -n tools
kubectl get pods -n tools \
  -o jsonpath='{range .items[*]}{.metadata.name}: {.spec.containers[*].image}{"\n"}{end}'
```

## 踩坑记录

### 1. 多 MutatingPolicy 的 webhook selector 冲突
**现象：** 为每个 namespace 创建一个 MutatingPolicy 后，只有最后一个 namespace 的 Pod 被 mutate。
**原因：** 所有 MutatingPolicy 共享同一个 `MutatingWebhookConfiguration`（`kyverno-resource-mutating-webhook-cfg`），webhook 的 `namespaceSelector` 被最后注册的 policy 覆盖。
**解决：** 使用单一 MutatingPolicy + `matchExpressions.In` 列出所有目标 namespace。

# Kyverno 1.18 新特性（CNCF 毕业后首个版本）

> 原文：https://www.cncf.io/blog/2026/05/05/announcing-kyverno-release-1-18/

Kyverno 1.18 现已发布，这是 Kyverno 在 CNCF 毕业后的首个版本。

本次发布进一步巩固了 Kyverno 作为 Kubernetes 原生策略引擎的定位，重点投入方向包括安全、CLI 能力以及策略引擎可靠性。同时，Kyverno 也在继续向基于 CEL 的策略类型演进，为未来的 Policy as Code 奠定基础。

## TL;DR

Kyverno 1.18 带来了以下更新：

- 面向基于 HTTP 的策略执行，提供更强的安全控制，并缓解多个 CVE 问题
- 大幅增强 CLI 能力，用于测试和应用现代策略类型
- 提升策略引擎在性能、可观测性和可扩展性方面的表现
- 增强 policies Helm chart，支持更灵活的自定义配置

本次发布没有破坏性变更，但 ClusterPolicy 的弃用计划仍在推进，用户应开始迁移到新的策略类型。

## 安全改进

安全一直是 Kyverno 的核心支柱。1.18 版本为策略执行引入了多项重要防护能力。

### 更安全的 HTTP 执行

Kyverno 策略可以通过 HTTP CEL 库调用外部服务。在 1.18 中，这一能力得到了显著加固：

- **阻止列表 / 允许列表强制执行**：默认情况下，loopback、元数据服务等不安全地址会被阻止。用户可以为集群级策略和命名空间级策略配置允许列表和阻止列表。此外，来自命名空间级策略的 HTTP 调用默认被禁用，需要通过配置标志显式开启。这些变更有助于防止 SSRF 类型的滥用。更多细节可参考 CVE-2026-4789。
- **作用域 token 授权**：此前，Kyverno HTTP 调用中包含的 token 可能被用于冒充 Kyverno 控制器。现在，HTTP 调用会携带一个单独的、具备作用域限制的 token，确保服务端无法滥用该 token。更多细节可参考 CVE-2026-41323。

这些变化在保持高级策略场景灵活性的同时，降低了非预期外部访问的风险。

## CLI 扩展与开发者体验

Kyverno CLI 正在持续演进，成为策略开发和测试中的关键工具。

### 扩展策略支持

`kyverno apply` 和 `kyverno test` 命令现在支持：

- Cleanup policies
- HTTP 和 Envoy 授权策略
- MutatingPolicy 中的 mutateExisting 规则
- `--exceptions-with-policies` 标志，用于改进测试工作流

这显著提升了在本地环境和 CI 流水线中测试现代策略类型的能力。

### 可靠性与易用性改进

本次版本还修复了多个问题，涉及：

- 错误处理与错误报告
- 无集群连接场景下的 CRD 兼容性
- panic、文件句柄泄漏等稳定性问题

这些改进让用户在处理策略时获得更可预测、更友好的开发体验。

## 策略引擎改进

Kyverno 1.18 包含多项增强，用于改进策略在大规模环境中的执行和管理方式。

### 更细粒度的成功事件过滤

新的 `successEventActions` ConfigMap 参数允许用户控制：

- 哪些成功事件会被发出
- 策略报告的噪声程度

这对于大型环境尤其有价值，因为在这些环境中，事件数量往往需要进行调优。

### 性能与可扩展性

关键改进包括：

- admission controller 支持基于内存的 HPA 自动扩缩容
- `/metrics` 端点支持 TLS
- 改进并发处理，降低竞态条件风险

这些变化让 Kyverno 在大规模生产环境中更加可靠。

### CEL 与策略执行增强

- 新增 gzip CEL 库，支持更高级的表达式
- 改进策略变量和条件的编译与求值
- 改善策略类型与执行引擎之间的一致性

## 镜像验证改进

本次版本还对镜像验证能力进行了多项针对性改进：

- 对于 ClusterPolicies，`imageRegistryCredentials.secrets` 现在支持 `namespace/name` 表示法；同时，Pod 级别的 `imagePullSecrets` 会自动被用作镜像仓库凭证。这对于多租户环境很有用，因为每个命名空间通常会管理自己的 pull secrets。
- ImageValidatingPolicy 可靠性修复，包括更好地处理签名时间戳和 TSA 证书链、Notary resolver 修复、正确的 `matchImageReferences` 过滤，以及改进命名空间级策略的 autogen 支持。

## Policies Helm Chart 增强

policies Helm chart 也在持续演进，提供更好的自定义能力和控制能力。

新增能力包括：

- 在 ValidatingPolicies 中支持 excludes，包括 namespace、subject、resource rules 和 match conditions
- `auditAnnotation` 配置
- 每个策略级别的 annotation 覆盖

这些改进让用户可以更容易地根据组织和运维需求定制策略。

## 支持策略更新

从 1.18 版本开始，Kyverno 将采用 "main + 1" 补丁支持模型（N-1 模型）。

- **当前版本（main）和上一个版本** 会获得补丁支持。补丁范围仅限于严重和高危 CVE，以及其他关键修复。这大约提供 3 个月的社区补丁支持。
- **更早版本** 将不再获得常规更新或修复。

这一调整帮助维护者团队更高效地管理安全问题和 PR 数量增长，将精力集中在当前活跃版本上，在项目规模扩大时保持可持续和可管理。

建议用户保持使用较新的 Kyverno 版本，根据约 3 个月的支持窗口规划升级。

## ClusterPolicy 弃用提醒

ClusterPolicy 资源计划在今年晚些时候弃用。用户应开始迁移到新的策略类型：

| 旧类型 | 新类型 |
|--------|--------|
| ClusterPolicy (validate) | ValidatingPolicy |
| ClusterPolicy (mutate) | MutatingPolicy |
| ClusterPolicy (generate) | GeneratingPolicy |
| ClusterPolicy (imageVerify) | ImageValidatingPolicy |
| CleanupPolicy | DeletingPolicy |

迁移建议：

1. 开始迁移现有策略
2. 使用 CLI 进行充分测试
3. 反馈功能差距或问题

## Roadmap

展望未来，Kyverno roadmap 将重点关注：

- 持续投入基于 CEL 的策略类型
- 改进策略编写体验
- 在多集群环境中扩展策略能力
- 拓展 AI governance 与策略驱动自动化能力

## 参考链接

- 原文：https://www.cncf.io/blog/2026/05/05/announcing-kyverno-release-1-18/
- CNCF 毕业公告：https://www.cncf.io/announcements/2026/04/02/cloud-native-computing-foundation-announces-kyverno-graduation/
- CVE-2026-4789：https://github.com/kyverno/kyverno/security/advisories/GHSA-xxxx
- CVE-2026-41323：https://github.com/kyverno/kyverno/security/advisories/GHSA-xxxx
- Kyverno 安装：https://kyverno.io/docs/installation/
- GitHub Releases：https://github.com/kyverno/kyverno/releases
- Roadmap：https://github.com/kyverno/kyverno/milestones
