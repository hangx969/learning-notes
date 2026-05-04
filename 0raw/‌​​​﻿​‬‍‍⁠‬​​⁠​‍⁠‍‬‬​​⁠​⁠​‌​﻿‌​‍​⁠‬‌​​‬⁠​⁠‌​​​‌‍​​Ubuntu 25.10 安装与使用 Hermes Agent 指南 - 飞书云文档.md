---
title: "‌​​​﻿​‬‍‍⁠‬​​⁠​‍⁠‍‬‬​​⁠​⁠​‌​﻿‌​‍​⁠‬‌​​‬⁠​⁠‌​​​‌‍​​Ubuntu 25.10 安装与使用 Hermes Agent 指南 - 飞书云文档"
source: "https://jcnrb2wjsrl6.feishu.cn/docx/Mk3vdmmmJobjOjxxgRBcsTsun5g"
author:
published:
created: 2026-05-04
description:
tags:
  - "clippings"
---
DSHX

Ubuntu 25.10 安装与使用 Hermes Agent 指南

最近修改: 2 分钟前

0

输入“/”快速插入内容

## Ubuntu 25.10 安装与使用 Hermes Agent 指南

HX

今天修改

<table><colgroup><col width="350"> <col width="350"></colgroup><tbody><tr><td rowspan="1" colspan="1"></td><td rowspan="1" colspan="1"></td></tr><tr><td rowspan="1" colspan="1"></td><td rowspan="1" colspan="1"></td></tr><tr><td rowspan="1" colspan="1"></td><td rowspan="1" colspan="1"></td></tr><tr><td rowspan="1" colspan="1"><p>~/.openclaw/workspace/USER.md</p></td><td rowspan="1" colspan="1"><p>~/.hermes/memories/USER.md</p></td></tr><tr><td rowspan="1" colspan="1"><p>~/.openclaw/workspace/memory/*.md</p></td><td rowspan="1" colspan="1"><p>合并进 ~/.hermes/memories/MEMORY.md</p></td></tr><tr><td rowspan="1" colspan="1"><p>OpenClaw Skills</p></td><td rowspan="1" colspan="1"><p>~/.hermes/skills/openclaw-imports/</p></td></tr><tr><td rowspan="1" colspan="1"><p>模型配置</p></td><td rowspan="1" colspan="1"><p>~/.hermes/config.yaml</p></td></tr><tr><td rowspan="1" colspan="1"><p>API Key / Token</p></td><td rowspan="1" colspan="1"><p>~/.hermes/.env，需 --migrate-secrets</p></td></tr><tr><td rowspan="1" colspan="1"><p>命令 allowlist</p></td><td rowspan="1" colspan="1"><p>合并进 ~/.hermes/config.yaml</p></td></tr><tr><td rowspan="1" colspan="1"><p>TTS 资源</p></td><td rowspan="1" colspan="1"><p>~/.hermes/tts/</p></td></tr></tbody></table>

3.6 迁移后验证

迁移完成后建议执行：

hermes doctor

hermes config check

hermes --version

如果使用消息网关：

hermes gateway status

如果迁移了 Skills，建议检查：

hermes skills list

3.7 迁移注意事项

•

复杂的 OpenClaw 自定义 Skill 可能需要人工检查和改写。

•

OpenClaw 插件配置不一定能 1:1 迁移成 Hermes 原生集成。

•

飞书 Channel 建议迁移后重新按 Hermes 官方 Feishu/Lark Setup 配置一遍。

•

不建议让 OpenClaw 和 Hermes 同时接管同一个飞书 Bot，否则可能出现重复回复、会话状态混乱或事件竞争。

•

可先让 OpenClaw 和 Hermes 并行运行，但使用不同 Bot 或不同 Channel 做灰度验证。

4\. Hermes Agent 怎么升级

Hermes Agent 官方提供 hermes update 系列命令。

4.1 检查是否有更新

hermes update --check

该命令用于检查本地是否落后于远端版本，不修改文件，也不会重启 Gateway。

4.2 带备份升级，推荐方式

hermes update --backup

该方式会在升级前备份 Hermes Home，包括配置、认证、会话、Skills、配对状态等关键数据。

也可以在配置中长期启用升级备份：

评论（0）

跳转至首条评论

真诚点赞，手留余香

0 字

- 上传日志

- 联系客服

- 功能更新

- 帮助中心

- 效率指南