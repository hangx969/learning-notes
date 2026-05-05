---
title: Obsidian 可视化 Skills — Excalidraw / Mermaid / Canvas
tags:
  - ai/obsidian
  - ai/skills
  - ai/visualization
date: 2026-01-14
source: "https://mp.weixin.qq.com/s/EbNkKTGkp2WnqJ0nKNBwmA"
---

# Obsidian 可视化 Skills — Excalidraw / Mermaid / Canvas

## 项目简介

**axton-obsidian-visual-skills** 是一个 GitHub 开源项目，通过 AI Skills 让大模型直接在 Obsidian 中生成**可编辑**的图表文件。

- GitHub 地址：https://github.com/axtonliu/axton-obsidian-visual-skills

核心思路：通过预设的 Markdown 提示词文件（Skills），让 AI 按照特定格式生成结构化 JSON 图表，而非静态图片——生成后可随时打开调整布局、修改文字、增删元素。

## 支持的三种图表格式

### 1. Excalidraw — 手绘风格

- **文件格式**：`.excalidraw.md`（JSON 结构）
- **特点**：视觉温暖的手绘美学风格，适合灵感记录和快速表达
- **Skill 名称**：`excalidraw-diagram`
- 对中文支持友好

### 2. Mermaid — 专业规范

- **文件格式**：Markdown 内嵌 Mermaid 代码块
- **特点**：专业规范的流程图风格，适合流程说明和技术文档
- **Skill 名称**：`mermaid-visualizer`

### 3. Canvas — 自由布局

- **文件格式**：`.canvas`（JSON 结构）
- **特点**：自由布局的无限画布，适合复杂网络和思维发散
- **Skill 名称**：`obsidian-canvas-creator`

> 三种格式底层都是结构化 JSON 代码，AI 可以直接生成，用户可以自由编辑。

## 安装配置

### 第一步：下载项目

```bash
git clone https://github.com/axtonliu/axton-obsidian-visual-skills.git
```

或直接在 GitHub 仓库页面点击「Code → Download ZIP」手动下载。

### 第二步：复制 Skills 到对应目录

将仓库中的三个 Skills 目录复制到 AI 工具的 skills 目录下：

```bash
# Claude Code
cp -r axton-obsidian-visual-skills/excalidraw-diagram ~/.claude/skills/
cp -r axton-obsidian-visual-skills/mermaid-visualizer ~/.claude/skills/
cp -r axton-obsidian-visual-skills/obsidian-canvas-creator ~/.claude/skills/

# Gemini CLI —— 将 .claude 换成 .gemini
# Codex     —— 将 .claude 换成 .codex
```

> Windows 用户需手动复制。注意 `.claude`、`.gemini`、`.codex` 为隐藏目录：
> - **macOS**：Finder 中按 `Cmd + Shift + .` 显示隐藏文件
> - **Windows**：文件资源管理器 → 查看 → 显示 → 勾选「隐藏的项目」

### 第三步：验证安装

在 Obsidian 目录下启动 AI 工具（`claude` / `gemini` / `codex`），输入：

```
/skills
```

确认 Skills 列表中出现三个新技能即安装成功。

## 使用方式

在终端中用自然语言描述需求即可。示例：

```
请帮我把好笔记的五个原则.md 这篇文章转换成 Obsidian Excalidraw，放在当前文件夹下
```

AI 会自动：读取笔记内容 → 理解结构 → 规划布局 → 生成 JSON 代码 → 保存为对应格式文件。过程中只需在请求文件读写权限时点击同意。

## 兼容性

| AI 工具 | 支持情况 |
|---------|---------|
| Claude Code | ✅ |
| Gemini CLI | ✅ |
| Codex | ✅ |

三个工具生成的图表风格略有不同，但均支持自由编辑。
