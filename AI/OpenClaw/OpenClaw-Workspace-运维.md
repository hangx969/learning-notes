---
title: OpenClaw Workspace 运维实战
tags:
  - AI
  - openclaw
  - workspace
  - ops
aliases:
  - OpenClaw Workspace 运维
  - Workspace运维
---

# OpenClaw Workspace 运维

> 来源：[牛逼干货分享！OpenClaw Workspace 运维实战手册](https://mp.weixin.qq.com/s/4tVt4g6BlRv_Xe7RUIOzGQ)

---

## 核心概念：配置与内容的分离

Workspace 本质上将 Agent 运行环境拆分为两个正交体系：

| 体系 | 文件 | 性质 | 决定 |
|------|------|------|------|
| **配置文件**（静态） | `AGENTS.md` `SOUL.md` `IDENTITY.md` `TOOLS.md` | 定义行为规范 | Agent 能做什么、怎么做 |
| **内容文件**（动态） | `USER.md` `memory/` Session 历史 | 存储知识记忆 | Agent 知道什么、记得什么 |

全局配置 `~/.openclaw/openclaw.json` 是"系统宪法"，定义 Gateway 行为和运行时参数，采用 JSON5 格式，严格 Schema 验证（`openclaw doctor` 检查）。

---

## 标准目录布局

```
~/.openclaw/
├── openclaw.json              # 全局系统配置
├── workspace-main/            # 主 Agent Workspace
│   ├── AGENTS.md              # 工作手册（任务流程、安全边界、输出规范）
│   ├── SOUL.md                # 性格配置（响应风格、专业领域、沟通偏好）
│   ├── USER.md                # 用户档案（偏好、技术栈、历史交互）
│   ├── IDENTITY.md            # 身份标识（名称、头像、功能标签）
│   ├── TOOLS.md               # 工具权限（白名单/黑名单/确认策略）
│   ├── memory/                # 长期记忆
│   │   ├── MEMORY.md          # 记忆入口索引
│   │   ├── projects.md        # 项目状态
│   │   ├── infra.md           # 基础设施配置速查
│   │   ├── lessons.md         # 踩坑教训（按严重程度分级）
│   │   └── YYYY-MM-DD.md      # 日志归档
│   └── sessions/              # Session 历史（可选）
├── workspace-dev/             # 开发专用 Workspace
├── workspace-work/            # 工作任务 Workspace
├── skills/                    # 系统级 Skills（全局生效）
├── cron/                      # Cron 任务配置
└── logs/                      # Gateway 日志
```

### Workspace 路径优先级

1. Agent 配置中显式指定的 `workspace` 路径（最高）
2. `agents.defaults.workspace` 配置项
3. `~/.openclaw/workspace`（默认）

```sh
# 查看当前路径
openclaw config get agents.defaults.workspace

# 启动时指定
openclaw gateway start --workspace /path/to/custom/workspace
```

> [!note]
> Gateway 启动时目录不存在会自动创建并执行 bootstrap 流程。

---

## 多 Agent 环境隔离

| 环境 | 用途 | 配置倾向 |
|------|------|---------|
| `workspace-main` | 主力助手，日常对话 | 保守，稳定优先 |
| `workspace-dev` | 开发测试，新功能验证 | 激进，可快速迭代 |
| `workspace-work` | 专项任务自动化 | 按任务调整 |

**隔离级别**：

| 级别 | 隔离内容 | 适用场景 |
|------|---------|---------|
| 完全隔离 | 独立 Workspace + 独立端口 | 不同业务线 |
| 配置隔离 | 共享 Gateway，独立 Workspace | 同业务线不同角色 |
| 会话隔离 | 共享 Workspace，独立 session | 临时任务 |

**配置示例**：

```json5
{
  agents: {
    defaults: { workspace: "~/.openclaw/workspace-main" },
    list: [
      { id: "main", default: true, workspace: "~/.openclaw/workspace-main" },
      { id: "dev", workspace: "~/.openclaw/workspace-dev" },
      { id: "ops", workspace: "~/.openclaw/workspace-ops" }
    ]
  }
}
```

**模型与 Token 差异化分配**：

```json5
{
  agents: {
    list: [
      { id: "main", model: { primary: "claude-opus-4-20250514" }, compaction: { reserveTokensFloor: 25000 } },
      { id: "dev",  model: { primary: "claude-sonnet-4-20250514" } },
      { id: "batch", model: { primary: "claude-haiku-4-20250514" }, compaction: { reserveTokensFloor: 10000 } }
    ]
  }
}
```

---

## 核心配置文件速查

### openclaw.json 关键配置项

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace-main",
      model: { primary: "provider/claude-sonnet-4-20250514", fallbacks: ["provider/claude-haiku-4-20250514"] },
      timeoutSeconds: 600,
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: { enabled: true, softThresholdTokens: 4000 }
      },
      heartbeat: { every: "30m", activeHours: { start: "08:00", end: "23:00" } }
    }
  },
  gateway: { port: 18789, bind: "loopback", auth: { mode: "token", token: "your-secret-token" }, reload: { mode: "hybrid" } },
  memorySearch: { enabled: true, provider: "openai", remote: { baseUrl: "https://api.siliconflow.cn/v1", apiKey: "your-api-key" }, model: "BAAI/bge-m3" }
}
```

### TOOLS.md 权限分级

| 级别 | 操作 | 示例 |
|------|------|------|
| **始终允许** | 读取类 | `git pull`、`docker ps`、`kubectl get/describe` |
| **需要确认** | 写入/变更类 | `systemctl restart`、`docker run`、`kubectl apply`、`ansible-playbook` |
| **禁止执行** | 破坏性操作 | `rm -rf`、`dd`、`mkfs`、修改 `/etc/passwd` |
| **仅隔离会话** | 安装类 | `apt-get install`、`docker pull/push`、`kubectl delete`（生产） |

### SOUL.md vs openclaw.json

- **SOUL.md**：定义"软性"行为规范（响应风格、沟通偏好），依赖 AI 模型理解执行
- **openclaw.json**：定义"硬性"运行时参数（超时、Token、端口），由系统强制执行

---

## 记忆系统运维

### builtin vs qmd 方案

| 维度 | builtin | qmd |
|------|---------|-----|
| 实现复杂度 | 低 | 中 |
| 检索能力 | 依赖 memorySearch 向量检索 | 更强的语义组织 |
| 维护成本 | Agent 自动维护 | 需定期结构化整理 |
| 推荐场景 | 个人助手、小型团队 | 知识密集型、企业级 |

### 记忆污染处理

**症状**：Agent 信息与实际配置不符、重复提示已解决的问题、项目状态不一致。

**处理流程**：

```sh
ls -la ~/.openclaw/workspace-main/memory/           # 检查最后修改时间
cat ~/.openclaw/workspace-main/memory/projects.md   # 检查内容
# 直接编辑修正污染内容
openclaw gateway reload                             # 验证修正
```

**预防**：定期复核 memoryFlush 内容、重大变更后主动更新、保持 MEMORY.md 索引准确。

### 清理策略

| 触发条件 | 操作 |
|---------|------|
| 单个日志文件 > 100KB | 归档 |
| memory/ 总大小 > 500MB | 清理旧日志 |
| 项目状态文件 > 6 个月未更新 | 归档或删除 |

```sh
# 归档旧日志
mkdir -p ~/.openclaw/workspace-main/memory/archive/
mv ~/.openclaw/workspace-main/memory/2025-*.md ~/.openclaw/workspace-main/memory/archive/
tar -czf ~/.openclaw/workspace-main/memory/archive-2025.tar.gz ~/.openclaw/workspace-main/memory/archive/
rm -rf ~/.openclaw/workspace-main/memory/archive/
# 更新 MEMORY.md 索引
```

---

## Skill 加载层级

| 层级 | 位置 | 范围 |
|------|------|------|
| 系统级 | `~/.openclaw/skills/` | 全局，所有 Agent 共享 |
| Workspace 级 | `~/.openclaw/workspace-<name>/skills/` | 仅该 Workspace |
| 会话级 | 随对话上下文动态加载 | 不持久化 |

**优先级**：会话级 > Workspace 级 > 系统级（高覆盖低）

**Skill 不生效排查**：

```sh
ls -la ~/.openclaw/skills/ ~/.openclaw/workspace-main/skills/  # 确认文件存在
cat ~/.openclaw/skills/my-skill.md | head -50                  # 检查语法
openclaw logs --grep "skill\|load" --lines 50                  # 查看加载日志
```

---

## 故障排查清单

| 问题类型 | 首要检查项 | 快速修复 |
|---------|-----------|---------|
| 配置不生效 | 文件存在性、语法正确性 | `openclaw gateway reload` |
| 权限问题 | 文件/目录权限、所有关系 | `chown -R openclaw:openclaw` + `chmod 700` |
| 记忆失效 | memoryFlush 配置、文件存在 | 启用 memoryFlush |
| 工具不可用 | TOOLS.md 配置、工具开关 | 检查白名单 |
| 性能下降 | 系统资源、memory/ 大小 | 清理 memory/ 目录 |
| Skill 不加载 | Skill 文件路径、语法正确 | 重新部署 Skill |
| 向量检索失败 | memorySearch 配置、API Key | 检查网络和 API Key |

---

## 备份与恢复

### 备份策略

| 内容 | 频率 | 保留周期 |
|------|------|---------|
| 配置文件 | 每次变更后 | 90 天 |
| memory/ | 每日增量 | 30 天 |
| sessions/ | 每周 | 30 天 |

**备份脚本**：

```sh
#!/bin/bash
BACKUP_DIR="/var/backups/openclaw/workspace"
WORKSPACE_DIR="$HOME/.openclaw/workspace-main"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
mkdir -p "$BACKUP_DIR"

# 备份配置 + 记忆
tar -czf "$BACKUP_DIR/config-$TIMESTAMP.tar.gz" \
  "$WORKSPACE_DIR/AGENTS.md" "$WORKSPACE_DIR/SOUL.md" \
  "$WORKSPACE_DIR/USER.md" "$WORKSPACE_DIR/IDENTITY.md" "$WORKSPACE_DIR/TOOLS.md"
tar -czf "$BACKUP_DIR/memory-$TIMESTAMP.tar.gz" -C "$WORKSPACE_DIR" memory/

# 清理旧备份
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

### Git 版本控制

```sh
cd ~/.openclaw/workspace-main
git init
git add AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md memory/
git commit -m "Initial workspace commit"
```

**.gitignore**：排除 `sessions/`、`*.tmp`、`*.bak`、`archive/`。

### 灾难恢复

RTO 约 30 秒（Gateway 重启），RPO 建议不超过 24 小时（每日备份）。

```sh
sudo systemctl stop openclaw-gateway
cp -r ~/.openclaw/workspace-main ~/.openclaw/workspace-main-crash-$(date +%Y%m%d-%H%M%S)
tar -xzf /var/backups/openclaw/workspace/config-XXXXXXXX.tar.gz -C ~/.openclaw/
sudo systemctl start openclaw-gateway
openclaw gateway health
```

---

## 安全加固

### 权限基线

| 路径 | 权限 | 说明 |
|------|------|------|
| `~/.openclaw/` | 700 | 仅 owner 可访问 |
| `~/.openclaw/openclaw.json` | 600 | 含敏感配置 |
| `~/.openclaw/workspace-*/` | 700 | Workspace 目录 |
| 配置文件（*.md） | 600 | 工作手册等 |

### 敏感信息管理

- **环境变量方案**：`"apiKey": "env:MEMORY_SEARCH_API_KEY"`，运行时替换
- **密钥管理系统**：生产环境推荐 Vault 等，启动时注入

### 安全检查清单

**部署前**：
- [ ] openclaw.json 不含明文密钥
- [ ] Gateway 绑定 loopback
- [ ] 认证 Token 32 位以上
- [ ] Workspace 目录权限 700，配置文件 600
- [ ] 运行用户为专用非 root 用户

**日常巡检**：
- [ ] 日志中无异常登录尝试
- [ ] 无未授权配置变更
- [ ] memory/ 大小正常
- [ ] 磁盘空间充足

### 日志保留

| 类型 | 保留期 |
|------|-------|
| 操作日志 | 90 天 |
| 审计日志 | 1 年 |
| 错误日志 | 180 天 |

---

## 自动化工具

### Workspace 初始化脚本

```sh
#!/bin/bash
# init-workspace.sh <name>
WORKSPACE_DIR="$HOME/.openclaw/workspace-$1"
mkdir -p "$WORKSPACE_DIR/memory" "$WORKSPACE_DIR/sessions"
# 从模板复制配置文件...
chmod -R 700 "$WORKSPACE_DIR"
```

### Workspace 校验脚本

```sh
#!/bin/bash
# validate-workspace.sh [path]
WORKSPACE_DIR="${1:-$HOME/.openclaw/workspace-main}"
# 检查必需文件：AGENTS.md SOUL.md USER.md IDENTITY.md TOOLS.md
# 检查 memory/ 目录和 MEMORY.md
# 检查目录权限是否为 700
# 检查 memory/ 大小是否超过 500MB
```

### 自动清理 Cron 任务

```json5
{
  "name": "记忆目录清理",
  "schedule": { "kind": "every", "everyMs": 604800000 },  // 每周
  "payload": {
    "kind": "agentTurn",
    "message": "检查 memory/ 目录大小，超过 500MB 则归档 6 个月前的日志并更新索引"
  },
  "sessionTarget": "isolated",
  "delivery": { "mode": "none" }
}
```
