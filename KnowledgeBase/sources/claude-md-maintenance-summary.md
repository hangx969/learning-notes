---
title: CLAUDE.md 维护工程
tags:
  - knowledgebase/source
  - AI/claude-code
date: 2026-06-07
sources:
  - "[[AI/ClaudeCode/CLAUDE.md维护工程-四层加载与指令预算]]"
aliases:
  - CLAUDE.md维护摘要
---

# CLAUDE.md 维护工程

## 元信息
- **原始文档**：[[AI/ClaudeCode/CLAUDE.md维护工程-四层加载与指令预算]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-06-07

## 摘要
系统讲解 CLAUDE.md 的维护工程——从四层加载体系（全局→项目→本地→子目录）到 LLM 指令预算（arXiv 论文实证 500 条指令准确率仅 68%），再到 rules/ 目录精准投放、@path 语法、/init vs /memory 分工、配置体系四角色（CLAUDE.md 建议/settings.json 强制/hooks 自动化/rules/ 精准投放）。含源码级加载顺序分析和 Anthropic 官方 CLAUDE.md 结构参考。

## 关键知识点
1. **四层加载体系**：全局 `~/.claude/CLAUDE.md` → 项目 `CLAUDE.md` → 本地 `CLAUDE.local.md` → 子目录 CLAUDE.md（按需加载），越靠近工作目录优先级越高
2. **指令预算**：arXiv 论文实证 500 条指令准确率仅 68%，瓶颈不是上下文窗口而是注意力分配；CLAUDE.md 内容叠加在系统提示之上，有效空间有限
3. **好规则三特征**：一句话写完、Claude 自己推断不出来、有明确行动指导
4. **rules/ 目录**：带 `paths` 前置字段的规则文件只在操作匹配路径时加载，节省指令预算；核心 CLAUDE.md 控制在 80 行以内
5. **配置体系四角色分工**：CLAUDE.md 管建议、settings.json 管强制、hooks 管自动化、rules/ 管精准投放
6. **/init 冷启动 + /memory 热更新**：CLAUDE.md 放团队共享长期规则，memory 放个人日常积累经验，定期从 memory 提炼通用规则到 CLAUDE.md
7. **Anthropic 官方结构**：Commands / What This Is / How It Runs / Key Concepts / Things That Will Bite You / Code Conventions

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code]]

## 值得注意
- 与已有 `CLAUDE.md最佳实践-12条规则模板.md`（具体规则内容）和 `21条指令清单.md`（拿来即用的指令）定位不同——本文讲的是**维护方法论和架构设计**
- 源码级的加载顺序分析（`getMemoryFiles()` 函数）是独家内容
- 指令预算的学术依据（arXiv 2507.11538）为"CLAUDE.md 要精简"提供了量化支撑
