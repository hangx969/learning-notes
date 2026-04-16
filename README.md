# Cloud-Native & Infrastructure Learning Notes

A comprehensive knowledge base covering cloud-native technologies, infrastructure automation, programming languages, AI/ML, and modern DevOps practices.

> **297 篇文档 · 17 个技术领域 · 42 篇知识编译层文件**

## 🧭 知识库导航（KnowledgeBase）

本仓库在原始文档之上构建了一个 **知识编译层**，提供全局导航、概念网络和分析报告，无需逐篇翻找。

**→ [进入知识库首页](./KnowledgeBase/INDEX.md)**

| 类型 | 说明 | 入口 |
|------|------|------|
| 📋 全库盘点 | 297 篇文档逐一索引 | [repository-inventory](./KnowledgeBase/inventory/repository-inventory.md) |
| 🗺️ 领域地图 | 按技术领域导航 | [domain-map](./KnowledgeBase/maps/domain-map.md) |
| 🔧 工具地图 | 按工具/平台聚合 | [tool-map](./KnowledgeBase/maps/tool-map.md) |
| ☸️ K8s 专题 | 145 篇 K8s 生态导航 | [kubernetes-map](./KnowledgeBase/maps/kubernetes-map.md) |
| 🤖 AI 专题 | Claude Code + OpenClaw | [ai-workflow-map](./KnowledgeBase/maps/ai-workflow-map.md) |
| ☁️ 云平台专题 | Aliyun vs Azure 对标 | [cloud-platform-map](./KnowledgeBase/maps/cloud-platform-map.md) |
| 🐧 Linux 运维 | 系统管理 + HPC + GPU | [linux-ops-map](./KnowledgeBase/maps/linux-ops-map.md) |
| 🐍 Python 运维 | 27 篇 Python 开发导航 | [python-devops-map](./KnowledgeBase/maps/python-devops-map.md) |
| 📈 覆盖分析 | 主题深度与缺口识别 | [topic-coverage-analysis](./KnowledgeBase/analysis/topic-coverage-analysis.md) |
| ✏️ 写作建议 | 10 个推荐补写方向 | [next-writing-suggestions](./KnowledgeBase/analysis/next-writing-suggestions.md) |

### 推荐阅读路径

**云原生入门**：[云原生概念](./CloudComputing/云原生.md) → [Docker 基础](./Docker-Kubernetes/docker/docker基础.md) → [K8s 架构](./Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → [Prometheus 全家桶](./Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md)

**AI 赋能运维**：[Claude Code 指南](./AI/ClaudeCode/ClaudeCode基础指南.md) → [MCP 协议](./AI/ClaudeCode/MCP.md) → [OpenClaw 安装](./AI/OpenClaw/OpenClaw-基础-安装.md)

---

## 📚 Container Orchestration & Kubernetes

- [Docker](./Docker-Kubernetes/docker)
  - Docker fundamentals and best practices
  - Containerized service deployment

- [Kubernetes Foundations](./Docker-Kubernetes/k8s-installation-management)
  - Installation methods (kubeadm, binary)
  - Cluster upgrades and version management
  - Troubleshooting guides

- [Kubernetes Core Resources](./Docker-Kubernetes/k8s-basic-resources)
  - System components and architecture
  - Workload resources (Pod, Deployment, DaemonSet, StatefulSet)
  - Job scheduling (Job, CronJob)
  - Networking (Service, Ingress)
  - Configuration management (ConfigMap, Secrets)
  - Access control (Authentication, Authorization)
  - Storage (Volumes, PV, PVC)
  - Auto-scaling (HPA, VPA)

- [Kubernetes Advanced Topics](./Docker-Kubernetes/)
  - [Service Mesh](./Docker-Kubernetes/k8s-service-mesh)
  - [Security & Authentication](./Docker-Kubernetes/k8s-security-auth)
  - [Storage Solutions](./Docker-Kubernetes/k8s-storage)
  - [Scaling Strategies](./Docker-Kubernetes/k8s-scaling)
  - [AI & GPU Workloads](./Docker-Kubernetes/k8s-ai-gpu)
  - [Database & Middleware on K8s](./Docker-Kubernetes/k8s-db-middleware)
  - [Spring Cloud on K8s](./Docker-Kubernetes/k8s-springcloud)

- [Observability & Monitoring](./Docker-Kubernetes/k8s-monitoring-logging)
  - Prometheus, Grafana, AlertManager
  - Logging: EFK/ELK Stack

- [CI/CD Pipelines](./Docker-Kubernetes/k8s-CICD)
  - GitLab, Jenkins, GitHub Actions

- [Package Management & Operators](./Docker-Kubernetes/)
  - [Helm & Helm Operators](./Docker-Kubernetes/helm-operator)
  - [KubeBlocks](./Docker-Kubernetes/kubeblocks)

- [Container Registries & Platforms](./Docker-Kubernetes/)
  - [Harbor](./Docker-Kubernetes/harbor)
  - [Container Platforms](./Docker-Kubernetes/container-platform) (OpenShift, K3S)

- [Kubernetes Tools & UI](./Docker-Kubernetes/k8s-UI-tools)
  - K9S, Lens, Dashboard, Rancher

- [CKA + CKS Certification](./Docker-Kubernetes/CKA-CKS)

## ☁️ Cloud Platforms

### Azure
- [Virtual Machines & Scale Sets](./Azure/0_Azure-VM-VMSS.md)
- [Azure Kubernetes Service (AKS)](./Azure/)
  - [AKS Basics](./Azure/2_AKS-basics.md)
  - [Workload Identity](./Azure/3_AKS-workload-identity.md)
  - [Key Vault Integration](./Azure/4_AKS-SecretProviderClass-KeyVault.md)
- [Azure Storage](./Azure/5_Azure-Storage.md)
- [Azure Networking](./Azure/6_Azure-Networking.md)
- [Container Services](./Azure/7_ACR-ACI.md)
- [Azure DevOps](./Azure/)
  - [DevOps Basics](./Azure/8_Azure-devops-basics.md)
  - [Self-hosted Agents](./Azure/9_Azure-devops-self-host-agents.md)
  - [Agent Pool Management](./Azure/10_Azure-devops-agent-pool-management.md)
- [Azure Policy](./Azure/11_Azure-Policy.md)
- [Troubleshooting & Tools](./Azure/)
  - Linux VM troubleshooting
  - Monitoring tools (Kusto Query, Fiddler, Postman, PerfMon)
- [Customer Support Resources](./Azure/Customer%20Support)

### Alibaba Cloud (Aliyun)
- [ACP Certification](./Aliyun/ACP认证.md)
- [Compute Services](./Aliyun/计算)
- [Networking](./Aliyun/网络)
- [Storage Solutions](./Aliyun/存储)
- [Database Services](./Aliyun/数据库)
- [Resource Management](./Aliyun/资源管理)

## 🏗️ Infrastructure as Code

- [Terraform](./IaC/)
  - [Terraform Basics](./IaC/terraform-basics.md)
  - [Terraform Documentation](./IaC/terraform-docs.md)

## 💻 Programming Languages

### Python
- [Python Fundamentals](./Python/python-基础)
- [Data Analysis & AI/ML](./Python/python-数据分析-AI大模型)
- [Network Programming & Frontend](./Python/python-网络编程-前端)
- [DevOps Development](./Python/python-运维开发)
- [Python Manuscripts & Projects](./Python/python-manuscripts)

### Go
- [Go Programming](./Go/)

### C++
- [C++ Development](./C++/)

## 🤖 AI & Machine Learning

- [AI Tools & Workflows](./AI/)
  - [Claude Code](./AI/ClaudeCode)
  - [GitHub Copilot CLI](Copilot%20CLI.md)
  - [Prompt Engineering](提示词.md)

- [GPU Computing & Deep Learning](./GPU-DeepLearning/)

## 💾 Data Infrastructure

### Databases
- [MySQL Deployment & Management](./Database/)
  - MySQL MGR Cluster
  - MySQL Fundamentals
- [Redis](./Database/)
  - Source installation and configuration

### Message Queues & Middleware
- [Kafka](./Middlewares/Kafka.md)
- [RabbitMQ](./Middlewares/RabbitMQ.md)
- [RocketMQ](./Middlewares/RocketMQ.md)

## 🖥️ System Operations & Computing

- [Linux & Shell](./Linux-Shell/)
  - Linux fundamentals
  - Shell scripting
  - Ubuntu system management
  - Configuration management

- [Operating Systems](./OS/)

- [High Performance Computing](./HPC/)

- [Networking](./Networking/)

- [Cloud Computing Fundamentals](./CloudComputing/)

## 🛠️ Development Tools & Testing

- [Git](./Git/git-learning)
  - Git fundamentals and workflows

- [Software Testing](./SoftwareTesting/)
