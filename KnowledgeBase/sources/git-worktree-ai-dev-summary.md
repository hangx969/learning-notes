---
title: Git Worktree AI 开发实践指南
tags:
  - knowledgebase/source
  - AI/claude-code
  - git/worktree
date: 2026-06-28
sources:
  - "[[Git-Worktree-AI开发实践指南]]"
aliases:
  - Worktree实践摘要
---

# Git Worktree AI 开发实践指南

## 元信息
- **原始文档**：[[Git-Worktree-AI开发实践指南]]
- **领域**：AI / Git / Vibe Coding
- **摄入日期**：2026-06-28

## 摘要
AI 辅助开发（Vibe Coding）场景下，传统 Git 单工作目录模式成为瓶颈——分支切换破坏 AI 上下文、stash 引发冲突、多方案只能串行。Git Worktree 通过"一个 AI 会话 = 一个 Worktree"的核心原则，实现多 AI 会话并行工作、上下文不丢失、实验不污染主分支。

## 关键知识点
1. **核心问题**：AI 会话积累了 20+ 轮上下文后，`stash → checkout → pop` 会导致上下文归零；AI 可能在 stash 后的版本上修改文件导致冲突
2. **核心原则**：一个 AI 会话 = 一个 Worktree，所有 worktree 共享 `.git` 目录（commit 历史共享，文件独立）
3. **场景 1——紧急 Bug 修复**：不切分支，新建 worktree 修 Bug，原会话文件和上下文零影响
4. **场景 2——多方案并行探索**：3 个 worktree 同时跑 3 种技术方案（如 gRPC/REST/MQ），行留不行删
5. **踩坑清单**：
   - `.env`/`config.yaml` 等 gitignore 文件需手动复制到每个 worktree
   - 编译产物散落各处，需配好 `.gitignore`
   - IDE 需为每个 worktree 开独立窗口（VSCode 可用工作区关联）
   - 命名规范：`project-feat-{name}` / `project-exp-{name}` / `project-hotfix-{issue}`
   - 删除 worktree 前必须先合并到 main

## 涉及的概念与实体
- [[KnowledgeBase/entities/Claude-Code]]：原生支持 worktree（`EnterWorktree` 工具）
- [[KnowledgeBase/sources/ai-git-best-practices-summary|AI 时代 Git 实践]]：互补——该文覆盖 11 条 Agent Git 最佳实践，本文专攻 Worktree 并行模式

## 值得注意
- Claude Code 已内置 worktree 支持（`EnterWorktree`/`ExitWorktree` 工具、Agent isolation: "worktree" 模式），与本文"一个 AI 会话 = 一个 Worktree"原则完全吻合
- 与知识库中 [[KnowledgeBase/sources/ai-git-best-practices-summary|AI 时代 Git 实践]] 互补：该文第 4 条"Worktree 替代 Stash"、第 5 条"每个 Agent 独立分支"正是本文的展开实践
- Worktree 本质是给 AI 提供"稳定的文件环境"——与 CodeGraph 给 AI 提供"稳定的代码地图"是同一层思路的不同维度
