---
title: "Planning with Files：让 AI 像顶级工程师一样稳扎稳打做项目"
source: "https://mp.weixin.qq.com/s/hSUuFfu8rbkfB88D18i8uQ"
created: 2026-05-18
tags:
  - claude-code
  - skills
  - planning
---

# Planning with Files：AI 项目规划 Skill

用 AI 做项目时常见的问题：聊着聊着就跑偏、做到一半忘目标、上下文一清空直接重来、反复踩同一个坑、复杂任务直接乱套。

**Planning with Files**（GitHub 21.4K Star）专门解决这些问题——让 AI 把所有计划、进度、坑点、成果全写成本地文件，不丢失、不跑偏、不返工。

- GitHub 地址：https://github.com/OthmanAdi/planning-with-files
- 协议：MIT 开源免费
- 支持平台：Claude Code / Cursor / GitHub Copilot / Gemini / Hermes / Codex / OpenCode 等 17+

## 一、核心特性

| 能力 | 说明 |
| --- | --- |
| 文件当记忆，永不丢失 | 计划、发现、进度存在 3 个 Markdown 文件里，关软件/清上下文/重启电脑都还在 |
| 先规划再动手 | AI 自动生成任务计划，分阶段、打勾推进，一步一步稳扎稳打 |
| 自动记坑，不重复犯错 | 所有错误、失败、问题自动记录，AI 下次自动避开 |
| 支持 17+ AI 平台 | Claude Code、Cursor、Copilot、Gemini、Hermes、OpenCode 全能用 |
| 自动恢复上下文 | 清屏/重启后，AI 自动读取文件恢复进度，不用重新说明 |
| 严格对齐目标 | 每一步都会对照计划，确保不偏离需求 |

## 二、与普通 AI 的对比

| 场景 | 普通 AI | Planning with Files |
| --- | --- | --- |
| 记忆 | 关窗就忘，依赖上下文 | 文件永久记忆，永不丢失 |
| 任务规划 | 想到哪做到哪，容易乱 | 自动分阶段，结构化推进 |
| 错误处理 | 错了就忘，反复踩坑 | 自动记录错误，绝不重复 |
| 长项目 | 做着做着跑偏 | 全程对齐目标，绝不走歪 |
| 恢复进度 | 要从头解释 | 一键恢复，无缝继续 |
| 成功率 | 复杂任务很低 | 测试通过率 96.7% |

## 三、使用方法

### 3.1 一键安装

~~~bash
npx skills add OthmanAdi/planning-with-files --skill planning-with-files -g
~~~

### 3.2 在 AI 里启动

输入命令开启规划模式：

~~~bash
/plan
~~~

### 3.3 自动生成 3 个核心文件

| 文件 | 用途 |
| --- | --- |
| `task_plan.md` | 任务计划与进度——分阶段任务列表，打勾推进 |
| `findings.md` | 资料、研究、结论——项目过程中的发现和决策记录 |
| `progress.md` | 过程记录、测试、日志——错误记录和执行日志 |

AI 会自动按计划执行、记录、检查、完成，全程不用你盯。

## 四、核心价值

借鉴 Meta 20 亿美金收购的 Manus AI 工作法——把 AI 的工作过程文件化：

- **文件化规划**：所有任务拆解为结构化的 Markdown 文件
- **外置记忆**：不依赖上下文窗口，文件就是持久记忆
- **稳定执行**：每一步对照计划，错误自动记录避免重犯
- **长任务神器**：任务成功率从 6.7% → 96.7%

## 五、与知识库中其他 Skills 的对比

| Skill | 定位 | 核心机制 |
| --- | --- | --- |
| **Planning with Files** | 项目规划与进度管理 | 3 个 Markdown 文件（计划/发现/进度），结构化推进 |
| andrej-karpathy-skills | 编码行为约束 | 4 条行为规则，减少 AI 编码错误 |
| code-review-graph | 代码知识图谱 | Tree-sitter AST 解析 + blast-radius 影响分析 |
| Skill Craft | Skill 质量检测 | 7 类失效模式检测 + check/fix/create/audit 四模式 |
| superpowers (obra) | 强制工程师流程 | 22 个 Skill，TDD + 头脑风暴 + 代码审查 |
