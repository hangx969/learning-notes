---
title: AI做PPT - ppt-master
tags:
  - AI
  - ppt
  - prompt-engineering
aliases:
  - ppt-master
  - AI PPT
---

# AI做PPT - ppt-master

> 来源：[这才是AI做ppt的正确姿势！](https://mp.weixin.qq.com/s/uJXM0G3frzTQ6tbTQwxY-Q)
> 仓库：[hugohe3/ppt-master](https://github.com/hugohe3/ppt-master)
> 协议：MIT（可商用、可二次开发）

---

## 项目简介

PPT Master 是一个开源的 AI 驱动演示文稿生成工具（4 个月 6200+ Star）。

核心思路：**先用 AI 生成 SVG，再通过自研转换引擎把 SVG 逐元素翻译成 DrawingML（PowerPoint 底层矢量格式）**。输出的 PPTX 中每个文本框、渐变、阴影、发光效果、箭头标记、图片裁剪路径都是原生 PowerPoint 形状——能编辑、能拖动、能改颜色，就像你自己一个个画出来的一样。

### 与现有 AI PPT 工具的核心区别

| 痛点 | 现有工具（Gamma / Beautiful.ai / Copilot） | PPT Master |
|------|-------------------------------------------|------------|
| 导出质量 | 输出图片或 Web 截图，字体替换、图表移位、格式全乱 | SVG → DrawingML 原生转换，每个元素可编辑 |
| 数据隐私 | 文件必须上传到第三方服务器 | 除 AI 通信外，全流程本地运行 |
| 费用 | 月费 $8~$40，锁定在平台上 | 工具本身免费，仅需 AI 编辑器费用（VS Code Copilot 低至 $0.08/份） |
| 可编辑性 | 导出后改不了、调不好 | 输出两个文件：原生形状版 `.pptx`（编辑用）+ `_svg.pptx` 快照版（视觉参考） |

---

## 核心特性

- **原生 PPTX 导出**：v2.3.0 起默认使用 DrawingML 导出，文本框/渐变/阴影/发光/箭头/裁剪路径全部原生转换
- **多格式输出**：16:9 / 4:3 演示文稿、小红书 (3:4)、朋友圈 (1:1)、Story (9:16) 等 10+ 种画布格式
- **三种设计风格**：通用灵活 / 一般咨询 / 顶级咨询（MBB 级）
- **丰富内置资源**：20 个布局模板、52 个可视化模板、6700+ 矢量图标
- **14 个图像生成后端**（每个后端单独配 API Key，切换时只改 `IMAGE_BACKEND`）
- **公司模板支持**：自动提取背景、Logo、主题色、字体，在模板基础上生成 PPT
- **遵循 CRAP 设计原则**：对比（Contrast）、重复（Repetition）、对齐（Alignment）、亲密性（Proximity）
- **多编辑器支持**：Claude Code、Cursor、VS Code Copilot 均可用；Claude、GPT、Gemini、Kimi 等模型均支持

---

## 四角色协作工作流

PPT Master 不是简单地把文档丢给大模型，而是设计了一套四角色协作的管道工作流：

```
Strategist（策略师）→ Image Generator（图片生成师）→ Executor（执行师）→ Optimizer（优化师）
```

| 角色 | 职责 | 说明 |
|------|------|------|
| **Strategist（策略师）** | 入口角色，分析内容、规划结构、确认视觉风格 | 产出完整的设计规范 |
| **Image Generator（图片生成师）** | 条件触发，负责配图 | 调用配置的图像生成后端 |
| **Executor（执行师）** | 按设计规范逐页生成 SVG | 三个变体对应三种风格 |
| **Optimizer CRAP（优化师）** | 可选，按 CRAP 原则迭代优化视觉质量 | 逐页审查优化 |

> [!note] 强制顺序生成
> 项目强制要求页面顺序生成，不允许并行。这是为了保证跨页面的视觉一致性——配色、字号、间距不会在翻页时突然跳变。

---

## 使用流程

### 环境准备

```bash
# 需要 Python 3.10+
git clone https://github.com/hugohe3/ppt-master.git
cd ppt-master
pip install -r requirements.txt
# 配置大模型 API Key
```

### 生成 PPT

1. 将源文件（PDF、DOCX 等）放到 `projects/` 目录下
2. 用 VS Code / Cursor 等 AI 编辑器打开项目，在聊天面板中指定文件路径：

```
Please create a PPT from projects/my-doc/sources/report.pdf
```

3. **Strategist 确认**：AI 先确认设计规范——模板、画幅、页数等
4. **Executor 生成**：确认后自动逐页生成 SVG
5. **导出**：生成的 PPTX 保存到 `exports/` 目录

> [!tip] 公司模板
> 如果有公司模板，放到项目目录中即可。PPT Master 会自动提取背景、Logo、主题色、字体，在模板基础上生成 PPT，导出后风格完全一致。

---

## 案例展示

官方提供了 15 个案例项目，覆盖多种风格，总共 229 页，均可在线预览：

- 像素复古游戏风的 Git 入门 PPT（霓虹绿 + 赛博粉 + 电光蓝 + 深空黑）
- 麦肯锡风格的客户忠诚度分析
- Google 品牌风格的年度汇报
- 禅意水墨风的金刚经研究
- ……

所有案例导出的 PPTX 都是原生可编辑的。

---

## 注意事项

- **Windows 兼容性**仍在打磨中，安装可能有坑，参考项目安装指南
- 需要 AI 编辑器的 **API 额度**：VS Code Copilot 最低 $0.08/份，Claude / GPT 费用更高
- 项目仍在快速迭代中

---

## 核心理念

> AI 生成的演示文稿，不应该是一个终点，而应该是一个起点——你可以在此基础上继续修改、调整、完善，就像你自己做的一样。

作者本身是金融背景（CPA、CPV、投资咨询工程师），每天审阅和编辑数百张幻灯片。做这个项目的起因：**现有 AI PPT 工具导出的都是图片，不是可编辑形状，这在专业场景下完全不可接受。**
