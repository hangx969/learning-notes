---
title: Codex
tags:
  - knowledgebase/entity
  - ai/codex
date: 2026-09-05
sources:
  - "[[AI/Codex/Codex-config-toml-全量配置参考]]"
  - "[[AI/Codex/Codex-省Token工具实测-Ponytail-Headroom-RTK]]"
  - "[[AI/Codex/Codex-两个设置提升体验]]"
  - "[[0raw/在 Codex 里随时切换不同厂家的 Harness]]"
aliases:
  - OpenAI Codex
---

# Codex

## 简介
Codex 是面向软件工程任务的 AI 编程助手。本仓库覆盖其 `config.toml` 配置、减少无效 Token 消耗的工作流，以及在普通模式中进行需求澄清的实践。

## 核心功能
- **配置与权限控制**：通过 `config.toml` 设置模型、推理强度、审批与沙箱、MCP、Hooks、Skills 等运行参数。
- **交互式任务执行**：可在执行前或过程中澄清需求；`default_mode_request_user_input` 可将该能力扩展到普通模式（以当前版本支持为准）。
- **工作流优化**：借助约束、Skills 与 Hooks 减少不必要的工具调用和输出；重要结果仍须用测试与审查验证。

## 使用场景
- 将项目级规范、权限边界和外部工具接入 Codex 的开发环境。
- 面对复杂或歧义需求时，先收集用户选择和验收标准，再实施修改。
- 需要控制上下文与执行成本的长任务。

## 相关概念与实体
- 提示词工程：通过结构化指令和澄清降低任务歧义。
- [[KnowledgeBase/entities/Claude-Code|Claude Code]]：同属 AI 编程助手，可比较其交互与扩展机制。
- [[KnowledgeBase/entities/MCP|MCP]]：Codex 可配置接入的外部工具协议。

## 在本仓库中的覆盖
- [[AI/Codex/Codex-config-toml-全量配置参考]]：覆盖配置字段、特性开关、权限、MCP、Hooks 和 Agents。
- [[AI/Codex/Codex-省Token工具实测-Ponytail-Headroom-RTK]]：讨论通过工具与约束减少 Token 消耗的实践。
- [[AI/Codex/Codex-两个设置提升体验]]：记录普通模式主动澄清配置与 Juice 提示的经验性自检方式。
- [[0raw/在 Codex 里随时切换不同厂家的 Harness]]：介绍以 `codex-host` 将多个厂商 Harness 接入 Codex 的设想；兼容性与支持范围尚待验证。

## 知识空白
- 不同 Codex 版本中各配置项的支持范围与默认值。
- 主动澄清设置对任务完成率、返工率的可复现效果。
- Juice 提示与实际任务质量之间是否存在可验证关联。
