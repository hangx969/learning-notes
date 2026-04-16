---
title: 高价值知识缺口
tags:
  - knowledgebase/analysis
  - knowledgebase/gaps
date: 2026-04-16
---

# 🔍 高价值知识缺口

> [!info] 识别多次提到但没有专门页面的主题、明显偏空白的领域、以及高价值但低连接的知识孤岛。

---

## 一、多次提到但没有专门页面的主题

| 主题 | 被引用位置 | 当前状态 | 优先级 |
|------|-----------|----------|:------:|
| **etcd** | K8s 安装多篇、高可用配置 | 有 1 篇 etcd 高可用，但无独立概念页 | 🔥 高 |
| **Calico / CNI** | K8s 基础、网络安全 | 有 1 篇 Calico 基础，CNI 无专题 | 🔥 高 |
| **RBAC** | K8s 认证授权准入 | 嵌入在 K8s 认证文章中，无独立页 | ⭐ 中 |
| **PV/PVC/StorageClass** | K8s 存储、Ceph | 嵌入在 storage 文章中 | ⭐ 中 |
| **Nginx** | Docker 部署、Python 运维、Ingress | 分散在 3 个目录，无统一页 | ⭐ 中 |
| **Ansible** | Linux-Shell 有 1 篇 | 仅安装篇，无 playbook/role/galaxy 深入 | 🔥 高 |
| **Alertmanager** | Prometheus 监控系列 | 有 1 篇版本特定部署，无告警规则最佳实践 | ⭐ 中 |
| **PromQL** | Prometheus 多篇引用 | 完全无专门内容 | 🔥 高 |
| **KQL (Kusto)** | Azure 排障 | 有 1 篇参考，但无系统教程 | ⭐ 中 |

---

## 二、应该存在但明显偏空白的领域

### 🔥 高优先级空白

**1. GitOps 方法论**
- 现状：ArgoCD 工具使用有 4 篇，但 GitOps 理论、最佳实践、工作流设计为零
- 价值：GitOps 是云原生 CI/CD 的核心范式
- 关联：[[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD基础]]

**2. SRE 实践与可靠性工程**
- 现状：完全空白。有故障排查指南和生产优化，但无 SRE 体系
- 价值：SLO/SLI/Error Budget 是运维工程师核心技能
- 关联：[[Docker-Kubernetes/k8s-installation-management/k8s故障排查指南]]、[[KnowledgeBase/concepts/Observability]]

**3. 混沌工程**
- 现状：完全空白
- 价值：Chaos Mesh / Litmus 是 K8s 生态重要组成
- 关联：[[Docker-Kubernetes/k8s-installation-management/k8s生产环境优化与最佳实践]]

**4. 容器安全深入**
- 现状：仅有 Trivy/SonarQube 工具安装，缺少安全扫描策略、镜像签名、运行时安全
- 价值：安全左移是云原生趋势
- 关联：[[Docker-Kubernetes/k8s-security-auth/helm部署trivy-operator]]

**5. FinOps / 云成本优化**
- 现状：完全空白
- 价值：多云环境下成本优化是刚需
- 关联：Aliyun、Azure 两个云平台

### ⭐ 中优先级空白

**6. K8s Operator 开发**
- 现状：有 CRD 基础 + Operator 部署 MySQL/Redis，但无自定义 Operator 开发
- 关联：[[Docker-Kubernetes/k8s-basic-resources/k8s基础-自定义CRD资源]]

**7. Go 并发与微服务**
- 现状：Go 基础完整，但缺少 goroutine、channel、微服务框架
- 关联：[[Go/云原生开发-基础]]

**8. API Gateway**
- 现状：有 Ingress-Nginx 和 Istio，但无 Kong/APISIX/Traefik 等 API 网关
- 关联：[[Docker-Kubernetes/k8s-basic-resources/k8s基础-ingress]]

**9. 分布式系统理论**
- 现状：有 etcd 高可用，但缺 CAP/Raft/Paxos 理论基础
- 关联：[[Docker-Kubernetes/k8s-installation-management/etcd高可用配置以及模拟集群故障和恢复]]

---

## 三、高价值但低连接的知识孤岛

> [!warning] 以下文档/领域有价值内容但几乎不被其他文档引用

| 孤岛 | 内容价值 | 连接缺失 |
|------|----------|----------|
| [[CloudComputing/深入剖析Kubernetes]] | K8s 理论深入 | 未被 145 篇 K8s 实操文档引用 |
| [[CloudComputing/Auth]] | OAuth/OIDC/SAML/SSO | 未连接到 Azure AD、K8s RBAC |
| [[Docker-Kubernetes/简历指南]] | 求职实用 | 孤立文档 |
| [[Linux-Shell/Linux-learning-notes]] | 2688 行 Linux 知识 | 未连接到任何其他文档 |
| [[Docker-Kubernetes/k8s-installation-management/k8s两地三中心架构]] | 高可用架构 | 未连接到 Aliyun/Azure 多地域 |
| [[GPU-DeepLearning/Server-basics]] | 服务器硬件知识 | 未连接到 HPC、GPU |
| [[Middlewares/Kafka]] + [[Middlewares/RabbitMQ]] + [[Middlewares/RocketMQ]] | 消息中间件对比 | 无 Frontmatter，无双链，三者之间也无互引 |

---

## 行动建议

1. **补概念页**：etcd、Calico、RBAC、PromQL
2. **补专题文章**：GitOps 方法论、SRE 基础、混沌工程入门
3. **修复孤岛**：为 CloudComputing 和 Middlewares 添加双链
4. **强化连接**：Linux-learning-notes 拆分或添加索引
