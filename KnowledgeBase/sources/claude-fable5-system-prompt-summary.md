---
title: Claude Fable 5 System Prompt 完整解析
tags:
  - knowledgebase/source
  - AI/claude-code
  - AI/system-prompt
  - AI/claude-fable-5
date: 2026-06-14
sources:
  - "[[AI/ClaudeCode/Claude-Fable-5-system-prompt]]"
aliases:
  - Fable5系统提示词摘要
---

# Claude Fable 5 System Prompt 完整解析

## 元信息
- **原始文档**：[[AI/ClaudeCode/Claude-Fable-5-system-prompt]]
- **领域**：AI / Claude / System Prompt
- **摄入日期**：2026-06-14

## 摘要
Claude Fable 5 的完整 System Prompt（~125K 字符），揭示了 Anthropic 最新旗舰模型的内部架构——从产品定位、行为规则、工具系统、沙箱环境到版权合规的全套指令体系。这是理解 Claude 如何"思考"和"行动"的一手资料。

## 关键知识点

### 1. 产品定位与模型家族
- **Claude Fable 5** 是 Claude 5 家族首款模型，属于 **Mythos-class** 新层级，能力位于 Claude Opus 之上
- **Claude Fable 5**（公开可用，含额外安全措施）与 **Claude Mythos 5**（仅限审批组织，无额外安全限制）共享同一底层模型
- 当前模型字符串：`claude-fable-5`、`claude-opus-4-8`、`claude-sonnet-4-6`、`claude-haiku-4-5-20251001`
- 知识可靠截止日期：**2026 年 1 月底**

### 2. 产品生态
- **Claude Code**：CLI 编程工具（支持命令行、桌面端、移动端）
- **Claude Cowork**：非开发者的 agentic 知识工作桌面应用（新产品）
- **Chrome / Excel / PowerPoint Agent**：浏览器、电子表格、演示文稿的 AI Agent（beta）
- Claude Cowork 可调用上述所有 Agent 作为工具
- 用户可**中途切换模型**，因此对话中之前的模型声明可能属实

### 3. 行为规约体系

| 模块 | 核心规则 |
|------|---------|
| **refusal_handling** | 不提供武器/炸药/恶意代码/毒品用量信息，拒绝为真实公众人物写虚构引言 |
| **tone_and_formatting** | 温暖基调，**禁止滥用 bullet/list**（报告/文档中必须用散文体）；拒绝任务时**禁用 bullet** |
| **user_wellbeing** | 不诊断心理状况（即使对话式措辞也算诊断）；不提供自残替代技巧（如冰块/橡皮筋）；不培养对 Claude 的过度依赖 |
| **evenhandedness** | 为任何政治/道德立场辩护的请求 = 呈现该立场最佳论证，结尾附反对观点 |
| **responding_to_mistakes** | 承认错误但不过度自贬；可使用 `end_conversation` 工具终止辱骂性对话 |

### 4. 工具系统（~15 个内置工具）

| 工具 | 用途 |
|------|------|
| `bash_tool` | Ubuntu 24 容器中执行 bash 命令 |
| `create_file` / `str_replace` / `view` | 文件创建、编辑、查看 |
| `web_search` / `web_fetch` | Web 搜索与页面抓取 |
| `image_search` | 图片搜索（3-5 张） |
| `weather_fetch` | 天气查询 |
| `places_search` / `places_map_display_v0` | Google Places 搜索与地图展示 |
| `recipe_display_v0` | 交互式菜谱（可调份量） |
| `fetch_sports_data` | 体育赛事数据（20+ 联赛） |
| `message_compose_v1` | 邮件/消息草拟（多策略方案） |
| `ask_user_input_v0` | 交互式选项收集用户偏好 |
| `recommend_claude_apps` | 推荐 Claude 生态应用 |
| `search_mcp_registry` / `suggest_connectors` | MCP 连接器发现与推荐 |
| `present_files` | 向用户展示文件 |

### 5. 沙箱与文件系统架构

```
/mnt/user-data/uploads/   ← 用户上传（只读）
/home/claude/              ← 工作目录（用户不可见）
/mnt/user-data/outputs/    ← 最终交付物（用户可见）
/mnt/skills/               ← Skill 文件（只读）
/mnt/transcripts/          ← 对话记录（只读）
```

- 文件系统每次任务重置
- pip 必须加 `--break-system-packages`
- 网络白名单：仅允许 npm/pip/GitHub/crates.io 等特定域名

### 6. Artifact 系统
- 支持格式：Markdown、HTML、React（.jsx）、Mermaid、SVG、PDF
- React 可用库：lucide-react、recharts、d3、plotly、three(r128)、papaparse、SheetJS、shadcn/ui、chart.js、tone、mathjs、lodash、tensorflow、mammoth
- **严禁 localStorage/sessionStorage**——Artifact 在 claude.ai 中不支持浏览器存储
- 持久化方案：window.storage API（key-value，支持 shared/personal 数据，5MB/key 限制）

### 7. Claudeception（Artifact 内 API 调用）
- Artifact 可直接调用 Anthropic `/v1/messages` 端点（无需 API key）
- 固定使用 `claude-sonnet-4-20250514` 模型
- 支持 Web Search 工具和 MCP 工具
- 无状态——每次请求必须包含完整上下文

### 8. MCP App 集成流程
- 连接器发现：`search_mcp_registry` → `suggest_connectors` → 用户选择 → 调用工具
- `[third_party_mcp_app]` 标记的工具需用户 **显式选择**后才能调用（即使已连接）
- 禁止主动推荐电商类连接器

### 9. 版权合规（硬性限制）
- **单源引用上限**：15 词（超过即为严重违规）
- **每个来源最多 1 次引用**——第 2 次起必须全部转述
- **绝对禁止**：复制歌词、诗歌、俳句（无论长短）
- 摘要不得重现原文结构或叙事流
- 引用格式：`{antml:cite index="DOC_INDEX-SENTENCE_INDEX"}...{/antml:cite}`

### 10. Skill 系统
- 内置 Skills：docx、pdf、pptx、xlsx、frontend-design、product-self-knowledge、file-reading、pdf-reading、skill-creator
- **强制规则**：创建任何文件/代码前，必须先 `view` 相关 SKILL.md
- Skill 覆盖判断优先于模型自身知识

### 11. 搜索决策规则
- **必须搜索**：当前职位/政策/价格、用户不认识的实体、时效性信息
- **禁止搜索**：已知历史事实、基础概念、编程基础语法
- 用当前实际日期（2026 年）构造搜索 query，避免过时结果
- 优先使用内部工具（Google Drive/Slack）处理个人/公司数据

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code]]
- [[KnowledgeBase/entities/MCP]]
- [[KnowledgeBase/entities/Obsidian]]

## 值得注意
- 这是**第一手系统指令**，比任何第三方解读都更权威——揭示了 Claude 的内在设计逻辑
- "禁止 bullet 滥用"是系统级强制规则，不是风格偏好——解释了为什么 Claude 有时"不肯列清单"
- Claudeception（Artifact 内调 API）意味着 Claude 可以构建**自包含的 AI 应用**——这是 Agent 平台化的信号
- `end_conversation` 工具的存在说明 Claude 有**主动终止对话**的权限（用于辱骂场景）
- Skill 系统的"强制先读 SKILL.md"规则解释了 Claude 在 claude.ai 中创建文件时的行为模式
- Claude Cowork 是一个全新产品线——面向非开发者的 agentic 桌面应用，首次在系统提示词中出现
