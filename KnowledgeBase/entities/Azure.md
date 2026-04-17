---
title: Azure
tags:
  - knowledgebase/entity
  - azure
date: 2026-04-17
sources:
  - "[[Azure/0_Azure-VM-VMSS]]"
  - "[[Azure/2_AKS-basics]]"
  - "[[Azure/6_Azure-Networking]]"
  - "[[Azure/5_Azure-Storage]]"
  - "[[Azure/8_Azure-devops-basics]]"
  - "[[Azure/11_Azure-Policy]]"
  - "[[Azure/Kusto Query]]"
  - "[[KnowledgeBase/sources/azure-batch-summary]]"
---

# Azure

## 简介

Microsoft Azure 是微软提供的公有云计算平台，涵盖计算、存储、网络、容器、DevOps、治理等完整云服务体系。本仓库共收录 21 篇 Azure 相关笔记（详见 [[KnowledgeBase/sources/azure-batch-summary|Azure 来源批量摘要]]），内容定位为 **Azure 技术支持工程师的实战知识库**，侧重于 Azure China Cloud（中国区）的部署与运维场景。

## 核心服务覆盖

### 计算：VM / VMSS

- Azure IaaS 核心，物理节点由 Fabric Controller 统一管理资源分配，Guest Agent (waagent) 负责 VM 内部管理
- 约 1000 台 Windows Server 物理机组成一个集群，支撑 IaaS/PaaS/SaaS 三层服务模型
- Linux VM 故障排查覆盖磁盘扩展（fdisk + resize2fs）、文件系统损坏（rescue VM + fsck）、fstab 配置错误等常见场景
- 详见 [[Azure/0_Azure-VM-VMSS|VM 与 VMSS]] 和 [[Azure/1_Azure-Linux-VM-troubheshooting|Linux VM 故障排查]]

### 容器服务：AKS / ACR / ACI

- **AKS** 控制面由 Azure 托管（apiserver、scheduler、etcd、controller），工作节点使用 containerd 运行时（1.19+），资源预留按节点规格递增
- **AKS 安全体系**形成闭环：[[Azure/3_AKS-workload-identity|Workload Identity]]（Pod 身份认证，通过 OIDC + Federated Credential 关联 Managed Identity）→ [[Azure/4_AKS-SecretProviderClass-KeyVault|SecretProviderClass]]（CSI 驱动将 Key Vault 密钥同步为 K8s Secret）
- **ACR** 层级：容器注册表 > 存储库 > 容器镜像，中国区域名为 `azurecr.cn`
- **ACI** 支持快速部署容器实例，可与 VNet 集成
- 详见 [[Azure/2_AKS-basics|AKS 基础]]、[[Azure/7_ACR-ACI|ACR 与 ACI]]

### 网络

- 网络连通性测试工具集：psping、telnet、nc、dig（DNS 查询）、curl（出站验证）、siege（压测）
- 覆盖 VNet、NSG、负载均衡等基础网络概念，以及 K8s 集群内部 DNS 解析
- 详见 [[Azure/6_Azure-Networking|Azure Networking]]

### 存储

- 五种冗余策略：LRS、GRS、RA-GRS、ZRS、GZRS
- Blob 三种类型（Block/Append/Page），三种访问层（Hot/Cool/Archive）
- 托管磁盘类型：Premium SSD、Standard SSD、Standard HDD
- 详见 [[Azure/5_Azure-Storage|Azure Storage]]

### DevOps CI/CD

- Pipeline 通过 `azure-pipelines.yml` 定义，层级为 Pipeline > Stage > Job > Step，Steps 间通过 logging command 传递变量
- **Azure China 不支持 MS Managed Agents**，只能使用自托管代理，Agent 通过 capability/demand 机制匹配 pipeline
- Agent 注册支持 PAT、Device Code、Service Principal 三种认证方式
- Agent Pool 管理通过 Az CLI + REST API 完成，Agent 删除只能走 REST API
- 详见 [[Azure/8_Azure-devops-basics|DevOps 基础]]、[[Azure/9_Azure-devops-self-host-agents|自托管 Agent]]、[[Azure/10_Azure-devops-agent-pool-management|Agent Pool 管理]]

### 治理与安全策略

- Azure Policy 在 ARM 层拦截所有 CRUD 请求，位于 RBAC 之后，采用 Explicit Deny System
- Policy 针对资源定义（"这个资源能不能这样配"），RBAC 针对用户操作（"这个人能不能做这件事"）
- 支持 Audit（审计）和 Enforcement（强制）两大用途
- 详见 [[Azure/11_Azure-Policy|Azure Policy]]

### 监控与诊断工具

本仓库约半数文档属于诊断工具类，体现了技术支持工程师的视角：

| 工具 | 用途 | 详情 |
|------|------|------|
| [[Azure/Kusto Query\|KQL]] | Azure 内部诊断平台查询，覆盖 VM/AKS/ACR 等多种资源 | 关键表：LogContainerSnapshot、LogNodeSnapshot |
| [[Azure/IO-monitor\|IO Monitor]] | VM 磁盘 I/O 基准测试 | Diskspd (Windows) / FIO (Linux) |
| [[Azure/fiddler\|Fiddler]] | HTTP 调试代理 | 支持 HTTPS 解密和进程级过滤 |
| [[Azure/perfMon ProcessMon\|PerfMon]] | Windows 性能计数器采集 | 配合 Diskspd 做磁盘基准测试 |
| [[Azure/browser trace\|Browser Trace]] | HAR 网络请求捕获 | 排查 Azure Portal 问题 |
| [[Azure/postman\|Postman]] | Azure ARM/AAD API 调试 | 需区分 AAD Token 和 ARM Token |
| [[Azure/command-line-tools\|命令行工具]] | Az CLI / PowerShell / AzCopy | 中国区需指定 AzureChinaCloud 环境 |

### 其他

- [[Azure/Jfrog-artifactory-Azure|JFrog Artifactory]]：在 Azure 上通过 ACI 或 AKS 部署 Artifactory，与 ACR、Azure Storage 集成
- [[Azure/Customer Support/Email Templates|邮件模板]]：面向 Azure 全球技术中心（GTC）的中英文工单邮件模板

## 实践亮点

1. **Azure China Cloud 专注**：多篇文档专门针对中国区 Azure 的特殊配置（AzureChinaCloud 环境变量、`azurecr.cn` 域名、自托管 DevOps Agent 的必要性），该知识库主要服务于中国区 Azure 运维
2. **AKS 安全链路闭环**：Workload Identity → SecretProviderClass → Key Vault 三篇文档构成从 Pod 身份认证到密钥注入的完整链路
3. **DevOps 全链路覆盖**：从 Pipeline 基础概念、自托管 Agent 部署到 Agent Pool 运维管理，覆盖 CI/CD 完整流程
4. **存储与计算交叉**：磁盘类型、IO 基准测试、存储冗余等知识点跨 VM、AKS、Storage 多篇文档互相关联
5. **诊断工具链完整**：约半数文档为工具类，从网络抓包到性能监控、从 API 调试到日志查询，形成完整的故障排查工具箱

## 相关概念与实体

- [[KnowledgeBase/entities/AKS|AKS]] - Azure Kubernetes Service
- [[KnowledgeBase/entities/Azure VM|Azure VM]] / [[KnowledgeBase/entities/VMSS|VMSS]]
- [[KnowledgeBase/entities/Azure Storage|Azure Storage]]
- [[KnowledgeBase/entities/Azure Networking|Azure Networking]]
- [[KnowledgeBase/entities/ACR|ACR]] / [[KnowledgeBase/entities/ACI|ACI]]
- [[KnowledgeBase/entities/Azure DevOps|Azure DevOps]]
- [[KnowledgeBase/entities/Azure Policy|Azure Policy]]
- [[KnowledgeBase/entities/Key Vault|Key Vault]]
- [[KnowledgeBase/entities/Workload Identity|Workload Identity]]
- [[KnowledgeBase/entities/KQL|KQL]]
- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/CICD|CICD]]
- [[KnowledgeBase/concepts/Observability|Observability]]

## 知识空白

- **Azure Landing Zone 架构设计**：缺少企业级多订阅拓扑、管理组层级、蓝图等顶层设计内容
- **Azure Monitor 与 Log Analytics**：缺少 Application Insights、Log Analytics Workspace、告警规则等可观测性体系
- **Azure Bicep / ARM 模板**：缺少基础设施即代码的模板语言实践
- **Azure RBAC 与 Entra ID**：缺少身份管理、条件访问策略、PIM 等安全身份体系
- **Azure Cost Management**：缺少成本分析、预算告警、预留实例优化等 FinOps 实践
- **Azure 网络深层**：缺少 Application Gateway、Front Door、Private Link/Endpoint、ExpressRoute 等高级网络服务
- **Azure Functions / App Service**：缺少 PaaS 级计算服务的实践记录
