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
> - **Schema 文件**：[[CLAUDE.md]]
> - **操作日志**：[[KnowledgeBase/log]]
> - **扫描日期**：2026-04-17
> - **核心定位**：云原生运维工程师的全栈技术知识库

---

## 🧠 概念页（Concepts）

抽象概念的独立知识页面。

| 页面 | 摘要 |
|------|------|
| [[KnowledgeBase/concepts/CICD\|CICD]] | 持续集成与持续交付，覆盖 Jenkins、ArgoCD、GitLab CI、Tekton 等工具链 |
| [[KnowledgeBase/concepts/Observability\|Observability]] | 可观测性三大支柱：日志、指标、链路追踪 |
| [[KnowledgeBase/concepts/日志系统\|日志系统]] | EFK/ELK、Loki 等日志采集与分析方案 |
| [[KnowledgeBase/concepts/服务网格\|服务网格]] | Istio 为代表的服务网格架构与流量管理 |
| [[KnowledgeBase/concepts/容器运行时\|容器运行时]] | containerd、Docker Engine 等容器运行时技术 |
| [[KnowledgeBase/concepts/自动化运维\|自动化运维]] | Ansible、Python 脚本、Terraform 等自动化运维实践 |
| [[KnowledgeBase/concepts/Python运维开发\|Python运维开发]] | Python 在运维场景中的应用：自动化脚本、Web 运维平台、API 调用 |

---

## 🔧 实体页（Entities）

具体工具、平台、项目的独立知识页面。

| 页面 | 摘要 |
|------|------|
| [[KnowledgeBase/entities/Kubernetes\|Kubernetes]] | 容器编排平台，145 篇文章覆盖全生命周期 |
| [[KnowledgeBase/entities/Docker\|Docker]] | 容器运行时，12 篇覆盖基础与服务部署实战 |
| [[KnowledgeBase/entities/Helm\|Helm]] | Kubernetes 包管理器 |
| [[KnowledgeBase/entities/ArgoCD\|ArgoCD]] | GitOps 持续交付工具 |
| [[KnowledgeBase/entities/Jenkins\|Jenkins]] | CI/CD 自动化服务器 |
| [[KnowledgeBase/entities/Prometheus\|Prometheus]] | 云原生监控系统 |
| [[KnowledgeBase/entities/Grafana\|Grafana]] | 可视化与仪表盘平台 |
| [[KnowledgeBase/entities/Istio\|Istio]] | 服务网格平台 |
| [[KnowledgeBase/entities/Ingress\|Ingress]] | Kubernetes 入口控制器 |
| [[KnowledgeBase/entities/Azure\|Azure]] | Microsoft 公有云平台 |
| [[KnowledgeBase/entities/AKS\|AKS]] | Azure 托管 Kubernetes 服务 |
| [[KnowledgeBase/entities/Aliyun\|Aliyun]] | 阿里云公有云平台 |
| [[KnowledgeBase/entities/Terraform\|Terraform]] | 基础设施即代码工具 |
| [[KnowledgeBase/entities/Claude-Code\|Claude-Code]] | AI 编程助手 |
| [[KnowledgeBase/entities/MCP\|MCP]] | Model Context Protocol |
| [[KnowledgeBase/entities/OpenClaw\|OpenClaw]] | 开源 AI 工具平台 |
| [[KnowledgeBase/entities/Obsidian\|Obsidian]] | 知识管理与笔记工具 |
| [[KnowledgeBase/entities/Slurm\|Slurm]] | HPC 作业调度系统 |

---

## 📄 来源摘要（Sources）

每篇原始来源文档的知识提炼摘要。

### AI/ClaudeCode（已摄入 ✅）

| 页面 | 原始来源 | 摘要 |
|------|---------|------|
| [[KnowledgeBase/sources/ClaudeCode基础指南-summary\|ClaudeCode基础指南]] | [[AI/ClaudeCode/ClaudeCode基础指南]] | 3 种模式、Extended Thinking、Claude.md、Spec 工作流、5 大实战场景 |
| [[KnowledgeBase/sources/MCP配置-summary\|MCP配置]] | [[AI/ClaudeCode/MCP]] | 10 个 MCP 服务器安装配置、场景组合推荐 |
| [[KnowledgeBase/sources/Skills-summary\|Skills]] | [[AI/ClaudeCode/Skills]] | 渐进式加载设计、3 层使用模式、代码审查与事故响应实战 |
| [[KnowledgeBase/sources/Subagents-summary\|Subagents]] | [[AI/ClaudeCode/Subagents]] | 独立 Claude 副本、5 组件架构、并行执行与适用场景评级 |
| [[KnowledgeBase/sources/Slash-Command-summary\|Slash Command]] | [[AI/ClaudeCode/Slash Command]] | 手动触发工作流快捷方式、与 Skills 的注入方式区别 |
| [[KnowledgeBase/sources/Plugin-summary\|Plugin]] | [[AI/ClaudeCode/Plugin]] | 应用级打包容器、组成上限、团队分发实践 |
| [[KnowledgeBase/sources/obsidian-claude-搭建个人知识库-summary\|Obsidian+Claude知识库]] | [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]] | 3 种集成工具（Claudian、Skills、MCP）、知识库架构选型 |

### Docker-Kubernetes（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [[KnowledgeBase/sources/docker-batch-summary\|Docker]] | 12 | Docker 基础、GPU 配置、服务部署实战（GitLab/Prometheus/Loki 等） |
| [[KnowledgeBase/sources/k8s-basic-resources-batch-summary\|K8s 基础资源]] | 20 | Pod/Deployment/Service/Ingress/ConfigMap/Storage/RBAC/CRD/Operator |
| [[KnowledgeBase/sources/k8s-installation-management-batch-summary\|K8s 安装管理]] | 16 | v1.20→v1.35 安装演进、企业高可用、etcd HA、运行时迁移 |
| [[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary\|K8s 监控日志]] | 20 | Prometheus 全栈、EFK/Loki 日志、Jaeger/SkyWalking 链路追踪 |
| [[KnowledgeBase/sources/k8s-CICD-batch-summary\|K8s CI/CD]] | 19 | Jenkins/ArgoCD/GitLab CI/Tekton/Kustomize/GitHub Actions |
| [[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary\|K8s 网络与服务网格]] | 7 | Ingress-Nginx/External-DNS/Calico/Istio 流量管理 |
| [[KnowledgeBase/sources/k8s-security-auth-batch-summary\|K8s 安全认证]] | 7 | Cert-Manager/External Secrets/Kyverno/OAuth2 Proxy/Trivy/SonarQube |
| [[KnowledgeBase/sources/k8s-scaling-storage-batch-summary\|K8s 扩缩容与存储]] | 7 | HPA/VPA/KEDA/Karpenter 扩缩容 + NFS/Longhorn/Rook-Ceph 存储 |
| [[KnowledgeBase/sources/k8s-db-middleware-UI-batch-summary\|K8s 中间件与 UI]] | 18 | Redis/MySQL/PostgreSQL/Kafka 部署 + Dashboard/Rancher/k9s 管理工具 |
| [[KnowledgeBase/sources/k8s-misc-batch-summary\|K8s 杂项]] | 18 | Helm 工具链/CKA-CKS/KubeBlocks/Harbor/K3S/Velero/GPU |

### Azure（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [[KnowledgeBase/sources/azure-batch-summary\|Azure]] | 21 | VM/VMSS、AKS 全栈、网络/存储、DevOps Pipeline、Policy 治理、诊断工具链 |

### Aliyun（已摄入 ✅）

| 页面 | 覆盖文档数 | 摘要 |
|------|:---------:|------|
| [[KnowledgeBase/sources/aliyun-batch-summary\|Aliyun]] | 19 | ECS/ESS 计算、VPC/SLB/WAF/DDoS 网络安全纵深、OSS 存储、RDS/DTS 数据库、Landing Zone |

> [!note] 待摄入领域
> Python（27 篇）、Linux-Shell（24 篇）、Go（9 篇）、HPC（7 篇）、CloudComputing（7 篇）等。

---

## 🗺️ 主题地图（Maps）

| 页面 | 摘要 |
|------|------|
| [[KnowledgeBase/maps/domain-map\|领域地图]] | 按技术领域导航全库 |
| [[KnowledgeBase/maps/tool-map\|工具地图]] | 按工具/平台聚合知识 |
| [[KnowledgeBase/maps/kubernetes-map\|Kubernetes 专题]] | 145 篇 K8s 生态知识导航 |
| [[KnowledgeBase/maps/ai-workflow-map\|AI 工作流专题]] | Claude Code + OpenClaw + AI 辅助运维 |
| [[KnowledgeBase/maps/claude-code-openclaw-map\|Claude Code & OpenClaw 专题]] | AI 编程与开源 AI 工具 |
| [[KnowledgeBase/maps/cloud-platform-map\|云平台专题]] | Aliyun + Azure 对标 |
| [[KnowledgeBase/maps/linux-ops-map\|Linux 运维专题]] | Linux 系统管理与 Shell 脚本 |
| [[KnowledgeBase/maps/python-devops-map\|Python 运维开发专题]] | Python 运维场景应用 |

---

## 📊 分析报告（Analysis）

| 页面 | 摘要 |
|------|------|
| [[KnowledgeBase/analysis/topic-coverage-analysis\|主题覆盖分析]] | 17 个领域的覆盖度评估 |
| [[KnowledgeBase/analysis/high-value-gaps\|高价值知识缺口]] | 优先填补的知识空白 |
| [[KnowledgeBase/analysis/next-writing-suggestions\|后续写作建议]] | 推荐下一步写作方向 |

---

## 📋 盘点与维护

| 页面 | 摘要 |
|------|------|
| [[KnowledgeBase/inventory/repository-inventory\|全库文档盘点]] | 全部文档逐一列出 |
| [[KnowledgeBase/inventory/domain-summary\|领域内容特点分析]] | 17 个领域的成熟度与优先级 |
| [[KnowledgeBase/maintenance/broken-links-report\|断链报告]] | wikilink 有效性检查 |
| [[KnowledgeBase/maintenance/naming-normalization\|命名规范]] | 文件命名约定 |
| [[KnowledgeBase/maintenance/update-workflow\|增量维护流程]] | 新增文档后的更新步骤 |

---

## 🏗️ 按领域导航

| 领域 | 篇数 | 成熟度 | 入口 |
|------|------|:------:|------|
| Docker-Kubernetes | 145 | 🟢 | [[KnowledgeBase/maps/kubernetes-map\|kubernetes-map]] |
| Python | 27 | 🟢 | [[KnowledgeBase/maps/python-devops-map\|python-devops-map]] |
| Linux-Shell | 24 | 🟡 | [[KnowledgeBase/maps/linux-ops-map\|linux-ops-map]] |
| Azure | 21 | 🟢 | [[KnowledgeBase/maps/cloud-platform-map\|cloud-platform-map]] |
| Aliyun | 19 | 🟢 | [[KnowledgeBase/maps/cloud-platform-map\|cloud-platform-map]] |
| AI | 16 | 🟡 | [[KnowledgeBase/maps/ai-workflow-map\|ai-workflow-map]] |
| Go | 9 | 🟡 | [[Go/go-01-环境配置-基础]] |
| CloudComputing | 7 | 🟡 | [[CloudComputing/云原生]] |
| HPC | 7 | 🟡 | [[HPC/CentOS7-slurm23.02-二进制安装]] |
| GPU-DeepLearning | 4 | 🟠 | [[GPU-DeepLearning/GPU-basics]] |
| Database | 3 | 🟡 | [[Database/MySQL入门]] |
| Middlewares | 3 | 🔴 | [[Middlewares/Kafka]] |
| OS | 3 | 🟠 | [[OS/OS]] |
| Networking | 2 | 🟠 | [[Networking/计算机网络基础]] |
| IaC | 2 | 🟠 | [[IaC/terraform-basics]] |

---

## ⭐ 推荐优先阅读

### 云原生核心路径
1. [[CloudComputing/云原生]] → 理解云原生哲学
2. [[Docker-Kubernetes/docker/docker基础]] → 容器基础
3. [[Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源]] → K8s 架构
4. [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]] → 最新版安装
5. [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]] → 可观测性

### AI 赋能运维
1. [[AI/ClaudeCode/ClaudeCode基础指南]] → Claude Code 入门
2. [[AI/ClaudeCode/MCP]] → MCP 协议
3. [[AI/OpenClaw/OpenClaw-基础-安装]] → OpenClaw 入门
4. [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]] → 知识库搭建方法论

### 云平台实战
1. [[Aliyun/网络/VPC]] + [[Azure/6_Azure-Networking]] → 云网络对比
2. [[Aliyun/网络/负载均衡SLB]] + [[Azure/2_AKS-basics]] → 负载均衡与 K8s 托管服务
3. [[Python/python-运维开发/python-Linux-operation]] → 自动化运维脚本
