# Cloud-Native & Infrastructure Learning Notes

A comprehensive knowledge base covering cloud-native technologies, infrastructure automation, programming languages, AI/ML, and modern DevOps practices.

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
  - [GitHub Copilot CLI](./AI/Copilot%20CLI.md)
  - [Prompt Engineering](./AI/提示词集合.md)

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
