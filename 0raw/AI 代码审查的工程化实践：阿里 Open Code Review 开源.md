---
title: "AI 代码审查的工程化实践：阿里 Open Code Review 开源"
source: "https://mp.weixin.qq.com/s/YzZE4GlDabV-rPGCEXJqjw?scene=1"
author:
  - "[[稻草人&QClaw]]"
published:
created: 2026-06-05
description: "代码审查是保障软件质量的关键环节，但人工审查受限于时间和精力，往往只能覆盖部分变更。"
tags:
  - "clippings"
---
稻草人&QClaw *2026年5月31日 12:16*

代码审查是保障软件质量的关键环节，但人工审查受限于时间和精力，往往只能覆盖部分变更。AI 驱动的代码审查本应补上这个缺口，但实际使用中暴露出的问题比想象中多。

阿里集团内部运行了两年的 AI 代码审查助手，近期以 Open Code Review（OCR）的名字开源。这个工具在内部服务了数万开发者，累计识别数百万个代码缺陷。它的设计思路与通用 Agent 方案有本质区别。

## 通用 Agent 做代码审查的三个问题

用 Claude Code 等通用 Agent 配合 Skills 做代码审查，实践中会反复遇到以下问题：

覆盖不全 变更文件较多时，Agent 倾向于只审查部分文件，遗漏没有固定的规律，难以预测。

位置漂移 审查意见标注的行号与实际代码位置存在偏移，开发者需要额外花时间定位。

效果不稳定 提示词的细微变化会导致审查质量大幅波动，难以在同一项目中保持一致的审查标准。

这些问题的根因是：纯语言驱动的架构无法对审查流程形成强约束。

## 确定性工程与 Agent 的混合架构

OCR 的核心设计是将确定性工程与 Agent 能力结合，各负责自己擅长的部分。

确定性工程处理"不能出错"的环节：

- **文件筛选** ：工程逻辑决定哪些文件需要审查、哪些应该过滤，不依赖模型判断。
- **关联文件打包** ：关联文件归为同一审查单元。例如 `message_en.properties` 与 `message_zh.properties` 会被打包在一起审查。每个包作为独立的 sub-agent 任务运行，上下文隔离。这种分治策略在大型变更中表现稳定，同时支持并发。
- **规则匹配** ：基于模板引擎对不同文件类型匹配对应的审查规则，让模型注意力聚焦在相关内容上，减少信息噪声。相比用自然语言描述规则，模板引擎的匹配行为可预期、可复现。
- **定位与反思模块** ：独立的评论定位模块和评论反思模块，分别解决位置偏移和内容不准的问题。

Agent 处理需要灵活判断的环节：

- **场景化提示词** ：针对代码审查场景深度优化提示词模板，同时控制 Token 消耗。
- **专属工具集** ：基于线上工具调用轨迹的分析数据（调用频率分布、重复调用率、新增工具对链路的影响等），对通用 Agent 工具集进行取舍和拆分，沉淀出一套行为可预期的专属工具集。

## 安装与使用

```sql
npm install -g @alibaba-group/open-code-review
```

配置模型端点后即可使用：

```bash
ocr config set llm.url https://api.anthropic.com/v1/messagesocr config set llm.auth_token your-api-key-hereocr config set llm.model claude-opus-4-6ocr config set llm.use_anthropic true
```

三种审查模式：

```css
工作区变更ocr review分支对比ocr review --from main --to feature-branch单个提交ocr review --commit abc123
```

输出支持 text 和 JSON 两种格式。JSON 格式适合接入 CI/CD 或其他自动化流程。

## 集成到编程 Agent

OCR 支持三种方式集成到 AI 编程工具中：

1. Skill 安装：
	```css
	npx skills add alibaba/open-code-review --skill open-code-review
	```
2. Claude Code Plugin：
	```bash
	/plugin marketplace add\` 和 \`/plugin install
	```
3. 命令文件：直接复制 \`.md\` 文件到 \`.claude/commands/\` 目录

审查规则采用四层优先级链：CLI 参数 > 项目级配置 > 全局配置 > 系统默认。规则文件为 JSON 格式，用 glob 模式匹配文件路径，首匹配生效。项目级配置可提交到 git，团队共享审查标准。

## 项目信息

- **仓库** ：github.com/alibaba/open-code-review
- **协议** ：Apache-2.0
- **安装** ： `npm install -g @alibaba-group/open-code-review`

收录于AI

作者提示: 内容由AI生成

继续滑动看下一个

80后程序员

向上滑动看下一个