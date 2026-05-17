---
title: "从 0 到 1 搭建 Confluence 内部 Wiki RAG 知识库增强检索系统：正文、评论、附件、图片全量打通"
source: "https://mp.weixin.qq.com/s/txOIukp2zL__nHbtALZnDA?scene=1&click_id=219"
author:
  - "[[认真做自己]]"
published:
created: 2026-05-17
description: "AI的增强，可以做很多之前想做但很难完成的事了，公司的wiki知识库积累了运维部门近五年的知识内容，年初的一"
tags:
  - "clippings"
---
认真做自己 *2026年5月13日 22:54*

AI的增强，可以做很多之前想做但很难完成的事了，公司的wiki知识库积累了运维部门近五年的知识内容，年初的一个KPI目标就想着如何结合达模型实现内部知识库RAG增强检索功能，这次真的可以实现了，先看效果：

![2026-05-13 203136.gif](https://mmbiz.qpic.cn/mmbiz_gif/WdiaYZu25Qiaic6hibKtCCTInqW7Sqy5BtlBnn3LbTzh0zJh7rJckvuXmn7T8NS717ZVu6NpIG4HuqOQkSCGSf7hvxtT5PyGb4cjZJnjwnBnTmw/640?from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

2026-05-13 203136.gif

不仅是正文内容，包括插入的图片，附件，评论等都可以在RAG检索中展示出来，整个方案的技术流程，我用gpt-image2生成了完整的流程图

![ChatGPT Image 2026年5月13日 20_32_14.png](https://mmbiz.qpic.cn/sz_mmbiz_png/WdiaYZu25QiaiceYpbfCuPia5KpVAiczHjiabFyPwRmM5Gyau06lCGjUL021Ymd3GwgMtAhQR6iciat0BkCdHicnswfqHkVKvM3bZajL2UBekwogvxpE/640?from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

为什么要做RAG知识库检索呢？结合传统wiki检索存在的问题：

1. 搜索关键词不准，很难找到真正需要的内容。
2. 页面里有大量代码宏、配置文件、附件、图片、架构图，普通文本检索覆盖不完整。
3. 知识分散在正文、评论、附件、图片和 draw.io 图里。
4. 新增或更新页面后，需要有增量同步机制。
5. 大模型回答时必须可溯源，不能胡编。

因此，我们设计了一套基于 Confluence + Qdrant + LiteLLM + FastAPI + Vue 的内部 Wiki RAG 知识库方案。

最终目标是：

```markdown
Confluence Wiki  ├── 页面正文  ├── 代码宏  ├── 页面评论  ├── 页面附件  ├── 普通图片  └── draw.io 架构图        ↓ 采集 / 清洗 / 解析 / 切分Qdrant 向量库        ↓ RAG 检索LiteLLM 网关 + 大模型        ↓FastAPI HTTP 服务        ↓Vue 前端问答页面
```

整体架构如下：

```markdown
┌──────────────────────────────┐│        Confluence Wiki        ││ 正文 / 评论 / 附件 / 图片 / 图 │└───────────────┬──────────────┘                │ REST API                ↓┌──────────────────────────────┐│          数据采集层            ││ fetch_one_page.py             ││ fetch_pages_tree.py           ││ build_one_full_doc.py         │└───────────────┬──────────────┘                ↓┌──────────────────────────────┐│        内容解析清洗层          ││ confluence_cleaner.py         ││ 附件解析 / 图片识别 / draw.io解析│└───────────────┬──────────────┘                ↓┌──────────────────────────────┐│          Chunk 构建层          ││ data/chunks/by_doc/*.jsonl    │└───────────────┬──────────────┘                ↓┌──────────────────────────────┐│          向量化入库层          ││ index_one_doc.py              ││ index_qdrant.py               ││ Embedding: bge-m3             ││ Vector DB: Qdrant             │└───────────────┬──────────────┘                ↓┌──────────────────────────────┐│           RAG 服务层           ││ rag_chat.py                   ││ web_app.py FastAPI            ││ LiteLLM Gateway               │└───────────────┬──────────────┘                ↓┌──────────────────────────────┐│            Vue 前端            ││ 问答 / 来源 / 图片预览 / 附件下载│└──────────────────────────────┘
```

技术选型：

| 模块 | 技术方案 |
| --- | --- |
| Wiki 来源 | Confluence Server / Data Center |
| 页面采集 | Confluence REST API |
| 文本清洗 | BeautifulSoup + 自定义 Confluence Storage Format 清洗 |
| 向量模型 | BAAI/bge-m3 |
| 向量数据库 | Qdrant |
| 大模型网关 | LiteLLM |
| 后端接口 | FastAPI + Uvicorn |
| 前端页面 | Vue 3 + Vite |
| PDF 解析 | pypdf |
| Word 解析 | python-docx |
| Excel 解析 | openpyxl |
| PPT 解析 | python-pptx |
| 图片理解 | LiteLLM 后接多模态模型 |
| 图片压缩 | Pillow |

**为什么不能只处理页面正文**

Confluence Wiki 的内容并不只是普通文本。

一个真实的内部 Wiki 页面中，可能同时包含：

```markdown
页面正文代码宏配置文件表格页面评论PDF 附件Word 附件Excel 附件PPT 附件普通图片draw.io 架构图
```

如果只处理正文，会丢掉大量关键信息。

例如一个 DNS 架构页面里：

- 正文中描述了 dnsdist、Bind9、PowerDNS 的功能；
- draw.io 图里展示了请求流量、响应流量、代理、出口和集群关系；
- 附件里可能有部署说明；
- 评论里可能有后续变更提醒。

因此最终方案要把不同来源统一处理成 RAG 可检索的 chunk。

**数据来源类型设计**

我们用source\_type区分不同来源

| 数据来源 | source\_type | 说明 |
| --- | --- | --- |
| 页面正文 | page | 普通正文、代码宏、配置文件、表格 |
| 页面评论 |
