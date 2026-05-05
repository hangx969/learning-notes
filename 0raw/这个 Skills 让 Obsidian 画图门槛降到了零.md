---
title: "这个 Skills 让 Obsidian 画图门槛降到了零"
source: "https://mp.weixin.qq.com/s/EbNkKTGkp2WnqJ0nKNBwmA"
author:
  - "[[艾康在路上]]"
published:
created: 2026-05-05
description:
tags:
  - "clippings"
---
艾康在路上 *2026年1月14日 20:02*

见字如面，我是艾康。

**点击关注 **👆防止迷路。****

> 本文字数 1778，阅读大约需 4 分钟

前段时间，我写了一篇《 [邪修玩法：用 Gemini 解锁 Obsidian Excalidraw 的 100 种可能](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490920&idx=1&sn=3bdb110469eaf7fa1db4b3307c73ea16&scene=21#wechat_redirect) 》。

文章里介绍了几种用好 Obsidian Excalidraw 的方式，不少读者朋友说很实用。

但说实话，那些方法还不够完美。

一方面，生成出来的图，是静态的图片，不能自由编辑。

另一方面，如果想要自由编辑，还得自己动手去画，这对很多人来说，存在一定门槛。

那有没有一种方案，能够兼顾两者呢？ **既不用自己动手画，还可以自由编辑** 。

别说，还真被我找到了。

#### 这个项目，解决了什么问题？

这是一个叫 **axton-obsidian-visual-skills** 的 Github 项目。

![img](https://mmbiz.qpic.cn/sz_mmbiz_png/ruvdeFXJIOj8QWd6nn84IdNdSHrqxjf2DlgpQoGMbGr2pzQksCJbHJXiaGFX2icfaawQ9I5dGIX6QqxBbseibfopg/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

它的核心思路很简单： **通过 Skills，让 AI 直接在 Obsidian 里生成可编辑的图表文件。**

这里需要稍微解释一下 Skills 是什么。

如果你看过我之前的文章《 [Gemini CLI 也能用 Skills 了，我用它解放了 Obsidian 的图片整理](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247491315&idx=1&sn=7f6fb0f8d08aad23f56ab8282ac3ce09&scene=21#wechat_redirect) 》

应该知道，Skills 本质上是 AI 的「技能包」，是一些预设好的 Markdown 提示词文件，让 AI 按照特定的规则和格式来完成任务。

**而这个项目，就是给 AI 装上了三个「画图技能包」。**

它支持生成三种格式的图表：

**1\. Excalidraw** — 手绘风格，视觉温暖，适合灵感记录和快速表达。

**2\. Mermaid** — 专业规范，适合流程说明和技术文档。

**3\. Canvas** — 自由布局，适合复杂网络和思维发散。

关键在于，这三种格式背后都是结构化的 JSON 代码，而不是一张死的图片。

**这意味着，你可以随时打开它，调整布局、修改文字、增删元素。**

目前支持的图表类型很丰富，基本覆盖了日常的大部分需求：

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

#### 安装配置，没你想的那么复杂

看到这，你可能会想，这种工具安装起来会不会很麻烦？

其实不会，整个过程分三步。

跟把大家装进冰箱一样简单。

**第一步：下载项目文件**

打开你的终端，输入以下命令：

```
git clone https://github.com/axtonliu/axton-obsidian-visual-skills.git
```

如果你因为网络问题下载失败，也可以直接去仓库页面：https://github.com/axtonliu/axton-obsidian-visual-skills

点击右上角的「Code」按钮，选择「Download ZIP」手动下载。

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**第二步：复制 Skills 到对应目录**

下载完成后，把仓库里的 skills 文件夹复制到你常用的大模型的 skills 目录下。

常用的 Claude Code、Gemini、Codex，都支持 Skills，区别只是模型能力不一样。

如果你用的是 Mac 或 Linux，可以直接在终端运行以下命令：

```
cp -r axton-obsidian-visual-skills/excalidraw-diagram ~/.claude/skills/
cp -r axton-obsidian-visual-skills/mermaid-visualizer ~/.claude/skills/
cp -r axton-obsidian-visual-skills/obsidian-canvas-creator ~/.claude/skills/
```

如果你想同时给 Gemini 和 Codex 也装上，把上面命令里的 `.claude` 换成 `.gemini` 或 `.codex` 就行。

**如果你是 Windows 用户** ，上面这条命令直接执行不了，手动复制也是可以的。

只不过需要注意，`.claude` 、`.gemini` 、`.codex` 这些文件夹默认是隐藏的。

Mac 用户可以在 Finder 中按下 `Command (⌘) + Shift + .` 快捷键，就能看到隐藏文件夹了。

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

Windows 用户需要打开文件资源管理器，点击顶部菜单「查看」→「显示」→ 勾选「隐藏的项目」。

**第三步：验证安装**

完成以上操作后，打开你的 Obsidian。

如果你用的是 Claude Code，在终端输入 `claude` 进入；

用 Gemini 就输入 `gemini` ；

用 Codex 就输入 `codex` 。

进来之后，输入命令：

```
/skills
```

正常情况下，你应该能看到 Skills 列表里多出了三个新技能：

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

看到这个列表，就说明安装成功了。

#### 实战演示：看看效果如何

准备工作做完了，接下来我用一个真实的例子，给大家演示一下实际效果。

我之前写过一篇笔记，叫《好笔记的五个原则》。

内容不多，但结构清晰，很适合用图像的形式呈现出来。

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

我打开 Obsidian，在 claude 终端里，直接输入：

```
请帮我把好笔记的五个原则.md 这篇文章转换成 Obsidian Excalidraw，放在当前文件夹下
```

因为 Skills 已经加载好了，Claude 能够识别我需要创建 Excalidraw 的需求，于是自动调用了 `excalidraw-diagram` 这个 Skills。

接下来就是一系列自动化的过程。

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**AI 会读取你的笔记内容，理解结构，规划布局，生成 Excalidraw 的 JSON 代码，最后保存成****`.excalidraw.md`** **文件。**

这个过程完全自动化，你只需要在它请求文件读写权限时，点击同意就行。

等待一会，就能看到终端里提示，文件已经保存在当前目录下。

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

打开 Obsidian 确认一下，文件能否正常显示。

**完全没有问题。**

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

更重要的是，它不是一张静态的图片。

你可以点击进去，自由编辑每一个元素：调整位置、修改文字、改变颜色、增删内容。

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

这种感觉，就像你自己亲手画出来的一样。

如果你没有 Claude Code，用 Gemini 或 Codex 也是可以的。

我分别用这三个工具，生成了同一篇笔记的 Excalidraw 图表。

**风格略有不同，但都是手绘美学，都可以自由编辑。**

对比一下我自己之前手绘的 Excalidraw，大家觉得哪个最好看？

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

说实话，我个人实际体验下来，真的觉得非常好用。

手绘美学风格我非常喜欢，而且对中文支持很友好，完美解决了自己手绘画图耗时漫长的痛点。

**除了 Excalidraw，Mermaid 和 Canvas 也能完美支持。**

![img](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

只是我个人比较喜欢手绘风格的图，所以日常用 Excalidraw 更多一些。

#### 写在最后

这个项目，借由 SKills 把「AI 生成」和「自由编辑」这两个看似矛盾的需求，完美地结合在了一起。

你不需要学习复杂的绘图技巧，也不需要花费大量时间手动调整布局。

**真的就只需要一句话，AI 就能帮你把文字内容，转换成结构清晰、视觉美观、可自由编辑的图表。**

如果你也有画图需求，可以去下载体验一下。

项目地址：https://github.com/axtonliu/axton-obsidian-visual-skills

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

以上，就是本文全部内容，如果觉得这篇文章对你有启发，点赞、比心、分享三连就是对我最大的支持，谢谢～

往期推荐阅读：

• [Obsidian 从入门到进阶合集](https://mp.weixin.qq.com/mp/appmsgalbum?action=getalbum&__biz=MzkxOTY1MjA1Ng==&scene=1&album_id=4151857975356817416&count=3&token=1752453856&lang=zh_CN#wechat_redirect)

• [AI把我推成“知名”博主后，我发现了一条产业链](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490247&idx=1&sn=627e1ae7bd0d01ecd3099de9e54cc451&scene=21#wechat_redirect)

• [AI写作的真相：你才是那个最重要的模型](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490217&idx=1&sn=c61ca41033ff98eb724cc7aaae52ba94&scene=21#wechat_redirect)

• [善用 AI，实际上对人的要求只会越来越高](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490639&idx=1&sn=28421e985b52a797e29f3728fb34873a&scene=21#wechat_redirect)

• [用 Gemini 解锁 YouTube 新用法，信息获取效率提升 10 倍](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490776&idx=1&sn=d1e6b83578bffabd3d74791108cca706&scene=21#wechat_redirect)

• [AI 是如何变强的？Jeff Dean 斯坦福分享解读](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490801&idx=1&sn=8964730775d61caa9a213afb1c044ca3&scene=21#wechat_redirect)

• [别再纠结 AI 味，内容创作应该回归第一性原理](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490811&idx=1&sn=835ebe21dcdd9df4fd36787c12d64ae2&scene=21#wechat_redirect)

• [有了 NotebookLM 后，还需要 Obsidian 吗？](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490868&idx=1&sn=f1193dcb7fade0042c0514e1d6ed4998&scene=21#wechat_redirect)

• [你越是会写作，就越能把 AI 用好](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490877&idx=1&sn=55ec82cbc6809585982eaccde17165ba&scene=21#wechat_redirect)

• [我试了 NotebookLM 学习法后，彻底抛弃传统学习方式](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490943&idx=1&sn=270b19200d4d2a34221d3060a2a5bc1e&scene=21#wechat_redirect)

• [NotebookLM 的这个更新，比 Gemini 3 Flash 更让我兴奋](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247490959&idx=1&sn=e4faf854dc900c8633cd6c83651e275a&scene=21#wechat_redirect)

• [NotebookLM 再次升级，来自谷歌的年终礼物](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247491016&idx=1&sn=4ae9bc14a7453c647fcda68c24488e7b&scene=21#wechat_redirect)

• [我用 NotebookLM 解锁 PPT 的 5 种玩法，实现了 PPT 自由](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247491035&idx=1&sn=553471c458a5131fff2a089549183385&scene=21#wechat_redirect)

• [AI 设计的下半场，拼的不只是模型，还有工作流](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247491189&idx=1&sn=49a3363e75edcce466fa17f2bc0518b2&scene=21#wechat_redirect)

• [AI 时代，你的上下文才是最值钱的资产](https://mp.weixin.qq.com/s?__biz=MzkxOTY1MjA1Ng==&mid=2247491293&idx=1&sn=c5714360a5c36f1cfe6b83ce0a146958&scene=21#wechat_redirect)

**微信扫一扫赞赏作者**

Obsidian · 目录

作者提示: 个人观点，仅供参考

继续滑动看下一个

艾康的AI自留地

向上滑动看下一个