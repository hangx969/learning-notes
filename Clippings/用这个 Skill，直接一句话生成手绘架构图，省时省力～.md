---
title: "用这个 Skill，直接一句话生成手绘架构图，省时省力～"
source: "https://mp.weixin.qq.com/s/DlEY3CHRFTjYHaw-SyJaog"
author:
  - "[[RUNOOB]]"
published:
created: 2026-04-18
description:
tags:
  - "clippings"
---
原创 RUNOOB *2026年4月3日 11:28*

现在有了 AI 对我们开发来说确实很多工作方式多改变了，就说画图这件事，以前画架构图、流程图，得打开 Draw.io、Visio 或 Excalidraw，一点点拖拽组件、反复调整布局，还要操心对齐、配色、箭头样式，光是排版就能耗掉不少时间。

![图片](https://mmbiz.qpic.cn/mmbiz_png/EYxI5IfBe8WyPITYzHKCsia7O34NP0ZC7rd7f9vH8BVWeQzHukTQC4iaGib0wwWvp27JsibspQQqNBDyMzNT3DibwHVeZliaEyHOcRIkk1ddGEic4Q/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

而今年过年以来，最火的无疑是 Agent，Agent 已经不只是帮你写点代码的工具了，而是一个可以替你干活的全能打工人。

当我们给它配上画图 Skill（比如基于 **Excalidraw** ），它就可以自动拆结构、自动排版、自动生成整张图。

整个过程只需要一句话：生成一个用户登录流程图，然后图就出来了。

## 今天我们要聊的这个 Skill 是来自 GitHub 官方技能库： excalidraw-diagram-generator，能让 AI 瞬间把你的文字描述变成漂亮的手绘图。

**excalidraw-diagram-generator 的核心能力就一句话：用自然语言生成 **可编辑 的** Excalidraw 图。**

我们只需要用一句话描述需求，它就能帮你生成一个可以直接打开的 `.excalidraw` 文件。

开源地址：https://github.com/github/awesome-copilot/blob/main/skills/excalidraw-diagram-generator/

Skills 市场：  

- https://skills.sh/github/awesome-copilot/excalidraw-diagram-generator
- https://skillsmp.com/zh/skills/github-awesome-copilot-skills-excalidraw-diagram-generator-skill-md

安装方式：

```cs
npx skills add https://github.com/github/awesome-copilot --skill excalidraw-diagram-generator
```

这个 Skill 支持将文本转换成多种图

- 流程图（Flowcharts）
- 关系图（Relationship Diagrams）
- 思维导图（Mind Maps）
- 架构图（Architecture Diagrams）
- 数据流图（DFD）
- 泳道图（Swimlane）
- 类图（Class Diagram）
- 时序图（Sequence Diagram）
- ER 图（数据库建模）

## excalidraw-diagram-generator 工作方式：

- **理解需求：分析你要画什么类型、关键元素、关系。**
- **提取结构：把文字拆成节点、箭头、决策点、泳道等。**
- **选模板：自动匹配 8 个内置模板之一（或者自定义）。**
- **生成 JSON：严格遵守 Excalidraw 规范（字体必须用 Excalifont，颜色方案统一，布局自动优化）。**
- **输出文件：直接给你 <名字>.excalidraw，拖进 Excalidraw 就能用，还能继续涂改。**

安装完这个 skill 后，我们可用 Claude Code 等工具，只需要输入一句话，它就会直接生成一个 `.excalidraw` 文件给你：

```
生成一个用户登录流程图
```
![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

我用的是 Claude Code，它会直接调用 excalidraw-diagram-generator 来绘制图片并生成.excalidraw 文件给我们，我们可以用 VS Code 打开查看：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

VS Code 需要安装 excalidraw 扩展，我们就可以直接在里头编辑了：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

再画个支付流程试试：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

还有完整的说明：

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

我们直接看效果，整体逻辑已经表达得很清晰了。

我也先后试了好几款模型对比下来，也是需要好用的大模型，才能真正画出结构完整、细节到位的理想架构图。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

继续滑动看下一个

菜鸟教程

向上滑动看下一个