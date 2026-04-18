---
title: "牛逼干货分享！OpenClaw Workspace 运维实战手册"
source: "https://mp.weixin.qq.com/s/4tVt4g6BlRv_Xe7RUIOzGQ"
author:
  - "[[点击关注👉]]"
published:
created: 2026-04-18
description:
tags:
  - "clippings"
---


## 前言

本文档从运维工程师视角出发，系统阐述 OpenClaw Workspace 的生产环境部署、配置管理、故障诊断、安全加固和自动化运维实践。

所有内容基于 OpenClaw 官方文档和实际生产经验，面向具备基础操作能力的运维人员。

本文与《 [OpenClaw 进阶配置与自动化运维实战手册](https://mp.weixin.qq.com/s?__biz=MzI0MDQ4MTM5NQ==&mid=2247576578&idx=1&sn=48af5baf7b4c9ef5d85e8aa2cc4b3d5e&scene=21#wechat_redirect) 》形成互补：前者侧重 Gateway、渠道和 Cron 等系统级配置，后者聚焦 Workspace 这一 Agent 运行环境的规划与运维。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

## 第一章：Workspace 概念再定义——运维视角

#### 配置文件体系与内容文件体系的分离

OpenClaw 的 Workspace 本质上是将 Agent 的运行环境拆分为两个正交体系：

**配置文件体系** （静态定义）

- `openclaw.json` ： `~/.openclaw/openclaw.json` ，系统宪法，定义 Gateway 行为和 Agent 运行时参数
- `AGENTS.md` ：工作手册，定义任务执行流程、安全边界、输出规范
- `SOUL.md` ：性格配置，定义 Agent 响应风格和交互模式
- `IDENTITY.md` ：身份元数据，定义名称、头像、视觉标识
- `TOOLS.md` ：工具权限，定义允许使用的工具及其使用策略

**内容文件体系** （动态数据）

- `USER.md` ：用户档案，包含用户偏好、历史交互摘要
- `memory/` ：长期记忆目录，包含结构化日志、项目状态、教训记录
- Session 历史：每次对话的上下文记录

理解这一分离架构是 Workspace 运维的基础。配置文件决定 Agent 能做什么、怎么做；内容文件决定 Agent 知道什么、记得什么。

#### Workspace 在生产环境中的角色

在生产部署场景下，Workspace 承担以下核心职责：

**环境隔离** ：每个 Agent 实例拥有独立的 Workspace，避免配置和记忆污染。生产环境建议为不同用途的 Agent（主助手、专项任务、自动化任务）分配独立 Workspace。

**状态持久化** ：通过 memoryFlush 机制，Agent 的重要记忆会持久化到文件系统。Workspace 的备份策略直接影响 Agent 的长期记忆完整性。

**配置载体** ：Workspace 内的配置文件定义了 Agent 的行为规范。修改 Workspace 配置比修改全局 `openclaw.json` 更轻量，适合快速切换 Agent 行为模式。

**审计追踪** ：Workspace 的变更历史可以纳入 Git 版本控制，实现配置的可审计和可回滚。

#### Workspace 路径与加载机制

**默认 Workspace 位置** ： `~/.openclaw/workspace`

**路径优先级** ：

1.Agent 配置中显式指定的 `workspace` 路径（最高优先级）

2.`agents.defaults.workspace` 配置项

3.`~/.openclaw/workspace` （默认）

**验证 Workspace 路径** ：

```
# 查看当前 Agent 的 Workspace 路径 
openclaw config get agents.defaults.workspace      

# 启动时指定 Workspace   
openclaw gateway start --workspace /path/to/custom/workspace
```

**目录存在性要求** ：

Gateway 启动时，如果指定的 Workspace 目录不存在，会自动创建。因此首次启动时会看到 memory/、logs/ 等子目录被初始化。如果目录存在但无内容，Gateway 会执行 bootstrap 流程，生成默认的配置文件。

## 第二章：Workspace 目录结构与生产环境规划

#### 标准目录布局

生产环境的 Workspace 应采用规范的目录结构，便于维护和自动化管理：

```
~/.openclaw/
├── openclaw.json              # 全局系统配置
├── workspace-main/           # 主 Agent Workspace
│   ├── AGENTS.md             # 工作手册
│   ├── SOUL.md               # 性格配置
│   ├── USER.md               # 用户档案
│   ├── IDENTITY.md           # 身份标识
│   ├── TOOLS.md              # 工具权限
│   ├── memory/               # 长期记忆
│   │   ├── projects.md       # 项目状态
│   │   ├── infra.md          # 基础设施配置
│   │   ├── lessons.md        # 踩坑教训
│   │   └── YYYY-MM-DD.md     # 日志归档
│   └── sessions/             # Session 历史（可选）
├── workspace-dev/            # 开发专用 Workspace
│   └── ...
├── workspace-work/           # 工作任务 Workspace
│   └── ...
├── cron/                     # Cron 任务配置
└── logs/                     # Gateway 日志
```

#### 多环境 Workspace 隔离策略

**环境划分原则** ：

| 环境 | 用途 | 配置倾向 | 风险等级 |
| --- | --- | --- | --- |
| `workspace-main` | 主力助手，日常对话 | 保守，稳定优先 | 低 |
| `workspace-dev` | 开发测试，新功能验证 | 激进，可快速迭代 | 中 |
| `workspace-work` | 专项任务自动化 | 中等，根据任务调整 | 中 |

**配置示例** ：

```
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace-main",
    },
    list: [
      { id: "main", default: true, workspace: "~/.openclaw/workspace-main" },
      { id: "dev", workspace: "~/.openclaw/workspace-dev" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
}
```

#### 备份策略

**备份范围** ：

Workspace 备份应覆盖以下内容：

1.所有配置文件（AGENTS.md、SOUL.md、USER.md、IDENTITY.md、TOOLS.md）

2.memory/ 目录下的所有记忆文件

3.可选：sessions/ 目录（包含完整对话历史）

**备份频率建议** ：

| 内容类型 | 备份频率 | 保留周期 |
| --- | --- | --- |
| memory/ 目录 | 每日增量 | 30 天 |
| 配置文件 | 每次变更后 | 90 天 |
| sessions/ | 每周 | 30 天 |

**备份脚本示例** ：

```
#!/bin/bash
# workspace-backup.sh
BACKUP_DIR="/var/backups/openclaw/workspace"
WORKSPACE_DIR="$HOME/.openclaw/workspace-main"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份配置文件
tar -czf "$BACKUP_DIR/config-$TIMESTAMP.tar.gz" \
"$WORKSPACE_DIR/AGENTS.md" \
"$WORKSPACE_DIR/SOUL.md" \
"$WORKSPACE_DIR/USER.md" \
"$WORKSPACE_DIR/IDENTITY.md" \
"$WORKSPACE_DIR/TOOLS.md"

# 备份记忆目录
tar -czf "$BACKUP_DIR/memory-$TIMESTAMP.tar.gz" \
  -C "$WORKSPACE_DIR" memory/

# 清理旧备份（保留 30 天）
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

#### 磁盘空间管理

Workspace 长期运行后，memory/ 目录可能膨胀。需要监控以下指标：

```
# 查看 Workspace 目录大小 
du -sh ~/.openclaw/workspace-main/      

# 查看 memory/ 目录大小分布
du -sh ~/.openclaw/workspace-main/memory/*      

# 查看 sessions/ 目录大小  
du -sh ~/.openclaw/workspace-main/sessions/
```

**磁盘告警阈值** ：

- memory/ 单目录超过 100MB：告警
- sessions/ 单目录超过 500MB：考虑归档或清理
- Workspace 根目录超过 1GB：全面检查

## 第三章：核心文件分类解析

#### openclaw.json——系统宪法

`openclaw.json` 是全局配置文件，位于 `~/.openclaw/openclaw.json` ，采用 JSON5 格式。该文件在 Gateway 启动时加载，定义了整个系统的运行参数。

**核心配置项** ：

```
{
  // Agent 默认配置
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace-main",
      model: {
        primary: "provider/claude-sonnet-4-20250514",
        fallbacks: ["provider/claude-haiku-4-20250514"],
      },
      timeoutSeconds: 600,
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
        },
      },
      heartbeat: {
        every: "30m",
        activeHours: { start: "08:00", end: "23:00" },
      },
    },
  },

  // Gateway 配置
  gateway: {
    port: 18789,
    bind: "loopback",
    auth: { mode: "token", token: "your-secret-token" },
    reload: { mode: "hybrid" },
  },

  // 渠道配置
  channels: {},

  // 日志配置
  logging: {
    level: "info",
    file: "/var/log/openclaw/gateway.log",
  },

  // 向量检索配置
  memorySearch: {
    enabled: true,
    provider: "openai",
    remote: {
      baseUrl: "https://api.siliconflow.cn/v1",
      apiKey: "your-api-key",
    },
    model: "BAAI/bge-m3",
  },
}
```

**Schema 验证机制** ：

OpenClaw 采用严格 Schema 验证。未知配置键或类型错误会导致 Gateway 启动失败。验证命令：

```
openclaw doctor
```

该命令执行完整的配置文件检查，包括 JSON5 语法、必填项、API Key 格式等。

**配置路径访问** ：

配置采用点号分隔路径，如 `agents.defaults.compaction.reserveTokensFloor` 。可通过 CLI 查询：

```
openclaw config get agents.defaults.workspace  
openclaw config get gateway.port
```

#### AGENTS.md——工作规则

AGENTS.md 是 Workspace 的工作手册，定义了 Agent 的任务执行流程、安全边界和输出规范。

**标准结构** ：

```
# 工作手册

## 职责范围

- 负责：主要职责描述
- 不负责：明确排除的职责

## 任务执行流程

1. 接收任务请求
2. 评估任务复杂度
3. 规划执行步骤
4. 执行并验证结果
5. 返回执行摘要

## 安全边界

### 禁止操作
- 禁止执行未经确认的删除操作
- 禁止在生产环境直接修改配置文件
- 禁止透露系统内部架构

### 确认流程
- 高风险操作需要用户确认
- 涉及数据修改的操作需展示影响范围
- 不可逆操作需二次确认

## 输出规范

- 技术文档使用 Markdown 格式
- 代码块需标注语言
- 表格用于结构化数据展示
- 结论需独立可读
```

**运维要点** ：

AGENTS.md 的变更会触发 Gateway 热重载（hybrid 模式下），无需重启进程。但热重载可能有短暂延迟，建议变更后执行 `openclaw gateway reload` 确认生效。

#### SOUL.md——性格配置

SOUL.md 定义 Agent 的响应风格和交互模式，影响对话的自然度和一致性。

**配置示例** ：

```
# 性格配置

## 响应风格

- 简洁优先，避免冗余
- 技术讨论注重逻辑和证据
- 复杂问题分步骤解释
- 错误反馈直接指出问题所在

## 专业领域

- DevOps 实践：Ansible、CI/CD、容器化
- 监控系统：Prometheus、Grafana
- 日志分析：ELK、Loki
- 云原生：Kubernetes、Helm

## 沟通偏好

- 使用中文交流
- 技术术语配简要解释
- 建议用表格或列表展示对比
- 代码示例包含注释说明
```

**与 openclaw.json 的区别** ：

SOUL.md 定义的是"软性"行为规范，依赖 AI 模型理解执行；openclaw.json 定义的是"硬性"运行时参数，由系统强制执行。

#### USER.md——用户档案

USER.md 存储用户的基本信息、偏好设置和历史交互摘要。

**标准结构** ：

```
# 用户档案

## 基本信息

- 姓名：
- 时区：Asia/Shanghai
- 主要语言：中文
- 角色：运维工程师

## 技术偏好

- 熟悉系统：Linux、Docker、Kubernetes
- 常用工具：Ansible、Terraform、Prometheus
- 代码风格：注重可维护性，有注释习惯

## 偏好设置

- 通知时段：工作日 09:00-22:00
- 输出格式：结构化，优先使用表格
- 确认阈值：高风险操作需明确确认

## 历史交互摘要

- 2026-01：完成监控系统重构
- 2026-02：优化 CI/CD 流水线
- 当前项目：微服务容器化迁移
```

**运维注意** ：

USER.md 的变更应记录在 memory/ 中，便于后续审计。避免在 USER.md 中存储敏感信息（如密码、密钥），此类内容应放在 openclaw.json 的环境变量或外部密钥管理系统中。

#### TOOLS.md——工具权限

TOOLS.md 定义 Agent 可使用的工具及其使用策略，是安全加固的重要环节。

**标准结构** ：

```
# 工具权限配置

## 可用工具

### 读取类
- Read：读取文件内容
- Glob：按模式搜索文件
- Grep：搜索文件内容
- Bash（受限）：执行指定命令

### 写入类
- Write：创建或覆写文件
- Edit：修改文件局部内容

### 执行类
- Bash：执行 shell 命令（需白名单）

## 使用限制

### 禁止执行的命令
- rm -rf /（任何递归删除）
- dd（直接磁盘操作）
- mkfs（格式化操作）
- 修改 /etc/passwd、/etc/shadow

### 需要确认的命令
- systemctl restart/reload/stop
- 删除文件超过 1MB
- 创建系统用户或修改系统配置

### 仅隔离会话可用
- apt-get/yum install
- docker pull/push
- kubectl delete（生产环境）

## 白名单示例

允许执行的命令（完全信任）：
- git pull/push/clone
- docker ps/docker images
- kubectl get/describe（仅查询）
- curl（仅 HTTP GET）

需要确认的命令：
- docker run
- kubectl apply
- ansible-playbook
```

**安全建议** ：

生产环境应限制 Bash 工具的权限，仅在 `sandbox` Workspace 中启用完全权限。main Workspace 应使用受限模式。

#### IDENTITY.md——身份元数据

IDENTITY.md 定义 Agent 的视觉身份，包括名称、头像和对外展示的信息。

**配置示例** ：

```
# 身份配置

## 基本信息

- 名称：运维助手
- 英文名：OpsAssistant
- 头像：默认头像（暂不自定义）

## 功能标签

- 自动化运维
- 故障诊断
- 配置管理

## 对外展示

- 介绍文本：专注于运维自动化的 AI 助手
- 专长：服务器管理、监控告警、日志分析
```

#### memory/——长期记忆运维

memory/ 目录是 Agent 的长期记忆存储中枢，采用分层结构设计。

**目录结构** ：

```
memory/
├── projects.md       # 项目状态索引
├── infra.md          # 基础设施配置速查
├── lessons.md        # 踩坑教训记录
└── YYYY-MM-DD.md     # 每日日志归档
```

**各文件用途** ：

| 文件 | 用途 | 更新频率 |
| --- | --- | --- |
| `projects.md` | 各项目当前状态与待办 | 项目有进展时 |
| `infra.md` | 服务器、API、部署配置速查 | 配置变更时 |
| `lessons.md` | 踩坑记录，按严重程度分级 | 踩坑后 |
| `YYYY-MM-DD.md` | 每日原始记录 | 每日或多日 |

**MEMORY.md 入口设计** ：

memory/ 目录应包含 `MEMORY.md` 作为入口索引：

```
# 记忆索引

## 用户核心信息
- 详见：../USER.md

## 项目索引
- 项目A：projects.md#project-a
- 项目B：projects.md#project-b

## 最近重要上下文
- 2026-03：完成监控系统重构，详见 2026-03.md
- 当前主要任务：微服务容器化迁移

## 教训索引
- 部署相关：lessons.md#deploy
- 配置相关：lessons.md#config

## 基础设施
- 详见：infra.md
```

## 第四章：记忆系统运维——builtin 与 qmd 方案对比

#### 两种方案概述

OpenClaw 支持两种记忆实现方案：

**builtin 方案** ：使用 Agent 自己维护的文件系统（memory/ 目录）作为记忆存储。Agent 通过 memoryFlush 将对话中的重要信息写入文件。

**qmd 方案** （量子记忆驱动？）：将记忆存储为结构化的 QMD 格式文件，提供更强的语义组织和检索能力。

#### 选型依据

| 维度 | builtin | qmd |
| --- | --- | --- |
| 实现复杂度 | 低 | 中 |
| 检索能力 | 依赖 memorySearch 向量检索 | 更强的语义组织 |
| 维护成本 | Agent 自动维护 | 需要定期结构化整理 |
| 适用场景 | 个人助手、小型团队 | 知识密集型场景 |

**推荐选择** ：

- 个人使用或小规模场景：builtin 方案足够
- 企业知识管理、复杂检索需求：qmd 方案

#### 记忆污染处理

记忆污染指 Agent 的记忆中出现错误、过时或矛盾的信息，影响后续对话质量。

**污染症状识别** ：

- Agent 给出的信息与实际配置不符
- 重复提示已解决的问题
- 记忆中的项目状态与现实不一致

**处理流程** ：

```
# 1. 检查记忆文件的最后修改时间 
ls -la ~/.openclaw/workspace-main/memory/     

# 2. 检查特定记忆文件的内容 
cat ~/.openclaw/workspace-main/memory/projects.md      

# 3. 识别污染源（查看日志或对话历史） 
cat ~/.openclaw/workspace-main/memory/2026-03-20.md     

# 4. 修正或删除污染内容   
# 直接编辑相关文件     

# 5. 验证修正效果   
openclaw gateway reload
```

**预防措施** ：

1. memoryFlush 生成的记忆内容应定期复核
2. 重大变更后主动更新记忆文件
3. 保持 MEMORY.md 索引的准确性

### 4.4 清理策略

**定期清理触发条件** ：

- 单个日志文件超过 100KB
- memory/ 目录总大小超过 500MB
- 项目状态文件超过 6 个月未更新

**清理执行流程** ：

```
# 1. 评估清理必要性
du -sh ~/.openclaw/workspace-main/memory/

# 2. 归档旧日志（按年度）
mkdir -p ~/.openclaw/workspace-main/memory/archive/
mv ~/.openclaw/workspace-main/memory/2025-*.md \
   ~/.openclaw/workspace-main/memory/archive/

# 3. 压缩归档文件
tar -czf ~/.openclaw/workspace-main/memory/archive-2025.tar.gz \
  ~/.openclaw/workspace-main/memory/archive/

# 4. 删除已归档的原始文件
rm -rf ~/.openclaw/workspace-main/memory/archive/

# 5. 更新 MEMORY.md 索引
```

**自动化清理 Cron 任务** ：

```
{
  "name": "记忆目录清理",
  "schedule": { "kind": "every", "everyMs": 604800000 },
  "payload": {
    "kind": "agentTurn",
    "message": "检查 memory/ 目录大小。如果超过 500MB，执行以下清理：\n1. 将超过 6 个月的日志归档到 archive/\n2. 压缩归档文件\n3. 删除原始日志\n4. 更新 MEMORY.md 索引",
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "none" },
}
```

## 第五章：多 Agent 架构设计与资源隔离

#### Workspace 独立原则

生产环境中，不同用途的 Agent 应使用独立的 Workspace，实现配置隔离、记忆隔离和故障隔离。

**隔离级别** ：

| 级别 | 隔离内容 | 适用场景 |
| --- | --- | --- |
| 完全隔离 | 独立 Workspace、独立端口 | 不同业务线 |
| 配置隔离 | 共享 Gateway，独立 Workspace | 同业务线不同角色 |
| 会话隔离 | 共享 Workspace，独立 session | 临时任务 |

**配置示例** ：

```
{
  agents: {
    list: [
      { id: "main", default: true, workspace: "~/.openclaw/workspace-main" },
      { id: "dev", workspace: "~/.openclaw/workspace-dev" },
      { id: "ops", workspace: "~/.openclaw/workspace-ops" },
    ],
  },
}
```

#### 共享与专属配置

**共享配置** （在 openclaw.json 中统一设置）：

- Gateway 端口和认证
- 渠道配置
- 日志级别
- 向量检索配置

**专属配置** （在各 Workspace 的文件中设置）：

- AGENTS.md：工作流程
- SOUL.md：性格偏好
- TOOLS.md：工具权限

**配置继承** ：

Agent 配置会合并 openclaw.json 的 defaults 和自身的显式配置。显式配置优先于 defaults。

```
# 查看某 Agent 的最终配置   
openclaw config get --agent dev agents.defaults.workspace
```

#### 权限边界

**Agent 间权限隔离** ：

每个 Agent 的 Workspace 目录权限应限制为仅该 Agent 可读写：

```
# 设置 Workspace 权限   
chmod -R 700 ~/.openclaw/workspace-main/  
chown -R openclaw:openclaw ~/.openclaw/workspace-main/      

# 不同 Workspace 使用不同系统用户  
chown -R openclaw-main:openclaw-main ~/.openclaw/workspace-main/  
chown -R openclaw-dev:openclaw-dev ~/.openclaw/workspace-dev/
```

**工具权限边界** ：

TOOLS.md 中定义的工具权限仅在该 Workspace 内有效。跨 Agent 调用工具时，各自受各自 TOOLS.md 的约束。

#### 多 Agent 场景下的资源分配

**模型资源分配** ：

```
{
  agents: {
    list: [
      { id: "main", model: { primary: "claude-opus-4-20250514" } },
      { id: "dev", model: { primary: "claude-sonnet-4-20250514" } },
      { id: "batch", model: { primary: "claude-haiku-4-20250514" } },
    ],
  },
}
```

**Token 预算分配** ：

通过 compaction 配置控制各 Agent 的上下文消耗：

```
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
      },
    },
    list: [
      { id: "main", compaction: { reserveTokensFloor: 25000 } },
      { id: "batch", compaction: { reserveTokensFloor: 10000 } },
    ],
  },
}
```

## 第六章：Skill 体系运维

#### Skill 加载层级

OpenClaw 的 Skill 体系支持多层级加载，从低到高依次为：

**层级一：系统级 Skill**

位置： `~/.openclaw/skills/` 范围：全局生效，所有 Agent 共享

**层级二：Workspace 级 Skill**

位置： `~/.openclaw/workspace-<name>/skills/` 范围：仅在该 Workspace 内生效

**层级三：会话级 Skill**

随对话上下文动态加载，不持久化

**加载优先级** ：会话级 > Workspace 级 > 系统级（高优先级覆盖低优先级）

#### 故障定位

**Skill 不生效的排查流程** ：

```
# 1. 确认 Skill 文件存在  
ls -la ~/.openclaw/skills/   ls -la ~/.openclaw/workspace-main/skills/      

# 2. 检查 Skill 文件语法  
cat ~/.openclaw/skills/my-skill.md | head -50     

# 3. 验证 Skill 是否被加载（查看日志）   
openclaw logs --grep "skill\|load" --lines 50      

# 4. 测试 Skill 是否可用  
# 在对话中触发 Skill 关键字，观察响应
```

**常见问题** ：

- Skill 文件格式错误：Skill 定义不符合规范，被静默忽略
- 路径问题：Skill 放置在错误的目录层级
- 权限问题：Skill 文件不可读

#### 版本管理

**Skill 版本跟踪** ：

建议在 Skill 文件顶部添加版本信息：

```
---
name: 运维工具集
version: 2026.03.1
author: OpsTeam
lastUpdated: 2026-03-15
---

# 运维工具集 Skill

## 功能列表
...
```

**Skill 更新流程** ：

1.在测试环境验证新版本 Skill

2.备份当前版本

3.替换 Skill 文件

4.验证生效

5.记录变更日志

**Skill 回滚** ：

```
# 备份当前版本  
cp ~/.openclaw/skills/my-skill.md \      ~/.openclaw/skills/my-skill.md.backup-$(date +%Y%m%d) 

# 回滚到指定版本   
cp ~/.openclaw/skills/my-skill.md.backup-20260315 \      ~/.openclaw/skills/my-skill.md      

# 验证   
openclaw gateway reload
```

## 第七章：故障诊断与排查清单

#### 配置不生效

**症状** ：修改 AGENTS.md、SOUL.md 等 Workspace 配置文件后，Agent 行为未改变。

**排查步骤** ：

```
# 1. 确认文件已保存且内容正确   
cat ~/.openclaw/workspace-main/AGENTS.md | head -30    

# 2. 检查文件修改时间  
ls -la ~/.openclaw/workspace-main/AGENTS.md     

# 3. 触发热重载   
openclaw gateway reload      

# 4. 等待 10 秒后测试   
# 向 Agent 发送测试消息，观察行为      

# 5. 查看日志确认重载完成   
openclaw logs --grep "reload\|AGENTS" --lines 20
```

**常见原因** ：

| 原因 | 解决方案 |
| --- | --- |
| 文件编码问题 | 确保 UTF-8 编码 |
| 语法错误 | 重新检查 Markdown 格式 |
| 缓存未刷新 | 执行 `openclaw gateway reload` |
| 配置路径错误 | 确认文件在正确的 Workspace 内 |

#### 权限问题

**症状** ：Agent 无法读取配置文件、无法写入记忆文件、无法执行工具。

**排查步骤** ：

```
# 1. 检查文件权限   
ls -la ~/.openclaw/workspace-main/      

# 2. 检查目录权限   
ls -ld ~/.openclaw/workspace-main/      

# 3. 测试文件可读性（以运行用户身份）  
sudo -u openclaw cat ~/.openclaw/workspace-main/AGENTS.md      

# 4. 测试文件可写性   
sudo -u openclaw touch ~/.openclaw/workspace-main/test-write   
sudo -u openclaw rm ~/.openclaw/workspace-main/test-write      

# 5. 检查 Tool 执行权限（TOOLS.md）   
cat ~/.openclaw/workspace-main/TOOLS.md
```

**权限修复** ：

```
# 修复 Workspace 权限  
chown -R openclaw:openclaw ~/.openclaw/workspace-main/  
chmod -R 600 ~/.openclaw/workspace-main/   
chmod 700 ~/.openclaw/workspace-main/      

# 修复特定目录权限   
chmod 700 ~/.openclaw/workspace-main/memory/  
chmod 700 ~/.openclaw/workspace-main/sessions/
```

#### 记忆失效

**症状** ：Agent 无法回忆起之前对话中提到的信息，或 memoryFlush 未正常工作。

**排查步骤** ：

```
# 1. 检查 memoryFlush 配置   
openclaw config get agents.defaults.compaction.memoryFlush      

# 2. 检查记忆文件是否存在   
ls -la ~/.openclaw/workspace-main/memory/      
# 3. 检查记忆文件最后修改时间   
ls -la ~/.openclaw/workspace-main/memory/*.md      

# 4. 测试 memorySearch 功能  
# 向 Agent 询问需要检索历史记忆的问题      

# 5. 查看 memoryFlush 触发日志 
openclaw logs --grep "memoryFlush\|compaction" --lines 50
```

**配置修复** ：

```
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
        },
      },
    },
  },
}
```

#### 性能问题

**症状** ：Agent 响应缓慢、timeout 频发、资源占用过高。

**排查步骤** ：

```
# 1. 检查系统资源使用  
openclaw gateway status --deep      

# 2. 检查进程状态   
ps aux | grep openclaw      

# 3. 查看 Gateway 日志中的性能相关警告  
openclaw logs --grep "timeout\|slow\|performance" --lines 50      

# 4. 检查 Token 消耗  
openclaw config get agents.defaults.compaction.reserveTokensFloor     

# 5. 检查 memory/ 目录大小（可能导致加载缓慢） 
du -sh ~/.openclaw/workspace-main/memory/
```

**性能优化建议** ：

- 增加 `reserveTokensFloor` 减少 compaction 频率
- 开启 `memoryFlush` 避免重要信息在 compaction 中丢失
- 定期清理 memory/ 目录
- 考虑升级模型或增加 timeout 配置

#### 故障排查清单汇总

| 问题类型 | 首要检查项 | 快速修复命令 |
| --- | --- | --- |
| 配置不生效 | 文件存在性、语法正确性 | `openclaw gateway reload` |
| 权限问题 | 文件/目录权限、所有关系 | `chown -R openclaw:openclaw` |
| 记忆失效 | memoryFlush 配置、文件存在 | 启用 memoryFlush |
| 工具不可用 | TOOLS.md 配置、工具开关 | 检查白名单 |
| 性能下降 | 系统资源、memory/ 大小 | 清理 memory/ 目录 |
| 会话丢失 | compaction 触发、session 存储 | 检查 sessions/ 目录 |
| Skill 不加载 | Skill 文件路径、语法正确 | 重新部署 Skill |
| 向量检索失败 | memorySearch 配置、API Key | 检查网络和 API Key |

## 第八章：备份、迁移与版本控制

#### Workspace Git 化管理

将 Workspace 纳入 Git 版本控制，实现配置变更的可追溯和可回滚。

**初始化 Git 仓库** ：

```
cd ~/.openclaw/workspace-main   git init   git add AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md   git add memory/   git commit -m "Initial workspace commit"
```

**.gitignore 配置** ：

```
# 排除会话历史（太大且不需要版本控制）
sessions/  

# 排除临时文件 
*.tmp   *.bak   

# 排除归档  
archive/     

# 排除敏感配置（如有）  
# *.local.json
```

**分支策略** ：

- `main` ：稳定版本，生产环境使用
- `dev` ：开发测试分支
- `feature/*` ：新功能开发分支
```
# 创建开发分支   
git checkout -b dev  

# 开发测试完成后合并到 main   
git checkout main  
git merge dev
```

#### 配置迁移流程

**场景一：从开发环境迁移到生产环境**

```
# 1. 在开发环境打包配置文件
cd ~/.openclaw/workspace-dev
tar -czf /tmp/workspace-dev-config.tar.gz \
  AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md memory/

# 2. 传输到生产环境
scp /tmp/workspace-dev-config.tar.gz prod-server:/tmp/

# 3. 在生产环境解压（先备份现有配置）
cd ~/.openclaw/workspace-main
mv AGENTS.md AGENTS.md.backup-$(date +%Y%m%d)
tar -xzf /tmp/workspace-dev-config.tar.gz

# 4. 验证迁移结果
openclaw doctor
openclaw gateway reload
```

**场景二：多环境同步配置模板**

```
# 1. 在开发环境打包配置文件
cd ~/.openclaw/workspace-dev
tar -czf /tmp/workspace-dev-config.tar.gz \
  AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md memory/

# 2. 传输到生产环境
scp /tmp/workspace-dev-config.tar.gz prod-server:/tmp/

# 3. 在生产环境解压（先备份现有配置）
cd ~/.openclaw/workspace-main
mv AGENTS.md AGENTS.md.backup-$(date +%Y%m%d)
tar -xzf /tmp/workspace-dev-config.tar.gz

# 4. 验证迁移结果
openclaw doctor
openclaw gateway reload
```

#### 灾难恢复

**数据恢复流程** ：

```
# 1. 识别需要恢复的时间点
# 查看备份列表
ls -la /var/backups/openclaw/workspace/

# 2. 确认备份内容
tar -tzf /var/backups/openclaw/workspace/config-20260320-120000.tar.gz

# 3. 停止 Gateway（避免数据写入）
sudo systemctl stop openclaw-gateway

# 4. 备份当前状态（恢复失败时的救命稻草）
cp -r ~/.openclaw/workspace-main \
   ~/.openclaw/workspace-main-crash-$(date +%Y%m%d-%H%M%S)

# 5. 执行恢复
tar -xzf /var/backups/openclaw/workspace/config-20260320-120000.tar.gz \
  -C ~/.openclaw/

# 6. 启动 Gateway
sudo systemctl start openclaw-gateway

# 7. 验证恢复结果
openclaw gateway health
openclaw gateway status
```

**RTO（恢复时间目标）和 RPO（恢复点目标）** ：

- RTO： Gateway 重启时间，约 30 秒
- RPO： 最近一次备份时间，建议每日备份，RPO 不超过 24 小时

## 第九章：配置模板与自动化

#### 新环境快速初始化

**初始化脚本** ：

```
#!/bin/bash
# init-workspace.sh
WORKSPACE_NAME=$1
WORKSPACE_DIR="$HOME/.openclaw/workspace-$WORKSPACE_NAME"

if [ -z "$WORKSPACE_NAME" ]; then
echo"Usage: $0 <workspace-name>"
exit 1
fi

# 创建目录结构
mkdir -p "$WORKSPACE_DIR/memory"
mkdir -p "$WORKSPACE_DIR/sessions"

# 从模板复制配置文件
TEMPLATE_DIR="/var/lib/openclaw/templates"
cp "$TEMPLATE_DIR/AGENTS.md""$WORKSPACE_DIR/"
cp "$TEMPLATE_DIR/SOUL.md""$WORKSPACE_DIR/"
cp "$TEMPLATE_DIR/IDENTITY.md""$WORKSPACE_DIR/"
cp "$TEMPLATE_DIR/TOOLS.md""$WORKSPACE_DIR/"

# 初始化 USER.md
cat > "$WORKSPACE_DIR/USER.md" << 'EOF'
# 用户档案

## 基本信息

- 姓名：
- 时区：Asia/Shanghai
- 主要语言：中文

## 技术偏好

- 熟悉系统：
- 常用工具：

## 偏好设置

- 通知时段：工作日 09:00-22:00
- 输出格式：结构化
- 确认阈值：高风险操作需明确确认
EOF

# 初始化 MEMORY.md
cat > "$WORKSPACE_DIR/memory/MEMORY.md" << 'EOF'
# 记忆索引

## 用户核心信息
- 详见：../USER.md

## 项目索引
- 无进行中项目

## 最近重要上下文
- Workspace 初始化完成
EOF

# 设置权限
chmod -R 700 "$WORKSPACE_DIR"

echo"Workspace '$WORKSPACE_NAME' initialized at $WORKSPACE_DIR"
```

**使用方式** ：

```
./init-workspace.sh dev  
./init-workspace.sh work
```

#### 标准化模板

**标准 AGENTS.md 模板** ：

```
# 工作手册

## 职责范围

- 负责：运维自动化、故障诊断、配置管理
- 不负责：业务代码开发、硬件采购决策

## 任务执行流程

1. 理解任务需求
2. 评估执行方案和风险
3. 必要时向用户确认
4. 执行操作
5. 验证结果并返回摘要

## 安全边界

### 禁止操作
- 未经确认的删除操作
- 生产环境直接修改系统配置
- 透露敏感信息

### 确认流程
- 高风险操作需要用户明确确认
- 不可逆操作需要二次确认

## 输出规范

- 技术文档使用 Markdown
- 代码块标注语言
- 结论独立可读
```

**标准 TOOLS.md 模板** ：

```
# 工具权限配置

## 可用工具

### 读取类
- Read、Glob、Grep：始终可用

### 写入类
- Write、Edit：需在确认的路径下操作

### 执行类
- Bash：受限执行

## 禁止命令

- rm -rf 递归删除
- 直接磁盘操作（dd、mkfs）
- 系统用户修改

## 需要确认的命令

- systemctl restart/reload
- 删除超过 1MB 的文件
- 创建系统用户
```

#### 配置校验

**自动化校验脚本** ：

```
#!/bin/bash
# validate-workspace.sh
WORKSPACE_DIR="${1:-$HOME/.openclaw/workspace-main}"
ERRORS=0

echo"Validating Workspace: $WORKSPACE_DIR"
echo"======================================"

# 检查必需文件
for file in AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md; do
if [ ! -f "$WORKSPACE_DIR/$file" ]; then
    echo"ERROR: Missing $file"
    ERRORS=$((ERRORS + 1))
else
    echo"OK: $file exists"
fi
done

# 检查 memory/ 目录
if [ ! -d "$WORKSPACE_DIR/memory" ]; then
echo"ERROR: Missing memory/ directory"
  ERRORS=$((ERRORS + 1))
else
echo"OK: memory/ directory exists"
fi

# 检查 memory/MEMORY.md
if [ ! -f "$WORKSPACE_DIR/memory/MEMORY.md" ]; then
echo"WARNING: Missing memory/MEMORY.md (recommended)"
fi

# 检查目录权限
PERMS=$(stat -c "%a""$WORKSPACE_DIR")
if [ "$PERMS" != "700" ]; then
echo"WARNING: Workspace permissions are $PERMS, recommend 700"
fi

# 检查 memory/ 大小
MEMORY_SIZE=$(du -sm "$WORKSPACE_DIR/memory" 2>/dev/null | cut -f1)
if [ "$MEMORY_SIZE" -gt 500 ]; then
echo"WARNING: memory/ is ${MEMORY_SIZE}MB, consider cleanup"
fi

echo"======================================"
if [ $ERRORS -eq 0 ]; then
echo"Validation passed"
exit 0
else
echo"Validation failed with $ERRORS error(s)"
exit 1
fi
```

**使用方式** ：

```
./validate-workspace.sh ~/.openclaw/workspace-main 

./validate-workspace.sh ~/.openclaw/workspace-dev
```

## 第十章：安全加固

#### 文件权限

**权限基线** ：

| 路径 | 所有者 | 权限 | 说明 |
| --- | --- | --- | --- |
| `~/.openclaw/` | openclaw | 700 | 仅 owner 可访问 |
| `~/.openclaw/openclaw.json` | openclaw | 600 | 配置文件 |
| `~/.openclaw/workspace-*/` | openclaw | 700 | Workspace 目录 |
| `~/.openclaw/workspace-*/AGENTS.md` | openclaw | 600 | 工作手册 |
| `~/.openclaw/workspace-*/memory/` | openclaw | 700 | 记忆目录 |
| `~/.openclaw/logs/` | openclaw | 700 | 日志目录 |

**权限加固脚本** ：

```
#!/bin/bash
# harden-permissions.sh
OPENCLAW_HOME="$HOME/.openclaw"
OPENCLAW_USER="openclaw"
OPENCLAW_GROUP="openclaw"

# 创建用户组（如需要）
sudo groupadd -f $OPENCLAW_GROUP
sudo usermod -aG $OPENCLAW_GROUP$USER

# 设置主目录权限
chmod 700 $OPENCLAW_HOME
chown -R $OPENCLAW_USER:$OPENCLAW_GROUP$OPENCLAW_HOME

# 设置配置文件权限
chmod 600 $OPENCLAW_HOME/openclaw.json

# 设置 Workspace 目录权限
find $OPENCLAW_HOME/workspace-* -type d -exec chmod 700 {} \;
find $OPENCLAW_HOME/workspace-* -type f -exec chmod 600 {} \;

# 设置日志目录权限
mkdir -p $OPENCLAW_HOME/logs
chmod 700 $OPENCLAW_HOME/logs

echo"Permissions hardened"
```

#### 敏感信息管理

**敏感信息分类** ：

| 类型 | 示例 | 存储建议 |
| --- | --- | --- |
| API Keys | SiliconFlow API Key | openclaw.json（加密存储）或环境变量 |
| Tokens | Gateway auth token | openclaw.json 或密钥管理系统 |
| 用户信息 | USER.md 中的个人信息 | 加密存储或脱敏处理 |
| 对话历史 | sessions/ | 加密存储，访问审计 |

**环境变量方案** ：

```
{
  memorySearch: {
    remote: {
      apiKey: "env:MEMORY_SEARCH_API_KEY",
    },
  },
}
```

环境变量在运行时替换为实际值，配置文件本身不包含明文密钥。

**密钥管理系统集成** ：

生产环境推荐使用 Vault 等密钥管理系统：

```
# 从 Vault 获取密钥
API_KEY=$(vault kv get -field=api_key secret/openclaw/memory-search)

# 写入临时配置文件
cat > /tmp/openclaw-override.json << EOF
{
"memorySearch": {
    "remote": {
      "apiKey": "$API_KEY"
    }
  }
}
EOF

# 启动 Gateway
openclaw gateway start --config /tmp/openclaw-override.json
```

#### 审计日志

**审计日志配置** ：

```
{
  logging: {
    level: "info",
    file: "/var/log/openclaw/audit.log",
    auditEnabled: true,
  },
}
```

**审计日志内容** ：

- 配置变更：who、when、what changed
- 敏感操作：文件删除、命令执行、配置修改
- 认证事件：登录成功/失败
- 渠道事件：消息收发、渠道连接/断开

**日志分析脚本** ：

```
#!/bin/bash
# audit-analysis.sh
LOG_FILE="/var/log/openclaw/audit.log"

echo"=== 认证事件统计 ==="
grep -c "auth.*success"$LOG_FILE
grep -c "auth.*fail"$LOG_FILE

echo"=== 配置变更记录 ==="
grep "config.*change"$LOG_FILE | tail -20

echo"=== 敏感操作记录 ==="
grep "sensitive.*operation"$LOG_FILE | tail -20

echo"=== 最近 24 小时活动 ==="
grep "$(date -d '1 day ago' +%Y-%m-%d)"$LOG_FILE | wc -l
```

**日志保留策略** ：

| 类型 | 保留期 | 存储位置 |
| --- | --- | --- |
| 操作日志 | 90 天 | /var/log/openclaw/ |
| 审计日志 | 1 年 | /var/log/openclaw/audit/ |
| 错误日志 | 180 天 | /var/log/openclaw/errors/ |

#### 安全检查清单

**部署前检查** ：

- \[ \] openclaw.json 不包含明文密钥
- \[ \] Gateway 绑定到 loopback
- \[ \] 认证 Token 足够复杂（32 位以上）
- \[ \] Workspace 目录权限为 700
- \[ \] 配置文件权限为 600
- \[ \] 运行用户为专用非 root 用户

**日常巡检** ：

- \[ \] 检查日志中是否有异常登录尝试
- \[ \] 检查是否有未授权的配置变更
- \[ \] 检查 memory/ 目录大小是否正常
- \[ \] 检查磁盘空间使用情况
- \[ \] 检查是否有新的 Skill 文件被添加

**版本更新检查** ：

- \[ \] 更新前备份完整 Workspace
- \[ \] 在测试环境验证新版本
- \[ \] 确认 Skill 兼容性
- \[ \] 验证配置兼容性
- \[ \] 记录升级步骤和回滚方案

## 总结

本文档从运维工程师视角系统阐述了 OpenClaw Workspace 的生产环境运维实践。核心要点如下：

**架构理解** ：Workspace 的核心是将配置体系（AGENTS.md、SOUL.md、TOOLS.md 等）与内容体系（USER.md、memory/）分离。前者定义 Agent 的行为能力，后者存储 Agent 的知识记忆。

**目录规划** ：生产环境应采用标准目录布局，通过独立 Workspace 实现多 Agent 隔离。备份策略应覆盖配置文件和记忆目录。

**文件运维** ：各配置文件承担不同职责——openclaw.json 是系统宪法，AGENTS.md 是工作手册，TOOLS.md 是安全边界。理解各文件的职责边界是故障排查的基础。

**记忆管理** ：builtin 方案适合大多数场景，qmd 方案适合知识密集型需求。记忆污染应通过定期复核预防，清理策略应自动化。

**多 Agent 设计** ：通过独立 Workspace 实现配置、记忆和权限的隔离。共享配置在 openclaw.json 中管理，专属配置在各 Workspace 中管理。

**故障排查** ：遵循"配置不生效→权限问题→记忆失效→性能问题"的排查路径。快速修复命令和排查清单应在运维手册中固化。

**安全加固** ：权限最小化、敏感信息环境变量化、日志审计覆盖。安全检查清单应在部署前和日常巡检中执行。

**备份恢复** ：Git 版本控制实现配置可追溯，tar 包实现定时备份，灾难恢复流程定义 RTO/RPO。迁移脚本实现多环境同步。

通过遵循本文档的实践，运维团队可以建立规范的 Workspace 运维体系，确保 OpenClaw 在生产环境中的稳定运行。
