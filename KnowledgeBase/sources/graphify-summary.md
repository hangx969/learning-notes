---
title: Graphify 软件工程知识图谱工具
tags:
  - knowledgebase/source
  - AI/tools
date: 2026-06-07
sources:
  - "[[Graphify-软件工程知识图谱工具]]"
aliases:
  - Graphify摘要
---

# Graphify 软件工程知识图谱工具

## 元信息
- **原始文档**：[[Graphify-软件工程知识图谱工具]]
- **领域**：AI / 代码理解工具
- **摄入日期**：2026-06-07

## 摘要
Graphify 是一个开源工具，将项目中的代码（AST 本地解析）、文档、PDF、图片、视频（AI 语义提取）整合成一张可查询的软件工程知识图谱。支持 Claude Code、Codex、Cursor 等 10+ 平台，提供关系查询、路径追踪、节点解释、增量更新、MCP Server 模式和团队协作功能。

## 关键知识点
1. **核心定位**：从"检索文件"走向"查询关系"——AI 沿已有关系查找，不再每次从头翻文件
2. **双轨处理**：代码用 tree-sitter 本地 AST 解析（无 API 成本）；文档/PDF/图片/视频交 AI 模型语义提取
3. **置信度标记**：每条关系标 EXTRACTED（直接提取）/ INFERRED（推断）/ AMBIGUOUS（歧义），工程场景下"发现"和"推断"分开标注
4. **查询方式**：`/graphify query`（关系查询）、`/graphify path`（路径追踪）、`/graphify explain`（节点解释）
5. **可扩展**：PDF/Office/Video/MCP/Neo4j/Ollama/OpenAI/SQL 按需安装
6. **团队协作**：graphify-out/ 提交 git 共享、git hook 自动重建、merge-graphs 合并多图谱
7. **隐私边界**：代码本地处理，但文档/PDF 需发送给 AI 模型——企业项目需确认数据边界

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code]]
- [[KnowledgeBase/entities/MCP]]

## 值得注意
- 与知识库中 RAG 方案（向量检索）互补——RAG 侧重"语义搜索"，Graphify 侧重"关系查询"
- MCP Server 模式可让 AI 助手通过结构化接口查询图谱，是 MCP 生态的实用扩展
- PyPI 包名是 `graphifyy`（两个 y），但命令行仍是 `graphify`
