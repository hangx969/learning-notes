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
- [[KnowledgeBase/entities/Aliyun|Aliyun]]
- [[KnowledgeBase/entities/Azure|Azure]]
- [[KnowledgeBase/entities/AKS|AKS]]

---

## 功能域对标

| 功能域 | Aliyun | Azure |
|--------|--------|-------|
| **计算** | [[Aliyun/计算/ECS|ECS]]、[[Aliyun/计算/弹性伸缩ESS|弹性伸缩ESS]] | [[Azure/0_Azure-VM-VMSS|0_Azure-VM-VMSS]] |
| **K8s 托管** | — | [[Azure/2_AKS-basics|2_AKS-basics]]、[[Azure/3_AKS-workload-identity|3_AKS-workload-identity]]、[[Azure/4_AKS-SecretProviderClass-KeyVault|4_AKS-SecretProviderClass-KeyVault]] |
| **网络** | [[Aliyun/网络/VPC|VPC]]、[[Aliyun/网络/CEN-TR|CEN-TR]]、[[Aliyun/网络/网关-VPN-专线|网关-VPN-专线]] | [[Azure/6_Azure-Networking|6_Azure-Networking]] |
| **负载均衡** | [[Aliyun/网络/负载均衡SLB|负载均衡SLB]]（CLB/ALB/NLB） | 含在 Azure Networking |
| **存储** | [[Aliyun/存储/对象存储OSS|对象存储OSS]]、[[Aliyun/存储/数据湖-HDFS-POSIX|数据湖-HDFS-POSIX]] | [[Azure/5_Azure-Storage|5_Azure-Storage]] |
| **容器镜像** | — | [[Azure/7_ACR-ACI|7_ACR-ACI]] |
| **数据库** | [[Aliyun/数据库/关系型数据库RDS|关系型数据库RDS]]、[[Aliyun/数据库/数据传输服务DTS|数据传输服务DTS]] | — |
| **安全-WAF** | [[Aliyun/网络/WAF|WAF]] | — |
| **安全-DDoS** | [[Aliyun/网络/DDoS高防|DDoS高防]] | — |
| **安全-防火墙** | [[Aliyun/网络/云安全中心-云防火墙|云安全中心-云防火墙]] | — |
| **安全-策略** | — | [[Azure/11_Azure-Policy|11_Azure-Policy]] |
| **DevOps** | — | [[Azure/8_Azure-devops-basics|8_Azure-devops-basics]]、[[Azure/9_Azure-devops-self-host-agents|9_Azure-devops-self-host-agents]]、[[Azure/10_Azure-devops-agent-pool-management|10_Azure-devops-agent-pool-management]] |
| **迁移** | [[Aliyun/计算/主机迁移工具SMC|主机迁移工具SMC]] | — |
| **资源管理** | [[Aliyun/资源管理/Landing Zone|Landing Zone]] | — |
| **认证考试** | [[Aliyun/ACP考试|ACP考试]] | — |
| **排障工具** | — | [[Azure/Kusto Query|Kusto Query]]、[[Azure/IO-monitor|IO-monitor]]、[[Azure/fiddler|fiddler]]、[[Azure/browser trace|browser trace]] |

---

## 推荐阅读顺序

### Aliyun 路径
1. [[Aliyun/网络/VPC|VPC]] — 网络基础
2. [[Aliyun/计算/ECS|ECS]] — 计算入口
3. [[Aliyun/网络/负载均衡SLB|负载均衡SLB]] — 流量分发
4. [[Aliyun/网络/DNS-CDN-SSL|DNS-CDN-SSL]] — 域名与加速
5. [[Aliyun/网络/WAF|WAF]] → [[Aliyun/网络/DDoS高防|DDoS高防]] → [[Aliyun/网络/云安全中心-云防火墙|云安全中心-云防火墙]] — 安全链
6. [[Aliyun/存储/对象存储OSS|对象存储OSS]] — 存储
7. [[Aliyun/数据库/关系型数据库RDS|关系型数据库RDS]] — 数据库

### Azure 路径
1. [[Azure/0_Azure-VM-VMSS|0_Azure-VM-VMSS]] — 虚拟机基础
2. [[Azure/6_Azure-Networking|6_Azure-Networking]] — 网络
3. [[Azure/5_Azure-Storage|5_Azure-Storage]] — 存储
4. [[Azure/2_AKS-basics|2_AKS-basics]] — AKS 入门
5. [[Azure/3_AKS-workload-identity|3_AKS-workload-identity]] + [[Azure/4_AKS-SecretProviderClass-KeyVault|4_AKS-SecretProviderClass-KeyVault]] — AKS 安全集成
6. [[Azure/8_Azure-devops-basics|8_Azure-devops-basics]] → [[Azure/9_Azure-devops-self-host-agents|9_Azure-devops-self-host-agents]] — DevOps
7. [[Azure/11_Azure-Policy|11_Azure-Policy]] — 治理

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
- [[KnowledgeBase/maps/kubernetes-map|kubernetes-map]] — K8s 自建集群 vs 云托管
- [[Networking/计算机网络基础|计算机网络基础]] — 云网络理论基础
- [[Aliyun/存储/跨域共享CORS|跨域共享CORS]] — 跨域问题（通用）
