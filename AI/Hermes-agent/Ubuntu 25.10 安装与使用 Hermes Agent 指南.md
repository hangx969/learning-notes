---
title: "Ubuntu 25.10 安装与使用 Hermes Agent 指南"
source: "https://jcnrb2wjsrl6.feishu.cn/docx/Mk3vdmmmJobjOjxxgRBcsTsun5g"
created: 2026-05-04
description: "Hermes Agent 在 Ubuntu 25.10 上的完整指南：安装、Web Dashboard、OpenClaw 迁移、升级、飞书集成"
tags:
  - clippings
  - AI/hermes-agent
---

# Ubuntu 25.10 安装与使用 Hermes Agent 指南

## 官方参考

- Installation: https://hermes-agent.nousresearch.com/docs/getting-started/installation
- Web Dashboard: https://hermes-agent.nousresearch.com/docs/user-guide/features/web-dashboard
- Migrate from OpenClaw: https://hermes-agent.nousresearch.com/docs/guides/migrate-from-openclaw
- Updating: https://hermes-agent.nousresearch.com/docs/getting-started/updating/
- Feishu/Lark Setup: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/feishu

---

## 1. 在 Ubuntu 25.10 中安装 Hermes Agent

### 1.1 安装前建议

Hermes Agent 官方提供一行安装脚本，支持 Linux、macOS、WSL2 和 Android Termux。Ubuntu 25.10 可以直接使用 Linux 安装方式。

官方安装器会自动处理大部分依赖，包括：

- Python 3.11，通常通过 `uv` 管理
- Node.js v22
- ripgrep
- ffmpeg
- 构建工具和 Hermes 自身运行环境

建议先确保系统有基础工具：

```bash
sudo apt update
sudo apt install -y git curl ca-certificates
```

### 1.2 一行命令安装

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

安装完成后重新加载 shell 配置：

```bash
source ~/.bashrc
# 如果使用 zsh：
# source ~/.zshrc
```

验证命令是否可用：

```bash
command -v hermes
hermes --version
```

### 1.3 安装目录说明

普通用户安装时，典型路径如下：

| 内容 | 默认路径 |
| --- | --- |
| Hermes Agent 源码 | `~/.hermes/hermes-agent/` |
| Hermes 命令 | `~/.local/bin/hermes` |
| Hermes 数据目录 | `~/.hermes/` |
| 配置文件 | `~/.hermes/config.yaml` |
| 密钥与环境变量 | `~/.hermes/.env` |
| 会话、记忆、技能等 | `~/.hermes/sessions/`、`~/.hermes/memories/`、`~/.hermes/skills/` |

root 模式路径通常是：

| 内容 | 默认路径 |
| --- | --- |
| Hermes Agent 源码 | `/usr/local/lib/hermes-agent/` |
| Hermes 命令 | `/usr/local/bin/hermes` |
| Hermes 数据目录 | `/root/.hermes/` 或 `$HERMES_HOME` |

### 1.4 初始配置

安装完成后可以运行交互式配置：

```bash
hermes setup
```

也可以分别配置模型、工具和网关：

```bash
hermes model
hermes tools
hermes gateway setup
```

常用验证命令：

```bash
hermes doctor
hermes gateway status
```

---

## 2. 安装完成后如何访问 UI 界面

Hermes Agent 的官方浏览器 UI 叫 **Web Dashboard**。

### 2.1 启动 Web Dashboard

默认启动方式：

```bash
hermes dashboard
```

默认访问地址：

```
http://127.0.0.1:9119
```

如果服务器没有图形界面，建议加 `--no-open`：

```bash
hermes dashboard --no-open
```

### 2.2 Dashboard 常用参数

| 参数 | 说明 |
| --- | --- |
| `--port` | 指定端口，默认 `9119` |
| `--host` | 指定监听地址，默认 `127.0.0.1` |
| `--no-open` | 启动后不自动打开浏览器 |
| `--tui` | 在浏览器中启用 Chat/TUI 标签页，需要 pty 支持 |
| `--insecure` | 允许绑定非 localhost 地址，有安全风险 |

示例：

```bash
hermes dashboard --host 127.0.0.1 --port 9119 --no-open
```

### 2.3 远程服务器访问方式

如果 Hermes 安装在远程 Ubuntu 服务器上，推荐使用 SSH 端口转发，而不是直接暴露 Dashboard 端口：

```bash
ssh -L 9119:127.0.0.1:9119 user@server-ip
```

然后在本地浏览器打开：

```
http://127.0.0.1:9119
```

### 2.4 如果缺少 Web UI 依赖

Web Dashboard 依赖 FastAPI、Uvicorn 等 Web 组件；Chat/TUI 标签页还需要 pty 支持。若启动时提示依赖缺失，可以安装 Web 相关 extra：

```bash
pip install 'hermes-agent[web,pty]'
```

如果使用官方安装器创建的虚拟环境，建议优先根据 Hermes 启动时的提示，在对应环境中安装依赖。

### 2.5 Dashboard 和 Gateway/API 的区别

| 项目 | 默认端口 | 作用 |
| --- | --- | --- |
| Web Dashboard | `9119` | 浏览器管理界面：状态、配置、API Keys、会话等 |
| Gateway/API | `8642` | 后端网关/API 服务，供消息平台或 Open WebUI 等前端连接 |

如果只是访问 Hermes 自带管理 UI，通常看 `9119`。如果要接 Open WebUI 这类外部聊天前端，通常会涉及 `8642`。

---

## 3. 将 OpenClaw 配置迁移到 Hermes Agent

Hermes Agent 官方提供 OpenClaw 迁移工具：

```bash
hermes claw migrate
```

该工具默认从 `~/.openclaw/` 读取 OpenClaw 数据，并迁移到 `~/.hermes/`。

### 3.1 迁移前先备份

建议先备份 OpenClaw 原始目录：

```bash
tar -czf ~/openclaw-backup-$(date +%F-%H%M%S).tgz ~/.openclaw
```

如果已经有 Hermes 数据，也建议备份 Hermes：

```bash
tar -czf ~/hermes-backup-$(date +%F-%H%M%S).tgz ~/.hermes
```

### 3.2 先 dry-run 预览

迁移前先看会改什么：

```bash
hermes claw migrate --dry-run
```

或者直接运行预览流程：

```bash
hermes claw migrate
```

### 3.3 执行完整迁移

如果确认要迁移完整配置，并包含 API Key 等密钥：

```bash
hermes claw migrate --preset full --migrate-secrets --yes
```

### 3.4 常用迁移参数

| 参数 | 说明 |
| --- | --- |
| `--dry-run` | 只预览，不写入 |
| `--preset user-data` | 只迁移用户数据，默认不迁移基础设施配置和密钥 |
| `--preset full` | 迁移尽可能完整的兼容配置 |
| `--migrate-secrets` | 迁移允许迁移的密钥到 `~/.hermes/.env` |
| `--source PATH` | 指定 OpenClaw 目录，默认 `~/.openclaw` |
| `--workspace-target PATH` | 指定 `AGENTS.md` 写入的工作区路径 |
| `--skill-conflict skip/overwrite` | 遇到技能冲突时的处理方式 |
| `--overwrite` | 遇到冲突时覆盖现有 Hermes 文件 |
| `--no-backup` | 跳过迁移前自动备份，不建议使用 |
| `--yes` | 跳过确认，适合确认无误后的自动化执行 |

### 3.5 主要迁移内容映射

| OpenClaw 内容 | Hermes 目标位置 |
| --- | --- |
| `~/.openclaw/workspace/SOUL.md` | `~/.hermes/SOUL.md` |
| `~/.openclaw/workspace/AGENTS.md` | 指定 workspace 的 `AGENTS.md` |
| `~/.openclaw/workspace/MEMORY.md` | `~/.hermes/memories/MEMORY.md` |
| `~/.openclaw/workspace/USER.md` | `~/.hermes/memories/USER.md` |
| `~/.openclaw/workspace/memory/*.md` | 合并进 `~/.hermes/memories/MEMORY.md` |
| OpenClaw Skills | `~/.hermes/skills/openclaw-imports/` |
| 模型配置 | `~/.hermes/config.yaml` |
| API Key / Token | `~/.hermes/.env`，需 `--migrate-secrets` |
| 命令 allowlist | 合并进 `~/.hermes/config.yaml` |
| TTS 资源 | `~/.hermes/tts/` |

### 3.6 迁移后验证

迁移完成后建议执行：

```bash
hermes doctor
hermes config check
hermes --version
```

如果使用消息网关：

```bash
hermes gateway status
```

如果迁移了 Skills，建议检查：

```bash
hermes skills list
```

### 3.7 迁移注意事项

- 复杂的 OpenClaw 自定义 Skill 可能需要人工检查和改写。
- OpenClaw 插件配置不一定能 1:1 迁移成 Hermes 原生集成。
- 飞书 Channel 建议迁移后重新按 Hermes 官方 Feishu/Lark Setup 配置一遍。
- 不建议让 OpenClaw 和 Hermes 同时接管同一个飞书 Bot，否则可能出现重复回复、会话状态混乱或事件竞争。
- 可先让 OpenClaw 和 Hermes 并行运行，但使用不同 Bot 或不同 Channel 做灰度验证。

---

## 4. Hermes Agent 怎么升级

Hermes Agent 官方提供 `hermes update` 系列命令。

### 4.1 检查是否有更新

```bash
hermes update --check
```

该命令用于检查本地是否落后于远端版本，不修改文件，也不会重启 Gateway。

### 4.2 带备份升级（推荐方式）

```bash
hermes update --backup
```

该方式会在升级前备份 Hermes Home，包括配置、认证、会话、Skills、配对状态等关键数据。

也可以在配置中长期启用升级备份：

```yaml
update:
  backup: true
```

### 4.3 执行普通升级

```bash
hermes update
```

升级后建议验证：

```bash
hermes --version
hermes doctor
hermes gateway status
```

如果 Gateway 正在运行，升级后根据提示重启 Gateway，或者重新启动服务进程。

### 4.4 升级失败时回滚

如果升级前使用了 `--backup`，可以按官方备份/恢复机制回到升级前状态。常见思路是恢复 pre-update 备份，例如：

```bash
hermes backup restore --state pre-update
```

实际可用命令以当前安装版本的帮助为准：

```bash
hermes backup --help
hermes update --help
```

---

## 5. Hermes Agent 集成飞书 Channel

Hermes Agent 支持 Feishu/Lark 消息平台集成，可以让飞书机器人连接 Hermes Gateway。

### 5.1 推荐连接方式：WebSocket

官方推荐使用 WebSocket 模式：

- Hermes 主动向飞书建立出站 WebSocket 长连接
- 不需要公网 Webhook 地址
- 适合内网服务器、家庭服务器、NAT 环境
- 配置项：`FEISHU_CONNECTION_MODE=websocket`

### 5.2 方式一：交互式配置（推荐）

运行：

```bash
hermes gateway setup
```

然后选择 Feishu/Lark，按提示完成配置。官方文档提到支持扫码创建/配置，凭证会自动保存。

配置完成后启动 Gateway：

```bash
hermes gateway
```

检查状态：

```bash
hermes gateway status
```

然后给飞书机器人发私聊消息测试。

### 5.3 方式二：手动配置 `.env`

编辑：

```bash
nano ~/.hermes/.env
```

添加或修改：

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxx
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
```

可选项：

```bash
# 只允许指定用户使用，多个用户用逗号分隔
FEISHU_ALLOWED_USERS=ou_xxx,ou_yyy

# 默认主页/通知 Channel，按实际 Hermes 文档和当前版本支持填写
FEISHU_HOME_CHANNEL=...
```

配置项说明：

| 配置项 | 说明 |
| --- | --- |
| `FEISHU_APP_ID` | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret，必须保密 |
| `FEISHU_DOMAIN` | 国内飞书用 `feishu`，国际 Lark 用 `lark` |
| `FEISHU_CONNECTION_MODE` | 推荐 `websocket`，也可用 `webhook` |
| `FEISHU_ALLOWED_USERS` | 可选，限制允许访问的飞书用户 |
| `FEISHU_HOME_CHANNEL` | 可选，默认通知或 Home Channel |

### 5.4 WebSocket 模式依赖

WebSocket 模式需要 Python `websockets` 包。如果启动时报缺失，可以在 Hermes 对应 Python 环境中安装：

```bash
pip install websockets
```

然后重新启动 Gateway：

```bash
hermes gateway
```

### 5.5 Webhook 模式（可选）

如果必须使用 Webhook，需要：

```bash
FEISHU_CONNECTION_MODE=webhook
```

Webhook 模式需要 `aiohttp`：

```bash
pip install aiohttp
```

默认 Webhook 路径：

```
/feishu/webhook
```

Webhook 模式需要将公网 HTTPS 地址配置到飞书开发者后台，例如：

```
https://your-domain.example.com/feishu/webhook
```

### 5.6 飞书侧行为规则

Hermes 官方文档说明的默认行为：

| 场景 | 默认行为 |
| --- | --- |
| 私聊 Bot | 回复所有消息 |
| 群聊 | 通常只在被 @ 时回复 |
| 共享群会话 | 默认按用户隔离会话历史 |

共享群会话相关配置通常由 `group_sessions_per_user` 控制：

```yaml
group_sessions_per_user: true
```

如果设置为 `false`，则群内可能共享同一个会话上下文。生产使用时建议先保持默认隔离，避免多人上下文混在一起。

### 5.7 飞书集成验证清单

配置完成后依次检查：

```bash
hermes doctor
hermes gateway status
hermes gateway
```

然后在飞书中验证：

- 私聊 Bot：发送一句测试消息
- 群聊：将 Bot 拉入群，并 @Bot 测试
- 查看 Hermes Gateway 日志是否有 Feishu/Lark 连接成功信息
- 确认不会和 OpenClaw 使用同一个 Bot 同时在线处理消息

### 最小命令合集

```bash
# 1. 安装基础工具
sudo apt update
sudo apt install -y git curl ca-certificates

# 2. 安装 Hermes Agent
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc

# 3. 验证与初始化
hermes --version
hermes setup
hermes doctor

# 4. 启动 UI
hermes dashboard --no-open
# 浏览器访问 http://127.0.0.1:9119

# 5. OpenClaw 迁移预览
hermes claw migrate --dry-run

# 6. 执行完整迁移，包含密钥
hermes claw migrate --preset full --migrate-secrets --yes

# 7. 配置飞书
hermes gateway setup
hermes gateway

# 8. 升级
hermes update --check
hermes update --backup
hermes doctor
```

---

## 7. 结论

- Ubuntu 25.10 安装 Hermes Agent 最简单的方式是使用官方一行安装脚本。
- UI 默认是 Web Dashboard，地址为 `http://127.0.0.1:9119`。
- 从 OpenClaw 迁移建议先 `--dry-run`，确认后再 `--preset full --migrate-secrets`。
- 升级建议用 `hermes update --backup`，升级后执行 `hermes doctor` 和 `hermes gateway status`。
- 飞书集成优先选择 WebSocket 模式，不需要公网 Webhook，适合大多数服务器环境。
