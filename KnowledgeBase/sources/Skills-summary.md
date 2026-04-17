---
title: Skills
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/Skills]]"
---

# Skills

## 元信息
- **原始文档**：[[AI/ClaudeCode/Skills]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要
Skills 是 Claude Code 于 2025 年 10 月发布的自动触发能力包，采用渐进式加载设计（初始仅加载元数据，按需加载完整指令）。文档详细介绍了 Skill 的三层能力递进（单点自动化 → 编排工作流 → 团队智能），并通过 smart-code-review 和 incident-response 两个典型案例展示了实际效果，还涵盖了版本治理、安装方式和 Obsidian 相关 Skills。

## 关键知识点
1. Skills 是自动触发的能力包，2025 年 10 月发布
2. 与 MCP 的区别：Skills 范围更广，可调用 MCP，可包含 Python 脚本
3. 能力递进公式："单个 Skill = 能力；多个 Skill 编排 = 工作流；Skill + MCP + SubAgent = 智能体"
4. 渐进式加载设计：初始仅加载元数据（名称+描述，约数十 token），触发时按需加载完整指令，复杂 Skill 拆分为模块
5. Skill 文件夹结构：SKILL.md（核心，YAML 元数据 + Markdown 指令）、scripts/、references/、assets/
6. 存储位置：个人级（~/.claude/skills/）、项目级（.claude/skills/）
7. 安装方式：手动创建、Marketplace（/plugin marketplace）、打包 .skill 文件
8. 三层能力递进：
   - 第一层：工程单点自动化（pre-commit-check、smart-code-review、dependency-upgrade-check）
   - 第二层：参数化编排工作流（incident-response 含并行阶段）
   - 第三层：知识积累的团队智能（tech-debt-tracker 集成 SonarQube）
9. smart-code-review：自动检测文件类型 → 选择检查项 → 调用专项 SubAgent → 生成分级报告。"团队生产事故下降 60%"
10. incident-response：四阶段（并行分诊 → 根因分析 → 3 套缓解方案 → 确认后执行）。"MTTR 从 45 分钟降至 12 分钟"
11. 版本治理：像代码一样管理 Skill 版本，支持 A/B 测试和回滚
12. skill-creator：Anthropic 官方 Skill，用于辅助创建其他 Skills
13. Obsidian 相关 Skills：obsidian-markdown、obsidian-bases、json-canvas

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/Obsidian|Obsidian]]

## 值得注意
- 渐进式加载是关键设计——避免大量 Skills 占满上下文窗口，初始仅消耗数十 token
- "团队生产事故下降 60%"和"MTTR 从 45 分钟降至 12 分钟"是极具说服力的量化成果
- 三层递进模型清晰地展示了从工具到智能体的演进路径
- skill-creator 体现了"用 AI 构建 AI 工具"的自举思想
- Skills 与 MCP 的关系是包含而非替代——Skill 可以调用 MCP，但 MCP 不能调用 Skill
