每个SubAgent是完全独立的Claude副本,你需要:手动指定角色定位(如security-auditor、performance-engineer)、提供必要上下文、明确任务边界和产出。

SubAgent是用户通过Markdown文件(.md)自定义的 系统提示 + 工具配置 组合。

# 组成
每个subagent是一个md文件，核心主要由5部分组成：

- name：agent名字；
- description：对于agent的描述，核心说明这个agent的作用是什么，claude要在什么情况下调用这个agent；
- tools：这个agent能调用的工具，可以设置多个工具；
- model：agent使用的模型；
- system：系统提示词，该agent的角色定位、规则限制、输出风格、工作流程等；

# 产品逻辑
subagent的产品逻辑是将自己处理的结果返回给claude code，claude code会将各个子agent返回的这些结果统一处理后将最终内容输出给你，所以要注意subagent的输出对象不是你，而是claud code，claude code的输出对象才是你。

# 典型场景
你: 这个支付模块需要全面审查  

并行创建5个Task:  
1、架构分析SubAgent → 模块设计和接口审查  
2、安全审计SubAgent → SQL注入、XSS、CSRF检查  
3、性能分析SubAgent → 慢查询和瓶颈定位  
4、代码质量SubAgent → 测试覆盖和规范检查  
5、数据库SubAgent → 索引和查询优化建议  
  
- 30分钟返回5份报告(串行需2.5小时)  
- 成本:5倍token,节省80%时间,ROI极高
- 成本模型: 这是一个 时间换成本 的策略, 而非成本优化。线性累加(5个=5倍),但节省时间通常50-80%。

### 适用与不适用场景
1、 (★★★★★) 极度推荐: 多角度代码审查、项目规划、文档生成 (任务完全独立)。
2、 (★★★★☆) 推荐: 文件批处理、API集成测试 (任务独立)。
3、 (★★☆☆☆) 不推荐: 迭代式功能调试 (因其无状态特性)。
4、 (★☆☆☆☆) 禁止: 任务间有依赖、敏感数据处理、单一复杂任务 (不需要并行)。

# 存储位置
https://github.com/VoltAgent/awesome-claude-code-subagents?tab=readme-ov-file#subagent-storage-locations

| Type              | Path                | Availability         | Precedence |
| ----------------- | ------------------- | -------------------- | ---------- |
| Project Subagents | `.claude/agents/`   | Current project only | Higher     |
| Global Subagents  | `~/.claude/agents/` | All projects         | Lower      |

Note: When naming conflicts occur, project-specific subagents override global ones.

# 新建subagent
https://github.com/VoltAgent/awesome-claude-code-subagents?tab=readme-ov-file#setting-up-in-claude-code
1. Place subagent files in `.claude/agents/` within your project
2. Claude Code automatically detects and loads the subagents
3. Invoke them naturally in conversation or let Claude decide when to use them

# Agent仓库
常见的subagent在github上也有很多人已经整理好了，更多可查看：  https://github.com/VoltAgent/awesome-claude-code-subagents ，里面有100多个agent ，可以进行按场景挑选使用，直接对照文档安装即可。