---
title: "为什么 AI Agent 时代，TypeScript 正在抢走 Python 的主场？"
source: "https://mp.weixin.qq.com/s/9DmKOFGieHnLDDyo8amqkg?scene=1"
author:
  - "[[小智]]"
published:
created: 2026-06-28
description: "为什么 AI Agent 时代，TypeScript 正在抢走 Python 的主场？"
tags:
  - "clippings"
---
小智 华智启航AI *2026年6月7日 08:58*

2024年以前，问一个AI工程师"做AI用什么语言？"，答案不会有悬念——Python。

但到2026年，你再去问正在做AI Agent产品的团队"你们主力语言是什么"，越来越多的人会说出同一个回答：TypeScript。

GitHub 2025年Octoverse报告显示，TypeScript首次超过Python，成了GitHub上使用量最多的语言——同比新增超过100万贡献者，增长66.63%。Python新增约85万贡献者，排在第二。

Python在AI里的位置谁也替不了，但AI技术栈正在分层，而在"把AI做成产品"这一层，TypeScript已经有了结构性的优势——不是靠某一个特性取胜，是一堆东西凑在一起，让选TS成了一件很自然的事。

这篇文章想讲的，就是这些优势具体在哪，谁在推动这个变化，以及对你选技术栈意味着什么。

一、GitHub的数据不会撒谎：AI代码在往TypeScript跑

几组数据放在一起看。

GitHub 2025年Octoverse报告（2025年10月发布）给出的结论很清楚：TypeScript同比增长66.63%，首次超过Python排到平台第一，领先约4.2万贡献者。JavaScript第三。

但更值得关注的是AI相关仓库的数据。

同一份报告里有一组数字：Python驱动了近一半新增的AI仓库（58.2万个，同比增长50.7%)，而TypeScript在AI相关仓库的增速达到77.9%（8.6万个），从相对小的基数上实现了更高的增长率。

TypeScript的增长主要由默认使用TypeScript脚手架的前端框架和受益于严格类型系统的AI辅助开发所推动。

npm的数据也在说同一件事。

2025年底，npm上打"AI"或"LLM"标签的包总量超过1.5万个，同比涨了200%多。Vercel AI SDK到了2026年初，每周npm下载量280万次，LangChain.js每周130万次。

这两个数放在哪个语言生态里都是现象级的。

这些数据指向同一个事实：全球开发者在新开AI项目的时候，是在主动选TypeScript。

不是"因为前端用了TS所以后端顺便用"，而是"我就要用TS来搭AI产品的核心逻辑"。

二、AI应用层不等于模型层：两种语言到底如何分工

要搞明白TypeScript为什么能在AI里崛起，得先破掉一个常见误解：以为AI开发是一个统一的技术栈。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/nsNb9aIKc6vzGghyQedGUHPYV0hEWjA35LNhbntY50aysP5XYBUpCAgH0EeDONPeOaeohqQWAB5hJR92IPu8QIM508DYicSRdW0tIDHw9LxI/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

实际上，现在的AI技术栈已经分成了两个明显的层。

底层是模型训练和推理。GPU编程、分布式训练、模型架构设计、数据管线——这一层Python说了算，短期内谁也动不了。

PyTorch、JAX、Transformers、vLLM、HuggingFace整个生态全是Python原生的。如果你在训一个语言模型或者在微调视觉模型，Python是唯一合理的选择，这事没什么好争的。

上层是AI应用和Agent产品。LLM API调用、Agent编排、工具调用、RAG管线、前端集成、后端业务逻辑、实时通信、边缘部署——这一层过去也是用Python的，但TypeScript正在快速变成默认选项。

YC 2025年夏季批次是个很好的横截面。据多位YC合伙人和投资人在社交媒体上分享的数据，那批里60-70%的AI Agent创业公司选了TypeScript当主力语言。同个数字在2024年冬季批次里还不到40%。一年时间，翻了一倍。

Blaxel——一个AI基础设施的决策框架——2025年底出了篇分析文章，里头直接给了一个决策建议："团队在构建面向用户的产品集成型Agent？选TypeScript。团队在做ML密集型负载（训练、微调、大规模数据处理）？选Python。"不是哲学主张，是工程建议。

投资端也有信号。

P72.vc在2025年一篇分析里写，TypeScript在AI应用开发中是"流行的、企业就绪的、理想的选择"，理由列了三条：类型安全能压住AI代码的bug密度、全栈能力省掉多语言团队的协作成本、以及npm生态的成熟度。

三、类型安全：AI写的代码最需要的那道护栏

要是说有一个技术特性让TypeScript在AI时代天然比Python有优势，那就是类型系统。

![图片](https://mmbiz.qpic.cn/mmbiz_png/nsNb9aIKc6vLy85yaCoYL3m30aCdrc3CXkCbspMRqUzRoMGhwXSTib6O1O76otWXCgqRvtXg9z3o1mq3GYym17vCq5EhqwWrv0ianStqmpVias/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

这件事在人类自己写代码的时候已经挺要紧了，在AI生成的代码占比越来越高以后，它直接变成了决定性的。

2025年有一项针对LLM生成代码质量的研究，结论是这样的：LLM输出的TypeScript代码里，94%的编译错误能在编译期被类型检查器抓出来。同样的Python代码，同类错误要跑到运行时才暴露——而这里面大概30%最终会导致生产环境故障。

这个差距的根因不复杂：LLM特别擅长生成"看着没问题"的代码，但搞不清隐含的类型约束。

TypeScript的类型系统相当于一个自动安检门——LLM生成什么都行，过了类型检查才能进主分支。Python的类型注解是可选、也不强制执行的，在AI代码占比高的项目里，这个差别会被放大很多倍。

放到真实工程实践里，这个优势体现在很多地方。

你用Vercel AI SDK调LLM做工具调用的时候，SDK会自动从你的TypeScript函数签名生成JSON Schema，再传给LLM——参数类型严格定义，返回值被类型守卫验证。整个过程端到端类型安全。

在Python那边做同样的事，你得手动管JSON Schema的同步，手动验证返回值——每一步都可能出错。

再往深想一层，Agent的核心挑战之一是"可靠性"：Agent要执行多步工具调用，每一步都可能搞出类型不匹配的错误。TypeScript让你能在编译时就掐掉这些错误路径，不用等用户在生产环境里撞到。

Cursor的团队选TypeScript当AI IDE核心语言的时候公开表达过：类型安全让他们能更激进地引入AI生成的代码，因为编译器和类型检查器相当于"第二双眼睛"。

四、生态武器库：框架和SDK都在爆发

一个语言在某个领域能不能成，最靠谱的指标不是语言特性多好，而是框架生态够不够壮。

TypeScript的AI生态在过去一年半里是肉眼可见的爆发。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/nsNb9aIKc6ujgh8J9ibQ39HlaT9OtyOvvicpKlvOr28RsfYnOkjEHT1TsP0guMoOV6vNBRTqSVu87lmqTGPicLjkkHbGuXEoZ8iajhJyRshGLlQ/640?wx_fmt=png&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

**Vercel AI SDK（周下载280万次）** 是目前最主流的TypeScript AI开发框架。

它设计上最聪明的地方是把LLM调用变成了标准TypeScript流—— `generateText()` 、 `streamText()` 、 `generateObject()` 用起来跟调一个普通函数没区别。

支持几十个模型提供商的统一接口，工具调用、结构化输出、Agent循环都是原生集成的。

**LangChain.js（周下载130万次）** 是LangChain生态在TS侧的分支。LangChain自己作为框架有过"过度抽象"的争议，但它在TypeScript侧的采用率摆在那，说明大量开发者确实在用TS搭RAG和Agent。

**Mastra** 值得单独说一下。它是TypeScript原生的Agent框架，一上来就自带工作流引擎、评估系统和可观测面板。

设计哲学跟LangChain完全是两个方向——不去做万能抽象层，而是给一个有清晰边界的Agent运行时。

2024年8月首次发布后增长迅速，到2026年初已积累超过2万GitHub Star和每月180万次npm下载，被不少开发者称为"TypeScript Agent开发的正确打开方式"。

**CopilotKit** 解决的问题比较独特——专做Agent UI。用它可以直把LLM Agent嵌进React组件里，Agent能读写你的应用状态，用户在前端看到的Agent交互是全类型安全的。这是典型的"只有TS才做得这么自然"的东西。

**Claude Agent SDK** 是Anthropic在2025年发布的官方TypeScript/JavaScript SDK，专门用来构建基于Claude的Agent。

前身是Claude Code SDK，2025年9月正式更名为Agent SDK。支持长时间跑的Agent循环、子Agent委派、上下文管理。该SDK同时提供TypeScript和Python两种语言的版本。

![Mastra、CopilotKit、Claude Agent SDK](https://mmbiz.qpic.cn/mmbiz_png/nsNb9aIKc6ueWo3pOkmS7dcQBo5LE79eaEVLDR6pAhNBQLCfqMh5Xp7nFoSAgTzFeibQqyCmEjLq4Ss62DKcHXpbibk5d3VjkEhTq9AvsxviaY/640?from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

Mastra、CopilotKit、Claude Agent SDK

除了这些框架，还有一个常被忽略的生态优势：npm。TypeScript/JavaScript的包管理统一在npm下面，一个 `npm install` 解决所有依赖。

Python的包管理在过去几年经历了一轮又一轮碎片化——pip、poetry、pipenv、uv——到现在也没个统一方案。对于需要集成十几种API和工具的Agent应用来说，依赖管理的可靠性直接决定开发体验。

五、全栈同构与边缘部署：运行时的结构优势

TypeScript做AI产品开发，还有一个核心优势：全栈同构。

一个典型的AI Agent产品有三层：前端（用户界面）、后端（业务逻辑和API路由）、AI层（LLM调用、工具执行、Agent循环）。在TypeScript生态里，这三层共用一种语言、一套类型定义、一个包管理器，甚至连工具函数的代码都能直接共享。

这意味着什么？你定义了一个"搜索文档"的工具函数，这个函数的类型定义能同时在三个地方复用：前端展示工具调用结果的UI组件、后端处理Agent工作流的逻辑、还有就是AI SDK传给LLM的JSON Schema定义。改类型定义的时候，整个栈同时拿到编译时错误提示。

在Python栈里这几乎做不到——前端怎么说都要用JavaScript或TypeScript，所以天然存在"AI逻辑在Python，前端类型在TS"的断层。

**异步模型** 也是个被低估的差异。JavaScript和TypeScript的async/await是运行时原生的，它的设计前提就是"一切都可能是异步的"。

AI Agent应用本质上是一个异步超密集的场景——每个LLM调用、每个工具执行、每个API请求都是异步的。TypeScript的并发模型在这个场景下比Python的asyncio更顺手，性能也更稳。

Python的asyncio是在同步语言上后加的异步层，很多库还是阻塞的，在Agent这种高并发异步场景很容易变瓶颈。

**JSON的原生性** 是第三个基础优势。Agent开发到处是JSON：LLM的输入输出格式、工具调用的参数、Agent状态的序列化。

TypeScript里 `JSON.parse()` 和 `JSON.stringify()` 是运行时原生的，JSON到类型对象转换零成本。Python需要 `JSON.dumps()` 加手动类型转换。

然后说 **边缘部署** 。AI Agent产品对延迟越来越敏感——用户不会等一个Agent想好几秒。这意味着Agent逻辑要尽量靠近用户跑，也就是部署到边缘节点。

TypeScript和JavaScript是目前边缘运行时支持最广的语言——Cloudflare Workers、Vercel Edge Functions、Deno Deploy、AWS Lambda@Edge。

你可以把一个TS写的AI Agent部署到Cloudflare Workers上，全球200多个节点跑，冷启动不到5毫秒。用Python在边缘跑Agent？目前基本不现实。

Portkey的案例很能说明问题。他们构建了号称"全球最快的AI网关"，TypeScript写的，跑在Cloudflare Workers上，P99延迟压到10毫秒以下。

他们在技术博客里专门解释了选型逻辑——标题就叫"Why We Chose TypeScript Over Python for the World's Fastest AI Gateway"——核心原因是TypeScript编译后的JavaScript在Cloudflare Workers的V8引擎上有近乎原生的性能，异步模型天然匹配AI网关的并发请求处理需求，而且类型系统在代码规模扩大后带来了明显安全性优势。

六、Python没有也不会被替代——这是技术栈在成熟

话说回来，有一件事得讲得特别清楚：TypeScript有优势不代表Python在衰退。反过来，两种语言在AI里的分工越来越清晰，这恰恰说明AI技术栈在走向成熟。

Python在下面这几个领域有不可替代的位置，而且短期内看不到任何变化：

**模型训练和微调** 。

PyTorch和JAX的Python绑定是深度学习行业的默认标准。没任何别的语言能在这个层面对Python构成威胁。HuggingFace的Transformers、微软的DeepSpeed、Meta的LLaMA系列——全部Python原生。

**数据处理和科学计算** 。

NumPy、Pandas、Polars、PySpark——数据管线的每个环节都在Python上。TypeScript在这个领域基本没有对等的替代品。

**ML研究** 。

论文复现、实验管理、超参数调优——学术界的通用语言就是Python。这个事实在未来很长时间里不会变。

**Python侧的AI应用框架盘子依然很大** 。

LangChain Python周下载超过500万次，LlamaIndex有完整的Python生态。纯Python团队当然可以用Python构建完整AI应用。Python不是"做不了"，是"在某些场景下不如TS顺手"。

打个比方：你不会用造汽车工厂的语言去造汽车的仪表盘。Python是建AI工厂的语言，TypeScript正在变成做AI产品体验的语言。两种语言服务的是同一个产业的不同环节，是互补，不是替代。

真正值得关注的不是"谁取代了谁"，而是AI应用层的开发者正在主动选TypeScript。这些人里大多数本来就会Python——他们选TS不是因为不会Python，而是因为TS做AI产品确实更好用。

七、2026年的趋势

时间线拉到2026年下半年甚至往后看，有几个趋势是越来越清楚的。

**AI从"训模型"进入了"做产品"的下半场。**

2023到2024年，行业的核心故事是"谁能训出最好的模型"。到了2025、2026年，核心故事变成了"谁能用这些模型做出最好的产品"。模型本身在商品化，意味着更多资源会流到应用层——应用层恰好是TypeScript的主场。

**Agent架构的标准在TypeScript生态上定型。**

你去看：Anthropic的Claude Agent SDK，TypeScript和Python双语言支持。

OpenAI的Agents SDK同样提供TypeScript版本。Google的Gemini SDK把TypeScript作为主要支持语言之一。

三大顶级AI公司都将TypeScript纳入Agent SDK的一等支持——这不是巧合，是客户需求在推。

**"AI全栈工程师"在变成一个独立岗位。**

这个岗位要求同时碰前端、后端和AI/Agent开发——三种技能在TypeScript生态里是可以无缝拼在一起的。用TypeScript的公司能招一种工程师覆盖全部三层。

用Python的公司在前端那层无论如何要引入第二个语言。从招聘效率和组织成本来看，TypeScript的"单语言三层"模式正在胜出。

**中国公司也在跟这个趋势。**

阿里云通义千问的DashScope SDK在2025年加上了TypeScript支持。月之暗面Kimi的API客户端同时有Python和TypeScript版本，TS版也在持续迭代。

中国AI模型出海的时候，大量客户直接开口要TypeScript SDK——人家产品栈就是TS的。

回到最初的问题：为什么越来越多全球开发者做AI应用和Agent产品时选TypeScript而不是Python？

不是一个原因，是一组结构性优势加在一起：

类型安全在AI代码占比越来越高的时代成了刚需，全栈同构消掉了前后端和AI层之间那条语言缝，边缘部署满足了Agent对低延迟的硬要求，异步原生模型跟Agent的I/O密集特点天然对得上，而框架生态在过去18个月从"勉强能用"跑到了"生产力工具"。

Python不会消失。做模型训练、数据处理、科研，它还是最好的选择。但如果你现在搭一支团队做AI Agent产品，面向用户交付一个靠谱的AI应用——TypeScript是更实际的选项。

不是什么语言宗教之争，就是工程现实。而工程现实正在推着越来越多的开发者做出一样的决定。