---
title: "html-anything：AI 生成 HTML 全场景工具"
source: "https://mp.weixin.qq.com/s/X8ePB4OBoJFShDx4hSsdnw"
created: 2026-05-17
tags:
  - AI-视觉
  - HTML
  - ppt
  - video
---

# html-anything：AI 生成 HTML 全场景工具

## 一、项目背景

Anthropic 的 Claude Code 团队宣布，他们内部文档不再写 Markdown 了，直接写 HTML。理由是：Markdown 是写给作者看的，HTML 才是给读者看的。

随后，一个叫 html-anything 的项目在 GitHub 上火了——**已经拿到 2500+ Star**。

**它能让本地 AI Agent 帮你写 HTML。不生成 Markdown 或 PPTX，直接输出纯静态的 HTML 文件。**

![image.png](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260517223522004.png)

左侧输入需求，中间选模板，右侧实时预览。装好后你只需要做一件事：

~~~
做一份技术博客，暗色主题，要有代码示例和数据图表
~~~

AI 自动选模板、应用设计约束、输出完整 HTML 文件。

- 开源地址：https://github.com/nexu-io/html-anything
- 协议：Apache-2.0

---

## 二、核心特性

### 2.1 不提供 AI，只做调度

html-anything 不自带模型，也不卖 API Key。它**调用你电脑上已经装好的 AI 工具**：Claude Code、Cursor、Gemini CLI、Copilot……只要你之前用过并且登录过，它直接拿来用。不需要额外注册或付费。

### 2.2 75 套模板，覆盖 9 种场景

![image.png](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260517223548635.png)

自带 75 套精心设计的模板。每个模版都有严格约束：

- CJK 优先字体栈
- 8px 基线网格
- 对比度 ≥ 4.5
- 必须使用真实数据
- 禁止占位文本

覆盖 9 种常见场景：

| 场景 | 说明 |
| --- | --- |
| Web 原型 | 落地页、定价页、后台管理、技术博客 |
| 演示文稿 | 20 套风格（详见下文） |
| 生成视频 | 写完一键导出渲染成 MP4 视频 |
| 社交卡片 | 小红书、推特、Spotify 风格配图一键生成 |
| 办公文档 | 周报、需求文档、财务报告 |
| 简历 | 多种排版风格 |
| 数据报表 | 图表与数据可视化 |
| 其他 | 邮件模板等 |

### 2.3 20 套演示文稿模板

做技术分享和产品路演的朋友，这部分会让你眼前一亮。

**01 瑞士国际主义风格**：16 列网格配一个主色调（克莱因蓝、柠檬绿等），22 种固定布局直接套。打开就是那种「一看就贵」的冷峻感。

**02 杂志和电子墨水风**：10 种布局搭配 5 套配色方案（墨水、靛蓝瓷、牛皮纸等），看起来就像一本印刷精美的艺术杂志。

还有 deck-xhs-pastel（小红书柔和风）、deck-hermes-cyber（爱马仕赛博霓虹风格）、deck-replit（Replit 产品演示风格）等。

### 2.4 视频帧脚本，可直接渲染成 MP4

html-anything 还能生成视频内容。提供了 10 个遵循 heygen-com/hyperframes 规范的帧脚本，交给 Remotion 就能渲染成 .mp4。

| 帧脚本 | 说明 |
| --- | --- |
| frame-glitch-title | 故障艺术标题帧——青色/洋红色差偏移、CRT 扫描线、损坏数据字幕、ASCII 噪声。赛博朋克专用 |
| frame-logo-outro | 品牌 Logo 片尾帧——Logo 逐块组装 + 发光光晕、标语升起、CTA 出现。产品发布收尾卡 |
| vfx-text-cursor | 光标打字特效——每个字符以品红 × 青色色差轨迹显现。丢进一句引用，得到电影级开场帧 |

### 2.5 一键导出到多个平台

生成好的内容支持一键导出：

- **微信公众号**：CSS 全部内联，粘贴进去直接用
- **X / 微博 / 小红书**：自动渲染成 2× 高 DPI PNG，复制到剪贴板
- **知乎**：LaTeX 公式自动处理成图片占位符

如果你之前也经历过同一份内容在不同平台重新排版的痛苦，这个功能就很实用。

### 2.6 流式渲染 + 沙箱预览

生成过程采用 SSE 流式渲染技术，能实时看到 AI 的创作过程。发现方向不对可以马上中断、重新提示，避免浪费生成资源。

安全上，所有生成的 HTML 都在沙箱 iframe 中进行预览，隔离本地存储和 Cookie。

---

## 三、安装使用

前提：本地至少安装了一个支持的 AI CLI（如 Claude Code），要能正常使用。

~~~bash
git clone https://github.com/nexu-io/html-anything
cd html-anything
pnpm install
pnpm dev
~~~

浏览器打开 http://localhost:3000 就能看到入口界面。

想看每个模版长什么样，打开仓库里的 `skills/` 目录，每个模板都有 `example.html`，双击就能看到效果。

---

## 四、当前局限

1. 目前只能输出 **HTML 和 PNG** 格式。如果你需要 PDF 或 PPTX，得依靠浏览器打印或第三方工具转换。
2. 修改内容需要通过 **AI Agent 重新生成**。没装过 AI CLI 的人上手门槛会偏高。

---

## 五、HTML 还是 Markdown？

社区里争议挺大。关键不在格式本身，而在于所处的场景：

- **写笔记、做文档**：Markdown 就够了，简单直接，版本控制友好
- **跨平台发布、需要精细排版**：HTML 的优势就出来了。尤其是现在 AI 能帮你写 HTML，格式门槛已经不是问题了

---

## 六、与同类工具定位对比

| 工具 | 定位 | 输出格式 | AI 依赖 |
| --- | --- | --- | --- |
| html-anything | AI 调度 + 75 套模板 + 多平台导出 | HTML / PNG | 复用本地已有 AI CLI |
| ppt-master | SVG → PPTX 原生生成 | PPTX | 内置 AI 角色系统 |
| html-ppt-skill | 36 主题 HTML 幻灯片 | HTML | OpenClaw/Claude Code Skill |
| AI-Animation-Skill | 44 个 HTML 科普动画 | HTML | OpenClaw Skill |
