---
title: "云原生基础设施 + SRE 落地项目：从平台建设到稳定性工程闭环"
source: "https://mp.weixin.qq.com/s/bGRMoGmVyRycNZNWnYF2BA?scene=1&click_id=68"
author:
  - "[[银河技术]]"
published:
created: 2026-06-05
description:
tags:
  - "clippings"
---
银河技术 *2026年4月19日 22:26*

## 云原生基础设施 + SRE 落地项目：从平台建设到稳定性工程闭环

在很多团队里，“上 Kubernetes”“接 Prometheus”“做自动化发布”往往是分散推进的：基础设施团队负责集群，研发团队负责应用，运维团队负责告警，出了故障再临时拉群协同。这样做的问题不是技术组件不够先进，而是缺少一套围绕“交付效率 + 系统可靠性 + 运行成本”统一设计的工程体系。

本文基于一个真实可复用的云原生平台建设思路，系统讲清楚如何从 0 到 1 搭建生产级 Kubernetes 平台，并把 GitOps、可观测性、容量治理、故障演练和 SRE 方法论串成一个可以落地、可以扩展、可以支撑高并发业务的完整项目。

文章重点不只停留在“用了什么技术”，而是回答四个更重要的问题：

- • 为什么要这样设计，而不是简单堆组件
- • 这些组件在高并发和生产环境下如何协同
- • 稳定性目标如何被量化、治理和验证
- • 一套平台如何支撑多环境、多团队和持续演进

---

## 一、项目背景与建设目标

### 1.1 背景

项目服务于公司内部多个业务系统，包括用户中心、订单服务、支付服务、营销服务和内部管理后台。随着业务增长，传统部署方式逐渐暴露出几个典型问题：

- • 发布依赖人工操作，环境不一致，变更风险高
- • 应用运行状态不可见，故障定位依赖 SSH 登录和日志 grep
- • 资源规划粗放，峰值期间容易出现节点资源争抢
- • 告警很多，但真正能体现用户影响的告警很少
- • 故障恢复依赖专家经验，缺少标准化流程和自动化能力

### 1.2 建设目标

平台建设最终不是为了“搭一套技术栈”，而是为了形成以下结果：

- • 统一交付：基于 GitOps 打通代码提交、镜像构建、配置发布和自动回滚
- • 统一运行：应用运行在标准化 Kubernetes 平台上，具备资源约束、自愈、伸缩和隔离能力
- • 统一观测：指标、日志、事件三位一体，面向系统运行质量和业务可用性建模
- • 统一治理：以 SLI/SLO 为核心，建立告警、值班、复盘、演练和容量规划闭环
- • 统一扩展：支持多环境、多命名空间、多业务线接入，满足未来多集群与多区域演进

---

## 二、总体架构设计

### 2.1 架构全景

```
┌────────────────────────────┐
                   │        开发者 / 平台工程师   │
                   └──────────────┬─────────────┘
                                  │
                        Git Push / Merge Request
                                  │
         ┌────────────────────────▼────────────────────────┐
         │                  GitLab CI                      │
         │  单元测试 / 代码扫描 / 镜像构建 / 镜像签名 / 推送 │
         └────────────────────────┬────────────────────────┘
                                  │
                          更新 GitOps 仓库
                                  │
                 ┌────────────────▼────────────────┐
                 │            Argo CD              │
                 │   期望状态管理 / 自动同步 / 回滚  │
                 └────────────────┬────────────────┘
                                  │
┌─────────────────────────────────▼─────────────────────────────────┐
│                      Kubernetes Production                        │
│  Ingress / Service / Deployment / HPA / PDB / NetworkPolicy      │
│  RuntimeClass / PriorityClass / LimitRange / ResourceQuota       │
└──────────────┬────────────────────────┬───────────────────────────┘
               │                        │
 ┌─────────────▼────────────┐  ┌────────▼───────────┐
 │  Observability Plane      │  │  Security Plane    │
 │  Prometheus / Alertmanager│  │  RBAC / OIDC       │
 │  Grafana / Loki / Tempo   │  │  Secret 管理        │
 └─────────────┬────────────┘  └────────┬───────────┘
               │                        │
 ┌─────────────▼────────────────────────▼─────────────┐
 │              SRE Control Loop                      │
 │  SLI/SLO -> Alert -> Oncall -> Mitigation -> RCA   │
 │  Capacity -> Chaos -> Review -> Optimization       │
 └────────────────────────────────────────────────────┘
```

### 2.2 架构设计原则

这套架构遵循五个核心原则：

1. 1\. **声明式优先**  
	集群资源、应用配置、告警规则、Dashboard 等都采用 Git 声明式管理，减少“手工改线上”的不可审计行为。
2. 2\. **控制面与数据面解耦**  
	GitLab 负责构建，Argo CD 负责交付，Kubernetes 负责调度运行，Prometheus/Loki 负责观测，避免单系统承担过多职责。
3. 3\. **平台标准化优先于个体优化**  
	对应用接入规定统一模板，包括健康检查、资源限制、监控暴露、日志规范、告警定义，提升整体治理效率。
4. 4\. **以用户感知为核心定义可靠性**  
	不是 CPU 高就告警，而是围绕成功率、延迟、饱和度和错误预算构建监控体系。
5. 5\. **为高并发和多团队协作预留扩展位**  
	组件选型和分层设计必须考虑未来接入更多业务、跨环境发布、多区域部署和容量弹性。

---

## 三、核心组件选型与原理分析

### 3.1 为什么选择 Kubernetes 作为基础设施底座

Kubernetes 的价值不只是容器编排，更重要的是它提供了一套统一的资源抽象与控制回路：

- • `Deployment` 维护副本期望状态
- • `Service` 提供稳定服务发现
- • `Ingress` 或网关负责南北向流量接入
- • `HPA` 根据指标自动扩缩容
- • `PDB` 限制中断预算，保证滚动变更安全
- • `Node Affinity` 、 `Taint/Toleration` 实现资源调度隔离

它本质上是一个不断把“当前状态”收敛到“期望状态”的分布式控制系统。SRE 落地的很多能力，例如自愈、弹性、标准化交付、发布回滚，都是建立在这套控制回路之上的。

### 3.2 为什么选择 Calico 而不是简单 Overlay 网络

在生产环境下，网络方案需要的不只是“能通”，更重要的是性能、策略和可观测性。

Calico 的优势主要体现在：

- • 支持三层路由和 BGP，减少额外 Overlay 开销
- • 支持细粒度 `NetworkPolicy` ，适合多业务线隔离
- • 与 Kubernetes 生态集成成熟，运维成本可控
- • 在多节点、大规模 Pod 网络场景下稳定性较好

对于存在多租户、内网服务隔离和数据库访问控制要求的环境，网络策略是平台治理的基础能力，而不是可选增强项。

### 3.3 为什么选择 Prometheus + Loki

很多团队在观测体系上容易出现两种误区：

- • 只做基础资源监控，不做业务指标监控
- • 只有日志，没有统一标签体系和关联分析能力

Prometheus 适合做时序指标采集与告警，Loki 则通过标签化日志降低存储和索引成本。两者与 Grafana 结合后，可以把“某接口 5xx 飙升”“对应 Pod 在过去 10 分钟的错误日志”“该节点是否存在资源争抢”串联起来，提高故障定位效率。

### 3.4 为什么采用 GitOps 而不是传统脚本发布

GitOps 的本质不是“用 Argo CD 替代 kubectl apply”，而是把系统期望状态放到 Git 中，让发布过程具备以下特征：

- • 可审计：任何配置变更都有提交记录和评审过程
- • 可回滚：回退就是回滚 Git 版本
- • 可复现：新环境可以通过同一套配置快速拉起
- • 可协作：研发、平台、SRE 通过同一事实源协作

一旦业务数量变多、环境变多、参与角色变多，基于脚本和人工的发布方式会迅速失控。

---

## 四、生产级 Kubernetes 平台落地设计

### 4.1 集群规划

典型生产环境采用如下规格：

- • 控制平面：3 台 Master 节点，跨可用区部署
- • 工作节点：按业务池拆分为通用节点池、计算密集型节点池、状态型服务节点池
- • 容器运行时： `containerd`
- • CNI： `Calico`
- • Ingress： `Nginx Ingress Controller` 或云厂商负载均衡接入
- • 存储： `Ceph RBD/CephFS` 、云盘 CSI 或高可用 NFS

### 4.2 多可用区与高可用设计

高可用不是“副本数 >= 2”这么简单，需要从多个层面同时保证：

- • Master 节点跨可用区，避免单机房故障导致控制面不可用
- • etcd 独立部署或保证磁盘性能，防止控制面抖动
- • 关键服务至少跨两个节点和两个可用区调度
- • 通过 `topologySpreadConstraints` 避免副本集中到单节点
- • 使用 `PodDisruptionBudget` 保证维护期间最小可用副本数

生产级应用部署示例如下：

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: prod
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      terminationGracePeriodSeconds: 60
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchExpressions:
                  - key: app
                    operator: In
                    values: ["payment-service"]
              topologyKey: kubernetes.io/hostname
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: payment-service
      containers:
        - name: app
          image: harbor.example.com/prod/payment-service:1.3.12
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2"
              memory: "1Gi"
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
          startupProbe:
            httpGet:
              path: /actuator/health
              port: 8080
            failureThreshold: 30
            periodSeconds: 5
```

### 4.3 资源治理与多租户隔离

当集群承载多个团队应用时，不做资源治理几乎一定会出问题。典型治理项包括：

- • `ResourceQuota` 限制命名空间总资源上限
- • `LimitRange` 限制默认 requests/limits，避免“裸奔 Pod”
- • `PriorityClass` 为核心服务提供抢占优先级
- • `NetworkPolicy` 限制跨服务访问
- • 命名空间级别的 RBAC，降低误操作风险

例如限制某命名空间的资源额度：

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: prod-quota
  namespace: prod
spec:
  hard:
    requests.cpu: "40"
    requests.memory: 80Gi
    limits.cpu: "80"
    limits.memory: 160Gi
    persistentvolumeclaims: "20"
    pods: "200"
```

### 4.4 安全治理

生产级云原生平台至少需要覆盖以下安全面：

- • 身份认证：OIDC 对接企业统一身份系统
- • 权限控制：RBAC 最小权限原则
- • 镜像安全：镜像漏洞扫描、镜像签名与准入校验
- • 密钥管理：Sealed Secrets 或 External Secrets 对接 Vault
- • 运行时安全：限制特权容器、只读根文件系统、Seccomp/AppArmor

平台侧推荐通过 OPA Gatekeeper 或 Kyverno 编写策略，禁止不合规工作负载直接进入集群，例如：

- • 禁止未配置 requests/limits 的 Deployment
- • 禁止使用 `latest` 标签
- • 禁止特权容器和宿主机网络

---

## 五、可观测性体系设计：从“看到”到“可治理”

### 5.1 监控分层

一套成熟的监控体系一般分三层：

1. 1\. **基础设施层**  
	节点 CPU、内存、磁盘、网络、容器重启、kubelet、etcd、API Server 状态
2. 2\. **平台中间件层**  
	Nginx Ingress、MySQL、Redis、Kafka、MQ、对象存储等核心依赖
3. 3\. **业务服务层**  
	请求量、成功率、错误率、P95/P99 延迟、线程池饱和、数据库连接池占用

如果只有前两层，就只能知道“机器忙不忙”，不知道“用户有没有受影响”。

### 5.2 SLI / SLO / Error Budget 的工程化落地

SRE 不是“多配几个告警规则”，而是先定义可靠性目标。

以支付服务为例：

- • SLI： `/api/payments` 接口 5 分钟窗口成功率
- • SLO：月度成功率不低于 `99.95%`
- • Error Budget：一个自然月允许的失败预算约为 `0.05%`

这套定义的意义在于：

- • 告警不再围绕机器状态，而围绕用户体验
- • 发布节奏可以和错误预算挂钩
- • 团队能客观讨论“当前是否为了新功能透支稳定性”

PromQL 示例：

```
sum(rate(http_requests_total{app="payment-service",status!~"5.."}[5m]))
/
sum(rate(http_requests_total{app="payment-service"}[5m]))
```

用于监控 P99 延迟：

```
histogram_quantile(
  0.99,
  sum(rate(http_server_requests_seconds_bucket{app="payment-service"}[5m])) by (le)
)
```

### 5.3 告警设计原则

生产环境下，最怕的不是没有告警，而是告警风暴。告警必须满足三个条件：

- • 能反映真实用户影响
- • 有明确处理动作
- • 尽量减少噪音和重复

推荐按四级设计：

- • `P1` ：用户核心路径故障，需立即升级处理
- • `P2` ：核心服务存在明显退化，需快速介入
- • `P3` ：潜在风险或容量临界，需当天处理
- • `Info` ：趋势提醒，用于治理而非叫醒值班

燃烧率告警示例：

```
groups:
  - name: sre-slo-alerts
    rules:
      - alert: PaymentServiceHighErrorBudgetBurn
        expr: |
          (
            1 -
            (
              sum(rate(http_requests_total{app="payment-service",status!~"5.."}[5m]))
              /
              sum(rate(http_requests_total{app="payment-service"}[5m]))
            )
          ) > 0.02
        for: 10m
        labels:
          severity: critical
          service: payment-service
        annotations:
          summary: "payment-service 错误预算消耗过快"
          description: "过去 10 分钟错误率持续高于阈值，请检查上游依赖、发布变更和节点资源。"
```

### 5.4 日志体系设计

日志平台设计的关键不在“把日志收上来”，而在于是否支持按业务、实例、链路快速检索和关联分析。

推荐日志标准字段：

- • `timestamp`
- • `traceId`
- • `spanId`
- • `level`
- • `service`
- • `namespace`
- • `pod`
- • `node`
- • `message`
- • `errorCode`
- • `userId` 或 `orderId` 等业务定位字段

Loki 中的标签不宜过多，尤其不能把高基数字段直接做 label，否则会引发索引膨胀和查询性能下降。适合作为标签的是：

- • `cluster`
- • `namespace`
- • `app`
- • `container`
- • `level`

不适合作为标签的是：

- • `requestId`
- • `userId`
- • `orderId`

Loki 告警示例：

```
sum by (app) (
  count_over_time({namespace="prod", app="payment-service"} |= "TimeoutException" [5m])
) > 20
```

---

## 六、GitOps 持续交付体系设计

### 6.1 发布链路

完整交付链路如下：

```
开发提交代码
  -> GitLab CI 执行 lint / test / build
  -> 构建 Docker 镜像并推送 Harbor
  -> 更新 GitOps 配置仓库中的镜像 Tag
  -> Argo CD 检测配置变化
  -> 自动同步到目标环境
  -> Prometheus / Grafana 验证发布后状态
  -> 异常时自动或人工回滚
```

### 6.2 为什么 GitOps 更适合多环境治理

随着环境数量增加，手工发布会遇到三个核心问题：

- • 版本漂移：测试环境和生产环境配置不一致
- • 权责不清：谁改了配置无法追踪
- • 回滚不稳定：回滚依赖人工记忆和临时脚本

GitOps 通过把环境差异固化在 Kustomize 或 Helm values 中，天然适合管理 `dev` 、 `staging` 、 `prod` 等多环境。

### 6.3 GitLab CI 生产级示例

```
stages:
  - test
  - build
  - deploy-config

variables:
  IMAGE_NAME: harbor.example.com/prod/payment-service
  IMAGE_TAG: $CI_COMMIT_SHORT_SHA

unit_test:
  stage: test
  image: maven:3.9-eclipse-temurin-17
  script:
    - mvn -B clean test
  only:
    - merge_requests
    - main

docker_build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
    - docker push ${IMAGE_NAME}:${IMAGE_TAG}
  only:
    - main

update_gitops:
  stage: deploy-config
  image: alpine:3.20
  before_script:
    - apk add --no-cache git yq
  script:
    - git clone https://gitlab.example.com/platform/gitops-repo.git
    - cd gitops-repo/apps/payment-service/overlays/prod
    - yq -i '.images[0].newTag = env(IMAGE_TAG)' kustomization.yaml
    - git config user.email "ci-bot@example.com"
    - git config user.name "ci-bot"
    - git commit -am "release payment-service ${IMAGE_TAG}"
    - git push origin main
  only:
    - main
```

### 6.4 Argo CD 应用定义示例

```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service-prod
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://gitlab.example.com/platform/gitops-repo.git
    targetRevision: main
    path: apps/payment-service/overlays/prod
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

`selfHeal` 的价值在于：即使有人手工改动线上资源，Argo CD 也会把实际状态重新拉回 Git 定义的期望状态。

---

## 七、SRE 核心实践：把“稳定性”变成工程系统

### 7.1 健康检查、自愈与优雅终止

很多服务虽然“部署成功”，但并不具备真正生产可用的运行特征。比如：

- • 应用还没完成预热就开始接流量
- • Pod 被 kill 时没有优雅下线，导致请求中断
- • 下游数据库抖动时，健康检查误判触发连锁重启

因此需要区分三类探针：

- • `startupProbe` ：应用是否完成启动
- • `readinessProbe` ：是否可以接流量
- • `livenessProbe` ：是否需要重启

同时应用侧需要正确处理 `SIGTERM` ，让连接摘除、任务收尾和事务提交有足够时间。

### 7.2 弹性伸缩：从 CPU 指标走向业务指标

很多团队最初只基于 CPU 做 HPA，但高并发系统中 CPU 不一定是瓶颈，真实瓶颈可能在：

- • 请求队列积压
- • 数据库连接池耗尽
- • Kafka 消费 lag 持续增长
- • 网关 QPS 激增而业务线程池饱和

因此生产环境推荐基于多指标弹性策略，例如 CPU + 自定义 QPS。

HPA 示例：

```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: payment-service
  namespace: prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: payment-service
  minReplicas: 4
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "120"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
        - type: Percent
          value: 100
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 20
          periodSeconds: 60
```

### 7.3 发布稳定性：滚动更新、金丝雀与回滚

SRE 不只关注“线上故障后怎么救火”，更关注“如何减少故障进入生产”。

平台上线后，推荐逐步采用以下发布策略：

- • 默认滚动更新：适合大多数无状态服务
- • 金丝雀发布：对高风险版本先引流少量流量验证
- • 蓝绿发布：对核心交易系统提供更可控切换
- • 自动回滚：发布后关键指标异常触发回退

如果接入服务网格或 Ingress 灰度能力，可以实现更细粒度流量控制，例如：

- • 按流量百分比分批放量
- • 按地区或租户分批发布

### 7.4 混沌工程与故障演练

没有演练过的高可用，通常只是一种假设。

混沌工程的价值不在于“制造破坏”，而在于验证以下事实：

- • 服务是否真的具备自愈能力
- • 告警是否能及时发现异常
- • 值班流程是否能在可接受时间内收敛故障
- • 架构中是否存在单点依赖

典型演练场景包括：

- • 随机删除核心服务 Pod
- • 注入节点不可用
- • 模拟服务间网络延迟和丢包
- • 压测时叠加缓存失效场景
- • 模拟数据库主从切换或连接超时

Chaos Mesh 示例：

```
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: payment-service-pod-kill
  namespace: chaos-testing
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces:
      - prod
    labelSelectors:
      app: payment-service
  duration: "30s"
```

---

## 八、高并发场景下的工程化升级

### 8.1 高并发系统的四类瓶颈

一个看起来“容器化完成”的系统，在高并发场景下通常会卡在以下四层之一：

1. 1\. **入口层瓶颈**  
	Ingress、网关连接数不足，TLS 握手开销大，负载均衡不均
2. 2\. **服务层瓶颈**  
	线程池、连接池、JVM 堆、GC、同步锁竞争
3. 3\. **数据层瓶颈**  
	MySQL 热点行争抢、慢 SQL、Redis 大 Key、缓存击穿
4. 4\. **基础设施层瓶颈**  
	节点 CPU 抢占、磁盘 IO 饱和、跨可用区网络延迟、容器网络抖动

因此平台治理不能只盯着 Pod 数量，还要有系统化容量模型。

### 8.2 容量治理方法

容量规划建议按如下方式进行：

- • 基于 Prometheus 历史数据提取高峰 QPS、CPU、内存、网络趋势
- • 建立“单 Pod 吞吐能力”基准值
- • 按业务活动日、营销峰值、节假日做系数放大
- • 预留故障冗余，例如 N+1 节点冗余或单 AZ 故障冗余

简化计算公式：

```
目标副本数 = 峰值 QPS / 单 Pod 安全承载 QPS * 冗余系数
```

例如：

- • 峰值 QPS = 3600
- • 单 Pod 安全承载 QPS = 180
- • 冗余系数 = 1.5

则推荐副本数约为：

```
3600 / 180 * 1.5 = 30
```

这时 HPA 的 `maxReplicas` 、节点池容量、数据库连接池上限都必须一起校准，而不是只改一个参数。

### 8.3 缓存、削峰与异步化

在高并发场景下，平台稳定性和应用架构必须共同设计：

- • 热点接口前置本地缓存或 Redis 缓存
- • 使用消息队列削峰，把同步重处理流程改为异步事件流
- • 对非核心链路做限流和降级
- • 为下游不稳定依赖设置超时、重试、熔断和隔离舱

平台侧则通过以下方式协同：

- • 为高优先级业务设置专属节点池
- • 对异步消费服务设置与 lag 关联的弹性扩容规则
- • 对网关设置连接数、请求体、限流规则
- • 对关键链路建立 Dashboard 和专项告警

---

## 九、一个完整实战案例：支付服务的稳定性治理

### 9.1 场景描述

支付服务是核心交易路径，日常流量稳定，但在营销活动期间会出现 6 到 10 倍突增。历史上该服务出现过以下问题：

- • 发布后 readiness 检查过早通过，流量进入未预热实例
- • HPA 只看 CPU，实际瓶颈在数据库连接池
- • 错误日志很多，但没有和接口错误率建立关联
- • 节点维护时未配置 PDB，导致副本同时驱逐

### 9.2 解决方案

平台和应用联合完成如下治理：

- • 应用改造健康检查接口，增加预热状态判断
- • 为数据库连接池、线程池、接口延迟暴露 Micrometer 指标
- • HPA 从单一 CPU 扩展为 CPU + QPS 复合扩缩容
- • 为支付服务补充 `PDB` 、反亲和和跨可用区分散调度
- • 构建支付服务专项 Dashboard，纳入成功率、P99、连接池、重启次数、异常日志量
- • 发布阶段采用 10% -> 30% -> 100% 渐进放量

PDB 示例：

```
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: payment-service-pdb
  namespace: prod
spec:
  minAvailable: 3
  selector:
    matchLabels:
      app: payment-service
```

### 9.3 治理效果

治理完成后，核心收益通常体现在以下维度：

- • 发布失败率显著下降
- • 高峰期扩容更平滑，避免 CPU 还没高但连接池已打满
- • 节点维护不再引发服务整体抖动
- • 告警从“机器有点忙”转向“支付成功率下降”
- • 故障定位从 30 分钟缩短到 5 到 10 分钟

如果把项目写进简历或述职，建议输出量化结果，例如：

- • 发布耗时从 30 分钟缩短到 5 分钟
- • 核心服务 MTTR 从 45 分钟下降到 12 分钟
- • 生产故障中因配置变更导致的问题占比下降 60%
- • 日志检索和问题定位效率提升 70%
- • 高峰期资源利用率提升 25%，同时维持 SLO 达标

---

## 十、生产级代码与配置补全建议

### 10.1 应用必须暴露的指标

如果业务是 Java Spring Boot，推荐通过 Micrometer 暴露以下关键指标：

- • HTTP 请求数、状态码、延迟分布
- • JVM 堆、GC、线程池
- • 数据库连接池活跃数、等待数、超时数
- • 缓存命中率
- • MQ 消费 lag 或积压量

示例：

```
@Bean
MeterBinder paymentMetrics(ThreadPoolTaskExecutor executor, DataSource dataSource) {
    return registry -> {
        Gauge.builder("payment_executor_active_count",
                executor.getThreadPoolExecutor(),
                ThreadPoolExecutor::getActiveCount)
            .tag("service", "payment-service")
            .register(registry);

        if (dataSource instanceof HikariDataSource hikari) {
            Gauge.builder("payment_db_connections_active",
                    hikari.getHikariPoolMXBean(),
                    bean -> bean.getActiveConnections())
                .tag("service", "payment-service")
                .register(registry);
        }
    };
}
```

### 10.2 优雅停机代码示例

```
@Component
public class GracefulShutdown implements SmartLifecycle {

    private final AtomicBoolean running = new AtomicBoolean(false);

    @Override
    public void start() {
        running.set(true);
    }

    @Override
    public void stop() {
        running.set(false);
        try {
            Thread.sleep(15000L);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    @Override
    public boolean isRunning() {
        return running.get();
    }
}
```

这个实现需要和 `readinessProbe` 联动，在收到终止信号后先摘流量，再等待存量请求完成，避免滚动发布时请求被硬切断。

### 10.3 NetworkPolicy 示例

```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-gateway-to-payment
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: payment-service
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: gateway
          podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - protocol: TCP
          port: 8080
```

---

## 十一、项目实施路径与阶段拆分

为了避免平台项目“周期很长、收益滞后”，建议按阶段推进：

### 阶段一：基础平台可用

- • 搭建 Kubernetes 高可用集群
- • 建立基础镜像仓库和 CI 流水线
- • 完成 Ingress、存储、日志采集和基础监控接入
- • 首批应用容器化迁移

### 阶段二：交付标准化

- • 引入 Argo CD 和 GitOps 仓库
- • 统一 Helm/Kustomize 模板
- • 配置规范化的健康检查、资源限制和告警模板
- • 建立发布回滚流程

### 阶段三：SRE 治理闭环

- • 定义关键业务 SLI/SLO
- • 建立错误预算和告警分级机制
- • 落地值班、升级、复盘制度
- • 开展定期混沌演练和容量评审

### 阶段四：高阶能力演进

- • 引入服务网格，实现灰度与流量治理
- • 建立多集群和多区域交付能力
- • 结合成本监控做 FinOps 优化
- • 推进自动化故障缓解与自愈

---

## 十二、面试 / 答辩高频问题与回答思路

### 12.1 为什么要用 SLO，而不是只看 CPU、内存告警

因为资源告警只反映系统内部状态，不一定代表用户受影响；SLO 则直接衡量用户体验和业务目标，更适合作为稳定性管理指标。

### 12.2 Prometheus 单点怎么办

生产环境可采用 Prometheus Operator + 多副本采集，配合 Thanos 或 VictoriaMetrics 做长期存储与统一查询；Alertmanager 也可做集群化部署。

### 12.3 Loki 和 ELK 怎么选

如果日志场景主要是云原生应用排障与按标签检索，Loki 成本和接入复杂度更优；如果需要复杂全文搜索、日志分析加工和大规模异构数据处理，ELK 更强，但运维成本也更高。

### 12.4 GitOps 如何管理敏感信息

不要把明文密码直接放到 Git；推荐使用 Sealed Secrets、External Secrets Operator 或 Vault 集成，在 Git 中只保留加密态或引用关系。

### 12.5 高并发场景下 HPA 为什么可能失效

因为 HPA 扩容需要时间，而突发流量可能在几十秒内到达；如果只依赖 CPU 指标，往往已经晚于连接池和线程池饱和。因此需要预热副本、业务指标扩容、节点容量预留和流量削峰联动。

---

## 十三、结语：平台建设的真正价值

云原生基础设施和 SRE 落地，真正要解决的不是“组件是否先进”，而是让系统具备三种长期能力：

- • 更快地交付变化
- • 更稳地承接流量和故障
- • 更低成本地支持业务增长

一个成熟的平台项目，最终产出不只是 Kubernetes 集群、Prometheus 面板或 Argo CD 页面，而是一套工程秩序：研发知道如何接入，平台知道如何治理，SRE 知道如何衡量和改进，业务团队知道系统在高并发和故障场景下仍然可信。

如果把这类项目写进简历、述职或技术分享，建议一定要突出三点：

- • 架构设计是否体现了系统性思考
- • 工程落地是否支撑了高并发和多团队协作
- • 稳定性治理是否形成可量化、可复盘、可持续优化的闭环

做到这三点，这个项目就不再只是“搭过一套 K8s 平台”，而是真正具备了高级基础设施工程师、云原生架构师和 SRE 负责人的项目深度。

**微信扫一扫赞赏作者**

作者提示: 个人观点，仅供参考

继续滑动看下一个

Ray的银河技术

向上滑动看下一个