---
title: "Vibe Coding 时代的 Git Worktree 实践指南"
source: "https://mp.weixin.qq.com/s/QOjkU5QYcCb-OETfahnVBQ"
created: 2026-06-28
tags:
  - claude-code
  - git
  - vibe-coding
  - worktree
---

# Git Worktree：AI 开发时代的并行工作流

## 问题：AI 开发为什么怕切分支？

想象一个常见场景：你正在用 AI 工具开发某个功能，已经迭代了 20 多轮，AI 理解了项目结构和你的设计意图。

这时候线上出了个紧急 Bug。

传统做法：stash 当前修改 → checkout 到 hotfix 分支 → 开一个**新的 AI 会话**修 Bug → 修完 checkout 回来 → stash pop。

结果：AI 会话的上下文归零了。AI 上下文里已经读过的代码、已经理解的文件结构，随着分支切换、文件变化，全部失效。

还有个更糟的情况：AI 不知道文件被 stash 了，它还在 `auth.go` 上修改，结果改的是 stash 后的版本，pop 的时候直接冲突。

再加上一个限制：你想同时让三个 AI 探索不同方案，Git 只允许你串行——方案 A 试完 reset，方案 B 试完 reset，三个 AI 硬被拖成串行。

## Worktree 是什么

一句话：**Git Worktree 让你从一个仓库 checkout 出多个工作目录，每个目录对应一个分支。**

```bash
# 从主仓库创建新 worktree（同时创建新分支）
git worktree add -b feat-auth ../project-feat-auth

# 在另一个目录创建 worktree（checkout 已有分支）
git worktree add ../project-hotfix-123 hotfix-123

# 列出所有 worktree
git worktree list

# 删除 worktree
git worktree remove ../project-feat-auth

# 清理残留
git worktree prune
```

所有 worktree 共享同一个 `.git` 目录，所以 commit 历史是共享的，但文件是独立的。

## 核心原则：一个 AI 会话 = 一个 Worktree

这是使用 Worktree 做 Vibe Coding 的核心：

```
~/projects/
├── main-repo/           # 主仓库（main 分支，保持干净）
├── project-feat-a/      # worktree feat-a → AI 会话 A
├── project-feat-b/      # worktree feat-b → AI 会话 B
├── project-hotfix-c/    # worktree hotfix-c → AI 会话 修复C
└── project-exp-d/       # worktree exp-d → AI 会话 实验D
```

**每个目录里跑独立的 AI 会话，互不打扰。** 比如会话 A 在改认证模块，会话 C 在修 Bug——每个会话都在自己的目录里，文件各自稳定，不会 stash 来 stash 去。

## 典型场景

### 场景 1：正在开发，突然来 Bug

没有 Worktree：stash → checkout → 新会话 → 修完 → checkout 回来 → pop → 旧会话已废

有 Worktree：

```bash
# AI 会话 A 在 project-feat-a 里继续工作

# 新开一个终端，创建 hotfix worktree
git worktree add ../project-hotfix-123 -b hotfix-123
cd ../project-hotfix-123

# 在 project-hotfix-123 目录启动 AI 工具，修 Bug，完全不影响 A
opencode

# 修完，merge 到 main，删除 worktree
git add . && git commit -m "fix: #123"
git checkout main && git merge hotfix-123
git worktree remove ../project-hotfix-123

# AI 会话 A 的文件、上下文一行没动
```

### 场景 2：多方案并行探索

你想让 AI 试三种不同的内部通信方案：

```bash
git worktree add ../bench-grpc -b bench-grpc
git worktree add ../bench-rest -b bench-rest
git worktree add ../bench-mq -b bench-mq

# 三个终端，各自启动 AI 工具，同时跑
cd ../bench-grpc && opencode     # 用 gRPC 做服务间通信
cd ../bench-rest && opencode     # 用 HTTP REST 做服务间通信
cd ../bench-mq && opencode       # 用消息队列做异步通信
```

三个目录同时干活，而不是串行。哪个方案行留哪个，其他直接 `git worktree remove` 删掉，主仓库一行没动。

## 实践踩坑

### 本地配置文件不会跟过去

`config.yaml`、`.env` 这些不进 git 的本地配置（被 `.gitignore` 过滤），每个 worktree 都要单独复制一份：

```bash
# 创建 worktree 后第一件事
cd ../project-feat-a
cp ../main-repo/config.yaml .
cp ../main-repo/.env .
```

### 编译二进制散落各处

每个 worktree 都有自己的 `go build` 产物，注意 `.gitignore` 要配好：

```gitignore
# .gitignore 加上
/bin/           # 统一放 bin 目录
*.exe           # Windows 交叉编译产物
```

### IDE 要多开窗口

GoLand 或 VSCode 都需要把每个 worktree 作为独立项目打开，可以通过 VSCode 的"工作区"关联在一起：

```bash
# GoLand：命令行打开
goland ../project-feat-a
goland ../project-feat-b

# VSCode：命令行打开
code ../project-feat-a
code ../project-feat-b
```

### 命名规范

worktree 命名要和分支对应，不然几天后 `git worktree list` 一堆乱码目录都不知道在干什么：

- **功能性 worktree**：`project-feat-{name}`
- **探索性 worktree**：`project-exp-{name}`
- **修复性 worktree**：`project-hotfix-{issue-number}`

### 删除前去 main 合并

删除 worktree 之前，确认对应分支已经合并到 main，不然改动直接没了：

```bash
# 先合并后删除
git checkout main && git merge feat-auth
git worktree remove ../project-feat-auth
```

## 总结

Git Worktree 解决的就一件事：**让 AI 的文件环境稳定**。

Vibe Coding 配上 worktree，开发过程更可靠。该做的事就能做下去，不会被切分支打断、不会因为 stash 冲突而返工。
