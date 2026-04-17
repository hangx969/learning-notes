---
title: ClaudeCode基础指南
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/ClaudeCode基础指南]]"
---

# ClaudeCode基础指南

## 元信息
- **原始文档**：[[AI/ClaudeCode/ClaudeCode基础指南]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要
Claude Code 的全面入门与进阶指南，涵盖单项目原则、三种操作模式（Normal/Plan/Auto-accept）、Extended Thinking 分级触发词、Claude.md 备忘机制以及 Spec 工作流。文档还介绍了三大核心能力（Plugin、SubAgent、MCP）并演示了五个实战场景，最终给出最佳实践建议。

## 关键知识点
1. 单项目原则：CC 应从具体项目文件夹启动，不要在多项目父目录运行
2. 三种模式：Normal（正常执行）、Plan（仅讨论不写代码）、Auto-accept（自动执行）
3. 推荐工作流：先 Plan 模式讨论 → 确认方案 → 切换 Normal/Auto 执行
4. Extended Thinking 分级："think" < "think hard" < "think harder" < "ultrathink"，逐级增加思考预算
5. Claude.md：用户与 CC 之间的备忘文件，分为 user-level（全局）和 project-level（项目级），通过 /init 或 # memory 创建
6. Spec 工作流四步：需求文档 → 技术文档 → TODO 文档 → 合并为 spec.md → 执行实现
7. Spec 解决了上下文丢失问题——文档在会话之间保留完整上下文
8. 三大核心能力：Plugin 系统、SubAgent、MCP
9. 五个实战场景：微服务决策、事故响应、遗留项目接管、新功能开发、技术栈升级
10. 最佳实践：从 3 个 MCP（memory、context7、sequential-thinking）、3 个 Skills 起步，设计团队工作流 Playbook
11. "好的工具链会自己长知识"——强调工具链的知识积累效应

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/MCP|MCP]]

## 值得注意
- Plan 模式是降低风险的关键入口——先讨论再执行，避免 AI 盲目修改代码
- Extended Thinking 的分级触发词设计直观，允许用户按需调整 AI 思考深度
- Spec 工作流本质上是将"人脑上下文"外化为文档，使 AI 协作具备可持续性
- "好的工具链会自己长知识"这一观点揭示了 Claude Code 生态的核心价值——工具不只是执行器，还是知识载体
