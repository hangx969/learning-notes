---
title: "CodeGraph：给 Claude Code 先画一张代码地图，工具调用砍掉 92%"
source: "https://mp.weixin.qq.com/s/8sEC_IISL9BVcmOlw-Zlig"
created: 2026-06-08
tags:
  - claude-code
  - code-understanding
  - knowledge-graph
---

# CodeGraph：代码语义知识图谱

## 解决什么问题

用 Claude Code 跑大项目时，它每次都需要先 grep、再 glob、再 Read，文件夹扫一圈、函数名追一遍，等它终于搞清楚入口在哪，token 已经烧了一截。

CodeGraph 做的事很直接：**提前给代码库建一张语义知识图谱**。Claude Code 不再每次从零扫文件，而是直接查图。函数调用链、类继承、模块引用这些关系，先被整理好，真正问问题时少绕很多路。

## 效果数据

项目 README 给出的基准：

| 指标 | 数据 |
|------|------|
| 平均工具调用减少 | **92%** |
| 探索速度提升 | **71%** |

VS Code 项目（TypeScript）实测：

| 场景 | 无 CodeGraph | 有 CodeGraph |
|------|-------------|-------------|
| 索引规模 | — | 4002 文件、59377 节点 |
| 回答"extension host 怎么和 main process 通信" | 52 次工具调用，1 分 37 秒 | 3 次工具调用，17 秒 |

## 核心能力

### 不只是搜索

改代码前可以先看影响范围：这个函数被谁调用，这个类继承链往哪里走，这个模块改了会牵到哪些地方。对重构来说，这比单纯全文搜索舒服很多。

尤其是那种"我只想改一小块，但怕炸一大片"的场景。

### 语言和框架覆盖

支持 **19 种编程语言**，还能识别 Django、Express、Spring 这类框架里的路由映射。不只是找到函数，还能把请求入口、业务逻辑、底层调用串起来看。

### 数据在本地

不依赖外部服务，不用把公司代码库丢到第三方平台。对团队项目来说心理负担小很多。

### 自动同步

文件保存后会自动同步图谱，不需要每次手动重建。

## 安装与使用

```bash
# 安装
npx @colbymchenry/codegraph

# 进入项目后交互式初始化（配置 Claude Code 集成）
codegraph init -i
```

初始化完成后，Claude Code 会自动使用图谱。文件保存时图谱自动增量更新。

## 适用场景

**适合**：
- 代码量已经上来、依赖关系开始绕的仓库
- 经常让 Claude Code 做代码探索和重构的场景
- 大型 monorepo 或复杂框架项目

**不太需要**：
- 小项目里 Claude Code 本来就能很快扫完，收益不明显

## 与 Graphify 的区别

| 维度 | CodeGraph | Graphify |
|------|-----------|---------|
| 定位 | **代码专用**语义图谱 | **软件工程**知识图谱（代码+文档+PDF+视频） |
| 解析方式 | 本地 AST（tree-sitter） | 代码用 AST + 文档/PDF/视频用 AI 语义提取 |
| 核心价值 | 减少 Agent 工具调用、加速代码探索 | 关联代码与外部资料（论文/设计文档/视频） |
| 框架识别 | 支持 Django/Express/Spring 路由映射 | 不特别针对框架 |
| 外部资料 | 不支持 | 支持论文/YouTube/PDF 等 |
| 自动同步 | 文件保存自动更新 | 需手动 `--update` 或 git hook |

GitHub：https://github.com/colbymchenry/codegraph
