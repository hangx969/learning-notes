---
title: "Understand-Anything：AI 代码知识图谱可视化工具"
source: "https://mp.weixin.qq.com/s/F0evpeuQlZ_opQcidX328w"
created: 2026-06-28
tags:
  - code-understanding
  - knowledge-graph
  - ai-coding
  - tree-sitter
---

# Understand-Anything：代码知识图谱可视化

> GitHub 55.5k stars。核心理念："图的目标不是用代码库的复杂性来震撼你，而是悄悄地向你展示每个部分是如何组合在一起的。"

## 解决什么问题

- 近半数研发有效工时耗在读存量代码、梳理调用链、维护遗留系统上
- 现有 AI 编程工具受 Token 窗口限制读不下整仓代码，缺少全局架构判断，跨模块问题常出片面方案
- 传统代码可视化只画简单依赖拓扑，无业务语义，节点连线杂乱，实用价值有限
- 行业矛盾：静态分析精准但不会智能解读，大模型能理解却承载不下完整代码架构

## 三层分层耦合架构

### 一、底层：Tree-sitter AST 解析层

- 基于成熟的 Tree-sitter 引擎，覆盖 Python/Java/Go/JS/C++ 等 99% 主流编程语言
- 全盘扫描仓库，生成标准 AST，精准提取文件、类、方法、全局变量、导入依赖、函数调用链路
- **完全不调用大模型**，没有幻觉误差
- 自带自动过滤机制：测试用例文件、废弃注释代码、无用工具脚本直接筛掉，不给上层图谱塞垃圾节点

### 二、中层：多智能体图谱构建层

流水线跑三个分工明确的轻量智能体：

| 智能体 | 职责 |
|--------|------|
| **结构 Agent** | 把 AST 提取的数据拼接成基础图谱框架，搭建节点和依赖连线 |
| **语义 Agent** | 对接大模型，自动给每个类/函数打标签：支付回调、用户鉴权、入参限制——把纯代码翻译成业务语言 |
| **精简 Agent** | 二次降噪，合并重复链路，弱化边缘小工具类，高亮支付/订单/权限这类核心业务模块 |

最终输出标准 JSON 图谱文件：

```json
{
  "nodes": [
    {
      "id": "src/auth/login.ts",
      "type": "file",
      "layer": "API",
      "summary": "处理用户登录认证，支持JWT和OAuth2",
      "business_domain": "用户认证"
    }
  ],
  "edges": [
    {"from": "login.ts", "to": "user-service.ts", "type": "depends_on"}
  ]
}
```

可以直接丢进 Git 跟随代码仓库同步提交，团队所有人共用一套代码认知图谱。

### 三、顶层：交互应用层

两大核心交互模块：

1. **可视化画布**：网页端交互式图谱，支持缩放、框选模块、隐藏无关节点、点击展开完整调用链。经典三分栏布局——左侧代码目录树、中间分色标识的力导向图谱画布、右侧节点详情与 AI 对话面板

2. **全局图谱问答**：大模型不再零散读取单个文件，手里握着整份项目完整图谱。彻底解决普通 AI 上下文不足的痛点

## 安装与使用

本质上是一个 **AI 编码助手插件**，适配 Claude Code、Cursor、VS Code + Copilot、Codex、Gemini CLI 等主流平台。

### Claude Code（推荐，功能最完整）

```bash
/plugin marketplace add Lum1104/Understand-Anything
/plugin install understand-anything

# 在任意代码仓库中运行
/understand

# 分析完成后打开可视化面板
/understand-dashboard
```

### 其他平台一键安装

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/Lum1104/Understand-Anything/main/install.sh | bash

# 指定平台
curl -fsSL https://raw.githubusercontent.com/Lum1104/Understand-Anything/main/install.sh | bash -s codex

# Windows PowerShell
iwr -useb https://raw.githubusercontent.com/Lum1104/Understand-Anything/main/install.ps1 | iex
```

### Cursor / VS Code + Copilot

克隆仓库到本地即可自动发现插件（Cursor 通过 `.cursor-plugin/plugin.json`，VS Code Copilot v1.108+ 通过 `.copilot-plugin/plugin.json`）。

### 团队共享图谱

图谱生成为标准 JSON 文件，建议提交至 Git 仓库（`.understand-anything/knowledge-graph.json`）。团队成员克隆代码后**无需重新扫描**即可直接使用，适用于新人上手、PR 评审和文档即代码场景。

超过 10 MB 的大型图谱建议用 git-lfs 管理：

```bash
git lfs install
git lfs track ".understand-anything/*.json"
git add .gitattributes .understand-anything/
```

**不需要统一 IDE**——有人用 Cursor，有人用 VS Code，有人用 Claude Code，都能共享同一份知识图谱。

## 与同类工具对比

| 维度 | Understand-Anything | CodeGraph | Graphify |
|------|:-------------------:|:---------:|:--------:|
| **核心定位** | 代码知识图谱 + 可视化 + 问答 | 代码 AST 图谱（减少 Agent 工具调用） | 代码 + 文档 + PDF + 视频全资料图谱 |
| **解析方式** | Tree-sitter AST + 多智能体语义标注 | Tree-sitter AST | AST + AI 语义提取 |
| **语义能力** | ✅ 多智能体自动打业务标签 | ❌ 纯结构 | ✅ AI 语义 |
| **可视化** | ✅ 交互式 Web 画布 + 问答 | ❌ 无 UI | ✅ 图谱查询 |
| **框架识别** | 通用 | Django/Express/Spring 路由映射 | 不特别针对框架 |
| **外部资料** | ❌ 仅代码 | ❌ 仅代码 | ✅ 论文/YouTube/PDF |
| **团队共享** | ✅ JSON 文件 Git 同步 | ✅ 文件保存自动更新 | 需手动 --update 或 git hook |
| **GitHub Stars** | 55.5k | ~2k | ~1k |

**GitHub**：https://github.com/Egonex-AI/Understand-Anything
