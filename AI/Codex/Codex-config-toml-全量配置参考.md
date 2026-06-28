---
title: "OpenAI Codex config.toml 全量配置参考"
source: "https://config.codexapp.cc/#"
created: 2026-06-28
tags:
  - codex
  - config
  - ai-coding
---

# OpenAI Codex config.toml 全量配置参考

> 来源：[Codex 可视化配置生成器](https://config.codexapp.cc/#)——网页表单填写即可生成 config.toml、requirements.toml、环境变量和 .rules 文件。

---

## 一、基础配置

Codex CLI 与 IDE 扩展共享的顶层标量字段。

| 字段 | 说明 | 备注 |
|------|------|------|
| `model` | 默认模型 | |
| `review_model` | /review 使用的模型覆盖 | 默认当前会话模型 |
| `approval_policy` | 审批策略 | |
| `sandbox_mode` | 沙箱级别 | |
| `model_reasoning_effort` | 推理强度 | xhigh 视模型而定 |
| `plan_mode_reasoning_effort` | Plan 模式推理强度 | 未设置时用内置预设 |
| `personality` | 沟通风格 | |
| `web_search` | 网页搜索 | |
| `model_auto_compact_token_limit` | 自动压缩 token 阈值 | |
| `service_tier` | 服务层级 | flex / fast |
| `log_dir` | 日志目录 | |
| `sqlite_home` | SQLite 目录 | |
| `commit_attribution` | 提交归属 | 默认 `Codex <noreply@openai.com>`；设为空字符串禁用 |

---

## 二、模型与提供方

选择内置/自定义 `model_provider`，或用 `openai_base_url` 把内置 OpenAI 提供方指向代理/路由。自定义 provider 不能复用保留 id：`openai`、`ollama`、`lmstudio`。

| 字段 | 说明 |
|------|------|
| `model_provider` | 指向自定义 provider 的 id，或内置 amazon-bedrock |
| `openai_base_url` | 仅改内置 openai 提供方的 base URL，无需新建 provider |
| `oss_provider` | 配合 `--oss` 使用；未指定 provider 时的本地默认 |

常见用法：proxy / local_ollama / mistral / azure / openaidr。

---

## 三、模型调优

调整推理摘要、响应详略、上下文窗口等。`model_verbosity` 仅对 Responses API 生效。

---

## 四、审批与沙箱（高级）

细粒度审批、可写工作区、自动审核策略。

| 字段 | 说明 |
|------|------|
| `approvals_reviewer` | 把符合条件的交互审批请求交给自动审核（不改沙箱边界） |

基础 `approval_policy` / `sandbox_mode` 见基础配置。

---

## 五、特性开关

在 `[features]` 中切换可选/实验性能力。点击开关循环：未设置 → 启用 → 禁用 → 未设置。

---

## 六、网络代理 (network_proxy)

`[features.network_proxy]` 启用沙箱化网络。未设置 allow 规则前无任何外部目的地可达。

| 字段 | 说明 |
|------|------|
| `domains` | 域名规则。支持精确主机、`*.example.com`（子域）、`**.example.com`（顶级+子域）、`*`（全局）。deny 优先 |
| `unix_sockets` | Unix socket 规则 |
| `proxy_url` | HTTP 监听 URL |
| `socks_url` | SOCKS5 监听 URL |

---

## 七、TUI 快捷键与选项

### 快捷键 `[tui.keymap.*]`

| 分组 | 按键 |
|------|------|
| `[tui.keymap.global]` | `open_transcript` |
| `[tui.keymap.composer]` | `submit`、`submit_newline`、`history_next`、`history_prev` |
| `[tui.keymap.chat]` | `interrupt_turn`、`edit_message` |

### TUI 选项 `[tui]`

| 字段 | 说明 |
|------|------|
| `notifications` | 启用/禁用或限定事件类型 |
| `notification_method` | auto 优先 OSC9，不支持时回退 BEL |
| `notification_condition` | 仅失焦时触发，或总是触发 |
| `alternate_screen` | 设为 never 可保留终端回滚历史 |

---

## 八、命令环境策略

`[shell_environment_policy]` 控制 Codex 把哪些环境变量转发给子进程。

| 字段 | 说明 |
|------|------|
| `inherit` | 继承集合（默认从当前 shell 继承） |
| `set` | 强制设置，内联表直接覆盖/注入指定变量 |
| `include_only` | 仅转发列出的变量（allowlist） |
| `exclude` | 从继承集合中剔除（blocklist，大小写不敏感 glob） |

---

## 九、Windows 沙箱

`[windows]` 下设置原生沙箱模式。

| 字段 | 说明 |
|------|------|
| `sandbox` | 推荐 elevated；仅在管理员权限不可用时使用 unelevated |

---

## 十、权限 Profiles

完整 `[permissions.<name>]` schema：extends / workspace_roots / filesystem / network 表。

| 字段 | 说明 |
|------|------|
| `default_permissions` | 预设模板（一键载入 Permissions · Common profiles） |

---

## 十一、MCP Servers

模型上下文协议服务器，输出为 `[[mcp_servers]]` 数组表。本地命令型填 command+args，远程型填 url。

---

## 十二、Hooks 钩子

生命周期钩子，在关键事件触发时执行命令。输出为 `[hooks]` 下的 `[[hooks.<event>]]` 数组表。

---

## 十三、Agents（子代理）

`[agents]` 控制多线程上限与嵌套深度，并定义命名角色 `[agents.<name>]`。

| 字段 | 默认值 | 说明 |
|------|:------:|------|
| `max_threads` | 6 | 最大并发线程 |
| `max_depth` | 1 | 最大嵌套深度（根会话从 0 开始） |
| `job_max_runtime_seconds` | 1800 | spawn_agents_on_csv 默认超时 |

---

## 十四、Memories（记忆）

`[memories]` 控制记忆生成、使用与合并的限额。默认关闭，需在 features.memories 启用。

| 字段 | 默认值 | 说明 |
|------|:------:|------|
| `max_raw_memories_for_consolidation` | 256 | 合并保留上限（上限 4096） |
| `max_unused_days` | 30 | 最大未使用天数（0-365） |
| `max_rollout_age_days` | 30 | 线程最大年龄（0-90） |
| `max_rollouts_per_startup` | 16 | 每次启动候选数（上限 128） |
| `min_rollout_idle_hours` | 6 | 最小空闲小时（1-48） |
| `min_rate_limit_remaining_percent` | 25 | 最小限流剩余百分比（0-100） |
| `extract_model` | — | 抽取模型 |
| `consolidation_model` | — | 合并模型 |

---

## 十五、Apps（应用/连接器）

`[apps._default]` 默认值 + `[apps.<id>]` 逐个覆盖。

---

## 十六、Tools（工具配置）

`[tools]` 配置 web_search 工具（对象形式）与 view_image。

| 字段 | 说明 |
|------|------|
| `context_size` | 搜索上下文大小 |
| `allowed_domains` | 允许的域名 |
| `location.country/region/city/timezone` | 位置信息 |

---

## 十七、Skills 与 Plugins

### Skills `[[skills.config]]`

数组，逐个覆盖技能的启用状态。

### Plugins `[plugins."id@source"]`

顶层启用/禁用已安装插件；嵌套 `[plugins.<plugin>.mcp_servers.<server>]` 覆盖 MCP 服务器配置。

---

## 十八、可观测性 (OTel)

`[otel]` 启用 OpenTelemetry 日志导出，追踪 API 请求、SSE 事件、工具审批等。默认禁用。

| 字段 | 说明 |
|------|------|
| `environment` | 环境标签，默认 "dev" |
| `exporter` | 顶层 exporter 简写 |
| `trace_exporter` | none（默认）/ otlp-http / otlp-grpc |
| `metrics_exporter` | 默认 statsig |

---

## 十九、指令与项目文档

| 字段 | 说明 |
|------|------|
| `instructions` | 保留字段；推荐用 model_instructions_file 或 AGENTS.md |
| `developer_instructions` | 额外注入会话的开发者指令 |
| `model_instructions_file` | 替代内置指令（而非 AGENTS.md） |
| `compact_prompt` | 内联覆盖历史压缩 prompt |
| `project_doc_max_bytes` | AGENTS.md 最大字节 |
| `project_doc_fallback_filenames` | AGENTS.md 缺失时尝试的其它文件名 |

---

## 二十、认证与凭证

| 字段 | 说明 |
|------|------|
| `chatgpt_base_url` | 覆盖 ChatGPT 登录流程的 base URL |
| `cli_auth_credentials_store` | file(auth.json) / keyring(系统钥匙串) / auto |
| `mcp_oauth_credentials_store` | MCP OAuth 凭证存储 |
| `mcp_oauth_callback_port` | OAuth 回调端口（留空则用临时端口） |
| `mcp_oauth_callback_url` | 重定向 URI 覆盖 |
| `forced_login_method` | 强制登录方式 |
| `forced_chatgpt_workspace_id` | 强制 ChatGPT workspace |

---

## 二十一、状态与杂项

| 字段 | 说明 |
|------|------|
| `project_root_markers` | 默认 [.git]；设为 [] 把当前目录当作根 |
| `notify` | 外部通知命令（agent-turn-complete 等事件时执行） |
| `file_opener` | 文件打开器 |
| `[history].persistence` | 持久化 |
| `[history].max_bytes` | 最大字节 |
| `tool_output_token_limit` | 工具输出 token 上限 |
| `background_terminal_max_timeout` | 后台终端超时(ms) |
