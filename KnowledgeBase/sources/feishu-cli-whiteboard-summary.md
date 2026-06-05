---
title: 飞书 CLI 画板生成能力
tags:
  - knowledgebase/source
  - AI/tools
  - feishu
date: 2026-06-05
sources:
  - "[[AI/OpenClaw/飞书CLI画板-一句话生成架构图]]"
aliases:
  - 飞书CLI画板摘要
---

# 飞书 CLI 画板生成能力

## 元信息
- **原始文档**：[[AI/OpenClaw/飞书CLI画板-一句话生成架构图]]
- **领域**：AI 工具 / 效率提升
- **摄入日期**：2026-06-05

## 摘要
飞书 CLI 新增画板生成能力，AI Agent（Codex、Claude Code、OpenClaw）可通过自然语言一句话生成可编辑的飞书画板。生成的是原生飞书画板对象而非截图，支持节点编辑、拖拽调整、AI 对话迭代修改，且可直接嵌入飞书文档。

## 关键知识点
1. 飞书 CLI 画板生成的核心优势是**可编辑性**——不是截图，是原生画板，节点/连线/文字都可独立修改
2. 支持多种结构化图表：架构图、流程图、思维导图、甘特图、泳道图、组织架构图、系统交互图
3. 安装命令：`npx @larksuite/cli@latest install`，也可通过飞书 aily 内置直接使用
4. 配套开源风格 Skill（[feishu-whiteboard-themes](https://github.com/inhai-wiki/feishu-whiteboard-themes)）可根据图表类型自动匹配视觉风格
5. 修改方式灵活：手动双击编辑 + AI 对话式修改，需求变更后几秒即可更新

## 涉及的概念与实体
- [[KnowledgeBase/entities/OpenClaw]]
- [[KnowledgeBase/entities/Claude-Code]]

## 值得注意
- 这是飞书 CLI 作为 MCP 工具生态的延伸——画板能力可被各类 AI Agent 直接调用，实现"AI 生图 → 飞书沉淀 → 人工微调"的闭环工作流
- 对比传统 AI 生图（Mermaid/Excalidraw），飞书画板的优势在于**企业协作场景**：画板与文档一体化、多人可编辑、版本跟随文档沉淀
