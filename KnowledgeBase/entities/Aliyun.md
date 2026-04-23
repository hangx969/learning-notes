---
title: Aliyun
tags:
  - knowledgebase/entity
  - aliyun
date: 2026-04-17
sources:
  - "[[Aliyun/计算/ECS]]"
  - "[[Aliyun/网络/VPC]]"
  - "[[Aliyun/网络/负载均衡SLB]]"
  - "[[Aliyun/网络/CEN-TR]]"
  - "[[Aliyun/存储/对象存储OSS]]"
  - "[[Aliyun/数据库/关系型数据库RDS]]"
  - "[[Aliyun/资源管理/Landing Zone]]"
  - "[[Aliyun/资源管理/FinOps-云成本优化实战]]"
  - "[[KnowledgeBase/sources/aliyun-batch-summary]]"
---

# Aliyun

## 简介

阿里云（Alibaba Cloud）是阿里巴巴集团旗下的公有云平台，提供计算、网络、存储、数据库、安全、资源管理等全栈云服务。本仓库共收录 19 篇阿里云相关笔记（详见 [[KnowledgeBase/sources/aliyun-batch-summary|Aliyun 来源批量摘要]]），围绕 **ACP 云计算工程师认证备考**和**实战运维**两条主线展开，系统梳理五大领域的产品架构、功能特性与计费模式。认证路径为 ACP → 专项工程师 → ACE 架构师（详见 [[Aliyun/ACP考试|ACP 考试笔记]]）。

## 核心服务覆盖

### 计算：ECS / ESS

- **ECS** 虚拟化架构经历四代演进：Xen → KVM → 神龙架构（裸金属零损耗）→ CIPU，费用由实例规格、镜像、云盘、公网带宽、快照五部分构成
- 计费模式：按量付费、包年包月、抢占式实例；节省计划相当于按量付费的预付会员卡
- **云盘**采用三副本机制分布在不同机架，ESSD 多重挂载（NVMe 共享盘）可同时挂载至最多 16 台 ECS；一块云盘只能挂载到同一地域同一可用区的一台 ECS
- 快照机制：首份全量，后续增量
- **ESS 弹性伸缩**自动创建/删除 ECS 实例并联动 SLB（加入后端服务器组）和 RDS（IP 加入白名单），支持优先级、均衡分布、成本优化三种策略
- **SMC 主机迁移**支持跨账号、跨 Region、VMWare 无代理迁移，通过中转实例中转数据再制作镜像
- 详见 [[Aliyun/计算/ECS|ECS]]、[[Aliyun/计算/弹性伸缩ESS|ESS]]、[[Aliyun/计算/云盘-快照-镜像|云盘快照镜像]]、[[Aliyun/计算/主机迁移工具SMC|SMC]]

### 网络：VPC / SLB / WAF / DDoS / CDN / CEN

**VPC 是所有网络服务的基础枢纽**，几乎所有计算、数据库文档都依赖 VPC 作为基础网络环境：

- **VPC** 基于隧道技术实现二层和三层网络隔离，不同 VPC 天然不互通。路由表采用最长前缀匹配，每个交换机网段首尾 4 个 IP 为系统保留
- VPC 互通方式：VPC Peering、云企业网 CEN、VPN 网关
- **CEN + TR**：CEN 打通不同地域/账号的 VPC 内网连接，TR（转发路由器）作为地域级核心转发组件，支持统一互联网出口和共享服务 VPC 架构
- **SLB 负载均衡**产品家族：ALB（七层，100 万 QPS）、NLB（四层，1 亿并发）、CLB（传统，四层基于 LVS+keepalived，七层基于 Tengine）。CLB 仅提供被动公网访问，主动出公网需 EIP/NAT
- **NAT 网关**提供 SNAT（出）和 DNAT（入），支持多台 ECS 共用，与 EIP（只能绑一台）形成互补
- **连接本地 IDC**：VPN 网关、高速通道（运营商专线）、智能接入网关 SAG
- **DNS/CDN/SSL**：云解析 DNS 是唯一提供 100% SLA 的服务，TTL 最快 1 秒全球生效；CDN 将源站资源缓存到全球加速节点
- **ACK 网络规划**：Pod/Service CIDR 设计直接影响成本（IP 不足→集群重建、CIDR 重叠→跨 AZ 绕路），网络插件 Flannel（轻量）vs Terway（ENI 弹性）按集群规模选型
- 详见 [[Aliyun/网络/VPC|VPC]]、[[Aliyun/网络/CEN-TR|CEN-TR]]、[[Aliyun/网络/负载均衡SLB|SLB]]、[[Aliyun/网络/网关-VPN-专线|网关-VPN-专线]]、[[Aliyun/网络/DNS-CDN-SSL|DNS-CDN-SSL]]、[[Aliyun/网络/ACK网络规划与成本优化|ACK 网络规划]]

**安全防护形成多层纵深联动**：

- **WAF**（七层）：防护 SQL 注入、XSS、WebShell、CC 攻击等 OWASP 威胁，3.0 版本引入 SDK 插件模式嵌入 ALB/MSE/FC 网关，无需额外转发层
- **DDoS 高防**（三/四层）：覆盖 SYN Flood、CC 攻击、Slowloris 慢速攻击、DNS 随机子域名攻击等，免费版遭攻击时会被拉入黑洞
- **云防火墙**（SaaS 化）：区分南北流量（互联网边界）和东西流量（VPC 边界）
- **云安全中心**（态势感知）：通过 Agent 部署，企业版满足等保合规，旗舰版额外支持容器安全
- 详见 [[Aliyun/网络/WAF|WAF]]、[[Aliyun/网络/DDoS高防|DDoS 高防]]、[[Aliyun/网络/云安全中心-云防火墙|云安全中心与云防火墙]]

### 存储：OSS

- 对象存储采用扁平化 Key-Value 架构（哈希表结构），无论数据量多大查找速度一致，不支持部分修改只能整体覆盖
- 系统对比：块存储（数组）vs 文件存储（二叉树）vs 对象存储（哈希表）
- **数据湖趋势**：存算分离，OSS/S3 负责存储，Spark/K8s 负责计算；数据仓库是 ETL（先清洗再存），数据湖是 ELT（先存再分析）
- S3/OSS 不完全兼容 POSIX，强行挂载模拟会导致性能极差
- **CORS 跨域**：同源策略要求协议+域名+端口完全一致，复杂请求先发 OPTIONS 预检，需在流量入口配置 Access-Control-Allow-* 响应头
- 详见 [[Aliyun/存储/对象存储OSS|OSS]]、[[Aliyun/存储/数据湖-HDFS-POSIX|数据湖]]、[[Aliyun/存储/跨域共享CORS|CORS]]

### 数据库：RDS / DTS

- **RDS** 支持 MySQL、SQL Server、PostgreSQL、MariaDB 四种引擎，实例类型分基础版/高可用版（一主一备）/集群版（一主四备可读）
- 高可用版备节点故障时主节点会短暂只读（全局锁，不超过 5 秒）
- ESSD PL3 相比 PL1 最高提升 20 倍 IOPS、11 倍吞吐量
- **DTS** 提供数据同步、迁移、集成、订阅、加工、校验六大功能。同步适合长期实时双向，迁移适合短期单向；不停机迁移需同时选择结构迁移+全量迁移+增量迁移
- 详见 [[Aliyun/数据库/关系型数据库RDS|RDS]]、[[Aliyun/数据库/数据传输服务DTS|DTS]]

### 资源管理：Landing Zone / FinOps

- 企业上云框架 Landing Zone 涵盖资源规划、财务管理、网络规划、身份权限、安全防护、合规审计、运维管理、自动化八大模块
- CAF（云采用框架）四阶段：上云战略 → 上云准备 → 应用上云 → 运营治理
- 核心原则：**网络先行**——先确定 Region，再规划 VPC 互通/隔离，最后确定云上云下互联方式
- Landing Zone 的八大模块恰好对应了仓库中其他文档中各产品的具体实现
- **FinOps 成本优化**：先量化（三个月账单基线）→ 再优化（夜间关机、降配、存储分层、EIP 回收）→ 再固化（预算告警、Infracost PR 卡点、Prometheus 账单看板）。覆盖阿里云/腾讯云/华为云三家 CLI 操作
- 详见 [[Aliyun/资源管理/Landing Zone|Landing Zone]]、[[Aliyun/资源管理/FinOps-云成本优化实战|FinOps]]

## 实践亮点

1. **安全防护纵深联动**：WAF（七层）+ DDoS 高防（三/四层）+ 云防火墙（南北+东西流量）+ 云安全中心（主机层）形成完整的多层防御体系
2. **弹性伸缩深度集成**：ESS 一次扩容自动联动 ECS 创建、SLB 后端挂载、RDS 白名单更新三大操作，缩容反向操作，体现云服务间深度耦合设计
3. **迁移工具链完整**：SMC 负责主机迁移（支持无代理 VMWare 迁移），DTS 负责数据库迁移/同步，两者配合覆盖大部分企业上云场景
4. **VPC 作为核心枢纽**：CIDR 规划、路由表、安全组贯穿全局，CEN + TR 实现跨地域/跨账号统一组网
5. **存算分离趋势**：从 OSS 到数据湖架构，强调存储与计算分离的云原生理念

## 与 Azure 对比视角

| 维度 | 阿里云 | Azure |
|------|--------|-------|
| 计算 | ECS（神龙/CIPU 架构）、ESS 弹性伸缩 | VM/VMSS（Fabric Controller 管理） |
| 容器 | ACK（本仓库未覆盖） | AKS（3 篇深度文档） |
| 网络 | VPC + CEN/TR 跨地域组网 | VNet + VNet Peering |
| 负载均衡 | ALB/NLB/CLB 三代产品 | Azure Load Balancer / App Gateway |
| 对象存储 | OSS | Azure Blob Storage |
| 数据库 | RDS（四引擎） | Azure SQL / Cosmos DB（本仓库未覆盖） |
| CI/CD | 未覆盖 | Azure DevOps（3 篇全链路文档） |
| 治理 | Landing Zone 八大模块 | Azure Policy（本仓库已覆盖，Landing Zone 未覆盖） |
| 安全 | WAF + DDoS + 云防火墙 + 云安全中心 | 未覆盖 |
| 诊断工具 | 未覆盖 | KQL + Fiddler + PerfMon 等完整工具链 |
| 侧重点 | ACP 认证备考 + 产品全景 | 技术支持工程师实战运维 |

两套知识体系互为补充：阿里云侧重**产品架构和功能全景**（安全、网络尤为丰富），Azure 侧重**运维实操和故障排查工具链**。

## 相关概念与实体

- [[KnowledgeBase/entities/Azure|Azure]] - 对标公有云平台
- [[KnowledgeBase/entities/ECS|ECS]] / [[KnowledgeBase/entities/VPC|VPC]] / [[KnowledgeBase/entities/OSS|OSS]]
- [[KnowledgeBase/entities/RDS|RDS]] / [[KnowledgeBase/entities/DTS|DTS]]
- [[KnowledgeBase/entities/SLB|SLB]] / [[KnowledgeBase/entities/CEN|CEN]]
- [[KnowledgeBase/entities/WAF|WAF]] / [[KnowledgeBase/entities/DDoS|DDoS]]
- [[KnowledgeBase/entities/HDFS|HDFS]] / [[KnowledgeBase/entities/Landing Zone|Landing Zone]]
- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 知识空白

- **容器服务 ACK**：已有网络规划与成本优化（[[Aliyun/网络/ACK网络规划与成本优化|ACK 网络规划]]），但缺少 ACK 集群部署、运维、与 AKS 对比等完整实践
- **Terraform Provider**：缺少阿里云 Terraform 资源编排实践
- **多云/混合云架构**：缺少 Azure + Aliyun 混合云设计方案
- **日志服务 SLS**：缺少阿里云可观测性体系（SLS、ARMS、Prometheus 集成）
- **RAM 权限管理**：缺少 RAM 用户/角色/策略的安全合规实践
- **Serverless**：缺少函数计算 FC、Serverless 应用引擎 SAE 等无服务器产品
- ~~**成本优化**：缺少 FinOps 实践~~ → 已补充 [[Aliyun/资源管理/FinOps-云成本优化实战|FinOps 实战]]
