---
title: 云平台专题地图
tags:
  - knowledgebase/map
  - knowledgebase/cloud
aliases:
  - Cloud Platform Map
date: 2026-04-16
---

# ☁️ 云平台专题地图

> [!info] 专题范围
> 覆盖 Aliyun（19 篇）和 Azure（21 篇）两大云平台，共 ==40 篇文档==。按功能域对标展示。

---

## 核心概念
- [Aliyun](../concepts/Aliyun.md)
- [Azure](../concepts/Azure.md)
- [AKS](../concepts/AKS.md)

---

## 功能域对标

| 功能域 | Aliyun | Azure |
|--------|--------|-------|
| **计算** | [ECS](../../Aliyun/计算/ECS.md)、[弹性伸缩ESS](../../Aliyun/计算/弹性伸缩ESS.md) | [0_Azure-VM-VMSS](../../Azure/0_Azure-VM-VMSS.md) |
| **K8s 托管** | — | [2_AKS-basics](../../Azure/2_AKS-basics.md)、[3_AKS-workload-identity](../../Azure/3_AKS-workload-identity.md)、[4_AKS-SecretProviderClass-KeyVault](../../Azure/4_AKS-SecretProviderClass-KeyVault.md) |
| **网络** | [VPC](../../Aliyun/网络/VPC.md)、[CEN-TR](../../Aliyun/网络/CEN-TR.md)、[网关-VPN-专线](../../Aliyun/网络/网关-VPN-专线.md) | [6_Azure-Networking](../../Azure/6_Azure-Networking.md) |
| **负载均衡** | [负载均衡SLB](../../Aliyun/网络/负载均衡SLB.md)（CLB/ALB/NLB） | 含在 Azure Networking |
| **存储** | [对象存储OSS](../../Aliyun/存储/对象存储OSS.md)、[数据湖-HDFS-POSIX](../../Aliyun/存储/数据湖-HDFS-POSIX.md) | [5_Azure-Storage](../../Azure/5_Azure-Storage.md) |
| **容器镜像** | — | [7_ACR-ACI](../../Azure/7_ACR-ACI.md) |
| **数据库** | [关系型数据库RDS](../../Aliyun/数据库/关系型数据库RDS.md)、[数据传输服务DTS](../../Aliyun/数据库/数据传输服务DTS.md) | — |
| **安全-WAF** | [WAF](../../Aliyun/网络/WAF.md) | — |
| **安全-DDoS** | [DDoS高防](../../Aliyun/网络/DDoS高防.md) | — |
| **安全-防火墙** | [云安全中心-云防火墙](../../Aliyun/网络/云安全中心-云防火墙.md) | — |
| **安全-策略** | — | [11_Azure-Policy](../../Azure/11_Azure-Policy.md) |
| **DevOps** | — | [8_Azure-devops-basics](../../Azure/8_Azure-devops-basics.md)、[9_Azure-devops-self-host-agents](../../Azure/9_Azure-devops-self-host-agents.md)、[10_Azure-devops-agent-pool-management](../../Azure/10_Azure-devops-agent-pool-management.md) |
| **迁移** | [主机迁移工具SMC](../../Aliyun/计算/主机迁移工具SMC.md) | — |
| **资源管理** | [Landing Zone](../../Aliyun/资源管理/Landing%20Zone.md) | — |
| **认证考试** | [ACP考试](../../Aliyun/ACP考试.md) | — |
| **排障工具** | — | [Kusto Query](../../Azure/Kusto%20Query.md)、[IO-monitor](../../Azure/IO-monitor.md)、[fiddler](../../Azure/fiddler.md)、[browser trace](../../Azure/browser%20trace.md) |

---

## 推荐阅读顺序

### Aliyun 路径
1. [VPC](../../Aliyun/网络/VPC.md) — 网络基础
2. [ECS](../../Aliyun/计算/ECS.md) — 计算入口
3. [负载均衡SLB](../../Aliyun/网络/负载均衡SLB.md) — 流量分发
4. [DNS-CDN-SSL](../../Aliyun/网络/DNS-CDN-SSL.md) — 域名与加速
5. [WAF](../../Aliyun/网络/WAF.md) → [DDoS高防](../../Aliyun/网络/DDoS高防.md) → [云安全中心-云防火墙](../../Aliyun/网络/云安全中心-云防火墙.md) — 安全链
6. [对象存储OSS](../../Aliyun/存储/对象存储OSS.md) — 存储
7. [关系型数据库RDS](../../Aliyun/数据库/关系型数据库RDS.md) — 数据库

### Azure 路径
1. [0_Azure-VM-VMSS](../../Azure/0_Azure-VM-VMSS.md) — 虚拟机基础
2. [6_Azure-Networking](../../Azure/6_Azure-Networking.md) — 网络
3. [5_Azure-Storage](../../Azure/5_Azure-Storage.md) — 存储
4. [2_AKS-basics](../../Azure/2_AKS-basics.md) — AKS 入门
5. [3_AKS-workload-identity](../../Azure/3_AKS-workload-identity.md) + [4_AKS-SecretProviderClass-KeyVault](../../Azure/4_AKS-SecretProviderClass-KeyVault.md) — AKS 安全集成
6. [8_Azure-devops-basics](../../Azure/8_Azure-devops-basics.md) → [9_Azure-devops-self-host-agents](../../Azure/9_Azure-devops-self-host-agents.md) — DevOps
7. [11_Azure-Policy](../../Azure/11_Azure-Policy.md) — 治理

---

## 独有优势分析

> [!tip] Aliyun 独有
> - 安全产品矩阵完整：WAF + DDoS + 云防火墙 + 云安全中心
> - 网络架构深度：VPC + CEN-TR + VPN + 专线
> - ACP 认证备考资料

> [!tip] Azure 独有
> - AKS 深度集成：Workload Identity + KeyVault + SecretProviderClass
> - DevOps 流水线：Agent Pool 管理
> - 排障工具链：KQL + Fiddler + PerfMon + Browser Trace + JFrog

---

## 🔗 关联领域
- [kubernetes-map](kubernetes-map.md) — K8s 自建集群 vs 云托管
- [计算机网络基础](../../Networking/计算机网络基础.md) — 云网络理论基础
- [跨域共享CORS](../../Aliyun/存储/跨域共享CORS.md) — 跨域问题（通用）
