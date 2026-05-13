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

## [2026-05-13] ingest | Hermes Curator — Skill 膨胀治理

- **来源**：AI技术立文，2026-05-07，微信公众号
- **清洗**：去除作者署名行、SVG 占位图片（2 张）、页脚营销（赞赏/滑动导航）
- **新建文件**：
  - `AI/Hermes-agent/Hermes-Curator-Skill膨胀治理.md` — 清洗后技术文章
- **更新页面**：
  - `sources/hermes-agent-batch-summary.md`：frontmatter 新增 source、文档数 3→4、正文新增 Curator 小节
  - `entities/Hermes-Agent.md`：新增 Curator 核心功能条目、sources 引用、覆盖条目；移除"Skill Factory 质量评估"知识空白（已覆盖）
  - `maps/ai-workflow-map.md`：Hermes 路径 3→4 步、来源摘要 3→4 篇
  - `index.md`：Hermes-agent 批量摘要 3→4 篇
- **核心知识**：Curator 四步工作流（监测/降级/复盘/锁定）、Skill 膨胀数学（365→36 条/年）、Skill vs 记忆区别、Agent 四种记忆类型（工作/语义/情景/程序性）

---

## [2026-05-13] ingest | K8s CGroup v2 深度解析：资源隔离原理、迁移实战与避坑指南

- **来源**：WAKEUP技术，2026-05-12，微信公众号
- **清洗**：去除作者署名行、页脚营销（关注/赞赏/滑动导航）、列表序号冗余格式
- **新建文件**：
  - `Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南.md` — 清洗后技术文章
  - `KnowledgeBase/sources/k8s-cgroup-v2-summary.md` — 来源摘要页
- **更新页面**：
  - `sources/k8s-installation-management-batch-summary.md`：frontmatter 新增 source、文档数 16→17、正文新增 cgroup v2 小节
  - `entities/Kubernetes.md`：新增 cgroup v2 资源隔离章节、sources 引用、篇数 145→147
  - `entities/containerd.md`：新增核心功能章节（含 cgroup v2 支持说明）、覆盖条目
  - `maps/kubernetes-map.md`：总篇数 146→147、安装运维 16→17 篇、列表新增 cgroup v2
  - `index.md`：安装管理批量摘要 16→17、Kubernetes 实体 146→147、领域导航 146→147
- **核心知识**：cgroup v2 统一层次树、CPU Burst（P99 降 30-50%）、memory.high 双层限制、MemoryQoS（v1.27 Beta）、5 个生产踩坑案例、3 条 Prometheus 告警规则

---

## [2026-05-13] ingest | AI 行业动态：AI 时代 Git 版本管理最佳实践

- **来源**：TRAE 技术专家 小夏，2026-04-28
- **清洗**：去除公众号引流、页脚导航；修复全部代码块格式（错误的语言标识符 xml/sql/kotlin/perl/css/makefile/apache/python/nginx/cs/php → text/bash/markdown/json；恢复代码块内换行）
- **新建文件**：
  - `AI/行业动态/AI时代的Git版本管理最佳实践.md` — 清洗后技术文章
  - `KnowledgeBase/sources/ai-git-best-practices-summary.md` — 来源摘要页
- **更新页面**：
  - `maps/ai-workflow-map.md`：行业动态 2→3 篇
  - `index.md`：行业动态表格新增一行
  - `AI/index.md`：行业动态/ 2→3 篇

---

## [2026-05-13] ingest | AI 行业动态：HTML 取代 Markdown

- **来源**：量子位 QbitAI（Jay），2026-05-12，Anthropic 工程师 Thariq 长文 + Karpathy 回应
- **清洗**：去除公众号引流、广告、AIGC 峰会推广、评论区引导、页脚导航
- **新建文件**：
  - `AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议.md` — 清洗后技术文章
  - `KnowledgeBase/sources/html-vs-markdown-summary.md` — 来源摘要页
- **更新页面**：
  - `maps/ai-workflow-map.md`：行业动态 1→2 篇，推荐阅读顺序新增条目
  - `index.md`：行业动态表格新增一行
  - `AI/index.md`：行业动态/ 1→2 篇

---

## [2026-05-11] restructure | Hermes Agent 两篇合并 + KB 同步

- **操作**：将 `Hermes Agent 资源合集` 与 `Hermes满配指南-五大配置模块` 合并为一篇
- **新建文件**：
  - `AI/Hermes-agent/Hermes-Agent-满配指南与生态资源.md` — 合并后文章（八大章节：配置总览 + 五大模块 + 高阶玩法 + 工具增强 + 生态资源）
- **删除文件**：
  - `AI/Hermes-agent/Hermes Agent 资源合集.md`
  - `AI/Hermes-agent/Hermes满配指南-五大配置模块.md`
  - `KnowledgeBase/sources/hermes-config-summary.md`（孤儿摘要页，内容已吸收入 batch summary）
- **更新页面**：
  - `sources/hermes-agent-batch-summary.md`：资源合集条目替换为合并文章，新增五大配置模块要点
  - `entities/Hermes-Agent.md`：sources 4→3、覆盖条目 4→3
  - `maps/ai-workflow-map.md`：Hermes 路径 4 条→3 条
  - `inventory/repository-inventory.md`：Hermes-agent/ 4 篇→3 篇
  - `INDEX.md`：删除 hermes-config-summary 行，更新 batch summary 描述
  - `AI/index.md`：Hermes-agent/ 4→3 篇
  - `AI/HarnessKit.md`：修复因删除产生的断链（资源合集→满配指南与生态资源）

---

## [2026-05-09] ingest | Claude Code+Obsidian 知识管家实践

- **来源**：微信公众号"强西"，2026-05-06 发布
- **清洗**：去除作者署名行、3 个 SVG 占位图片、页脚营销（微信扫一扫赞赏、继续滑动看下一个），保留全部技术内容
- **新建文件**：
  - `AI/Obsidian/obsidian-claude-code-AI知识管家.md` — 清洗后的原始来源文档
  - `KnowledgeBase/sources/obsidian-claude-code-AI知识管家-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Obsidian.md`：frontmatter 新增 source、覆盖条目新增知识管家文章
  - `entities/Claude-Code.md`：frontmatter 新增 source、覆盖条目新增知识管家文章
  - `maps/ai-workflow-map.md`：总篇数 19→20、Obsidian 节 3→4 篇、新增推荐阅读条目和来源摘要引用
  - `INDEX.md`：新增来源摘要条目、AI 领域篇数 119→120
  - `inventory/repository-inventory.md`：总文档数 298→299、AI 27→28 篇、Obsidian/ 3→4 篇
- **核心知识**：Markdown 是 LLM 母语（Token 效率优 30-50%）、三大 $1B+ 项目殊途同归于 .md（Manus/OpenClaw/Claude Code）、30 分钟四步上手、Karpathy Wiki 模式、自动 backlinks 进阶方向

---

## [2026-05-08] ingest | Helm 部署 RabbitMQ HA

- **来源**：微信公众号"爱踢人生sre"
- **清洗**：去除公众号作者名片、SVG 占位图片、页脚导航（"继续滑动看下一个"）、"微信扫一扫赞赏作者"，保留全部技术内容
- **新建文件**：
  - `Docker-Kubernetes/k8s-db-middleware/helm部署rabbitmq-ha.md` — 清洗后的原始来源文档
  - `KnowledgeBase/sources/rabbitmq-ha-summary.md` — 来源摘要页
- **更新页面**：
  - `sources/k8s-db-middleware-UI-batch-summary.md`：frontmatter 新增 source、文档数 18→19（中间件 10→11）、正文新增 RabbitMQ HA 小节
  - `maps/kubernetes-map.md`：总篇数 145→146、中间件 10→11、列表新增 RabbitMQ HA
  - `INDEX.md`：K8s 中间件批量摘要 18→19、Kubernetes 实体 145→146、领域导航 145→146
  - `inventory/repository-inventory.md`：总文档数 297→298、Docker-Kubernetes 145→146、k8s-db-middleware/ 10→11
- **备注**：aliyun/rabbitmq-ha Chart 版本较旧（1.0.0，RabbitMQ 3.7），需手动修复 API 版本兼容性，生产环境建议评估 bitnami/rabbitmq

---

## [2026-05-07] ingest | Kyverno 1.18 新特性 + Kyverno 实体页

- **来源**：CNCF 官方博客，微信公众号转载
- **清洗**：去除微信公众号图片横幅、KubeCon 广告区块、CNCF 基金会介绍模板、页脚导航（"继续滑动看下一个"），保留全部技术内容与参考链接
- **操作方式**：清洗后的 1.18 新特性内容追加到已有文档 `helm部署kyverno和policy-reporter.md` 末尾，未新增独立文件
- **新建文件**：
  - `KnowledgeBase/sources/kyverno-1.18-summary.md` — 来源摘要页
  - `KnowledgeBase/entities/Kyverno.md` — Kyverno 实体页（新建，CNCF 毕业项目）
- **更新页面**：
  - `Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter.md`：追加 Kyverno 1.18 全部新特性内容
  - `sources/k8s-security-auth-batch-summary.md`：Kyverno 小节新增 1.18 要点
  - `maps/kubernetes-map.md`：安全认证条目标注"含 1.18 新特性"
  - `INDEX.md`：实体表新增 Kyverno，安全认证条目标注含 1.18
  - `inventory/repository-inventory.md`：无文件数变更

---

## [2026-05-06] ingest | Boris Cherny 红杉大会七个判断 + AI 行业动态目录

- **来源**：微信公众号文章（原始视频 https://www.youtube.com/watch?v=SlGRN8jh2RI）
- **清洗**：去除作者署名行、#01 章节标记、AI Maker Summit 广告（419元报名）、SVG 占位图、微信页脚导航，保留全部 7 个行业判断及分析
- **新建目录**：`AI/行业动态/` — AI 行业趋势与洞察专题目录
- **新建文件**：
  - `AI/行业动态/Claude-Code创始人红杉大会七个判断.md` — 清洗后的文章
  - `KnowledgeBase/sources/boris-cherny-sequoia-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Claude-Code.md`：新增 sources 引用 + 覆盖条目（行业判断 + 摘要）
  - `entities/MCP.md`：新增 sources 引用 + 覆盖条目 + 新增"行业观点"章节（Boris Cherny 的 MCP 定位论述）
  - `maps/ai-workflow-map.md`：新增"AI 行业动态"阅读路径 + 文档表（1 篇）+ 总数 18→19
  - `INDEX.md`：新增"AI/行业动态"来源摘要分区 + AI 领域篇数 118→119
  - `inventory/repository-inventory.md`：新增行业动态/ 子节（1 篇）+ AI 总数 26→27

---

## [2026-05-05] ingest | Harness 实战文章摄入

- **来源**：`0raw/Harness 实战：从零搭建最小可用的 Harness 系统.md`（微信公众号剪藏）
- **清洗**：去除作者署名行、微信赞赏/滑动导航、SVG 占位图，保留全部技术内容（四层架构、三个拦截器完整代码、编排流程、踩坑经验、组件清单表）
- **新建文件**：
  - `AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/harness-system-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Claude-Code.md`：新增 sources 引用 + 覆盖条目 + 标记 Hooks 知识空白已填补
  - `maps/ai-workflow-map.md`：Claude Code 路径新增第 5 步 + 文档表 4→5 篇 + 总数 17→18
  - `maps/tool-map.md`：Claude Code 相关文档 6→7 篇
  - `INDEX.md`：新增来源摘要条目
  - `inventory/repository-inventory.md`：ClaudeCode/ 4→5 篇

---

## [2026-05-05] ingest | Skill Craft 质检工具文章摄入

- **来源**：`0raw/我做了一个 Claude Skill 质检工具：专门解决 Claude Skill 的不触发、乱触发、越用越跑偏.md`（微信公众号剪藏）
- **清洗**：去除营销文案（01 节引入语、10 节目标受众推荐、11 节关注引导、页脚），保留技术内容（7 类失效模式、三层评估体系、四模式详解）
- **新建文件**：
  - `AI/ClaudeCode/Claude-Skill质检工具-SkillCraft.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/skill-craft-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Claude-Code.md`：新增 sources 引用 + 覆盖条目
  - `maps/ai-workflow-map.md`：Claude Code 路径新增第 4 步 + 文档表 3→4 篇
  - `maps/tool-map.md`：Claude Code 相关文档 5→6 篇
  - `INDEX.md`：新增来源摘要条目
  - `inventory/repository-inventory.md`：ClaudeCode/ 3→4 篇

---

## [2026-05-05] update | CLAUDE.md 新增原始文章清洗准则

- 在操作流程 Ingest 节新增 Step 0："清洗原始文章"——去除营销内容，仅保留技术内容
- 明确列出需要去除的内容类型：引流话术、关注/转发引导、评论区互动、广告/赞助、页脚导航

---

## [2026-05-05] ingest | Hermes 满配指南文章摄入

- **来源**：`0raw/装完 Hermes 一定要配置这五套系统，秒变满配版，能力提升数倍不止.md`（微信公众号剪藏）
- **清洗**：去除营销文案，保留五大配置模块技术内容及安装命令
- **新建文件**：
  - `AI/Hermes-agent/Hermes满配指南-五大配置模块.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/hermes-config-summary.md` — 来源摘要页
  - `KnowledgeBase/entities/Hermes-Agent.md` — 新建实体页（4 篇文档达到 ≥3 阈值）
- **更新页面**：
  - `sources/hermes-agent-batch-summary.md`：更新实体引用（去掉"无独立实体页"备注）
  - `maps/ai-workflow-map.md`：新增 Hermes Agent 路径（4 篇）+ 相关工具列表
  - `INDEX.md`：新增实体条目 + 来源摘要条目
  - `inventory/repository-inventory.md`：新增 Hermes-agent/ 子节（4 篇）

---

## [2026-05-05] ingest | Obsidian 可视化 Skills 文章摄入

- **来源**：`0raw/这个 Skills 让 Obsidian 画图门槛降到了零.md`（微信公众号剪藏）
- **清洗**：去除营销内容（作者介绍、关注提示、往期推荐、赞赏等），保留技术内容
- **新建文件**：
  - `AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas.md` — 清洗后的技术文章
  - `KnowledgeBase/sources/obsidian-visual-skills-summary.md` — 来源摘要页
- **更新页面**：
  - `entities/Obsidian.md`：新增覆盖条目
  - `maps/ai-workflow-map.md`：Obsidian 区块 2→3 篇
  - `maps/tool-map.md`：Obsidian 区块新增文档
  - `INDEX.md`：新增来源摘要条目
  - `inventory/repository-inventory.md`：Obsidian/ 篇数 2→3

---

## [2026-05-05] restructure | Obsidian 知识库文章从 ClaudeCode 目录迁移到独立目录

- **操作**：将 `AI/ClaudeCode/` 中 2 篇 Obsidian 知识库主题文章迁移到新建的 `AI/Obsidian/` 目录
  - `obsidian-claude-搭建个人知识库.md` → `AI/Obsidian/`
  - `karpathy-llm-wiki-改造计划.md` → `AI/Obsidian/`
- **引用修复**：更新 9 个 KB 文件中的 wikilink 路径（entities/Claude-Code、entities/Obsidian、entities/MCP、maps/tool-map、maps/ai-workflow-map、maps/claude-code-openclaw-map、INDEX、inventory/repository-inventory、sources/obsidian-claude-搭建个人知识库-summary）
- **结构调整**：
  - `ai-workflow-map.md`：Claude Code 篇数 5→3，新增 Obsidian 知识库区块（2 篇）
  - `claude-code-openclaw-map.md`：更新目录树和文档计数
  - `repository-inventory.md`：ClaudeCode 篇数 5→3，新增 Obsidian/ 子节（2 篇）
- **目的**：使目录结构更清晰——ClaudeCode/ 保留纯 Claude Code 文章，Obsidian/ 独立存放知识库主题文章

---

## [2026-05-04] ingest | Hermes Agent 架构解析文章

- **来源**：`0raw/Hermes Agent全解析：与OpenClaw对比及飞书接入指南 - 飞书官网.md`
- **操作**：
  - 清理格式后放置到 `AI/Hermes-agent/Hermes Agent全解析-与OpenClaw对比及飞书接入指南.md`
  - 更新 `sources/hermes-agent-batch-summary.md`：文档数 2→3，新增第三篇摘要（五层架构、记忆系统、子代理委托、OpenClaw 六维对比、飞书接入）
  - 更新 `entities/OpenClaw.md`：新增"与 Hermes Agent 的对比"章节
  - 更新 `index.md`：Hermes-agent 覆盖文档数 2→3
- **新增知识点**：Hermes 五层架构、冻结快照记忆、子代理深度限制 2 / 并行 max 3、Hermes vs OpenClaw 六维对比

---

## [2026-05-04] update | 消除孤儿来源页面

- **操作**：为 15 个无入站链接的 sources/ 页面添加来自 entities/concepts/maps 的引用
- **修改文件**：
  - `entities/Claude-Code.md` — +3 refs（基础指南、扩展体系、知识库搭建摘要）
  - `entities/OpenClaw.md` — +2 refs（OpenClaw 批量摘要、多智能体导出摘要）
  - `entities/Terraform.md` — +1 ref（容器管理摘要）
  - `entities/Helm.md` — +1 ref（Terraform Helm Provider）
  - `entities/Slurm.md` — +1 ref（HPC-Cloud-GPU 摘要）
  - `concepts/Python运维开发.md` — +1 ref（Python 批量摘要）
  - `entities/Kafka.md`、`entities/Redis.md`、`entities/MySQL.md` — 各 +1 ref（杂项领域摘要）
  - `maps/linux-ops-map.md` — +2 refs（Linux-Shell、HPC-Cloud-GPU 摘要）
  - `maps/ai-workflow-map.md` — +4 refs（CloudOps-Agent、RAG-Agent、Hermes-agent、k8s-report-skills 摘要）
  - `maps/domain-map.md` — +3 refs（Go、杂项领域、IaC 摘要）
- **影响**：孤儿来源页面从 15 个减少到 0 个

---

## [2026-05-04] update | 修复链接格式问题

- **操作**：修复 Docker Compose 命名不一致（空格 → 连字符）
- **修改文件**：
  - `entities/Docker.md` — 2 处 `Docker Compose` → `Docker-Compose`
  - `sources/docker-batch-summary.md` — 1 处同上
- **说明**：`\|` 在表格内的 wikilink 是正确的 Markdown 转义，非错误，无需修复

---

## [2026-05-04] create | 补建高频缺失概念页面

- **操作**：创建 7 个被多页面引用但不存在的概念页面
- **新增概念页**：
  - [[KnowledgeBase/concepts/StorageClass]] — K8s 动态存储分配（4 处引用）
  - [[KnowledgeBase/concepts/ServiceMesh]] — 服务网格别名页，指向 [[KnowledgeBase/concepts/服务网格]]（3 处引用）
  - [[KnowledgeBase/concepts/高可用架构]] — HA 冗余与故障切换（3 处引用）
  - [[KnowledgeBase/concepts/CRD]] — K8s 自定义资源定义（2 处引用）
  - [[KnowledgeBase/concepts/Operator模式]] — CRD + Controller 模式（2 处引用）
  - [[KnowledgeBase/concepts/RBAC]] — 基于角色的访问控制（2 处引用）
  - [[KnowledgeBase/concepts/联邦集群]] — 多集群联邦管理（2 处引用）
- **更新页面**：[[KnowledgeBase/index|index.md]] — 概念页表格新增 7 行
- **影响**：消除 16 处断链引用

---

## [2026-05-04] ingest | AI 新项目 + IaC Terraform 容器管理

- **操作**：批量摄入 4 个新来源项目到 wiki 编译层
- **新增来源摘要页**：
  - [[KnowledgeBase/sources/cloudops-agent-batch-summary|CloudOps-Agent 批量摘要]] — 57 篇，AI/CloudOps-Agent-项目，三语言智能 OnCall Agent
  - [[KnowledgeBase/sources/rag-agent-batch-summary|RAG-Agent 批量摘要]] — 33 篇，AI/RAG-Agent，Spring Boot + ES 混合检索企业 RAG 系统
  - [[KnowledgeBase/sources/hermes-agent-batch-summary|Hermes-agent 批量摘要]] — 2 篇，AI/Hermes-agent，Hermes Agent 安装与资源合集
  - [[KnowledgeBase/sources/iac-terraform-container-summary|Terraform 容器管理摘要]] — 1 篇，IaC/terraform-container-management
- **更新页面**：
  - [[KnowledgeBase/index|index.md]] — 新增 4 个来源分组，AI 领域篇数 26→118，IaC 领域 2→3
- **影响范围**：AI 领域覆盖率从 12% 提升至 ~90%，IaC 领域新增 Terraform 容器管理专题

---

## [2026-04-23] ingest | External Secrets Operator 进阶

- **来源**：[[0raw/K8S实战教程 如何使用 External Secrets Operator 管理 Kubernetes密钥]]（微信公众号文章）
- **操作**：整合到现有文档 [[Docker-Kubernetes/k8s-security-auth/helm部署external-secrets]]
- **新增内容**：
  - "为什么需要 ESO" 对比表 + 工作原理架构说明 + 核心 CRD 对照表
  - AWS Secrets Manager 集成（第三个 Provider，补充 Azure KV 和 Vault）
  - 进阶用法：精细字段映射、模板渲染、creationPolicy 策略、GitOps 集成
  - 监控与可观测性（Prometheus Metrics、告警）
  - 五方案横向对比（原生 Secret / Sealed Secrets / SOPS / CSI / ESO）
  - 生产落地六步路线
- **决策**：已有 external-secrets 部署文章覆盖 Azure KV + Vault，新文章补充架构原理和进阶特性，合并避免内容分裂

---

## [2026-04-23] ingest | kubelogin OIDC 认证

- **来源**：[[0raw/K8S工具推荐：告别复杂认证！Kubernetes登录神器kubelogin指南]]（微信公众号文章）
- **操作**：整合到现有文档 [[Docker-Kubernetes/k8s-installation-management/k8s多集群kubeconfig管理]]，新增"OIDC 认证：kubelogin"章节
- **新增内容**：
  - kubelogin 核心特性（浏览器登录、短期令牌、自动刷新、加密存储）
  - 安装方式（brew / choco / krew）
  - kubeconfig exec 模式配置示例
  - 适用场景（企业 SSO、多团队共享、合规审计）
- **决策**：原文内容较轻，不足以独立成文，整合到已有 kubeconfig 管理文章中更自然

---

## [2026-04-23] ingest | Client-Go K8s 客户端开发

- **来源**：[[0raw/初始K8S客户端工具Client-Go]]（微信公众号文章）
- **操作**：创建 [[Go/client-go-K8s客户端开发]] 新文章
- **新增内容**：
  - client-go 简介、用途、核心功能
  - 客户端初始化（集群内外双模式）
  - CRUD 完整代码示例（Create / Update 冲突重试 / List / Delete 三种策略）
  - Client-Go + Gin 实战：Web API + 模板渲染控制台

---

## [2026-04-23] ingest | ACK 网络规划与成本优化

- **来源**：[[0raw/踩过网段坑才懂：K8s 网络规划与成本优化的底层逻辑]]（微信公众号文章）
- **操作**：创建 [[Aliyun/网络/ACK网络规划与成本优化]] 新文章
- **新增内容**：
  - 网段规划与成本关系（IP 不足→集群重建、CIDR 重叠→跨 AZ 费用、路由膨胀）
  - CIDR 设计最佳实践（分区分段、Pod 大 Service 小、不与 VPC 重叠、多集群留空间）
  - ACK 流量成本优化（单 AZ 优先、控制公网、SLB 精打细算）
  - 网络插件选型：Flannel vs Terway
- **关联更新**：[[KnowledgeBase/entities/Aliyun]] 网络章节补充 ACK 网络规划，知识空白标记更新为"部分填补"

---

## [2026-04-23] ingest | K8s 部署防火墙端口配置

- **来源**：[[0raw/部署K8S时关闭防火墙被吐槽了，我连夜整理全部需要开放的端口]]（微信公众号文章）
- **操作**：创建 [[Docker-Kubernetes/k8s-installation-management/k8s部署防火墙端口配置]] 新文章
- **新增内容**：
  - 生产环境正确做法：保留 firewalld + 精准开放端口（而非关闭防火墙）
  - 各组件端口详解：kubeadm 核心、kubelet、kube-proxy、Calico、Ingress
  - Master / Worker 节点分别的 firewalld 配置命令
  - 端口速查总结表（组件 × Master/Worker × 是否必需）

---

## [2026-04-23] ingest | K8s 1.35 EnvFiles（fileKeyRef）

- **来源**：[[0raw/k8s 1.35 版本 Pod环境变量配置]]（微信公众号文章）
- **操作**：将 K8s 1.35 新特性 EnvFiles 整合到现有文档 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-configMap-Secret]]
- **新增内容**：
  - K8s 1.35 `fileKeyRef` 机制：从 emptyDir 卷文件加载环境变量，主容器无需挂载
  - initContainer 生成配置 → kubelet 启动时注入的工作流
  - 5 种环境变量注入方式对比表
  - 环境变量管理规范（分层管理、命名规范、默认值、文档化）

---

## [2026-04-23] ingest | FinOps 云成本优化实战

- **来源**：[[0raw/老杨的压箱底的技能聊聊FinOps]]（微信公众号文章）
- **操作**：创建 [[Aliyun/资源管理/FinOps-云成本优化实战]] 新文章
- **新增内容**：
  - FinOps 方法论（量化→优化→固化）
  - 多云账单 CLI（阿里云 BSS OpenAPI / 腾讯云 tccli / 华为云 BSS v2）
  - 4 类浪费场景（低 CPU / 闲置 EIP / 存储无生命周期 / K8s 过配）
  - 4 个即时优化动作（夜间关机、降配、冷热分层、包年包月）
  - 预算告警 + Prometheus 账单看板 + Infracost PR 级成本评估
  - 实战案例：三步 30% 降本
- **关联更新**：[[KnowledgeBase/entities/Aliyun]] 资源管理章节补充 FinOps，知识空白标记已填补

---

## [2026-04-23] restructure | AI-视觉目录：提示词抽离 + awesome-design-md 归集

- **操作**：
  1. 从 [[AI/提示词]] 抽离"作图"、"PPT"、"Claude Design 系统提示词"三个视觉设计章节，合并为 [[AI/AI-视觉/视觉设计提示词]]
  2. 将 `AI/awesome-design-md/`（67 个品牌 DESIGN.md）整体移入 `AI/AI-视觉/awesome-design-md/`
  3. 原 提示词.md 中保留交叉引用指向新文件
  4. 修复所有 wikilink 引用（README.md 中 67 个品牌链接 + log.md）
- **AI-视觉 目录当前内容**：
  - `AI做PPT-ppt-master.md` — SVG → PPTX 原生生成
  - `AI-Animation-Skill-科普动画.md` — 44 个 HTML 科普动画模板
  - `html-ppt-skill-实测指南.md` — HTML 幻灯片生成系统
  - `视觉设计提示词.md` — 作图/PPT/Claude Design 系统提示词
  - `awesome-design-md/` — 67 个品牌 DESIGN.md 前端设计系统

---

## [2026-04-23] restructure + create | AI-视觉目录整合 + html-ppt-skill

- **来源**：[[0raw/一句话生成PPT，已经能用了：html-ppt-skill实测指南]]（微信公众号文章）
- **操作**：
  1. 创建 `AI/AI-视觉/` 目录，将 PPT/HTML 视觉生成类文章归集
  2. 移动 [[AI/AI-视觉/AI做PPT-ppt-master]] 和 [[AI/AI-视觉/AI-Animation-Skill-科普动画]] 至新目录
  3. 创建 [[AI/AI-视觉/html-ppt-skill-实测指南]] 新文章
  4. 修复所有跨文件 wikilink 引用（OpenClaw 实体、log.md、文章间交叉引用）
- **新增内容**：
  - html-ppt-skill：36 主题 + 31 布局 + 14 deck + 47 动画的 HTML 幻灯片生成系统
  - 3 组实测场景（技术分享 cyberpunk / 融资路演 / 小红书图文）
  - 三款工具（PPT Master / AI-Animation-Skill / html-ppt-skill）横向定位对比

---

## [2026-04-23] create | AI-Animation-Skill HTML 科普动画生成

- **来源**：[[0raw/扔掉PPT，用这44个HTML动画模板，让AI帮你做科普视频]]（微信公众号文章）
- **操作**：创建 [[AI/AI-视觉/AI-Animation-Skill-科普动画]] 新文章
- **新增内容**：
  - 项目简介：单 HTML 文件输出、零依赖、完全离线
  - 与 Gamma / Beautiful.ai 对比表
  - 44 个模板详解（26 PPT Level2 + 4 基础 + 14 流程图动画）
  - 安装使用流程（OpenClaw / WorkBuddy / QClaw）
  - 与 PPT Master 的定位对比
- **关联更新**：[[KnowledgeBase/entities/OpenClaw]] Skills 插件生态补充 AI-Animation-Skill 条目

---

## [2026-04-23] update | Skill 质量治理：7 类失效模式与 Skill Craft

- **来源**：[[0raw/我做了一个 Claude Skill 质检工具：专门解决 Claude Skill 的不触发、乱触发、越用越跑偏]]（微信公众号文章）
- **操作**：将 Skill 失效模式分析和 Skill Craft 工具整合到 [[AI/ClaudeCode/Claude Code 扩展体系]] 的 Skills 章节
- **新增内容**：
  - 7 类系统性失效模式（约束衰减、工具漂移、输出膨胀、依赖链断裂、并行孤岛、触发模糊、幻觉填充）
  - Skill Craft 质检工具 4 种模式（check/fix/create/audit）
  - 3 层评估体系（8 结构模块 + 7 反模式 + 3 完整性原则）
  - fix 模式的 4 类关联检查机制
- **关联更新**：[[KnowledgeBase/entities/Claude-Code]] Skills 章节补充质量治理说明

---

## [2026-04-23] update | Obsidian 微信公众号发布插件

- **来源**：[[0raw/告别公众号排版烦恼：Obsidian一键发布插件使用指南]]（微信公众号文章）
- **操作**：将插件功能、安装配置、使用方法整合到 [[KnowledgeBase/entities/Obsidian]] 的"实用社区插件"章节
- **新增内容**：
  - Wechat Public Platform 插件介绍（作者 ai-chen2050）
  - 7 项核心功能表（上传素材、添加草稿、发布文章、群发消息、下载素材、百家号分发、数据统计）
  - 安装与配置步骤（AppID / AppSecret / IP 白名单）
  - Frontmatter 发布参数示例（封面图三级优先级）
  - 权限说明（个人订阅号 vs 认证公众号）
- **知识空白更新**：移除"Obsidian 插件开发与定制"条目

---

## [2026-04-22] update | Claude Code 并行开发：Git Worktree + 工作流编排 + Routines

- **来源**：[[0raw/Claude Code 并行开发完全指南：Subagents + Agent Teams + Git Worktree + 工作流编排实战]]（微信公众号文章）
- **操作**：将 Git Worktree、工作流编排、Routines 三块新内容整合到 [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams]]
- **新增内容**：
  - 第三部分：Git Worktree 并行开发（命令、实战、与 Agent Teams 对比选型表）
  - 第四部分：工作流编排（Plan 模式嵌入、5 阶段 Multi-Agent 工作流模板、CLAUDE.md 固化）
  - Routines 定时自动执行（3 种触发方式、配置示例、与 Agent Teams 无人值守流水线）
  - 常见坑汇总（4 类）、全局选型决策表（6 场景）

---

## [2026-04-21] create | Awesome DESIGN.md 前端设计提示词集合

- **来源**：[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 仓库
- **操作**：将 67 个品牌的 DESIGN.md 设计系统文件添加到 `AI/AI-视觉/awesome-design-md/` 子目录
- **内容**：每个品牌目录保留 DESIGN.md + README.md + preview.html + preview-dark.html（共 268 个文件）
- **新建**：[[AI/AI-视觉/awesome-design-md/README|导航首页]]，含 DESIGN.md 概念说明、使用方法、按 8 大分类的品牌 wikilink 目录

---

## [2026-04-20] update | Claude Code 扩展体系 - Datadog MCP 配置

- **来源**：[[0raw/Set Up the Datadog MCP Server 1]]（Datadog 官方文档）
- **操作**：在 [[AI/ClaudeCode/Claude Code 扩展体系]] MCP 章节新增 Datadog MCP Server 配置
- **内容**：Claude Code 两种配置方式（远程 HTTP / 本地二进制）、权限要求、Toolset 按需加载机制、18 个 Toolset 完整列表（16 GA + 2 Preview）

---

## [2026-04-20] update | OpenClaw second-brain 知识管理插件

- **来源**：[[0raw/Openclaw帮你管理个人知识库]]（微信公众号文章）
- **操作**：将 second-brain 插件内容整合到 [[OpenClaw-Skills-Plugins]] 的"记忆插件"章节前，新增"个人知识库 - second-brain"章节
- **改动**：安装配置命令、6 种使用场景表格、核心能力总结、与记忆插件的区别说明
- **实体更新**：[[KnowledgeBase/entities/OpenClaw]] Skills 插件生态新增 second-brain 条目

---

## [2026-04-20] update | AI做PPT - ppt-master 补充完整内容

- **来源**：[[Clippings/这才是AI做ppt的正确姿势 ！ 1]]（完整版微信公众号文章）
- **操作**：根据完整原文更新 [[AI/AI-视觉/AI做PPT-ppt-master]]
- **新增内容**：与现有工具对比表（Gamma/Beautiful.ai/Copilot）、SVG→DrawingML 原生转换原理、双文件输出机制、强制顺序生成设计、内置资源数量（20 布局 + 52 可视化 + 6700 图标 + 12 图像后端）、公司模板支持、15 个官方案例（229 页）、作者背景与项目动机

---

## [2026-04-20] create | AI做PPT - ppt-master

- **来源**：[[0raw/这才是AI做ppt的正确姿势 ！]]（微信公众号文章）+ [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) 仓库
- **操作**：在 AI 目录下新建 [[AI/AI-视觉/AI做PPT-ppt-master]] 文章
- **内容**：ppt-master 项目简介、核心特性（多格式/多风格/CRAP 设计原则）、AI 角色系统（Strategist→Executor→Optimizer 管道）、7 步使用流程、技术栈

---

## [2026-04-18] update | Containerd V2 私有仓库配置整合

- **来源**：[[0raw/V2 版 Containerd 配置私有仓库和镜像加速]]（微信公众号文章）
- **操作**：将 V2 版 containerd 私有仓库配置内容整合到 [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤]] 的 containerd 配置章节
- **改动**：
  - 新增 `config_path` 与 `mirrors` 互斥警告 callout，含 V1/V2 插件路径差异说明
  - 将原有 Harbor 私有仓库示例扩展为两种方式：跳过证书校验（测试环境）+ 自签 CA 证书验证（生产环境推荐）
  - 新增 Authorization header 认证配置和 crictl 验证命令

---

## [2026-04-18] update | K8s Namespace Terminating 强制删除脚本

- **来源**：[[Clippings/实用脚本：强制删除K8s命名空间（Terminating状态）]]（微信公众号文章）
- **操作**：将自动化删除脚本整合到 [[Docker-Kubernetes/k8s-basic-resources/k8s基础-namespace-资源分配]] 的"ns删除后卡在Terminating状态"章节
- **改动**：原有手动步骤保留，新增原理说明 + 完整自动化脚本（含参数交互和结果验证）

---

## [2026-04-18] ingest | Istio Sidecar vs Ambient 模式对比

- **来源**：[[0raw/Istio Sidecar vs Ambient：不是"谁先进"，而是"谁更省、谁更稳、谁更适合你现在"]]（微信公众号文章）
- **操作**：简化整理为 [[Docker-Kubernetes/k8s-networking-service-mesh/Istio-Sidecar-vs-Ambient]]
- **知识库更新**：
  - `entities/Istio.md` — 新增 Sidecar vs Ambient 模块 + sources 引用 + 相关文章链接
  - "可延展方向"中 Ambient Mesh 条目已标记为已覆盖

---

## [2026-04-18] create | OpenClaw Workspace 运维实战文章

- **来源**：[[0raw/牛逼干货分享！OpenClaw Workspace 运维实战手册]]（微信公众号文章，1500+ 行）
- **操作**：简化整理为 [[AI/OpenClaw/OpenClaw-Workspace-运维]]（约 400 行），保留核心运维知识，去除冗余示例和重复内容
- **核心内容**：
  - 配置与内容文件体系分离架构
  - 标准目录布局与多 Agent 环境隔离策略
  - 核心配置文件速查（openclaw.json / TOOLS.md 权限分级）
  - 记忆系统运维（builtin vs qmd、污染处理、清理策略）
  - Skill 三级加载层级
  - 故障排查清单（7 类问题）
  - 备份恢复与灾难恢复（RTO/RPO）
  - 安全加固（权限基线、敏感信息管理、审计日志）
- **知识库更新**：
  - `entities/OpenClaw.md` — 新增 sources 引用 + Workspace 运维模块
  - `index.md` — 新增 OpenClaw Workspace 运维条目

---

## [2026-04-18] update | Claude Code Plugin 新增 obra/superpowers

- **来源**：[obra/superpowers](https://github.com/obra/superpowers)（通过 DeepWiki 获取仓库信息）
- **操作**：从"开源 Skills 仓库"一句话提及扩展为"开源 Plugin 推荐"独立章节，含 22 个 Skill 全表、强制工作流 7 步说明、安装方式
- **内容**：强迫 AI 按高级工程师标准流程工作的 Skills 套件——TDD + 头脑风暴 + 子智能体隔离开发 + 代码审查

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


## [2026-04-27] create | 多Agent vs 单Agent架构决策分析

- 创建 `analysis/multi-agent-vs-single-agent.md` 分析页
- 核心论点：多Agent在现阶段很多时候是伪需求，提出信息隔离与并发需求两个决策维度
- 内容涵盖：决策框架表格、信息损失分析、模型注意力论证、多Agent身份切换的真正价值
- 关联页面：[[KnowledgeBase/sources/多智能体协作-summary]]、[[KnowledgeBase/entities/Claude-Code]]
- 更新 INDEX.md 分析报告分类，新增第 4 条条目


## [2026-05-04] lint | 知识库全面健康检查

### 1. 断链检查
- 共检查 2,458 个 wikilink，发现 346 个断链（273 个唯一目标）
- **15 个格式错误链接**：`entities/OpenClaw.md` 和 `entities/Azure.md` 中有尾部反斜杠 `\` 的畸形 wikilink
- **1 个命名不一致**：`Docker Compose`（空格）→ 实际文件名 `Docker-Compose`（连字符）
- **9 个路径错误**：链接指向 `KnowledgeBase/entities/X` 但实际文件在 Raw Source 目录（ECS、VPC、WAF、Fiddler、Landing Zone、OpenStack、RabbitMQ、RocketMQ、VSCode）
- **217 个缺失 KB 页面**：被引用但从未创建的概念/实体页（66 个概念 + 151 个实体），高频缺失：StorageClass(4次)、ServiceMesh(3次)、高可用架构(3次)
- **19 个死链**：`log.md` 中引用的 `0raw/` 路径，文件已移动或删除

### 2. 孤儿页检查（无入链页面）
- 总计 83 个 wiki 页面，25 个孤儿页（30%）
- concepts/ 和 entities/：**0 孤儿**（核心知识页全部互联良好）
- sources/：11 个孤儿（50%）— 无概念/实体页链回这些摘要
- maps/：5 个孤儿（63%）
- analysis/：4 个孤儿（100%）
- inventory/：2 个孤儿（100%）
- maintenance/：3 个孤儿（100%）

### 3. Raw Source 覆盖检查
- 16 个 Raw Source 目录已 100% 覆盖（Docker-Kubernetes、Aliyun、Azure、Go、Python、Linux-Shell 等）
- **AI/ 目录严重欠缺**：301 个文件仅 37 个被引用（12%覆盖）
  - CloudOps-Agent-项目/（74 文件）：完全未摄入
  - RAG-Agent-项目/（33 文件）：完全未摄入
  - Hermes-agent/（2 文件）：完全未摄入
  - AI-视觉/awesome-design-md/（135 文件）：完全未摄入
- **IaC/**：`terraform-container-management.md` 新增未摄入（1 文件）

### 4. Frontmatter 规范检查
- 80 个 wiki 页面全部通过：title、tags（含 `knowledgebase/*`）、date — **100% 合规**
- **aliases 字段缺失**：58 个文件（72.5%）缺少 aliases

### 5. Index 完整性检查
- index.md 与磁盘文件 **完全同步**：82 个条目全部对应实际文件，无缺失、无多余

### 建议优先修复项
1. 修复 15 个反斜杠畸形链接（OpenClaw.md、Azure.md）
2. 修复 Docker Compose 命名不一致
3. 摄入 AI/ 下新增项目（CloudOps-Agent、RAG-Agent、Hermes-agent）
4. 为 sources/ 页面建立入链（从 concepts/entities 页面链回）
5. 补充高频缺失概念页（StorageClass、ServiceMesh、高可用架构）


---

## [2026-05-05] lint | 文件重命名后断链修复

- **触发**：用户更新了文章标题（`OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`，`Hermes Agent全解析-与OpenClaw对比及飞书接入指南` → `Hermes与OpenClaw对比及飞书接入指南`）
- **检查范围**：KnowledgeBase/ 全部 93 个页面，748 个 wikilink

### 1. 断链修复（12 处）

| 文件 | 修复内容 |
|------|----------|
| [[KnowledgeBase/maps/ai-workflow-map.md\|ai-workflow-map]] | `OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`（2 处）；Hermes 摘要篇数 2→3 |
| [[KnowledgeBase/maps/claude-code-openclaw-map.md\|claude-code-openclaw-map]] | `OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`（3 处：代码块 + 表格） |
| [[KnowledgeBase/inventory/repository-inventory.md\|repository-inventory]] | `OpenClaw-Skills-插件` → `OpenClaw-Skills-Plugins`（2 处） |
| [[KnowledgeBase/sources/hermes-agent-batch-summary.md\|hermes-agent-batch-summary]] | 补全路径 `AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南`（frontmatter + 正文，2 处） |
| [[KnowledgeBase/entities/OpenClaw.md\|OpenClaw]] | 补全路径 `AI/OpenClaw/OpenClaw-Skills-Plugins`（frontmatter + 正文，2 处）；补全 `AI/Hermes-agent/` 前缀（1 处） |
| [[KnowledgeBase/sources/ai-openclaw-misc-batch-summary.md\|ai-openclaw-misc-batch-summary]] | 补全路径 `AI/OpenClaw/OpenClaw-Skills-Plugins`（frontmatter + 正文，2 处） |

### 2. 孤儿页检查
- **结果**：0 个孤儿页。所有 93 个 KB 页面至少有 1 个入链（主要来自 INDEX.md 和 maps/）

### 3. 概念覆盖差距（≥3 篇引用但无独立页面）
- Tekton（11 篇）、Ansible（11 篇）、Kyverno（7 篇）、Velero（6 篇）、Skywalking（6 篇）、VPA（6 篇）
- Hermes Agent（5 篇）、RAG（5 篇）、KEDA（5 篇）、HPA（5 篇）
- 飞书/Lark（4 篇）

### 4. 残留历史链接（不修改）
- `log.md` 中 3 处历史记录引用旧文件名（`Hermes Agent全解析-与OpenClaw对比及飞书接入指南`、`[[OpenClaw-Skills-Plugins]]` 短路径），属于历史快照不做修改


---

## [2026-05-05] ingest | HarnessKit — AI 编码智能体统一管理工具

- **来源**：GitHub 仓库 https://github.com/RealZST/HarnessKit（README + API 元数据）
- **操作**：
  - 新建 [[AI/HarnessKit]]：工具介绍文章（功能特性、支持的 Agent、安装使用、安全审计、与其他 AI 工具的关系）
  - 新建 [[KnowledgeBase/sources/harnesskit-summary]]：来源摘要页
  - 更新 [[KnowledgeBase/maps/ai-workflow-map]]：补充阅读列表 + 相关工具
  - 更新 [[KnowledgeBase/INDEX.md]]：新增 HarnessKit 来源摘要条目


---

## [2026-05-09] ingest | Obsidian + Claude Code AI 知识库完整指南（三文合并）

- **来源**：[[AI/Obsidian/obsidian-claude-code-AI知识库完整指南]]
- **操作**：
  - 将三篇文章合并为一篇完整指南：
    - `karpathy-llm-wiki-改造计划`（内部规划文档，含差距分析与行动计划）
    - `obsidian-claude-搭建karpathy-wiki知识库`（工具搭建方法论，含六大操作谱系）
    - `obsidian-claude-code-AI知识管家`（公众号文章，含 Markdown 母语论证与实践判断）
  - 删除三篇原始文件（内容已完整保留在合并文章中）
  - 删除两个旧来源摘要页：`obsidian-claude-搭建个人知识库-summary.md`、`obsidian-claude-code-AI知识管家-summary.md`
  - 新建 [[KnowledgeBase/sources/obsidian-claude-AI知识库完整指南-summary.md]]：合并后的来源摘要
  - 更新 [[KnowledgeBase/index.md]]：替换两个旧条目为一个新条目
  - 更新 [[AI/index.md]]：Obsidian 子目录条目从 4 篇→2 篇，关键入口更新

