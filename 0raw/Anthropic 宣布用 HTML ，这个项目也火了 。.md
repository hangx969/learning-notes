---
title: "Anthropic 宣布用 HTML ，这个项目也火了 。"
source: "https://mp.weixin.qq.com/s/X8ePB4OBoJFShDx4hSsdnw"
author:
  - "[[开源日记]]"
published:
created: 2026-05-17
description:
tags:
  - "clippings"
---
开源日记 *2026年5月17日 15:17*

前几天在 X 上刷到一条有意思的消息：

Anthropic 的 Claude Code 团队宣布，他们内部文档不再写 Markdown 了，直接写 HTML。

理由是：Markdown 是写给作者看的，HTML 才是给读者看的。

然后。

一个叫 html-anything 的项目在 GitHub 上火了—— **已经拿到 2500+ Star** 。

**它能让本地 AI Agent 帮你写 HTML。不生成 Markdown 或 PPTX，直接输出纯静态的 HTML 文件。**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/VDCUoW3UiblICXq920sl7rJJxMDczVHrjvYic4bPWLACh6otQn0thm5pZNUJE4FJ2qVkX6v9LVryVPxpmYZwf6MQnnfQotcSwwGlhAVXhOFXU/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

左侧输入需求，中间选模板，右侧实时预览。

装好后你只需要做一件事：

```
做一份技术博客，暗色主题，要有代码示例和数据图表
```

AI 自动选模板、应用设计约束、输出完整 HTML 文件。

### 不提供 AI，只做调度

说到实现方式，html-anything 不自带模型，也不卖 API Key。

说白了就是 **调用你电脑上已经装好的 AI 工具** 。

Claude Code、Cursor、Gemini CLI、Copilot……只要你之前用过并且登录过，它直接拿来用。不需要额外注册或付费。

### 生成的每一页都是成品，不是半成品

自带 75 套精心设计的模板。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

每个模版都有严格约束：

- CJK 优先字体栈。
- 8px 基线网格。
- 对比度 ≥ 4.5。
- 必须使用真实数据。
- 禁止占位文本。

这样做的好处就是确保输出契合专业规范。

覆盖 9 种常见场景:

**01 Web 原型。**

能够用来制作落地页、定价页以及后台管理、技术博客这些页面。

**02 演示文稿。**

有 20 套风格可以选用，下面我会单独拿出来说说。

![演示文稿示例](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

演示文稿示例

**03 生成视频。**

写完一键导出渲染成 MP4 视频，下面我也会单独讲一下。

![视频帧示例](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

视频帧示例

**04 社交卡片。**

像小红书、推特以及 Spotify 风格的配图都能够借助它来一键生成。

**05 办公文档。**

日常办公要用到的周报、需求文档、财务报告等文档，都有相应模板。

![办公文档示例](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

办公文档示例

此外还囊括了简历此外海囊括了据报表等其它场景。

### 这 9 种场景里，演示文稿模板值得单独聊聊

足足有 20 套演示文稿。

做技术分享和产品路演的朋友，这部分会让你眼前一亮。

**01 瑞士国际主义风格。**

你用 16 列网格配一个主色调就行，克莱因蓝、柠檬绿这些随便挑，22 种固定布局直接套。打开就是那种「一看就贵」的冷峻感。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**02 杂志和电子墨水风。**

10 种布局搭配 5 套配色方案，墨水、靛蓝瓷、牛皮纸这些都有。看起来就像一本印刷精美的艺术杂志。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

还有 deck-xhs-pastel 也就是小红书柔和风、deck-hermes-cyber 即爱马仕赛博霓虹风格、deck-replit 也就是 Replit 产品演示风格等。

![Deck 演示模式](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

Deck 演示模式

### 视频帧脚本，可直接渲染成 MP4

除了静态页面和演示文稿，html-anything 还能生成视频内容。

它提供了 10 个遵循 heygen-com/hyperframes 规范的帧脚本，交给 Remotion 就能渲染成.mp4。

**frame-glitch-title** — 故障艺术标题帧

青色/洋红色差偏移、CRT 扫描线、损坏数据字幕、段落 ASCII 噪声。赛博朋克专用。

![frame-glitch-title](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

frame-glitch-title

**frame-logo-outro** — 品牌 Logo 片尾帧

Logo 逐块组装 + 发光光晕、标语升起、CTTA 出现。产品发布的收尾卡。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**vfx-text-cursor** — 光标打字特效

每个字符以品红 × 青色色差轨迹显现。丢进一句引用，得到电影级开场帧。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

![Hyperframes 视频帧](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

Hyperframes 视频帧

### 一键导出到多个平台

内容生成好了，接下来就是发布。

html-anything 支持一键导出到多个主流平台，省去了手动排版的麻烦。

![一键导出](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

一键导出

- **微信公众号** ：CSS 全部内联，粘贴进去直接用。
- **X / 微博 / 小红书** ：自动渲染成 2× 高 DPI PNG，复制到剪贴板。
- **知乎** ：LaTeX 公式自动处理成图片占位符。

如果你之前也经历过同一份内容在不同平台重新排版的痛苦，这个功能就很实用。

### 流式渲染 + 沙箱预览

生成过程中的体验同样重要。html-anything 采用了 SSE 流式渲染技术，让你能实时看到 AI 的创作过程。

![SSE 流式渲染](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

SSE 流式渲染

你能看到页面被 AI 画出来的过程。发现方向不对可以马上中断、重新提示，避免浪费生成资源，也让创作过程更可控。

安全上有考虑，不是只顾功能的粗放实现。

所有生成的 HTML 都在沙箱 iframe 中进行预览，隔离本地存储Cookie。

### 看完这些功能，相信有些人已经迫不及待了。

注意本地至少安装了一个支持的 AI CLI，比如 Claude Code，要能正常用 。

传统手艺先用git把代码下载到你的电脑上。

```
git clone https://github.com/nexu-io/html-anything
```

进到目录，把依赖安装好。

```
cd html-anything
pnpm install
```

最后一行命令启动。

```
pnpm dev
```

浏览器打开 http://localhost:3000 就能看到入口界面。

像看看每个模版长啥样，打开仓库里的 `skills/` 目录，每个模板都有 `example.html` ，双击就能看到效果。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

### 两个小问题

当然这个项目也不是完美的。目前有两个主要局限：

1. 目前只能输出 **HTML 和 PNG** 格式。如果你需要 PDF 或 PPTX 的话，得依靠浏览器打印或第三方工具来进行转换。
2. 修改内容需要通过 **AI Agent 重新生成** 。没装过 AI CLI 的人上手门槛会偏高。

### 写在最后

说了这么多功能，回到最初的话题——HTML 还是 Markdown？

社区里争议挺大。

有人觉得 Markdown 够用了，简单直接，版本控制友好；也有人觉得 HTML 才是正解，排版自由，所见即所得。

两种观点都有道理。我觉得关键不在格式本身，而在于你所处的场景。

写笔记、做文档。

Markdown 就够了。

跨平台发布、需要精细排版。

HTML 的优势就出来了。尤其是现在 AI 能帮你写 HTML，格式门槛已经不是问题了。

你的看法呢 ？

项目基于 Apache-2.0 协议开放，感兴趣的同学可以去 GitHub 仓库看看源码和文档。

开源地址：https://github.com/nexu-io/html-anything

既然看到这了，欢迎随手点赞、在看、转发，也可以给我个星标⭐，接收最新的文章，我们下期见！

AI · 目录

继续滑动看下一个

开源日记

向上滑动看下一个