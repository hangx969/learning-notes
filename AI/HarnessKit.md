---
title: HarnessKit — AI 编码智能体统一管理工具
tags:
  - AI/tools
  - AI/agent-management
date: 2026-05-05
---

# HarnessKit — AI 编码智能体统一管理工具

> **One home for every agent.**
> 一个免费开源的应用，统一管理所有 AI 编码智能体的扩展、配置、记忆和规则。

- **GitHub**：https://github.com/RealZST/HarnessKit
- **许可证**：Apache-2.0
- **技术栈**：Rust（核心）+ TypeScript/Vite（前端）
- **当前版本**：v1.3.1（2026-05-01）
- **支持平台**：macOS / Linux / Windows

---

## 解决的问题

每个 AI 编码智能体（Claude Code、Cursor、Codex、Gemini CLI 等）都有自己的扩展格式、配置目录、记忆文件和规则约定。当你同时使用多个 Agent 时，面临的问题是：

- 扩展（Skills、MCP Server、Plugins）**分散在不同目录**，格式各异
- 同一个扩展在不同 Agent 上的**配置方式不同**（JSON、TOML、hook 约定、MCP schema）
- **无法跨 Agent 复用**扩展，需要手动逐一安装和维护
- 缺乏统一的**安全审计**视角，不清楚扩展实际访问了哪些权限

HarnessKit 将所有 Agent 的扩展、配置、记忆和规则纳入一个统一管理界面。

---

## 支持的 AI 智能体

| Agent | Skills | MCP | Plugins | Hooks | Agent-first CLIs |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Claude Code** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Codex** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Gemini CLI** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Cursor** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Antigravity** | ✓ | ✓ | — | — | ✓ |
| **Copilot** | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Windsurf** | ✓ | ✓ | — | ✓ | ✓ |

> **路线图**中计划支持 Hermes-agent、OpenClaw、OpenCode 等更多 Agent。

---

## 核心功能

### 1. 全类型扩展管理

管理五种扩展类型：**Skills**、**MCP Servers**、**Plugins**、**Hooks**、**Agent-first CLIs**。

- **智能分组**：按类型、Agent 或来源筛选；同源扩展自动归组为 Pack，支持批量操作
- **全局可视**：每个扩展展示所属 Agent、权限范围、Trust Score 和状态
- **一键操作**：启用/禁用直接在列表中完成；一键检查所有扩展更新
- **跨 Agent 部署**：查看哪些 Agent 已安装、哪些缺失，一键部署到任意 Agent，HarnessKit 自动处理格式差异

### 2. 配置/记忆/规则管理

统一管理每个 Agent 的 **Configs**、**Memory**、**Rules** 和 **Ignore** 文件。

- 自动发现全局和项目级配置文件
- 每个 Agent 独立仪表板，按类别展示所有文件（作用域、路径、大小、扩展摘要）
- 支持添加自定义路径到仪表板
- 配置文件修改实时检测刷新

### 3. 安全审计与权限透明

内置安全引擎，18 条静态分析规则，为每个扩展计算 **Trust Score**（0–100）：

| 等级 | 分数 | 含义 |
|------|------|------|
| Safe | 80+ | 安全 |
| Low Risk | 60–79 | 低风险 |
| Needs Review | <60 | 需审查 |

- **一键全扫描**：对所有扩展运行安全审计
- **精确定位**：每条发现标注文件和行号
- **独立审计**：即使多个 Agent 共享同一扩展，每份副本独立审计
- **五维权限透视**：文件系统路径、网络域名、Shell 命令、数据库引擎、环境变量

### 4. 扩展市场

三大市场集成：

- **Skills**：浏览 [skills.sh](https://skills.sh) 注册表，也支持从 Git URL 或本地目录安装
- **MCP Servers**：浏览 [Smithery](https://smithery.ai) 的 MCP 服务器注册表
- **Agent-first CLI**：发现专为 Agent 构建的 CLI 工具

每个列表展示描述、安装量和来源。Skills 支持预览文档、查看第三方安全评分，一键安装到任意 Agent。

### 5. 原地管理（In-Place）

- 直接读写 Agent 原生配置目录，**不做影子拷贝**
- 启用/禁用扩展仅做文件重命名，**不移动不复制**
- 卸载 HarnessKit 后**零残留**，一切保持原状

---

## 三种使用模式

### 桌面应用（macOS）

```bash
# 下载 DMG 安装
# Apple Silicon: HarnessKit_x.x.x_aarch64.dmg
# Intel:         HarnessKit_x.x.x_x64.dmg
```

### CLI 模式（全平台）

```bash
# 安装
curl -fsSL https://raw.githubusercontent.com/RealZST/HarnessKit/main/install.sh | sh

# Windows
# irm https://raw.githubusercontent.com/RealZST/HarnessKit/main/install.ps1 | iex

# 常用命令
hk status                              # 查看检测到的 Agent 和扩展概览
hk list --kind skill --agent claude     # 按类型和 Agent 筛选
hk audit                               # 安全审计
hk enable my-skill                      # 启用扩展
hk disable --pack owner/repo            # 按来源批量禁用
```

### Web 模式（全平台）

```bash
hk serve
# 访问 http://localhost:7070
```

适用于 Linux 服务器、HPC 集群等无桌面环境，与桌面应用功能完全一致。

远程服务器使用方式：

```bash
ssh -L 7070:localhost:7070 user@your-server
hk serve
# 本地浏览器访问 http://localhost:7070
```

---

## 与本仓库其他工具的关系

| 工具 | 定位 | 关系 |
|------|------|------|
| [[AI/ClaudeCode/ClaudeCode基础指南\|Claude Code]] | AI 编码助手 | HarnessKit 管理其 Skills/MCP/Plugins/Hooks/Rules |
| [[AI/OpenClaw/OpenClaw-基础-安装\|OpenClaw]] | AI 多智能体运维平台 | HarnessKit 路线图计划支持 |
| [[AI/Hermes-agent/Hermes Agent 资源合集\|Hermes Agent]] | AI Agent 框架 | HarnessKit 路线图计划支持 |
| [[AI/GithubCopilot/Copilot CLI\|Copilot CLI]] | GitHub Copilot | HarnessKit 已支持 Copilot 扩展管理 |

HarnessKit 不替代任何 Agent，而是作为**元管理层**运行在所有 Agent 之上，解决多 Agent 并存时的扩展碎片化问题。

---

## 路线图

- 更多 Agent 支持：Hermes-agent、OpenClaw、OpenCode
- 扩展迁移：跨设备导入/导出扩展配置
- CLI 增强：更丰富的命令和交互功能
