---
title: AI-Animation-Skill - HTML科普动画生成
tags:
  - AI
  - animation
  - html
  - openclaw
  - skill
aliases:
  - AI-Animation-Skill
  - 科普动画
---

# AI-Animation-Skill — HTML 科普动画生成

> 来源：[扔掉PPT，用这44个HTML动画模板，让AI帮你做科普视频](https://mp.weixin.qq.com/s/s53qdw1IvU4Ei77ebuKF9Q)
> 仓库：[Unclecheng-li/AI-Animation-Skill](https://github.com/Unclecheng-li/AI-Animation-Skill)
> 协议：MIT

---

## 项目简介

AI-Animation-Skill 是一套面向科普视频制作的 HTML 动画模板集，以 Skill 形式运行在 OpenClaw / WorkBuddy / QClaw 等 AI Agent 平台上。

核心思路：**输出物是单个 HTML 文件**——浏览器直接打开即可看到完整动画效果，F11 全屏 + 录屏即为视频。44 个模板全部是纯前端代码，零第三方框架依赖，最轻量的模板仅 331 行。

**传统科普视频链路**：写稿 → 做 PPT → 调动画 → 录屏 → 剪辑（每步不同工具）
**AI-Animation-Skill**：输入科普文本 → AI 自动选模板生成 HTML → 录屏完成

### 与主流 AI PPT 工具的核心区别

| 维度 | AI-Animation-Skill | Gamma | Beautiful.ai |
|------|---------------------|-------|--------------|
| 价格 | 免费（MIT 开源） | 免费版有限 / Plus $8/月 | 无免费版 / Pro $45/月 |
| 中文支持 | 原生（模板为中文内容设计） | 机翻痕迹明显 | 无中文支持 |
| 网络依赖 | 完全离线 | 必须联网 | 必须联网 |
| 输出格式 | 单 HTML 文件（直接录制） | PDF/PPTX/网页 | PDF/PPTX |
| 动画质量 | CSS 原生动画 + 3D Transform | 网页过渡效果 | 智能排版动画 |
| 可定制性 | 完全开源，代码随便改 | 有限 | 中等 |
| 适合场景 | 科普/教学/技术演示 | 通用演示 | 企业商务演示 |

---

## 44 个模板

### PPT Level2（26 个）— 核心资产

26 个模板分 9 个系列，每个系列针对特定内容类型优化：

| 系列 | 数量 | 适用场景 | 亮点 |
|------|------|---------|------|
| 系列 1 | 1 | 概念引入、对比 | VS 对比卡片 + SVG 流程图 |
| 系列 2 | 1 | 概念定义、层级结构 | 13 种动画，最多元化 |
| 系列 3 | 3 | 轻量/步骤/极简 | 3-3 模板仅 331 行代码 |
| 系列 4 | 3 | 案例/实验/代码 | 含代码雨动画效果 |
| 系列 5 | 4 | 警示/失败/危险 | 5-4 模板达 15 种动画 + 13 页 |
| 系列 6 | 4 | 护栏/架构/反馈 | 6-2 红绿 VS 对比（15 种动画） |
| 系列 7 | 4 | 追踪/上下文/Doom Loop | 7-2 模板达 17 种动画 |
| 系列 8 | 3 | 辩论/对比/融合 | 8-3 模板达 30 组 VS 对比 |
| 系列 9 | 3 | 总结/共识/精炼 | 9-3 模板仅 5 页，最精炼 |

覆盖科普视频常见内容结构：概念解释、案例展示、问题分析、方案对比、总结提炼。

### PPT 基础模板（4 个）

通用基础模板，Level2 不适用时的回退选项。推荐 PPT-Generate-3（视觉效果最好）。

### Animation 流程图模板（14 个）

将科普内容转化为平面 UI 风格的流程图动画。默认 RNN-3（分层卡片），特定技术概念有专用模板：

- **LSTM-1**：LSTM 三阶段门控机制
- **word2vec-1**：词向量语义身份证概念
- **GPU 模板**：计算节点架构展示

---

## 安装与使用

### 前置条件

需要 AI Agent 环境。支持平台：

| 平台 | 说明 |
|------|------|
| **OpenClaw** | 开源社区版，可通过 ClawHub 一键安装 |
| **WorkBuddy** | 腾讯版 |
| **QClaw** | — |
| **摩尔线程 AIBOOK** | 国产 GPU 平台 |

### 安装（以 WorkBuddy 为例）

```bash
# 1. 下载源码
git clone https://github.com/Unclecheng-li/AI-Animation-Skill.git

# 2. 复制到 skills 目录
cp -r AI-Animation-Skill ~/.workbuddy/skills/

# 3. 重启 WorkBuddy
```

OpenClaw 用户可通过 ClawHub 一键安装，无需手动操作。

### 生成科普动画

**模式一：PPT 演示生成** — 输入科普内容，告诉 Agent"帮我生成 PPT"。AI 自动完成：分析内容类型 → 从 26 个 Level2 模板中选择最合适的 → 生成完整动画 HTML。

**模式二：流程图生成** — 在模式一完成后，说"生成流程图"，AI 从 14 个 Animation 模板中选择合适的重构。

两种模式可组合：先 PPT 版用于完整展示，再流程图版用于快速回顾。

### 从 HTML 到视频

HTML 文件浏览器打开 → F11 全屏 → 录屏（OBS / Win+G / 浏览器插件）。动画是确定性的，每次打开效果完全一致。

---

## 边界与局限

- **不适合品牌演示**：风格偏技术科普简洁风，无企业级品牌管控
- **不支持实时协作**：单人工作流，无多人同时编辑
- **依赖 AI Agent 环境**：不是独立软件，需配合 OpenClaw / WorkBuddy 等使用
- **模板有限**：44 个模板覆盖科普场景，营销/品牌/广告场景模板不够

---

## 与 PPT Master 的定位对比

| 维度 | AI-Animation-Skill | [[AI/AI-视觉/AI做PPT-ppt-master|PPT Master]] |
|------|---------------------|------------|
| 输出格式 | HTML 文件（动画） | 原生 PPTX（可编辑） |
| 目标场景 | 科普视频录制 | 专业演示文稿 |
| 运行平台 | OpenClaw / WorkBuddy | Claude Code / Cursor / VS Code |
| 可编辑性 | 修改 HTML 代码 | PowerPoint 原生编辑 |
| 中文优化 | 原生中文设计 | 通用多语言 |
| 适合人群 | 科普 UP 主 / 教育工作者 | 企业 / 咨询 / 专业演示 |
