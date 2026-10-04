---
title: 文章标题审阅
tags:
  - knowledgebase/analysis
  - knowledgebase/title-review
date: 2026-10-04
sources:
  - "[[AI/Obsidian/github-pages-quartz]]"
  - "[[AI/AI-视觉/Markdown-Viewer-Skills-Markdown中直接画图]]"
  - "[[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板]]"
  - "[[Docker-Kubernetes/k8s-security-auth/k8s-Admission-Webhook链冲突排查-Istio-Kyverno-Gatekeeper]]"
aliases:
  - 标题优化分析报告
  - Digital Garden 标题审阅
---

# 文章标题审阅

> [!info] 待确认稿
> 本轮扫描并逐条审阅了 856 个 Markdown 文件的标题。建议优化 75 个文件，其中 49 个参与 GitHub Pages 发布。原文章标题、文件名和发布配置均未修改；本轮只新增审阅报告、完整清单与对应导航/日志记录。

建议先确认**网页标题可直接精简的 26 条**。另有 **23 条网页标题需要短主标题配合副标题或引言**，以保留数字、作者归因、组件列表和适用条件；这 23 条不能只采用短主标题。**26 条离线建议**目前不会影响网页，可按需安排。其余 781 个文件保留现状或另列问题。

## 1. 扫描范围与计数

扫描基于 2026-10-04 工作区中 Git 跟踪的 Markdown，未发现额外的未跟踪主题文章。未计入生成的网站、Quartz 缓存或忽略的依赖文件；也未把本轮新建报告计入扫描快照。

| 范围 | 文件数 | 与网页的关系 |
| --- | ---: | --- |
| 18 个主题下参与发布的 Markdown | 412 | 本轮网页建议的分母；含 38 份角色/Skill 定义 |
| KnowledgeBase 编译层 | 178 | 当前发布筛选排除整个目录 |
| AI/RAG 引用与嵌入内容 | 110 | 当前发布筛选排除 |
| AI 视觉设计参考库 | 135 | 当前发布筛选排除 |
| 主题根目录 index.md | 18 | 网页主题页由构建器生成，不直接使用这些导航稿 |
| 根目录 README.md、AGENTS.md、CLAUDE.md | 3 | 不作为网页文章发布 |
| 合计 | 856 | 文件数，不等同于 856 篇独立学习文章 |

完整逐文件记录见 [[KnowledgeBase/maintenance/title-audit-2026-10-04|标题审阅清单]]。清单保留原路径、取值标题、首个正文 H1、标题载体、发布状态和审阅结论，包含建议保留的文件。

## 2. 网页标题实际来自哪里

GitHub Actions 的 `.github/workflows/deploy-pages.yml` 调用 `tools/site/build.py`。其 `extract_title()` 的顺序是：

1. 非空字符串形式的 frontmatter `title`。
2. 去除 frontmatter 后，正文**首个非空行**若是 H1，则使用该 H1。
3. 否则使用文件名，不会继续向下寻找其他 H1。

412 个发布文件分别有 **362 个取 frontmatter、46 个取首行 H1、4 个取文件名**。49 个网页候选中有 **47 个取 frontmatter、2 个取首行 H1**；没有候选需要改文件名。

导出器把选出的标题写入 Quartz 的 frontmatter，首页最近更新、主题列表和文章标题使用这一值。网页的完整文章 URL 由文件路径生成；标题文字和文件路径可分别处理。搜索及目录标签也需要在后续构建时抽查。

### 在线抽样结果

本轮读取首页和以下三篇在线 HTML，均返回 HTTP 200；三篇页面顶部的 `.article-title` 与本地取值一致：

| 页面 | 网页顶部 | 正文首个 H1 |
| --- | --- | --- |
| [[AI/AI-视觉/Markdown-Viewer-Skills-Markdown中直接画图\|Markdown Viewer Skills]] | Markdown Viewer Skills：让 AI 写文档时顺手把图也画了 | Markdown Viewer Skills：AI 文档配图 |
| [[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板\|CLAUDE.md 12 条规则]] | Mnilax：CLAUDE.md 规则从 Karpathy 的 4 条增加到 12 条，错误率从 41% 降到 3% | 无 |
| [[Docker-Kubernetes/k8s-security-auth/k8s-Admission-Webhook链冲突排查-Istio-Kyverno-Gatekeeper\|Webhook 冲突排查]] | 当 Istio、Kyverno、Gatekeeper 三个 Webhook 同时存在，你的集群会发生什么？ | Admission Webhook 链冲突排查 |

这说明正文已经有短标题时，仅修改正文 H1 仍可能留下网页上的长标题。对有 frontmatter 的文章，构建器保留正文 H1，因此 Markdown Viewer 和 Webhook 样例还出现了顶部标题与正文标题并列的情况。

全库记录到 117 个取值标题与首个正文 H1 不同的文件，其中 70 个参与发布。差异也可能来自正文小节，不把这些差异全部视为错误。确认后应只同步明确属于文章标题的 H1；没有文章 H1 的文件只处理实际标题字段。

## 3. 审阅原则

使用 humanizer-zh 的本地版本 `/Users/hang.xu/.codex/skills/humanizer-zh/SKILL.md`，重点检查起跑式铺垫、重复、宣传语、装饰性标题和长定语。

- 保留产品、技术对象、版本、数量、比较对象、适用条件、时间和归因；保留“只读”“低风险”等操作边界。
- 直接精简只合并重复表达或去掉没有独立信息的铺垫。“全家桶”“完整”“详解”等逐题判断，不能机械删词。
- 组件列表、比例和作者信息若无法同时放入短主标题，采用“主标题＋副标题/引言”。表中的保留项属于方案的一部分。
- 保留有意义的问句、技术长名、书名和系列编号。英文设计参考保留原语种；角色与 Skill 定义保留原标识。

程序使用“中文/全宽字符约 1 em、其他字符约 0.5 em”作粗略筛查，标记到 21 个约 28 em 以上的网页标题。该估计不包含实际字形与屏幕宽度，只用来发现候选；全部标题都经过审阅，精简建议也不只来自这 21 个标题。长度下降不作为语义正确的验收标准。

## 4. 网页标题：可直接精简的 26 条

“优先”表示冗余较明显或较影响浏览；“可选”表示改动幅度较小，可保留现题。这一组不需要删除或迁移数字、归因、版本和独立技术范围。

| 条目 | 原标题 | 建议主标题 | 理由与信息保留 |
| --- | --- | --- | --- |
| [[AI/AI-视觉/Diagram-design\|T0004]] · 优先 | Diagram Design：让 Claude Code / Codex 生成更有设计感的技术图 | Diagram Design：Claude Code / Codex 技术图设计 | 把“让……生成更有设计感的”改成用途名称，保留两种工具与技术图设计。 |
| [[AI/AI-视觉/Markdown-Viewer-Skills-Markdown中直接画图\|T0006]] · 优先 | Markdown Viewer Skills：让 AI 写文档时顺手把图也画了 | Markdown Viewer Skills：AI 文档配图 | 沿用现有正文 H1，删去“让 AI 写文档时顺手把图也画了”的长句。 |
| [[AI/ClaudeCode/CLAUDE.md最佳实践-21条指令清单\|T0185]] · 优先 | Mayank Agarwal：21 条 CLAUDE.md 指令，让 Claude 真正懂你 | Mayank Agarwal：21 条 CLAUDE.md 指令 | 删去“让 Claude 真正懂你”的空泛效果表述，保留作者、21 条和配置文件名。 |
| [[Docker-Kubernetes/docker/docker无需本地环境从DockerHub下载镜像并保存为tar\|T0419]] · 优先 | 不依赖本地 Docker 环境：从 Docker Hub 下载镜像并保存为 tar 文件 | 无需本地 Docker：下载 Docker Hub 镜像为 tar | 合并“下载镜像并保存为 tar 文件”，保留不依赖本地 Docker、镜像来源与输出格式。 |
| [[Docker-Kubernetes/k8s-ai-gpu/从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖”\|T0466]] · 优先 | 从零部署 NVIDIA Device Plugin：K8s 识别 GPU 的“第一块敲门砖” | NVIDIA Device Plugin：K8s GPU 识别与部署入门 | 用具体用途替换“第一块敲门砖”，保留插件名、K8s GPU 识别和从零部署的入门定位。 |
| [[Docker-Kubernetes/k8s-basic-resources/k8s-APIServer深度剖析-请求链路-认证授权-生产调优\|T0471]] · 优先 | Kubernetes API Server 深度剖析：请求链路、认证授权与生产调优 | K8s API Server：请求链路、认证授权与生产调优 | 删去“深度剖析”，用常用 K8s 缩写；三个技术范围全部保留。 |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-pod调度-标签与选择器实战\|T0484]] · 优先 | Kubernetes 标签与选择器避坑：5 条核心铁律与生产级实战案例 | K8s 标签与选择器避坑：5 条规则与生产案例 | 将“核心铁律”改为“规则”，合并“生产级实战案例”，保留五条规则和生产案例。 |
| [[Docker-Kubernetes/k8s-installation-management/k8s-Backstage-内部开发者平台IDP实战\|T0513]] · 优先 | K8s 平台工程实战：用 Backstage 打造一站式内部开发者平台 | Backstage：K8s 一站式内部开发者平台实战 | 删除“平台工程实战：用……打造”的套叠，保留一站式、内部开发者平台、K8s 与实战定位。 |
| [[Docker-Kubernetes/k8s-installation-management/k8s-cgroup-v2深度解析-迁移实战与避坑指南\|T0514]] · 优先 | K8s CGroup v2 深度解析：资源隔离原理、迁移实战与生产避坑指南 | K8s cgroup v2：资源隔离原理、迁移与生产避坑 | 删去“深度解析”和“指南”，保留 v2、资源隔离原理、迁移与生产边界。 |
| [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶\|T0540]] · 优先 | Prometheus-Stack 全家桶：生产级部署与运维完全指南 | Prometheus-Stack：生产部署与运维 | 删除“全家桶”和“完全指南”，保留 Stack、生产部署与运维。 |
| [[Docker-Kubernetes/k8s-security-auth/k8s容器安全上下文-SecurityContext\|T0570]] · 优先 | Kubernetes 容器安全上下文完全指南：从入门到生产避坑 | K8s 容器安全上下文：从入门到生产避坑 | 删除“完全指南”，保留从入门到生产避坑的范围和顺序。 |
| [[Docker-Kubernetes/k8s-storage/让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入\|T0577]] · 优先 | 让存储故障现形：Kubernetes Volume Health Monitor 原理与生产接入 | K8s Volume Health Monitor：原理与生产接入 | 删除“让存储故障现形”的引导语，保留完整组件名、原理与生产接入。 |
| [[AI/AIOps/AIOps实战-Golang手搓K8s智能运维工具链\|T0146]] · 可选 | AIOps 实战：Golang 手搓 K8s 智能运维工具链 | Golang 构建 K8s 智能运维工具链实战 | 把“手搓”换成直接动作，保留语言、平台、智能运维和实战范围。 |
| [[AI/ClaudeCode/Claude-Code-Harness实战-最小可用系统\|T0190]] · 可选 | Harness 实战：从零搭建最小可用的 Harness 系统 | Harness 实战：从零搭建最小可用系统 | 合并标题中重复的 Harness，保留从零搭建与最小可用范围。 |
| [[AI/ClaudeCode/Claude-Code为什么用grep不用RAG\|T0191]] · 可选 | 为什么 Claude Code 不用 RAG 检索代码，而是 grep？ | Claude Code 为何用 grep 而非 RAG 检索代码？ | 缩短问句，保留为什么、代码检索、grep 与 RAG 的比较。 |
| [[AI/ClaudeCode/Git-Worktree-AI开发实践指南\|T0194]] · 可选 | Vibe Coding 时代的 Git Worktree 实践指南 | Vibe Coding 的 Git Worktree 实践 | 压缩“时代的……实践指南”，保留 Vibe Coding 语境与 Worktree 实践。 |
| [[AI/Hermes-agent/Hermes与OpenClaw对比及飞书接入指南\|T0208]] · 可选 | Hermes Agent全解析：与OpenClaw对比及飞书接入指南 | Hermes Agent：OpenClaw 对比与飞书接入 | 去掉“全解析”和“指南”，保留两个具体主题。 |
| [[AI/Obsidian/Obsidian-Vault模板库合集-48个宝藏vault\|T0212]] · 可选 | Obsidian Vault 模板库合集：48 个 GitHub 宝藏 vault | Obsidian Vault：48 个 GitHub 模板库 | 合并重复的 vault/模板库/合集，删除“宝藏”，保留数量和 GitHub 来源。 |
| [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南\|T0215]] · 可选 | Obsidian + Claude Code：AI 驱动的知识库完整指南 | Obsidian + Claude Code：AI 知识库指南 | 压缩“AI 驱动的”和“完整”，保留两种工具与 AI 知识库主题。 |
| [[AI/行业动态/Claude-Code创始人红杉大会七个判断\|T0353]] · 可选 | Claude Code 创始人在红杉大会上的 7 个重要判断 | Claude Code 创始人：红杉大会的 7 个判断 | 删去“在……上的”和“重要”，保留身份、场合和七个判断。 |
| [[Docker-Kubernetes/docker/docker安全配置-Capabilities与容器加固\|T0418]] · 可选 | Docker 安全配置详解：Capabilities 与容器加固 | Docker 安全配置：Capabilities 与容器加固 | 只删去“详解”，保留 Capabilities 和容器加固两个范围。 |
| [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD部署Helm应用时域名解析失败问题排查与解决\|T0436]] · 可选 | ArgoCD部署Helm应用时域名解析失败问题排查与解决 | ArgoCD Helm 部署：域名解析故障处理 | 用“故障处理”概括排查与解决，保留 ArgoCD 部署 Helm 应用时的域名解析问题。 |
| [[Docker-Kubernetes/k8s-CICD/Claude-Code实现CICD自动化发布流程\|T0438]] · 可选 | Claude Code 实现 CI/CD 自动化发布流程详细指南 | Claude Code CI/CD 自动发布指南 | 压缩“实现……流程详细指南”，保留工具、CI/CD 与自动发布。 |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Operator开发实战-Kubebuilder\|T0475]] · 可选 | 从零开发 Kubernetes Operator：Kubebuilder 实战教程 | Kubebuilder：从零开发 K8s Operator | 突出开发工具，保留从零开发和 Kubernetes Operator，压缩“实战教程”。 |
| [[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理-采集方案与审计日志\|T0541]] · 可选 | K8s 日志管理：基础机制、六种采集方案与审计日志实战 | K8s 日志：基础机制、六种采集方案与审计日志 | 压缩“管理”和“实战”标签，保留基础机制、六种方案、审计日志三个范围。 |
| [[Docker-Kubernetes/k8s-scaling/k8s-HPA-VPA\|T0559]] · 可选 | Kubernetes 自动扩缩容实战：HPA、VPA 与 Scale-to-Zero | K8s 自动扩缩容：HPA、VPA 与 Scale-to-Zero | 用 K8s 缩写并压缩实战标签，保留三项独立技术范围，未删去 Scale-to-Zero。 |

## 5. 网页标题：需保留副标题或引言的 23 条

**采用此组时，必须同时保留最后一列的信息。** 建议将副标题放在正文开头的普通段落或现有引言中，避免重复生成第二个文章 H1。当前代码未实现独立的 frontmatter `subtitle` 显示组件，不能只新增该字段就假定网页会显示。

其中数据、效果与趋势均作为原文的说法保留，本轮没有核验 41%→3%、92%、60%、“上百个集群”等结论，也没有将它们推广为普遍效果。

| 条目 | 原标题 | 建议主标题 | 理由与信息保留 |
| --- | --- | --- | --- |
| [[AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板\|T0184]] · 优先 | Mnilax：CLAUDE.md 规则从 Karpathy 的 4 条增加到 12 条，错误率从 41% 降到 3% | Mnilax 的 CLAUDE.md：12 条规则 | **副标题/引言：** 在 Karpathy 的 4 条规则上扩为 12 条；原文报告错误率从 41% 降到 3%。<br>主标题聚焦规则集；作者归因、原有 4 条规则和错误率数据必须留在引言或副标题，数据未在本轮独立核验。 |
| [[AI/Code review和知识图谱/CodeGraph-代码语义知识图谱\|T0198]] · 优先 | CodeGraph：给 Claude Code 先画一张代码地图，工具调用砍掉 92% | CodeGraph：Claude Code 代码知识图谱 | **副标题/引言：** 提前构建代码地图；项目 README 的基准称平均工具调用减少 92%。<br>保留 Claude Code 使用场景，把数字放入带来源的说明，避免精简时丢掉独立信息。 |
| [[AI/Code review和知识图谱/code-review-graph-本地代码知识图谱\|T0201]] · 优先 | 开源 Claude Code 本地代码知识图谱：code-review-graph 完整上手攻略 | code-review-graph：本地代码知识图谱指南 | **副标题/引言：** 开源工具，面向 Claude Code 的本地代码知识图谱。<br>把很长的产品名放在开头；开源属性与 Claude Code 场景放入副标题。 |
| [[AI/Hermes-agent/Hermes-Curator-Skill膨胀治理\|T0207]] · 优先 | Skill 太多导致上下文膨胀怎么办？来自 Hermes Agent 的实践 | Hermes Agent：Skill 膨胀与上下文治理 | **副标题/引言：** Skill 过多导致上下文膨胀；本文介绍 Hermes Agent 的治理实践。<br>把问题式长标题改成主题名，原题的数量原因与上下文影响保留在副标题。 |
| [[AI/OpenClaw/OpenClaw-K8s智能运维实战\|T0218]] · 优先 | 用 OpenClaw 智能体网关接管 K8s 日常运维：从只读巡检到低风险变更 | OpenClaw K8s 运维：从只读巡检到低风险变更 | **副标题/引言：** 通过 OpenClaw 智能体网关接管 K8s 日常运维。<br>优先保留只读、低风险和阶段顺序，网关角色与日常运维放入副标题。 |
| [[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议\|T0352]] · 优先 | Anthropic 工程师力推 HTML 取代 Markdown —— Karpathy 附议 | HTML 取代 Markdown：Anthropic 工程师的建议 | **副标题/引言：** Karpathy 对这一建议表示支持。<br>缩短宣传语与破折号结构；两方归因分别保留，不把原文主张改成本站结论。 |
| [[AI/行业动态/TypeScript-vs-Python-AI-Agent时代的语言之争\|T0356]] · 优先 | 为什么 AI Agent 时代，TypeScript 正在抢走 Python 的主场？ | AI Agent 时代：TypeScript 与 Python 的竞争 | **副标题/引言：** 原文讨论 TypeScript 正在抢走 Python 主场的原因。<br>主标题便于浏览；原题的变化方向、正在发生和原因分析保留在副标题。 |
| [[Docker-Kubernetes/k8s-CICD/ArgoCD/ArgoCD多集群GitOps实战\|T0435]] · 优先 | 多集群 GitOps 实战：用 Argo CD 管理上百个 Kubernetes 集群 | Argo CD 多集群 GitOps 实战 | **副标题/引言：** 用 Argo CD 管理上百个 Kubernetes 集群。<br>主标题保留平台和实践类型，集群规模作为原文场景保留。 |
| [[Docker-Kubernetes/k8s-CICD/Kustomize/Kustomize入门-Base与Overlay多环境配置\|T0449]] · 优先 | Kustomize 入门：用 Base 和 Overlay 管理 Kubernetes 多环境配置 | Kustomize 入门：Base 与 Overlay | **副标题/引言：** 用 Base 和 Overlay 管理 Kubernetes 多环境配置。<br>主标题保留学习阶段和两个核心术语，多环境配置用途放入副标题。 |
| [[Docker-Kubernetes/k8s-basic-resources/k8s基础-容器设计模式-Sidecar-Init-Ambassador-Adapter\|T0489]] · 优先 | K8s 容器设计模式：Sidecar / Init Container / Ambassador / Adapter | K8s 四种容器设计模式 | **副标题/引言：** Sidecar / Init Container / Ambassador / Adapter。<br>四种模式全部保留在副标题；数量来自原题的四项列表，也可区别已存在的“K8s 容器设计模式”来源摘要。 |
| [[Docker-Kubernetes/k8s-monitoring-logging/OpenTelemetry实战-统一Traces-Metrics-Logs\|T0533]] · 优先 | OpenTelemetry 实战：告别厂商锁定，统一 Traces/Metrics/Logs | OpenTelemetry 统一可观测性实战 | **副标题/引言：** 原文主张：告别厂商锁定，统一 Traces / Metrics / Logs。<br>三个信号与厂商锁定主张留在副标题；本轮只审阅表达，不确认厂商锁定已被解决。 |
| [[Docker-Kubernetes/k8s-scaling/k8s-基于KEDA的弹性能力\|T0560]] · 优先 | Kubernetes KEDA 事件驱动自动扩缩容：原理、选型与 KServe 实战 | KEDA：事件驱动扩缩容与 KServe 实战 | **副标题/引言：** Kubernetes 事件驱动自动扩缩容的原理与选型。<br>主标题突出 KEDA 与 KServe；平台、自动扩缩容原理和选型信息留在副标题。 |
| [[Docker-Kubernetes/k8s-security-auth/k8s-Admission-Webhook链冲突排查-Istio-Kyverno-Gatekeeper\|T0569]] · 优先 | 当 Istio、Kyverno、Gatekeeper 三个 Webhook 同时存在，你的集群会发生什么？ | Admission Webhook 链冲突排查 | **副标题/引言：** Istio、Kyverno、Gatekeeper 三个 Webhook 同时存在的集群。<br>正文已有准确短标题；三个组件及同时存在的条件留在副标题。 |
| [[AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas\|T0213]] · 可选 | Obsidian 可视化 Skills — Excalidraw / Mermaid / Canvas | Obsidian 可视化 Skills | **副标题/引言：** Excalidraw / Mermaid / Canvas。<br>三种格式都有独立意义，只建议移到副标题，不能直接删去。 |
| [[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？\|T0338]] · 可选 | 一个 Deployment 就能跑 vLLM，为什么还需要 KServe？ | 为何用 KServe 管理 vLLM 推理服务？ | **副标题/引言：** 单个 Deployment 已能运行 vLLM；本文讨论继续引入 KServe 的理由。<br>保留提问语气与原题前提，主标题聚焦 KServe 的用途。 |
| [[Azure/7_ACR-ACI\|T0391]] · 可选 | Azure Container Registry & Azure Container Instances | Azure ACR 与 ACI | **副标题/引言：** Azure Container Registry 与 Azure Container Instances。<br>列表标题使用正文和文件名已有的缩写，副标题保留两个完整产品名。 |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.394)的DevOps工具链-基于yaml\|T0446]] · 可选 | K8s部署基于Jenkins(2.394)的DevOps工具链-基于YAML | K8s DevOps 工具链：Jenkins 2.394 | **副标题/引言：** 基于 YAML 部署。<br>删除两层“基于”的套叠；版本留在主标题，部署方式留在副标题，区分另一篇 Jenkins 版本文章。 |
| [[Docker-Kubernetes/k8s-CICD/Jenkins/k8s部署基于Jenkins(2.426.3)的Devops工具链-基于yaml\|T0447]] · 可选 | K8s部署基于Jenkins(2.426.3)的DevOps工具链-基于YAML | K8s DevOps 工具链：Jenkins 2.426.3 | **副标题/引言：** 基于 YAML 部署。<br>与 Jenkins 2.394 条目采用同一结构，完整保留版本与 YAML 部署方式。 |
| [[Docker-Kubernetes/k8s-image-management/Dragonfly与Harbor-P2P镜像分发\|T0508]] · 可选 | Dragonfly + Harbor：AI 集群的 P2P 镜像与大文件分发 | Dragonfly + Harbor：P2P 分发 | **副标题/引言：** 面向 AI 集群的 P2P 镜像与大文件分发。<br>产品组合与 P2P 在主标题，AI 场景及两类分发对象留在副标题。 |
| [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶\|T0538]] · 可选 | Helm部署Loki+Promtail+Tempo+GrafanaAgent全家桶 | Helm 部署日志与追踪栈 | **副标题/引言：** Loki / Promtail / Tempo / Grafana Agent。<br>把四个组件名移到副标题，删除“全家桶”；组件与部署方式全部保留。 |
| [[Docker-Kubernetes/k8s-networking-service-mesh/k8s-Gateway-API入门-Ingress下一代方案\|T0554]] · 可选 | Kubernetes Gateway API 入门：Ingress 的下一代方案 | Kubernetes Gateway API 入门 | **副标题/引言：** Ingress 的下一代方案。<br>沿用现有正文 H1；与 Ingress 的关系留在副标题。 |
| [[Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战\|T0561]] · 可选 | K8s 集群成本优化方案：砍掉 60% 云账单 | K8s 集群成本优化 | **副标题/引言：** 原文主张：砍掉 60% 云账单。<br>保留 60% 的原文主张和归因，避免把未经本轮核验的节省比例放在列表标题中。 |
| [[HPC/Ubuntu2204-Slurm-安装指南\|T0604]] · 可选 | Ubuntu 22.04 Slurm 22.05.11 与 23.11.4 安装与配置指南 | Ubuntu 22.04：Slurm 安装与配置 | **副标题/引言：** Slurm 22.05.11 与 23.11.4；三套环境分开阅读和使用。<br>系统版本保留在主标题，两个 Slurm 版本留在副标题；部署参数不能跨版本混用。 |

## 6. 离线页面：26 条可选建议

以下 18 个 RAG 文件与 8 个 Wiki 来源摘要均未参与当前 Pages 发布。修改它们可以改善本地标题，但不会改变现有网页。章节编号保留；技术依赖、版本、更新状态等按表中说明保留。

| 条目 | 原标题 | 建议主标题 | 理由与信息保留 |
| --- | --- | --- | --- |
| [[AI/RAG/Confluence-Wiki-RAG知识库增强检索系统\|T0300]] · RAG | 从 0 到 1 搭建 Confluence 内部 Wiki RAG 知识库增强检索系统 | Confluence 内部 Wiki RAG 增强检索系统搭建 | **副标题/引言：** 从 0 到 1 搭建内部 Wiki RAG 知识库。<br>主标题保留内部 Wiki、RAG、增强检索和搭建；从零开始的定位移到副标题。 |
| [[AI/RAG/OpenRAG生产级知识库架构实战\|T0301]] · RAG | OpenRAG 生产级知识库架构实战：构建可治理、可扩展、可审计的企业级 RAG 平台 | OpenRAG 企业知识库：生产架构实战 | **副标题/引言：** 构建可治理、可扩展、可审计的企业级 RAG 平台。<br>三项能力都承载信息，移到副标题，不能作为空泛排比直接删除。 |
| [[AI/RAG/RAG-Agent-项目/1-开篇词/1.1-RAG-Agent RAG 知识库项目上线了！AI 时代，你值得拥有！\|T0302]] · RAG | 1.1-RAG-Agent RAG 知识库项目上线了！AI 时代，你值得拥有！ | 1.1 RAG-Agent RAG 知识库项目上线 | 只删去“AI 时代，你值得拥有”的营销语，保留章节号与已经上线的状态。 |
| [[AI/RAG/RAG-Agent-项目/2-工程篇/2.1-RAG-Agent环境搭建指南（新人必看）Java 17、MySQL、Elasticsearch、Redis、MinIO、Kafka\|T0304]] · RAG | 2.1-RAG-Agent环境搭建指南（新人必看）Java 17、MySQL、Elasticsearch、Redis、MinIO、Kafka | 2.1 RAG-Agent 环境搭建 | **副标题/引言：** Java 17 / MySQL / Elasticsearch / Redis / MinIO / Kafka。<br>删去“新人必看”，依赖清单完整保留，尤其保留 Java 17。 |
| [[AI/RAG/RAG-Agent-项目/2-工程篇/2.2-Elasticsearch 8.10安装教程（新人必看）\|T0305]] · RAG | 2.2-Elasticsearch 8.10安装教程（新人必看） | 2.2 Elasticsearch 8.10 安装 | 删除“新人必看”和教程标签，保留章节号、组件名与 8.10 版本。 |
| [[AI/RAG/RAG-Agent-项目/2-工程篇/2.4-Ollama+DeepSeek本地部署（新人必看）\|T0307]] · RAG | 2.4-Ollama+DeepSeek本地部署（新人必看） | 2.4 Ollama + DeepSeek 本地部署 | 只删去“新人必看”，保留两种工具与本地部署范围。 |
| [[AI/RAG/RAG-Agent-项目/2-工程篇/2.5-DeepSeek API申请（新人必看）\|T0308]] · RAG | 2.5-DeepSeek API申请（新人必看） | 2.5 DeepSeek API 申请 | 只删去“新人必看”，保留章节号和 API 申请。 |
| [[AI/RAG/RAG-Agent-项目/2-工程篇/2.6-本地运行RAG-Agent指南（新人必看）\|T0309]] · RAG | 2.6-本地运行RAG-Agent指南（新人必看） | 2.6 RAG-Agent 本地运行 | 删除“新人必看”和指南标签，保留本地运行场景。 |
| [[AI/RAG/RAG-Agent-项目/2-工程篇/2.7-Docker部署RAG-Agent（懒人福音）\|T0310]] · RAG | 2.7-Docker部署RAG-Agent（懒人福音） | 2.7 Docker 部署 RAG-Agent | 只删去“懒人福音”，保留章节号、Docker 与项目名。 |
| [[AI/RAG/RAG-Agent-项目/3-大厂篇/3.1-RAG-Agent RAG 系统的需求分析（非常重要）\|T0311]] · RAG | 3.1-RAG-Agent RAG 系统的需求分析（非常重要） | 3.1 RAG-Agent RAG 系统需求分析 | 去掉“非常重要”，保留系统、需求分析和章节号。 |
| [[AI/RAG/RAG-Agent-项目/3-大厂篇/3.2-RAG-Agent RAG整体设计方案（非常重要）\|T0312]] · RAG | 3.2-RAG-Agent RAG整体设计方案（非常重要） | 3.2 RAG-Agent RAG 整体设计 | 去掉“非常重要”和重复的设计方案标签，保留整体设计范围。 |
| [[AI/RAG/RAG-Agent-项目/4-进阶篇/4.2-RAG-Agent RAG 项目的ElasticSearch混合检索精讲\|T0320]] · RAG | 4.2-RAG-Agent RAG 项目的ElasticSearch混合检索精讲 | 4.2 RAG-Agent：Elasticsearch 混合检索 | 项目名已包含 RAG；压缩重复的“RAG 项目的……精讲”，保留 Elasticsearch 与混合检索。 |
| [[AI/RAG/RAG-Agent-项目/4-进阶篇/4.3-如何基于Spring Security实现RAG-Agent RAG 知识库的RBAC 权限系统？\|T0321]] · RAG | 4.3-如何基于Spring Security实现RAG-Agent RAG 知识库的RBAC 权限系统？ | 4.3 RAG-Agent：用 Spring Security 实现 RBAC | 把长问句改成动作标题，保留章节号、项目、Spring Security 与 RBAC。 |
| [[AI/RAG/RAG-Agent-项目/5-Go版本/5.2-RAG 项目RAG-Agent Go 版如何通过 Docker 一键部署安装启动\|T0323]] · RAG | 5.2-RAG 项目RAG-Agent Go 版如何通过 Docker 一键部署安装启动 | 5.2 RAG-Agent Go：Docker 一键部署、安装与启动 | 合并两次项目和版本说明，保留 Go、Docker、一键操作以及部署、安装、启动。 |
| [[AI/RAG/RAG-Agent-项目/6-补充篇/6.1-RAG项目的QA，有问题在看这里\|T0324]] · RAG | 6.1-RAG项目的QA，有问题在看这里 | 6.1 RAG 项目问答 | 去掉“有问题在看这里”，保留 QA 的用途和章节号。 |
| [[AI/RAG/RAG-Agent-项目/6-补充篇/6.2-RAG 项目RAG-Agent的学习路线（怎么快速上手 Java+Go 版）\|T0325]] · RAG | 6.2-RAG 项目RAG-Agent的学习路线（怎么快速上手 Java+Go 版） | 6.2 RAG-Agent Java / Go 入门路线 | 压缩重复项目名与括号说明，保留 Java、Go 和快速上手的入门定位。 |
| [[AI/RAG/RAG-Agent-项目/6-补充篇/6.3-es安装\|T0326]] · RAG | ✅Elasticsearch 8.10安装（新人必看） | Elasticsearch 8.10 安装 | 删除装饰图标与“新人必看”，版本完整保留。 |
| [[AI/RAG/RAG-Agent-项目/7-面试篇/7.7-RAG-Agent RAG 真实面经参考，已累计 27 家，700 道题目（不断更新中）\|T0334]] · RAG | 7.7-RAG-Agent RAG 真实面经参考，已累计 27 家，700 道题目（不断更新中） | 7.7 RAG-Agent RAG 真实面经（持续更新） | **副标题/引言：** 已累计 27 家、700 道题目。<br>数量放入副标题，保留真实面经、已累计与持续更新状态，未核验数量现状。 |
| [[KnowledgeBase/sources/effective-html-agent-workflow-summary\|T0731]] · Wiki | Effective HTML Agent 页面制作与 HTML 交付工作流来源摘要 | Effective HTML：Agent 页面制作与交付来源摘要 | 合并重复的 HTML 和工作流标签，保留 Agent 页面制作、交付和来源摘要类型。 |
| [[KnowledgeBase/sources/k8s-installation-management-batch-summary\|T0764]] · Wiki | k8s-installation-management 来源批量摘要 | K8s 安装与管理来源批量摘要 | 把英文目录式长名称改为原有范围的中文表达，保留批量摘要类型。 |
| [[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary\|T0768]] · Wiki | k8s-monitoring-logging 来源批量摘要 | K8s 监控与日志来源批量摘要 | 把目录式长名称换成监控与日志，保留批量范围。 |
| [[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary\|T0769]] · Wiki | k8s-networking-service-mesh 来源批量摘要 | K8s 网络与服务网格来源批量摘要 | 对应现有 networking/service-mesh 两个范围，保留批量摘要类型。 |
| [[KnowledgeBase/sources/k8s-scaling-storage-batch-summary\|T0776]] · Wiki | k8s-scaling 与 k8s-storage 来源批量摘要 | K8s 扩缩容与存储来源批量摘要 | 保留 scaling 和 storage 两个领域，压缩英文目录式名称。 |
| [[KnowledgeBase/sources/kubectl-server-side-apply-summary\|T0781]] · Wiki | kubectl apply 背后的真相：为什么 Server-side Apply 正在成为标配 | kubectl Server-side Apply 来源摘要 | **副标题/引言：** 原文讨论为什么 Server-side Apply 正在成为标配。<br>删除“背后的真相”的悬念；原文的趋势判断留在带归因的副标题。 |
| [[KnowledgeBase/sources/misc-domains-batch-summary\|T0788]] · Wiki | 杂项领域（Database/Middlewares/OS/Networking/IaC/Git/C++/SoftwareTesting）来源批量摘要 | 八个技术领域来源批量摘要 | **副标题/引言：** Database / Middlewares / OS / Networking / IaC / Git / C++ / SoftwareTesting。<br>标题不再嵌入八个目录名；八个领域完整列在副标题和现有元信息中。 |
| [[KnowledgeBase/sources/obsidian-claude-AI知识库完整指南-summary\|T0790]] · Wiki | Obsidian + Claude Code：AI 驱动的知识库完整指南 — 来源摘要 | Obsidian + Claude Code：AI 知识库来源摘要 | 与原文标题精简方案相配，保留两种工具、AI 知识库和来源摘要类型。 |

## 7. 建议保留与另议的情况

| 页面或范围 | 本轮结论 | 理由 |
| --- | --- | --- |
| [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni\|大模型本地部署选型]] | 保留 | 四个 Runtime 名称是比较对象，不把它们当作赘词删除 |
| [[AI/ClaudeCode/多智能体协作-Subagents与Agent-Teams\|Claude Code 多智能体协作]] | 保留 | Subagents 与 Agent Teams 是两个独立机制 |
| [[Azure/4_AKS-SecretProviderClass-KeyVault\|AKS SecretProviderClass 与 KeyVault]] | 保留 | 资源 API 名与平台是有效定位信息 |
| [[Docker-Kubernetes/k8s-installation-management/latest-version/安装k8s-1.35-基于rockylinux10-最新步骤\|Rocky Linux 10 安装 Kubernetes 1.35]] | 保留 | 系统和 Kubernetes 版本均需保留，现题已清楚 |
| [[IaC/terraform/README\|Terraform 学习路线]] 与 15 篇编号正文 | 保留 | 编号、标题与现有学习顺序一致，长度不构成明显问题 |
| 《大话云计算》《深入浅出云计算》《深入剖析 Kubernetes》等书籍/课程名 | 保留 | 不按普通宣传语改动正式名称 |
| 38 份角色/Skill 定义 | 保留 | 标题与功能文件类型、身份或技能标识相关，单独归类审阅 |
| 135 份英文设计参考 | 保留 | 参考范本名称，当前不发布；没有必要统一翻译或机械缩短 |
| 部分 CloudOps-Agent 文章取到“前言”“配置修改”等 H1 | 另议 | 文件名与正文章节标题的问题，不属于长标题精简；当前也未发布 |
| [[AI/企业级私有化大模型/基于docker部署vLLM和LiteLLM私有化大模型\|企业级私有大模型]] | 另议 | 现题较宽泛，问题在定位而非过长 |
| [[Docker-Kubernetes/k8s-installation-management/2025最新-企业级高可用集群-基于rockylinux\|2025 最新高可用集群]]、[[Docker-Kubernetes/k8s-installation-management/legacy-versions/安装k8s-1.33-基于rockylinux-最新步骤\|K8s 1.33 最新步骤]] | 另议 | “最新”依赖时间，不能把旧版本标题直接改成新的版本；本轮未做时效性重写 |

这些文件都列入完整清单；“建议保留”表示标题范围无需本轮调整，并不表示整篇正文已完成事实核查。

## 8. 确认后的修改范围与验收

建议按三组分别选择：26 条直接精简、23 条配合副标题、26 条离线可选。也可按表中编号选择个别条目。用户确认获选条目后，再更新相应标题；确认包含原始来源时，仅授权所选标题字段、对应文章 H1 和本表要求保留的副标题/引言。

1. 按真实标题载体修改；保留文件名、路径和现有主题目录。没有文章 H1 的页面不默认新增一个重复标题。
2. 文章 H1 与 frontmatter 的同步仅限文章标题；技术小节、代码、命令、版本、引用目标保持原样。对旧题承载的独立信息，按已选方案保留。
3. 检查页面链接与标题锚点。文件路径未改时，路径型文章链接继续使用原地址；`LegacyAnchors()` 还会从标题生成锚点，标题变更仍可能影响旧的 `#标题` 外部链接，需要核对并按需保留兼容锚点。
4. 本轮静态找到 12 处明确指向候选文件的章节 wikilink，均为技术小节，没有匹配本次文章主标题。保留这些小节文字；这项检查不覆盖所有 Markdown URL、代码示例或站外书签。
5. 不把旧长标题批量写入 `aliases` 来代替锚点检查：当前 Quartz 的 `AliasRedirects` 会把 aliases 用于重定向路由，含 `/` 等字符的别名还需要检查路径与冲突。
6. 对获选改动进行 YAML、标题取值、引用与差异检查，再本地构建抽查首页、主题列表、搜索、正文和移动端显示。发布结果需在之后的 GitHub Actions/Pages 上观察，报告确认不等于已经发布。

本轮发现的一处候选同名已经处理：原文拟用“K8s 容器设计模式”会与已有来源摘要相同，改为“K8s 四种容器设计模式”，数量来自原题四个模式。按大小写及常见标点归一化比较全库最终候选，没有新增的候选标题同名组；路径也未变化。

## 9. 本轮验收与边界

- 856 个文件均纳入清单且编号唯一，发布清单与直接调用现有 `load_notes()` 的结果一致；YAML 解析没有扫描警告。
- 75 条建议均可对应原文件；49 条网页建议为 26 条直接精简、23 条配合副标题，26 条离线建议为 20 条直接精简、6 条配合副标题。
- 候选标题中的原有阿拉伯数字、版本与百分比在建议主标题和保留说明中全部可定位；另人工核对了作者、平台、组件列表、比较关系、只读/低风险范围和更新状态。
- 全库标题经过逐条审阅，候选再结合引言与相关章节判断。没有逐篇核验全部技术正文，也没有验证原文的性能、趋势和时效性结论。
- 本轮保留原始文章、原标题和文件名；报告归档只影响新增报告/清单以及 INDEX、log 的导航记录。扫描开始时，发布工具和主题存在在途改动；本轮只读取构建器、主题与 workflow 核对行为，文件内容与扫描前一致。
- 在线验证仅包括现有页面的 HTML/标题抽样；尚未执行改题后的构建、移动端视觉验收或部署。当前没有标题变更可供这些验收。
- 本轮由主 Agent 完成审阅与验收；当前工具未提供 GPT-5.1 型号。

相关入口：[[KnowledgeBase/maintenance/title-audit-2026-10-04|完整审阅清单]]、[[AI/Obsidian/github-pages-quartz|Quartz 发布流程]]。

在线抽样入口：[Markdown Viewer](https://hangx969.github.io/learning-notes/AI/AI-%E8%A7%86%E8%A7%89/Markdown-Viewer-Skills-Markdown%E4%B8%AD%E7%9B%B4%E6%8E%A5%E7%94%BB%E5%9B%BE.html)、[CLAUDE.md 规则](https://hangx969.github.io/learning-notes/AI/ClaudeCode/CLAUDE.md%E6%9C%80%E4%BD%B3%E5%AE%9E%E8%B7%B5-12%E6%9D%A1%E8%A7%84%E5%88%99%E6%A8%A1%E6%9D%BF.html)、[Webhook 冲突](https://hangx969.github.io/learning-notes/Docker-Kubernetes/k8s-security-auth/k8s-Admission-Webhook%E9%93%BE%E5%86%B2%E7%AA%81%E6%8E%92%E6%9F%A5-Istio-Kyverno-Gatekeeper.html)。
