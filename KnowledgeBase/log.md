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

## [2026-04-18] update | Claude Code Plugin 新增 shanraisshan/claude-code-best-practice

- **来源**：[shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice)（通过 DeepWiki 获取仓库信息）
- **操作**：整理简化后添加到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的"开源 Plugin 推荐"部分
- **内容**：Vibe Coding → Agentic Engineering 进阶指南，Command→Agent→Skill 三层编排模式 + RPI/Cross-Model 等工作流

---

## [2026-04-18] update | Claude Code Plugin 新增 davila7/claude-code-templates

- **来源**：[davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)（通过 DeepWiki 获取仓库信息）
- **操作**：整理简化后添加到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的"开源 Plugin 推荐"部分
- **内容**：500+ 组件的模板市场，含 7 个内置 Plugin 套件（git-workflow、supabase-toolkit、nextjs-vercel-pro 等）+ 多语言项目模板 + 附带工具

---

## [2026-04-18] update | Claude Code Skills 新增 excalidraw-diagram-generator

- **来源**：[[0raw/用这个 Skill，直接一句话生成手绘架构图，省时省力～]]（微信公众号文章，菜鸟教程）
- **操作**：整理简化后添加到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的"各种 Skill 推荐"部分
- **知识库更新**：`entities/Claude-Code.md` 覆盖描述更新

---

## [2026-04-18] update | Openclaw-多智能体 内联代码块替换为 wikilinks

- **来源**：[[AI/OpenClaw/Openclaw-多智能体]]（Raw Source，应用户明确要求修改）
- **操作**：将两个多智能体章节中的内联身份文件和 Skill 文件替换为 wikilinks
  - **"实现多智能体程序开发团队"章节**：12 个内联代码块（architect/pm/frontend-engineer/backend-engineer × AGENTS.md/IDENTITY.md/SOUL.md）→ wikilinks，节省约 13,700 字符
  - **"实现多智能体AIOps团队"章节**：12 个内联代码块（aiops/linux/container/k8s × AGENTS.md/IDENTITY.md/SOUL.md）→ wikilinks
  - **Skills开发**：4 个 Skill 子章节添加 `→ 生成的 Skill 文件：[[AI/agents/xxx/skills/yyy/SKILL.md]]` 链接
- **效果**：文档共减少约 2800 行重复内容，身份文件和 Skill 定义由 `AI/agents/` 目录统一管理

---

## [2026-04-18] ingest | OpenClaw 多智能体定义文件导出

- **来源**：`/Users/hang.xu/Downloads/agents-export-20260417-235735/`（从 [[AI/OpenClaw/Openclaw-多智能体]] 导出）
- **操作**：创建 `AI/agents/` 目录，拷入 8 个智能体完整定义文件集
  - **调度核心**：aiops（AIOps 架构师，纯路由型）
  - **基础设施层**：linux / container / k8s（三个运维执行专家）
  - **开发层**：architect / backend-engineer / frontend-engineer
  - **管理层**：pm（产品经理）
  - 每个智能体含 IDENTITY.md + SOUL.md + AGENTS.md + HEARTBEAT.md
  - 4 个附带 Skills：k8s-install-orchestrator、docker-runtime-install、k8s-cluster-install、rocky-linux10-init
- **知识库更新**：
  - 新建 `sources/openclaw-agents-export-summary.md` — 来源摘要页
  - `entities/OpenClaw.md` — 新增 sources 引用 + 智能体定义文件表格
  - `index.md` — 新增"AI/agents"分区，AI 篇数 18→26
  - `inventory/repository-inventory.md` — 新增 agents 目录盘点

---

## [2026-04-17] create | 自研 k8s-inspect-skills Skill（Shell 版）

- **来源**：基于 [[Docker-Kubernetes/k8s-monitoring-logging/K8s全面巡检脚本-生成HTML健康报告]] 的 Shell 脚本改造
- **新建目录**：`AI/skills/k8s-inspect-skills/`（含 SKILL.md + k8s_inspect.sh）
- **AI 适配改造**：
  - 新增 `--kubeconfig` / `--output-dir` 参数解析
  - 新增集群连接预检（`check_connection`）
  - 日志输出重定向到 stderr，stdout 仅输出结构化摘要 + 报告路径
  - 输出 `INSPECTION SUMMARY` 文本块供 Agent 解析
  - 修复 DaemonSet/Deployment 列格式差异（CoreDNS 误判）和事件字段位移
  - macOS/Linux 日期命令兼容
- **实测**：v1.35.3 集群（3 节点 / 43 Pod / 13 NS / 38 Warning Events）通过
- **知识库更新**：
  - `sources/k8s-report-skills-summary.md` — 扩展为合并摘要页，覆盖 Python + Shell 两个 Skill
  - `entities/Claude-Code.md` — 新增 sources 引用和覆盖列表条目
  - `index.md` — 新增 Shell 版条目，AI 篇数 17→18
  - `inventory/repository-inventory.md` — 新增 k8s-inspect-skills 目录盘点

---

## [2026-04-17] ingest | 自研 k8s-report-skills Skill（Python 版）

- **操作**：创建 `AI/skills/` 自研技能目录，从 `/Users/hang.xu/Downloads/skills/k8s-report-skills/` 拷入首个自研 Skill
- **新建目录**：`AI/skills/k8s-report-skills/`（含 SKILL.md、k8s_inspector.py、requirements.txt、templates/report.html）
- **清理**：删除 SKILL_TEMP.md（第三方 kubectl Skill 模板，与本项目无关）
- **Skill 功能**：Python kubernetes 客户端 + Jinja2 渲染 K8s 集群巡检 HTML 报告（6 大维度：集群信息/节点/Pod/Deployment/存储/事件）
- **知识库更新**：
  - 新建 `sources/k8s-report-skills-summary.md` — 来源摘要页
  - `entities/Claude-Code.md` — 新增 sources 引用和覆盖列表条目
  - `index.md` — 新增"AI/skills（自研 Skills）"分区，AI 篇数 16→17

---

## [2026-04-17] ingest | K8s 全面巡检脚本

- **来源**：`0raw/K8s 全面巡检脚本：一键生成炫酷 HTML 健康报告.md`（微信公众号文章剪藏）
- **操作**：清理网页扒取的混乱格式（转义字符、断行、HTML 残留），整理为标准 Markdown + 干净代码块
- **新建文件**：`Docker-Kubernetes/k8s-monitoring-logging/K8s全面巡检脚本-生成HTML健康报告.md`
  - 7 大巡检模块的完整 Shell 脚本（节点/Pod/资源/证书/网络/组件/事件）
  - HTML 报告模板（深色仪表盘风格）
  - CronJob 定时执行 + Dockerfile + RBAC
  - 钉钉/企微告警集成
- **知识库更新**：
  - `sources/k8s-monitoring-logging-batch-summary.md` — 新增文档摘要，文档数 20→21
  - `index.md` — 更新监控日志摘要描述

---

## [2026-04-17] update | 开源 Plugin 推荐（andrej-karpathy-skills）

- **来源**：`0raw/2.3K 小文件拿到 4 万星，它让你的 Claude Code 乖乖听话.md` + GitHub 仓库 forrestchang/andrej-karpathy-skills
- **操作**：在 `AI/ClaudeCode/Claude Code 扩展体系.md` Plugin 章节新增"开源 Plugin 推荐"
  - andrej-karpathy-skills（⭐46.5K）：4 条行为准则、3 种安装方式、效果判断标准
  - wshobson/agents：交叉引用到多智能体协作文档
- **知识库更新**：`sources/Claude-Code扩展体系-summary.md` 新增 2 条知识点 + 1 条"值得注意"

---

## [2026-04-17] update | wshobson/agents 开源 Agent 生态摄入

- **操作**：在 `AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams.md` 的"开源 Agents 推荐"章节新增 wshobson/agents 仓库完整介绍
  - 项目定位：72 个插件、112 个 Agent、146 个 Skills、16 个编排器
  - 全部 Agent 分类表（10 大类、112 个 Agent 含模型分配和一行描述）
  - 安装方式和模型分配策略
- **知识库更新**：
  - `sources/多智能体协作-summary.md` — 新增开源 Agent 生态知识点（4 条）
  - `entities/Claude-Code.md` — 更新覆盖列表，标注 wshobson/agents 内容

---

## [2026-04-17] restructure | Claude Code 扩展体系文章合并

- **操作**：将 4 篇独立文章合并为 1 篇 `AI/ClaudeCode/Claude Code 扩展体系.md`
  - 合并来源：`MCP.md`、`Skills.md`、`Slash Command.md`、`Plugin.md`（已删除）
  - 按四层架构重新组织：MCP（外部工具）→ Skills（自动能力包）→ Slash Commands（手动工作流）→ Plugin（打包分发）
  - 新增总览对比表和"一句话总结"帮助快速理解四层定位
- **知识库更新**：
  - 来源摘要页：4 篇旧摘要合并为 `sources/Claude-Code扩展体系-summary.md`（已删除旧文件）
  - 实体页：`entities/Claude-Code.md`、`entities/MCP.md` — 更新 sources 字段和覆盖列表
  - 地图：`maps/claude-code-openclaw-map.md` — 更新知识体系树和共同概念表
  - INDEX.md — 更新来源摘要表格和推荐阅读路径

---

## [2026-04-17] restructure | Subagents + Agent Teams 合并为一篇

- **操作**：将 `AI/ClaudeCode/Subagents.md` 和 `AI/ClaudeCode/Agent Teams.md` 合并为 `AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams.md`
- **删除文件**：`Subagents.md`、`Agent Teams.md`、`sources/Subagents-summary.md`、`sources/AgentTeams-summary.md`
- **新建文件**：`sources/多智能体协作-summary.md`（合并后的摘要页）
- **引用更新**：`entities/Claude-Code.md`、`INDEX.md`、`maps/tool-map.md`、`maps/ai-workflow-map.md`、`maps/claude-code-openclaw-map.md`、`inventory/repository-inventory.md` 中的所有链接已更新

---

## [2026-04-17] ingest | Agent Teams 文档摄入

- **摄入来源**：`AI/ClaudeCode/Agent Teams.md`（基于官方文档 https://code.claude.com/docs/en/agent-teams 撰写的中文使用指南）
- **来源摘要页**：`sources/AgentTeams-summary.md`
- **实体页增强**：`entities/Claude-Code.md` — 新增 5.5 Agent Teams 层级（与 SubAgents 对比表、核心组件说明），更新 sources 字段和覆盖列表，消除"多人协作"知识空白
- **INDEX.md 更新**：AI/ClaudeCode Sources 表格新增 Agent Teams 行

---

## [2026-04-17] restructure | INDEX.md 链接格式改造（wikilink → markdown link）

- **目的**：让 INDEX.md 在 GitHub 上也能点击跳转，同时 Obsidian 中保持可用
- **方案**：仅改造 INDEX.md（导航门面页），其他 wiki 内部页面保持 `[[wikilink]]` 不变
- **改动**：将 INDEX.md 中所有 `[[wikilink|显示名]]` 转换为 `[显示名](relative-path.md)` 格式
  - KnowledgeBase 内部链接使用相对路径：`entities/Docker.md`、`concepts/CICD.md`
  - 原始来源链接使用上级目录：`../AI/ClaudeCode/ClaudeCode基础指南.md`
- **影响范围**：仅 INDEX.md 一个文件，其他 70+ 个 wiki 页面不受影响

---

## [2026-04-17] create | 批量补建高频红链 stub 实体页（11 个）

- **触发**：用户请求补建引用 ≥3 次的实体红链
- **新建 stub 实体页（11 篇）**：
  - `entities/NVIDIA.md`（4 次引用）— GPU 硬件厂商
  - `entities/PBS.md`（4 次引用）— HPC 作业调度系统
  - `entities/containerd.md`（4 次引用）— K8s 默认容器运行时
  - `entities/CUDA.md`（3 次引用）— NVIDIA GPU 计算平台
  - `entities/Calico.md`（3 次引用）— K8s CNI 网络插件
  - `entities/Docker-Compose.md`（3 次引用）— 单机多容器编排工具
  - `entities/Kustomize.md`（3 次引用）— K8s 原生配置管理工具
  - `entities/NFS.md`（3 次引用）— 网络文件系统存储
  - `entities/Nginx.md`（3 次引用）— Web 服务器与反向代理
  - `entities/PostgreSQL.md`（3 次引用）— 开源关系型数据库
  - `entities/Rancher.md`（3 次引用）— K8s 多集群管理平台
- **INDEX.md 更新**：实体表格新增 11 行
- **断链报告更新**：红链从 236 降至 225，有效链接从 370 升至 381（63%）
- 累计实体页：35 个（18 原始 + 6 首次 lint stub + 11 本次 stub）

---

## [2026-04-17] lint | 首次全库健康检查

### 检查结果

| 检查项 | 结果 |
|--------|------|
| 总 wikilink 数 | 609 个唯一目标 |
| 有效链接 | 370 个（61%） |
| 孤儿页面 | 0 个 ✅ |
| 错误分类链接 | 5 个 → 已修复 ✅ |
| 缺失 concepts/ 页面 | 69 个（红链） |
| 缺失 entities/ 页面 | 167 个（红链） |
| 原始来源断链 | 0 个 ✅ |

### 修复操作

1. **修复 5 个错误分类链接**：ArgoCD/Helm/Ingress/Istio/Kubernetes 从 `concepts/` 改为 `entities/`
   - `maintenance/naming-normalization.md`（4 处）
   - `sources/k8s-networking-service-mesh-batch-summary.md`（1 处）

2. **创建 6 个高频引用的 stub 实体页**（引用 ≥5 次）：
   - `entities/Harbor.md`（8 次引用）
   - `entities/Redis.md`（6 次引用）
   - `entities/GitLab.md`（5 次引用）
   - `entities/Kafka.md`（5 次引用）
   - `entities/Loki.md`（5 次引用）
   - `entities/MySQL.md`（5 次引用）

### 剩余红链说明

236 个红链（引用了尚未创建独立页面的概念/实体）属于正常现象：
- 批量摘要中对工具和概念的引用超出了当前实体页覆盖范围
- Obsidian 原生支持红链，可在后续 Ingest 中按需创建页面
- 建议：引用 ≥3 次的概念/实体在后续维护中逐步补建页面

---

## [2026-04-17] ingest | 全库剩余领域摄入（103 篇）

- **摄入来源**：Python(27) + Linux-Shell(24) + AI-OpenClaw(9) + Go(9) + HPC(7) + CloudComputing(7) + GPU-DeepLearning(4) + Database(3) + Middlewares(3) + OS(3) + Networking(2) + IaC(2) + Git(2) + C++(1) + SoftwareTesting(2)
- **来源摘要页（6 篇新建）**：
  - `sources/python-batch-summary.md`（27 篇）
  - `sources/linux-shell-batch-summary.md`（24 篇）
  - `sources/ai-openclaw-misc-batch-summary.md`（9 篇：OpenClaw + Copilot + 提示词）
  - `sources/go-batch-summary.md`（9 篇）
  - `sources/hpc-cloud-gpu-batch-summary.md`（18 篇：HPC + CloudComputing + GPU）
  - `sources/misc-domains-batch-summary.md`（18 篇：Database/Middlewares/OS/Networking/IaC/Git/C++/SoftwareTesting）
- **实体页增强（3 篇）**：
  - `entities/OpenClaw.md`：补充 Skills 生态、Channels、AIOps、多智能体、CoPaw 对比
  - `entities/Terraform.md`：补充三阶段工作流、核心文件结构、ARM Template 对比
  - `entities/Slurm.md`：补充集群架构、4 种安装方式、GPU GRES 调度、Prometheus 监控集成
- **INDEX.md 更新**：Sources 区域新增 6 个领域摘要表格，标记"全部领域已摄入完成"
- 🎉 **里程碑**：全库 17 个领域、~350 篇原始文档已全部摄入 wiki 编译层

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
