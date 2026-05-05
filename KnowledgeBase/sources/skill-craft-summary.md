---
title: Skill Craft 来源摘要
tags:
  - knowledgebase/source
  - AI/claude-code
date: 2026-05-05
sources:
  - "[[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft]]"
aliases:
  - Skill Craft摘要
---

# Skill Craft 来源摘要

## 元信息
- **原始文档**：[[AI/ClaudeCode/Claude-Skill质检工具-SkillCraft]]
- **领域**：AI / Claude Code Skills 质量工程
- **摄入日期**：2026-05-05

## 摘要
Skill Craft 是面向 Claude Skill 的质量工程工具，解决 Skill 在真实场景中"不触发、乱触发、越用越跑偏"的问题。作者总结了 LLM Skill 的 7 类系统性失效模式，设计了三层评估体系（8 结构模块 + 7 反模式风险 + 3 完整性原则），提供 check/fix/create/audit 四种模式覆盖 Skill 的完整生命周期。

## 关键知识点
1. **7 类失效模式**：约束衰减、工具选择漂移、输出膨胀、依赖链断裂、并行孤岛、触发模糊、幻觉填充——它们会连锁触发（输出膨胀→上下文耗尽→约束衰减→工具漂移+幻觉填充）
2. **三层评估体系**：第一层 8 个结构模块（触发条件/行为准则/工具优先级/输出约束/流程 Checkpoint/依赖链/子 Agent 委派/幻觉防护）；第二层 7 类反模式风险覆盖；第三层 3 条完整性原则（可计数验收、Checkpoint 阻断、失败路径定义）
3. **fix 模式核心**：评估→问题清单→优先级修复→回归验证（重新评估分数/风险/结构闭环），附带四类关联检查（引用方/对称方/消费方/同层相似）
4. **create 模式**：根据复杂度自动选择模块，内置 `validate-metadata.py` 和 `validate-structure.py` 冒烟检查脚本
5. **audit 模式**：系统级多 Skill 治理，关注路由边界重叠、职责分工、真值源统一、外围文档传播

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude Code]]

## 值得注意
- "失败路径定义"原则极具实践价值：没写 else，模型默认的 else 往往就是 skip。这一洞察适用于所有 LLM 指令设计
- 连锁反应分析（输出膨胀→约束衰减→工具漂移+幻觉填充）为 Skill 质量退化提供了系统性解释
- 四类关联检查解决了"修了一处但遗漏三处"的工程维护难题
