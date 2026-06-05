---
title: "滴滴面试官逗乐了：\"你 SKILL.md 写了 2000 行？我刚翻完 Anthropic 官方文档，上限是 5K token。"
source: "https://mp.weixin.qq.com/s/4bZ6nK3C6wTXYRmuAoisnw"
author:
  - "[[吴师兄]]"
published:
created: 2026-06-05
description:
tags:
  - "clippings"
---
吴师兄 *2026年5月26日 11:23*

大家好，我是吴师兄。

上周写的那篇《 [字节面试官皱眉："Claude Skills 我也在用，但你 SKILL.md 写了 2000 行，是把它当 prompt 还是当文档？"](https://mp.weixin.qq.com/s?__biz=MzkzMDIwMzg1Mw==&mid=2247490449&idx=1&sn=f1e345f0d5510c69ba8c7af7aca989de&scene=21#wechat_redirect) 》发出来之后，很多人都有疑问：

**"那到底该写多长？"**

很多读者看完那篇是带着这个疑问走的。这一篇就是答案。

继续来个段子。

上周那个被字节面试官问倒的学员，这周二面又被滴滴面试官抓住了。他主动跟面试官说"那道题我回去查了"，本以为能扳回一城，结果面试官放下笔，冷笑了一下：

"哦？那你告诉我， **Anthropic 官方建议 SKILL.md 主文件最多多少 token？** "

学员卡了三秒，硬着头皮答："应该是……几千吧？"

面试官没说话，从抽屉里抽出 iPad， **当场翻到 docs.claude.com 上 Agent Skills 那一页** ，把屏幕转过来给学员看，指着其中一张表，淡淡说了一句：

" **Under 5k tokens。** "

学员傻眼。他写的那个 SKILL.md，大概 2000 行，换算成 token 起码 12K 起跳—— **超了官方上限 2-3 倍** 。

面试官把 iPad 收回去，继续问：

"那为什么是 5K？多一点不行吗？这个数字是怎么定的？"

"Anthropic 把 SKILL 的内容分成三个 Level，每个 Level 加载时机不同——你说说 Level 1、Level 2、Level 3 分别是什么？"

"如果你的 SKILL 真的需要 2000 行内容，正确的拆法是什么？"

这一连串三个问题下来，学员每一问都答得磕磕巴巴。这场面试在他第二次走出会议室的时候，又一次结束了。

上一篇我讲过"SKILL.md 不是 prompt 的延伸"，这一篇往前推一层—— **SKILL.md 到底是什么、官方给出的具体边界是什么、超过边界之后正确的拆法是什么** 。看完这一篇，下次再被追问到 5K、三层加载、Progressive Disclosure 怎么落地，你不会再卡住。

## 一、先把答案钉死：5K token 是 Anthropic 官方给的上限

直接翻 Anthropic 官方文档（platform.claude.com 上 Agent Skills 那一页），有一张表写得非常直接：

| Level | 加载时机 | Token 成本 | 内容 |
| --- | --- | --- | --- |
| Level 1（Metadata） | 永远加载（系统启动时） | **~100 tokens / 每个 Skill** | name + description |
| Level 2（Instructions） | Skill 被触发时 | **Under 5k tokens** | SKILL.md 主体 |
| Level 3+（Resources） | 按需 bash 读取 | 实际无限 | 引用文件、脚本、资源 |

这张表把所有边界都钉死了：

**Level 1 是 YAML frontmatter（name + description）** 。每装一个 Skill，启动时大约 100 token 进系统 prompt。装 50 个 Skill 也就 5K token，所以 Anthropic 鼓励你装多个细分 Skill 而不是装一个臃肿的 Skill。

**Level 2 是 SKILL.md 正文** 。当用户请求命中你的 description 时，Claude 用 bash 把整个 SKILL.md 读进上下文。这里官方建议的上限是 **"Under 5k tokens"** ——不是 5 万，不是 5 千行，是 5 千 token。换算成中文大概 3500-4000 字，换算成 markdown 行数大约 400-600 行。 **你写 2000 行，就是这一层超了 3-4 倍。**

**Level 3 是引用文件和脚本** 。SKILL.md 里写 "see FORMS.md" 或者 "运行 scripts/validate.py"，Claude 只在真的需要时才用 bash 去读那个文件、跑那个脚本。 **没被引用到的文件，永远不进 context。**

![Claude Skills 官方三层加载机制 · 各 Level 的 token 成本与加载时机](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

Claude Skills 官方三层加载机制 · 各 Level 的 token 成本与加载时机

另外两个具体字段限制官方也写得很死：

- `name`
	：最多 **64 字符** ，只能小写字母+数字+连字符，不能含 "anthropic" 或 "claude"
- `description`
	：最多 **1024 字符** ，必须非空，不能含 XML 标签

这些数字不是建议，是 API 校验时硬挡的。

## 二、Progressive Disclosure 是 Skills 的灵魂

为什么 Anthropic 要分三层？因为大模型的注意力是稀缺资源， **塞进 context 的每一个 token 都在和当前任务争抢模型的关注度** 。如果你启动时就把所有可能用到的工作流、模板、示例全塞进上下文，模型在处理实际请求时反而抓不到重点。

官方对这套机制有一个固定术语： **Progressive Disclosure（渐进式披露）** 。原文是这么定义的："Claude loads information in stages as needed, rather than consuming context upfront."（按需分阶段加载，而不是一次性占满上下文）。

这一概念在 UI 设计里早就成熟：好的软件设置页面，常用选项放最顶层，高级选项藏进二级菜单，专家选项再往下藏。用户既能第一眼看到最重要的东西，又不会被一堆细节淹没。Skills 把这套思路从界面层搬到了模型上下文层。

**SKILL.md 在这套架构里扮演的不是"文档"，不是"prompt"，是一个分层引用网络的根节点。** 它的职责只有三件事：

第一， **告诉模型什么时候用这个 Skill** （description 字段 + 主文件开头的触发条件）。 第二， **给模型一棵决策树** （工作流骨架、判断条件、分支处理）。 第三， **告诉模型在每个步骤里去引用哪个子文件** （"详细规则见 rules/style.md"、"模板见 templates/article.md"、"运行 scripts/upload.py"）。

凡是"细节填充"——具体的规则案例、模板正文、长篇示例、参考代码——一律不进主文件，全部下沉到 Level 3 的引用文件。

这就是为什么主文件 5K token 够用。 **它不需要装下所有内容，只需要装下"地图"** 。

Anthropic 官方自己的 Skills 就是这套思路最好的示范。它的 PDF skill 主文件只放"什么场景用、几行 quick start 代码、其它能力请见 FORMS.md / REFERENCE.md"——核心 SKILL.md 加起来才一百多行。但你只要喊一句"帮我填这个 PDF 表单"，模型会自动 bash 去读 FORMS.md，把表单填充的详细规则拉进来。同理 Excel skill 把图表生成的细节拆进单独的 charts.md，PowerPoint skill 把多语言模板拆进 templates/ 目录。 **没有一个官方 skill 的 SKILL.md 超过 200 行。** 这不是巧合，是 Anthropic 团队自己在用这套规范倒逼自己。

## 三、反例 vs 正例：我自己的 SKILL\_main.md 演进史

讲一个真实的演进案例。我自己维护的写作 SKILL 文件，过去半年迭代了三个版本，token 占用降了一半多，触发准确率反而上升。

**第一版（反例）** ：把所有写作规则、文风指南、案例分析、模板、配图规范、上传脚本说明、发布看板说明…… **全部塞进一个 SKILL.md** 。这个文件最高峰大概是 1900 行，换算成 token 大约 14K——超官方上限 180%。

那段时间问题很明显。每次让 Claude "写一篇"，它先得把这 14K 的工作手册读完，剩下的有效上下文被严重挤压。更要命的是，写公众号文章和写算法文章共用一个 SKILL，规则混在一起，模型经常把算法文章的代码风格用到公众号上，或者把公众号的钩子句式用到算法文章里—— **两份规则在主文件里互相干扰，模型抓不到重点** 。

![SKILL.md 反例 vs 正例 · 文件结构对比](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

SKILL.md 反例 vs 正例 · 文件结构对比

**第二版** ：开始拆分，把四个公众号的 SKILL 拆成四个文件（SKILL\_main.md、SKILL\_suanfa.md、SKILL\_chatdamoxing.md、SKILL\_zhihu.md），各管各的风格。这一步把"互相干扰"解决了，但每个文件还是 1000+ 行。因为我当时是机械拆分，没动单文件内部的结构。

**第三版（现在）** ：按 Progressive Disclosure 重新组织每一个 SKILL 文件本身。

主文件 `SKILL_main.md` 现在 **612 行** ，只放三种东西：

- 触发条件（什么场景触发这个 Skill）
- 工作流骨架（10 个步骤、每步一句话）
- 引用索引（细节去看哪个文件）

其他内容下沉成独立文件：

- 文风规范 → `references/style-guide.md` （独立 1100+ 行）
- 历史文章范本 → `references/article_*.md` （数十篇）
- 代码逻辑 → `scripts/*.py` （generate\_image / md\_to\_wechat / upload\_draft / review\_article 等）
- 选题库 → `config/topics.json`
- 账号配置 → `config/accounts.json`

模型触发这个 Skill 时，只会先读 612 行主文件，确定走哪条工作流之后， **才** bash 读对应的子文件。如果用户只是让我"检查标题格式"，模型走前两步就够，连 `style-guide.md` 都不用读，token 占用直接砍到一半以下。

![SKILL.md 拆分前后 · token 占用与触发准确率对比](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

SKILL.md 拆分前后 · token 占用与触发准确率对比

这次重构里有一个特别值得讲的环节—— **Step 10 的视频 handoff** 。我有一个文章 SKILL 和一个视频生成 SKILL，原本想把视频生成的逻辑也塞进文章 SKILL 里，"反正都是写作流程的一部分"。试过两个月之后发现这种思路完全错——把两件不同性质的事塞进一个 SKILL，主文件就会膨胀，决策树就会乱。后来改成：文章 SKILL 走到 Step 10 时只做三件事——复制视频模板副本、注入 input.md、然后 **显式把控制权交给视频副本里的 SKILL.md** 。文章 SKILL 不需要知道视频怎么生成、不需要知道 screens.js 怎么写、不需要知道 TTS 怎么调。这就是 Skill 之间的 handoff 协议—— **每个 Skill 只懂自己那一摊事，靠"路标"互相衔接** 。如果文章 SKILL 强行把视频生成的细节也吞下来，它今天就不可能控制在 612 行。

数据差距非常明显：

| 指标 | 拆分前（单文件 1900 行） | 拆分后（主文件 612 行 + 引用） |
| --- | --- | --- |
| 触发时初始 token 注入 | ~14000 | ~4500 |
| 单次工作流端到端 token 占用 | ~28000 | ~12000 |
| "写错风格" 案例频率 | 偶发（每 20 次约 1 次） | 几乎归零 |
| 维护成本（改一条规则） | 全文件找位置 | 单文件改 |

这套从单一文件拆分到 Progressive Disclosure 主从结构的工程演进，正是我们训练营 Claude Code 工程化实战那一节专门拆的内容。学员不是只听"应该拆分"这种空话，而是真的拿一个 1900 行的烂 SKILL 来手动拆——决定哪些是触发层、哪些是决策树、哪些必须下沉成引用文件、子文件之间又怎么互相引用。做过一遍之后，再被面试官追问 Progressive Disclosure 怎么实现，能讲到具体的 token 数字和取舍逻辑。

## 四、什么时候必须拆，什么时候不必拆

这里给一个工程上很实用的判断标准：

| 你的 SKILL.md 行数 | 状态 | 建议 |
| --- | --- | --- |
| < 200 行（< 2K token） | 健康 | 不用拆 |
| 200-500 行（2-5K token） | 接近上限 | 开始留意，新增内容前先想"能不能放子文件" |
| 500-800 行（5-8K token） | 已超上限 | 必须开始拆 |
| \> 800 行 | 严重超标 | 立刻按 Progressive Disclosure 重构 |

拆的优先级也有规律：

**第一刀** ，先把 **示例和模板** 下沉。这部分长但低频访问，是吃 token 最狠的。 **第二刀** ，把 **详细规则** 拆成 references/rules.md，主文件只留"风格规则见 references/rules.md"。 **第三刀** ，把 **长流程** 封装成脚本，模型 bash 调用即可，连读都不读。

反过来， **不要把决策树拆出去** 。哪个工作流处理哪种请求、判断分支怎么走，这是主文件的命根子，拆出去之后模型读完主文件根本不知道下一步该干嘛。

引用本身也有"好引用"和"坏引用"之分。好的引用写法长这样：

```
## 第三步：审稿

 按文风规范跑一遍审稿，对照标准见 references/style-guide.md。
 关键检查项：开头是否有面试场景、是否有"我是吴师兄"开头收尾、字数是否在 4000-5000 区间。
```

——一句话告诉模型"为什么去看、看哪几条"，模型可以基于这个判断是不是真的需要 bash 去读那个文件。

坏的引用是这样：

```
## 第三步：审稿

 详见 references/style-guide.md。
```

——光甩一个文件名，模型不知道这个文件里有什么、什么场景下值得读， **很可能要么不读跳过这一步、要么每次都全文读浪费 token** 。引用要带上"指路标签"——这个文件存的是什么、什么时候会需要——这是把 Level 3 从"摆设"变成"有效抽象"的关键细节。

另一个常被忽视的工程点是： **子文件之间不要循环引用** 。我见过有人在 rules.md 里写"详细案例见 examples.md"，又在 examples.md 里写"对应规则见 rules.md"，结果模型一旦触发其中一个，连带把另一个也读进来，Level 3 的"按需加载"优势直接归零。正确的做法是让所有子文件都被 SKILL.md 主文件统一索引，子文件之间互相只看不引——这跟前端模块依赖管理是一个套路。

## 五、面试官再问，怎么答

如果时间倒流，回到字节那场二面，正确的答法分三步走。

**先把官方数字钉死（20 秒）。** Anthropic 把 Skills 内容分成三个 Level：Level 1 是 metadata（name + description），约 100 token，永远加载；Level 2 是 SKILL.md 正文，官方建议 under 5k tokens，触发时加载；Level 3 是引用文件和脚本，按需加载、实际无限。我自己写的 SKILL 主文件超过 600 行就会开始拆。

**再讲 Progressive Disclosure 的本质（40 秒）。** 这不是"为了好看才分层"，是"为了不稀释模型注意力"。主文件只放三件事：触发条件、决策树、引用索引。所有细节下沉到子文件，模型用 bash 按需读取。SKILL.md 不是文档，不是 prompt，是 **分层引用网络的根节点** 。

**最后讲实战拆法（30 秒）。** 拆的优先级是示例 → 规则 → 长流程。决策树不能拆，否则模型读完主文件不知道下一步。我自己的 SKILL\_main.md 从 1900 行拆到 600 行，单次工作流 token 从 28K 降到 12K，触发准确率反而上升，因为主文件不再被无关细节稀释。

这三段答完，加起来不到两分钟。资深面试官听到 5K token、Level 1/2/3、Progressive Disclosure、拆分优先级，就知道你不是在背概念， **是真的写过 Skill 并且优化过** 。

## 六、Skills 工程化是 2026 年的新工程能力

最后说一个判断标准。

**Skills 是一种新的工程能力，跟"会写 prompt"是两件事。** 写 prompt 比的是"能不能让模型这次输出对"；写 Skill 比的是"能不能让模型在未来 100 次都能稳定输出对，并且 token 还省"。前者是经验，后者是架构。

这种能力跟传统软件工程其实非常像——把功能拆成职责单一的模块、用接口隔离细节、给每个模块写清楚 contract、避免循环依赖、用文档导航而不是把所有信息平铺。 **Skills 工程化把"模块化"这套老思路搬到了模型上下文的管理上** ——只不过这次模块之间传的不是函数返回值，是触发条件和文件引用；不是 CPU 时间，是 token 预算。

面试官在 2026 年问 Skills，问得越细越说明他想看的是架构判断力，不是 API 熟练度。能讲到 5K token、能讲到三层加载、能讲到 Progressive Disclosure 的工程取舍、能讲到自己的拆分案例和 handoff 设计，才说明你在用工程的眼光看待 Claude Code 这套体系。

今天这道题，只是大模型面试中 Claude Code 工程化的一个切面。

真正的面试官不会只问这一问。他们会顺着你的回答追下去，追到你答不上来为止——判断的就是你到底做没做过这个系统。

背答案的人和真正做过的人，说话方式完全不一样。前者说"SKILL.md 写得规范一点"；后者说"我把 SKILL\_main.md 从 1900 行拆成主文件 612 行 + 7 个引用文档之后，Claude 触发 skill 的初始注入从 14K token 降到 4.5K，单次工作流端到端 token 占用从 28K 降到 12K，触发准确率反而上升——因为主文件不再被无关细节稀释，决策树更清晰"。

面试官三句话就能听出来你是哪种人。

如果你想成为后者，欢迎了解我们的大模型训练营。训练营里专门有一节讲 Claude Code 工程化实践，SKILL 设计、MCP 集成、Memory 调优，这些恰好是面试官在问、市面教程几乎不讲的部分。

往期推荐

[在字节食堂打饭，我问同事 Memory 爆了怎么办，打饭阿姨头也没抬："你把'对花生过敏'压成'饮食偏好'，下次点外卖咋办？"](https://mp.weixin.qq.com/s?__biz=MzkzMDIwMzg1Mw==&mid=2247490463&idx=1&sn=984aaa194a79f319992f736ec3c78ebd&scene=21#wechat_redirect)

[鹅厂面试官："MCP 就是 Function Calling 套了层壳？" 我刚想点头，他："你点头之前先想三秒。"](https://mp.weixin.qq.com/s?__biz=MzkzMDIwMzg1Mw==&mid=2247490455&idx=1&sn=06896a9ca5c3086851d3e3ab9581f3cb&scene=21#wechat_redirect)

[字节面试官皱眉："Claude Skills 我也在用，但你 SKILL.md 写了 2000 行，是把它当 prompt 还是当文档？"](https://mp.weixin.qq.com/s?__biz=MzkzMDIwMzg1Mw==&mid=2247490449&idx=1&sn=f1e345f0d5510c69ba8c7af7aca989de&scene=21#wechat_redirect)

[阿里面试官冷笑："现在上下文窗口都 200 万 token 了，你的 RAG 还有存在的必要吗？" 我算了一笔账，他沉默了](https://mp.weixin.qq.com/s?__biz=MzkzMDIwMzg1Mw==&mid=2247490388&idx=1&sn=45180b1b2bff0b2359e76764cd48e4a1&scene=21#wechat_redirect)

大厂真题 · 目录

继续滑动看下一个

吴师兄学大模型

向上滑动看下一个