---
title: "这才是AI做ppt的正确姿势 ！"
source: "https://mp.weixin.qq.com/s/uJXM0G3frzTQ6tbTQwxY-Q"
author:
  - "[[开源日记]]"
published:
created: 2026-04-20
description:
tags:
  - "clippings"
---
原创 开源日记 *2026年4月19日 15:09*

Gamma 用户都冲到 7000 万了，微软又把 Copilot 硬塞进 PowerPoint……AI 做演示文稿这块已经卷得不行了。

输入一段文字，几十秒出一套幻灯片，看着挺像回事。然后你点导出，打开 PPTX 文件。

![图片](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblIsWPg64Eq62MspT3UNIqdSHMuiclCIthfzdJh8f7YM4vjOGTBEwaHnpw4OVKZkmKoIcc4gI3l36R9alYSXcR81QF4q7BONZ8mg/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

打开 PPTX 文件——字体被替换，图表移位，格式全乱了。改一页崩一页，最后还是自己手动调。

**说白了，导出来就是个半成品，改不了、调不好。**

你只能回去重新生成，祈祷下一版能好一点。但每次生成风格都不一样，改一版丢一版，最后还是自己打开 PowerPoint 手动做。

更气人的是，有些工具连导出都要收费，月费 8 美元起。你的文件还得上传到他们服务器，隐私什么的就别想了。

最近一个名为 PPT Master 的开源项目在 GitHub 上悄然走红。

**4 个月，6200+ Star，本周一周涨了 1500。**

![图片](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblKvHwJVOBic1iatFKeaQP5icaibzrFefxwcPqicricsdmp5CNS4Sq31uPkv7o9vgz7jYLVEP86aRIojbiaiaYcWVlk41icicRibOTEfFzfAak/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

它做的事很简单： **输出真正的、可编辑的 PPTX 文件，不是贴图。**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblK0hicSQlvMr5Vlg1xbiaQpak2RKfQicia6jkoUYl0kUcffCxKJYfZWQVbNjH9bibrTH06WPwVHSZic2kibFjKogxfeIlE3yoIRN5lia5o/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

说白了现有大部分 AI PPT 工具，输出的就是图片或 Web 截图。看起来漂亮，但在 PowerPoint 里一个元素都点不动。

Gamma 导出的 PPTX，图表会移位、字体会替换、动画会消失。Beautiful.ai 导出质量算好的，但非英文支持很弱。微软自家的 Copilot 倒是原生集成，但 M365 订阅加 Copilot 费用，一年下来不是小数目。

PPT Master 的路子完全不一样。

**先用 AI 生成 SVG，再通过自研转换引擎，把 SVG 逐元素翻译成 DrawingML——PowerPoint 底层的矢量格式。**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblJAcNamPl9Jpn25kEM1dDvRGdk0Xia2HKYArolkbx4xEwMo5nRxGAv9jBFNEwbK14tFax7XibibNQwjClPtsnicxiaZk2Hgr8eUNl2g/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

文本框、渐变、阴影、发光效果、箭头标记、图片裁剪路径，全部原生转换。v2.3.0 版本开始，原生 DrawingML 导出已经是默认选项。

**在 PowerPoint 里打开，随便点一个文本框——能编辑，能拖动，能改颜色。就像你自己一个个画出来的一样。**

它还贴心地输出两个文件，一个原生形状版 `.pptx` 拿去编辑，一个 `_svg.pptx` 快照版留着做视觉参考。都带时间戳，不会搞混。

**还有个头疼的是数据必须上传。**

![图片](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblLqvFKQNqicILswAyDSViaBQLPjRdN7HjGlC2x8ZInPk46gOEyqQL271FLoQKP15juqcaW9W7WI3BusomN7Rq05nEdV1ZicMfjM8M/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

Gamma、Beautiful.ai 这些 SaaS 工具，你的文件必须上传到他们的服务器才能处理。金融、咨询、政务这些对数据敏感的行业，这一关就过不了。

PPT Master 除了和 AI 模型通信那一步，整个流程都在本地跑。你的 PDF、DOCX 不用上传到任何第三方服务器。

**再来说说价格和锁定问题。**

Gamma 月费 12 美元起，Beautiful.ai 12 到 40 美元，而且都把你锁在他们的平台上。

PPT Master 基于 MIT 协议开源，工具本身免费。你唯一要付的钱，是 AI 编辑器的费用。

**用 VS Code Copilot 的话，最低 0.08 美元就能生成一整份 PPT。**

它也不把你绑死在某个编辑器上。Claude Code、Cursor、VS Code Copilot 都能用，Claude、GPT、Gemini、Kimi 等模型都支持。

PPT Master 不是简单地把文档丢给大模型就完事，它设计了一套四角色协作的工作流。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblK8hwEiaJW8bk6icQYdSRS7hus2I8JLJlnIibQicyUVN6F0MtbLJsZKkd8dC80U97ibVIHZIEk5uIkPwIRTfTfVtzLoBvQgDjiblIwn0/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

Strategist 先上场，分析内容、规划幻灯片结构、确认视觉风格，产出一份完整的设计规范。

然后 Executor 接手，按照设计规范逐页生成 SVG。中间如果需要配图，Image Generator 会调用你配置的图像后端。

最后是后处理和导出环节，SVG 被转换成原生 PPTX。

有个细节值得注意， **它强制要求页面顺序生成，不允许并行。** 听起来好像慢了，但这是为了保证跨页面的视觉一致性——配色、字号、间距不会在翻页时突然跳变。

官方提供了 15 个案例项目，覆盖咨询风格、通用风格、创意风格，总共 229 页，都能在线预览。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblKxxt7xC37ehKQKSmBTuh7IrQQes0ficicSNh69WcjTNoawiaibSvcNphEg4N3u4x97ZWChzSJFCdv3JNUDO7svOnUQTjNRwokVmRI/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

我最喜欢这个像素复古游戏风的 Git 入门 PPT。

![图片](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblLNibu7W8Kld4kFDFjxLclZsTbRfLzhfUJcYcwrtQ3LSPxYaaEr0SLNuOvo8FeYJ1Pgy3GZVTPg7JrQ7LYOaB2gabxBPEHCh31I/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

配色用了霓虹绿、赛博粉、电光蓝，背景是深空黑。导出的 `.pptx` 文件，每个元素都能直接编辑，不用回去重新生成。

还有麦肯锡风格的客户忠诚度分析、Google 品牌风格的年度汇报、禅意水墨风的金刚经研究……风格跨度很大，但输出的 PPTX 都是原生可编辑的。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblJeZxbPFGyFHtxASLxJ5WecLQjZG030iaHwEpeRTsCicOgGdOSKoodc6VZwYGQzRgn6Z7EzCWVibLt90wbhibu1zJQaaT9xkxd2JzY/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=8)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/VDCUoW3UiblLN73UYyxUibuY1DlzniaH48G7HNs1vkoeUOcMaiacNkEmqibolksDviahU4UpxmQtCLw9Xs2W6GUKMjXJwg66YydiasHyTibc2poDv6A/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=9)

如果你手头有现成的 PDF 或 DOCX，放到 `projects/` 目录下就行。有公司模板也没问题，它会自动提取背景、Logo、主题色、字体，在模板基础上生成 PPT，导出后风格完全一致。

再说个细节，PPT Master 还内置了 20 个布局模板、52 个可视化模板、6700+ 矢量图标，以及 12 个图像生成后端（Gemini、OpenAI、Qwen、智谱、火山引擎等）。每个后端单独配 API Key，不用全局混用。

![图片](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblL8KUWoibZzVpWDVTheoBN3SIruiaISicMwY96gqTWERcom5YtX68HwfFV6yVaTxicrrPCqsC4iaflGgUl8ZZ9UmdZcxRpouyytdDKY/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=10)

注意Windows 的兼容性也还在打磨中，项目专门写了安装指南，说明这块确实还有坑。

还有你得有 AI 编辑器的 API 额度。虽然 VS Code Copilot 最低 0.08 美元就能生成一份，但用 Claude 或 GPT 的话，费用会高一些。

想本地上手试试也简单。

由于项目是Python开发，环境要安装，版本有要求要装Python 3.10以上，别装错了。

第一步把代码下载到本地。

```
git clone https://github.com/hugohe3/ppt-master.git
```

继续安装项目依赖。

```
cd ppt-master
pip install -r requirements.txt
```

最后大模型api key别忘记配置了。

![图片](https://mmbiz.qpic.cn/mmbiz_png/VDCUoW3UiblKcjzFXpf7g3Fgxh2ZVJqgnbMZhrv0xJHGkyOUPsN3dlPOibibvAhNeGe2LtRZZoG15KiaM2iazdHzjttxLzqaWPhdulU6iarW2AlKI/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=11)

装好之后，用 VS Code 打开项目文件夹，把你的源文件（PDF、DOCX 等）放到 `projects/` 目录下。

直接在 AI 编辑器的聊天面板里，注意要指定 AI 文件路径：

```
Please create a PPT from projects/my-doc/sources/report.pdf
```

AI 会先确认设计规范——选什么模板、什么画幅、多少页。你确认之后，它就自动跑完整个流程，生成的 PPTX 会保存到 `exports/` 目录。

#### 最后说说

以前让 AI 帮你做 PPT，它只能给你一张张截图，改不了、调不了。

PPT Master 换了个路子——用 SVG 转 DrawingML，让输出的每一个元素都是真正的 PowerPoint 形状。同时把整个流程搬到本地，让数据不出设备。

作者本身就是金融背景——CPA、CPV、投资咨询工程师，每天审阅和编辑数百张幻灯片。他做这个项目的起因很直接： **现有 AI PPT 工具导出的都是图片，不是可编辑形状，这在专业场景下完全不可接受。**

**AI 生成的演示文稿，不应该是一个终点，而应该是一个起点——你可以在此基础上继续修改、调整、完善，就像你自己做的一样。**

PPT Master 目前还在快速迭代中，生态也还在建设中。但方向是对的——让 AI 做 PPT，输出应该是活的，不是死的。

项目基于 MIT 协议开放，可商用和二次开发。感兴趣的同学，可以去 GitHub 仓库看看源码和文档。

```
项目地址：https://github.com/hugohe3/ppt-master
```

既然看到这了，欢迎随手点赞、在看、转发，也可以给我个星标⭐，接收最新的文章，我们下期见！

继续滑动看下一个

开源日记

向上滑动看下一个