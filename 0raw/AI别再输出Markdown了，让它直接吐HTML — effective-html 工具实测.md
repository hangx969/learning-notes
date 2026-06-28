---
title: "AI别再输出Markdown了，让它直接吐HTML — effective-html 工具实测"
source: "https://mp.weixin.qq.com/s/UpwCCgiK8BkT9P8U74x_Vw?scene=1"
author:
  - "[[Jim Gadgets]]"
published:
created: 2026-06-28
description: "AI别出Markdown了，出HTML\x0d\x0a\x0d\x0a\x0d\x0a\x0d\x0a我上周用Claude写一个系统架构说明，它照例给我吐了一"
tags:
  - "clippings"
---
Jim Gadgets Jim Gadgets *2026年6月14日 11:00*

别让AI出Markdown了，出HTML

![图片](https://mmbiz.qpic.cn/mmbiz_png/buxFNhaTGwnwVwFmTGFTBl0cXs4CpjNpwRe2DKO1LDgAh0GIDjoA6at4WG6HJ5WP5Nbz48UE6ILrKfHNwUOt18UjlGIBicq0cLbUGMOgcogk/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

我上周用Claude写一个系统架构说明，它照例给我吐了一堆Markdown。我复制到文档里，看起来像那么回事，但发给同事之后对方问了一句：「流程图在哪？」

我愣了一下。Markdown里确实有文字描述，但没有图。没有视觉呈现的架构说明，就像只给你菜谱不让你看菜。

![图片](https://mmbiz.qpic.cn/mmbiz_png/buxFNhaTGwlcPSvLLl4JlBoIiaOOayZEeDrZXKDpGByfWMskB4HeBCCbbyqVz1HHAnzZjVRUu0O2INLUWu3QEH68xFnr49VoqpiaiaIdOnOW68/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

我又回去让Claude画图，它给了我一段Mermaid语法，粘贴到渲染器里…图出来了，但样式不是我想调就能调的，交互就更别想了。

我们是不是把Markdown当成了AI输出的唯一标准答案？

## 它是什么

effective-html，说白了就是一个三天拿了170多颗星的GitHub项目，做的事情极简： **教AI Agent直接输出自包含的HTML文件，而不是Markdown。**

听起来好像没什么？但你想想…HTML是什么？是浏览器直接渲染的语言嘛。AI给你一个`.html` 文件，双击打开，看到的是排版精美的页面、可交互的图表、带暗色模式的报告！

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/buxFNhaTGwlvpC6CxrFxlgJdnNvPxoWV8D8fObLDZBf0r6ib9mdWYqCXiaOVDUzeaqbd7vh1vd9A9zibF82HSxsfT4SX1WX1A9ZtT9kE0ffz38/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

不用装任何东西！不用Markdown渲染器，不用Mermaid，不用Jupyter。浏览器就是运行时呗。

这个项目来自plannotator这个组织，他们还有markdown-editor、webtui、web-highlighter几个项目。看得出来，这帮人一直在想一件事： **怎么让文本在浏览器里活起来。** 反正我看完他们的项目列表，感觉是有执念的。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/buxFNhaTGwm1lZibpZEOicwrt7e7Jzic9ddLJmtFcuaMv8eQTkvyzHV0IxoAicHoA99BjhofLdpVIk5R7h5mBlCpbbBicGoqasurY6NJ2mn8h1qc/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

## 三个Skill，三种武器

effective-html不是一个大而全的工具，它拆成了三个独立的Agent Skill：

### 1\. html — 通用生成器

最灵活的那个。你说「帮我做一个项目对比报告」或者「写一个功能介绍页面」…它直接给你一个完整的HTML文件。

我承认我试了一下让它做AI编程工具对比页面，输出的文件打开之后：卡片布局、颜色区分、表格对比，底部还有暗色模式切换按钮！切换之后配色丝滑过渡，刷新页面还能记住你的偏好。

### 2\. html-diagram — 架构图专用

这个我最有感觉。你描述一个系统架构，它生成一个全屏的SVG交互式架构图…节点可以点击，数据流可以动画演示，请求路径能高亮显示。

不是那种静态的框图，是真的能跑的、能交互的可视化！好家伙，我之前用Mermaid画架构图画到吐，早知道有这玩意就好了。

### 3\. html-plan — 计划文档专用

最克制的那个。你给它一段项目计划或者需求描述，它帮你整理成一个简洁实用的HTML页面。不会过度设计，就是干净、清晰、能看。

## 最让我服气的细节

effective-html的背后有一套叫做「html-effectiveness」的参考示例，作者是Thariq Shihipar。这个参考库里有20个精心制作的HTML模板…从代码审查报告、设计系统文档、原型动画，到流程图、事故报告、功能开关面板。

![图片](https://mmbiz.qpic.cn/mmbiz_png/buxFNhaTGwlNbr49Se9kic10Om5hXclZoy99h0RT13N2wv8YibjZQ4VTDRkYaKrHuH7mPnh1OoITXic2FHoytFVu89UE9PpRJx73RqCpCav7Jg/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

讲真，这些不是简单的CSS模板。每一个都是 **「AI生成这种东西应该长什么样」的范本** 。

这意味着什么？意味着当你用这个Skill的时候，AI不是从零开始瞎猜「一个好看的HTML该长什么样」，它参考的是这些经过设计验证的模式。就像给AI一本设计规范，让它照着规范出活…效果当然比裸奔强。

## 和Markdown比，到底强在哪

我不打算假装HTML在所有场景都碾压Markdown。该说缺点我也说。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/buxFNhaTGwnicPGeGfZUg1gkZxQupJZRicqicyNbcwpc9J22O93vu0KWIFubLqVfTC08VGWrE1pnYMGKJNqHub4CEbshIich57w6gT2UtraSYlw/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

**HTML赢的地方：**

**视觉表达力：** Markdown能做到的是结构化文本，HTML能做到的是完整的视觉设计！排版、色彩、动画、交互…这些Markdown根本做不了。

**自包含交付：** 一个HTML文件就是最终产品！Markdown永远是半成品，你总得找地方渲染它。

**交互性：** 架构图可以点击节点、动画展示数据流，报告里可以嵌入可切换的标签页。这些在Markdown里？不可能的。

**Markdown依然赢的地方：**

**版本控制友好：** Git diff看Markdown改了什么一目了然，HTML的diff基本没法看。

**纯文本生态：** 搜、grep、管道处理，Markdown天然适合，HTML里面有太多标签噪声。

**写作速度：** 随手记笔记，Markdown仍然是最快的选择。

> effective-html不是要替代Markdown，而是补上了AI输出格式缺失的那一环。当你需要交付一个「看」的东西…报告、架构图、演示文档…HTML是比Markdown更对的选择。当你需要的是「读」和「改」的纯文本，Markdown仍然是王。

## 怎么用

这个项目注册在 `skills.sh` 上，是Claude Agent的Skill格式。项目结构很清晰：每个Skill一个文件夹，里面有 `SKILL.md` 定义指令， `references/` 放参考模板。

它也兼容`.claude-plugin` 格式，在Claude Desktop里可以直接作为插件加载。

当然也可以自己安装：

```
# 安装所有项目npx skills add plannotator/effective-html
# 只装架构图技能npx skills add plannotator/effective-html --skill html-diagram
# 只装计划页技能npx skills add plannotator/effective-html --skill html-plan
```

## 我的判断

值得试。尤其是你经常让AI帮你做报告、画架构图、写文档的场景…试试让AI直接出HTML，你会发现效果比Markdown好得多。

但有一件事我还不确定…当AI输出的不再是纯文本，而是一个完整的视觉产品，我们对「AI输出」的预期会不会彻底变？今天我们觉得AI给一段Markdown就挺好了，明天我们会不会觉得AI必须给一个能看的HTML才算及格？

我的判断是… **会的。** 一旦你见过AI直接出HTML的效果，你就回不去了。就像你用惯了智能手机，再让你回到功能机，你受不了的。

不是Markdown不好。是你值得更好的。

```
项目地址：https://github.com/plannotator/effective-html参考示例：https://thariqs.github.io/html-effectiveness
```

Jim Gadgets

Jim 发掘好用工具，探索有趣项目