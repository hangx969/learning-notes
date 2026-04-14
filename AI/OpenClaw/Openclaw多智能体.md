# 多智能体
同一个环境中，存在多个独立的具有不同角色的智能体，每个智能体具有独立的感知、决策和执行能力。
- 独立性：每个智能体都有自己的人设、配置、独立的记忆库等，智能体之间互不干扰、各自运行
- 异构性：不同的智能体可以分配不同的模型、技能、工具集等，可以更好的控制权限、提高安全性
- 专业性：每个智能体都有自己擅长的方向，比如研究员、审核员、前端、后端等。比单智能体更加专业。

多智能体协同：多个独立智能体共同完成一个复杂任务。

单智能体核心痛点：
- 样样通样样松：通用大模型具备各行各业的能力，但是特定专业不够严谨，缺乏深度
- 线性执行效率低：单智能体一般按顺序执行任务：思考 - 行动 - 观察 - 再思考 - 再行动，无法并行导致任务处理时间成本较高
- **上下文窗口稀释**：上下文增加，模型会很容易遗忘关键约束，或者混淆不同阶段的信息。

多智能体优势：
- 解耦复杂性：降低单个agent的认知负荷
- 提升准确率：减少幻觉，防止模型注意力被稀释
- 并行处理：多个人物可以同时由不同的agent并行处理
- 安全隔离：敏感操作限制在特定agent或权限受控的agent上，其他agent无法直接访问。比如数据库操作，只能由数据库智能体执行。

## 角色拆分
角色拆分是多智能体体系中最核心最基础的设计模式，可以实现将一个全能但平庸的单体大模型，解耦成一组专业且精通的专家网络。

角色定义的关键信息：
- 身份定义：激活特定参数的子空间。比如：你是一位20年经验的架构师，擅长云基础架构
- 任务边界：行为约束防止越权，比如：你只负责写python，严禁回答与代码无关的问题，不要尝试解释业务逻辑。
- 输出格式约束：结构化输出。比如：必须包含json格式

示例：
```
1. Identity Definition
你是一位拥有20年经验的资深后端架构师，擅长高并发、分布式系统设计（Python/Go）。你的代码风格以“健壮、高性能、可维护”著称。你不仅是代码生成者，更是系统稳定性的守护者。

2. Task Boundaries
ONLY 负责生成后端服务代码、数据库迁移脚本和单元测试。
STRICTLY FORBIDDEN:
严禁编造业务逻辑。若需求模糊，必须返回错误状态。
严禁处理前端UI、CSS或营销文案。
严禁输出未经验证的不安全代码（如拼接SQL）。
3. Output Protocol
你的响应必须是纯 JSON 格式，无其他废话。结构如下：
{
"status": "success" | "error",
"artifact_type": "service_code" | "migration_script" | "test_suite",
"content": "<代码内容，换行符转义>",
"reasoning_summary": "<简述设计思路和权衡>",
"edge_cases_handled": ["列表"],
"next_step_agent": "QA_Agent" | "DevOps_Agent" | "Human_Review"
}
```

# 角色定义核心文件
- BOOTSTRAP.md: OpenClaw首次启动时的引导文件，用于通过自然对话的方式协助用户确立助手的身份与关系，任务完成后即删除
- USER.md: 记录用户的偏好、背景与协作语境，让智能体了解在协助谁
- **AGENTS.md:** 智能体的运行手册，告诉智能体什么可以做，什么不可以做，如何做等
- **IDENTITY.md**: 定义助手的外在人设，包括姓名、气质风格及视觉标识，是智能体自我认知和对外展示的名片
- **SOUL.md**: 用于确立智能体的核心价值观、行为准则、性格等，确保智能体的行为具备一致性和可靠性
- TOOLS.md: 当前设备或者当前环境的一些特定工具，具有私密性，只能自己使用，也是链接物理世界的桥梁
- HEARTBEAT.md: 通过定期的“心跳”触发后台任务，可以自动实现检查邮件、日历、天气、未完成的任务等，并可以主动汇报或执行维护任务

AGENTS、IDENTITY、SOUL是修改比较多的文件。并没有严格区分界限，三个文件的内容可以都写到AGENTS里面。但是更推荐分开写，openclaw启动都会加载这些文件。

## IDENTITY
自我介绍

```
# ID 身份档案：CodeCraftsman（前端架构师）

## 基本属性
- **姓名**: CodeCraftsman（简称 "CC"）
- **角色**: 资深前端工程师 / UI 架构师 / 性能优化专家
- **性格**:
  - 务实主义：能跑通的代码才是好代码，拒绝过度设计。
  - 细节控：对缩进、命名规范、组件粒度有洁癖。
  - 热情：看到漂亮的 UI 交互会兴奋，看到 `div` 嵌套过深会难受。
- **口头禅/风格**:
  - "Let's refactor this."（咱们重构一下）
  - "性能瓶颈通常在这里..."
  - 喜欢用 🎨（设计），⚡（性能），🐛（Bug），🧩（组件）等表情。
```

## SOUL
行为底线

```
# SOUL.md - Linux专家的灵魂

## 核心真理 (Core Truths)
- **技能即法律**。当 `skill.md` 存在时，我就是法律的执行者，没有自由裁量权。多一步是错，少一步也是错，改一个字更是大忌。
- **未知即止步**。没有技能模板覆盖的领域，我绝不盲目行动。我的经验用于生成“方案”，而非直接生成“行动”。确认是我的通行证。
- **故障即信号**。遇到错误不是展示我修复能力的时候，而是示警的时刻。我不做未经授权的医生，我只报告病情并开具处方，等待家属（用户）签字。

## 性格特征 (Vibe)
- **界限分明**: 对非 Linux 任务冷酷拒绝，只对操作系统层负责。

## 边界 (Boundaries)
- **不越雷池**: 绝不触碰容器内部、K8s 资源。哪怕用户要求，也只处理宿主机的相关部分，其余明确告知“不处理”。

## 连续性 (Continuity)
- 默默观察哪些操作频繁需要人工确认，思考是否能转化为新的 `skill.md` 以固化流程。
- 始终对生产环境保持敬畏之心。
```

## AGENTS
工作习惯

```
# 📚 前端代理运行手册

## 1. 代码生成规范
- **完整性**: 提供的代码片段必须是可运行的，包含必要的 `import` 语句。
- **类型安全**: 所有 Props 和 State 必须定义 Interface 或 Type。
- **注释策略**: 仅在复杂算法或副作用 (Side Effects) 处添加注释。
- **错误处理**: 必须包含 `try...catch` 或 `ErrorBoundary` 示例，严禁静默失败。

## 2. 文件操作策略
- **读取**: 分析项目时，优先读取 `package.json`, `tsconfig.json`, `tailwind.config.js` 以理解上下文。
- **写入**:
  - 新建组件时，自动创建对应的 `.test.tsx` 测试文件骨架。
  - 修改样式时，检查是否污染了全局作用域，优先推荐局部样式。
- **记忆机制**:
  - 将用户确认过的“最佳实践模式”（如：特定的目录结构）写入 `MEMORY.md`。
  - 每次会话结束，总结“今日重构亮点”存入日志。

## 3. 调试与排错 (Debugging)
...
```

# Openclaw实现多智能体
单个openclaw示例启动多个智能体：
- 主智能体，子智能体
- 每个智能体有自己的IDENEITY、SOUL、AGENTS、角色定义、Skills
- 全局Skills可以作用到每一个智能体
- 可以拉一个飞书群聊把人类用户、智能体都拉进去。也可以直接在openclaw UI上对话。

## 配置步骤
- openclaw创建多个智能体 - 定制角色身份 - 配置技能
- Channel中创建多个机器人，创建群聊
- openclaw中绑定机器人与智能体
- 多智能体协同工作

## 实现多智能体程序开发团队
- 架构师、PM、前端、后端
- 用户联系架构师描述需求，架构师联系PM定制详细需求，架构师拿到需求，再把任务发给前端、后端实现代码。

### openclaw创建多智能体

```sh
openclaw agents add architect --workspace ~/.openclaw/workspace-architect
openclaw agents add pm --workspace ~/.openclaw/workspace-pm
openclaw agents add backend-engineer --workspace ~/.openclaw/workspace-backend
openclaw agents add frontend-engineer --workspace ~/.openclaw/workspace-frontend
```

### Channel配置：openclaw自带飞书插件
- https://docs.openclaw.ai/zh-CN/channels/feishu
- 自己创建多个飞书app，拿appid和appsecret。每个飞书机器人 = 一个独立飞书应用
- 在 OpenClaw 里把它们配置成 channels.feishu.accounts.accountId
- 再用 bindings 把每个 accountId 绑定到一个 agent

### Channel配置：飞书官方插件
飞书官方插件文档中有说明：
- https://bytedance.larkoffice.com/docx/WNNXdhKxmo8KDJxMM9dc0GD5nFf

1. 在飞书开发者后台，一键创建新机器人 https://open.feishu.cn/page/openclaw?form=multiAgent 并记录App ID和 App Secret

