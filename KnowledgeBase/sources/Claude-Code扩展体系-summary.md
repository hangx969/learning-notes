---
title: Claude Code 扩展体系
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/Claude Code 扩展体系]]"
---

# Claude Code 扩展体系

## 元信息
- **原始文档**：[[AI/ClaudeCode/Claude Code 扩展体系]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17
- **合并来源**：原 MCP.md、Skills.md、Slash Command.md、Plugin.md 四篇合并而成

## 摘要
系统性整理了 Claude Code 的四层扩展机制：MCP（外部工具桥梁，10+ 服务器配置与场景组合）、Skills（自动触发能力包，渐进式加载设计，3 层使用模式）、Slash Commands（手动触发工作流快捷方式）、Plugin（应用级打包分发容器）。四层机制各有定位——MCP 是"手"，Skills 是"肌肉记忆"，Slash Commands 是"快捷键"，Plugin 是"安装包"——组合构成可编排、可沉淀、可分发的智能工作流系统。

## 关键知识点

### MCP（Model Context Protocol）
1. Client（Claude Code）↔ Server（MCP 进程）通过 stdio 通信，安装方式为 CLI 命令或 JSON 配置
2. 必装三件套：memory（跨会话记忆）、context7（实时文档查询）、sequential-thinking（结构化推理链）
3. 10+ MCP 服务器：atlassian、bitbucket、github、filesystem、playwright、exa、deepwiki、drawio 等
4. 场景组合：日常开发（filesystem+github+memory）、深度工作（sequential-thinking+context7+memory）、自动化（playwright+filesystem）、学习（context7+deepwiki+exa）
5. exa 的 Neural Search 能力支持语义搜索、结构化数据返回、域名/日期过滤、内容相似推荐
6. drawio 支持 Mermaid/CSV/XML 三种模式生成可编辑的 Draw.io 图表

### Skills（技能）
7. 2025 年 10 月发布的自动触发能力包，核心设计为渐进式加载（初始仅加载元数据约数十 token）
8. Skill 文件夹结构：SKILL.md（核心）+ scripts/ + references/ + assets/
9. 三层能力递进：单点自动化 → 编排工作流 → 团队智能体
10. smart-code-review：按文件类型分派专项 SubAgent 审查，"团队生产事故率下降 60%"
11. incident-response：四阶段（并行分诊→根因分析→3 套缓解方案→确认执行），"MTTR 从 45 分降至 12 分"
12. 安装方式：手动创建、Marketplace、打包 .skill 文件分享
13. Obsidian 相关 Skills：obsidian-markdown、obsidian-bases、json-canvas

### Slash Commands（斜杠命令）
14. 手动触发的工作流快捷方式，存储在 `.claude/commands/`，纯 Markdown 定义
15. 与 Skills 的核心区别：注入为 user message（非 system prompt），手动触发（非自动）
16. 典型场景：/release、/security-check、/perf-audit、/refactor-plan、/onboard、/rollback
17. /release 效果："版本发布错误率从 15% 降至 0"

### Plugin（插件）
18. 应用级打包容器：最多 5 Skills + 10 Slash Commands + 3 MCP + 2 SubAgents + Hooks
19. 适合团队标准化分发，个人用全局配置更简洁
20. 建议不超过 3 个插件，避免启动卡顿和功能重复

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/MCP|MCP]]
- [[KnowledgeBase/entities/Obsidian|Obsidian]]

## 值得注意
- 四层机制的定位清晰：MCP 操作外部世界、Skills 自动响应、Slash Commands 手动触发固定流程、Plugin 打包分发
- 渐进式加载是 Skills 高效的核心——支持安装上百个 Skills 却不占用上下文
- "单个 Skill = 能力 → 多个 Skill 编排 = 工作流 → Skill + MCP + SubAgent = 智能体"是理解扩展体系的关键公式
- Skills 与 MCP 的关系是包含而非替代——Skill 可调用 MCP，但 MCP 不能调用 Skill
- Plugin 本质是分发机制而非能力机制——不创造新能力，只打包已有能力
