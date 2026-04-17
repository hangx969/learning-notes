---
title: 知识库入口
tags:
  - knowledgebase/index
  - knowledgebase/navigation
aliases:
  - 知识库首页
  - KB Index
date: 2026-04-17
---

# 📚 Learning Notes 知识库

> [!info] 知识库说明
> 本知识库基于 [Karpathy LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 构建。
> 原始来源（顶层主题目录）只读不改，LLM 在本目录中生成和维护所有编译内容。
>
> - **Schema 文件**：[CLAUDE.md](../CLAUDE.md)
> - **操作日志**：[log.md](log.md)
> - **扫描日期**：2026-04-17
> - **核心定位**：云原生运维工程师的全栈技术知识库

---

## 🧠 概念页（Concepts）

抽象概念的独立知识页面。

| 页面 | 摘要 |
|------|------|
| [CICD](concepts/CICD.md) | 持续集成与持续交付，覆盖 Jenkins、ArgoCD、GitLab CI、Tekton 等工具链 |
| [Observability](concepts/Observability.md) | 可观测性三大支柱：日志、指标、链路追踪 |
| [日志系统](concepts/日志系统.md) | EFK/ELK、Loki 等日志采集与分析方案 |
| [服务网格](concepts/服务网格.md) | Istio 为代表的服务网格架构与流量管理 |
| [容器运行时](concepts/容器运行时.md) | containerd、Docker Engine 等容器运行时技术 |
| [自动化运维](concepts/自动化运维.md) | Ansible、Python 脚本、Terraform 等自动化运维实践 |
| [Python运维开发](concepts/Python运维开发.md) | Python 在运维场景中的应用：自动化脚本、Web 运维平台、API 调用 |

---

## 🔧 实体页（Entities）

具体工具、平台、项目的独立知识页面。

| 页面 | 摘要 |
|------|------|
| [Kubernetes](entities/Kubernetes.md) | 容器编排平台，145 篇文章覆盖全生命周期 |
| [Docker](entities/Docker.md) | 容器运行时，12 篇覆盖基础与服务部署实战 |
| [Helm](entities/Helm.md) | Kubernetes 包管理器 |
| [ArgoCD](entities/ArgoCD.md) | GitOps 持续交付工具 |
| [Jenkins](entities/Jenkins.md) | CI/CD 自动化服务器 |
| [Prometheus](entities/Prometheus.md) | 云原生监控系统 |
| [Grafana](entities/Grafana.md) | 可视化与仪表盘平台 |
| [Istio](entities/Istio.md) | 服务网格平台 |
| [Ingress](entities/Ingress.md) | Kubernetes 入口控制器 |
| [Azure](entities/Azure.md) | Microsoft 公有云平台 |
| [AKS](entities/AKS.md) | Azure 托管 Kubernetes 服务 |
| [Aliyun](entities/Aliyun.md) | 阿里云公有云平台 |
| [Terraform](entities/Terraform.md) | 基础设施即代码工具 |
| [Claude-Code](entities/Claude-Code.md) | AI 编程助手 |
| [MCP](entities/MCP.md) | Model Context Protocol |
| [OpenClaw](entities/OpenClaw.md) | 开源 AI 工具平台 |
| [Obsidian](entities/Obsidian.md) | 知识管理与笔记工具 |
| [Slurm](entities/Slurm.md) | HPC 作业调度系统 |
| [Harbor](entities/Harbor.md) | 企业级容器镜像仓库（stub） |
| [Redis](entities/Redis.md) | 高性能键值数据库（stub） |
| [GitLab](entities/GitLab.md) | DevOps 全生命周期平台（stub） |
| [Kafka](entities/Kafka.md) | 分布式消息队列/事件流平台（stub） |
| [Loki](entities/Loki.md) | 轻量级日志聚合系统（stub） |
| [MySQL](entities/MySQL.md) | 开源关系型数据库（stub） |
| [NVIDIA](entities/NVIDIA.md) | GPU 硬件厂商（stub） |
| [PBS](entities/PBS.md) | HPC 作业调度系统（stub） |
| [containerd](entities/containerd.md) | K8s 默认容器运行时（stub） |
| [CUDA](entities/CUDA.md) | NVIDIA GPU 计算平台（stub） |
| [Calico](entities/Calico.md) | K8s CNI 网络插件（stub） |
| [Docker Compose](entities/Docker-Compose.md) | 单机多容器编排工具（stub） |
| [Kustomize](entities/Kustomize.md) | K8s 原生配置管理工具（stub） |
| [NFS](entities/NFS.md) | 网络文件系统存储（stub） |
| [Nginx](entities/Nginx.md) | Web 服务器与反向代理（stub） |
| [PostgreSQL](entities/PostgreSQL.md) | 开源关系型数据库（stub） |
| [Rancher](entities/Rancher.md) | K8s 多集群管理平台（stub） |

---

## 📄 来源摘要（Sources）

每篇原始来源文档的知识提炼摘要。

### AI/ClaudeCode（已摄入 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [ClaudeCode基础指南](sources/ClaudeCode基础指南-summary.md) | [AI/ClaudeCode/ClaudeCode基础指南](../AI/ClaudeCode/ClaudeCode基础指南.md) | 3 种模式、Extended Thinking、Claude.md、Spec 工作流、5 大实战场景 |
| [扩展体系](sources/Claude-Code扩展体系-summary.md) | [AI/ClaudeCode/Claude Code 扩展体系](../AI/ClaudeCode/Claude%20Code%20扩展体系.md) | 四层扩展机制全解：MCP（10+ 服务器）、Skills（3 层模式）、Slash Commands、Plugin |
| [多智能体协作](sources/多智能体协作-summary.md) | [AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams](../AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams.md) | Subagents（5 组件、适用场景评级）+ Agent Teams（Team Lead/Teammates/Task List/Mailbox） |
| [Obsidian+Claude知识库](sources/obsidian-claude-搭建个人知识库-summary.md) | [AI/ClaudeCode/obsidian-claude-搭建个人知识库](../AI/ClaudeCode/obsidian-claude-搭建个人知识库.md) | 3 种集成工具（Claudian、Skills、MCP）、知识库架构选型 |

### Docker-Kubernetes（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Docker](sources/docker-batch-summary.md) | 12 | Docker 基础、GPU 配置、服务部署实战（GitLab/Prometheus/Loki 等） |
| [K8s 基础资源](sources/k8s-basic-resources-batch-summary.md) | 20 | Pod/Deployment/Service/Ingress/ConfigMap/Storage/RBAC/CRD/Operator |
| [K8s 安装管理](sources/k8s-installation-management-batch-summary.md) | 16 | v1.20→v1.35 安装演进、企业高可用、etcd HA、运行时迁移 |
| [K8s 监控日志](sources/k8s-monitoring-logging-batch-summary.md) | 21 | Prometheus 全栈、EFK/Loki 日志、Jaeger/SkyWalking 链路追踪、集群巡检脚本 |
| [K8s CI/CD](sources/k8s-CICD-batch-summary.md) | 19 | Jenkins/ArgoCD/GitLab CI/Tekton/Kustomize/GitHub Actions |
| [K8s 网络与服务网格](sources/k8s-networking-service-mesh-batch-summary.md) | 7 | Ingress-Nginx/External-DNS/Calico/Istio 流量管理 |
| [K8s 安全认证](sources/k8s-security-auth-batch-summary.md) | 7 | Cert-Manager/External Secrets/Kyverno/OAuth2 Proxy/Trivy/SonarQube |
| [K8s 扩缩容与存储](sources/k8s-scaling-storage-batch-summary.md) | 7 | HPA/VPA/KEDA/Karpenter 扩缩容 + NFS/Longhorn/Rook-Ceph 存储 |
| [K8s 中间件与 UI](sources/k8s-db-middleware-UI-batch-summary.md) | 18 | Redis/MySQL/PostgreSQL/Kafka 部署 + Dashboard/Rancher/k9s 管理工具 |
| [K8s 杂项](sources/k8s-misc-batch-summary.md) | 18 | Helm 工具链/CKA-CKS/KubeBlocks/Harbor/K3S/Velero/GPU |

### Azure（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Azure](sources/azure-batch-summary.md) | 21 | VM/VMSS、AKS 全栈、网络/存储、DevOps Pipeline、Policy 治理、诊断工具链 |

### Aliyun（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Aliyun](sources/aliyun-batch-summary.md) | 19 | ECS/ESS 计算、VPC/SLB/WAF/DDoS 网络安全纵深、OSS 存储、RDS/DTS 数据库、Landing Zone |

### Python（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Python](sources/python-batch-summary.md) | 27 | 基础语法、运维开发（SSH/subprocess/K8s API）、网络编程/前端、数据分析/AI、项目实战 |

### Linux-Shell（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Linux-Shell](sources/linux-shell-batch-summary.md) | 24 | 系统管理、Shell 脚本、SSH/网络、存储/LVM/NFS、zsh/vim/rsync 工具链 |

### AI - OpenClaw 与其他（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [AI-OpenClaw](sources/ai-openclaw-misc-batch-summary.md) | 9 | OpenClaw 全栈（安装/Skills/Channels/AIOps/多智能体）、Copilot CLI、提示词工程 |

### Go（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [Go](sources/go-batch-summary.md) | 9 | 环境配置→变量→控制流→函数→数据结构→OOP→错误处理→云原生选型 |

### HPC / CloudComputing / GPU（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [HPC-Cloud-GPU](sources/hpc-cloud-gpu-batch-summary.md) | 18 | Slurm 调度/PBS/GPU 管理、云原生/微服务/ServiceMesh、GPU 硬件/CUDA/驱动 |

### 杂项领域（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [杂项](sources/misc-domains-batch-summary.md) | 18 | Database(MySQL/Redis/MongoDB) + Middlewares(Kafka/RabbitMQ/RocketMQ) + OS + Networking + IaC(Terraform) + Git + C++ + SoftwareTesting |

> [!success] 全部领域已摄入完成
> 共 17 个领域、~350 篇原始文档已全部摄入 wiki 编译层。

---

## 🗺️ 主题地图（Maps）

| 页面 | 摘要 |
|------|------|
| [领域地图](maps/domain-map.md) | 按技术领域导航全库 |
| [工具地图](maps/tool-map.md) | 按工具/平台聚合知识 |
| [Kubernetes 专题](maps/kubernetes-map.md) | 145 篇 K8s 生态知识导航 |
| [AI 工作流专题](maps/ai-workflow-map.md) | Claude Code + OpenClaw + AI 辅助运维 |
| [Claude Code & OpenClaw 专题](maps/claude-code-openclaw-map.md) | AI 编程与开源 AI 工具 |
| [云平台专题](maps/cloud-platform-map.md) | Aliyun + Azure 对标 |
| [Linux 运维专题](maps/linux-ops-map.md) | Linux 系统管理与 Shell 脚本 |
| [Python 运维开发专题](maps/python-devops-map.md) | Python 运维场景应用 |

---

## 📊 分析报告（Analysis）

| 页面 | 摘要 |
|------|------|
| [主题覆盖分析](analysis/topic-coverage-analysis.md) | 17 个领域的覆盖度评估 |
| [高价值知识缺口](analysis/high-value-gaps.md) | 优先填补的知识空白 |
| [后续写作建议](analysis/next-writing-suggestions.md) | 推荐下一步写作方向 |

---

## 📋 盘点与维护

| 页面 | 摘要 |
|------|------|
| [全库文档盘点](inventory/repository-inventory.md) | 全部文档逐一列出 |
| [领域内容特点分析](inventory/domain-summary.md) | 17 个领域的成熟度与优先级 |
| [断链报告](maintenance/broken-links-report.md) | wikilink 有效性检查 |
| [命名规范](maintenance/naming-normalization.md) | 文件命名约定 |
| [增量维护流程](maintenance/update-workflow.md) | 新增文档后的更新步骤 |

---

## 🏗️ 按领域导航

| 领域 | 篇数 | 成熟度 | 入口 |
|------|------|:------:|------|
| Docker-Kubernetes | 145 | 🟢 | [kubernetes-map](maps/kubernetes-map.md) |
| Python | 27 | 🟢 | [python-devops-map](maps/python-devops-map.md) |
| Linux-Shell | 24 | 🟡 | [linux-ops-map](maps/linux-ops-map.md) |
| Azure | 21 | 🟢 | [cloud-platform-map](maps/cloud-platform-map.md) |
| Aliyun | 19 | 🟢 | [cloud-platform-map](maps/cloud-platform-map.md) |
| AI | 16 | 🟡 | [ai-workflow-map](maps/ai-workflow-map.md) |
| Go | 9 | 🟡 | [go-01-环境配置-基础](../Go/go-01-环境配置-基础.md) |
| CloudComputing | 7 | 🟡 | [云原生](../CloudComputing/云原生.md) |
| HPC | 7 | 🟡 | [CentOS7-slurm23.02-二进制安装](../HPC/CentOS7-slurm23.02-二进制安装.md) |
| GPU-DeepLearning | 4 | 🟠 | [GPU-basics](../GPU-DeepLearning/GPU-basics.md) |
| Database | 3 | 🟡 | [MySQL入门](../Database/MySQL入门.md) |
| Middlewares | 3 | 🔴 | [Kafka](../Middlewares/Kafka.md) |
| OS | 3 | 🟠 | [OS](../OS/OS.md) |
| Networking | 2 | 🟠 | [计算机网络基础](../Networking/计算机网络基础.md) |
| IaC | 2 | 🟠 | [terraform-basics](../IaC/terraform-basics.md) |

---

## ⭐ 推荐优先阅读

### 云原生核心路径
1. [云原生](../CloudComputing/云原生.md) → 理解云原生哲学
2. [docker基础](../Docker-Kubernetes/docker/docker基础.md) → 容器基础
3. [k8s基础-架构-组件-资源](../Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → K8s 架构
4. [安装k8s-1.35-基于rockylinux10-最新步骤](../Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤.md) → 最新版安装
5. [helm部署prometheus-stack全家桶](../Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md) → 可观测性

### AI 赋能运维
1. [ClaudeCode基础指南](../AI/ClaudeCode/ClaudeCode基础指南.md) → Claude Code 入门
2. [扩展体系](../AI/ClaudeCode/Claude%20Code%20扩展体系.md) → MCP、Skills、Slash Commands、Plugin
3. [OpenClaw-基础-安装](../AI/OpenClaw/OpenClaw-基础-安装.md) → OpenClaw 入门
4. [obsidian-claude-搭建个人知识库](../AI/ClaudeCode/obsidian-claude-搭建个人知识库.md) → 知识库搭建方法论

### 云平台实战
1. [VPC](../Aliyun/网络/VPC.md) + [Azure-Networking](../Azure/6_Azure-Networking.md) → 云网络对比
2. [负载均衡SLB](../Aliyun/网络/负载均衡SLB.md) + [AKS-basics](../Azure/2_AKS-basics.md) → 负载均衡与 K8s 托管服务
3. [python-Linux-operation](../Python/python-运维开发/python-Linux-operation.md) → 自动化运维脚本
