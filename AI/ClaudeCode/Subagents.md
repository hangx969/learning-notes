---
title: Claude Code SubAgents
tags:
  - AI
  - claude-code
  - subagent
aliases:
  - 子智能体
---

# SubAgents(子智能体)

每个 SubAgent 是完全独立的 Claude 副本,你需要:手动指定角色定位(如 security-auditor、performance-engineer)、提供必要上下文、明确任务边界和产出。

SubAgent 是用户通过 Markdown 文件(`.md`)自定义的==系统提示 + 工具配置==组合。

---

## 组成

每个 subagent 是一个 md 文件,核心主要由 5 部分组成:

- **name**:agent 名字
- **description**:对于 agent 的描述,核心说明这个 agent 的作用是什么,Claude 要在什么情况下调用这个 agent
- **tools**:这个 agent 能调用的工具,可以设置多个工具
- **model**:agent 使用的模型
- **system**:系统提示词,该 agent 的角色定位、规则限制、输出风格、工作流程等

---

## 产品逻辑

subagent 的产品逻辑是将自己处理的结果返回给 Claude Code,Claude Code 会将各个子 agent 返回的这些结果统一处理后将最终内容输出给你,所以要注意 subagent 的输出对象不是你,而是 Claude Code,Claude Code 的输出对象才是你。

---

## 典型场景

你:"这个支付模块需要全面审查"

并行创建 5 个 Task:

1. 架构分析 SubAgent → 模块设计和接口审查
2. 安全审计 SubAgent → SQL 注入、XSS、CSRF 检查
3. 性能分析 SubAgent → 慢查询和瓶颈定位
4. 代码质量 SubAgent → 测试覆盖和规范检查
5. 数据库 SubAgent → 索引和查询优化建议

- 30 分钟返回 5 份报告(串行需 2.5 小时)
- 成本:5 倍 token,节省 80% 时间,ROI 极高
- 成本模型:这是一个==时间换成本==的策略,而非成本优化。线性累加(5 个 = 5 倍),但节省时间通常 50-80%

### 适用与不适用场景

1. (★★★★★) **极度推荐**:多角度代码审查、项目规划、文档生成(任务完全独立)
2. (★★★★☆) **推荐**:文件批处理、API 集成测试(任务独立)
3. (★★☆☆☆) **不推荐**:迭代式功能调试(因其无状态特性)
4. (★☆☆☆☆) **禁止**:任务间有依赖、敏感数据处理、单一复杂任务(不需要并行)

---

## 存储位置

> [!info] 参考文档
> [SubAgent Storage Locations](https://github.com/VoltAgent/awesome-claude-code-subagents?tab=readme-ov-file#subagent-storage-locations)

| Type              | Path                | Availability         | Precedence |
| ----------------- | ------------------- | -------------------- | ---------- |
| Project Subagents | `.claude/agents/`   | Current project only | Higher     |
| Global Subagents  | `~/.claude/agents/` | All projects         | Lower      |

> [!note]
> When naming conflicts occur, project-specific subagents override global ones.

---

## 新建 subagent

> [!info] 参考文档
> [Setting Up in Claude Code](https://github.com/VoltAgent/awesome-claude-code-subagents?tab=readme-ov-file#setting-up-in-claude-code)

1. Place subagent files in `.claude/agents/` within your project
2. Claude Code automatically detects and loads the subagents
3. Invoke them naturally in conversation or let Claude decide when to use them

---

## Agent 仓库

常见的 subagent 在 GitHub 上也有很多人已经整理好了,更多可查看:[awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents),里面有 100 多个 agent,可以进行按场景挑选使用,直接对照文档安装即可。
