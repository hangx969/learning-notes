---
title: Hermes 满配指南来源摘要
tags:
  - knowledgebase/source
  - AI/hermes-agent
date: 2026-05-05
sources:
  - "[[AI/Hermes-agent/Hermes满配指南-五大配置模块]]"
---

# Hermes 满配指南来源摘要

## 元信息

- **原始文档**：[[AI/Hermes-agent/Hermes满配指南-五大配置模块]]
- **原始来源**：[微信公众号文章](https://mp.weixin.qq.com/s/-1CQxvdc1bDMrPzIHFPpbA)
- **领域**：AI Agent 配置
- **摄入日期**：2026-05-05

## 摘要

Hermes Agent 安装后需配置五大模块才能发挥全部能力：(1) SOUL.md 人格定义 + Hindsight 知识图谱记忆替代内置线性 MEMORY；(2) 感知层（Jina Reader/Crawl4AI/Scrapling/CamoFox 网页抓取）；(3) 搜索与文档（Tavily+DuckDuckGo 搜索、Pandoc+Marker 格式转换）；(4) 表达能力（Whisper 语音识别、Edge TTS 合成、Fal.ai/FLUX 图片生成）；(5) Token 精细管控（Tokscale 监控、hermes-hudui 仪表盘、RTK 终端压缩 60-90%、Self-evolution 遗传算法优化提示词）。

## 关键知识点

1. **Hindsight vs 内置 MEMORY**：内置 MEMORY 容量仅 ~2200 字符且只有 Hermes 认为重要时才写入；Hindsight 无硬上限、自动提取实体/事实/关系/时间戳、组织为知识图谱
2. **RTK（Rust Token Killer）**：Rust 编写的零依赖 CLI 代理，智能过滤终端输出，减少 60-90% Token 消耗，`rtk init -g` 一键集成
3. **agency-agents-zh**：211 个中文角色模板 + 46 个中国市场原创智能体，18 个部门分类，每个为独立 `.md` 文件
4. **Hermes-agent-self-evolution**：用 DSPy + GEPA 遗传算法自动优化 Agent 的 Skill、System Prompt、工具描述

## 涉及的概念与实体

- [[KnowledgeBase/entities/Hermes-Agent]]：本文的核心主体
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]]：Hermes 的前身/迁移来源

## 值得注意

- 本文与 [[AI/Hermes-agent/Hermes Agent 资源合集]] 互补——资源合集偏索引，本文偏实操配置
- Hindsight 知识图谱记忆系统是 Hermes 区别于其他 AI Agent 的核心差异化能力之一
- RTK 的终端输出压缩思路可应用于任何 AI 编码助手（Claude Code 等），不限于 Hermes
