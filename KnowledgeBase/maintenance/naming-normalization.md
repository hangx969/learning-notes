---
title: 命名规范
tags:
  - knowledgebase/maintenance
  - knowledgebase/naming
date: 2026-04-16
---

# 📝 命名规范

> [!info] 统一概念命名，避免同一事物多种写法导致链接断裂或知识碎片化。

---

## 概念命名标准

| 标准名称 | 别名/变体 | 使用规则 |
|----------|-----------|----------|
| **Claude Code** | ClaudeCode, claude-code | 两个单词空格分隔，首字母大写 |
| **OpenClaw** | Openclaw, openclaw, open-claw | 驼峰写法，O 和 C 大写 |
| **MCP** | Model Context Protocol | 缩写形式为主，全称在定义时使用 |
| **Kubernetes** | K8s, k8s | 概念页用全称，日常引用 K8s 可接受 |
| **Docker** | docker | 首字母大写 |
| **Helm** | helm | 首字母大写 |
| **Prometheus** | prometheus, prom | 首字母大写 |
| **Grafana** | grafana | 首字母大写 |
| **Istio** | istio | 首字母大写 |
| **ArgoCD** | Argo CD, argocd | 连写，A 和 C 大写 |
| **Jenkins** | jenkins | 首字母大写 |
| **Terraform** | terraform, TF | 首字母大写 |
| **Ansible** | ansible | 首字母大写 |
| **Obsidian** | obsidian | 首字母大写 |
| **Aliyun** | 阿里云, AliCloud | 英文场景用 Aliyun，中文场景用"阿里云" |
| **Azure** | azure | 首字母大写 |
| **AKS** | Azure Kubernetes Service | 缩写为主 |
| **Slurm** | slurm, SLURM | 首字母大写 |
| **PBS** | OpenPBS, Torque | 缩写为主 |
| **CI/CD** | CICD, ci/cd | 带斜杠格式 |
| **containerd** | Containerd | ==全小写==（官方风格） |
| **etcd** | ETCD, Etcd | ==全小写==（官方风格） |
| **kubeadm** | Kubeadm | ==全小写==（官方风格） |
| **kubectl** | Kubectl | ==全小写==（官方风格） |
| **nginx** | Nginx, NGINX | 文件名和概念页用 Nginx，配置文件中用 nginx |

---

## 文件命名规范

### 概念页
- 位置：`KnowledgeBase/concepts/`
- 格式：`概念名称.md`（与上表标准名称一致）
- 示例：`Claude-Code.md`、`Kubernetes.md`、`容器运行时.md`

### 地图页
- 位置：`KnowledgeBase/maps/`
- 格式：`主题-map.md`
- 示例：`kubernetes-map.md`、`tool-map.md`

### 分析页
- 位置：`KnowledgeBase/analysis/`
- 格式：`描述性名称.md`
- 示例：`topic-coverage-analysis.md`

---

## Tag 命名规范

| 格式 | 示例 | 规则 |
|------|------|------|
| 领域/子主题 | `docker/basics`, `kubernetes/ingress` | 小写，斜杠分层 |
| 知识库标签 | `knowledgebase/concept`, `knowledgebase/map` | `knowledgebase/` 前缀 |
| 云平台 | `aliyun/network`, `azure/aks` | 平台名小写 |
| 工具 | `monitoring/prometheus`, `cicd/argocd` | 功能域/工具名 |

---

## 同义词索引

> [!tip] 搜索时可能用到的别名

| 搜索词 | 应定位到 |
|--------|----------|
| 负载均衡 | [负载均衡SLB](../../Aliyun/网络/负载均衡SLB.md) |
| SLB / CLB / ALB / NLB | [负载均衡SLB](../../Aliyun/网络/负载均衡SLB.md) |
| 对象存储 | [对象存储OSS](../../Aliyun/存储/对象存储OSS.md) |
| 弹性计算 | [ECS](../../Aliyun/计算/ECS.md) |
| 容器编排 | [Kubernetes](../concepts/Kubernetes.md) |
| 服务发现 | [k8s基础-Service](../../Docker-Kubernetes/k8s-basic-resources/k8s基础-Service.md) |
| 包管理器 | [Helm](../concepts/Helm.md) |
| 可观测性 / Observability | [Observability](../concepts/Observability.md) |
| 流量管理 | [Istio](../concepts/Istio.md) |
| GitOps | [ArgoCD](../concepts/ArgoCD.md) |
