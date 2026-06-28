---
title: "OpenAI Codex 可视化配置生成器"
source: "https://config.codexapp.cc/#"
author:
  - "[[config.codexapp.cc]]"
published:
created: 2026-06-28
description: "OpenAI Codex 可视化配置生成器:在网页上填写表单即可生成 config.toml、requirements.toml、环境变量和 .rules 文件。涵盖权限 profiles、MCP 服务器、Hooks、Providers、沙箱、网络代理等全部配置项,内置真实场景的配置案例,直接复制即用。"
tags:
  - "clippings"
---
## 基础配置

Codex CLI 与 IDE 扩展共享的顶层标量字段。

默认模型 `model`

评审模型 `review_model`

/review 使用的模型覆盖(默认当前会话模型)。

审批策略 `approval_policy`

沙箱级别 `sandbox_mode`

推理强度 `model_reasoning_effort`

xhigh 视模型而定。

Plan 模式推理 `plan_mode_reasoning_effort`

未设置时用内置预设。

沟通风格 `personality`

网页搜索 `web_search`

自动压缩 token 阈值 `model_auto_compact_token_limit`

服务层级 `service_tier`

如 flex / fast。

日志目录 `log_dir`

SQLite 目录 `sqlite_home`

提交归属 `commit_attribution`

默认 Codex <noreply@openai.com>;下方开关设为「禁用」则输出 commit\_attribution = ""

## 模型与提供方

选择内置/自定义 `model_provider`,或用 `openai_base_url` 把内置 OpenAI 提供方指向代理/路由。自定义 provider 不能复用保留 id:`openai` 、 `ollama` 、 `lmstudio` 。

当前提供方 `model_provider`

指向下方自定义 provider 的 id,或内置 amazon-bedrock。

OpenAI 基础 URL `openai_base_url`

仅改内置 openai 提供方的 base URL,无需新建 provider。

OSS 默认提供方 `oss_provider`

配合 --oss 使用;未指定 provider 时的本地默认。

暂无自定义 provider。常见用法:proxy / local\_ollama / mistral / azure / openaidr。

## 模型调优

调整推理摘要、响应详略、上下文窗口等。 `model_verbosity` 仅对 Responses API 生效。

## 审批与沙箱(高级)

细粒度审批、可写工作区、自动审核策略。基础 `approval_policy` / `sandbox_mode` 见「基础配置」分组。

审核者 `approvals_reviewer`

把符合条件的交互审批请求交给自动审核(不改沙箱边界)。

## 特性开关

在 `[features]` 中切换可选/实验性能力。点击开关循环: 未设置 → 启用 → 禁用 → 未设置。

## 网络代理(network\_proxy)

`[features.network_proxy]` 启用沙箱化网络。未设置 allow 规则前无任何外部目的地可达。

域名规则 `domains`

暂无条目

支持精确主机、\*.example.com(子域)、\*\*.example.com(顶级+子域)、\*(全局)。deny 优先。

Unix socket 规则 `unix_sockets`

暂无条目

HTTP 监听 URL `proxy_url`

SOCKS5 监听 URL `socks_url`

## TUI 快捷键

在 `[tui.keymap.*]` 下自定义终端快捷键。值可以是单个按键或按键数组,用逗号分隔多个。清空则删除该绑定。

\[tui.keymap.global\]

open\_transcript

\[tui.keymap.composer\]

submit

submit\_newline

history\_next

history\_prev

\[tui.keymap.chat\]

interrupt\_turn

edit\_message

## TUI 选项

`[tui]` 下的通知、动画、滚动屏等行为。快捷键见「TUI 快捷键」分组。

通知 `notifications`

启用/禁用或限定事件类型。

通知方式 `notification_method`

auto 优先 OSC9,不支持时回退 BEL。

通知触发条件 `notification_condition`

仅失焦时触发,或总是触发。

备用屏幕 `alternate_screen`

设为 never 可保留终端回滚历史。

## 命令环境策略

`[shell_environment_policy]` 控制 Codex 把哪些环境变量转发给子进程。 从干净起点(`inherit = "none"`)或精简集合开始,再叠加 include/exclude/override。

继承集合 `inherit`

默认从当前 shell 继承的环境变量范围。

强制设置 `set`

暂无条目

内联表,直接覆盖/注入指定变量。

仅包含(allowlist) `include_only`

启用后只转发列出的变量,例如只给 PATH 和 HOME。

排除(blocklist) `exclude`

从继承集合中剔除这些变量,大小写不敏感 glob。

## Windows 沙箱

在 Windows 上原生运行 Codex 时,设置 `[windows]` 下的原生沙箱模式。

原生沙箱模式 `sandbox`

推荐 elevated;仅在管理员权限不可用或安装失败时使用 unelevated。

## 权限 Profiles

完整 `[permissions.<name>]` schema:extends / workspace\_roots / filesystem / network 表。

默认权限 `default_permissions`

预设模板(一键载入《Permissions · Common profiles》)

暂无自定义 profile。

## MCP Servers

模型上下文协议服务器,输出为 `[[mcp_servers]]` 数组表。本地命令型填 command+args,远程型填 url。

还没有 MCP server。点击「添加」开始配置。

## Hooks 钩子

生命周期钩子,在关键事件触发时执行命令。输出为 inline `[hooks]` 下的 `[[hooks.<event>]]` 数组表。

暂无 hook。

## Agents(子代理)

`[agents]` 控制多线程上限与嵌套深度,并定义命名角色 `[agents.<name>]` 。

最大并发线程 `max_threads`

默认 6。

最大嵌套深度 `max_depth`

根会话从 0 开始;默认 1。

作业超时(秒) `job_max_runtime_seconds`

spawn\_agents\_on\_csv 默认 1800。

## Memories(记忆)

`[memories]` 控制记忆生成、使用与合并的限额。默认关闭,需在 features.memories 启用。

合并保留上限 `max_raw_memories_for_consolidation`

默认 256,上限 4096。

最大未使用天数 `max_unused_days`

默认 30,0-365。

线程最大年龄 `max_rollout_age_days`

默认 30,0-90。

每次启动候选数 `max_rollouts_per_startup`

默认 16,上限 128。

最小空闲小时 `min_rollout_idle_hours`

默认 6,1-48。

最小限流剩余(%) `min_rate_limit_remaining_percent`

默认 25,0-100。

抽取模型 `extract_model`

合并模型 `consolidation_model`

## Apps(应用/连接器)

`[apps._default]` 默认值 + `[apps.<id>]` 逐个覆盖。

\[apps.\_default\]

## Tools(工具配置)

`[tools]` 配置 web\_search 工具(对象形式)与 view\_image。

搜索上下文大小 `context_size`

允许的域名 `allowed_domains`

位置 - 国家 `location.country`

位置 - 地区 `location.region`

位置 - 城市 `location.city`

位置 - 时区 `location.timezone`

## Skills(技能)

`[[skills.config]]` 数组,逐个覆盖技能的启用状态。

暂无技能条目。

## Plugins(插件 MCP)

顶层 `[plugins."id@source"]` 启用/禁用已安装插件;嵌套 `[plugins.<plugin>.mcp_servers.<server>]` 覆盖 MCP 服务器配置。

插件启用/禁用

插件 MCP 服务器覆盖

暂无插件服务器条目。

## 可观测性(OTel)

`[otel]` 启用 OpenTelemetry 日志导出,追踪 API 请求、SSE 事件、工具审批等。默认禁用。

环境标签 `environment`

默认 "dev"。

顶层 exporter 简写 `exporter`

也可在下方配置复杂的 otlp-http / otlp-grpc 内联表。

导出器类型(详细)

设置后会生成 exporter = { otlp-xxx = {... } } 内联表。

Trace exporter `trace_exporter`

none(默认)| otlp-http | otlp-grpc

Metrics exporter `metrics_exporter`

默认 statsig。

## 指令与项目文档

自定义指令、压缩 prompt、AGENTS.md 读取行为。

指令(保留) `instructions`

保留字段;推荐用 model\_instructions\_file 或 AGENTS.md。

开发者指令 `developer_instructions`

额外注入会话的开发者指令。

指令文件 `model_instructions_file`

替代内置指令(而非 AGENTS.md)。

压缩 prompt `compact_prompt`

内联覆盖历史压缩 prompt。

压缩 prompt 文件 `experimental_compact_prompt_file`

AGENTS.md 最大字节 `project_doc_max_bytes`

回退文件名 `project_doc_fallback_filenames`

AGENTS.md 缺失时尝试的其它文件名。

## 认证与凭证

登录流程 URL、凭证存储位置、OAuth 回调与登录方式约束。

ChatGPT 登录 URL `chatgpt_base_url`

覆盖 ChatGPT 登录流程的 base URL。

CLI 凭证存储 `cli_auth_credentials_store`

file(auth.json)/keyring(系统钥匙串)/auto。

MCP OAuth 凭证存储 `mcp_oauth_credentials_store`

OAuth 回调端口 `mcp_oauth_callback_port`

留空则用临时端口。

OAuth 回调 URL `mcp_oauth_callback_url`

重定向 URI 覆盖。

强制登录方式 `forced_login_method`

强制 ChatGPT workspace `forced_chatgpt_workspace_id`

## 状态与杂项

提示状态跟踪、项目信任、新手提示状态等内部记录键。

\[notice\]

model\_migrations `notice.model_migrations`

暂无条目

已确认的模型迁移 old→new 映射。

projects / tui.model\_availability\_nux

model\_availability\_nux `tui.model_availability_nux`

暂无条目

model → 整数。

## 通知 / 历史 / 分析

项目根标记 `project_root_markers`

默认 \[.git\];设为 \[\] 把当前目录当作根。

外部通知命令 `notify`

agent-turn-complete 等事件时执行的程序(数组)。

文件打开器 `file_opener`

\[history\]

持久化 `persistence`

最大字节 `max_bytes`

工具输出 token 上限 `tool_output_token_limit`

后台终端超时(ms) `background_terminal_max_timeout`