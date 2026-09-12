---
title: Codex
tags:
  - knowledgebase/entity
  - ai/codex
date: 2026-09-12
sources:
  - "[[AI/Codex/Codex-Harness架构-任务循环与扩展]]"
  - "[[AI/Codex/Codex-config-toml-全量配置参考]]"
  - "[[AI/Codex/Codex-省Token工具实测-Ponytail-Headroom-RTK]]"
  - "[[AI/Codex/Codex-两个设置提升体验]]"
  - "[[AI/Code review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理]]"
  - "[[AI/AI-视觉/Effective-HTML-Agent页面工作流]]"
  - "[[AI/AI-视觉/effective-html-AI直出HTML工具实测]]"
aliases:
  - OpenAI Codex
---

# Codex

## 简介
Codex 是面向软件工程任务的 AI 编程助手。本仓库覆盖其 `config.toml` 配置、Harness 任务循环与工具执行、减少无效 Token 消耗的工作流，以及在普通模式中进行需求澄清的实践。

## 核心功能
- **配置与权限控制**：通过 `config.toml` 设置模型、推理强度、审批与沙箱、MCP、Hooks、Skills 等运行参数。
- **交互式任务执行**：可在执行前或过程中澄清需求；`default_mode_request_user_input` 可将该能力扩展到普通模式（以当前版本支持为准）。
- **Harness 运行架构**：在模型外组织 App Server、Session、上下文、工具路由与执行、状态持久化和长期记忆，驱动“请求模型—执行动作—反馈—继续判断”的 Agent 闭环。
- **上下文与状态管理**：通过 Thread/Turn/Item/Session 组织任务状态，用 StepContext 固定单次请求的模型设置、环境视图、工具路由和项目规则；上下文压缩服务于当前任务，不等于长期记忆。
- **工作流优化**：借助约束、Skills 与 Hooks 减少不必要的工具调用和输出；重要结果仍须用测试与审查验证。
- **视觉交付**：可通过 Effective HTML Skills 先确定页面结构，再生成交互式、自包含的 HTML 报告、架构图或计划页。
- **代码审查与验证**：检查改动风险，并通过项目测试、真实场景和对抗式用例验证审查结论。

## 使用场景
- 将项目级规范、权限边界和外部工具接入 Codex 的开发环境。
- 面对复杂或歧义需求时，先收集用户选择和验收标准，再实施修改。
- 需要控制上下文与执行成本的长任务。
- 分析 Agent 如何通过审批、沙箱、并发和长进程工具完成多步骤软件工程任务。

## 相关概念与实体
- 提示词工程：通过结构化指令和澄清降低任务歧义。
- [[KnowledgeBase/entities/Claude-Code|Claude Code]]：同属 AI 编程助手，可比较其交互与扩展机制。
- [[KnowledgeBase/entities/MCP|MCP]]：Codex 可配置接入的外部工具协议。

## 在本仓库中的覆盖
- [[AI/Codex/Codex-Harness架构-任务循环与扩展]]：从 App Server、Session 和 Agent 主循环，到上下文、工具执行、持久化记忆及 Skills/MCP/Hooks/子 Agent 扩展。
- [[KnowledgeBase/sources/codex-harness-architecture-summary|Codex Harness 架构来源摘要]]：文章的结构化知识点与版本边界说明。
- [[AI/Codex/Codex-config-toml-全量配置参考]]：覆盖配置字段、特性开关、权限、MCP、Hooks 和 Agents。
- [[AI/Codex/Codex-省Token工具实测-Ponytail-Headroom-RTK]]：讨论通过工具与约束减少 Token 消耗的实践。
- [[AI/Codex/Codex-两个设置提升体验]]：记录普通模式主动澄清配置与 Juice 提示的经验性自检方式。
- [[AI/Code review和知识图谱/AI代码审查闭环-验证优先与敏感信息清理]]：记录完整仓库上下文、真实运行验证、安全扫描和发布前敏感信息清理的审查闭环。
- [[AI/AI-视觉/Effective-HTML-Agent页面工作流]]：Effective HTML 的页面制作工作流，以及 Codex 插件安装方式。
- [[KnowledgeBase/sources/effective-html-agent-workflow-summary|Effective HTML 来源摘要]]：HTML 直出、自包含交付、交互式图表和 Markdown 的适用边界。

## 知识空白
- 不同 Codex 版本中各配置项的支持范围与默认值。
- 主动澄清设置对任务完成率、返工率的可复现效果。
- Juice 提示与实际任务质量之间是否存在可验证关联。
