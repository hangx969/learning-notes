---
title: "Mnilax：CLAUDE.md 规则从 Karpathy 的 4 条增加到 12 条，错误率从 41% 降到 3%"
source: "https://x.com/Mnilax/status/2053116311132155938"
created: 2026-05-15
tags:
  - claude-code
  - CLAUDE-md
  - best-practices
---

> 一篇 X 长帖，Mnilax 在 Karpathy 原版 4 条规则的基础上，花了 6 周在 30 个代码库上实测，新增了 8 条新规则。错误率从 41% 降到 3%。

---

2026 年 1 月底，Andrej Karpathy 发了一条长帖吐槽 Claude 写代码的三个问题：静默错误假设、过度复杂化、波及非目标代码。Forrest Chang 把这些问题提炼成了 4 条行为规则，放进 CLAUDE.md 文件，传到了 GitHub。文件发布第一天 5582 颗星，两周 6 万书签，到今天 12 万星——**2026 年增长最快的单文件仓库**。

5 月，Mnilax 发现一个问题：Karpathy 的模板是为 1 月的代码编写问题设计的。5 月的 Claude Code 生态已经有了新的病灶——Agent 冲突、Hook 级联、Skill 加载冲突、跨会话断裂的多步工作流。

于是他做了件很硬核的事：**30 个代码库，50 个标准任务，6 周持续测试**。

---

## 一、CLAUDE.md 是 AI 编程栈里最被低估的文件

大多数开发者的 CLAUDE.md 处于三种状态之一：

- **什么都往里塞**，膨胀到 4000+ token，遵循率掉到 30%
- **完全跳过**，每次手动 Prompt——5 倍 Token 浪费，会话之间零一致性
- **复制一个模板就忘了**，用两周还行，代码库一变就静默失效

Anthropic 的官方文档说得很清楚：CLAUDE.md 是建议性的，Claude 大约遵循 80%。**超过 200 行，遵循率急剧下降**——因为重要规则被埋在了噪音里。

---

## 二、原版 4 条规则——底线，不是天花板

**规则 1——先思后码。** 明确声明前提假设，阐明方案权衡。有疑问先确认，切忌盲目猜测。

**规则 2——简单至上。** 仅以最少代码解决问题。不添加"以防万一"的冗余功能，不为仅用一次的代码强行设计抽象层。

**规则 3——外科手术式修改。** 仅改动绝对必要的部分。切勿"顺手优化"相邻代码、注释或格式排版。

**规则 4——目标驱动执行。** 明确定义成功标准（验收条件）。持续迭代直至验证通过。

这四条规则大约能覆盖 ~40% 的失败模式。而剩余约 60% 的问题，存在于下述的空白地带中。

---

## 三、补齐的 8 条规则——每条都来自一个真实翻车场景

### 规则 5：模型只做判断，不做决策

> 适用于 Claude 的任务：分类、内容起草、摘要总结、非结构化文本信息提取。
> 切勿将 Claude 用于：路由分发、重试机制、状态码处理、确定性数据转换。
> 若状态码本身已能明确判定结果，直接使用常规代码即可。

**翻车现场：** 一段调用 Claude 去"判断 503 该不该重试"的代码，稳定运行两周后出问题——因为模型开始把请求体内容当成决策的上下文。重试策略变成了随机的。

### 规则 6：硬性 Token 预算，没有例外

> 单任务预算：4,000 Token。单会话预算：30,000 Token。
> 任务接近预算上限时，立即执行摘要总结并重置上下文。切勿强行推进。
> 主动暴露超支 > 静默越界消耗。

**翻车现场：** 某次调试会话持续 90 分钟。模型对着同一条 8KB 错误日志反复迭代，逐渐丢失了已尝试修复方案的上下文记忆。到对话末尾，它开始建议 40 条消息前就已否决的方案。

### 规则 7：暴露冲突，不要折中

> 若代码库中既有的两种模式相互矛盾，切勿强行融合。
> 明确选择其一（优先采用更新或经过更充分测试的版本），阐明选择理由，并将另一种标记为待清理项。

**翻车现场：** 某代码库中并存 async/await try/catch + 全局 Error Boundary 两种错误处理模式。Claude 写的新代码将两者强行叠加，异常被重复捕获并静默"吞掉"两次。

### 规则 8：先读后写

> 在文件中追加代码前，务必通读该文件的导出接口、直接调用方，以及任何显而易见的公共工具函数。
> 若你无法理解现有代码为何采用当前结构，在动手添加前必须先提问确认。

**翻车现场：** Claude 在一个已有相同功能的函数旁边加了一个新函数——它没读到那个已有函数。两个函数做一样的事，新函数因导入顺序而优先执行。

### 规则 9：测试验证意图，而非仅验证行为

> 每个测试都必须明确体现该行为*为何重要*（WHY），而不仅仅是断言它*做了什么*（WHAT）。
> 如果你无法写出一个在业务逻辑变更时会失败的测试，那就说明该函数本身的设计就是错误的。

**翻车现场：** Claude 为某认证函数编写了 12 个测试，全部通过。然而生产环境认证功能彻底失效——测试仅验证了"是否返回了数据"，而非"是否返回了正确数据"。

### 规则 10：长任务必须设检查点

> 在执行多步骤任务时，每完成一个关键节点后必须执行状态同步：明确总结已实施操作、已验证结果，以及剩余待办事项。
> 若无法向我清晰描述当前上下文与执行状态，绝不可继续推进。

**翻车现场：** 一个 6 步重构在第 4 步出了问题。Claude 在错误状态上继续完成了第 5 和第 6 步。拆解比整个重做还花时间。

### 规则 11：约定胜于新奇

> 在代码库内部：规范一致性 > 个人技术偏好。
> 若确信某规范存在实质性危害，请显式提出。切勿暗中另起范式。

**翻车现场：** Claude 在一个 class 组件的代码库里引入了 React hooks。能跑，但搞坏了测试模式——测试假定有 componentDidMount。花了半天时间删除和重写。

### 规则 12：显性失败，不要静默

> 若有 30 条记录被静默跳过，宣称"迁移完成"便是错误结论。
> 若有任意测试被跳过，宣称"测试通过"便是错误结论。
> 默认原则：主动暴露不确定性，绝不掩盖。

**翻车现场：** Claude 说一次数据库迁移"成功完成"。它悄悄跳过了 14% 因为约束冲突没处理的记录。11 天后报告数据开始对不上时才发现。

---

## 四、从 41% 到 3%：实测数据

Mnilax 用三组配置测试了同一批 50 个标准任务：

| 配置 | 错误率 | 合规率 |
| --- | --- | --- |
| 无 CLAUDE.md | ~41% | N/A |
| Karpathy 4 条 | ~11% | ~78% |
| 完整 12 条 | ~3% | ~76% |

真正值得关注的结果：规则从 4 条扩展至 12 条，**几乎未增加合规执行开销**（78% → 76%），却将错误率进一步降低了 8 个百分点。新增规则覆盖了原始 4 条未能触及的失败模式——它们并非在争夺同一份注意力预算，而是形成了互补增强。

---

## 五、原版 4 条规则的局限性

1. **长任务 Agent**：缺乏预算约束、状态检查点和"显式报错"机制，任务流在长时间运行中极易发生语义漂移
2. **多代码库一致性**："匹配既有风格"预设了环境的单一性，Monorepo 中面临多种风格博弈
3. **测试质量**：将"测试通过"与"任务成功"画等号，忽略了测试本身的有效性与完备性
4. **生产 vs 原型**：防止过度设计的约束在原型开发阶段反而成为迭代枷锁

---

## 六、试过但放弃的

- **从 Reddit/X 看来的规则**：大多数是 Karpathy 4 条的翻版，或不可泛化的领域特化规则。删了。
- **超过 12 条**：测到 18 条，合规率从 76% 掉到 52%。**200 行天花板是真的**。
- **在 CLAUDE.md 里放例子**：例子比规则重，三个例子消耗约 10 条规则的上下文，而且 Claude 会过度拟合。用规则。
- **"小心"/"多想"/"真正专注"**：纯噪音。合规率掉到约 30%——因为它们不可测试。替换为具体的祈使句。
- **让 Claude 做"高级工程师"**：没用。Claude 已经觉得自己是高级的。差距在"想"和"做"之间。祈使句规则能闭合这个差距；身份提示不能。

---

## 七、12 条完整模板

Mnilax 提供了可以直接粘贴的完整版本。以下是核心 12 条（项目专属规则如技术栈、测试命令、错误模式需另外追加，总行数控制在 200 以内）：

~~~markdown
# CLAUDE.md — 12 条规则模板

除非显式覆盖，否则本规则适用于本项目中的所有任务。
核心倾向：非琐碎工作，谨慎优先于速度；琐碎任务可自主判断处理。

## 规则一：先思后码（Think Before Coding）

明确声明前提假设。遇不确定处，先提问而非盲目猜测。
存在歧义时，列出多种可能的理解路径。
若存在更简方案，应果断提出异议。
陷入困惑时立即暂停，并明确指出模糊之处。

## 规则二：简单至上（Simplicity First）

仅用最少代码解决问题。
杜绝任何"以防万一"的猜测性实现。
不实现需求之外的功能。
不为仅用一次的代码强行设计抽象。
自检：资深工程师是否会认为此实现过度复杂？若是，立即简化。

## 规则三：外科手术式修改（Surgical Changes）

仅改动绝对必要的部分。
仅清理自身引入的冗余或错误。
切勿"顺手优化"相邻代码、注释或排版格式。
未出问题的代码绝不重构。
严格贴合项目既有风格。

## 规则四：目标驱动执行（Goal-Driven Execution）

明确定义成功标准（验收条件）。
持续迭代直至验证通过。
不要死板遵循步骤。定义成功形态并自主迭代。
清晰的成功标准赋予你独立闭环执行的能力。

## 规则五：仅将模型用于判断与裁量场景（Use the model only for judgment calls）

适用于我：分类、起草、摘要总结、信息提取。
切勿用于：路由分发、重试机制、确定性数据转换。
若常规代码能给出答案，就由代码处理。

## 规则六：Token 预算绝非软性建议（Token budgets are not advisory）

单任务上限：4,000 Token。
单会话上限：30,000 Token。
接近预算上限时，执行上下文摘要并重置状态。
主动暴露超支。切勿静默越界消耗。

## 规则七：显式暴露冲突，拒绝折中调和（Surface conflicts, don't average them）

若两种模式相互矛盾，明确择一（优先更新或更经测试的版本）。
阐明选择理由。
将另一处标记为待清理项。
切勿强行融合冲突范式。

## 规则八：落笔前先阅读（Read before you write）

添加代码前，通读该文件的导出接口、直接调用方及公共工具函数。
"看似互不干涉"是最危险的判断。
若不理解现有代码为何如此设计，先提问。

## 规则九：测试验证意图，而非仅验证行为（Tests verify intent, not just behavior）

测试必须体现该行为*为何重要*（WHY），而非仅断言它*做了什么*（WHAT）。
若业务逻辑变更时测试仍不报错，则该测试设计错误。

## 规则十：关键步骤后强制设立检查点（Checkpoint after every significant step）

总结已完成事项、已验证结果及剩余待办。
若无法向我清晰描述当前状态，绝不可继续推进。
若丢失上下文或逻辑偏离，立即暂停并重新声明当前状态。

## 规则十一：严格遵从代码库既有规范，即便持保留意见（Match the codebase's conventions, even if you disagree）

在代码库内部：规范一致性 > 个人技术偏好。
若确信某规范存在实质危害，请显式提出。
切勿暗中另起范式。

## 规则十二：显式失败（Fail loud）

若有步骤被静默跳过，宣称"已完成"即为错误。
若有测试被跳过，宣称"测试通过"即为错误。
默认原则：主动暴露不确定性，绝不掩盖。
~~~

```markdown
# CLAUDE.md — 12-rule template

These rules apply to every task in this project unless explicitly overridden.
Bias: caution over speed on non-trivial work. Use judgment on trivial tasks.

## Rule 1 — Think Before Coding
State assumptions explicitly. If uncertain, ask rather than guess.
Present multiple interpretations when ambiguity exists.
Push back when a simpler approach exists.
Stop when confused. Name what's unclear.

## Rule 2 — Simplicity First
Minimum code that solves the problem. Nothing speculative.
No features beyond what was asked. No abstractions for single-use code.
Test: would a senior engineer say this is overcomplicated? If yes, simplify.

## Rule 3 — Surgical Changes
Touch only what you must. Clean up only your own mess.
Don't "improve" adjacent code, comments, or formatting.
Don't refactor what isn't broken. Match existing style.

## Rule 4 — Goal-Driven Execution
Define success criteria. Loop until verified.
Don't follow steps. Define success and iterate.
Strong success criteria let you loop independently.

## Rule 5 — Use the model only for judgment calls
Use me for: classification, drafting, summarization, extraction.
Do NOT use me for: routing, retries, deterministic transforms.
If code can answer, code answers.

## Rule 6 — Token budgets are not advisory
Per-task: 4,000 tokens. Per-session: 30,000 tokens.
If approaching budget, summarize and start fresh.
Surface the breach. Do not silently overrun.

## Rule 7 — Surface conflicts, don't average them
If two patterns contradict, pick one (more recent / more tested).
Explain why. Flag the other for cleanup.
Don't blend conflicting patterns.

## Rule 8 — Read before you write
Before adding code, read exports, immediate callers, shared utilities.
"Looks orthogonal" is dangerous. If unsure why code is structured a way, ask.

## Rule 9 — Tests verify intent, not just behavior
Tests must encode WHY behavior matters, not just WHAT it does.
A test that can't fail when business logic changes is wrong.

## Rule 10 — Checkpoint after every significant step
Summarize what was done, what's verified, what's left.
Don't continue from a state you can't describe back.
If you lose track, stop and restate.

## Rule 11 — Match the codebase's conventions, even if you disagree
Conformance > taste inside the codebase.
If you genuinely think a convention is harmful, surface it. Don't fork silently.

## Rule 12 — Fail loud
"Completed" is wrong if anything was skipped silently.
"Tests pass" is wrong if any were skipped.
Default to surfacing uncertainty, not hiding it.
```

---

## 八、心智模型

1. **CLAUDE.md 不是许愿清单。** 是一个闭合了你观察到过的特定失效模式的行为合约。每条规则都应该能回答一个问题：这条规则预防的是什么错误？
2. **6 条针对你真踩过的坑的规则，比 12 条里有 6 条你永远用不上的更好。** Karpathy 的 4 条是地基——别跳过。补齐的那些选你实际需要的。读完全部 12 条，保留那些映射到你真实翻车现场的规则，其余的可以不要。

> "模型进步了。生态变了。多步 Agent、Hook 级联、Skill 加载、多代码库工作——Karpathy 写那条帖子的时候这些都不存在。4 条规则没错；是不够用。8 条新规则。6 周在 30 个代码库上的测试。错误率从 41% 到 3%。"
