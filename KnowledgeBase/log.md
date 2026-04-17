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

## [2026-04-17] ingest | Docker-Kubernetes 全量摄入（145 篇）

- **摄入来源**：`Docker-Kubernetes/` 全部子目录，共 145 篇原始文档
- **来源摘要页（10 篇新建，按子目录批量摘要）**：
  - `sources/docker-batch-summary.md`（12 篇）
  - `sources/k8s-basic-resources-batch-summary.md`（20 篇）
  - `sources/k8s-installation-management-batch-summary.md`（16 篇）
  - `sources/k8s-monitoring-logging-batch-summary.md`（20 篇）
  - `sources/k8s-CICD-batch-summary.md`（19 篇）
  - `sources/k8s-networking-service-mesh-batch-summary.md`（7 篇）
  - `sources/k8s-security-auth-batch-summary.md`（7 篇）
  - `sources/k8s-scaling-storage-batch-summary.md`（7 篇）
  - `sources/k8s-db-middleware-UI-batch-summary.md`（18 篇）
  - `sources/k8s-misc-batch-summary.md`（18 篇：Helm/CKA-CKS/KubeBlocks/Harbor/K3S/Velero/GPU）
- **实体页增强（9 篇重写或增强）**：
  - `entities/Kubernetes.md`：从文章索引升级为知识编译页——核心架构、9 大子领域覆盖地图
  - `entities/Docker.md`：补充核心功能、部署实践总结
  - `entities/Helm.md`：补充 v3 架构、OCI 支持、Helm vs Kustomize 对比
  - `entities/ArgoCD.md`：补充架构细节、Image Updater、GitOps 理念
  - `entities/Jenkins.md`：补充 4 种部署方式、企业 DevOps 落地模式
  - `entities/Prometheus.md`：补充数据模型、3 种 HA 模式、联邦架构、5 层监控体系
  - `entities/Grafana.md`：补充统一可视化定位、LGTM 轻量级可观测性栈
  - `entities/Istio.md`：补充数据面/控制面架构、流量管理、企业落地模式
  - `entities/Ingress.md`：补充 hostNetwork 部署、DNS 解析链
- **INDEX.md 更新**：Sources 区域新增 Docker-Kubernetes 10 篇批量摘要表格

---

## [2026-04-17] ingest | Azure 全量摄入（21 篇）

- **摄入来源**：`Azure/` 目录，共 21 篇原始文档
- **来源摘要页**：`sources/azure-batch-summary.md`
- **实体页增强**：
  - `entities/Azure.md`：补充 7 大服务子领域、实践亮点、知识空白
  - `entities/AKS.md`：添加 sources 字段
- **INDEX.md 更新**：Sources 区域新增 Azure 摘要表格

---

## [2026-04-17] ingest | Aliyun 全量摄入（19 篇）

- **摄入来源**：`Aliyun/` 目录（计算/网络/存储/数据库/资源管理），共 19 篇原始文档
- **来源摘要页**：`sources/aliyun-batch-summary.md`
- **实体页增强**：
  - `entities/Aliyun.md`：补充 5 大服务子领域、安全纵深链、与 Azure 对比视角
- **INDEX.md 更新**：Sources 区域新增 Aliyun 摘要表格

---

## [2026-04-17] ingest | AI/ClaudeCode 试点摄入（7 篇）

- **摄入来源**：`AI/ClaudeCode/` 目录下 7 篇原始文档（跳过改造计划元文档）
- **来源摘要页（7 篇新建）**：
  - `sources/ClaudeCode基础指南-summary.md`
  - `sources/MCP配置-summary.md`
  - `sources/Skills-summary.md`
  - `sources/Subagents-summary.md`
  - `sources/Slash-Command-summary.md`
  - `sources/Plugin-summary.md`
  - `sources/obsidian-claude-搭建个人知识库-summary.md`
- **实体页增强（3 篇重写）**：
  - `entities/Claude-Code.md`：从文章索引升级为 7 层架构知识编译页（+sources 字段、核心架构、工作流模式、最佳实践、知识空白）
  - `entities/MCP.md`：补充 10 个 MCP 服务器详细信息、推荐组合、安装方式
  - `entities/Obsidian.md`：补充 3 种 Claude Code 集成方案、知识库架构实践
- **INDEX.md 更新**：Sources 区域从"待摄入"更新为 7 篇摘要表格
- 本次 Ingest 是 Phase 2 试点，验证完整 Ingest 流程

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
