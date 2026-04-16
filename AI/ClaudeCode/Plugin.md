---
title: Claude Code Plugin
tags:
  - AI
  - claude-code
  - plugin
aliases:
  - CC Plugin
---

# Plugin（插件）

Plugins（插件）是应用级打包容器，用来打包其他四个工具的打包容器。

一个 Plugin 可以包含：

1. 5 个 Skills
2. 10 个 Slash Commands
3. 3 个 MCP 服务器配置
4. 2 个 SubAgent 定义
5. 若干 Hooks

## 适合场景

1. 团队标准化工具打包、快速分享工作流、一键安装完整套件
2. 临时用一次，快速试试某个功能

## 缺点

装太多会卡，而且大部分功能都重复。

> [!tip] 建议
> 个人用全局配置，团队用 Plugins 打包分发。别超过 3 个，够用就行。
