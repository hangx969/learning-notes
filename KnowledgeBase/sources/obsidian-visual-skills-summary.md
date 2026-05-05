---
title: Obsidian 可视化 Skills 来源摘要
tags:
  - knowledgebase/source
  - ai/obsidian
  - ai/skills
date: 2026-05-05
sources:
  - "[[AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas]]"
---

# Obsidian 可视化 Skills 来源摘要

## 元信息

- **原始文档**：[[AI/Obsidian/Obsidian可视化Skills-Excalidraw-Mermaid-Canvas]]
- **原始来源**：[微信公众号文章](https://mp.weixin.qq.com/s/EbNkKTGkp2WnqJ0nKNBwmA)
- **领域**：AI / Obsidian / 可视化
- **摄入日期**：2026-05-05

## 摘要

介绍 axton-obsidian-visual-skills 开源项目，通过 AI Skills 机制让大模型在 Obsidian 中直接生成可编辑的图表文件（非静态图片）。支持 Excalidraw（手绘风格）、Mermaid（专业流程图）、Canvas（自由画布）三种格式，底层均为 JSON 结构化数据。兼容 Claude Code、Gemini CLI、Codex 三种 AI 工具。

## 关键知识点

1. Skills 本质是预设的 Markdown 提示词文件，让 AI 按特定规则和格式完成任务
2. 三种图表格式均基于 JSON 代码，生成后可自由编辑（调整布局、修改文字、增删元素）
3. 安装方式简单：`git clone` 项目后将三个 skills 目录复制到 `~/.claude/skills/`（或对应工具目录）
4. 使用时用自然语言描述需求即可，AI 自动读取笔记 → 理解结构 → 生成图表文件

## 涉及的概念与实体

- [[KnowledgeBase/entities/Obsidian]]：图表生成的目标平台
- [[KnowledgeBase/entities/Claude-Code]]：兼容的 AI 工具之一，Skills 存放在 `~/.claude/skills/`

## 值得注意

- 这是一个将 AI Skills 概念应用于 Obsidian 可视化场景的实际案例，与 [[AI/ClaudeCode/Claude Code 扩展体系]] 中的 Skills 机制属同一范畴
- 解决了此前 AI 生成图表只能输出静态图片、不可编辑的痛点
