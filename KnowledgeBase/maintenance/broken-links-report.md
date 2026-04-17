---
title: 断链报告
tags:
  - knowledgebase/maintenance
date: 2026-04-17
---

# 🔗 断链报告

> [!info] 扫描日期：2026-04-17（首次 Lint）

---

## 总览

| 指标 | 数值 |
|------|------|
| 总 wikilink 目标 | 609 |
| 有效链接 | 381（63%） |
| 断链（红链） | 225 |
| 孤儿页面 | 0 ✅ |

---

## 已修复的问题

### 错误分类链接（5 个 → 已修复 ✅）

以下实体在 Phase 1 中从 `concepts/` 移到 `entities/`，但部分文件仍引用旧路径：

| 错误路径 | 正确路径 | 所在文件 |
|----------|---------|---------|
| `concepts/Kubernetes` | `entities/Kubernetes` | `maintenance/naming-normalization.md` |
| `concepts/Helm` | `entities/Helm` | `maintenance/naming-normalization.md` |
| `concepts/Istio` | `entities/Istio` | `maintenance/naming-normalization.md` |
| `concepts/ArgoCD` | `entities/ArgoCD` | `maintenance/naming-normalization.md` |
| `concepts/Ingress` | `entities/Ingress` | `sources/k8s-networking-service-mesh-batch-summary.md` |

### 高频红链 → 已创建 stub 页面（17 个）

| 实体 | 引用次数 | 状态 |
|------|:--------:|------|
| Harbor | 8 | ✅ stub 已创建 |
| Redis | 6 | ✅ stub 已创建 |
| GitLab | 5 | ✅ stub 已创建 |
| Kafka | 5 | ✅ stub 已创建 |
| Loki | 5 | ✅ stub 已创建 |
| MySQL | 5 | ✅ stub 已创建 |
| NVIDIA | 4 | ✅ stub 已创建 |
| PBS | 4 | ✅ stub 已创建 |
| containerd | 4 | ✅ stub 已创建 |
| CUDA | 3 | ✅ stub 已创建 |
| Calico | 3 | ✅ stub 已创建 |
| Docker Compose | 3 | ✅ stub 已创建 |
| Kustomize | 3 | ✅ stub 已创建 |
| NFS | 3 | ✅ stub 已创建 |
| Nginx | 3 | ✅ stub 已创建 |
| PostgreSQL | 3 | ✅ stub 已创建 |
| Rancher | 3 | ✅ stub 已创建 |

---

## 剩余红链

### 建议优先创建的概念页（引用 ≥2 次）

| 概念 | 引用次数 |
|------|:--------:|
| StorageClass | 3 |
| CRD | 2 |
| Operator模式 | 2 |
| RBAC | 2 |
| ServiceMesh | 2 |
| 联邦集群 | 2 |
| 高可用架构 | 2 |

### ~~建议优先创建的实体页（引用 ≥3 次）~~ → 已全部创建 ✅

### 低频红链统计

| 类别 | 引用 2 次 | 引用 1 次 |
|------|:---------:|:---------:|
| concepts/ | 7 | 62 |
| entities/ | 50 | 111 |

> [!note] 处理策略
> - 引用 ≥3 次：建议在下次 Ingest 或维护中创建 stub 页面
> - 引用 1-2 次：Obsidian 原生支持红链显示，保持现状即可
> - 后续新增文档摄入时会自然消化部分红链
