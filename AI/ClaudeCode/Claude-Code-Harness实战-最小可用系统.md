---
title: "Harness 实战：从零搭建最小可用的 Harness 系统"
source: "https://mp.weixin.qq.com/s/Q1pAwfL2FXGg2mEQNSNrkw"
date: 2026-04-09
tags:
  - AI/claude-code
  - AI/harness
  - AI/safety
---

# Harness 实战：从零搭建最小可用的 Harness 系统

## 问题的起源

当我用 Claude Code 做项目后，大概第三四天的时候，就逐渐出现问题了。

一次，AI 在实现一个功能时，顺手把 `.env` 文件里的数据库连接字符串写进了代码注释里。另一次，AI 执行了一段 Bash 命令之后，把返回的 API Key 中间结果复制成了变量名，然后又把这个变量名写进了代码文件。还有一次，AI 修改 migrations 目录下的文件，觉得那是"顺便的优化"，但实际上把之前的数据迁移记录覆盖了一部分。

说到底，这三件事都指向同一个原因：AI 有完整的文件系统访问权限，却没有系统层面的边界约束。

我想过用更好的提示词来解决。但提示词是软约束——AI 可以听，也可以不听。当上下文变长、任务变复杂时，提示词里的要求经常被忽略，这不是 Claude 的问题，是提示词本身无法被强制执行。

真正有效的方式，是在系统层面把边界画死：不是告诉 AI"你应该这样做"，而是让 AI"必须这样做"。在它试图越界的那一刻就拦住，比事后发现再打补丁要有效得多。这就是 Harness 的思路——不是更好的提示，是系统强制执行的约束。

## 核心设计思路

想清楚这些之后，我开始设计自己的 Harness。先从三个遇到的最核心问题开始：

**AI 能访问哪些文件？** 我的项目里，敏感文件就几种：`.env`（环境变量）、`*.pem`（密钥文件）、`credentials.json`（第三方凭证）。这几种必须拦截。

**AI 在什么时候最容易越界？** 刚启动会话时最危险——Claude 不了解项目上下文，容易在不该操作的地方动手。其次是改完代码之后，它倾向于"顺手"修复旁边看起来不顺眼的东西，但 AI 顺手修复的那部分根本不在这次任务范围内。

**AI 的产出需要满足什么条件才能接受？** 就三个条件：没有硬编码凭证、没有越界访问、日志输出规范。这三条必须进行自动化检查，不能靠肉眼看。

把这三个问题的答案梳理清楚，Harness 系统的骨架就有了——不能靠 AI 的自觉，而是要靠系统来强制约束。

## 四层架构概览

搭建一套在 Claude Code 中最小可用的 Harness 系统，只需要实现下面的四个层面：

- **约束层**：两份上下文文件，定义 AI 的行为边界，告诉它什么该做什么不该做。
- **工具层**：权限配置，控制 AI 能调用什么工具、不能调用什么工具。
- **中间件层**：三层拦截器，分别在工具调用前、工具调用后、会话结束时触发，处理不同的安全问题。
- **编排层**：规范先行的开发流程，让 AI 在动手之前先确认理解是否正确。

不是说只有上面这四层，而是说这四层是必备的——少任何一层，系统就有明显的缺口。

核心原则只有一条：**不是靠 AI 自觉，是靠系统强制。**

## 第一层：约束层——通过两份文件定义 AI 的行为边界

最底层是上下文文件。Claude Code 每次启动时必然会读取这两个文件，它们是整个 Harness 系统的基石。

### CLAUDE.md：项目总规范

第一份叫 `CLAUDE.md`，放在项目根目录，告诉 AI 这个项目是干什么的、谁在里面扮演什么角色：

```markdown
# 项目概况

这是一个提供 RESTful API 的 Node.js 后端服务。
技术栈：Express + PostgreSQL + Redis。

## 团队协作方式

- 我（人类）：产品决策，代码审查，最终上线
- 你（AI）：主力开发，响应需求实现

## 当前阶段

MVP 开发中，预计 2 周后首版发布。

## 工作约定

1. 方案确认后再动手，不要边想边写
2. 改动超过 20 行必须主动告知我
3. 凭证相关操作必须停下来等我确认
```

### ARCHITECTURE.md：不可违反的铁律

第二份叫 `ARCHITECTURE.md`，里面写的是绝对不允许 AI 违反的规则：

```markdown
# 架构铁律（不可违反）

## 凭证铁律

- 绝对不读取 `.env` 文件内容
- 绝对不将任何 Key、Token、密码写入代码或注释
- 所有外部凭证必须通过环境变量注入，代码中只引用 `process.env.XXX`

## 访问边界

- 禁止对 `src/migrations/` 目录执行 Write/Edit 操作
- 禁止修改 `.gitignore` 文件
- 禁止对 `node_modules/` 执行任何操作

## 代码质量

- 所有 API 路由必须有输入校验
- 错误必须返回结构化 JSON，不允许裸字符串
- console.log 只用于开发调试，提交前必须替换为日志库
```

这两份文件是刻在系统里的约束，不是给 AI 看的建议。AI 读不到是我的失职，读到了还违反，那就是它的责任。

## 第二层：工具层——按角色给权限，最小权限原则

Claude Code 的权限由 `settings.local.json` 控制。我在这里定义了一套权限组合：

```json
{
  "permissions": {
    "allow": ["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
    "deny": ["NotebookEdit", "WebFetch"],
    "automaticToolApproval": false
  }
}
```

光配置权限不够。有些权限（如 Bash）是双刃剑，AI 可能用它执行危险命令。我在拦截器里进一步细化了对命令的拦截逻辑。

## 第三层：中间件层——三层拦截器，解决三个关键问题

这是 Harness 系统的核心。三层拦截器，分别在工具调用前、工具调用后，会话结束时触发。

### 拦截器 1：工具调用前拦截——把不该碰的拦住

AI 每次调用工具前都会触发这个拦截器。用它拦截对敏感文件和禁止目录的操作：

```python
#!/usr/bin/env python3
# hooks/pre-tool-guard.py

import json
import re
import sys

SENSITIVE_PATTERNS = [
    r'\.env$',
    r'\.pem$',
    r'_key$',
    r'id_rsa',
    r'credentials\.json$',
    r'\.p12$',
]

BLOCKED_DIRS = [
    'src/migrations',
    '.git',
    'node_modules/',
]

def check_path(path: str) -> tuple[bool, str]:
    """检查路径是否命中敏感规则。返回 (blocked, reason)"""
    if not path:
        return False, ""

    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, path, re.IGNORECASE):
            return True, f"敏感文件模式: {pattern}"

    for blocked in BLOCKED_DIRS:
        if blocked in path:
            return True, f"禁止目录: {blocked}"

    return False, ""

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)

        payload = json.loads(raw)
        tool = payload.get("tool", "")
        path = payload.get("path", "") or payload.get("command", "")

        if tool in ("Read", "Write", "Edit", "Bash"):
            blocked, reason = check_path(path)
            if blocked:
                print(f"\n[Harness Guard] BLOCKED: {tool} on {path}")
                print(f"[Harness Guard] 原因: {reason}")
                print("[Harness Guard] 如需解除限制，请联系项目管理员。\n")
                sys.exit(1)

    except Exception as e:
        print(f"[Harness Guard] 检查异常: {e}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

测试结果：

```bash
# 测试：Claude 试图读取 .env 文件
echo '{"tool": "Read", "path": "/project/.env"}' | python3 pre-tool-guard.py
# 输出：[Harness Guard] BLOCKED: Read on /project/.env
# 退出码：1

# 测试：Claude 试图编辑 migrations 目录
echo '{"tool": "Edit", "path": "/project/src/migrations/001_add_users.sql"}' \
  | python3 pre-tool-guard.py
# 输出：[Harness Guard] BLOCKED: Edit on ...src/migrations/...
# 退出码：1

# 测试：正常文件操作
echo '{"tool": "Read", "path": "/project/src/controllers/user.js"}' \
  | python3 pre-tool-guard.py
# 退出码：0
```

注册方式，在 `settings.local.json` 里配置：

```json
{
  "hooks": {
    "PreToolUse": {
      "Read": "python3 /path/to/hooks/pre-tool-guard.py",
      "Write": "python3 /path/to/hooks/pre-tool-guard.py",
      "Edit": "python3 /path/to/hooks/pre-tool-guard.py",
      "Bash": "python3 /path/to/hooks/pre-tool-guard.py"
    }
  }
}
```

### 拦截器 2：工具调用后审查——检测输出中的敏感信息

这道拦截器不阻断操作，但会扫描 AI 的 Bash 输出，检测是否包含泄露的凭证信息：

```python
#!/usr/bin/env python3
# hooks/post-output-guard.py

import json
import re
import sys

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?[\w\-]{16,}',
     "API/密钥泄露"),
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "私钥泄露"),
    (r'password\s*[:=]\s*["\'][^"\']{6,}["\']', "密码硬编码"),
]

def scan_output(output: str) -> list[str]:
    violations = []
    for pattern, label in SECRET_PATTERNS:
        if re.search(pattern, output):
            violations.append(label)
    return violations

def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)

        payload = json.loads(raw)
        tool_name = payload.get("tool", "")
        output = payload.get("output", {})

        if tool_name not in ("Bash", "Write"):
            sys.exit(0)

        output_text = ""
        if isinstance(output, dict):
            output_text = output.get("stdout", "") + str(output.get("stderr", ""))
        elif isinstance(output, str):
            output_text = output

        violations = scan_output(output_text)
        if violations:
            print(f"\n[Harness Output Guard] 检测到敏感信息: {', '.join(violations)}")
            print("[Harness Output Guard] 请审查输出内容，确保无误。\n")

    except Exception as e:
        print(f"[Harness Output Guard] 扫描异常: {e}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

注册方式：

```json
{
  "hooks": {
    "PostToolUse": {
      "Bash": "python3 /path/to/hooks/post-output-guard.py"
    }
  }
}
```

这里我选择只警告、不阻断，因为误报率比预期高——Claude 的 Bash 输出里有时候恰好匹配变量名 `api_key`，直接阻断会影响正常流程。

### 拦截器 3：会话结束拦截——自动生成工作摘要

这是最容易被忽略的一项内容。我设计了一个会话结束拦截器，在 AI 完成工作时自动生成一份结构化的工作记录：

```bash
#!/bin/bash
# hooks/session-summary.sh

SESSION_DIR="$HOME/.claude/sessions/$(date +%Y-%m-%d)"
mkdir -p "$SESSION_DIR"

SESSION_FILE="$SESSION_DIR/summary-$(date +%H%M%S).md"

{
    echo "# 会话摘要 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "## 项目"
    echo "$(pwd)"
    echo ""
    echo "## 变更文件"
    git diff --name-only --diff-filter=ACMR 2>/dev/null \
      || echo "（非git仓库或无变更）"
    echo ""
    echo "## 新增文件"
    git ls-files --others --exclude-standard 2>/dev/null \
      || echo "（无新文件）"
    echo ""
    echo "## 拦截记录"
    grep -r "BLOCKED\|Harness" "$HOME/.claude/logs/" 2>/dev/null \
      | tail -10 || echo "无"
    echo ""
} > "$SESSION_FILE"

echo "[Harness] 会话摘要已生成: $SESSION_FILE"
```

以上三层拦截器，各司其职：工具调用前拦截是不让 AI 碰到不该碰的东西；工具调用后审查是检测输出中的敏感信息泄露；会话结束时拦截是每次 AI 离开后留下可追溯的痕迹。

## 第四层：编排层——规范先行的开发流程

三层拦截器解决了"AI 不越界"的问题。但光不越界还不够——AI 经常在错误的理解上做正确的事。

为此我引入了一套规范先行的开发流程，让 AI 在动手之前先确认理解是否正确：

```
需求进来 → /追问（追问澄清）→ /固化（固化规范）→ /实现（执行）→ /验证（逐条检查）
```

### /追问：挖掘隐含假设

在动手之前，先把需求里的隐含假设全部挖出来。

比如我说"给用户模块加上注册功能"，AI 会追问：

- 密码强度规则是什么？最小几位？必须包含特殊字符吗？
- 邮件验证是指注册时发送验证链接，还是可选操作？
- 注册后直接登录，还是需要人工审核？
- 一个邮箱是否允许重复注册？

### /固化：形成合约

我把答案补全，AI 整理成一份规范：

```markdown
# 规范：用户注册功能 v1.0

## 功能描述

支持邮箱注册，邮件验证后才能登录。

## 详细规则

1. 密码：最小8位，必须包含数字和字母
2. 邮件验证：注册后发送验证链接，24小时内有效
3. 登录：验证通过前禁止登录，返回 401 + {"error": "email_not_verified"}
4. 重复注册：已注册邮箱返回 409 + {"error": "email_already_registered"}

## API 设计

- POST /api/auth/register → {email, password} → {message, user_id}
- POST /api/auth/verify → {token} → {success, token}

## 验收标准

- [ ] 正常注册流程完整
- [ ] 密码强度校验生效
- [ ] 重复注册被拒绝
- [ ] 所有错误返回结构化 JSON
```

这份规范经过我确认之后，AI 才会开始实现。实现完成后，AI 对照规范逐条自检是否满足。

**规范是 AI 和人共同签署的合约。** 在此之前，不动手。

## CI/CD 门禁：Git 合并前的最后一道防线

通过实现上面的四层架构，已经可以实现一套适用于 Claude Code 的最小可用的 Harness 系统，但我不希望有问题的代码绕过 Harness 系统直接进入主干，为此我在 Git 层面又加了一道门禁，作为代码合并前的最后一道防线。

```bash
#!/bin/bash
# .git/hooks/pre-commit.d/harness-gate.sh

set -e

echo "[Harness Gate] 开始检查..."

# 1. 凭证扫描
if grep -rEn "(api[_-]?key|secret[_-]?key|password\s*=)" \
    --include="*.js" --include="*.ts" --include="*.py" \
    --include="*.md" --include="*.json" \
    -e "-----BEGIN.*PRIVATE KEY-----" \
    . 2>/dev/null | grep -v "node_modules" | grep -v ".git"; then
    echo "[Harness Gate] 凭证扫描未通过"
    echo "请使用环境变量或 .env.example 管理凭证"
    exit 1
fi

# 2. migrations 目录变更拦截
CHANGED_FILES=$(git diff --cached --name-only)
if echo "$CHANGED_FILES" | grep -q "src/migrations/"; then
    echo "[Harness Gate] 检测到 migrations 目录变更，需人工审查"
    exit 1
fi

echo "[Harness Gate] 门禁通过"
exit 0
```

## 踩过的两个坑

### 坑 1：工具调用后审查的误报问题

一开始，我让这道拦截器检测所有包含 `password` 字样的输出。结果 AI 执行 `grep -r "password" ./src` 做代码审查时，输出里每个匹配行都被误判为"密码泄露"，然后阻断操作。

后来我把检测规则调紧了：不再检测变量名，只检测真正的密钥格式（16 位以上的字母数字组合前面带 `=` 或 `:` 的）。误报率降下来了。

### 坑 2：规范流程用在小需求上太重

我发现 /追问 → /固化 → /验证 这套流程，用在小需求上反而降低效率。一个两句话能说清楚的需求，让 AI 完整走一遍规范流程，做的事情比直接实现还多。

现在的做法是：简单需求直接实现，遇到复杂需求（涉及多个模块、有状态依赖、需要权衡方案）才启用这套流程。

**流程是为复杂度服务的，不是必须遵守的教条。**

## 实际效果——用了两个月后的感受

我没有对数据进行精确的量化对比，只说感受层面的变化。

之前最让我头疼的两件事：凭证不小心泄露到代码里（Claude 有时候会把 Bash 输出的中间结果直接写进注释）、越界修改 migrations 目录的文件（Claude Code 觉得这是"顺手的事"）。引入了 Harness 系统之后，这两类问题基本消失，因为 AI 在动手之前就被拦住了。

代码返工率有明显下降。之前 AI 按照自己理解实现功能，经常在 code review 时发现理解偏差，然后重写。现在多了规范确认那一步，理解偏差在动手之前就被纠正了。

对话轮次也少了。之前一个任务要来回改 3、4 轮，现在基本 1-2 轮就定。

**不是因为 AI 变聪明了，是因为它在动手之前先确认理解，理解对了，实现自然就对了。**

## 组件清单

上面这套 Claude Code Harness 系统（约束层→工具层→中间件层→编排层）加上 Git 门禁，共同构成一套最小可用的 Harness。以下是各层对应的具体组件：

| 层级 | 组件 | 作用 |
| --- | --- | --- |
| 约束层 | CLAUDE.md | 项目总规范 |
| 约束层 | ARCHITECTURE.md | 架构铁律 |
| 工具层 | settings.local.json | 权限配置 |
| 中间件层 | pre-tool-guard.py | 事前拦截敏感文件操作 |
| 中间件层 | post-output-guard.py | 事后检测输出敏感信息 |
| 中间件层 | session-summary.sh | 会话结束生成工作摘要 |
| 编排层 | /追问 | 追问需求，挖掘隐含假设 |
| 编排层 | /固化 | 固化规范，形成合约 |
| 编排层 | /实现 | 按规范执行实现 |
| 编排层 | /验证 | 对照规范逐条验证 |
| CI/CD 层 | harness-gate.sh | Git 合并前最后门禁 |

## 总结

搭这套系统，我花了大约 10 个小时一次性投入。之后每个新项目，Clone 下来改一下上下文文件内容，5 分钟完成基础配置。

真正难的不是写代码，是想清楚你的边界在哪里。你允许 AI 做什么，不允许它做什么，什么情况下让它停下来等你确认——这些问题在你写代码之前就得有答案。代码只是把你做的决定翻译成系统可执行的规则。

Claude Code 的 Harness 四层架构（约束层→工具层→中间件层→编排层）加上 Git 门禁，构成了一套完整的最小可用系统。这个系统不是一次性建成的，它是和你的项目一起长大的。
