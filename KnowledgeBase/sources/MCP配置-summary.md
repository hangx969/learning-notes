---
title: MCP配置
tags:
  - knowledgebase/source
  - ai/claude-code
date: 2026-04-17
sources:
  - "[[AI/ClaudeCode/MCP]]"
---

# MCP配置

## 元信息
- **原始文档**：[[AI/ClaudeCode/MCP]]
- **领域**：AI / Claude Code
- **摄入日期**：2026-04-17

## 摘要
系统性整理了 10 个 MCP Server 的安装命令、配置方式和使用场景，包括文档查询（context7、deepwiki）、项目管理（atlassian、bitbucket、github）、深度推理（sequential-thinking）、长期记忆（memory）、浏览器自动化（playwright）、语义搜索（exa）和图表生成（drawio）。文档还提供了按工作场景的推荐组合以及一键安装的完整 JSON 配置。

## 关键知识点
1. context7：查询最新框架文档（Next.js 15、React 19），支持 npx 和 VSCode 扩展安装
2. atlassian：通过 Docker 容器集成 Jira + Confluence，需配置 JIRA_URL、JIRA_USERNAME、JIRA_PERSONAL_TOKEN 等环境变量
3. bitbucket：通过 npx @zhanglc77/bitbucket-mcp-server 实现代码搜索和 PR 管理
4. sequential-thinking：深度推理引擎，适用于复杂技术决策和根因分析，展示完整推理链：假设 → 验证 → 排除 → 聚焦 → 验证 → 结论
5. memory：项目长期记忆，存储团队约定、踩坑记录、架构决策
6. playwright：浏览器自动化，用于竞品监控、截图、测试
7. filesystem：本地文件操作，需指定允许访问的路径
8. github：GitHub 操作，需 GITHUB_PERSONAL_ACCESS_TOKEN
9. exa：神经语义搜索（Neural Search），支持域名/日期/类型过滤和内容相似度推荐
10. deepwiki：深度文档聚合，比 context7 更全面但更慢
11. drawio：将 AI 生成的 Mermaid/CSV/XML 转换为 Draw.io 图表，支持三种模式
12. 推荐组合：日常开发（filesystem+github+memory）、深度工作（sequential-thinking+context7+memory）、自动化（playwright+filesystem）、学习（context7+deepwiki+exa）

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/MCP|MCP]]

## 值得注意
- sequential-thinking 的推理链展示方式（假设 → 验证 → 排除 → 聚焦）使 AI 决策过程透明可追溯
- context7 vs deepwiki 的取舍：速度 vs 深度，日常查 API 用前者，深入理解用后者
- exa 的 Neural Search 能力使其超越关键词搜索，适合探索性调研
- 按场景组合 MCP 的思路比逐个使用更高效——组合产生协同效应
