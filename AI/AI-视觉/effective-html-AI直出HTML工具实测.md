---
title: "effective-html：让 AI 直接输出 HTML 而非 Markdown"
source: "https://mp.weixin.qq.com/s/UpwCCgiK8BkT9P8U74x_Vw"
created: 2026-06-28
tags:
  - ai-visual
  - skills
  - html
  - effective-html
---

# effective-html：AI 直出 HTML 工具实测

## 解决什么问题

用 AI 写系统架构说明，它给你一堆 Markdown。复制到文档里看起来像那么回事，但发给同事对方问："流程图在哪？"

没有视觉呈现的架构说明，就像只给你菜谱不让你看菜。

让 AI 画图，它给一段 Mermaid 语法，粘贴到渲染器里——图出来了，但样式不是你想调就能调的，交互就更别想了。

**effective-html 做的事情极简：教 AI Agent 直接输出自包含的 HTML 文件，而不是 Markdown。** 双击打开就是排版精美的页面、可交互的图表、带暗色模式的报告。不用装任何东西——浏览器就是运行时。

## 三个 Skill，三种武器

effective-html 拆成三个独立的 Agent Skill：

### 1. html — 通用生成器

最灵活的那个。"帮我做一个项目对比报告"或"写一个功能介绍页面"——直接给你一个完整的 HTML 文件。

实测效果：卡片布局、颜色区分、表格对比，底部还有暗色模式切换按钮，切换后配色丝滑过渡，刷新页面还能记住偏好。

### 2. html-diagram — 架构图专用

最有感觉的那个。描述一个系统架构，它生成一个全屏的 SVG 交互式架构图——节点可以点击，数据流可以动画演示，请求路径能高亮显示。

**不是那种静态的框图，是真的能跑的、能交互的可视化。**

### 3. html-plan — 计划文档专用

最克制的那个。给它一段项目计划或需求描述，它整理成一个简洁实用的 HTML 页面。不会过度设计，就是干净、清晰、能看。

## 背后的设计范本

effective-html 的背后有一套叫做 "html-effectiveness" 的参考示例（作者 Thariq Shihipar）。参考库里有 20 个精心制作的 HTML 模板——从代码审查报告、设计系统文档、原型动画，到流程图、事故报告、功能开关面板。

这些不是简单的 CSS 模板。每一个都是**"AI 生成这种东西应该长什么样"的范本**。

当你用这个 Skill 的时候，AI 不是从零开始瞎猜"一个好看的 HTML 该长什么样"，它参考的是这些经过设计验证的模式。就像给 AI 一本设计规范，让它照着规范出活——效果当然比裸奔强。

## HTML vs Markdown：各自擅长什么

### HTML 赢的地方

| 优势 | 说明 |
|------|------|
| **视觉表达力** | 排版、色彩、动画、交互——Markdown 根本做不了 |
| **自包含交付** | 一个 HTML 文件就是最终产品，Markdown 永远是半成品（需要渲染器） |
| **交互性** | 架构图可以点击节点、动画展示数据流，报告里可以嵌入可切换的标签页 |

### Markdown 依然赢的地方

| 优势 | 说明 |
|------|------|
| **版本控制友好** | Git diff 看 Markdown 改了什么一目了然，HTML 的 diff 基本没法看 |
| **纯文本生态** | 搜、grep、管道处理，Markdown 天然适合，HTML 里面有太多标签噪声 |
| **写作速度** | 随手记笔记，Markdown 仍然是最快的选择 |

> effective-html 不是要替代 Markdown，而是补上了 AI 输出格式缺失的那一环。当你需要交付一个"看"的东西（报告、架构图、演示文档），HTML 是比 Markdown 更对的选择。当你需要的是"读"和"改"的纯文本，Markdown 仍然是王。

## 安装与使用

项目注册在 `skills.sh` 上，是 Claude Agent 的 Skill 格式。也兼容 `.claude-plugin` 格式，在 Claude Desktop 里可以直接作为插件加载。

```bash
# 安装所有技能
npx skills add plannotator/effective-html

# 只装架构图技能
npx skills add plannotator/effective-html --skill html-diagram

# 只装计划页技能
npx skills add plannotator/effective-html --skill html-plan
```

**项目地址**：https://github.com/plannotator/effective-html
**参考示例**：https://thariqs.github.io/html-effectiveness

## 与同类工具的定位对比

| 工具 | 定位 | 输出格式 | 适用场景 |
|------|------|---------|---------|
| **effective-html** | AI 直出自包含 HTML | HTML | 报告、架构图、演示文档 |
| **Markdown Viewer Skills** | Markdown 内嵌图表 | Markdown + 代码块 | 技术文档配图（PlantUML/Vega/Graphviz） |
| **html-anything** | AI 生成任意 HTML 页面 | HTML | 全场景 HTML 生成 |
| **Mermaid** | 文本描述生成流程图 | SVG（需渲染器） | 简单流程图/时序图 |
