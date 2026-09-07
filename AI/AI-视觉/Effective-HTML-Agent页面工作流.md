---
title: "Effective HTML：Agent 页面制作与 HTML 交付工作流"
source:
  - "https://mp.weixin.qq.com/s/EWFsQChEmC4aGfuQ1lcpgA"
  - "https://mp.weixin.qq.com/s/UpwCCgiK8BkT9P8U74x_Vw"
created: 2026-09-05
updated: 2026-09-07
tags:
  - ai-visual
  - html
  - skills
  - ai-agent
  - effective-html
---

现在让Codex 做网页已经很快了。

给出一个需求，几分钟就可以生成一份HTML。

但是用多了就会发现，代码出来得快，并不等于页面就做好了。

你只是想先看看布局，它已经开始加渐变、阴影和动画。让它画一张架构图，又很容易变成几个方框加箭头。

做交互页面也是一样。

正常状态有了，加载、报错、提交失败这些真正用起来会碰到的情况，可能还得自己一条条提醒。

最近我在 GitHub 上看到一个项目，正好管这些事情。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211510363.webp)

它叫 Effective HTML。

目前项目已经接近3000个Star。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211513385.webp)

简单来说，它就是一套给 Coding Agent 用的 HTML Skills。

装到 Claude、Codex 这类工具里以后，做页面之前先判断该怎么做，完成以后还要自己检查一遍。

我也会让Agent画流程图、做些小页面。

现在让我比较头疼的已经不是代码写不出来，而是第一版看着挺快，后面又得不断告诉它这里改一下，那里再补一个状态。

Effective HTML 补的就是这部分。

## 它解决的另一个问题：AI 应该输出什么

用 AI 写系统架构说明，常见结果是一大段 Markdown；复制到文档里看起来像那么回事，但真正需要交付给同事时，流程图、排版和交互还得另行处理。让 AI 画图也不一定能解决问题：它可能只给出一段 Mermaid 语法，必须经过渲染器才能看到结果，样式也不容易继续调整，更谈不上交互。

Effective HTML 的核心做法，是让 Coding Agent 直接输出**自包含的 HTML 文件**，而不是把 Markdown 当成最终交付物。双击文件就能在浏览器中打开，浏览器本身就是运行时；页面可以包含排版、可交互图表、暗色模式和状态切换，不需要额外安装运行环境。

### HTML 与 Markdown，各有适合的交付场景

| HTML 擅长的地方 | 说明 |
|---|---|
| **视觉表达力** | 排版、色彩、动画和交互能力远超 Markdown |
| **自包含交付** | 一个 HTML 文件就是最终页面，打开即可查看 |
| **交互性** | 架构图可以点击节点、演示数据流，报告可以加入标签页和状态切换 |

| Markdown 擅长的地方 | 说明 |
|---|---|
| **版本控制友好** | Git diff 能清楚看出文字和结构改动 |
| **纯文本生态** | 搜索、grep 和管道处理都很自然 |
| **写作速度快** | 随手记录和持续编辑仍然是 Markdown 的优势 |

所以 Effective HTML 不是要替代 Markdown，而是补上 AI 输出格式缺失的一环：需要交付一个“看”的东西时优先考虑 HTML；需要持续“读”和“改”的知识内容时，Markdown 仍然更合适。

## 先给 Agent 一套视觉范本

项目背后还有一套叫 `html-effectiveness` 的参考示例库（作者 Thariq Shihipar），包含 20 个经过设计的 HTML 模板，覆盖代码审查报告、设计系统文档、原型动画、流程图、事故报告和功能开关面板等场景。

这些示例不只是 CSS 模板，更像是“这类内容应该如何组织和呈现”的设计范本。Agent 有了可参考的模式，就不必从零猜测页面应该长什么样，输出的结构、信息层级和交互方式也更容易贴合任务。

## 先不要急着写页面

它可以从两个层面理解。按交付入口看，有三个核心 Skill：

- **`html`**：通用生成器，也是最外层的任务判断入口。适合项目对比报告、功能介绍页等一般 HTML 交付，实测可以生成卡片布局、颜色区分、表格对比、暗色模式切换，并在刷新后记住偏好。
- **`html-diagram`**：架构图和关系图专用。可以生成全屏 SVG 交互式图表，让节点可点击、数据流可动画演示，并高亮请求路径。
- **`html-plan`**：计划文档专用。将项目计划或需求整理成简洁、清晰、实用的 HTML 页面，重点是信息组织而不是过度设计。

按页面制作过程细化后，第一篇文章进一步拆成六个 Skill：`html`、`html-wireframe`、`html-prototype`、`html-diagram`、`html-plan` 和 `design-artifact`。后面重点介绍这种“先结构、再交互、再视觉”的工作流。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211516381.webp)

最外层的 `html` 用来做任务判断。

比如你说：

*帮我设计一个设备管理后台。*

它不会拿到这句话就直接开始堆 HTML 和 CSS。

还没有确定页面结构的情况下，就先用 `html-wireframe` 。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211519356.webp)

已经有明确的结构了，要做一个可以点击操作的页面，就交给 `html-prototype` 。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211522364.webp)

要展示系统架构、业务流程或调用关系的时候就用 `html-diagram` 。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211525529.png)

另外还有html-plan负责计划，design-artifact负责视觉。

这样拆开以后，Agent 每一步要做到什么程度就比较清楚了。

平时说一句“做后台”，最怕的就是它把整个页面都做完了。

等我发现左边菜单不该这么放，或者信息层级不对，后面的样式和交互也得跟着一起改。

先拦住这一步，就会省事很多。

## 页面没定，先画个线框

html-wireframe 做的事情很简单，就是把页面的骨架先搭起来。

设备管理后台。

左边是设备列表，右边是运行状态，下面有报警和实时数据。

这时它不会急于做出漂亮的造型。

主要就是灰度、边框和简单的区块，品牌色、阴影、渐变等等先放一放。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211528447.png)

现在只看结构。

设备列表到底放左边还是顶部。

报警应该先看到，还是实时数据更重要。

主要按钮放在哪里顺手。

到了手机上，这几个区域又该怎么排。

如果结构不确定的话，可以同时做几套方案，在一个HTML里面进行比较。

我自己反倒愿意先看这种简单版本。

一旦页面做得过于漂亮，就容易陷入对颜色、图标等细节的纠结之中。骨架确定之后，后面换主题、调样式就容易多了。

## 接着把页面做活

线框已经没有问题了，然后进入html-prototype。

这样就可以把静态页面变成可以操作的原型了。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211531541.png)

比如登录页，密码输错要给出提示，提交的时候要显示加载状态，成功和失败都要有相应的反馈。

弹窗、键盘操作以及手机端适配等细节，它也会一并进行检查。

平时用 Agent 做页面，第二轮修改往往都耗在这些地方。Effective HTML 把要求提前写进 Skill，就不用每次再提醒一遍。

## 画图也不能上来就堆方框

我的文章里经常用到流程图，因此对 `html-diagram` 也十分关注。

它开始画之前，会先看这张图到底要讲什么。

服务器、数据库、网关之间怎么连接，可以按拓扑关系来画。

一次请求先到哪里、再经过哪个服务，适合画时序图。

业务怎么一步一步地往下走，就用流程图。

如果重点是设备从运行到报警，再到报警恢复到正常状态，那么就比较适合用状态图来表示。

确定了形式之后，再用 HTML、CSS、SVG 或 Canvas 来实现。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/20260905211534478.png)

这一点挺实用。

我自己配图最怕的就是框很多、线很多，看起来像那么回事，读者看完还是不知道先看哪里。

不需要画得非常复杂，只要把关系说明白就可以了。

## AI 常见的页面风格，它也管

design-artifact 主要负责页面的视觉部分。

告诉Agent不要使用一些常见的AI风格，比如紫蓝渐变、满屏圆角卡片、黑底荧光色、各种不需要的动画。

如果项目已经有自己的一套设计规范，就继续沿用；没有的话就根据页面用途来决定字体、颜色和布局。

我平时看这类页面比较多，最怕换个项目还是用同一套模板。页面不需要非常惊艳，但是要和项目本身相匹配。

## 安装方法

安装也十分简单，想要一次把6个技能都装上，直接运行：

```
npx skills add plannotator/effective-html
```

如果平时主要做交互页面的话，可以只安装 `html-prototype` ：

```
npx skills add plannotator/effective-html --skill html-prototype
```

如果只需要架构图或计划页，也可以按需安装：

```bash
npx skills add plannotator/effective-html --skill html-diagram
npx skills add plannotator/effective-html --skill html-plan
```

Codex 用户直接通过插件来安装：

```
codex plugin marketplace add plannotator/effective-html
codex plugin add plannotator-effective-html@effective-html
```

项目登记在 `skills.sh` 上，采用 Claude Agent 的 Skill 格式，同时兼容 `.claude-plugin` 格式，可在 Claude Desktop 中作为插件加载。

安装好之后就可以直接让Agent按照这些规则来写页面了。

## 与同类工具的定位

| 工具 | 定位 | 输出格式 | 适用场景 |
|---|---|---|---|
| **effective-html** | AI 直出自包含 HTML | HTML | 报告、架构图、演示文档 |
| **Markdown Viewer Skills** | Markdown 内嵌图表 | Markdown + 代码块 | 技术文档配图（PlantUML/Vega/Graphviz） |
| **html-anything** | AI 生成任意 HTML 页面 | HTML | 全场景 HTML 生成 |
| **Mermaid** | 文本描述生成流程图 | SVG（需渲染器） | 简单流程图和时序图 |

项目地址：https://github.com/plannotator/effective-html

参考示例：https://thariqs.github.io/html-effectiveness

## 写在最后

Effective HTML 把做页面的流程提前定好了，用Agent来写页面可以少走很多弯路。

如果你经常用Codex来写页面的话，可以安装一下试一试。
