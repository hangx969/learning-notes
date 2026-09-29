---
title: AI/OpenClaw/杂项 来源批量摘要
tags:
  - knowledgebase/source
  - AI
  - openclaw
  - prompt-engineering
  - github-copilot
date: 2026-04-17
sources:
  - "[[AI/OpenClaw/OpenClaw-基础-安装]]"
  - "[[AI/OpenClaw/OpenClaw-Skills-Plugins]]"
  - "[[AI/OpenClaw/OpenClaw-Channels]]"
  - "[[AI/OpenClaw/Openclaw-AIOps]]"
  - "[[AI/OpenClaw/Openclaw-多智能体]]"
  - "[[AI/OpenClaw/CoPaw]]"
  - "[[AI/OpenClaw/Ubuntu-2510-Setup-Guide]]"
  - "[[AI/GithubCopilot/Copilot CLI]]"
aliases:
  - "AI/OpenClaw 杂项批量摘要"
  - "AI-OpenClaw 批量摘要"
---

## 元信息

- **文档数量**：本批次收录 8 篇（`AI/OpenClaw/` 与 `AI/GithubCopilot/` 现有 11 篇）
- **主要领域**：AI Agent 平台（OpenClaw）、GitHub Copilot CLI、Linux 环境配置
- **知识层次**：从安装部署到高级多智能体协同，覆盖基础使用、插件扩展、渠道对接、AIOps 实践、多智能体架构设计

## 摘要

本批次文档以 **OpenClaw** 这一大模型驱动的通用 AI Agent 平台为核心，完整记录了从零搭建到生产级多智能体协同的全流程。内容涵盖：平台安装与模型接入、Skills 插件生态（办公、搜索、浏览器、自我进化、安全审计）、飞书/QQ 渠道对接、基于 K8s 的 AIOps 巡检与邮件通知、多智能体架构设计（角色拆分、IDENTITY/SOUL/AGENTS 核心文件、飞书多账号路由、agent-to-agent 通信）。此外还包括竞品 CoPaw（阿里）、Ubuntu 25.10 环境初始化、GitHub Copilot CLI 配置。

## 关键知识点

1. OpenClaw 通过 npm 安装，需 Node.js 22+ 与 Python 环境；配置文件位于 `~/.openclaw/openclaw.json`，gateway token 用于 WebUI 认证。
2. 自定义模型通过 OpenAI 协议接入；GitHub Copilot 原生支持，通过 OAuth 设备授权流程接入。
3. Skills 决定 Agent 的实际可用性：Clawhub 负责 Skill 的搜索、安装与升级；API 不含搜索能力且模型知识有截止日期，因此搜索 Skill 是关键；Agent-browser 使用 accessibility-tree 快照实现稳定的元素引用。
4. 飞书 Channel 的 Connection Mode 选 WebSocket，需订阅 `im.message.receive_v1` 事件，首次对话需执行 pairing 命令。
5. AIOps 的前置条件是在 OpenClaw 所在机器安装 kubectl 并配置 kubeconfig；之后可用自然语言查询节点、Pod 状态和诊断异常，巡检报告通过 imap-smtp-email Skill 发送到邮箱。
6. 多智能体角色定义包含身份定义、任务边界、输出格式约束三要素；AGENTS.md 定义工作习惯，IDENTITY.md 定义外在人设，SOUL.md 定义核心价值观。
7. 飞书多账号路由通过 `channels.feishu.accounts` + `bindings` 实现一个 bot 对应一个 agent；agent-to-agent 通信通过 `tools.agentToAgent` 与 `subagents.allowAgents` 配置。
8. Ubuntu 25.10 的 APT 源采用 DEB822 格式（`/etc/apt/sources.list.d/ubuntu.sources`）；Fcitx5 中文输入法需设置 GTK_IM_MODULE/QT_IM_MODULE/XMODIFIERS 环境变量。

## 各文档摘要

### [[AI/OpenClaw/OpenClaw-基础-安装|OpenClaw-基础-安装]]

- **核心内容**：OpenClaw 平台介绍、架构分层（入口层/Gateway/AgentRuntime/原子操作/持久化）、Windows 和 Linux 下的安装流程、引导配置、多供应商多模型接入（魔塔/Deepseek/GitHub Copilot）、升级与卸载
- **关键知识点**：
  - OpenClaw = 大模型驱动的通用 AI Agent，可操作电脑、管理文件、调用 API
  - 通过 npm 安装，需 Node.js 22+、Python 环境
  - 支持 OpenAI 协议接入自定义模型，可通过配置文件或自然语言添加模型
  - GitHub Copilot 原生支持，通过 OAuth 设备授权流程接入
  - 配置文件位于 `~/.openclaw/openclaw.json`，gateway token 用于 WebUI 认证

### [[AI/OpenClaw/OpenClaw-Skills-Plugins|OpenClaw-Skills-Plugins]]

- **核心内容**：Skills 生态与管理工具 Clawhub、办公类 Skills（PDF/Excel/PPT）、自我进化 Skill、记忆插件、安全审计 skill-vetter、浏览器自动化（Agent-browser/Agent-Reach）、百度搜索 Skill、可视化面板 ClawDeckX
- **关键知识点**：
  - Clawhub 是官方 Skill 管理工具，支持搜索、安装、升级
  - Agent-browser（Vercel Labs）使用 accessibility-tree 快照实现稳定元素引用
  - 搜索 Skill 是 Agent 实用性的关键，API 不含搜索能力，模型知识有截止日期
  - self-improving-agent 实现"做事-复盘-记录-沉淀-改进"的行为模式
  - skill-vetter 提供四步安全审查流程（来源/代码/权限/风险评级）

### [[AI/OpenClaw/OpenClaw-Channels|OpenClaw-Channels]]

- **核心内容**：飞书 Channel 配置（自带版和官方版）、QQ Channel 配置、飞书机器人创建与事件订阅、代理环境变量导致的通信问题排障
- **关键知识点**：
  - 飞书支持自动安装和手动安装两种方式，Connection Mode 选 WebSocket
  - 需配置事件订阅 `im.message.receive_v1`，首次对话需执行 pairing 命令
  - 代理环境变量残留会导致关闭代理后通信失败，需清理 systemd 服务中的 proxy 环境变量
  - QQ 通过腾讯官方快捷接入通道，扫码创建机器人

### [[AI/OpenClaw/Openclaw-AIOps|Openclaw-AIOps]]

- **核心内容**：通过飞书+OpenClaw 远程管理 K8s 集群、kubectl Skill 使用、K8s 巡检报告生成与邮件发送、定时任务配置
- **关键知识点**：
  - 前置条件：OpenClaw 机器上需安装 kubectl 并配置 kubeconfig
  - 可用自然语言下发 K8s 管理命令（查询节点、Pod 状态、异常诊断）
  - 邮箱 Skill（imap-smtp-email）支持发送巡检报告到指定邮箱
  - 定时任务推荐用 `openclaw cron add` 命令行方式添加，而非自然语言方式

### [[AI/OpenClaw/Openclaw-多智能体|Openclaw-多智能体]]

- **核心内容**：多智能体理论基础、角色拆分设计模式、核心配置文件（BOOTSTRAP/USER/AGENTS/IDENTITY/SOUL/TOOLS/HEARTBEAT）、OpenClaw 多智能体实现（创建/Channel 绑定/飞书多账号路由/agent-to-agent 通信）、开发团队实战案例
- **关键知识点**：
  - 多智能体解决单智能体"上下文窗口稀释"、线性执行效率低等痛点
  - 角色定义三要素：身份定义、任务边界、输出格式约束
  - AGENTS.md 定义工作习惯，IDENTITY.md 定义外在人设，SOUL.md 定义核心价值观
  - 飞书多账号路由通过 `channels.feishu.accounts` + `bindings` 实现一个 bot 对应一个 agent
  - agent-to-agent 通信通过 `tools.agentToAgent` 和 `subagents.allowAgents` 配置
  - 标准流程：PM 先输出需求分析 -> 架构师分发 -> 前后端并行开发

### [[AI/OpenClaw/CoPaw|CoPaw]]

- **核心内容**：阿里推出的对标 OpenClaw 的 AI Agent 产品，基于 AgentScope
- **关键知识点**：
  - 通过 pip 安装，`copaw init --defaults` 初始化，`copaw app` 启动
  - 访问 `127.0.0.1:8088` 使用 WebUI

### [[AI/OpenClaw/Ubuntu-2510-Setup-Guide|Ubuntu-2510-Setup-Guide]]

- **核心内容**：Ubuntu 25.10 (Questing) 新机初始化配置指南，涵盖 SSH、sudo、APT 国内源、开发工具、中文输入法、VMware Tools
- **关键知识点**：
  - Ubuntu 25.10 使用 DEB822 格式的 APT 源配置（`/etc/apt/sources.list.d/ubuntu.sources`）
  - 支持阿里云/清华 TUNA/中科大三种国内镜像源
  - Fcitx5 中文输入法配置，需设置 GTK_IM_MODULE/QT_IM_MODULE/XMODIFIERS 环境变量
  - open-vm-tools 替代 VMware 官方 Tools，更稳定

### [[AI/GithubCopilot/Copilot CLI|Copilot CLI]]

- **核心内容**：GitHub Copilot CLI 安装与使用、MCP 配置
- **关键知识点**：
  - 支持通过 JSON 配置文件管理 MCP Server
  - 文档链接指向 GitHub 官方文档

## 涉及的概念与实体

- **平台/工具**：OpenClaw、CoPaw、AgentScope、Clawhub、Agent-browser、Agent-Reach、ClawDeckX、GitHub Copilot CLI、Fcitx5
- **模型/API**：Deepseek、魔塔（ModelScope）、GitHub Copilot、OpenAI 协议
- **消息渠道**：飞书（Lark）、QQ、WebSocket
- **运维/基础设施**：Kubernetes、kubectl、crontab、SMTP/IMAP、SSH 隧道、VMware Tools、Ubuntu 25.10
- **架构概念**：多智能体协同、角色拆分、agent-to-agent 通信、上下文窗口稀释、accessibility-tree
- **核心文件**：AGENTS.md、IDENTITY.md、SOUL.md、BOOTSTRAP.md、USER.md、TOOLS.md、HEARTBEAT.md、MEMORY.md、openclaw.json

## 交叉主题发现

1. **飞书贯穿多个场景**：从基础 Channel 配置到 AIOps 巡检通知再到多智能体群聊协同，飞书是 OpenClaw 最深度集成的消息渠道
2. **Skills 是 Agent 能力的核心扩展机制**：搜索 Skill 解决模型知识截止问题、kubectl Skill 实现 K8s 管理、邮箱 Skill 实现通知、浏览器 Skill 实现 Web 数据采集，Skills 生态决定了 Agent 的实际可用性
3. **多智能体架构复用了角色设计模式**：IDENTITY/SOUL/AGENTS 三文件体系既用于单智能体人设定义，也是多智能体场景下每个 agent 的独立配置单元
4. **环境配置是 AI Agent 部署的基础**：Ubuntu 初始化指南和 OpenClaw 安装指南互为补充，构成完整的 Agent 部署环境准备流程
5. **提示词工程与 Agent 角色定义本质相通**：多智能体的角色定义（身份/边界/输出格式）本质上就是系统级提示词工程的实践

## 值得注意

- **代理环境变量残留**：开着代理安装 OpenClaw 和飞书插件后，OpenClaw 服务文件（`~/.config/systemd/user/openclaw-gateway.service`）中会残留 http/https/all_proxy 环境变量，关闭代理后飞书机器人无法与 OpenClaw 通信（`connect ECONNREFUSED`）；删除这些 Environment 行后执行 `systemctl --user daemon-reload` 并重启 gateway。
- **定时任务不要用自然语言创建**：原笔记指出自然语言方式有失败几率，大概率会直接在 Linux 中生成 crontab，而不是加入 OpenClaw 的定时任务，因此推荐 `openclaw cron add`。
- **第三方 Skill 的安全审查**：skill-vetter 是纯文档型 Skill，安装后每次安装新 Skill 都会引导完成来源、代码、权限、风险评级四步审查，风险分 LOW、MEDIUM、HIGH、EXTREME 四级。
- **部分笔记较简略**：CoPaw 仅记录 pip 安装、初始化、启动与 WebUI 访问；Copilot CLI 主要是指向 GitHub 官方文档的链接（安装、使用、MCP 的 JSON 配置）。
