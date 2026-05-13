---
title: "Skill 太多导致上下文膨胀怎么办？ 来自 Hermes Agent 的一些实践"
source: "https://mp.weixin.qq.com/s/eTE8rk-mCsqo0w88VmzYGw?scene=1&click_id=147"
author:
  - "[[AI技术立文]]"
published:
created: 2026-05-13
description: "自我改进型 Agent 的技能会无限堆积，Agent 最终在每次提示时都在重读自己过去的作品。Hermes Curator 是刚发布的后台维护系统，通过监测→降级→复盘→锁定四步，自动管理 Agent 创建的技能文件，防止技能目录腐化。本文解析 Curator 的设计原理。"
tags:
  - "clippings"
---
AI技术立文 *2026年5月7日 00:03*

**目录**

1. Curator 如何管理 Skill
2. Curator 的四步工作流
3. Skill 膨胀的数学
4. Skill 与记忆的区别
5. Skill 在 Agent 运行时中的位置

---

自我改进型 Agent（如Hermes）一个显著的特点是能够自我学习，这种自我学习，一般是通过将历史内容总结为Skill来实现的。这就导致了一个问题-Skill膨胀。每个 Agent 写下的Skill都会永远保留，哪怕从未被用过。如何解决这个问题？Hermes Agent给出了实践，推出了 Hermes Curator专门处理Skill膨胀，方案供大家参考。

Hermes Curator 是一个后台维护系统，专门管理 Agent 自己创建的Skill。它追踪每个Skill被查看、使用和打补丁的频率，将长期未使用的Skill流转到活跃 → 陈旧 → 归档状态，并定期触发一次辅助模型的简短审查，提出合并建议或修复Skill漂移。

它的存在，是为了防止通过自我改进循环创建的Skill无限堆积。

## 1\. Curator 如何管理 Skill？

Hermes Agent 会将Skill保存为文件，伴随 Agent 一起学习。每个"Agent 创建"的已保存Skill都会成为Skill文件夹里的一个文件。没有维护，这个文件夹就会无限膨胀——Agent 每次提示都要加载更多内容，Skill目录变成了噪音。

Curator 就是 Hermes Agent 推出的清理系统，目的就是阻止这种情况。

它只在你的 Agent 闲置时运行。大约每周一次，当 Agent 空闲至少两小时后，它会醒来，在后台运行一次审查。审查分两部分。

![图1. Hermes Curator Skill生命周期：telemetry-driven 状态机 + 分支审查通道](https://mmbiz.qpic.cn/mmbiz_jpg/IUJGIjicknic2tmUXojicpvVtUKN2UGaGic7NgzCa01PiasdMTvmHtVb3FJD0ic0MVNZQ8m9gyajqJzLpVE0wVBcGm7zCwuic4S7LQp8hoHH8vAm1w/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

**第一部分是自动的。** Curator 检查每个Skill的最后使用时间。任何 30 天未触碰的Skill都会被标记为陈旧。任何 90 天未触碰的Skill会被移入归档文件夹。不会有任何内容被删除，任何已归档的Skill都可以用一条命令恢复回来。

**第二部分使用一个单独的、更便宜的模型。** 这个模型读取 Agent 写下的Skill，判断哪些重叠了、哪些漂移了，以及哪些应该被合并、打补丁或归档。因为它运行在一个辅助槽位上，你可以指向一个廉价模型（如 Gemini Flash），而不必在日常家务上支付主对话模型的费用。

> 所有这些数字都可以在 config.yaml 的 curator: 下配置。如果 30 天对你的工作流来说太激进，可以调大。如果你想每天运行一次审查，把间隔调小即可。

你可以通过 config.yaml 或 Hermes Curator CLI 来管理它。

有三个值得特别指出的护栏：

- Curator 只操作 Agent 写的Skill或你手动写的Skill。随 Hermes 原装的Skill或你从 hub 安装的Skill不受影响。
- 你可以锁定任何Skill。被锁定的Skill对自动计时器和审查模型都是不可见的。就连 Agent 自己的编辑工具也会拒绝修改被锁定的Skill。这是你保护任何依赖项的杠杆。
- Curator 使用的每个计数器和时间戳都保存在Skill文件夹内部的一个伴生文件里。你可以读取它，可以审计它。没有隐藏的数据库。

## 2\. Curator 的四步工作流

Curator 做四件事： **监测、降级、复盘、锁定优先。**

1. **监测。**
	每次Skill被加载到提示中或被 Agent 读取时，计数器就会增加，并写入一个时间戳。那个伴生文件记录了每个Skill实际被使用的次数和时间——也就是它的价值记忆。
2. **降级。**
	如果某个Skill 30 天没有被触碰，它会从活跃降级到陈旧。陈旧Skill仍然能用，但系统已经将它们标记为可疑。如果再过 60 天仍然没有触碰，它们会被移出活动文件夹，进入归档文件夹。不会有任何内容被删除。你随时可以用一条命令拉回某个Skill。
3. **复盘。**
	大约每周一次，当 Agent 空闲几小时后，一个单独的廉价模型会醒来并读取Skill文件夹。它寻找漂移的Skill、重叠的Skill，以及应该被合并为一条更简洁版本的Skill。它可以打补丁、合并，或将它们发送到归档。然后继续睡觉。
4. **锁定优先。**
	任何你标记为锁定的内容，对降级计时器和审查模型都是不可见的。就连 Agent 自己也不能重写一个被锁定的Skill。这保证了任何你依赖的Skill不会在你脚下漂移。

这就是全部用户可见行为。监测、降级、复盘、锁定优先。

### Curator CLI

你不必等待每周一次的 Curator 清理。Curator 提供了一个小型 CLI 界面，让你检查状态、触发运行、暂停，或保护特定Skill。

```bash
hermes curator status              # 上次运行时间、计数、锁定列表、LRU 前5
hermes curator run                 # 立即触发复盘（默认后台运行）
hermes curator run --sync          # 同上，但阻塞直到LLM复盘完成
hermes curator pause               # 停止运行，直到恢复
hermes curator resume
hermes curator pin <skill>        # 永不让此Skill自动流转
hermes curator unpin <skill>
hermes curator restore <skill>     # 将已归档Skill移回活跃状态
```

日常最有用的命令是 `hermes curator status` 。除了上次运行时间戳和计数之外，它还会列出五个最近最少使用的Skill，这是快速判断哪些最可能下一步变为陈旧的方法。如果你发现列表里有你实际想保留的Skill，在下次运行前用 `hermes curator pin` 锁定它。

## 3\. Skill 膨胀的数学

数学很简单。即使每天保存一个新Skill，Skill目录一个月就会达到 30 条，一年达到 365 条。通过 Curator 复盘合并近似重复项，每月大约只存活 3 条唯一Skill。也就是说一年大约 36 条，而不是 365 条。

![图2. 有无 Hermes Curator 的 Agent 创建Skill数量对比](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

大多数"Agent 创建"的Skill并非唯一。Agent 会在五天里用五种不同方式写"修复 bug"，彼此互不知晓。

Curator 的复盘正是为解决这一问题而设计：它读取目录、识别重叠，将近似重复项合并为一个规范Skill，同时将冗余副本移入归档。

如果不做任何修剪，两件事会出问题：

1. **Token 账单上涨，**
	因为每次提示都要读取一个越来越大的目录。
2. **推理质量下降，**
	因为五个近似重复的Skill都对同一查询有响应，模型没有好的信号来判断选择哪个。

有时它选错了。有时它会尝试同时使用两个。无论哪种情况，目录越大，Agent 越慢、越笨。

Curator 的设计选择充满了踩坑后的妥协。它每周只运行一次，只在 Agent 空闲至少两小时后运行，而且始终在单独的进程中运行，因为团队不希望清理过程干扰你的实时工作。锁定功能存在，是因为如果不管，Agent 会重写你依赖的Skill。锁定与 Agent 核心记忆使用的是同一合约：Agent 禁止覆盖的事实。

## 4\. Skill 与记忆的区别

有必要精确区分 Curator 处理的"记忆"类型，因为这个领域倾向于将两个截然不同的东西混为同一词汇。

大多数人口中的"记忆"，是 Agent 知道的东西：关于用户、项目和领域的事实。过去的对话以及由此产生的决策。Agent 需要随时获取的参考资料。

记忆保存着 Agent 运作其中的上下文。记忆层是这些内容所在的地方，由相应的记忆管理系统负责。

![图3. 记忆与 Skill 层](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

Skill 则不同。Skill 是活在 Agent 行动和项目核心的程序性知识。它是 Agent 给自己写的操作指南：如何预订航班、如何重构文件、如何查询特定 API。Skill 告诉 Agent 如何工作。Skill 层是这些内容所在的地方，Hermes Curator 是管理它的系统。

这两个系统并不竞争。它们处理同一问题的不同部分：保持 Agent 积累状态的有用性，而不仅仅是重量。记忆整合处理 Agent 知道什么。Curator 处理 Agent 如何工作。两者共同覆盖长期运行 Agent 需要维护的两个方面。

> 重要的原因：看到 Curator，很容易认为这只是记忆管理。它们处于不同的层，以不同的速度衰减，需要不同的清理逻辑。构建一个不能替代另一个。两者都构建，才能得到一个真正持续学习的 Agent。

## 5\. Skill 在 Agent 运行时中的位置

Agent 运行时的形态在不断扩展。

几年前，一个 Agent 就是一个模型加一个提示。然后我们添加了：

- 工具注册表，让它能行动
- 记忆层，让它能跨会话记忆
- 长上下文窗口技巧，让它能一次性读取更多内容

今天，一个正经的 Agent 运行时拥有的管道比 Agent 本身还多。有一个服务层，带 KV 缓存逐出。有一个长期记忆层，带周期性整合，由自己的后台模型运行。有一个Skill层，带使用追踪、状态流转、锁定和单独的审查通道。

管理Skill层的层就是 Hermes Curator。

还有一个工具层，带权限管理；一个提示缓存，带过期机制；一个编排器，决定哪个后台任务何时运行。

Agent 实际上同时在维护四种不同的记忆：

- 缓存在工作记忆，每次轮次使用后丢弃。
- 向量库里的语义记忆，保存 Agent 可查找的事实。
- 对话日志里的情景记忆，事件记录。
- Skill文件夹里的程序性记忆，操作指南库。

每种记忆以自己的速度衰减，以自己的节奏填充，需要自己的后台静默清理进程。

## 要点

Hermes Curator 是自我学习型 Agent 应有的清理方案。它监测被使用的内容，淘汰未被使用的，合并重复项，并让你锁定任何不想被触碰的东西。行为很简单。令人惊讶的是此前没有人构建它。

如果你在构建能保存自己Skill的 Agent，清理通道不再是可选项的基础设施。

没有上下文管理层，每周都会给你的未来自我留下更多要整理的Skill，你依赖的Skill迷失在噪音中的概率也越大。

自我改进型 Agent 需要自我修剪系统和上下文管理。

**微信扫一扫赞赏作者**

继续滑动看下一个

AI技术立文

向上滑动看下一个