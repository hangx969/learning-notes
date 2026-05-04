---
title: "Hermes Agent全解析：与OpenClaw对比及飞书接入指南"
source: "https://www.feishu.cn/content/article/7628541877674953666"
author:
  - "飞书官方"
created: 2026-05-04
description: "深度剖析 Hermes Agent 五大核心架构组件，对比 OpenClaw 工程化设计差异，详解如何通过飞书 Bot 与飞书 CLI 让 AI Agent 直接在飞书中执行任务。"
tags:
  - AI/hermes-agent
  - AI/openclaw
  - AI/agent-architecture
aliases:
  - Hermes Agent vs OpenClaw
  - Hermes Agent 架构解析
---

# Hermes Agent 全解析：与 OpenClaw 对比及飞书接入指南

2025 年以来，AI Agent 从概念验证走向工程化落地，开源社区涌现出大量框架级项目。其中，Nous Research 推出的 Hermes Agent 和社区驱动的 OpenClaw 是两个值得深入研究的标杆：前者以"会自我成长的 Agent"为核心定位，35.7k Star，3,496 次提交，317 位贡献者；后者是当前 GitHub 上最受欢迎的个人 AI 助手项目之一，352k Star，29,172 次提交，已发展为一个覆盖全平台的成熟产品。

两个项目在技术栈、架构理念和产品定位上走了截然不同的路径。本文将以 Hermes Agent 的源码为主线进行深度架构剖析，然后从工程化维度与 OpenClaw 进行结构化对比，最后详解如何将 Hermes Agent 接入飞书 Bot 和飞书 CLI。

---

## 一、Hermes Agent 是什么

> 一句话理解：Hermes 是一个运行在你自己服务器上、用得越久越聪明的开源 AI Agent。

Hermes 由 AI 研究实验室 Nous Research 开发（曾获 Paradigm 领投 6500 万美元融资），基于自研 Hermes 模型家族构建。与一般 Agent 不同，它有一套闭环学习机制：

- **记住跨会话的上下文**：通过 FTS5 全文搜索 + LLM 摘要实现跨会话真实召回，能搜索数周前的对话细节
- **自动沉淀技能文档**：完成复杂任务后，将经验自动沉淀为可复用的"技能文档"
- **在使用中持续自我改进**：技能在使用中会持续优化，形成越用越好用的正向循环

它支持 400+ 模型（含本地部署），通过 Telegram、Discord、Slack、飞书等 8 个平台与用户交互，可 7×24 小时驻留在服务器上自主运行。

---

## 二、Hermes Agent 五层核心架构深度剖析

从源码目录结构和模块依赖链来看，Hermes Agent 的架构可以抽象为五个层次，依赖关系单向自下而上，工具注册层是整个系统的"脊柱"。

### 2.1 入口与编排层

负责与用户的交互入口和跨平台消息调度：

- **HermesCLI 类**（`cli.py`）：交互式终端编排器，基于 `prompt_toolkit` 实现 TUI
- **GatewayRunner 类**（`gateway/run.py`）：消息平台网关入口，管理所有平台适配器的生命周期
- **hermes_cli/main.py**：全局入口点，所有 `hermes` 子命令的调度中心

CLI 和 Gateway 两个入口共享同一套 Agent 核心，只是交互方式不同——前者面向终端用户，后者面向消息平台。

### 2.2 Agent 核心层

`AIAgent` 类是整个系统最核心的抽象，核心方法 `run_conversation()` 实现了一个**完全同步的对话循环**：

```
调用 LLM → 获取响应 → 如有工具调用则逐一执行 → 追加结果到消息列表 → 重复
```

**为什么选择同步而非异步？** 这是深思熟虑的工程决策。AI Agent 的核心瓶颈是 LLM API 调用的延迟，而非 I/O 并发。同步循环让代码更容易推理、调试和维护。当需要并行时（如子 Agent 批量执行），通过 `ThreadPoolExecutor` 显式并行。

关键设计：

- **迭代预算机制**：子 Agent 获得独立预算，不会消耗父 Agent 的配额，防止单一任务耗尽全局资源
- **消息格式遵循 OpenAI 标准**：所有消息使用 `{"role": "system/user/assistant/tool"}` 格式，多模型切换几乎无摩擦
- **参数类型强转**：`coerce_tool_args()` 函数将 LLM 返回的字符串参数与 JSON Schema 比对，自动安全强转

### 2.3 工具与注册层

> 工具注册表是整个系统最优雅的部分之一。

核心是 `ToolRegistry` 单例，每个工具文件在模块导入时调用 `registry.register()` 声明自己的 Schema、处理器、工具集归属和可用性检查函数。

**添加新工具只需三步：**

1. 创建工具文件并调用 `registry.register()`
2. 在 `model_tools.py` 的发现列表中添加导入
3. 在 `toolsets.py` 中将工具加入适当的工具集

**运行时可用性检查**是精髓所在：需要 API Key 的工具会在 Key 未配置时自动隐藏而非报错。这种"优雅降级"设计让缺少某些依赖时 Agent 仍可运行。

**动态 Schema 重建**同样精巧：`get_tool_definitions()` 会根据实际可用工具动态重建某些工具的 Schema。例如，`execute_code` 工具的描述会列出"沙箱中可用的工具"——如果 `web_search` 的 API Key 未配置，它就不会出现在描述中，从而避免模型产生"幻觉工具调用"。

### 2.4 状态与持久化层

- **SessionDB 类**（`hermes_state.py`）：SQLite 会话存储，启用 WAL 模式支持并发读和单写，FTS5 全文搜索覆盖所有历史会话
- **MemoryStore 类**（`tools/memory_tool.py`）：有界策展式记忆，`MEMORY.md`（Agent 笔记）和 `USER.md`（用户偏好）分离设计
- **Cron 调度器**：基于文件锁的定时任务调度，支持自然语言任务定义、多平台交付和技能注入

### 2.5 平台适配层

- **gateway/platforms/**：Telegram、Discord、Slack、WhatsApp、Signal 等平台适配器，单进程管理所有平台适配器生命周期
- **acp_adapter/**：VS Code / Zed / JetBrains 编辑器集成
- **environments/**：终端后端——local、Docker、SSH、Modal、Daytona、Singularity

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260504234800261.png)

---

## 三、记忆系统：为何"越用越聪明"

Hermes Agent 的记忆系统是其"自我成长"能力的核心支撑。

### 3.1 两个记忆存储的分离设计

- **MEMORY.md**：存储 Agent 的个人笔记（环境事实、项目惯例、工具特性、所学知识）
- **USER.md**：存储对用户的了解（偏好、沟通风格、工作流习惯）

这种分离让 Agent 可以独立管理"关于世界的知识"和"关于人的知识"。

### 3.2 有界设计的深意

记忆有字符数上限（MEMORY.md 约 2200 字符，USER.md 约 1375 字符）。这不是技术限制而是设计哲学——无限记忆看似更强大，但实际上会导致系统提示膨胀、检索噪声增大、前缀缓存失效等问题。

> "有限资源"的约束迫使 Agent 学会优先级管理：什么值得记住，什么可以遗忘。

### 3.3 冻结快照模式

`MemoryStore` 在 `load_from_disk()` 时捕获快照用于系统提示注入，之后的写入立即持久化但不改变当前会话的系统提示。这保证了 Anthropic 等支持前缀缓存的 LLM 在整个会话期间缓存有效，大幅降低成本。

---

## 四、子 Agent 委托：隔离执行与上下文零泄漏

`delegate_task` 工具实现了一个精心设计的子 Agent 系统。

**隔离原则**：每个子 Agent 获得全新的对话（不继承父上下文）、自己的 `task_id`（独立的文件操作缓存）、受限的工具集（`delegate_task`、`clarify`、`memory` 等危险工具总是被剥离）。

**深度限制**：最大委托深度为 2（父 → 子 → 孙辈被拒绝），防止递归委托导致的资源失控。

**并行执行**：批量模式下最多 3 个子 Agent 并行运行，使用 `ThreadPoolExecutor`。每个子 Agent 的进度通过回调实时传递给父 Agent 的 UI（CLI 显示树形视图）。

---

## 五、Hermes Agent vs OpenClaw：核心差异对比

两个项目代表了 AI Agent 工程化的两条截然不同的路径。

### 5.1 运行时形态：轻量后端 vs 全平台产品

| 维度 | Hermes Agent | OpenClaw |
|------|-------------|---------|
| 主语言 | Python 93.6% | TypeScript 90.3% |
| 核心架构 | Python 进程 + SQLite | Node.js Gateway + WebSocket |
| 入口形态 | CLI + Gateway 两个入口 | Gateway 控制平面 + 分布式 Node |
| 多平台覆盖 | Telegram/Discord/Slack/飞书等 8 个 | 26+ 消息渠道 + macOS/iOS/Android 原生应用 |
| 特色能力 | 无服务器持久化（Modal/Daytona） | Voice Wake、PTT、Talk Mode、Canvas |

> 本质差异：Hermes Agent 是"轻量后端 + 重 Agent 循环"，OpenClaw 是"重 Gateway 平台 + 分布式 Node 架构"。

### 5.2 工具系统：自注册 vs 插件生态

- **Hermes Agent**：`ToolRegistry` 单例为核心，支持自注册、工具集组合、运行时可用性检查和动态 Schema 重建（防止模型幻觉工具调用）
- **OpenClaw**：更重的插件化路线——npm 包分发插件，完整沙箱系统（off/non-main/all 三级）、工具文件系统硬化、完整 ACP 协议支持和插件信任模型

> 本质差异：Hermes Agent 偏向"开发者友好的扩展点"，OpenClaw 偏向"产品级的插件生态和运维体验"。

### 5.3 记忆系统：有机进化 vs 模块化

- **Hermes Agent**：有界约束迫使 Agent 学会信息管理，冻结快照模式保证前缀缓存效率
- **OpenClaw**：记忆是"可替换插件槽"，但缺少 Hermes Agent 那种"从经验中创建技能"的闭环学习机制

### 5.4 安全模型：选择性信任 vs 默认安全

- **Hermes Agent**：命令审批 + DM 配对 + 注入扫描，适合技术用户的自托管场景
- **OpenClaw**：完整信任模型文档（SECURITY.md 被评价为"开源 Agent 项目中最完善的安全文档之一"）、分级沙箱（off/non-main/all）、Gateway + Node 明确信任边界、`security audit --deep` 自动修复

---

## 六、如何接入飞书 Bot 和飞书 CLI

### 6.1 三步接入飞书

**第一步：安装 Hermes Agent**

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

**第二步：初始化 Hermes，连接飞书**

```bash
hermes setup
```

跟着向导操作：

1. 是否导入 OpenClaw → 可选否（N）

![](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260504234828996.png)

2. 选择快速安装 → 选择模型 → 配置模型 API

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/Wr3nbxRECoPRFFxnTj2cyliUnjh.png~tplv-jbbdkfciu3-image:0:0.image)

3. 选择配置 IM 工具

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/FqaGbKFT3ogJtkxBhiac0o4InD6.png~tplv-jbbdkfciu3-image:0:0.image)

4. 选择飞书（空格选中，Enter 下一步）

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/GMDObpkgJo4O7ZxjtricItbDnce.png~tplv-jbbdkfciu3-image:0:0.image)

5. 选择飞书扫码连接飞书

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/YtE2bqwMmopDNhx8WKicUPs2nGg.png~tplv-jbbdkfciu3-image:0:0.image)

6. 链接复制到浏览器或扫码配置飞书

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/L2K2bCQIzouwaqxy0oucQJsQn2g.png~tplv-jbbdkfciu3-image:0:0.image)

7. 选择新建飞书机器人或使用已有机器人

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/XI0EbziiooWkApxiDyNc8bIinHc.png~tplv-jbbdkfciu3-image:0:0.image)

8. 看到提示后，回到终端

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/RCrJbpuchou9VuxhEvPcdmFqnzh.png~tplv-jbbdkfciu3-image:0:0.image)

9. 设置消息配对方式（默认：私信配对）

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/KYXFblxCVowD5KxzIDTcbcFlnDg.png~tplv-jbbdkfciu3-image:0:0.image)

10. 设置群响应方式（默认：需 @bot）

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/UQhIblkgqo7DEuxd2V0cafkAn4g.png~tplv-jbbdkfciu3-image:0:0.image)

11. 定时任务推送群（可先跳过）

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/MP4tbbNk0ozLdDxPITDcJedvnSb.png~tplv-jbbdkfciu3-image:0:0.image)

12. 重启网关、启动 Hermes 对话

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/IyQCbOHVUoQ4Mkxg8Ylc3qUonue.png~tplv-jbbdkfciu3-image:0:0.image)

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/IHvObjsMOo7fLtxLEsHc9kCYnjc.png~tplv-jbbdkfciu3-image:0:0.image)

13. 在飞书中搜索 Bot 打招呼，获得配对码

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/A0iwbhMVDoerVLxaLyvcXfAZn0o.png~tplv-jbbdkfciu3-image:0:0.image)

14. 在终端对话完成配对

![](https://p1-hera.feishucdn.com/tos-cn-i-jbbdkfciu3/hera-doc/MlpybrfUUogaIGxRzmHcN2mDnJg.png~tplv-jbbdkfciu3-image:0:0.image)

**第三步：安装飞书 CLI**

> 💡 为什么需要飞书 CLI？
>
> AI 模型聪明，但不等于有用——如果 Agent 不知道你开了什么会、跟谁聊了什么、手上有哪些待办，它就只能给通用回答。飞书 CLI 同时解决两个问题：给 Agent **context**（上下文），也给它**"手"**（操作能力）。

飞书 CLI 提供的能力：

- **Context（上下文）**：读取即时消息、云文档、电子表格、多维表格、日历、妙记、邮箱、知识库、任务、通讯录
- **手（操作）**：创建文档、发送消息、建多维表格、约会议、搜索知识库、处理邮件

安装方式——告诉 Hermes 机器人：

```
请帮我安装飞书CLI：https://github.com/larksuite/cli
```

### 6.2 接入飞书后能做什么

| 场景 | 痛点 | Hermes 解法 |
|------|------|------------|
| **一句话整理会议纪要** | 每周 1-2h 手动整理散落在妙记里的会议记录 | 自动拉取妙记，提取待办/决策/讨论，按统一格式写入飞书文档，还能推送群聊 |
| **AI 隐形审稿人** | 改别人方案要反复沟通，自己写的难发现漏洞 | 以评论形式指出逻辑漏洞/数据缺失/表述不清，可设"仅自己可见" |
| **妙记视频→剪辑精华** | 会议录制没人看，手动剪辑工作量大 | 下载妙记视频+逐字稿，识别高光片段，FFmpeg 剪辑+自动字幕 |
| **Markdown→精美飞书文档** | MD 搬格式到飞书费时费力 | 自动转换保留高亮/表格/代码块，还能生成 Mermaid 架构图插入文档 |

> Hermes 加持：处理过几次后，会自动沉淀"技能文档"——记住你偏好的格式、关注的信息类型、推送目标群。再执行时速度更快、结果更准。

---

## 七、总结：如何选择

| 你的需求 | 推荐选择 |
|---------|---------|
| 需要长期记忆和自我进化 | Hermes Agent |
| 需要最大社区生态和多 Agent 编排 | OpenClaw |
| 面向更广泛用户的商业产品部署 | 飞书 OpenClaw（企业级部署方案） |
| AI Agent 研究和训练数据生成 | Hermes Agent（轨迹压缩 + RL 集成） |

两个项目不是替代关系，不少用户同时使用 Hermes 和 OpenClaw，各取所长——用 Hermes 的自我进化能力处理需要长期记忆的研究任务，用 OpenClaw 的多平台覆盖处理日常助手场景。
