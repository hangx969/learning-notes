---
title: Kubernetes
tags:
  - knowledgebase/entity
  - docker-kubernetes
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/k8s-basic-resources-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-installation-management-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-CICD-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-security-auth-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-scaling-storage-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-db-middleware-UI-batch-summary]]"
  - "[[KnowledgeBase/sources/k8s-misc-batch-summary]]"
---

# Kubernetes

## 简介

Kubernetes（K8s）是容器编排平台，源自 Google Borg 系统，2014 年开源，2018 年从 CNCF 毕业。本仓库以 **145 篇文章**覆盖了 K8s 全生命周期，包括基础资源、集群安装与管理、监控日志、CI/CD、网络与服务网格、安全认证、扩缩容、存储、数据库中间件、UI 工具、备份恢复、GPU 配置、认证考试等主题。全部源文档的详细摘要见上方 `sources` 中列出的 9 份批量摘要页面。

## 核心架构知识（从 145 篇中提炼）

### 控制平面与数据平面
- **API Server**：所有组件通信的中枢，唯一与 etcd 交互的组件
- **Scheduler**：监听未绑定节点的 Pod 并执行调度算法，支持 NodeResourceFit 插件的三种评分策略（LeastAllocated、MostAllocated、RequestedToCapacityRatio）
- **Controller Manager**：运行控制器循环，管理 Deployment、StatefulSet、DaemonSet 等工作负载的期望状态
- **etcd**：分布式键值存储，高可用需至少 3 节点，故障恢复通过 `etcdctl member remove/add` 实现
- **kubelet**：节点代理，管理 Pod 生命周期，默认日志限制 containerLogMaxSize 10Mi / containerLogMaxFiles 5
- **kube-proxy**：三种模式（Userspace、iptables、IPVS），IPVS 基于哈希表性能更优；v1.29 引入 nftables（Alpha）

### 声明式资源模型
- 所有资源通过 YAML 定义期望状态，由控制器自动实现：apiVersion、kind、metadata、spec、status
- **Pause 容器**：Pod 内所有容器的网络和存储共享根，容器间通过 localhost 互访
- **Operator = CRD + Controller**：无需修改 K8s 源码即可扩展 API，适合复杂有状态应用管理

### 网络体系三层协同
- **Calico**（底层网络连通性）：IPIP 模式隧道封装配置简单，BGP 模式直接路由性能更优
- **Service**（四层负载均衡）：通过标签选择器匹配 Pod，iptables/IPVS 转发规则
- **Ingress**（七层负载均衡）：流量直接从 Ingress Controller 到 Pod，不经过 Service；生产推荐独占节点 + hostNetwork:true + 前端网关

### 容器运行时演进
- CRI 标准化接口支持 containerd、CRI-O、Kata 等运行时
- 调用链：K8s -> containerd -> RunC
- K8s 1.24+ 全面转向 containerd，从 Docker 迁移步骤：cordon/drain -> 卸载 Docker -> 安装 containerd -> 修改 kubelet 配置

## 本仓库知识覆盖地图

### 基础资源（20 篇）
详见 [[KnowledgeBase/sources/k8s-basic-resources-batch-summary|k8s-basic-resources 批量摘要]]

覆盖 Pod、Deployment（滚动更新 maxSurge/maxUnavailable）、StatefulSet（Headless Service + volumeClaimTemplates）、DaemonSet、Job/CronJob、Service、Ingress、ConfigMap/Secret、Storage（EmptyDir/HostPath/NFS/PV/PVC）、Namespace 资源分配（ResourceQuota/LimitRange）、Calico 网络、kubeadm 集群搭建、容器运行时 containerd、CRD/Operator、认证授权 RBAC、临时容器 Ephemeral、YAML 编写规范、Python K8s API 编程。

**核心要点**：
- Deployment 仅 `spec.template` 变化才触发更新，产生新 ReplicaSet
- StatefulSet 基于 Headless Service 为 Pod 分配固定 DNS：`pod-name.svc-name.ns.svc.cluster.local`
- 生产环境必须对每个 Namespace 限制 Pod/RS 数量，防止异常激增拖垮集群
- K8s 1.24 后不再自动为 ServiceAccount 创建 Secret，需手动创建 Token

### 安装与管理（16 篇）
详见 [[KnowledgeBase/sources/k8s-installation-management-batch-summary|k8s-installation-management 批量摘要]]

覆盖 k8s 1.20 至 1.35 多版本 kubeadm 安装（CentOS -> Rocky Linux 迁移路径）、二进制安装高可用集群（keepalived + nginx）、企业级高可用集群规划、etcd 高可用配置与故障恢复、两地三中心与异地多活架构（Karmada、智能 DNS/GTM）、生产环境优化最佳实践、容器运行时迁移与版本升级、故障排查指南、多集群 kubeconfig 管理。

**核心要点**：
- 生产环境控制节点资源：0-100 节点用 8C+32G，100-250 用 16C+32G，250-500 需 etcd 分离
- 3 master 可管理约 900 个 worker 节点
- Pod 状态排查：Pending（资源/调度问题）、ImagePullBackOff（镜像问题）、CrashLoopBackOff（代码/权限问题）、Evicted（资源不足）
- kubeadm 配置 API 演进：v1beta2 -> v1beta3 -> v1beta4

### 监控与日志（20 篇）
详见 [[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary|k8s-monitoring-logging 批量摘要]]

**监控**：[[KnowledgeBase/entities/Prometheus|Prometheus]] 基础与多版本部署、联邦集群、Helm 部署 kube-prometheus-stack 全家桶、Alertmanager 告警、监控 K8s 系统组件/外部集群/非云原生应用、[[KnowledgeBase/entities/Grafana|Grafana]] 可视化。

**日志**：EFK/ELK 多种部署形态（K8s 容器化、二进制、ECK Operator）、Loki+Promtail 轻量方案、K8s Events 持久化。

**链路追踪**：SkyWalking（低侵入字节码注入）和 Jaeger（CNCF 项目，Uber 开源）。

**核心要点**：
- Prometheus 存储效率：每采样 3.5 bytes，300 万时间序列 30s 间隔 60 天约 200G
- 日志收集器轻量化趋势：Logstash -> Fluentd -> Filebeat/Fluent-bit
- EFK 适合 TB 级大规模日志，Loki 适合轻量级场景
- Kafka 作为缓冲层解决高吞吐日志延迟：Fluentd -> Kafka -> Logstash -> ES

### CI/CD（19 篇）
详见 [[KnowledgeBase/sources/k8s-CICD-batch-summary|k8s-CICD 批量摘要]]

覆盖 [[KnowledgeBase/entities/ArgoCD|ArgoCD]]（GitOps 持续交付、Image Updater、DNS 排查）、[[KnowledgeBase/entities/Jenkins|Jenkins]]（多版本部署、Pipeline 语法、DevOps 平台落地）、Tekton（云原生 Pipeline）、[[KnowledgeBase/entities/Kustomize|Kustomize]]（Base+Overlay 配置定制）、GitHub Actions（Self-hosted Runner）、多语言应用发布（Go/Python/Java）。

**核心要点**：
- GitOps（ArgoCD Pull 模式）vs 传统 CI/CD（Jenkins Push 模式）两种部署哲学
- 通用发版流程：GitLab 提交 -> Jenkins 构建 -> Docker 镜像 -> Harbor 推送 -> K8s 部署
- Tekton 核心优势：云原生、标准化 CRD、事件驱动，Pipeline 直接映射为 K8s Pod
- 云原生演进：Jenkins（VM 时代）-> Tekton（K8s 原生）-> ArgoCD（GitOps）

### 网络与服务网格（7 篇）
详见 [[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary|k8s-networking-service-mesh 批量摘要]]

覆盖 Ingress-Nginx 部署（hostNetwork + ClusterFirstWithHostNet）、External-DNS 域名自动同步、[[KnowledgeBase/entities/Istio|Istio]] 多版本部署与流量管理（熔断/超时/重试）、企业项目接入 Istio 实战、集群网络安全工具（kube-bench、kube-hunter、kubeaudit、Polaris）。

**核心要点**：
- 南北流量（Ingress-Nginx）vs 东西流量（Istio）协同工作
- Istio 1.5+ 将 Pilot/Mixer/Citadel 整合为 istiod 单体
- 服务网格 vs SpringCloud/Nacos：语言无关、无需侵入业务代码
- CVE-2019-5736：Docker 18.09.2 以下 runC 漏洞可提权

### 安全与认证（7 篇）
详见 [[KnowledgeBase/sources/k8s-security-auth-batch-summary|k8s-security-auth 批量摘要]]

覆盖 Capsule 多租户管理、Cert-Manager 证书自动化（ACME/Let's Encrypt）、External Secrets（Azure Key Vault 同步）、Kyverno 策略引擎、OAuth2 Proxy 身份认证、SonarQube 代码质量扫描、Trivy Operator 镜像漏洞扫描。

**核心要点**：
- 安全工具链：Kyverno（准入控制）+ Trivy（镜像扫描）+ SonarQube（代码扫描）构成从代码到运行时的完整安全防线
- Cert-Manager 核心资源：ClusterIssuer/Issuer + Certificate -> K8s Secret
- Capsule Tenant：一组 Namespace 的逻辑分组，RBAC + ResourceQuota + NetworkPolicy 策略隔离

### 扩缩容与存储（7 篇）
详见 [[KnowledgeBase/sources/k8s-scaling-storage-batch-summary|k8s-scaling-storage 批量摘要]]

**扩缩容四层体系**：HPA（Pod 水平，基于 CPU/内存）-> VPA（Pod 垂直，调整 request/limit）-> KEDA（事件驱动，支持缩容到 0）-> Cluster Autoscaler（节点级别弹性）。Goldilocks 提供 VPA 推荐值可视化。

**存储三种方案**：NFS（简单但非高可用）-> CubeFS（云原生友好但无块存储）-> Ceph（功能全面但运维复杂，支持 RBD/CephFS/RADOS Gateway 三种类型）。

**核心要点**：
- HPA 算法：`sum(实际使用量) / 使用率限额 + 1`，默认 30s 检测、5min 稳定期
- KEDA 支持数十种外部事件源（Kafka、RabbitMQ、HTTP、Cron 等），独特优势是缩容到 0
- Ceph 生产环境强烈建议二进制安装在服务器上，不要装在 K8s 中
- NFS exports 配置需写宿主机网段（非 Pod 网段），因 PV 先挂载到宿主机再挂载到 Pod

### 数据库中间件与 UI 工具（18 篇）
详见 [[KnowledgeBase/sources/k8s-db-middleware-UI-batch-summary|k8s-db-middleware-UI 批量摘要]]

**数据库部署**（三种范式对比）：原生 YAML（学习底层）、Helm Chart（标准化配置）、Operator（自动化运维）。覆盖 MySQL（NDB Operator/Helm/YAML 主从）、PostgreSQL HA（Pgpool+repmgr）、Redis（Cluster 模式 3主3从）、MongoDB（副本集/分片）、Kafka（Strimzi Operator）。

**UI 工具链**：Dashboard（Web 原生）、Kuboard（国产增强）、Lens（桌面 IDE，内置 Prometheus）、k9s（终端 TUI，Vim 风格）、Rancher（企业级多集群管理平台）、krew 插件管理器。

### 杂项专题（18 篇）
详见 [[KnowledgeBase/sources/k8s-misc-batch-summary|k8s-misc 批量摘要]]

覆盖 [[KnowledgeBase/entities/Helm|Helm]] v3 安装与使用、Config Syncer 跨 Namespace 同步、Dragonfly P2P 镜像分发（100 节点拉取 2GB 镜像可节约 99% 带宽）、Reloader 配置变更自动重启、CKA/CKS 认证备考、KubeBlocks 统一数据库管理、Harbor 镜像仓库（docker-compose/Helm/KubeBlocks 三种部署方式）、OpenShift（企业 PaaS）、K3S（轻量级边缘计算，仅需 512M 内存）、SpringCloud 迁移到 K8s、Velero 备份恢复（不推荐用于数据库，应使用 mysqldump/pg_dump）、K8s 配置 NVIDIA GPU（Device Plugin + taint 隔离）。

## 相关概念与实体

| 领域 | 核心实体 |
|------|----------|
| 容器基础 | [[KnowledgeBase/entities/Docker|Docker]]、[[KnowledgeBase/entities/containerd|containerd]] |
| 包管理与配置 | [[KnowledgeBase/entities/Helm|Helm]]、[[KnowledgeBase/entities/Kustomize|Kustomize]] |
| 网络与代理 | [[KnowledgeBase/entities/Ingress|Ingress]]、[[KnowledgeBase/entities/Istio|Istio]]、[[KnowledgeBase/entities/Calico|Calico]] |
| 监控与日志 | [[KnowledgeBase/entities/Prometheus|Prometheus]]、[[KnowledgeBase/entities/Grafana|Grafana]]、[[KnowledgeBase/entities/Loki|Loki]]、[[KnowledgeBase/entities/Alertmanager|Alertmanager]] |
| CI/CD | [[KnowledgeBase/entities/ArgoCD|ArgoCD]]、[[KnowledgeBase/entities/Jenkins|Jenkins]]、[[KnowledgeBase/entities/Tekton|Tekton]]、[[KnowledgeBase/entities/GitLab|GitLab]] |
| 安全 | [[KnowledgeBase/entities/Kyverno|Kyverno]]、[[KnowledgeBase/entities/Cert-Manager|Cert-Manager]]、[[KnowledgeBase/entities/Trivy|Trivy]] |
| 存储 | [[KnowledgeBase/entities/Ceph|Ceph]]、[[KnowledgeBase/entities/CubeFS|CubeFS]]、[[KnowledgeBase/entities/NFS|NFS]] |
| 数据库 | [[KnowledgeBase/entities/MySQL|MySQL]]、[[KnowledgeBase/entities/Redis|Redis]]、[[KnowledgeBase/entities/PostgreSQL|PostgreSQL]]、[[KnowledgeBase/entities/Kafka|Kafka]] |
| 集群管理 | [[KnowledgeBase/entities/Rancher|Rancher]]、[[KnowledgeBase/entities/K3S|K3S]]、[[KnowledgeBase/entities/Velero|Velero]]、[[KnowledgeBase/entities/KubeBlocks|KubeBlocks]] |

## 知识空白

- **Gateway API**：K8s 新一代入口 API，将逐步替代 Ingress 资源
- **多集群管理与联邦**：Karmada 已提及但未深入实践，Liqo、Submariner 等方案未覆盖
- **FinOps 成本优化**：Kubecost、OpenCost 等成本可视化工具未涉及
- **GitOps 进阶**：Flux CD 未覆盖，ArgoCD ApplicationSet 和多租户 GitOps 实践不足
- **eBPF 网络方案**：Cilium 作为下一代 CNI 未涉及
- **Serverless**：Knative 仅在 KPA 扩缩容中提及，完整 Serverless 方案缺失
- **混沌工程**：Chaos Mesh、Litmus 等故障注入工具未覆盖
- **Service Mesh 新方案**：Ambient Mesh（无 Sidecar 的 Istio）、Linkerd 未深入
