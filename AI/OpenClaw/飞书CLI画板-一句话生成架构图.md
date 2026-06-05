---
title: "飞书 CLI 画板：一句话生成架构图"
source: "https://mp.weixin.qq.com/s/kGZS9pjaiAAfhqaGEIIiJg"
created: 2026-06-05
tags:
  - AI/tools
  - feishu
  - diagram
---

# 飞书 CLI 画板：一句话生成架构图

## 核心能力

飞书 CLI 新增画板生成能力，可以通过 AI Agent（Codex、Claude Code、OpenClaw 等）**一句话生成可编辑的飞书画板**。

关键区别：生成的不是截图，而是**飞书画板本身**——每个元素是独立节点，双击改字、拖动调位置、连线关系完整保留。画板直接嵌在飞书文档里，文档沉淀了画板也跟着沉淀。

## 典型使用场景

### 产品架构图
一句话描述需求，模块分组、层级排列自动完成：

```
画一张电商后台的产品架构图，包含商品管理、订单管理、用户管理、营销活动、数据看板。
```

### 流程图与 SOP
把流程描述丢进去，流程图直接生成，每一步该谁做、怎么流转都标清楚。支持带判断逻辑的流程图。

### 思维导图
脑暴完想整理思路，把要点丢给 AI Agent，思维导图就出来了，主干分支一目了然。

### 其他图表
甘特图、组织架构图、泳道图、系统交互图——只要是结构化的图表基本都能搞定。

### 开源项目架构学习
让 AI Agent 研究开源项目后通过飞书画板呈现架构设计。

## 修改与迭代

- **手动修改**：双击节点改字，拖动调整位置
- **AI 对话修改**：直接跟 AI Agent 对话即可，比如"这个图能改成中英文双语版本吗"，自动更新到飞书在线画板

## 安装方式

### 方式一：手动安装

```bash
npx @larksuite/cli@latest install
```

### 方式二：让 AI Agent 安装

```
帮我安装飞书 CLI：https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md
```

### 方式三：飞书内置

飞书的 aily 左侧打开即可直接使用。

## 画板风格美化 Skill

开源项目地址：https://github.com/inhai-wiki/feishu-whiteboard-themes

功能：根据图的类型自动推荐合适的视觉风格，配色、排版、组件样式都会跟着变。例如：
- 技术架构图 → 科技感风格
- 产品 Roadmap → 简洁清爽风格
- 汇报用图 → 正式风格
