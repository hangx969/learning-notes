---
title: RAG PDF 解析难点与主流方案 — 来源摘要
tags:
  - knowledgebase/source
  - AI/RAG
date: 2026-05-13
sources:
  - "[[AI/RAG-PDF解析难点与主流方案]]"
aliases:
  - RAG PDF 摘要
---

# RAG PDF 解析难点与主流方案 — 来源摘要

## 元信息
- **原始文档**：[[AI/RAG-PDF解析难点与主流方案]]
- **领域**：AI / RAG
- **摄入日期**：2026-05-13

## 摘要

系统讲解 PDF 格式为何是 RAG 解析中最大的难题——PDF 本质是页面描述语言（无段落/标题/表格语义概念），解析器需要从坐标、字形、线段中推断语义结构。覆盖三大解析技术体系（原生文本提取/OCR/VLM）、四类工具方案（轻量库/AI 增强框架/商业 API/VLM 直接调用），以及 7 个常见生产问题的处理方案。

## 关键知识点

1. **PDF 格式本质**：渲染优先的页面描述语言，无显式阅读顺序、无表格数据结构、字体编码可能缺失，与 DOCX（语义优先）和 HTML（标签语义）根本不同
2. **三大解析路线**：原生文本提取（PyMuPDF/pdfplumber，最快但受 PDF 格式局限）→ OCR（Tesseract/PaddleOCR，处理扫描件）→ VLM（GPT-4o/Gemini 2.5/Qwen2.5-VL，绕过所有中间步骤但成本高）
3. **AI 增强开源框架**：Docling（DocLayNet 版面分析 + TableFormer 表格恢复 + DoclingDocument 文档树）、MinerU（PaddleOCR + 中文/LaTeX 强项）、Marker-PDF（多格式统一入口）
4. **多栏混排**：版面分析模型（DocLayNet/PP-StructureV2）先划分独立文本区域再按区域顺序拼接
5. **跨页表格**：需在解析阶段检测未结束表格并合并下一页行（Docling/MinerU 内置此逻辑）
6. **标题层级分块**：为每个 chunk 构建文档层级完整路径作元数据前缀；父子 chunk 策略（小 chunk 检索、大 chunk 生成）
7. **页眉页脚污染**：位置过滤（y 坐标 top/bottom 8%）+ 跨页重复检测（频率超阈值过滤）

## 涉及的概念与实体
- [[KnowledgeBase/sources/rag-agent-batch-summary|RAG-Agent 项目]]：RAG 知识库系统实现
- [[KnowledgeBase/concepts/Observability|可观测性]]：RAG 解析质量监控

## 值得注意
- "垃圾进，垃圾出"——无论检索策略和提示词多精致，如果 PDF 解析层质量差，RAG 整体效果天花板就在那里
- VLM 对比表：综合最强闭源 Gemini 2.5 Pro、开源 Qwen2.5-VL-72B、中文场景 Qwen2.5-VL/GLM-4.5V
- Docling 的 DoclingDocument 文档树设计使下游分块可按语义结构操作，是目前开源方案中结构化程度最高的
