---
title: "Ubuntu 25.10 安装与使用 Hermes Agent 指南"
source: "https://jcnrb2wjsrl6.feishu.cn/docx/Mk3vdmmmJobjOjxxgRBcsTsun5g"
created: 2026-05-04
description: "Hermes Agent 在 Ubuntu 25.10 上的安装使用指南，包含 OpenClaw 迁移和升级流程"
tags:
  - clippings
  - AI/hermes-agent
---

# Ubuntu 25.10 安装与使用 Hermes Agent 指南

> 注：原文来自飞书文档，剪藏时仅截取到 3.6 节之后的内容，前面章节（安装部分）缺失。完整文档请访问 [飞书原文](https://jcnrb2wjsrl6.feishu.cn/docx/Mk3vdmmmJobjOjxxgRBcsTsun5g)。

---

## OpenClaw → Hermes 迁移路径对照表

| OpenClaw 路径 | Hermes 路径 |
| --- | --- |
| `~/.openclaw/workspace/USER.md` | `~/.hermes/memories/USER.md` |
| `~/.openclaw/workspace/memory/*.md` | 合并进 `~/.hermes/memories/MEMORY.md` |
| OpenClaw Skills | `~/.hermes/skills/openclaw-imports/` |
| 模型配置 | `~/.hermes/config.yaml` |
| API Key / Token | `~/.hermes/.env`，需 `--migrate-secrets` |
| 命令 allowlist | 合并进 `~/.hermes/config.yaml` |
| TTS 资源 | `~/.hermes/tts/` |

## 3.6 迁移后验证

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

## 3.7 迁移注意事项

- 复杂的 OpenClaw 自定义 Skill 可能需要人工检查和改写。
- OpenClaw 插件配置不一定能 1:1 迁移成 Hermes 原生集成。
- 飞书 Channel 建议迁移后重新按 Hermes 官方 Feishu/Lark Setup 配置一遍。
- 不建议让 OpenClaw 和 Hermes 同时接管同一个飞书 Bot，否则可能出现重复回复、会话状态混乱或事件竞争。
- 可先让 OpenClaw 和 Hermes 并行运行，但使用不同 Bot 或不同 Channel 做灰度验证。

---

## 4. Hermes Agent 升级

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

也可以在配置中长期启用升级备份。
