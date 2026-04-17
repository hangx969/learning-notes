---
title: Obsidian
tags:
  - knowledgebase/entity
  - ai/knowledge-management
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/obsidian-claude-搭建个人知识库]]"
  - "[[AI/ClaudeCode/Claude Code 扩展体系]]"
---

# Obsidian

## 简介

Obsidian 是一款基于本地 Markdown 文件的知识管理工具，拥有 150 万月活用户。核心优势是数据完全本地化（.md 文件）、双向链接（`[[wikilink]]`）和 Graph View 知识图谱可视化。公司未接受风投，年收入约 2500 万美元，续费率 90%+。

## 核心功能

- **本地存储**：所有笔记就是电脑上的 `.md` 文本文件，不依赖任何云服务
- **双向链接**：笔记间用 `[[wikilink]]` 互相关联，形成知识网络
- **Graph View**：可视化所有笔记的关联关系，发现孤立知识和高频引用
- **插件生态**：社区插件极其丰富，从 Dataview 到 Local REST API

## 与 Claude Code 的集成方案

本仓库记录了 3 个关键集成工具，使 Obsidian 从"笔记工具"升级为"AI 知识库"：

### 1. Claudian 插件

将 Claude Code 嵌入 Obsidian 侧边栏，选中笔记即可让 AI 总结、扩写、找关联。

- GitHub: [YishenTu/claudian](https://github.com/YishenTu/claudian)
- 安装：下载 `main.js`、`manifest.json`、`styles.css` 到 `.obsidian/plugins/claudian/`

### 2. Obsidian Skills

让 Claude Code 理解 Obsidian 特有格式：双向链接、标签、属性、嵌入。包含 3 个核心 Skill：

- **obsidian-markdown**：Obsidian 风格的 Markdown 书写
- **obsidian-bases**：`.base` 类数据库视图（过滤、公式、汇总）
- **json-canvas**：`.canvas` 无限画布文件格式

- GitHub: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills)
- 安装：`/plugin marketplace add kepano/obsidian-skills`

### 3. Local REST API + MCP

Claude Code 直接搜索、读取、创建、修改笔记，无需手动复制粘贴。

- **依赖 1**：Local REST API 插件（Obsidian 插件市场搜索安装）
- **依赖 2**：mcp-obsidian MCP 服务器（`uvx mcp-obsidian`）
- 配置：在 `.claude/settings.json` 中添加 `OBSIDIAN_API_KEY`、`OBSIDIAN_HOST`、`OBSIDIAN_PORT`

## 知识库架构（本仓库实践）

本仓库本身即为 Obsidian Vault，采用 Karpathy LLM Wiki 模式运营：

- **原始来源层**：顶层主题目录（只读）
- **Wiki 编译层**：`KnowledgeBase/` 目录（LLM 维护）
- **Schema 层**：`CLAUDE.md`（人机共同演进）

> 之前的使用门槛（插件、同步、Markdown 语法、方法论如 Zettelkasten/PARA/MOC）曾让人望而却步。Claude Code 生态成熟后，这些门槛大幅降低——你不需要懂那些方法论，Claude Code 替你搞定。

## 相关概念与实体

- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]：通过 Claudian 插件 + MCP 与 Obsidian 深度集成
- [[KnowledgeBase/entities/MCP|MCP]]：mcp-obsidian 实现 AI 操作笔记库

## 在本仓库中的覆盖

- [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]]：3 种集成工具的完整安装配置指南
- [[AI/ClaudeCode/Claude Code 扩展体系]]：Obsidian Skills 的介绍与安装方法

## 知识空白

- Obsidian 插件开发与定制
- 基于 Dataview 的动态知识索引
- Obsidian 与 Git 版本管理的最佳实践
- Obsidian 同步方案对比（Obsidian Sync vs Git vs iCloud）
- Obsidian 模板系统（Templater 插件）的高级用法
