# 云原生与基础设施学习笔记

涵盖云原生技术、基础设施自动化、编程语言、AI/ML 和现代 DevOps 实践的综合知识库。

> **297 篇文档 · 17 个技术领域 · 42 篇知识编译层文件**

## 🧭 知识库导航（KnowledgeBase）

本仓库在原始文档之上构建了一个 **知识编译层**，提供全局导航、概念网络和分析报告，无需逐篇翻找。

**→ [进入知识库首页](./KnowledgeBase/INDEX.md)**

| 类型           | 说明                     | 入口                                                                               |
| ------------ | ---------------------- | -------------------------------------------------------------------------------- |
| 📋 全库盘点      | 297 篇文档逐一索引            | [repository-inventory](./KnowledgeBase/inventory/repository-inventory.md)        |
| 🗺️ 领域地图     | 按技术领域导航                | [domain-map](./KnowledgeBase/maps/domain-map.md)                                 |
| 🔧 工具地图      | 按工具/平台聚合               | [tool-map](./KnowledgeBase/maps/tool-map.md)                                     |
| ☸️ K8s 专题    | 145 篇 K8s 生态导航         | [kubernetes-map](./KnowledgeBase/maps/kubernetes-map.md)                         |
| 🤖 AI 专题     | Claude Code + OpenClaw | [ai-workflow-map](./KnowledgeBase/maps/ai-workflow-map.md)                       |
| ☁️ 云平台专题     | Aliyun vs Azure 对标     | [cloud-platform-map](./KnowledgeBase/maps/cloud-platform-map.md)                 |
| 🐧 Linux 运维  | 系统管理 + HPC + GPU       | [linux-ops-map](./KnowledgeBase/maps/linux-ops-map.md)                           |
| 🐍 Python 运维 | 27 篇 Python 开发导航       | [python-devops-map](./KnowledgeBase/maps/python-devops-map.md)                   |
| 📈 覆盖分析      | 主题深度与缺口识别              | [topic-coverage-analysis](./KnowledgeBase/analysis/topic-coverage-analysis.md)   |
| ✏️ 写作建议      | 10 个推荐补写方向             | [next-writing-suggestions](./KnowledgeBase/analysis/next-writing-suggestions.md) |

### 推荐阅读路径

**云原生入门**：[云原生概念](./CloudComputing/云原生.md) → [Docker 基础](./Docker-Kubernetes/docker/docker基础.md) → [K8s 架构](./Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → [Prometheus 全家桶](./Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md)

**AI 赋能运维**：[Claude Code 指南](./AI/ClaudeCode/ClaudeCode基础指南.md) → [MCP 协议](./AI/ClaudeCode/MCP.md) → [OpenClaw 安装](./AI/OpenClaw/OpenClaw-基础-安装.md)

---

## 📚 容器编排与 Kubernetes

- [Docker](./Docker-Kubernetes/docker)
  - Docker 基础与最佳实践
  - 容器化服务部署

- [Kubernetes 基础](./Docker-Kubernetes/k8s-installation-management)
  - 安装方式（kubeadm、二进制）
  - 集群升级与版本管理
  - 故障排查指南

- [Kubernetes 核心资源](./Docker-Kubernetes/k8s-basic-resources)
  - 系统组件与架构
  - 工作负载资源（Pod、Deployment、DaemonSet、StatefulSet）
  - 任务调度（Job、CronJob）
  - 网络（Service、Ingress）
  - 配置管理（ConfigMap、Secrets）
  - 访问控制（认证、授权、准入）
  - 存储（Volumes、PV、PVC）
  - 自动伸缩（HPA、VPA）

- [Kubernetes 进阶主题](./Docker-Kubernetes/)
  - [服务网格](./Docker-Kubernetes/k8s-service-mesh)
  - [安全与认证](./Docker-Kubernetes/k8s-security-auth)
  - [存储方案](./Docker-Kubernetes/k8s-storage)
  - [弹性伸缩](./Docker-Kubernetes/k8s-scaling)
  - [AI 与 GPU 工作负载](./Docker-Kubernetes/k8s-ai-gpu)
  - [数据库与中间件](./Docker-Kubernetes/k8s-db-middleware)
  - [Spring Cloud on K8s](./Docker-Kubernetes/k8s-springcloud)

- [可观测性与监控](./Docker-Kubernetes/k8s-monitoring-logging)
  - Prometheus、Grafana、AlertManager
  - 日志：EFK/ELK Stack

- [CI/CD 流水线](./Docker-Kubernetes/k8s-CICD)
  - GitLab、Jenkins、GitHub Actions

- [包管理与 Operator](./Docker-Kubernetes/)
  - [Helm 与 Helm Operator](./Docker-Kubernetes/helm-operator)
  - [KubeBlocks](./Docker-Kubernetes/kubeblocks)

- [容器镜像仓库与平台](./Docker-Kubernetes/)
  - [Harbor](./Docker-Kubernetes/harbor)
  - [容器平台](./Docker-Kubernetes/container-platform)（OpenShift、K3S）

- [Kubernetes 工具与 UI](./Docker-Kubernetes/k8s-UI-tools)
  - K9S、Lens、Dashboard、Rancher

- [CKA + CKS 认证](./Docker-Kubernetes/CKA-CKS)

## ☁️ 云平台

### Azure
- [虚拟机与规模集](./Azure/0_Azure-VM-VMSS.md)
- [Azure Kubernetes Service (AKS)](./Azure/)
  - [AKS 基础](./Azure/2_AKS-basics.md)
  - [工作负载身份](./Azure/3_AKS-workload-identity.md)
  - [Key Vault 集成](./Azure/4_AKS-SecretProviderClass-KeyVault.md)
- [Azure 存储](./Azure/5_Azure-Storage.md)
- [Azure 网络](./Azure/6_Azure-Networking.md)
- [容器服务](./Azure/7_ACR-ACI.md)
- [Azure DevOps](./Azure/)
  - [DevOps 基础](./Azure/8_Azure-devops-basics.md)
  - [自托管代理](./Azure/9_Azure-devops-self-host-agents.md)
  - [代理池管理](./Azure/10_Azure-devops-agent-pool-management.md)
- [Azure 策略](./Azure/11_Azure-Policy.md)
- [排障与工具](./Azure/)
  - Linux 虚拟机排障
  - 监控工具（Kusto Query、Fiddler、Postman、PerfMon）
- [客户支持资源](./Azure/Customer%20Support)

### 阿里云（Aliyun）
- [ACP 认证](./Aliyun/ACP认证.md)
- [计算服务](./Aliyun/计算)
- [网络](./Aliyun/网络)
- [存储方案](./Aliyun/存储)
- [数据库服务](./Aliyun/数据库)
- [资源管理](./Aliyun/资源管理)

## 🏗️ 基础设施即代码

- [Terraform](./IaC/)
  - [Terraform 基础](./IaC/terraform-basics.md)
  - [Terraform 文档](./IaC/terraform-docs.md)

## 💻 编程语言

### Python
- [Python 基础](./Python/python-基础)
- [数据分析与 AI 大模型](./Python/python-数据分析-AI大模型)
- [网络编程与前端](./Python/python-网络编程-前端)
- [运维开发](./Python/python-运维开发)
- [Python 手稿与项目](./Python/python-manuscripts)

### Go
- [Go 编程](./Go/)

### C++
- [C++ 开发](./C++/)

## 🤖 AI 与机器学习

- [AI 工具与工作流](./AI/)
  - [Claude Code](./AI/ClaudeCode)
  - [GitHub Copilot CLI](Copilot%20CLI.md)
  - [提示词工程](提示词.md)

- [GPU 计算与深度学习](./GPU-DeepLearning/)

## 💾 数据基础设施

### 数据库
- [MySQL 部署与管理](./Database/)
  - MySQL MGR 集群
  - MySQL 基础
- [Redis](./Database/)
  - 源码安装与配置

### 消息队列与中间件
- [Kafka](./Middlewares/Kafka.md)
- [RabbitMQ](./Middlewares/RabbitMQ.md)
- [RocketMQ](./Middlewares/RocketMQ.md)

## 🖥️ 系统运维与计算

- [Linux 与 Shell](./Linux-Shell/)
  - Linux 基础
  - Shell 脚本
  - Ubuntu 系统管理
  - 配置管理

- [操作系统](./OS/)

- [高性能计算](./HPC/)

- [网络](./Networking/)

- [云计算基础](./CloudComputing/)

## 🛠️ 开发工具与测试

- [Git](./Git/git-learning)
  - Git 基础与工作流

- [软件测试](./SoftwareTesting/)
