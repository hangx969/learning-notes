---
title: "Markdown Viewer Skills：让 AI 写文档时顺手把图也画了"
source: "https://mp.weixin.qq.com/s/gdIO1bWwjWUAceWcaovx9A"
created: 2026-06-28
tags:
  - ai-visual
  - skills
  - markdown
  - diagram
---

# Markdown Viewer Skills：AI 文档配图

## 解决什么问题

技术文档的痛点不在文字，而在图——架构图、流程图、部署图这些，总要切到另一个工具（draw.io、ProcessOn）去画，改一次流程图也跟着重画一遍。文字、图、表散在不同工具之间，最后 README 里留一张过期截图，Notion 里有一版流程图，draw.io 文件不知道谁本地还有。

Markdown Viewer 的 Skills 仓库把画图能力塞回 AI 编程助手的工作流里：让 AI coding agent 在 Markdown 里直接创建图表和可视化内容。图还是代码块，留在 Markdown 里，文档改了图也可以继续让 AI 改。

## 核心能力：按场景拆分的 Skill 集合

不是笼统地"让 AI 生成 Mermaid"，而是按具体场景拆成一组技能：

| 技能类别 | 覆盖内容 | 渲染引擎 |
|---------|---------|---------|
| **UML** | 类图、时序图、用例图、状态图、活动图 | PlantUML |
| **云架构** | AWS、Azure、GCP、Kubernetes 架构图（带官方图标） | PlantUML + 云图标库 |
| **网络拓扑** | 网络拓扑图 | Graphviz |
| **数据分析** | ETL、数据湖、实时流、数仓、BI 场景 | Vega / Vega-Lite |
| **信息卡片 (infocard)** | 带排版的 HTML 信息卡片，直接嵌入 Markdown | HTML（非代码块） |

### 关键设计点

- **窄比宽有用**：不是对 AI 说"帮我画个架构图"让它自由发挥，而是在文档上下文里，让它按云架构图、部署图、类图、状态图这些**固定范式**去出图
- **图是代码块**：图留在 Markdown 里作为代码块，可以 diff、可以 review、可以版本管理
- **文档改了图也改**：和文字在同一个文件里，AI 改文档时可以顺手更新图
- **可导出高清图片**：Markdown Viewer 支持把这些图表转成高分辨率图片，继续导出到 Word 等格式

### infocard 技能

不是流程图，而是在 Markdown 里生成带排版的 HTML 信息卡片。要求直接嵌入 HTML（不包在代码块里），会按内容密度和版式去组织卡片。适合项目概览、团队介绍、功能对比等需要视觉排版的场景。

## 支持的渲染引擎

- PlantUML
- Vega / Vega-Lite
- drawio
- Canvas
- Graphviz
- LaTeX

## 定位与局限

**适合**：技术文档配图的"第一版"——先让图出现，和文字待在一起，再慢慢改

**不适合**：复杂系统图的精修——架构边界、调用方向、状态流转这些地方错一根线就会误导别人，最终视觉稿还是要回到专门工具里

**核心价值**：把技术文档里最烦的那一步提前消掉——先让图出现，而不是写到一半跑去开另一个软件

## 安装与使用

```bash
# GitHub 仓库
# https://github.com/markdown-viewer/skills

# 作为 Claude Code / Codex / Cursor 的 Skill 安装
# 装一个 skill，继续在原来的编辑器里写文档，让 AI 在 Markdown 里补图
```

适用于 Claude Code、Codex、Cursor 等 AI 编程工具用户。
