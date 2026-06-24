---
title: CLAUDE.md 完全指南
tags:
  - knowledgebase/source
  - AI/claude-code
date: 2026-06-07
sources:
  - "[[CLAUDE.md最佳实践-12条规则模板]]"
  - "[[CLAUDE.md最佳实践-21条指令清单]]"
  - "[[CLAUDE.md维护工程-四层加载与指令预算]]"
aliases:
  - CLAUDE.md完全指南摘要
---

# CLAUDE.md 完全指南

## 元信息
- **原始文档**：[[AI/ClaudeCode/CLAUDE.md完全指南-规则-指令-维护工程]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-06-07
- **合并来源**：三篇文章合并——Mnilax 12 条规则模板 + Mayank Agarwal 21 条指令清单 + 四层加载与指令预算

## 摘要
CLAUDE.md 一站式参考：写什么（12 条行为规则，错误率从 41% 降到 3%）、怎么写（21 条指令覆盖沟通/行为/上下文/记忆/安全五维度）、怎么管（四层加载体系、指令预算学术依据、rules/ 精准投放、配置体系四角色分工、/init 与 /memory 维护节奏）。含 Anthropic 官方 CLAUDE.md 结构参考和实战模板。

## 关键知识点
1. **四层加载体系**：全局→项目→本地→子目录，越靠近工作目录优先级越高
2. **指令预算**：arXiv 论文实证 500 条指令准确率仅 68%；实测无 CLAUDE.md 错误率 41%、4 条规则降到 11%、12 条降到 3%、超过 18 条合规率崩到 52%
3. **好规则三特征**：一句话写完、Claude 自己推断不出来、有明确行动指导
4. **12 条行为规则**：Karpathy 4 条底线 + Mnilax 8 条补齐（模型只做判断/Token 预算硬限/暴露冲突/先读后写/测试验证意图/检查点/约定胜新奇/显性失败）
5. **21 条指令清单**：沟通方式（1-4）+ 行为准则（5-8）+ 个人上下文（9-11）+ 记忆连续性（12-15）+ 开发者安全网（16-21）
6. **rules/ 目录**：带 paths 前置字段按需加载，核心 CLAUDE.md 控制在 80 行以内
7. **配置体系四角色**：CLAUDE.md=建议 / settings.json=强制 / hooks=自动化 / rules/=精准投放
8. **Anthropic 官方结构**：Commands / What This Is / How It Runs / Key Concepts / Things That Will Bite You / Code Conventions

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code]]

## 值得注意
- 本文合并了三个不同维度的文章：规则内容（写什么）+ 指令格式（怎么写）+ 维护工程（怎么管），形成完整闭环
- 12 条规则中每条都附有真实翻车场景，便于判断哪些规则映射到自己的实际问题
- 源码级加载顺序分析（getMemoryFiles()）和 arXiv 论文引用是独家量化支撑
