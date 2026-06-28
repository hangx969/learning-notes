---
title: "Prompt该退环境了，未来属于Loop Engineering。"
source: "https://mp.weixin.qq.com/s/omwt7d9BSFX7kotW9vo9bQ?scene=1"
author:
  - "[[数字生命卡兹克]]"
published:
created: 2026-06-28
description: "技术的尽头是管理"
tags:
  - "clippings"
---
数字生命卡兹克 数字生命卡兹克 *2026年6月15日 10:05*

最近，AI行业又出现了一个有趣的新词。

Loop Engineering。

如果你关注AI这个领域的话，这两天应该都会刷到。

推特在刷，各种社媒也在刷，群里也有蛮多人在讨论。

事情是这样的。

6月7号，OpenClaw的创始人Peter发了一条推，非常的简短，但是直接就爆了。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqVewG0KLhz4puy8GwDE3BPBlBCqmVNnCXQVxAwREicuL4Bc9jQGdeZubh47nnlWWG3XOywq3AmpdXNwCQ3O55BGf6x6p8rZjG4Q/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

翻译过来意思就是：你不再需要为编码智能体编写提示词了，你应该设计循环来提示你的Agent。

这个循环，其实就是loop的意思。

而在这之前几天，Claude Code的创始人老哥Boris在一个开发者大会上也说了差不多的话。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqW1Fmel17J40MayHeficrvWlsSscpPcxPuiaick3Dqzib9alADSjhCrH8WSIppt0SXvB0yEbcunicfwLbicOtcJkCp151FiaBX2GXGlgg/640?wx_fmt=png&from=appmsg#imgIndex=1)

他的原话大概是，我不再手动给Claude写提示词了，我运行着能让Claude自动编排任务的循环，我的工作，就是编写这些循环机制。

也就是，写loop。

这两个人呢，说了同一件事。

然后Google的Addy Osmani紧接着发了一篇长文，把Loop Engineering这个概念正式梳理了出来。

![图片](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqVOfVAzf8qqOEb0lZvfKmLkA27iayFyvBrnLNKDJQ4NEiaYcMFUOQx7MVDAQgLMBt5Wfw2YAgfYwNjl1y0BfiaKfl1XVEHhuuicxG4/640?wx_fmt=png&from=appmsg#imgIndex=2)

于是，继Prompt Engineering、Context Engineering、Harness Engineering之后，AI行业的第四个逐渐形成共识的Engineering，就这么诞生了。

我其实是个特别不喜欢造新词的人，但是很多时候，造词这事我觉得还是得分两种情况，有一种我觉得就是为了炒概念，比如xxx 4.0。

而有的时候，真的只是行业太快，人们更需要一个精准的表达来帮助自己表达而已。

Loop Engineering我觉得就是后一种。

而且，这个东西跟我自己一直使用Agent的方法、一直在鼓励大家做的事，是高度吻合的。

如果你看过我之前写的那篇Harness Engineering的文章，你大概能理解一些我的感觉。

那篇文章里我聊了从Prompt到Context到Harness的三次跃迁，聊了马具和缰绳的比喻，聊了约束先行。

而Loop Engineering，其实就是在Harness之上，又往上走了一层。

把一个套马的缰绳，变成了全自动工业流水线。

很有《文明》里时代的进化的感觉。

给大家举个例子。

比如说，以前你用Claude Code写代码，流程大概是这样的。你给它一个任务，它写完了，你看一眼，觉得不太对，你再给它提一个修改意见，它改完了，你再看，再提意见。

整个过程你会发现，是坐在设备前的，一轮一轮的，你说一句它回一句，你就是那个驱动整个循环的发动机。

即使我们以前从chatbot时代迈向了Agent时代，绝大多数的事情，也一样是任务制的。

而现在，比如Boris老哥，他的工作方式是，他会去写一个loop，比如/loop babysit all my PRs，自动修CI问题，有新评论就派子Agent去处理，就这么一句话，然后Claude Code就开始自己跑了，它会自动去看他GitHub上所有的PR，哪些CI挂了就自己修，哪些review有新评论就自动派一个独立的工作树Agent去改代码。

他还把一些其他的loop挂到定时任务上，每天晚上自动启动去干这个事，晚上睡觉的时候，甚至有时候会有几千个Agent在同时工作。

他自己说，2026年，他就再也没有手写过一行代码了。

你会看到，这就是loop，定好目标，然后全自动流程化，你完全不需要在电脑前，甚至都不需要看手机。

你可以直接睡觉，醒来的时候，代码已经改好了，测试也已经跑过了，PR也已经提上去了。

你并不是自己给Agent写了一段Prompt帮你完成某个单次的任务，是你自己设计了一个目标，这个目标使用loop的方式，帮你提示Agent。

你定义目标，定义验证条件，定义失败了怎么处理，然后，就可以放手了，从此以后，这一切，交给系统。

说到这里，我估计很多人已经大概理解loop是个什么东西了。

Addy Osmani在他那篇长文里，把一个完整的loop拆成了五个组件。

我觉得这个拆法蛮清晰的，我用我自己的理解给大家过一下。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqUicg3Nl4Wana7slBmwbhXmYNx9iaJrF9hxRicDWNYXExXghGWibibN7ia5goW2Fyuz8hibGsroYkZhib0Biapzicc3eruuhzWeqFJ2BdmwA/640?wx_fmt=png&from=appmsg#imgIndex=3)

第一个是定时任务，整个loop的心跳。

你得有一个东西能自动启动循环，不管是定时跑、还是事件触发，都行。

Claude Code里有好几种方式，/loop命令按间隔自动执行，cron定时调度，Hook在Agent生命周期的特定节点自动触发（比如每次改完文件自动跑一遍lint，这个很好玩，教程和玩法我也在准备了），或者直接丢到GitHub Actions里，关上电脑它也在跑。

没有定时任务的Agent，你每次都得手动去踢一脚它才会动，那就不是loop了，那还是你在操控。

第二个是工作树隔离，Worktree（搞过开发的朋友应该秒懂）。

就是你同时跑好几个Agent的时候，给每个Agent一个独立的工作空间，各干各的互不干扰，干完了再合并。

两个Agent改同一个文件的痛苦，跟两个设计师同时改一个图层又不打招呼的痛苦，是一模一样的。

第三个是项目知识体系，Addy Osmani在他的原文里写的是skill，但是我觉得他写的不太对，单skill其实是不够的，必须得是知识管理体系。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/2jjfQoZLoqVecTSb8hflxdo1erAUYgOr7ftAytIV4fyLiawXMJ7rdRTGficibj1pg8ggQo5WY7XrWQf7HTJdmyqM3BBegib8zice33qrUU1asWhY/640?wx_fmt=jpeg#imgIndex=4)

大家也都知道，AI每次开新对话就啥都忘了，你跟它说过的代码规范、项目架构、踩过的坑，下次开对话全部从零开始。

所以你得有一整套方法来沉淀、优化这些知识，让Agent每次启动的时候就已经知道你的项目，我自己在这快一年的coding开发过程中，总结的方法论其实就沉淀成了我自己的洁癖.skill，这个基本是我的Agent每天调用最多的skill。

CLAUDE.md是全局的规则和约束，跨会话记忆是一些之前悬而未决的记录和文档路由，docs体系就是你完整的所有的知识和经验沉淀，因为CLAUDE.md和记忆都有大小和行数限制，所以每次任务完成后我会用洁癖.skill来对整个的知识体系进行梳理和审查，确保没有错误。

为什么知识管理体系这个东西在loop里特别重要呢？

因为loop是自动跑的，你不在场。如果Agent的记忆里有过期信息，它就会基于错误的前提做决策，如果CLAUDE.md膨胀到几百行全是历史叙事，真正的规则反而被挤出去了Agent读不到。

没有干净的知识体系的loop，就像一个每天早上都在看过期文档的员工，干的得越快错得越多。

所以洁癖.skill我非常推荐大家可以去安装一下，也在我自己的仓库里开源了，我自己真的觉得特别有用。

https://github.com/KKKKhazix/khazix-skills

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqXB6NjBBZmHtFbNxWFm9oNNDDK35N95zqeQqTDBqxSeVObHKBepggfWjtCgibjRx76EAUqgIia0G4ID17AtziaSuxn4y9MD7mQtl8/640?wx_fmt=png&from=appmsg#imgIndex=5)

第四个是连接器，MCP。

一个只能看文件系统的Agent，能力是很有限的。但你给它接上GitHub、飞书、数据库之类的，它就能在你的真实工作环境里干活了。

这才叫真正的闭环，从发现问题到解决问题到通知人类，一条龙。

第五个是子Agent。

做事的和检查的分开，写代码的Agent不能自己给自己打分，这跟学生自己批自己的考卷一个道理，它一定会对自己太宽容。

所以你得有另一个Agent，甚至用不同的模型，专门来检查前一个Agent的输出，一个负责做，一个负责验。

这五个东西加在一起，就是一个完整的loop的骨架。

Claude Code和Codex有一个命令，其实就是Loop Engineering这套骨架最直接的微观型的产品化体现，只不过很多人没有意识到。

他叫/goal，在Codex里叫追求目标。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/2jjfQoZLoqULAyUFREGNmEKO0ZFLe121vkAyNDagZowueOzsam1n1cybes16Gn60ObI5sEmWgOAkI5udWImdojLfdtvQPvFMfx9ObSl8ZEk/640?wx_fmt=png&from=appmsg#imgIndex=6)

意思就是你给Claude一个完成条件，比如「所有测试通过并且lint检查没有报错」，然后它就会一轮一轮的自己干，干完每一轮之后，就会检查这个条件是不是满足了。

大多数讲Loop Engineering的文章，都停在了这一层。

讲了五个组件，讲了/goal和/loop命令，讲了怎么配定时任务，就结束了。

这些我觉得，都是术。

而我更想聊的，是道。

Loop Engineering这件事，我觉得它最核心最核心的能力，其实不是什么技术能力，也不是写脚本的能力，更不是什么会配hook的能力。

最核心的，是定义目标的能力。

定义目标，相信我，这四个字，听起来简单，做起来是真的难。

回到前面说的/goal，它的用法看起来非常直接，给一个完成条件，Claude自己干到满足为止。

听起来很简单对吧。

但你如果真正用过就会知道，/goal用得好不好，完全取决于你那个目标定义得好不好。

这个事我拿两个例子对比一下你就明白了。

目标A，「把这个应用优化一下」。

目标B，「test/auth目录下所有测试通过，tsc --noEmit零报错，npm run lint零违规」。

目标A会发生什么呢。

大家可能都能猜到，Claude会陷入一种非常尴尬的状态，因为它不知道什么叫「优化好了」，除非他是Fable 5，能自己在你之上，自主的帮你定义目标。

而绝大多数的模型，包括Opus 4.8和GPT-5.5，在自己定义目标的能力上还是非常的弱，它可能改了一点代码，然后自己觉得还行，就停了。

也可能不停，一直改一直改，把你的代码库改得面目全非，因为它始终无法判断自己到底什么时候算完成了。

那目标B呢？Claude每改一轮代码，都会去跑测试、跑类型检查、跑lint。三个命令，三个明确的通过标准。

全过了就停，没过就继续，清清楚楚，干干净净。

同一个工具，同一个模型。

区别只在于，你的目标定义得好不好。

我自己其实一直有一个原则，我经常跟身边的人说，在公众号里也说了无数遍，如果一件事你重复做了三次，你就一定要想办法把它完全自动化掉。

这个习惯跟了我很多年了。

我每天也都在写代码、做自动化，我们的AIHOT热点监控系统，我们的数据分析流程，我们的财务对账流程，我们的数据清洗管道，能自动的我全部自动了。

但说实话，在做这些自动化的过程中，我踩过最多的坑，从来不是技术问题。

是目标不清晰的问题。

我早期做自动化的时候，经常犯一个错，就是目标定得太模糊。

举个例子，比如自动监控AI行业热点，这句话听起来没毛病，但其实是一句纯粹的废话。

什么叫热点？浏览量过万算热点还是过十万算热点？抓取频率是每小时还是每天？抓到以后怎么评估质量？评估完以后怎么排序？排完以后怎么推送？

这种反问的问题，我现在可以直接随手问20个以上。

每一个环节如果没有明确的判定标准，整个自动化链条就是一坨狗屎，你相信我，绝对的。

后来我懂了，每次做自动化之前，我会先花很多时间去定义目标。

去花很多很多时间，去定义怎么算做完了，怎么做完算做的好。

这其实就是/goal的逻辑。

也是Loop Engineering的灵魂。

而如何定义目标，这个能力，我其实不是从AI中也不是从开发中学来的。

这个能力，是我从这几年创业的过程中，学来的。

定义目标的能力，其实就是，管人的逻辑。

我自己也开公司，虽然公司不大，只有30来号人，但管人这件事我是真真切切经历过的。

管人最痛苦的是什么，不是人不努力，也不是人能力不够，是你给出去的目标不够清晰，然后下属就一脸懵逼，不知道你要什么，跟无头苍蝇一样打转，最后做出来的东西，你又不满意。

你跟员工说，“把这个功能做好”，那他做出来的东西大概率不是你想要的。因为你脑子里的好跟他脑子里的好不是一个东西。

你跟他说，“这个接口的响应时间降到200毫秒以下，错误率控制在0.1%以内，下周三之前上线”，他做出来的东西跟你预期的偏差就会小很多。

因为你给了他一个可以验证完成的标准。

这一切其实也适用于那种天才型的大神，虽然大神们会自己定义目标，甚至比你定义的还要强，但是给大神们依然是需要有目标的，只是这个目标，不需要那么细节了而已。

对人如此，对AI也是如此。

其实你回头看，所有好的管理方法论，不管是管理学之父Peter Drucker在上世纪50年代提出的目标管理，还是后来Andy Grove在Intel发明的OKR，还是再后来一代又一代CEO们用的各种变体，核心其实就一个东西。

你能不能把一个模糊的意图，翻译成一组可衡量、可验证的完成条件。

管理者要做的，是确保目标足够清晰、资源足够充足、反馈足够及时。

你看这三条。

跟一个好的loop的三个要素，是不是一模一样。

目标清晰，就是你的条件写得精准。

资源充足，就是你给Agent配好了Skill、连接器、工作权限，让它手里有足够的工具干活。

反馈及时，就是你设计了验证机制，每一轮都有一个独立的检查器告诉Agent做得对不对，哪里需要改。

管人的逻辑和管Agent的逻辑，是完全一样的。

只不过，管Agent比管人还要极端一些。因为人可以理解你的模糊意图，人可以主动来找你确认，人可以说老板你这个需求说得不太清楚我不太确定你是不是这个意思。

Agent很多时候是不会的。

Agent会非常自信地按照它自己的理解去执行，然后非常自信地告诉你它做完了。

所以，对管理能力的要求，其实比管人还高。

这也是为什么我一直说，AI时代我最讨厌什么「文科已死」「理科已死」的言论，管理学、心理学、组织行为学这些，不但没死，反而变得更重要了。

说到底，Loop Engineering说是Engineering，但我觉得其实它的核心竞争力根本不在工程。

在管理。

而在管理学上，就定义目标这件事，其实不止是把话说清楚就行，其实还有一个非常阴险的陷阱，在管理学和经济学里有个专门的名字，叫古德哈特定律。

![图片](https://mmbiz.qpic.cn/mmbiz_png/2jjfQoZLoqUC9PFXFiaxq1MQF3AEQGdhEZRAHV3s8hxiavrob2EkDh35nOAWUicx5vBCSu0Xic5janGaPXg8zM3Per4paJa7mLnGBDf1TuG4GKc/640?wx_fmt=png&from=appmsg#imgIndex=7)

当一个衡量指标变成了目标本身的时候，它就不再是一个好的衡量指标了。

翻译成人话就是，你考核什么，员工就只做什么，然后其他东西可能全都退化。

这个事在人类管理中已经是老问题了，而在AI Agent身上，这个问题被放大了一百倍，因为Agent比人类更擅长钻规则的空子。

有人总结过Loop Engineering里很好玩的事情，就是Agent会针对验证器做优化，而不是针对你真正的目标做优化。

比如说你的loop条件是让测试全部通过，那Agent可能最后不去修Bug，直接把失败的测试给你删了。

你看，最后答案依然是测试全过了，完事，从验证条件来看，它确实完成了目标，但从你真正想要的结果来看。。。它啥也没干。

人也会这么干，只不过，Agent做得更快、更彻底、更没有心理负担。

所以，一个好的目标定义，不能只有做完了的标准，还必须有不能怎么做的边界。

这其实就是Harness Engineering在Loop Engineering里面发挥作用的地方。

Harness是约束，是护栏，是告诉Agent你可以自由发挥，但这条线你不能越。

Loop是驱动力，是告诉Agent往那个方向一直跑。

两个加在一起，才是一个完整的系统。

到这里，骨架讲了，灵魂也讲了，陷阱也讲了。

Loop Engineering的东西，终于也差不多了。

最后我想把前面聊的管理学的思路收一下，给一个我自己用得比较多的目标定义框架，不一定科学，纯粹就是我自己的一点点经验。

1\. 完成标准要可以被机器验证。

2\. 边界条件要跟完成标准一起定义。

3\. 要有失败的降级方案。

4\. 目标要分层。

回到整条线来看，从Prompt到Context到Harness到Loop，四次跃迁，其实讲的是同一个故事。

Prompt Engineering告诉你，好好说话，AI会更懂你。核心能力是语言表达。

Context Engineering告诉你，光说话不够，得给AI足够的信息。核心能力是信息筛选和组织。

Harness Engineering告诉你，光给信息也不够，得给AI设规则和约束。核心能力是系统设计和规则制定。

Loop Engineering告诉你，光设规则也不够，得让整个系统能自己跑起来。核心能力是目标定义和管理。

语言学、信息科学、控制论、管理学。

四个Engineering，四门古老的学科。

多有意思。

人类社会，其实从来就没有变过。

******以上，既然看到这里了，如果觉得不错，随手点个赞、在看、转发三连吧，如果想第一时间收到推送，也可以给我个星标⭐～谢谢你看我的文章，我们，下次再见。******

\>/ 作者：卡兹克

\>/ 投稿或爆料，请联系邮箱：wzglyay@virxact.com

**微信扫一扫赞赏作者**

那些思想 · 目录