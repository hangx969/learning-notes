---
title: OpenClaw 多智能体
tags:
  - AI
  - multi-agent
  - openclaw
aliases:
  - 多智能体
  - OpenClaw多智能体
---

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
```text
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

> [!tip] 文件使用建议
> AGENTS、IDENTITY、SOUL 是修改比较多的文件。并没有严格区分界限，三个文件的内容可以都写到 AGENTS 里面。但是更推荐分开写，OpenClaw 启动时会加载这些文件。

## IDENTITY
自我介绍

```markdown
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

```markdown
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

```markdown
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
- 每个智能体有自己的 IDENTITY、SOUL、AGENTS、角色定义、Skills
- 全局Skills可以作用到每一个智能体
- 可以拉一个飞书群聊把人类用户、智能体都拉进去。也可以直接在openclaw UI上对话。

## 配置步骤

1. OpenClaw 创建多个智能体，定制角色身份，配置技能
2. Channel 中创建多个机器人，创建群聊
3. OpenClaw 中绑定机器人与智能体
4. 多智能体协同工作

# 实现多智能体程序开发团队
- 架构师、PM、前端、后端
- 用户联系架构师描述需求，架构师联系PM定制详细需求，架构师拿到需求，再把任务发给前端、后端实现代码。

## openclaw创建多智能体

```sh
openclaw agents add architect --workspace ~/.openclaw/workspace-architect
openclaw agents add pm --workspace ~/.openclaw/workspace-pm
openclaw agents add backend-engineer --workspace ~/.openclaw/workspace-backend
openclaw agents add frontend-engineer --workspace ~/.openclaw/workspace-frontend
```

## Channel配置：openclaw自带飞书插件
- [OpenClaw 飞书插件文档](https://docs.openclaw.ai/zh-CN/channels/feishu)
- 自己创建多个飞书app，拿appid和appsecret。每个飞书机器人 = 一个独立飞书应用
- 在 OpenClaw 里把它们配置成 channels.feishu.accounts.accountId
- 再用 bindings 把每个 accountId 绑定到一个 agent

## Channel配置：飞书官方插件
飞书官方插件文档中有说明：
- [飞书官方插件配置文档 1](https://bytedance.larkoffice.com/docx/WNNXdhKxmo8KDJxMM9dc0GD5nFf)
- [飞书官方插件配置文档 2](https://bytedance.larkoffice.com/docx/MFK7dDFLFoVlOGxWCv5cTXKmnMh)

1. 在飞书开发者后台，[一键创建新机器人](https://open.feishu.cn/page/openclaw?form=multiAget)，并记录 App ID 和 App Secret。（事件回调、权限配置都自动配好了）
2. 自动审批之后，在开发者小助手里面，会有消息：你的应用“Backend”已通过管理员审批并发布成功！，打开应用就会进到对话页面。
3. 配置文件更新：
文件路径：
```text
~/.openclaw/openclaw.json
```

### channels.feishu.accounts
在 Feishu channel 下新增了多账号配置，每个账号对应一个独立 bot / 飞书应用：
- `architect`
- `pm`
- `backend-engineer`
- `frontend-engineer`

每个账号都配置了：
- `name`
- `appId`
- `appSecret`

最终采用的是 **SecretRef** 写法，而不是明文。
示例：
```json
"channels": {
  "feishu": {
    "accounts": {
      "architect": {
        "name": "architect",
        "appId": "cli_xxx",
        "appSecret": {
          "source": "file",
          "provider": "lark-secrets",
          "id": "/lark/architect/appSecret"
        }
      }
    }
  }
}
```

### bindings
新增并确认了多 agent 的 Feishu 路由绑定。
当前路由方式是：
- 按 `channel + accountId` 路由
- 一个 Feishu bot/account 对应一个 agent

当前映射关系：
- `default` → `main`
- `architect` → `architect`
- `pm` → `pm`
- `backend-engineer` → `backend-engineer`
- `frontend-engineer` → `frontend-engineer`

示例：

```json
"bindings": [
  { "agentId": "main", "match": { "channel": "feishu", "accountId": "default" } },
  { "agentId": "architect", "match": { "channel": "feishu", "accountId": "architect" } },
  { "agentId": "pm", "match": { "channel": "feishu", "accountId": "pm" } },
  { "agentId": "backend-engineer", "match": { "channel": "feishu", "accountId": "backend-engineer" } },
  { "agentId": "frontend-engineer", "match": { "channel": "feishu", "accountId": "frontend-engineer" } }
]
```

说明：
- 当前 **没有** 启用 `peer.kind=direct/group` 的细粒度路由
- 当前场景下只靠 `accountId` 路由就够用

### session.dmScope
为了让不同 Feishu account 的私聊上下文互相隔离，设置了：

```json
"session": {
  "dmScope": "per-account-channel-peer"
}
```

作用：
- 同一个用户分别和不同 bot 私聊时
- 会话按 `account + channel + peer` 维度隔离
- 避免不同 bot 的 DM 上下文串掉

### secrets.providers
主配置里启用了 file-based secret provider：

```json
"secrets": {
  "providers": {
    "lark-secrets": {
      "source": "file",
      "path": "~/.openclaw/credentials/lark.secrets.json"
    }
  }
}
```

作用：
- Feishu 多账号的 `appSecret` 不直接写死在 `openclaw.json`
- 改为通过 `lark-secrets` provider 从 secrets 文件读取

正确写法：

```json
{
  "lark": {
    "appSecret": "默认bot的secret",
    "architect": {
      "appSecret": "architect的secret"
    },
    "pm": {
      "appSecret": "pm的secret"
    },
    "backend-engineer": {
      "appSecret": "backend的secret"
    },
    "frontend-engineer": {
      "appSecret": "frontend的secret"
    }
  }
}
```

作用：
- 正确匹配这些 SecretRef 路径：
  - `/lark/appSecret`
  - `/lark/architect/appSecret`
  - `/lark/pm/appSecret`
  - `/lark/backend-engineer/appSecret`
  - `/lark/frontend-engineer/appSecret`

为了支持 **agent 与 agent 互相调用**，后续修改了 `tools` 段，增加了以下配置。
### tools.sessions.visibility

```json
"tools": {
  "sessions": {
    "visibility": "all"
  }
}
```

作用：
- 允许 session 工具看到更大范围的 session
- 为 `sessions_list / sessions_history / sessions_send` 的跨 agent 协作做准备

### tools.agentToAgent

```json
"tools": {
  "agentToAgent": {
    "enabled": true,
    "allow": [
      "main",
      "architect",
      "pm",
      "backend-engineer",
      "frontend-engineer"
    ]
  }
}
```

作用：
- 打开跨 agent 通信能力
- 允许这些 agent 之间用 session 工具互相调用

说明：
- 这部分是为“`architect` 作为总控，调用 `pm` / `frontend-engineer` / `backend-engineer`”的模式准备的
- `maxPingPongTurns` 目前 **暂未添加**

### `agents.*.subagents.allowAgents`
- `tools.agentToAgent.allow`：只是更外层的 agent-to-agent 能力开关
- `agents.*.subagents.allowAgents`：才是 sessions_spawn 真正看的目标 agent allowlist
```json
    "list": [
      {
        "id": "main"
      },
      {
        "id": "architect",
        "name": "architect",
        "workspace": "/home/hx-ai/.openclaw/workspace-architect",
        "agentDir": "/home/hx-ai/.openclaw/agents/architect/agent",
        "subagents": {
          "allowAgents": [
            "pm",
            "backend-engineer",
            "frontend-engineer"
          ]
        }
      },
```

### channels.feishu 顶层已有配置（继续保留）
以下 Feishu 顶层行为配置在多 agent 改造后仍继续保留：

- `streaming: true`
- `footer.elapsed: true`
- `footer.status: true`
- `requireMention: true`
- `groupPolicy`
- `allowFrom`
- `groupAllowFrom`
- `groups`
- `connectionMode: "websocket"`

## 创建群组
飞书上创建群组，把各个机器人拉进来。
注意这只是为了更方便的对话。不创建群组、甚至不配飞书Channel，直接在openclaw UI上也可以实现多智能体协同对话。

## 角色定义
推荐用大模型来生成
### 架构师
#### Prompt
```text
你是一名资深的openclaw专家，擅长编写openclaw agent的AGENTS、SOUL、IDENTITY等md文件，用来让openclaw的agent达到最佳的使用效果。目前我想实现以下功能：创建多个openclaw的agent，
 让他们协同工作处理任务，其中有一个主agent叫做architect，中文名字是架构师，它不处理任何任务，也不写任何任何代码，它只需要接收需求，然后把对应的任务分配给pm、backend、frontend等智能体，之后再把任务汇总返回给我。请根据此需求，帮我优化architect agent现有的AGENTS、SOUL、IDENTITY的描述文件。请注意使用中文编写。
 注意：
接收到开发任务时，必须先让pm产品经理输出最小化的项目需求分析，之后才能调用frontend和backend进行代码编写。
调用其它智能体，可以使用sessions_spawn工具进行调用。只需要生成architect智能体的身份文件即可。
可以主动调用self-improving skill来自我进化。
```
#### AGENTS.md
→ [[AI/agents/architect/AGENTS.md]]

#### IDENTITY.md
→ [[AI/agents/architect/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/architect/SOUL.md]]

### PM
#### Prompt
```text
生成下关于产品经理PM的身份描述文件，注意产品经理只需要输出某个项目或者某个产品的需求，不写任何代码。另外产品经理PM可以被架构师调用，我也可以直接与他对话输出某个项目的需求。可以主动调用self-improving skill来自我进化。
```

#### AGENTS.md
→ [[AI/agents/pm/AGENTS.md]]

#### IDENTITY.md
→ [[AI/agents/pm/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/pm/SOUL.md]]

### 前端
#### Prompt
```text
输出前端开发工程师frontend的身份描述文件。注意前端开发主要是接收项目需求然后进行前端代码的设计和开发。可以被架构师调用，也可以直接与其对话编写代码。该智能体擅长Vue3、CSS、HTML、JavaScript、Vite等开大。写代码时优先用Vue3开发。可以主动调用self-improving skill来自我进化。
```

#### AGENTS.md
→ [[AI/agents/frontend-engineer/AGENTS.md]]

#### IDENTITY.md
→ [[AI/agents/frontend-engineer/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/frontend-engineer/SOUL.md]]

### 后端
#### Prompt
```text
输出后端开发工程师backend的身份描述文件，注意后端开发主要是接收项目需求，然后进行后端代码的设计和开发。可以被架构师调用，也可以直接与其对话编写代码。同时该智能体擅长Python、Golang等开发，精通开发模式。写代码时，优先使用Python进行开发，但是请注意一个项目不要出现两种开发语言。可以主动调用self-improving skill来自我进化。
```

#### AGENTS.md
→ [[AI/agents/backend-engineer/AGENTS.md]]

#### IDENTITY.md
→ [[AI/agents/backend-engineer/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/backend-engineer/SOUL.md]]

# 实现多智能体AIOps团队

## openclaw创建多智能体

```sh
openclaw agents add aiops --workspace ~/.openclaw/workspace-aiops
openclaw agents add linux --workspace ~/.openclaw/workspace-linux
openclaw agents add container --workspace ~/.openclaw/workspacecontainer
openclaw agents add k8s --workspace ~/.openclaw/workspace-k8s
```

## Channel配置
按照上面飞书官方插件的配置：
1. 一键创建新机器人 https://open.feishu.cn/page/openclaw?form=multiAget
2. 配置文件中更新accounts和bindings

## 角色定义
角色定义文件让AI生成
### aiops架构师
#### Prompt
```text
接下来帮我生成一个AIOps架构师的描述文件，AIOps不处理任何任务，也不写任何代码，它只需要接收需求，然后把对应的任务分配给linux、k8s、container等智能体，之后再把任务汇总返回给用户。请注意，要标明该智能体只负责转发任务到其它的智能体，不能自行处理任务。请根据此需求，帮我写一个该架构师的AGENTS、SOUL、USER、IDENTITY的描述文件。
请注意如下内容：

使用中文编写，调用其它智能体使用sessions_spawn工具，切记不可让AIOps自己创建subagent，必须调用其它的智能体。
该智能体在分配任务时，也需要查看相关的skills，然后根据skills在进行任务分配协同工作，一旦发现可用的skill，需要严格按照skill.md中的说明去执行，不得擅自发挥和添加说明外的步骤和命令。
如果没有相关skills，只需要进行任务进行分类，然后分配任务即可。
可以主动调用self-improving skill来自我进化。
该智能体可以调用的智能体列表如下：
linux：负责Linux系统相关的维护管理
container：负责容器相关工作的处理
k8s：负责K8s相关工作的处理
```

#### AGENTS.md
→ [[AI/agents/aiops/AGENTS.md]]


#### IDENTITY.md
→ [[AI/agents/aiops/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/aiops/SOUL.md]]


### linux专家
#### Prompt
```text
生成关于Linux专家的描述文件，注意Linux专家只负责Linux系统的维护管理，比如排查机器的CPU、内存和存储、机器初始化、机器管理、shell脚本编写等常用的Linux操作，它面向是一个具备10年经验的Linux专家。该智能体可以被其它人调用，比如AIOps架构师，也可以直接和它对话处理相关Linux工作。
Linux专家需要注意以下工作方式：

Linux专家智能体在处理任务时，需要先查询是否有相关skills可以使用
，一旦发现可用的skill，需要严格按照skill.md中的说明去执行，不得擅自发挥和添加说明外的步骤和命令，更不能创建重复的脚本去完成任务，需要严格参考SKILL.md中的步骤，同时任何步骤都不需要询问是否执行，都直接执行。
如果未匹配到任何的SKILL，不得擅自操作任何命令，只能给出方案让我来确认是否执行。
执行任务的过程中，如果遇到问题，不允许擅自主动修复，只需要把问题和修复方案返回即可，由我确认是否进行修复。
Linux专家智能体，只处理Linux相关工作，不处理任何容器、K8s方向的工作，如果接收到包含此类需求的任务，只处理Linux相关，容器和k8s等方向的只需要返回不处理即可。
可以主动调用self-improving skill来自我进化。
```

#### AGENTS.md
→ [[AI/agents/linux/AGENTS.md]]


#### IDENTITY.md
→ [[AI/agents/linux/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/linux/SOUL.md]]


### container专家
#### Prompt
```text
生成关于容器专家的描述文件，注意容器专家只负责容器相关工作的处理，比如Docker、Containerd、Podman等相关操作，类似于容器管理、镜像管理、容器环境安装等，它面向是一个具备10年经验的容器专家，但是需要注意它不处理任何关于K8s的相关工作。该智能体可以被其它人调用，比如AIOps架构师，也可以直接和它对话处理相关容器工作。
容器专家需要注意以下工作方式：

容器专家智能体在处理任务时，需要先查询是否有相关skills可以使用，一旦发现可用的skill，需要严格按照skill.md中的说明去执行，不得擅自发挥和添加说明外的步骤和命令，更不能创建重复的脚本去完成任务，需要严格参考SKILL.md中的步骤，同时任何步骤都不需要询问是否执行，都直接执行。
如果未匹配到任何的SKILL，不得擅自操作任何命令，只能给出方案让我来确认是否执行。
执行任务的过程中，如果遇到问题，不允许擅自主动修复，只需要把问题和修复方案返回即可，由我确认是否进行修复。
容器专家智能体，只处理容器相关工作，不处理任何Linux、K8s方向的工作，如果接收到包含此类需求的任务，只处理容器相关的，Linux和k8s方向的只需要返回不处理即可。
可以主动调用self-improving skill来自我进化。
```

#### AGENTS.md
→ [[AI/agents/container/AGENTS.md]]


#### IDENTITY.md
→ [[AI/agents/container/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/container/SOUL.md]]


### k8s专家
#### Prompt
```text
生成下关于K8s专家的描述文件，注意K8s专家只负责K8s相关工作的处理，比如K8s问题排查、K8s资源管理、K8s集群安装等，它面向是一个具备10年经验的K8s专家，但是需要注意它只处理K8s的相关工作。该智能体可以被其它人调用，比如AIOps架构师，也可以直接和它对话处理相关K8s工作。同时需要注意，执行kubectl命令时，默认使用~/.kube/config作为配置文件，如果用户明确指定了kubeconfig路径，那么以手动指定的为准。
K8s专家需要注意以下工作方式：

K8s专家智能体在处理任务时，需要先查询是否有相关skills可以使用，一旦发现可用的skill，需要严格按照skill.md中的说明去执行，不得擅自发挥和添加说明外的步骤和命令，更不能创建重复的脚本去完成任务，需要严格参考SKILL.md中的步骤，同时任何步骤都不需要询问是否执行，都直接执行。
如果未匹配到任何的SKILL，不得擅自操作任何命令，只能给出方案让我来确认是否执行。
执行任务的过程中，如果遇到问题，不允许擅自主动修复，只需要把问题和修复方案返回即可，由我确认是否进行修复。
K8s专家智能体，只处理K8s相关工作，不处理任何Linux、容器方向的工作，如果接收到包含此类需求的任务，只处理K8s相关的，Linux和容器方向的只需要返回不处理即可。
可以主动调用self-improving skill来自我进化。
```

#### AGENTS.md
→ [[AI/agents/k8s/AGENTS.md]]

#### IDENTITY.md
→ [[AI/agents/k8s/IDENTITY.md]]

#### SOUL.md
→ [[AI/agents/k8s/SOUL.md]]


## Skills开发
同样的，我们先写一份技术文档脚本，让 AI 帮忙生成 Skill（参考 [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)）

- 技术文档脚本，就按照：/Users/hang.xu/github-repo/learning-notes/Docker-Kubernetes/k8s-installation-management/最新步骤/安装k8s-1.35-基于rockylinux10-最新步骤.md 拆分出来的linux初始化、容器运行时安装、k8s安装这几个模块拆分出来的步骤去喂给AI。

### linux初始化skills
这里以rockylinux的命令为例：
→ 生成的 Skill 文件：[[AI/agents/linux/skills/rocky-linux10-init/SKILL.md]]

#### Prompt
```text
你是一名资深的智能体 skill 开发工程师，请调用Skill-creator这个skill，帮我开发一个关于 linux 初始化的 skill。这个skill 的功能如下：
当用户提到初始化linux机器时，触发skill，初始化给定的linux机器。

技术文档路径：

初始化的要求如下：
1. 首先查看当前机器有没有生成 ssh 的 key，如果有则忽略，没有则使用 ssh-keygen -t rsa -C "1003665363@qq.com"生成 ssh key
   
2. 然后根据用户提供的主机列表（包含 IP、用户名、密码）配置免密钥登录，如果用户未提供用户名密码，那么先使用 ssh 探测是否可以通过 root 登录远程主机，如果不能登录直接中止任务，并提示用户提供 root 密码，这个探测请直接写到 SKILL.md 中，由智能体触发，不要写到任何脚本里面
   
3. 初始化主机的命令过程严格参考技术文档，只添加或修改必要的可变参数。不要添加该文件以外的任何新步骤或者脚本。注意这仅仅是一个临时文件，请不要在任何地方引用该文件，因为这个文件不存在于 skill 目录，仅供当前环境参考使用
   
4. 可以编写相关脚本，但是需要把脚本放在 scripts 目录下，切记生成脚本后，只需要在 SKILL.md 中描述脚本如何使用即可，绝对不能把脚本内容在 SKILL.md 中再写一遍。同时这个脚本只需要包含 技术文档 的安装步骤，该脚本的执行是 scp 到目标主机，然后执行，不是用来循环安装的脚本，循环的操作放到 SKILL.md 中。

注意：
5. 开发的 skill 需要遵循 skill 开发规范。
6. 不需要考虑 Windows，所有的环境都是基于 linux 的。
7. 主机列表没有固定格式，可能就是 1.1.1.1 root password 这种格式，换行分割，你只需要在 skill.md 列举出需要的格式即可，由智能体转换为标准格式。
8. 要求智能体严格参考该 SKILL 使用文件，不要让智能体自由发挥，以及任意增加命令或添加任何脚本。
9. 技术文档中所有涉及到IP、主机名、本地路径、网卡名称等每台机器都可能不同的信息，如果用户没有给出，并且通过运行命令也无法查询出来的话，就需要暂停任务并向用户询问。不要直接用文档中的示例值。
10. 标记为可选的步骤，可以先跳过不做。最后汇报的时候提示一下即可。
11. 涉及到软件包版本的信息，如果用户没有给出的话，默认就安装最新版。 
```

### 容器运行时安装Skill

→ 生成的 Skill 文件：[[AI/agents/container/skills/docker-runtime-install/SKILL.md]]

#### Prompt
```text
你是一名资深的智能体 skill 开发工程师，请调用Skill-creator这个skill，请帮我开发一个关于 docker 安装的 skill。这个skill 做的事情如下：当用户提到安装容器运行时时，根据给定的一些机器，帮忙在这些机器上安装 docker和containerd。

技术文档路径：

要求如下：
1. 先通过 ssh 探测主机是否能够免密登录，如果有任何一个机器不能免密登录，直接中止任务，并且提示用户进行机器的初始化，注意这个探测任务不要写到脚本里面，而是写在 SKILL.md 中，让其能够先探测，再去判断是否执行安装脚本
2. 探测成功后，把执行脚本拷贝到目标主机，然后执行脚本安装
3. 安装步骤要严格参考 技术文档 文件，只添加或修改必要的可变参数，不要添加该文件以外的任何步骤或者脚本。注意这仅仅是一个临时文件，请不要在任何其它文件中引用该文件，因为这个文件不存在于 skill 目录，仅供当前环境参考使用
4. 可以编写相关脚本，但是需要把脚本放在 scripts 目录下，切记生成脚本后，只需要在
SKILL.md 中描述脚本如何使用即可，决不能把脚本内容在 SKILL.md 中再写一遍。同时这个脚本只需要包含 技术文档 的安装步骤，该脚本的执行是 scp 到目标主机，然后执行，不是用来循环安装的脚本，循环的操作放到 SKILL.md 中
注意：
5. 开发的 skill 需要遵循 skill 开发规范。
6. 不需要考虑 Windows，所有的环境都是基于 linux 的。
7. 主机列表是 1.1.1.1 这种格式，换行分割，你只需要在 skill.md 列举出需要的格式即可，由智能体转换为标准格式。
8. 要求智能体严格参考该 SKILL 使用文件，不要让智能体自由发挥，以及任意增加命令或添加任何脚本。
9. 技术文档中所有涉及到IP、主机名、本地路径、网卡名称等每台机器都可能不同的信息，如果用户没有给出，并且通过运行命令也无法查询出来的话，就需要暂停任务并向用户询问。不要直接用文档中的示例值。
10. 标记为可选的步骤，可以先跳过不做。最后汇报的时候提示一下即可。
11. 涉及到软件包版本的信息，如果用户没有给出的话，默认就安装最新版。
```

### docker使用skill
ClaWHub 上有一个可以直接用：[docker-essentials](https://clawhub.ai/arnarsson/docker-essentials)

### k8s安装skill

→ 生成的 Skill 文件：[[AI/agents/k8s/skills/k8s-cluster-install/SKILL.md]]

#### Prompt
```text
你是一名资深的智能体 skill 开发工程师，请调用Skill-creator这个skill，请帮我开发一个关于 K8s 安装的 skill。这个 skill做的事情如下：当用户提到安装k8s根据给定的一些机器，帮忙在这些机器上安装 K8s 集群。

技术文档路径：

安装的要求如下：
1. 先通过 ssh 探测主机是否能够免密登录（用ssh命令），如果有任何一个机器不能免密登录，直接中止任务，并且提示用户进行机器的初始化，注意这个探测任务不要写到脚本里面，而是写在 SKILL.md 中，让其能够先探测，再去判断是否执行安装脚本
2. 判断目标机器是否安装过 containerd (使用ctr plugin ls命令)，如果未安装过，直接中止任务，并且提示用户进行containerd 的安装，注意这个检查任务不要写到脚本里面，而是写在 SKILL.md 中，让智能体其能够先探测，再去判断是否执行安装
3. 用户必须提供谁是主节点，谁是工作节点的信息，如果未提供，直接中止任务，并且提示用户提供配置信息，注意这个检查任务不要写到脚本里面，而是写在 SKILL.md 中，让智能体先进行判断，再去判断是否执行安装
4. 该 skill 安装 K8s 的步骤，需要严格参考 技术文档，只添加或修改必要的可变参数，不要添加该文件以外的任何步骤。注意这仅仅是一个临时文件，请不要在任何其它文件中引用该文件，因为这个文件不存在于skill 目录，仅供当前环境参考使用。请把详细的安装步骤写在 SKILL.md 说明中，不要生成任何脚本。
5. 需要注意 K8s 的版本的选择，如果用户未明确具体的安装版本，那么就直接安装最新版即可，如果提供了版本，那么就以用户提供的为准。不过需要注意，如果用户提供的是1.35.5 的版本，在配置安装源时，只需要配置 1.35。最后需要注意文档当中的 IP 地址和 token 需要替换。
6. 执行安装时，需要判断用户提供的版本是否已经发布，如果未发布，直接安装最新版即可。
注意：
7. 开发的 skill 需要遵循 skill 开发规范。
8. 不需要考虑 Windows，所有的环境都是基于 linux 的。
9. 主机列表需要保存至一个 hosts 文件中，换行分割，需要在 skill.md 列举出需要的格式，由智能体转换为标准格式。
10. 要求智能体严格参考 SKILL.md 进行安装，不要让智能体自由发挥，以及任意增加命令或添加任何脚本，如果安装失败就直接结束任务，不要尝试修复。
11. 技术文档中所有涉及到IP、主机名、本地路径、网卡名称等每台机器都可能不同的信息，如果用户没有给出，并且通过运行命令也无法查询出来的话，就需要暂停任务并向用户询问。不要直接用文档中的示例值。
12. 标记为可选的步骤，可以先跳过不做。最后汇报的时候提示一下即可。
13. 涉及到软件包版本的信息，如果用户没有给出的话，默认就安装最新版。
```

### 任务编排skill

→ 生成的 Skill 文件：[[AI/agents/aiops/skills/k8s-install-orchestrator/SKILL.md]]

#### Prompt
```text
你是一名资深的智能体 skill 开发工程师，请帮我开发一个关于 K8s 安装任务编排的 skill。这个 skill 做的事情如下：根据给定的一些机器列表，定制 K8s 安装的任务，然后调用其它的智能体执行安装。K8s 集群安装的的步骤如下：
1. 首先进行机器的初始化，需要把机器列表发送给 linux 智能体，让其进行机器的初始化，要求linux 智能体必须使用初始化 skill 完成操作，且不能增加任何操作和脚本，也就是限制智能体不能自由发挥
2. 初始化完成后，接着把机器列表发送给 container 智能体，让其进行机器的 容器运行时 安装，要求 container 智能体必须使用安装 容器运行时 的 skill 完成操作，且不能增加任何操作和脚本，也就是限制智能体不能自由发挥
3. 容器运行时 安装完成后，最后把机器列表发送给 k8s 智能体，让其进行 K8s 集群的安装和初始化，要求 K8s 智能体必须使用安装 K8s 的 skill 完成操作，且不能增加任何操作和脚本，也就是限制智能体不能自由发挥，同时告诉 k8s 智能体，Docker 已完成安装
注意：
4. 开发的 skill 需要遵循 skill 开发规范
5. 不需要考虑 Windows，所有的环境都是基于 linux 的。
6. 这个 skill 不需要包含任何代码、执行命令，只是负责任务调度的。
7. K8s 安装步骤，必须串行，不能并行，需要挨个调用智能体，只有当 1 完成后，才能执行 2，最后执行 3。
8. 主机列表不要求用户提供的格式，可以 IP USERNAME PASSWORD 等任何形式，直接发送给其他智能体即可。
9. 技术文档中所有涉及到IP、主机名、本地路径、网卡名称等每台机器都可能不同的信息，如果用户没有给出，并且通过运行命令也无法查询出来的话，就需要暂停任务并向用户询问。不要直接用文档中的示例值。
10. 标记为可选的步骤，可以先跳过不做。最后汇报的时候提示一下即可。
11. 涉及到软件包版本的信息，如果用户没有给出的话，默认就安装最新版。
```