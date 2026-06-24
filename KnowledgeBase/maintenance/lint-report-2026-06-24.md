---
title: 知识库全量 Lint 报告 (2026-06-24)
tags:
  - knowledgebase/maintenance
  - lint-report
date: 2026-06-24
aliases:
  - Lint报告-20260624
---

# 知识库全量 Lint 报告 (2026-06-24)

> 覆盖 6 大检查维度：断链、孤儿页、交叉引用、来源时效性、Frontmatter 一致性、模板合规性。
> 审计范围：KnowledgeBase/ 下全部 113 个页面 + 全库原始来源文件。

---

## 📊 总览仪表盘

| 维度 | 状态 | 核心指标 |
|------|:----:|---------|
| **断链检查** | 🔴 | 810 个唯一链接目标中 234 个断链（29%） |
| **孤儿页检查** | 🟡 | 123 页中 29 页无入链（24%），但核心概念/实体页 0 孤儿 |
| **交叉引用** | 🟡 | 122 处缺失交叉引用（概念/实体页正文提及但未加 wikilink） |
| **来源时效性** | 🟡 | 4 篇严重过期（>20天）、2 篇 0raw/ 未处理、~25 篇原始文件无 wiki 覆盖 |
| **Frontmatter** | 🟡 | tags 100% 正确；25 页缺 sources、50+ 页缺 aliases |
| **模板合规** | 🟡 | 来源页 46/46 合规；概念页 6/13 合规；实体页 9/36 合规 |

---

## 1. 断链检查 🔴

**统计**：810 个唯一链接目标 → 234 个真正断链

### 1.1 路径不匹配（文件存在但路径已变）— 5 处

| 摘要页 | 引用路径 | 实际路径 |
|--------|---------|---------|
| `ClaudeCode基础指南-summary` | `Claude Code 基础指南` | `AI/ClaudeCode/Claude Code 基础指南.md` |
| `codegraph-summary` | `CodeGraph-代码语义知识图谱` | `AI/代码知识图谱/CodeGraph-代码语义知识图谱.md` |
| `graphify-summary` | `Graphify-软件工程知识图谱工具` | `AI/代码知识图谱/Graphify-软件工程知识图谱工具.md` |
| `k8s-mcp-server-dify-summary` | `Kubernetes-MCP-Server-Dify智能运维` | `AI/AIOps/Kubernetes-MCP-Server-Dify智能运维.md` |
| `rag-pdf-parsing-summary` | `RAG-PDF解析难点与主流方案` | `AI/RAG/RAG-PDF解析难点与主流方案.md` |

### 1.2 文件已删除/重命名 — 1 处

| 摘要页 | 引用路径 | 最近匹配 |
|--------|---------|---------|
| `claude-md-complete-guide-summary` | `CLAUDE.md完全指南-规则-指令-维护工程` | `CLAUDE.md维护工程-四层加载与指令预算.md` |

### 1.3 批量路径缺失 — 91 处

| 摘要页 | 断链数 | 原因 |
|--------|:------:|------|
| `cloudops-agent-batch-summary` | 58 | 使用短文件名，缺少 `AI/RAG/CloudOps-Agent-项目/<子目录>/` 前缀 |
| `rag-agent-batch-summary` | 33 | 使用短文件名，缺少 `AI/RAG/RAG-Agent-项目/<子目录>/` 前缀 |

### 1.4 其他说明
- macOS 大小写不敏感：`INDEX.md` vs `index.md` 同一 inode，本地不影响但跨平台有风险
- 短格式 wikilink（如 `[[CodeGraph-代码语义知识图谱]]`）大多能被 Obsidian 正确解析

---

## 2. 孤儿页检查 🟡

**统计**：29/123 页无入链（但 0 概念/实体页是孤儿 ✅）

### 孤儿分布

| 类别 | 数量 | 说明 |
|------|:----:|------|
| **sources/** | 17 | 最大孤儿群体——来源摘要页仅被 index.md 表格引用，无其他页面 wikilink |
| **analysis/** | 4 | 全部分析报告均为孤儿 |
| **maintenance/inventory/** | 4 | 维护与盘点页面 |
| **maps/** | 3 | domain-map、linux-ops-map、tool-map |
| **log.md** | 1 | 预期内 |

> **结论**：核心知识页（concepts/entities）零孤儿，问题集中在辅助页面。建议在相关概念/实体页的"在本仓库中的覆盖"部分补充 sources/ 链接。

---

## 3. 交叉引用缺失 🟡

**统计**：122 处——页面正文提及实体/概念名称但未添加 wikilink

### 缺失最多的页面 (Top 10)

| 页面 | 缺失数 | 缺失引用 |
|------|:------:|---------|
| Kubernetes.md | 10 | Azure, CRD, Docker-Compose, Harbor, NVIDIA, Nginx, RBAC… |
| CICD.md | 7 | ArgoCD, Docker, GitLab, Helm, Jenkins, Kubernetes, Kustomize |
| Helm.md | 7 | Docker, GitLab, Kustomize, Kyverno, Loki, Nginx, Terraform |
| Observability.md | 6 | Azure, Docker, Grafana, Kubernetes, Loki, Prometheus |
| Ingress.md | 5 | Azure, Docker, Harbor, Jenkins, Nginx |
| Jenkins.md | 5 | CICD, GitLab, Ingress, NFS, Prometheus |
| Python运维开发.md | 5 | Kubernetes, MySQL, Nginx, PostgreSQL, Terraform |
| ArgoCD.md | 5 | CICD, CRD, Calico, Kustomize, RBAC |
| 日志系统.md | 5 | Docker, Helm, Kafka, Kubernetes, Loki |
| 服务网格.md | 5 | Docker, Ingress, Istio, Kubernetes, Nginx |

### 最常被遗漏的实体
- **Docker**：被 21 个页面正文提及但未添加 wikilink
- **Kubernetes**：12 个页面
- **Nginx**：8 个页面

---

## 4. 来源时效性 🟡

### 4.1 严重过期摘要（>20天）

| 过期天数 | 摘要页 | 原始文档修改日 | 摘要修改日 |
|:--------:|--------|:------------:|:----------:|
| **53** | 多智能体协作-summary | 2026-06-10 | 2026-04-17 |
| **50** | Claude-Code扩展体系-summary | 2026-06-06 | 2026-04-17 |
| **33** | harnesskit-summary | 2026-06-07 | 2026-05-05 |
| **24** | obsidian-claude-AI知识库完整指南-summary | 2026-06-03 | 2026-05-09 |
| **23** | openclaw-agents-export-summary | 2026-05-11 | 2026-04-18 |
| **20** | misc-domains-batch-summary | 2026-05-07 | 2026-04-17 |

### 4.2 未处理的 0raw/ 文件

| 待处理天数 | 文件 |
|:----------:|------|
| 19 天 | `AI 代码审查的工程化实践：阿里 Open Code Review 开源.md` |
| 19 天 | `OpenCodeReview.md`（同一主题） |

### 4.3 无 wiki 覆盖的原始文件（排除课程批量文件）

| 领域 | 数量 | 代表文件 |
|------|:----:|---------|
| AI | ~17 | Claude-Code为什么用grep不用RAG、AI-视觉系列（5篇）、OpenClaw-K8s智能运维实战… |
| Docker-K8s | 3 | k8s部署防火墙端口配置、Istio-Sidecar-vs-Ambient、简历指南 |
| Aliyun | 2 | FinOps-云成本优化实战、ACK网络规划与成本优化 |
| Go | 1 | client-go-K8s客户端开发 |

---

## 5. Frontmatter 一致性 🟡

### 5.1 tags 合规 ✅

| 目录 | 预期 tag | 合规率 |
|------|---------|:------:|
| concepts/ | `knowledgebase/concept` | 14/14 (100%) |
| entities/ | `knowledgebase/entity` | 36/36 (100%) |
| sources/ | `knowledgebase/source` | 46/46 (100%) |
| maps/ | `knowledgebase/map` | 8/8 (100%) |

### 5.2 缺失字段

| 字段 | 缺失页数 | 说明 |
|------|:--------:|------|
| `title` | 0 | ✅ 全部合规 |
| `date` | 0 | ✅ 全部合规 |
| `sources` | 25 | 8 概念页 + 17 实体 stub 页 |
| `aliases` | 50+ | 遍布所有类别 |

### 5.3 index.md 缺失条目 — 4 页

- `sources/claude-md-maintenance-summary.md`
- `sources/k8s-cgroup-v2-summary.md`
- `sources/kyverno-1.18-summary.md`
- `sources/rabbitmq-ha-summary.md`

---

## 6. 模板合规性 🟡

### 6.1 概念页（concepts/）

| 状态 | 数量 | 页面 |
|------|:----:|------|
| ✅ 完全合规 | 6 | CRD、Operator模式、RBAC、StorageClass、联邦集群、高可用架构 |
| 🟡 旧模板 | 7 | CICD、Observability、Python运维开发、容器运行时、日志系统、服务网格、自动化运维 |

### 6.2 实体页（entities/）

| 状态 | 数量 | 说明 |
|------|:----:|------|
| ✅ 实质合规 | 9 | Aliyun、Azure、Claude-Code、Docker、Hermes-Agent、Kubernetes、Kyverno、MCP、Obsidian |
| 🟡 旧模板 | 10 | AKS、ArgoCD、Grafana、Helm、Ingress、Istio、Jenkins、Prometheus、Slurm、Terraform |
| ⚪ Stub 页 | 17 | 最小内容，缺 核心功能/使用场景/知识空白 |

### 6.3 来源页（sources/）
- **46/46 合规** ✅（批量摘要用 `整体概述`/`各文档摘要` 变体，属合理适配）

---

## 📋 优先修复清单

### 🔴 高优先（影响知识准确性）

| # | 任务 | 涉及页数 | 预估工作量 |
|---|------|:--------:|:---------:|
| 1 | 修复 5 处路径不匹配的断链引用 | 5 | 小 |
| 2 | 补充 4 篇缺失的 index.md 条目 | 4 | 小 |
| 3 | 调查被删文件 `CLAUDE.md完全指南-规则-指令-维护工程` | 1 | 小 |

### 🟡 中优先（提升知识完整度）

| # | 任务 | 涉及页数 | 预估工作量 |
|---|------|:--------:|:---------:|
| 4 | 重新摄入 4 篇严重过期摘要（>20天） | 4 | 中 |
| 5 | 处理 0raw/ 中 2 篇未摄入文章 | 2 | 中 |
| 6 | 修复 cloudops/rag-agent 批量摘要的 91 处短路径断链 | 2 | 中 |
| 7 | 迁移 7 篇旧模板概念页到标准模板 | 7 | 中 |
| 8 | 迁移 10 篇旧模板实体页到标准模板 | 10 | 大 |

### 🟢 低优先（锦上添花）

| # | 任务 | 涉及页数 | 预估工作量 |
|---|------|:--------:|:---------:|
| 9 | 补充 122 处缺失的交叉引用 wikilink | ~30 | 大 |
| 10 | 补充 50+ 页缺失的 `aliases` 字段 | 50+ | 中（批量） |
| 11 | 补充 25 页缺失的 `sources` 字段 | 25 | 中 |
| 12 | 摄入 ~23 篇无 wiki 覆盖的原始文件 | 23 | 大 |
| 13 | 统一 INDEX.md → index.md 大小写 | 1 | 小 |
