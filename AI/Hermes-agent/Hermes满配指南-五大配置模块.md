---
title: Hermes 满配指南 — 五大配置模块
tags:
  - ai/hermes-agent
  - ai/agent-config
date: 2026-01-14
source: "https://mp.weixin.qq.com/s/-1CQxvdc1bDMrPzIHFPpbA"
---

# Hermes 满配指南 — 五大配置模块

裸装 Hermes 只是普通的 AI 对话助手，配置完以下模块后变成真正的 AI Agent——具备长期记忆、全网信息抓取、语音+图片生成、Token 精细管控等能力。

## 配置模块总览

| 模块 | 能力 | 核心工具 |
|------|------|----------|
| 身份与记忆 | 人格定义 + 持久记忆 | SOUL.md + Hindsight |
| 感知能力 | 网页抓取 | Jina Reader / Crawl4AI / Scrapling / CamoFox |
| 搜索与文档 | 搜索 + 格式转换 | Tavily / DuckDuckGo / Pandoc / Marker |
| 表达能力 | 语音 + 图片生成 | Whisper / Edge TTS / Fal.ai / FLUX Skill |
| 效率与成本 | Token 监控 + 优化 | Tokscale / hermes-hudui / RTK / Self-evolution |

---

## 一、身份与记忆：SOUL.md + Hindsight

### 1.1 SOUL.md 人格定义

使用 **agency-agents-zh** 中文角色模板库，包含 211 个中文角色模板 + 46 个中国市场原创智能体。

- GitHub：https://github.com/jnMetaCode/agency-agents-zh
- 角色按 18 个部门分类（工程、设计、营销、产品、游戏、安全、金融、HR 等）
- 每个角色为独立 `.md` 文件，包含完整人设、专业流程和可交付成果
- 使用时直接告诉 Hermes 要激活哪个角色即可

### 1.2 Hindsight 替换内置 MEMORY

|  | 内置 MEMORY | Hindsight |
|---|---|---|
| **写入机制** | 只有 Hermes 认为重要时才写入 | 自动从每轮对话提取实体、事实、关系、时间戳 |
| **容量上限** | ≈ 2200 字符（硬上限） | 无硬上限 |
| **知识组织** | 线性文本 | 知识图谱 |

**安装步骤：**

```bash
# 1. 运行 setup wizard
hermes memory setup

# 2. 选择 hindsight，向导自动安装依赖

# 3. 获取 API Key（Cloud 模式）
# 打开 https://ui.hindsight.vectorize.io/connect 注册，生成 API Key（免费额度足够）

# 4. 验证
hermes memory status
# 应看到 Hindsight 已激活，显示 bank_id、auto-recall、auto-retain 等状态
```

---

## 二、感知能力：内容抓取工具

| 工具 | 用途 | 集成方式 |
|------|------|----------|
| **Jina Reader** | 单页抓取 | Skill 或直接调用 |
| **Crawl4AI** | 批量深度抓取 | Skill 或直接调用 |
| **Scrapling** | 反爬绕过 | 官方原生支持，`hermes tools + pip` 启用 |
| **CamoFox** | 隐身浏览器 | 官方可选技能，`hermes tools + pip` 启用 |

Scrapling 和 CamoFox 为官方原生/可选技能，直接通过 `hermes tools + pip` 启用。Jina Reader 和 Crawl4AI 无内置技能，推荐用 Skill 方式集成。

---

## 三、搜索与文档处理

| 工具 | 用途 | 说明 |
|------|------|------|
| **Tavily** | AI 专用搜索（主力） | 1000 次/月免费 |
| **DuckDuckGo** | 零成本兜底搜索 | 无 API Key 需求 |
| **Pandoc** | 万能格式转换器 | 任意格式互转 |
| **Marker** | PDF 转 Markdown 增强 | 高精度 PDF 文件提取 |

配置后搜索策略：Tavily（主力）+ DuckDuckGo（兜底）。

---

## 四、表达能力：语音与图片

| 工具 | 用途 | 说明 |
|------|------|------|
| **Whisper** | 语音识别 | 支持 99+ 语言 |
| **Edge TTS** | 语音合成 | 免费使用 |
| **Fal.ai** | 图片生成 | 云端 API |
| **FLUX Skill** | 高质量出图 | Skill 集成 |

---

## 五、效率与成本：Token 精细管控

### 5.1 Tokscale — Token 全局监控

专为 Hermes 等 AI 编码助手设计的 CLI 监控工具，实时查看全局 Token/成本（TUI 可视化 + JSON 导出）。

```bash
# 安装
npx tokscale@latest
# 或用 Bun
bunx tokscale@latest
```

```bash
# 使用
tokscale                  # 交互式 TUI（全局所有平台 Token 消耗总览）
tokscale --hermes         # 只看 Hermes Agent 的全局消耗
tokscale --hermes --week  # 过去7天 Hermes Token 趋势
tokscale --json           # JSON 导出全局数据（可脚本监控）
tokscale models           # 按模型统计 Token（含 Hermes）
```

### 5.2 hermes-hudui — Web 仪表盘

支持按模型/组件/会话深度拆解 Token 成本、实时 WebSocket 更新。

```bash
git clone https://github.com/joeynyc/hermes-hudui.git
cd hermes-hudui
./install.sh          # 自动安装 Python + Node 依赖
hermes-hudui          # 启动
# 访问 http://localhost:3001（支持手机端）
```

### 5.3 RTK（Rust Token Killer）

Rust 编写的零依赖 CLI 代理，智能过滤/压缩 `ls`、`git status`、`cargo test` 等终端输出，直接减少 60-90% Token。

```bash
# Homebrew
brew install rtk

# 或一键脚本（Linux/macOS/Windows WSL）
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh

# 集成到 Hermes（自动重写终端命令）
rtk init -g       # 安装全局 Hook + RTK.md
```

### 5.4 Hermes-agent-self-evolution

用遗传算法自动优化 Agent 提示词和行为（DSPy + GEPA 遗传-帕累托进化算法），能自动优化 Skill、System Prompt、工具描述。

```bash
git clone https://github.com/NousResearch/hermes-agent-self-evolution.git
cd hermes-agent-self-evolution
pip install -e ".[dev]"
```

### 5.5 Skill 批量扩展

一次性安装 wondelai 的 380 个跨平台 Skill。

---

## 生态入口

| 资源                       | 说明          |
| ------------------------ | ----------- |
| **awesome-hermes-agent** | 一站式资源汇总     |
| **hermes-ecosystem**     | 80+ 工具可视化地图 |
