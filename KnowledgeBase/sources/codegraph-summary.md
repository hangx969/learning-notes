---
title: CodeGraph 代码语义知识图谱
tags:
  - knowledgebase/source
  - AI/claude-code
  - code-understanding
date: 2026-06-08
sources:
  - "[[CodeGraph-代码语义知识图谱]]"
aliases:
  - CodeGraph摘要
---

# CodeGraph 代码语义知识图谱

## 元信息
- **原始文档**：[[CodeGraph-代码语义知识图谱]]
- **领域**：AI / Claude Code / 代码理解
- **摄入日期**：2026-06-08

## 摘要
CodeGraph 为代码库预建语义知识图谱（函数调用链、类继承、模块引用），让 Claude Code 直接查图而非从零扫文件。实测工具调用减少 92%、探索速度提升 71%。支持 19 种编程语言 + Django/Express/Spring 路由映射识别，本地 AST 解析不依赖外部服务，文件保存自动同步图谱。

## 关键知识点
1. **核心价值**：提前建图，让 Agent 少扫文件少烧 token——从"grep→glob→Read"变成"查图→沿边走"
2. **效果数据**：工具调用减少 92%，探索速度提升 71%；VS Code 项目（4002 文件）从 52 次调用/1 分 37 秒降到 3 次调用/17 秒
3. **不只是搜索**：能看影响范围（函数调用者、继承链、模块依赖），适合重构前的影响分析
4. **覆盖面**：19 种语言 + Django/Express/Spring 路由映射，能串联请求入口→业务逻辑→底层调用
5. **安装**：`npx @colbymchenry/codegraph` + `codegraph init -i`，文件保存自动同步
6. **数据本地化**：不依赖外部服务，代码不离开本机
7. **适用场景**：大仓库 + 复杂依赖 + 频繁代码探索/重构；小项目收益不明显

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code]]

## 值得注意
- 与知识库中的 [[AI/Graphify-软件工程知识图谱工具|Graphify]] 定位不同：CodeGraph 专注代码 AST 图谱（减少 Agent 工具调用），Graphify 覆盖代码+文档+PDF+视频的全资料知识图谱
- 本质是给 Claude Code 做了一层"代码记忆"缓存，与 CLAUDE.md 的"项目规则记忆"互补
