---
title: OpenClaw
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[AI/OpenClaw/OpenClaw-基础-安装]]"
  - "[[AI/OpenClaw/OpenClaw-Skills-插件]]"
  - "[[AI/OpenClaw/OpenClaw-Channels]]"
  - "[[AI/OpenClaw/Openclaw-AIOps]]"
  - "[[AI/OpenClaw/Openclaw-多智能体]]"
  - "[[AI/OpenClaw/CoPaw]]"
  - "[[AI/OpenClaw/Ubuntu-2510-Setup-Guide]]"
---

# OpenClaw

## 定义
OpenClaw 是一个大模型驱动的通用 AI Agent 平台，能够操作电脑、管理文件、调用 API，支持多智能体协作、AIOps 运维自动化、Channels 通道管理、Skills 插件扩展以及 CoPaw 交互界面。通过 npm 安装，需要 Node.js 22+ 和 Python 环境，配置文件位于 `~/.openclaw/openclaw.json`。本仓库记录了其安装部署、核心功能模块与实战用法。

## 核心功能模块

### Skills 插件生态
- 通过 **Clawhub** 官方工具管理 Skill 的搜索、安装与升级
- 办公类 Skills：PDF/Excel/PPT 文档处理
- **Agent-browser**（Vercel Labs）：基于 accessibility-tree 快照的浏览器自动化
- 百度搜索 Skill：弥补模型知识截止日期的关键能力
- **self-improving-agent**：实现"做事-复盘-记录-沉淀-改进"的自我进化行为模式
- **skill-vetter**：四步安全审查流程（来源/代码/权限/风险评级）
- **ClawDeckX**：可视化管理面板

### Channels 通道管理
- **飞书 Channel**：支持自动安装和手动安装，Connection Mode 选 WebSocket，需配置事件订阅 `im.message.receive_v1`
- **QQ Channel**：通过腾讯官方快捷接入通道，扫码创建机器人
- 常见排障：代理环境变量残留会导致通信失败，需清理 systemd 服务中的 proxy 环境变量

### AIOps 运维自动化
- 通过飞书 + OpenClaw 远程管理 [[KnowledgeBase/entities/Kubernetes|Kubernetes]] 集群
- 使用 kubectl Skill 以自然语言下发 K8s 管理命令（查询节点、Pod 状态、异常诊断）
- 邮箱 Skill（imap-smtp-email）支持发送 K8s 巡检报告
- 定时任务推荐用 `openclaw cron add` 命令行方式添加

### 多智能体协同
- 解决单智能体"上下文窗口稀释"和线性执行效率低的痛点
- 角色定义三要素：身份定义、任务边界、输出格式约束
- 核心配置文件体系：**IDENTITY.md**（外在人设）、**SOUL.md**（核心价值观）、**AGENTS.md**（工作习惯）
- 飞书多账号路由：通过 `channels.feishu.accounts` + `bindings` 实现一个 bot 对应一个 agent
- agent-to-agent 通信：通过 `tools.agentToAgent` 和 `subagents.allowAgents` 配置
- 标准流程：PM 输出需求分析 -> 架构师分发 -> 前后端并行开发

### 模型接入
- 支持 OpenAI 协议接入自定义模型（魔塔/Deepseek/GitHub Copilot）
- GitHub Copilot 原生支持，通过 OAuth 设备授权流程接入
- 可通过配置文件或自然语言添加模型

## CoPaw 对比
[[AI/OpenClaw/CoPaw|CoPaw]] 是阿里推出的对标 OpenClaw 的 AI Agent 产品，基于 AgentScope 框架。通过 pip 安装，`copaw init --defaults` 初始化，`copaw app` 启动，访问 `127.0.0.1:8088` 使用 WebUI。

## 与 Claude Code 的关系
OpenClaw 和 [[KnowledgeBase/entities/Claude-Code|Claude Code]] 同属 AI Agent 工具，但定位不同：OpenClaw 侧重多智能体协同和渠道对接（飞书/QQ），Claude Code 侧重代码开发场景的 CLI 交互。两者的 Skills/[[KnowledgeBase/entities/MCP|MCP]] 插件扩展机制有可比性。

## 在本仓库中的位置
主要集中在 `AI/OpenClaw/` 目录，共 7 篇文章。

## 相关文章
- [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]]
- [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]]
- [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]]
- [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]]
- [[AI/OpenClaw/OpenClaw-Skills-插件|OpenClaw-Skills-插件]]
- [[AI/OpenClaw/CoPaw|CoPaw]]
- [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]]

## 关联概念
- [[KnowledgeBase/entities/Claude-Code|Claude-Code]]
- [[KnowledgeBase/entities/MCP|MCP]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]

## 可延展方向
- OpenClaw 与 Kubernetes 集群的 AIOps 集成
- 多智能体在 DevOps 场景中的应用
- OpenClaw Skills 与 MCP 协议的对比
