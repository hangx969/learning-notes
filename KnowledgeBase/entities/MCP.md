---
title: MCP
tags:
  - knowledgebase/entity
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/Claude Code 扩展体系]]"
  - "[[AI/ClaudeCode/ClaudeCode基础指南]]"
  - "[[AI/ClaudeCode/obsidian-claude-搭建个人知识库]]"
---

# MCP

## 简介

Model Context Protocol（模型上下文协议）是连接 AI 模型与外部工具、数据源的标准化桥梁协议。通过 MCP Server，AI 助手（如 Claude Code）可以调用文件系统、数据库、API、浏览器等外部资源，实现工具增强的智能交互。MCP 采用 stdio 通信方式，服务器通过 `npx` 或 `docker` 启动。

## 核心机制

- **协议模型**：Client（Claude Code）↔ Server（MCP 进程），通过 stdio 通信
- **安装方式**：`claude mcp add <name> -- <command>` 或在 JSON 配置文件中声明
- **配置位置**：用户全局 `~/.claude/settings.json` 或项目级 `.claude/settings.json`
- **安全控制**：如 filesystem MCP 需指定允许访问的路径，避免权限过大

## 已记录的 MCP 服务器

### 必装三件套

| 服务器 | 用途 | 安装方式 |
|--------|------|---------|
| **memory** | 跨会话持久化记忆，记住团队规范、踩过的坑、架构决策 | `npx -y @modelcontextprotocol/server-memory` |
| **context7** | 实时拉取最新框架文档（Next.js、React 19），避免训练数据过时 | `npx -y @upstash/context7-mcp --api-key ""` |
| **sequential-thinking** | 结构化多步推理，输出完整推理链：假设→验证→排除→聚焦→结论 | `npx -y mcp-sequentialthinking-tools` |

### 开发与协作类

| 服务器 | 用途 | 安装方式 |
|--------|------|---------|
| **atlassian** | Jira + Confluence 集成，需配置 URL/用户名/Token | Docker 容器 `ghcr.io/sooperset/mcp-atlassian:latest` |
| **bitbucket** | 代码仓库操作（PR、代码搜索） | `npx -y @zhanglc77/bitbucket-mcp-server` |
| **github** | GitHub API 集成，需 `GITHUB_PERSONAL_ACCESS_TOKEN` | `npx -y @modelcontextprotocol/server-github` |
| **filesystem** | 本地文件读写操作 | `npx -y @modelcontextprotocol/server-filesystem /path` |

### 搜索与文档类

| 服务器 | 用途 | 特点 |
|--------|------|------|
| **exa** | AI 语义搜索引擎 | Neural Search 理解自然语言查询，返回干净结构化数据，支持域名/日期/类型过滤，支持"内容相似推荐" |
| **deepwiki** | GitHub 仓库文档聚合 | 比 context7 更全面但速度更慢 |

### 自动化与可视化类

| 服务器 | 用途 | 特点 |
|--------|------|------|
| **playwright** | 浏览器自动化 | 竞品监控、批量截图、自动化测试、数据抓取 |
| **drawio** | 流程图/架构图生成 | 3 种模式：Mermaid（最常用）、CSV（组织/拓扑图）、XML（复杂图表）。生成 Draw.io 编辑链接，节点可拖拽修改 |

### 知识库集成

| 服务器 | 用途 | 依赖 |
|--------|------|------|
| **mcp-obsidian** | Obsidian 笔记库读写 | Local REST API 插件 + `uvx mcp-obsidian` |

## 推荐场景组合

| 场景 | 推荐组合 |
|------|---------|
| 日常开发 | filesystem + github + memory |
| 深度工作 | sequential-thinking + context7 + memory |
| 自动化任务 | playwright + filesystem |
| 学习新技术 | context7 + deepwiki + exa |

## 相关概念与实体

- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]：MCP 的主要宿主环境
- [[KnowledgeBase/entities/Obsidian|Obsidian]]：通过 mcp-obsidian 实现 AI 操作笔记库
- [[KnowledgeBase/entities/OpenClaw|OpenClaw]]：另一个使用 MCP 的 AI 平台

## 在本仓库中的覆盖

- [[AI/ClaudeCode/Claude Code 扩展体系]]：10 个 MCP 服务器的安装配置、使用场景、完整 JSON 配置模板
- [[AI/ClaudeCode/ClaudeCode基础指南]]：MCP 在实战场景中的应用（事故响应、技术选型、文档查询）
- [[AI/ClaudeCode/obsidian-claude-搭建个人知识库]]：mcp-obsidian 的配置与 Obsidian 集成

## 知识空白

- 自定义 MCP Server 开发指南（如何用 Python/Node.js 开发自己的 MCP）
- MCP 与 OpenAPI / Function Calling 的架构对比
- MCP 在企业级安全合规场景中的权限控制
- MCP Server 的性能基准测试和资源消耗分析
- MCP 的错误处理和重试机制
