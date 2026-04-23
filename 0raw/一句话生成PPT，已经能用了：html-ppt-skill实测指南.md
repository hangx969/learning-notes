---
title: "一句话生成PPT，已经能用了：html-ppt-skill实测指南"
source: "https://mp.weixin.qq.com/s?__biz=MzUxNDAxMzQyMw==&mid=2247496098&idx=1&sn=41b4a48a760b8c205993ccdd3e00c451&scene=21&poc_token=HBLc6WmjJdzz5WUtbIJfxNKGDkeBB3XHL8Y5nI6A"
author:
  - "[[有料黑科技]]"
published:
created: 2026-04-23
description: "PPT 这个品类，真正的问题一直不是模板不够多。问题在交付链路太重。内容在文档里，设计在审美里，排版在鼠标里，导出在软件里。"
tags:
  - "clippings"
---
有料黑科技 *2026年4月17日 23:15*

PPT 这个品类，真正的问题一直不是模板不够多。

问题在交付链路太重。内容在文档里，设计在审美里，排版在鼠标里，导出在软件里。人要在四五个环节之间来回切，最后消耗最多的时间，常常不是想清楚讲什么，而是把一页页东西摆整齐。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/2tmmBsrhXa0aiae41tQC18ibUibqNtNr00podUU03N6HQW7cJmemAyvDKkiav2OIsFLPwAcultEtLuNDtkyEsQicLba5m4QbqzcxCiblFwq5Bz9gE/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

`html-ppt-skill` 有意思的地方，在于它把这条链路压扁了。

它不是传统意义上的 PPT 软件，也不是一个只会吐几张图的 AI 模板站。它更像一套给 AI Agent 准备好的幻灯片生成系统：输入自然语言，输出静态 HTML/CSS/JS 幻灯片；主题、布局、动画和整套 deck 模板都已经准备好，Agent 只需要按需求调用。

这件事一旦跑通，做 PPT 的方式就变了。内容、版式、主题和导出，开始变成一条连续的工具链。

先把答案压到一个具体问题上： `html-ppt-skill` 现在能不能在 Windows 环境里真正跑起来，并且交出能看的成品。

后面的内容只围着这件事展开：能力边界、安装过程、适配细节，还有三组真实测试结果。

## 先看结论

先给判断：能用。

而且覆盖的场景已经不算窄，技术分享、融资路演、小红书图文这几类高频任务都能落下来。

当前这套 skill 自带：

- 36 套主题
- 31 种页面布局
- 14 套完整 deck 模板
- 47 种动画效果

输出是普通 HTML/CSS/JS，没有额外编译流程。对 AI Agent 来说，这个结构非常重要，因为它意味着产物足够稳定、足够透明、足够容易改。

一句话触发的场景已经很明确：

- “做一份 8 页技术分享，cyberpunk 主题”
- “turn this outline into a pitch deck”
- “做一个小红书图文，9 张，白底柔和风”

这类任务以前依赖人手工搭模板、调样式、导页面。现在已经可以先由 Agent 直接产出第一版成品，再由人做最后一层判断。

这背后的变化很像 Karpathy 说的 Software 3.0：自然语言开始承担编程接口的角色。PPT 还在那里，页面还在那里，CSS 还在那里，变化发生在调用层。

## 它到底是什么

`html-ppt-skill` 的 GitHub 地址在这里：

https://github.com/lewislulu/html-ppt-skill

从结构看，它本质上是一套静态页面生成系统：

- `assets/`
	里放字体、基础样式、主题和运行时脚本
- `templates/`
	里放布局模板和完整 deck 模板
- `references/`
	里放主题说明、模板说明和写作约束
- `scripts/render.sh`
	负责把 HTML 渲染成 PNG

也就是说，它并不试图重新发明一个 PPT 文件格式。它直接绕开这件事，用浏览器能理解的那套东西来表达幻灯片。

这个选择很聪明。

因为浏览器渲染本来就是今天最成熟、最容易跨平台验证的视觉输出系统之一。HTML 幻灯片的可控性、可预览性、可导出性，都比封闭二进制格式更适合 Agent 调用。

## 真正关键的价值，不是主题多

36 套主题、31 种布局、14 套 deck 模板，当然有价值。

但更关键的价值是：PPT 从人工操作对象，变成了 AI 可以直接调度的能力模块。

以前做 PPT，人的工作流大概是这样：

1. 先想内容
2. 再选模板
3. 再改样式
4. 再补图表
5. 再调动画
6. 再导出

现在这套 skill 试图把第 2 到第 5 步直接收进 prompt 里。人给出需求，Agent 决定调用哪个模板、哪个主题、哪种版式，再吐出第一版 HTML 成品。

这个变化带来的最大收益，不是炫技，而是把人的精力从“执行排版”挪回“判断内容”。

换句话说，问题开始从“怎么做一页 PPT”，变成“这一页要不要这样表达”。这才是真正有价值的抽象提升。

## 安装过程：先说真实情况

这次安装最有分量的地方，落在三个细节上：离线包、本地适配、桌面交付。

- 受限网络环境下，本地压缩包安装比在线克隆更稳
- `SKILL.md、` `README.md、` `render.sh`
	都补了 Windows 路径和浏览器定位逻辑
- 生成结果统一复制到桌面，后续查看和分享都更直接

这部分的价值不在安装动作本身，而在于它把一个 GitHub 仓库变成了一个能在 Windows 本地稳定跑通的能力模块。

## 三组测试，分别验证了什么

安装和脚本修完之后，真正重要的是看它在三类任务里能不能稳定交付。

### 测试 1：技术分享 deck

提示词：

“做一份 8 页的技术分享 slides，用 cyberpunk 主题”

最后选用：

- deck 模板： `tech-sharing`
- 主题： `cyberpunk-neon`

实际产出的样例是：

`html-ppt-skill/examples/tech-sharing-cyberpunk/index.html`

这组测试验证了两件事：技术分享的骨架能否自动落位，强主题能否保持阅读秩序。结果说明，模板骨架和主题系统的分层是成立的。

### 测试 2：Pitch Deck

提示词：

“turn this outline into a pitch deck”

最后选用：

- deck 模板： `pitch-deck`
- 主题： `pitch-deck-vc`

实际产出样例：

`html-ppt-skill/examples/pitch-deck-demo/index.html`

这组测试验证了商业叙事的场景抽象能力。它能沿着同一套生成链路，把融资路演需要的节奏、层级和视觉重心排出来。

### 测试 3：小红书图文

提示词：

“做一个小红书图文，9 张，白底柔和风”

最后选用：

- deck 模板： `xhs-post`
- 主题： `xiaohongshu-white`
- 备选主题： `soft-pastel`

实际产出样例：

`html-ppt-skill/examples/xhs-white-soft-9/index.html`

这组测试验证的是跨场景迁移能力。它覆盖的已经是一类“多页结构化视觉输出”，范围从技术分享延展到商业路演，再延展到社交图文。

## 真正跑通的，是交付可靠性

把这三组测试摆在一起再看，会发现重点已经不在主题数量，也不在模板数量。

真正跑出来的是一条连续链路：内容进去，版式和主题跟上，最后能导出成品。做到这一步，PPT 就开始有了接口感。

这个变化对 AI Agent 很实在。用户丢进来一句需求，系统先吐出第一版，再交给人做判断和细修。整件事的重心已经落到交付，而不是演示。

## 它适合谁

适合三类人：

- 需要快速出技术分享稿的人
- 需要把文字提纲变成完整 deck 的人
- 需要做多页图文内容的人

## 它暂时不适合谁

适合度最高的前提也很明确：它需要一条能跑通的本地环境链路，需要愿意接受 HTML 作为中间产物，也需要对最终视觉结果做最后一轮判断。

## 真正该记住的事

`html-ppt-skill` 最重要的意义，是把 PPT 从人工排版对象，推进成 AI 可调度的视觉输出能力。

这件事一旦成立，后面就不只是做 PPT 了。技术分享、路演页面、社交图文，都会变成同一类任务。

一篇文章汇总了现在几乎所有热门ppt agent：

[AI做PPT总翻车？这套带6道质检的开源框架，彻底终结排版灾难](https://mp.weixin.qq.com/s?__biz=MzA4OTY3ODQzNw==&mid=2448503134&idx=1&sn=09bd21edd202f2d884e0e0772301bfc9&scene=21#wechat_redirect)

继续滑动看下一个

有料黑科技

向上滑动看下一个