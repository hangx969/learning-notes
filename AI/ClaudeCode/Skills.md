Skill (技能) 是自动触发的能力包,2025年10月发布。
https://code.claude.com/docs/zh-CN/skills

和MCP有啥区别：Skills的范围更大，Skills可以调用mcp。Skills还可以包含python脚本，功能更灵活丰富。

单个Skill是能力,多个Skill编排是流程,Skill+MCP+SubAgent是智能体

简单说，**Skills 就是给 Claude 安装的"专业技能包"**。
**技术上**，一个 Skill 就是一个文件夹，里面包含技能的描述、相关脚本、示例代码等等。

比如你搞了一个 Skill.md 文件，里面放了 AI 生成 PPT 固定流程的指令。你给 Claude 说：帮我生成 PPT，这个 Skill 就能激活。你就不需要每次都把你的要求写出来。

# 解决痛点
你是不是经常遇到这种情况：
每次让 Claude 生成 Git commit message，都要像念咒语一样重复：
- "用现在时"
- "50 字以内"
- "说 what 和 why，不说 how"
- "要包含影响的组件"

或者让 Claude 帮你写 API 文档，每次都要解释：
- "用 Markdown 格式"
- "包含请求示例和响应示例"
- "标注必填参数"

痛点 1：重复劳动
**之前**：每次都像教小孩一样解释规则  
**现在**：打包成 Skill，说一句话自动应用

痛点 2：团队协作混乱
**场景**：10 个人用 10 种方式让 Claude 生成文档，格式五花八门。
**解决**：
1. 把 Skill 提交到项目代码库：`.claude/skills/company-doc-generator/`
2. 团队成员 `git pull` 后自动同步
3. 全员统一规范 

痛点 3：知识无法沉淀
**之前**：老员工调试 API 的技巧藏在脑子里  
**现在**：写成 Skill，新人克隆代码立刻获得团队智慧

### Skills的核心设计：渐进式披露机制

这个设计是Skills高效的核心：

- **初始加载**：Claude只需记住每个Skill的元数据，包括：名称+描述，大概占几十个Token
- **按需触发**：当你的请求匹配某个Skill的描述时，Claude才会加载完整的指令和脚本
- **分模块读取**：复杂Skill可拆分多个文件，Claude只会读取当前任务所需的部分

按照这种设计让你可以安装或者设计上百个Skills，却不会占用大量上下文或影响交互的性能。

# 组成结构
一个Skill文件夹通常包含这几部分：

- SKILL.md ：核心文件。用YAML写元数据（名字、描述），用Markdown写详细的指令，告诉Claude在什么情况下、以及如何使用这个Skill。
- scripts/ ：存放可执行的 Python、Shell脚本。
- references/ ：存放 参考文档（如API文档、数据库Schema、公司政策等），作为给Claude看的知识库。
- assets/ ：存放 资源文件（如PPT模板、Logo、项目脚架等），供Claude在执行任务时直接使用。

# 手动安装
skills存放位置：
- 个人 Skills (`~/.claude/skills/`)
- 项目 Skills (`.claude/skills/`)
创建方法：
- 创建一个子目录和skill同名即可
- 在子目录中创建SKILL.md，其中是skill的prompt。

# market安装
```sh
/plugin marketplace add anthropics/skills
/plugin
```

1. Select **Browse and install plugins**
2. Select **anthropic-agent-skills**
3. Select **document-skills or example-skills**
4. Select **Install now**

# 打包Skill
claude可以打包skill变成一个xxx.skill文件，可以分享给其他人安装。

打包方法：skill-creator中提供了python脚本一键打包：
  python3 /Users/hang.xu/.claude/skills/skill-creator/scripts/package_skill.py \
    /Users/hang.xu/.claude/skills/gitops-code-review \
    /Users/hang.xu/.claude/skills

安装方法：
在Claude Code中：Install skill from /path/to/gitops-code-review.skill

# 各种skill仓库
**官方skills git 仓库：** https://github.com/anthropics/skills.git

**开源skills仓库：**
该项目收集了各种实用 Skill，采用模块化设计。比如文档处理、开发、数据分析、营销、写作创意啥的都有： https://github.com/ComposioHQ/awesome-claude-skills ， https://github.com/BehiSecc/awesome-claude-skills

传统的 Claude Code Skill 需要你手动记忆和调用，而这个项目通过创新的钩子机制，实现了 Skill 的智能自动触发。当你输入提示或操作文件时，系统会自动分析上下文，并建议最相关的技能： https://github.com/diet103/claude-code-infrastructure-showcase

开发者 @obra 觉得现在的 AI 写代码太随意了，所以他写了一组 Skills，**强迫** Claude 按照**世界级高级工程师**的标准流程来工作： https://github.com/obra/superpowers
装了之后，Claude 的模式就是：**收到需求 -> 先头脑风暴 -> 制定详细计划 -> 写测试用例（TDD） -> 写代码通过测试 -> 检查质量**。

# 使用
## 第一层: 工程化单点突破 (把说明书变技能包)
把最烦人的重复劳动自动化。少写废话提示词,让Claude自动识别场景。

### 简单测试：Pre-commit Review

在.claude/skills/目录下创建pre-commit-check/SKILL.md:

```markdown
# 名称  
pre-commit-check  
  
# 描述  
代码提交前的标准检查:格式化、Lint、测试  
  
# 触发  
当用户提到"提交""commit""推送"时自动触发  
  
# 执行逻辑  
1、运行代码格式化  
2、运行Lint检查  
3、运行相关测试  
4、生成检查报告  
  
# 输出  
分级报告:阻断问题、警告问题、通过项
```

### 案例1: 智能代码审查
smart-code-review:

效果: 以前代码审查靠人工挑毛病,经常遗漏关键问题。现在说"review这个PR",自动按文件类型做专项检查,该找的坑一个不漏。团队线上事故率下降60%。

```markdown
# 名称
smart-code-review

# 触发
当用户提到"review""审查""检查代码"或准备提交PR时

# 执行逻辑
1、分析变更文件类型和影响范围
2、根据文件类型选择检查项:
- API文件 → 检查鉴权、参数校验、错误处理、API文档
- 数据库迁移 → 检查索引、向后兼容、回滚脚本、性能影响
- 前端组件 → 检查无障碍、性能、状态管理、错误边界
- 配置文件 → 检查敏感信息泄露、环境变量、默认值安全性
3、调用对应SubAgent进行专项审查:
- security-auditor → SQL注入、XSS、CSRF等
- performance-engineer → N+1查询、大对象、内存泄漏
- frontend-developer → 重渲染、bundle大小、懒加载
4、汇总问题并按严重程度分级:
- 阻断级(安全漏洞、数据丢失风险)
- 警告级(性能隐患、可维护性问题)
- 建议级(优化空间、最佳实践)

# 输出
分级报告 + 修复建议 + 参考文档链接
```

### 案例2: 依赖升级风险评估
dependency-upgrade-check:

效果: 以前升级依赖全靠运气,升了才知道炸不炸。现在每次升级前先跑一遍评估,该注意的点全列出来,升级有底气。

~~~markdown
# 触发
检测到package.json/requirements.txt/go.mod等变更时

# 执行逻辑
1、识别新增、升级、删除的依赖
2、对每个变更依赖:
- 用github MCP查该库的changelog和breaking changes
- 用context7查新版本的API变化
- 扫描项目代码,找出使用该依赖的位置
- 评估影响面(多少文件、是否核心路径)
3、检查依赖树冲突(peerDependencies、版本兼容性)
4、查询CVE数据库,检查已知漏洞
5、生成升级checklist

# 输出
## 升级风险评估
- 高风险依赖(breaking changes多、使用面广)
- 中风险依赖(小改动、局部影响)
- 低风险依赖(bugfix、无API变化)

## 需要人工验证的点
[列出可能出问题的代码位置]

## 建议升级顺序
[从低风险到高风险,逐步验证]

## 回滚预案
[如果升级出问题,怎么快速回退]
~~~

## 第二层: 编排型工作流 (参数化+链式调用)

一个技能适配多项目,多个技能串成流水线。

### 案例: 生产事故应急响应
incident-response:

效果: 以前线上出问题,团队一片慌乱,排查靠经验靠猜。现在说"线上订单服务挂了",5分钟内给出完整分析+3套止损方案。平均故障恢复时间从45分钟降到12分钟。

~~~markdown
# 触发
用户说"线上出问题了""紧急""事故"等关键词

# 执行流程(自动并行+串行)
## 阶段1:快速止血(并行执行)
- 调用devops-troubleshooter → 分析日志、定位异常
- 调用performance-engineer → 检查资源使用、是否过载
- 调用database-optimizer → 检查慢查询、锁等待

## 阶段2:根因分析(基于阶段1结果)
- 如果是代码问题 → 调用debugger SubAgent
- 如果是配置问题 → 检查最近的配置变更
- 如果是依赖问题 → 检查上游服务状态
- 如果是资源问题 → 检查流量异常、是否被攻击

## 阶段3:止损方案(基于根因)
- 自动生成3个止损方案:
  1、 最快方案(回滚、降级、限流)
  2、 最稳方案(修复根因,重新发布)
  3、 临时方案(绕过问题点,保持可用)
- 对比每个方案的:恢复时间、风险、副作用

## 阶段4:执行确认
- 输出完整的执行命令和回滚命令
- 标注每步的预期结果和验证方式
- 等待人工确认后才执行

# 输出
## 事故摘要
影响范围、严重程度、开始时间、核心指标变化(错误率、延迟、可用性)

## 根因分析
详细分析,附日志/监控截图链接

## 止损方案对比
3个方案的完整对比表

## 执行清单
一步步操作指令,可复制执行

## 事后改进
如何预防类似问题再次发生
~~~

## 第三层: 团队智能体 (知识沉淀+自进化)
案例: 技术债追踪助手

效果: 不再是"想起来就还",而是每周有明确的3个小目标。结合SonarQube等专业工具，Skill负责排优先级和生成报告。

tech-debt-tracker:

```markdown
# 名称  
tech-debt-tracker  
  
# 描述  
每周帮助团队识别和追踪最重要的技术债  
  
# 触发  
用户提到"技术债""代码坏味道""重构计划"时  
  
# 执行逻辑  
1、集成SonarQube API,获取现有扫描结果  
2、按影响面排序(修改频率高 + bug数多 = 优先级高)  
3、生成本周TOP 3待还技术债清单  
4、每项包含:位置、问题描述、建议方案、预估工作量  
  
# 输出  
Markdown周报:  
- TOP 3技术债(本周建议优先处理)  
- 已还技术债(上周完成的3项)  
- 决策记录(为什么选这些,存入memory)
```

## 高级: 版本治理+回滚
目标: 把Skills当团队资产,能升级、能回退、可审计。
案例: 技能版本化
落地做法:
1. 小范围灰度两版,对比"查出率、耗时、误报率"。
2. 确定没问题再全量,有问题立即回滚。
3. 预期效果: 两周内误报率从18%压到6%。
   
```markdown
team-skills/  
  code-review/  
    v1.0.0/Skill.md  
    v1.1.0/Skill.md  
    v2.0.0/Skill.md  # 当前版本
```

# 用Skill创建Skill

Antrophic官方有一个帮助创建Skill的Skill： https://github.com/anthropics/skills/tree/main/skills/skill-creator

告诉claude code基于当前的Skill草稿，调用skill-creator来创建一个完成的skill，名称为xxx。

# Obsidian Skill
https://github.com/kepano/obsidian-skills

obsidian-skills直接把Obsidian专家集成在 Claude Code 里，仓库包含三个核心技能Skill:
- **obsidian-markdown** Obsidian 风格的 Markdown计写，各种专有格式都支持。
- **obsidian-bases**  .base 类数据库视图支持过滤、公式、汇总。
- **json-canvas**  .canvas无限画布文件格式可以实现点、连线、分组。

## 安装
```
/plugin marketplace add kepano/obsidian-skills
/plugin install obsidian@obsidian-skills
```