---
title: Anthropic 工程师力推 HTML 取代 Markdown
tags:
  - knowledgebase/source
  - AI/industry
  - AI/workflow
date: 2026-05-13
sources:
  - "[[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议]]"
aliases:
  - HTML vs Markdown
  - HTML取代Markdown
---

# Anthropic 工程师力推 HTML 取代 Markdown

## 元信息

- **原始文档**：[[AI/行业动态/Anthropic工程师力推HTML取代Markdown-Karpathy附议]]
- **领域**：AI 行业动态
- **摄入日期**：2026-05-13
- **原始来源**：Anthropic 工程师 Thariq 的 X 长文 + Karpathy 回应

## 摘要

Anthropic 工程师 Thariq 发文主张在 AI 工作流中用 HTML 全面取代 Markdown 作为输出格式，Karpathy 公开附议。核心论点：当 AI 成为主要的内容生产者时，为"方便人类手写"而设计的 Markdown 已不再是最优选择，HTML 在信息密度、可读性、分享性、交互性上全面碾压。

## 关键知识点

1. **HTML 五大优势**：信息密度碾压（SVG/CSS/JS/Canvas）、可读性（标签页/折叠/导航）、零成本分享（S3+链接）、双向交互（滑块/拖拽/实时预览）、开发体验更快乐
2. **五大使用场景**：规划探索（可视化方案对比）、代码审查（diff 视图+行内批注）、设计原型、报告研究（整合多源信息）、一次性编辑器（用完即弃的专用工具）
3. **代价与权衡**：Token 成本增加约 67%（6600→11000 美元/年/425 文件）；生成时间 2-4 倍；版本控制 diff 困难，暂无完美解决方案
4. **Karpathy 进化路线**：纯文本 → Markdown → HTML → 扩散模型生成的交互式视频；输入端也需进化（指向式交互）
5. **哥白尼式智能观**：人类不再是唯一的内容创作者和消费者，以人类为中心设计的工具（Markdown/GUI）正被重新审视；陶哲轩论断——"人类智能不是宇宙中心，存在截然不同的智能形态"

## 涉及的概念与实体

- [[KnowledgeBase/entities/Claude-Code|Claude Code]]：Thariq 的 HTML 工作流核心工具
- [[KnowledgeBase/entities/Obsidian|Obsidian]]：Markdown 生态的代表性工具，本文观点对其有直接影响

## 值得注意

- **反面观点同样重要**：评论区有人算账——HTML 每年多花 5000 美元纯粹用于模型无法利用的标签冗余；有人调侃这是 Anthropic 提升 usage 的"阴招"
- **与本库定位的张力**：本知识库基于 Obsidian+Markdown 构建（参见 [[AI/Obsidian/obsidian-claude-code-AI知识库完整指南|AI知识库完整指南]]），Thariq 的观点直接挑战了 Markdown 作为知识载体的前提。但两者并不完全矛盾——Markdown 仍适合作为**存储和编辑格式**，HTML 更适合作为**展示和交互格式**，二者可以互补
- **"一次性编辑器"概念**：这是文中最具实操价值的点——不追求可复用工具，而是让 AI 为当前任务定制一个专用 HTML 页面，用完即弃。这代表了一种新的"工具即消耗品"思维
