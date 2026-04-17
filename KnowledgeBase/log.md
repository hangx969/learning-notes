---
title: 操作日志
tags:
  - knowledgebase/log
date: 2026-04-17
---

# 📋 操作日志

> 仅追加的操作记录——摄入、查询、lint、结构调整。
> 最新条目在最上方。

---

## [2026-04-17] restructure | Phase 0 + Phase 1 改造

- 创建 `CLAUDE.md` schema 文件，定义三层架构、页面模板、操作流程
- 创建 `KnowledgeBase/sources/` 目录（原始来源摘要页存放处）
- 创建 `KnowledgeBase/entities/` 目录（工具/平台实体页存放处）
- 创建 `KnowledgeBase/log.md`（本文件）
- 将 18 个实体页从 `concepts/` 拆分到 `entities/`：AKS、Aliyun、ArgoCD、Azure、Claude-Code、Docker、Grafana、Helm、Ingress、Istio、Jenkins、Kubernetes、MCP、Obsidian、OpenClaw、Prometheus、Slurm、Terraform
- 保留 7 个概念页在 `concepts/`：CICD、Observability、Python运维开发、容器运行时、日志系统、服务网格、自动化运维
- 重构 `INDEX.md`，统一使用 `[[wikilink]]` 格式，按 concepts/entities/maps/analysis/maintenance 分类
- 更新所有概念页和实体页的交叉引用链接

---

## [2026-04-16] create | 初始构建知识编译层

- 创建全部知识编译层：盘点(2) + 地图(8) + 概念(25) + 分析(3) + 维护(3)
- 创建 INDEX.md 导航入口
