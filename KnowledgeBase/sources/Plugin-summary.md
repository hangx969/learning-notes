---
title: Plugin
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/Plugin]]"
---

# Plugin

## 元信息
- **原始文档**：[[AI/ClaudeCode/Plugin]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要
Plugin 是 Claude Code 的应用级打包容器，能将 Skills、Slash Commands、MCP 配置、SubAgent 定义和 Hooks 捆绑为一个可分发单元。文档阐述了 Plugin 的两大用途（团队标准化分发与快速试用功能）、使用限制以及个人与团队场景下的最佳实践。

## 关键知识点
1. Plugin 是应用级打包容器，可捆绑其他工具类型
2. 单个 Plugin 可包含：5 个 Skills、10 个 Slash Commands、3 个 MCP 配置、2 个 SubAgent 定义，外加 Hooks
3. 两大用途：团队标准化（打包并共享工作流）和快速试用功能
4. 缺点：插件过多会导致卡顿，且大部分功能存在重叠
5. 最佳实践：个人使用全局配置，团队使用 Plugin 分发；不超过 3 个插件

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]

## 值得注意
- Plugin 的价值主要体现在团队场景——个人用户直接用全局配置更简洁
- "不超过 3 个插件"的硬性建议说明当前 Plugin 系统的性能开销仍然显著
- Plugin 本质上是一个分发机制而非能力机制——它不创造新能力，只是打包已有能力
