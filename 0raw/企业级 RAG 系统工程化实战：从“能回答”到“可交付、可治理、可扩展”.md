---
title: "企业级 RAG 系统工程化实战：从“能回答”到“可交付、可治理、可扩展”"
source: "https://mp.weixin.qq.com/s/veNPSKdeWxxEJ_1xe9Ym4g?scene=1&click_id=1901168201"
author:
  - "[[银河技术]]"
published:
created: 2026-06-28
description:
tags:
  - "clippings"
---
银河技术 Ray的银河技术 *2026年6月12日 22:54*

## 企业级 RAG 系统工程化实战：从“能回答”到“可交付、可治理、可扩展”

> 真正的企业级 RAG，不是把向量库、Embedding、LLM 串起来就结束了，而是要把检索质量、权限边界、索引生命周期、并发控制、成本治理、可观测与发布回滚统一纳入一套工程体系。

## 一、前言：企业真正缺的不是一个 RAG Demo，而是一条可运营的知识服务链路

过去两年，RAG 已经从概念验证走向大量业务落地。无论是内部知识问答、售后辅助、合同审阅、研发助手、运维排障还是客服 Copilot，背后的第一阶段几乎都离不开 RAG。

但企业在落地时很快会发现： **RAG 的难点从来不在“把答案生成出来”，而在“让系统持续、稳定、合规、低成本地生成可信答案”。**

很多团队第一次做 RAG，通常会经历下面几个阶段：

1. 1\. 先用 Python 脚本把 PDF 导入向量库，搭一个最小 Demo。
2. 2\. 接着发现召回不稳，同一个问题今天能答、明天不能答。
3. 3\. 再往后发现权限收不住，跨部门文档被错误召回。
4. 4\. 文档一多，重建索引耗时数小时，期间线上结果波动明显。
5. 5\. 并发一上来，Embedding、Rerank、LLM 三段链路互相放大，GPU 负载与 RT 一起飙升。
6. 6\. 最后发现真正要维护的已经不是“一个问答接口”，而是一套包含文档接入、索引构建、检索编排、生成治理、监控告警和发布回滚的复杂系统。

所以，企业级 RAG 的主线不应该是：

- • “我用了哪个框架”
- • “我接了哪个大模型”
- • “我能不能在 10 分钟内跑起来”

而应该是：

- • 如何保证答案基于授权范围内的知识
- • 如何让索引构建与在线查询解耦
- • 如何在高并发下稳定控制延迟与成本
- • 如何让召回、重排、生成三段链路可度量、可回溯、可灰度
- • 如何在文档持续变化的情况下维护索引一致性和结果稳定性

本文将站在资深架构师和一线技术负责人的视角，完整拆解一套 **企业级私有化 RAG 平台** 的工程化设计。重点不是 API 调用本身，而是围绕以下四个维度展开：

- • 技术深度：原理、分层、检索链路、索引生命周期
- • 工程升级：高并发、弹性扩缩、缓存、隔离、降级、回滚
- • 生产代码：核心表结构、服务实现、消费幂等、SSE 流式链路
- • 实战场景：真实业务路径、容量估算、演进路线与常见故障

## 二、先把问题定义清楚：企业级 RAG 到底在解决什么

### 2.1 典型业务场景

以一个 3000 人规模、多个业务条线并存的企业为例，RAG 常见落地点包括：

| 场景 | 输入知识 | 用户诉求 | 对系统的核心要求 |
| --- | --- | --- | --- |
| 员工知识助手 | 制度、流程、HR 手册、报销规范 | 快速问答 | 权限隔离、口径统一 |
| 研发助手 | 架构文档、接口文档、变更记录、故障复盘 | 技术检索与归纳 | 长文档召回、引用可信 |
| 法务助手 | 合同模板、过往协议、审计条款 | 条款定位、风险总结 | 精确匹配、出处可追溯 |
| 售后助手 | FAQ、工单、维修记录、产品手册 | 现场答疑 | 低延迟、口语化表达 |
| 运维助手 | SOP、告警手册、历史故障、Runbook | 故障定位与建议 | 多源关联、相似案例召回 |

### 2.2 企业级 RAG 的真实非功能诉求

企业不只关心“能回答”，还关心以下指标是否长期稳定：

- • 可用性：核心问答链路全年 SLA 通常要求不低于 99.9%
- • 时延：交互式场景下 p95 通常要控制在 3 到 8 秒区间
- • 并发：工作时间会出现明显流量峰值，需要能承接瞬时放量
- • 安全：租户、部门、项目、目录、文档、片段都可能存在权限边界
- • 一致性：知识更新后，什么时候可查、查到的是哪个索引版本，必须可解释
- • 成本：Embedding、Rerank、LLM、存储、GPU、网络都在持续计费
- • 治理：召回质量、幻觉率、命中来源、失败原因、链路瓶颈必须可观测

### 2.3 为什么 Demo 架构一到生产就失效

Demo 之所以“看起来能跑”，是因为它默认忽略了这些问题：

- • 默认没有权限过滤，只要相似就返回
- • 默认离线全量导入，不考虑增量更新与索引版本切换
- • 默认没有多租户和配额，不考虑隔离
- • 默认没有请求削峰，不考虑大模型推理资源争抢
- • 默认没有评测闭环，不知道是召回差还是生成差
- • 默认没有回滚机制，索引建坏了只能硬顶

**企业级 RAG 的本质，是把“知识检索”从一个模型周边能力，提升为一个企业级知识服务平台。**

## 三、架构总览：企业级 RAG 不是一个服务，而是四层三面

我更推荐用“四层架构 + 三个平面”的方式理解企业级 RAG。

### 3.1 四层架构

1. 1\. 接入层：Web、管理台、OpenAPI、企业 IM 机器人、业务系统 SDK
2. 2\. 编排层：鉴权、会话、Query Rewrite、检索编排、SSE 聚合、缓存与限流
3. 3\. 知识层：文档接入、解析清洗、切片、Embedding、索引构建、版本管理
4. 4\. 推理层：Rerank、LLM 生成、摘要、结构化输出、工具调用

### 3.2 三个平面

1. 1\. 控制面：配置、租户、知识库、模型路由、发布灰度、实验开关
2. 2\. 数据面：文档、切片、索引、缓存、检索结果、对话记录、审计日志
3. 3\. 治理面：指标、Tracing、告警、评测、成本、限流、熔断、回滚

### 3.3 架构图

```
┌────────────────────────── Client Layer ──────────────────────────┐
│ Web / Admin / IM Bot / OpenAPI / SDK                            │
└──────────────────────────────┬───────────────────────────────────┘
                               │ HTTPS / SSE
┌──────────────────────────────▼───────────────────────────────────┐
│ API Gateway / BFF                                                │
│ AuthN / AuthZ / Tenant Context / Rate Limit / Audit / Routing    │
└──────────────┬───────────────────────────┬───────────────────────┘
               │                           │
┌──────────────▼─────────────┐   ┌────────▼───────────────────────┐
│ Query Orchestrator          │   │ Admin & Knowledge Management   │
│ Rewrite / Retrieve / Rerank │   │ KB / Docs / ACL / Version      │
│ Context Build / Stream SSE  │   │ Workflow / Evaluation          │
└──────────────┬─────────────┘   └────────┬───────────────────────┘
               │                           │
               ├───────────────┬──────────┘
               │               │
┌──────────────▼───────┐ ┌─────▼──────────────────────────────────┐
│ Retrieval Services    │ │ Indexing Pipeline                     │
│ Dense / Sparse / ACL  │ │ Parse / Clean / Chunk / Embed / Build │
│ Cache / Fusion / Rank │ │ CDC / Retry / DLQ / Version Switch    │
└──────────────┬───────┘ └─────┬──────────────────────────────────┘
               │               │
┌──────────────▼───────────────────────────────────────────────────┐
│ Storage & Infra                                                  │
│ PostgreSQL / pgvector / OpenSearch / Redis / Kafka / ObjectStore │
│ GPU Inference / Kubernetes / Prometheus / Grafana / Logging      │
└───────────────────────────────────────────────────────────────────┘
```

### 3.4 为什么要这样拆

因为企业级 RAG 有两个天然矛盾：

1. 1\. 离线构建链路很重，但在线查询必须稳定
2. 2\. 知识持续变化，但问答系统不能因为索引重建而抖动

所以必须解耦：

- • 文档接入与在线查询解耦
- • 索引构建与索引切换解耦
- • 权限治理与模型调用解耦
- • 查询编排与底层向量库解耦
- • 质量评测与线上流量解耦

## 四、核心设计原则：企业级 RAG 的“第一性原理”

### 4.1 检索优先，而不是生成优先

大多数线上问题，根因不在 LLM，而在检索链路：

- • 没召回
- • 召回错了
- • 召回太多噪声
- • 权限过滤位置错误
- • 上下文装配不合理

经验上，一个回答质量问题，至少有 60% 以上概率出在“检索前后”，而不是“模型本身”。所以架构重点必须放在：

- • Query 理解
- • 候选召回
- • 重排
- • Context Packing
- • 引用与证据链

### 4.2 权限过滤必须前置到检索阶段

企业 RAG 里最危险的错误之一，是先全库召回、后做结果过滤。这样会导致两个问题：

1. 1\. 不该被看到的片段已经进入候选集合，存在泄露风险
2. 2\. 过滤后剩余结果可能不足，模型仍会“基于残缺上下文”生成幻觉

正确做法是：

- • 先根据用户、角色、部门、项目、租户生成 ACL Filter
- • 检索时把 ACL 与知识域、标签、时间范围一起下推到搜索层
- • 所有未授权文档从候选池层面就不进入召回链路

### 4.3 索引必须版本化，而不是“覆盖式更新”

一旦线上只有一个活动索引，那么每次全量重建都会带来这些风险：

- • 构建中途失败，索引处于半完成状态
- • 新索引效果不稳定，用户今天查到的结果和昨天差异巨大
- • 无法回滚

正确方式是蓝绿索引：

- • `kb_001_v20260612_01` 构建中
- • `kb_001_v20260611_03` 仍负责线上查询
- • 构建完成后做质量校验
- • 通过后原子切换 active version
- • 异常时秒级回滚

### 4.4 把“片段”当成产品对象，而不是中间产物

很多系统只关心文档，不关心 chunk。但企业级场景里，真正参与检索、重排、引用、评测和权限控制的核心对象其实是 chunk。

每个 chunk 至少应具备：

- • 来源文档 ID
- • 章节路径
- • 页码或段落定位
- • 语言
- • 租户和知识库归属
- • 权限标签
- • 版本号
- • 切片策略版本
- • Embedding 模型版本
- • 校验摘要

也就是说，chunk 不是“切完就存”的文本块，而是一个可审计、可回溯、可演进的知识单元。

## 五、数据模型设计：没有好的元数据，就没有好的检索治理

### 5.1 关键实体

建议至少围绕以下实体建模：

- • `knowledge_base` ：知识库
- • `document` ：文档元数据
- • `document_version` ：文档版本
- • `chunk` ：切片
- • `chunk_embedding` ：向量与索引归属
- • `index_build_job` ：索引构建任务
- • `kb_active_index` ：知识库当前生效索引
- • `qa_session` ：问答会话
- • `qa_message` ：会话消息
- • `retrieval_trace` ：召回与重排记录
- • `audit_log` ：权限与访问审计

### 5.2 PostgreSQL 核心表示例

```
CREATE TABLE knowledge_base (
    id                BIGSERIAL PRIMARY KEY,
    tenant_id         BIGINT NOT NULL,
    kb_code           VARCHAR(64) NOT NULL,
    kb_name           VARCHAR(128) NOT NULL,
    visibility        VARCHAR(32) NOT NULL DEFAULT 'PRIVATE',
    status            VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_by        BIGINT NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tenant_id, kb_code)
);

CREATE TABLE document (
    id                BIGSERIAL PRIMARY KEY,
    tenant_id         BIGINT NOT NULL,
    kb_id             BIGINT NOT NULL,
    doc_code          VARCHAR(64) NOT NULL,
    file_name         VARCHAR(256) NOT NULL,
    file_ext          VARCHAR(16) NOT NULL,
    content_hash      VARCHAR(64) NOT NULL,
    storage_uri       VARCHAR(512) NOT NULL,
    parser_type       VARCHAR(32) NOT NULL,
    acl_scope         JSONB NOT NULL,
    biz_tags          JSONB NOT NULL DEFAULT '{}'::jsonb,
    status            VARCHAR(32) NOT NULL,
    created_by        BIGINT NOT NULL,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE index_build_job (
    id                BIGSERIAL PRIMARY KEY,
    tenant_id         BIGINT NOT NULL,
    kb_id             BIGINT NOT NULL,
    index_version     VARCHAR(64) NOT NULL,
    source_snapshot   JSONB NOT NULL,
    split_strategy    JSONB NOT NULL,
    embedding_model   VARCHAR(128) NOT NULL,
    status            VARCHAR(32) NOT NULL,
    total_docs        INT NOT NULL DEFAULT 0,
    success_docs      INT NOT NULL DEFAULT 0,
    failed_docs       INT NOT NULL DEFAULT 0,
    started_at        TIMESTAMP NULL,
    finished_at       TIMESTAMP NULL,
    error_message     TEXT NULL,
    UNIQUE (kb_id, index_version)
);

CREATE TABLE chunk (
    id                BIGSERIAL PRIMARY KEY,
    tenant_id         BIGINT NOT NULL,
    kb_id             BIGINT NOT NULL,
    doc_id            BIGINT NOT NULL,
    index_version     VARCHAR(64) NOT NULL,
    chunk_no          INT NOT NULL,
    section_path      VARCHAR(512) NULL,
    page_no           INT NULL,
    token_count       INT NOT NULL,
    content           TEXT NOT NULL,
    content_hash      VARCHAR(64) NOT NULL,
    acl_scope         JSONB NOT NULL,
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (doc_id, index_version, chunk_no)
);

CREATE TABLE chunk_embedding (
    chunk_id          BIGINT PRIMARY KEY REFERENCES chunk(id),
    tenant_id         BIGINT NOT NULL,
    kb_id             BIGINT NOT NULL,
    index_version     VARCHAR(64) NOT NULL,
    embedding_model   VARCHAR(128) NOT NULL,
    embedding         vector(1024) NOT NULL
);

CREATE TABLE kb_active_index (
    kb_id             BIGINT PRIMARY KEY,
    active_version    VARCHAR(64) NOT NULL,
    switched_by       BIGINT NOT NULL,
    switched_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 5.3 为什么一定要有 index\_version

`index_version` 会直接影响：

- • 查询命中哪个索引快照
- • 线上与离线评测是否在同一版本下对比
- • 回答引用能否追溯到构建时上下文
- • 故障出现后能否快速回滚

很多团队做不好线上稳定性，不是模型不行，而是数据版本不可控。

## 六、离线链路设计：文档接入、索引构建与蓝绿切换

### 6.1 离线链路目标

离线链路的职责不是“把文档变成向量”这么简单，而是要解决：

- • 多格式文档接入
- • 文本清洗标准化
- • 切片策略统一
- • 增量更新与全量构建
- • 失败重试与幂等
- • 构建完成后的质量门禁
- • 原子切换与回滚

### 6.2 标准离线流程

```
上传文档
  -> 保存对象存储
  -> 写文档元数据
  -> 投递索引任务
  -> 文本解析
  -> 清洗与结构恢复
  -> Chunk 切分
  -> Embedding
  -> 向量/倒排写入
  -> 索引质量检查
  -> 切换 active index
  -> 记录审计与通知
```

### 6.3 文档解析不是单纯“抽文本”，而是“恢复结构”

企业文档中最有价值的信息往往在结构里：

- • 标题层级
- • 表格行列
- • 图片说明
- • 页码
- • 编号
- • 附录
- • 更新时间

如果解析阶段把这些结构全丢掉，那么后面检索与引用会非常痛苦。建议原则如下：

1. 1\. Markdown、HTML、Wiki 等结构化文档优先保留标题树
2. 2\. PDF 不只提取文本，还要标记页码和块位置
3. 3\. 表格要转成可读文本，同时保留表头语义
4. 4\. 图像型 PDF 要有 OCR 回退，并标记解析质量
5. 5\. 对扫描错误或乱码文档要有低质量标记，避免污染索引

### 6.4 智能切片的正确目标

切片不是把文本平均截断，而是平衡三个维度：

- • 召回精度
- • 上下文完整性
- • 推理成本

实践上，常见策略如下：

- • 一级按标题或章节切
- • 二级按语义段落切
- • 三级按 token 长度做兜底切分
- • 保留适度 overlap，避免跨段断义

但更重要的是： **切片策略必须版本化** 。因为你未来一定会调整：

- • `chunk_size`
- • `overlap`
- • 标题权重
- • 表格拆分方式
- • 是否保留前后文摘要

一旦策略改了，实际上就等价于“重建另一版索引”。

### 6.5 生产级索引调度器示例

下面给一个更接近生产的 Python 索引编排实现，核心点不是语法，而是顺序控制、幂等与资源保护。

```
import asyncio
import hashlib
import logging
from dataclasses import dataclass
from typing import Iterable

logger = logging.getLogger(__name__)

@dataclass(slots=True)
class ChunkRecord:
    tenant_id: int
    kb_id: int
    doc_id: int
    index_version: str
    chunk_no: int
    section_path: str | None
    page_no: int | None
    content: str
    acl_scope: dict
    metadata: dict

class IndexBuildCoordinator:
    def __init__(
        self,
        doc_repo,
        chunk_repo,
        embedding_client,
        parser_registry,
        splitter,
        max_doc_concurrency: int = 4,
        embed_batch_size: int = 32,
    ):
        self.doc_repo = doc_repo
        self.chunk_repo = chunk_repo
        self.embedding_client = embedding_client
        self.parser_registry = parser_registry
        self.splitter = splitter
        self.doc_semaphore = asyncio.Semaphore(max_doc_concurrency)
        self.embed_batch_size = embed_batch_size

    async def build_index(self, job_id: int, docs: list[dict], index_version: str) -> None:
        await self.doc_repo.mark_job_running(job_id)
        results = await asyncio.gather(
            *[self._process_doc(job_id, doc, index_version) for doc in docs],
            return_exceptions=True,
        )

        failed = 0
        for result in results:
            if isinstance(result, Exception):
                failed += 1

        if failed:
            await self.doc_repo.mark_job_partial_failed(job_id, failed)
            raise RuntimeError(f"index build has {failed} failed documents")

        await self.doc_repo.mark_job_succeeded(job_id)

    async def _process_doc(self, job_id: int, doc: dict, index_version: str) -> None:
        async with self.doc_semaphore:
            doc_id = doc["doc_id"]
            if await self.chunk_repo.exists_by_doc_and_version(doc_id, index_version):
                logger.info("skip indexed document doc_id=%s version=%s", doc_id, index_version)
                return

            await self.doc_repo.mark_doc_indexing(doc_id, index_version)
            try:
                parser = self.parser_registry.get_parser(doc["file_name"])
                content = await parser.parse(doc["storage_uri"])
                chunk_records = self._split_doc(doc, content, index_version)

                for batch in self._batched(chunk_records, self.embed_batch_size):
                    texts = [item.content for item in batch]
                    embeddings = await self.embedding_client.embed_batch(texts)
                    await self.chunk_repo.save_batch(batch, embeddings)

                await self.doc_repo.mark_doc_indexed(doc_id, index_version, len(chunk_records))
            except Exception as exc:
                await self.doc_repo.mark_doc_failed(doc_id, index_version, str(exc))
                logger.exception("index doc failed doc_id=%s version=%s", doc_id, index_version)
                raise

    def _split_doc(self, doc: dict, content: str, index_version: str) -> list[ChunkRecord]:
        pieces = self.splitter.split(content)
        records: list[ChunkRecord] = []
        for idx, piece in enumerate(pieces):
            records.append(
                ChunkRecord(
                    tenant_id=doc["tenant_id"],
                    kb_id=doc["kb_id"],
                    doc_id=doc["doc_id"],
                    index_version=index_version,
                    chunk_no=idx,
                    section_path=piece.section_path,
                    page_no=piece.page_no,
                    content=piece.content,
                    acl_scope=doc["acl_scope"],
                    metadata={
                        "content_hash": hashlib.sha256(piece.content.encode("utf-8")).hexdigest(),
                        "splitter_version": "hierarchical-v3",
                        "parser_type": doc["parser_type"],
                    },
                )
            )
        return records

    @staticmethod
    def _batched(items: list[ChunkRecord], batch_size: int) -> Iterable[list[ChunkRecord]]:
        for i in range(0, len(items), batch_size):
            yield items[i : i + batch_size]
```

这个实现看似普通，但有几个生产要点：

- • 先查 `doc_id + index_version` 是否已构建，避免重复写入
- • 用 `Semaphore` 限制文档级并发，防止解析和向量化同时放大
- • 文档状态和任务状态分开维护，便于部分失败重试
- • 批次保存时要求 chunk 与 embedding 一一对应，不能乱序
- • 任何异常都必须回写状态，否则管理台无法判断实际进度

### 6.6 索引切换与回滚

索引构建成功后不要直接切流量，先过质量门禁：

- • 召回评测集 Recall@K 是否达标
- • TopN 命中来源是否符合预期
- • 高风险问题集是否出现权限穿透
- • 样本对比中答案引用是否稳定
- • 新索引查询 RT 是否显著上升

通过后再更新 `kb_active_index` 。失败时只需把 `active_version` 切回上一个版本即可。

这就是企业级系统里非常重要的一个原则：

**构建失败不应该影响线上，质量不达标也不应该影响线上。**

## 七、在线查询链路：真正决定用户体验的是“编排”，不是单一模型

### 7.1 在线查询的标准链路

一个成熟的问答请求，建议至少经历以下阶段：

1. 1\. 身份识别与租户上下文注入
2. 2\. ACL 解析与知识域判定
3. 3\. Query 规范化
4. 4\. Query Rewrite 或 Query Decomposition
5. 5\. 多路候选召回
6. 6\. 融合排序
7. 7\. 精排 Rerank
8. 8\. Context Packing
9. 9\. Answer Generation
10. 10\. 引用补全、审计落盘与指标上报

### 7.2 Query Rewrite 为什么必要

用户在企业里提问经常存在这些问题：

- • 用口语，不用系统术语
- • 问题上下文不完整
- • 混合多个意图
- • 带大量代词和省略

例如：

“上次那个采购审批超过 50 万的流程是怎么走的？”

如果系统直接拿这句话检索，可能效果很一般。更合理的处理是把它规范化为：

- • “采购审批流程”
- • “金额超过 50 万”
- • “审批节点”
- • “制度版本”

所以 Query Rewrite 的作用不是“让问题更像大模型语言”，而是把用户问题转换成更适合检索引擎理解的检索表达式。

### 7.3 混合检索是企业场景的默认解，而不是可选项

纯稠密向量检索擅长语义相近，但对以下内容不稳定：

- • 合同编号
- • 产品型号
- • 错误码
- • 版本号
- • 表字段名
- • 固定术语

所以企业级 RAG 更推荐混合检索：

- • 稠密检索：负责语义召回
- • 稀疏检索/BM25：负责关键词精确召回
- • 结构过滤：负责 ACL、知识域、文档类型、时间范围

最后再通过 RRF 或学习排序策略进行融合。

### 7.4 生产级混合检索服务示例

```
from dataclasses import dataclass

@dataclass(slots=True)
class SearchContext:
    tenant_id: int
    kb_id: int
    user_id: int
    active_version: str
    acl_filter: dict
    top_k: int

class HybridRetriever:
    def __init__(self, dense_repo, sparse_repo, embedder, rrf_k: int = 60):
        self.dense_repo = dense_repo
        self.sparse_repo = sparse_repo
        self.embedder = embedder
        self.rrf_k = rrf_k

    async def retrieve(self, query: str, ctx: SearchContext) -> list[dict]:
        normalized_query = self._normalize(query)
        query_vector = await self.embedder.embed(normalized_query)

        dense_hits, sparse_hits = await asyncio.gather(
            self.dense_repo.search(
                tenant_id=ctx.tenant_id,
                kb_id=ctx.kb_id,
                index_version=ctx.active_version,
                acl_filter=ctx.acl_filter,
                query_vector=query_vector,
                top_k=ctx.top_k * 3,
            ),
            self.sparse_repo.search(
                tenant_id=ctx.tenant_id,
                kb_id=ctx.kb_id,
                index_version=ctx.active_version,
                acl_filter=ctx.acl_filter,
                query=normalized_query,
                top_k=ctx.top_k * 3,
            ),
        )

        return self._rrf_merge(dense_hits, sparse_hits, ctx.top_k)

    def _normalize(self, query: str) -> str:
        return " ".join(query.strip().split())

    def _rrf_merge(self, dense_hits: list[dict], sparse_hits: list[dict], top_k: int) -> list[dict]:
        dense_rank = {hit["chunk_id"]: idx + 1 for idx, hit in enumerate(dense_hits)}
        sparse_rank = {hit["chunk_id"]: idx + 1 for idx, hit in enumerate(sparse_hits)}
        merged: dict[int, dict] = {}

        all_ids = set(dense_rank) | set(sparse_rank)
        for chunk_id in all_ids:
            d_rank = dense_rank.get(chunk_id, self.rrf_k * 2)
            s_rank = sparse_rank.get(chunk_id, self.rrf_k * 2)
            score = 1 / (self.rrf_k + d_rank) + 1 / (self.rrf_k + s_rank)
            source = self._pick_source(chunk_id, dense_hits, sparse_hits)
            merged[chunk_id] = {**source, "rrf_score": score}

        return sorted(merged.values(), key=lambda item: item["rrf_score"], reverse=True)[:top_k]

    @staticmethod
    def _pick_source(chunk_id: int, dense_hits: list[dict], sparse_hits: list[dict]) -> dict:
        for item in dense_hits:
            if item["chunk_id"] == chunk_id:
                return item
        for item in sparse_hits:
            if item["chunk_id"] == chunk_id:
                return item
        raise KeyError(f"chunk not found: {chunk_id}")
```

要点在于：

- • `active_version` 必须显式传入，确保查询版本确定
- • `acl_filter` 必须在检索仓储层下推，而不是结果层过滤
- • 稠密和稀疏并行执行，降低总 RT
- • 初排返回 `top_k * 3` ，给重排预留空间

### 7.5 Rerank 的意义，不只是“排序更准”

Rerank 的本质是把“召回相似”提升为“问题-片段相关性判断”。它常见带来的收益包括：

- • 提升 TopN 命中率
- • 降低噪声片段进入上下文
- • 让模型输入更聚焦，从而减少幻觉
- • 缩短有效上下文长度，降低推理成本

但要注意两点：

1. 1\. Rerank 是额外推理开销，不能无上限放大候选数
2. 2\. Rerank 是“精排器”，不是“兜底纠错器”，前面召回太差时它也救不回来

### 7.6 Context Packing 是一门单独的工程

很多系统召回和重排都不错，但答案仍不稳定，常见原因是 Context Packing 没设计好：

- • 把多个来源重复段落都塞进去，浪费窗口
- • 把高度相关片段拆散，没有相邻补全
- • 不区分主证据和辅助证据
- • 不记录引用锚点，导致回答后无法追溯

建议策略：

1. 1\. 先保留 TopN 主证据
2. 2\. 对同一文档相邻 chunk 做局部合并
3. 3\. 对重复内容做去重
4. 4\. 对引用字段保留 `doc_id / section / page_no / chunk_no`
5. 5\. 严格控制 token 预算，给回答部分留余量

## 八、生成层设计：模型调用只是最后一步，不是唯一一步

### 8.1 企业知识问答的 Prompt 目标

在企业场景里，Prompt 的核心不是“写得像人”，而是：

- • 基于上下文回答
- • 明确出处
- • 上下文不足时拒答或保守表达
- • 保留结构化输出能力

一个稳健的系统 Prompt 通常会要求模型：

- • 只基于提供材料作答
- • 不得虚构制度、流程、条款
- • 尽量按条目式输出
- • 每个关键结论附引用
- • 如果上下文冲突，优先使用更新版本或更高优先级来源

### 8.2 生成前要做“可答性判断”

并不是所有问题都该直接进入生成。

建议在生成前做一次 Answerability Check，判断：

- • 召回结果是否足够
- • 相关性分数是否达标
- • 是否存在关键字段缺失
- • 是否属于高风险问题类型

对于以下场景，可以直接降级：

- • 没有足够证据
- • 权限过滤后结果为空
- • 高风险问题但上下文冲突明显
- • 模型服务压力过高

降级策略可以是：

- • 返回“未找到足够依据”
- • 展示候选文档清单而不是强答
- • 返回知识库内可继续搜索的建议

### 8.3 SSE 流式输出链路的正确打开方式

企业级问答大多数要做流式输出，因为它显著改善体感时延。但 SSE 链路很容易踩坑：

- • 网关或代理缓冲响应
- • 上游服务超时早于下游生成
- • 前端断开后服务端还在继续推理
- • 无法统计首 token 时间和总完成时间

所以一个完整的流式链路，至少要追踪：

- • TTFT：Time To First Token
- • TTFB：首字节返回时间
- • 总生成时长
- • 输出 token 数
- • 用户是否中途取消

### 8.4 Java 编排服务示例

下面这个示例展示的是线上最重要的一层：查询编排，而不是模型推理细节。

```
@Service
@RequiredArgsConstructor
public class RagAskService {

    private final PermissionService permissionService;
    private final KnowledgeBaseService knowledgeBaseService;
    private final RetrievalClient retrievalClient;
    private final GenerationClient generationClient;
    private final QaTraceService qaTraceService;
    private final AnswerCacheService answerCacheService;

    public Flux<ServerSentEvent<String>> ask(AskRequest request, LoginUser user) {
        Long tenantId = user.getTenantId();
        Long kbId = request.getKbId();

        permissionService.checkReadPermission(user.getUserId(), kbId);

        String activeVersion = knowledgeBaseService.getActiveIndexVersion(kbId);
        String cacheKey = buildCacheKey(tenantId, kbId, activeVersion, request.getQuestion());

        return answerCacheService.get(cacheKey)
            .switchIfEmpty(Mono.defer(() -> doAsk(request, user, activeVersion, cacheKey)))
            .flatMapMany(Flux::just);
    }

    private Mono<ServerSentEvent<String>> doAsk(
        AskRequest request,
        LoginUser user,
        String activeVersion,
        String cacheKey
    ) {
        RetrievalRequest retrievalRequest = RetrievalRequest.builder()
            .tenantId(user.getTenantId())
            .kbId(request.getKbId())
            .userId(user.getUserId())
            .activeVersion(activeVersion)
            .question(request.getQuestion())
            .build();

        long startedAt = System.currentTimeMillis();

        return retrievalClient.retrieve(retrievalRequest)
            .flatMap(result -> {
                qaTraceService.recordRetrieval(
                    request.getTraceId(),
                    activeVersion,
                    result.getCandidates()
                );

                if (result.getCandidates().isEmpty() || !result.isAnswerable()) {
                    String fallback = "当前未检索到足够可信的内容，建议缩小范围或更换关键词。";
                    return answerCacheService.put(cacheKey, fallback)
                        .thenReturn(ServerSentEvent.builder(fallback).event("message").build());
                }

                GenerationRequest generationRequest = GenerationRequest.builder()
                    .traceId(request.getTraceId())
                    .question(request.getQuestion())
                    .context(result.getTopContexts())
                    .build();

                return generationClient.generate(generationRequest)
                    .doOnNext(chunk -> qaTraceService.appendToken(request.getTraceId(), chunk))
                    .reduce(new StringBuilder(), StringBuilder::append)
                    .flatMap(fullAnswer -> answerCacheService.put(cacheKey, fullAnswer.toString())
                        .thenReturn(ServerSentEvent.builder(fullAnswer.toString()).event("message").build()))
                    .doFinally(signalType ->
                        qaTraceService.finish(request.getTraceId(), System.currentTimeMillis() - startedAt));
            });
    }

    private String buildCacheKey(Long tenantId, Long kbId, String activeVersion, String question) {
        return tenantId + ":" + kbId + ":" + activeVersion + ":" + DigestUtils.md5DigestAsHex(question.getBytes(StandardCharsets.UTF_8));
    }
}
```

这个实现里最关键的不是 Reactor API，而是几个工程点：

- • 缓存键包含 `activeVersion` ，避免索引切换后命中旧答案
- • 权限校验在最前面执行
- • 召回结果要落盘留痕，方便问题复盘
- • `answerable` 判断失败时直接降级，不强行生成
- • 链路结束时记录总耗时

## 九、权限、多租户与合规：企业 RAG 成败的底层分水岭

### 9.1 权限模型不能只做“知识库级”

很多项目一开始只做知识库级权限，后面很快不够用。现实中往往至少要支持：

- • 租户级
- • 部门级
- • 项目级
- • 目录级
- • 文档级
- • 特定标签级

例如同属于“法务知识库”的文档，也可能分为：

- • 公开模板
- • 内部制度
- • 并购项目专属协议

这些内容不可能用一个读写权限解决。

### 9.2 ACL 下推策略

权限最稳妥的实现方式是：

1. 1\. 用户登录后生成访问主体 `subject`
2. 2\. 根据角色、部门、项目、标签计算允许访问范围
3. 3\. 把范围编译为底层可执行的 `acl_filter`
4. 4\. 在稠密检索、稀疏检索、缓存命中、引用返回四处统一复用

注意，缓存也不能忽略权限。因为同样的问题，不同用户可能命中不同文档。

### 9.3 审计是必须品，不是附加项

企业里只要涉及知识问答，就建议记录以下审计信息：

- • 谁在什么时间问了什么问题
- • 命中了哪些文档与片段
- • 使用了哪个索引版本
- • 返回了什么引用
- • 是否触发降级或拒答
- • 是否命中敏感分类

这不仅是安全需求，也是问题排查的基础。

## 十、高并发与可扩展设计：RAG 真正的压力点在哪里

### 10.1 RAG 的并发不是单点压力，而是级联放大

一个问答请求常常会触发多段资源消耗：

1. 1\. Query Rewrite
2. 2\. Embedding
3. 3\. 稠密检索
4. 4\. 稀疏检索
5. 5\. Rerank
6. 6\. LLM 生成

其中最昂贵的一般是：

- • Rerank
- • LLM 生成
- • 高并发下的 Embedding

所以 RAG 的并发问题，不是“接口 QPS”那么简单，而是：

- • 每个请求会放大成多少次下游推理调用
- • GPU 上同时排队的请求数是多少
- • 平均回答长度是多少
- • SSE 长连接会占用多久

### 10.2 核心性能手段

企业级 RAG 常见的性能优化手段包括：

- • Query 结果缓存
- • 高热问答缓存
- • Embedding 结果缓存
- • Rerank 候选数动态裁剪
- • 流量分级与请求队列
- • 多模型路由
- • 索引冷热分层
- • 异步预处理

### 10.3 缓存策略的正确姿势

缓存不是一把梭，而是分层设计：

1. 1\. Query Rewrite Cache：同义问题改写结果
2. 2\. Retrieval Cache：检索候选集合
3. 3\. Answer Cache：最终答案
4. 4\. Embedding Cache：文本向量结果

但要特别注意缓存键：

- • 必须包含 `tenant_id`
- • 必须包含 `kb_id`
- • 必须包含 `active_index_version`
- • 必须考虑权限视图
- • 问题文本要归一化

如果这些信息不进缓存键，缓存就是潜在的数据泄露点。

### 10.4 背压与限流必须做在入口层

RAG 系统如果缺少背压，最典型的后果就是：

- • 大量请求同时进入生成阶段
- • GPU 队列堆积
- • SSE 长连接暴涨
- • 网关线程或连接池被耗尽
- • 上游重试放大雪崩

建议至少做三层保护：

1. 1\. API 网关限流：按租户、用户、接口进行令牌桶控制
2. 2\. 编排层并发闸门：限制进入生成阶段的活跃请求数
3. 3\. 模型服务队列：超出阈值后快速失败或排队

### 10.5 生成阶段并发闸门示例

```
import asyncio
from contextlib import asynccontextmanager

class GenerationAdmissionController:
    def __init__(self, max_inflight: int):
        self._semaphore = asyncio.Semaphore(max_inflight)

    @asynccontextmanager
    async def acquire(self):
        await self._semaphore.acquire()
        try:
            yield
        finally:
            self._semaphore.release()

class GenerationService:
    def __init__(self, llm_client, admission_controller: GenerationAdmissionController):
        self.llm_client = llm_client
        self.admission_controller = admission_controller

    async def stream_answer(self, prompt: str):
        async with self.admission_controller.acquire():
            async for chunk in self.llm_client.stream(prompt):
                yield chunk
```

这里最重要的是 `release` 必须在 `finally` 里。生产代码里很多“偶发卡死”，本质上都是异常路径把许可吃掉了。

### 10.6 水平扩展应该优先扩哪一层

企业级 RAG 中，不同层的扩展方式不同：

- • 网关/BFF：优先水平扩容
- • 检索编排：优先水平扩容
- • 向量检索：看底层索引架构，可能是分片扩容
- • Rerank/LLM：通常是 GPU 服务池扩容
- • 索引构建：更适合异步 worker 扩容

也就是说，RAG 平台不是“统一加机器”就解决问题，而是要针对瓶颈层做差异化扩展。

## 十一、生产级案例场景：内部制度与合同审查双场景平台

### 11.1 场景背景

假设企业要同时服务两类用户：

1. 1\. 内部员工：查询 HR 制度、采购流程、财务规范
2. 2\. 法务团队：定位合同模板、条款解释、历史协议

这两个场景看似都叫“知识问答”，但技术上差别很大：

- • 内部制度场景：更强调响应速度和通用表达
- • 合同场景：更强调条款精确命中、来源可追溯和保守回答

因此平台在架构上应允许：

- • 知识库维度配置不同切片策略
- • 不同场景选择不同 Rerank 候选数
- • 不同场景使用不同 Prompt 模板
- • 高风险知识域启用更严格的 Answerability 阈值

### 11.2 实际查询链路

以“采购金额超过 50 万需要哪些审批节点”这个问题为例：

1. 1\. 用户登录后进入采购制度知识库
2. 2\. 编排层识别问题属于“流程查询 + 金额条件”
3. 3\. Query Rewrite 补足检索词：采购审批、50 万、审批节点、流程图
4. 4\. 稠密检索召回流程说明，稀疏检索召回制度编号和表格
5. 5\. Rerank 过滤掉不相关的旧制度
6. 6\. Context Packing 合并连续 chunk
7. 7\. LLM 输出条目式答案，并附制度名称、章节和页码

这条链路里，真正决定回答质量的通常不是模型温度，而是：

- • 是否检索到了“最新版制度”
- • 是否把表格审批链召回了
- • 是否过滤掉了旧版本制度
- • 是否把相邻章节一起送入上下文

### 11.3 合同审查类场景的额外约束

法务类场景应增加以下策略：

- • 优先返回条款定位和出处，不强求自然语言总结
- • 对“是否合规”“是否违法”类问题启用保守模板
- • 对未命中关键条款的问题直接拒答
- • 记录完整引用，便于审计与人工复核

这也说明一个重要事实：

**企业级 RAG 不应该是一套固定模板，而应该是面向知识域可配置的问答平台。**

## 十二、微服务治理：没有治理能力，RAG 迟早会退化成“运气系统”

### 12.1 服务拆分建议

对于一个中大型企业 RAG 平台，建议最少拆成以下服务：

- • `gateway-service` ：统一入口、鉴权、限流、审计
- • `kb-service` ：知识库、文档、权限、索引版本管理
- • `indexing-service` ：解析、切片、Embedding、索引构建
- • `retrieval-service` ：检索、融合、重排、可答性判断
- • `generation-service` ：Prompt 组装、模型路由、SSE 输出
- • `evaluation-service` ：评测集、回放、对比实验、质量报告

### 12.2 为什么不要把所有逻辑揉进一个 Python 服务

单体 Python 服务在 Demo 阶段很快，但在生产阶段会遇到：

- • 文档解析与在线查询资源竞争
- • 索引构建失败影响查询稳定性
- • 服务发布牵一发动全身
- • 权限、配置、审计很难统一治理

企业里最常见的问题不是“不够快开发”，而是“太快堆在一起，后面拆不动”。

### 12.3 配置中心与动态开关

建议把以下参数全部配置化：

- • 各知识库的切片策略
- • 检索 TopK
- • Rerank 候选数
- • Prompt 模板版本
- • 可答性阈值
- • 缓存 TTL
- • 限流阈值
- • 模型路由策略

这样做的价值是：

- • 无需发版即可调整检索策略
- • 可按租户或知识库做差异化治理
- • 便于灰度实验和问题回退

## 十三、发布、灰度与回滚：RAG 平台必须有“止损能力”

### 13.1 RAG 平台有三类发布对象

1. 1\. 代码发布：服务逻辑变更
2. 2\. 模型发布：Embedding、Rerank、LLM 切换
3. 3\. 索引发布：知识内容与切片策略变化

这三类发布都不应混在一起做。

### 13.2 索引发布流程建议

```
创建新索引版本
  -> 后台构建
  -> 运行评测集
  -> 抽样人工验收
  -> 灰度流量
  -> 切换 active version
  -> 保留旧索引窗口
```

### 13.3 模型发布注意事项

Embedding 模型一旦切换，通常意味着：

- • 全量向量需要重建
- • 线上召回结果会发生系统性变化
- • 旧缓存可能全部失效

所以模型升级绝不能被当成“小版本改动”。它本质上是一次检索系统变更。

### 13.4 灰度维度建议

可以按以下维度灰度：

- • 租户
- • 知识库
- • 问题类别
- • 白名单用户
- • 流量百分比

其中最推荐的顺序是：

1. 1\. 评测集离线验证
2. 2\. 内部白名单
3. 3\. 小租户灰度
4. 4\. 大流量正式切换

## 十四、可观测与评测闭环：你必须知道系统为什么答对、为什么答错

### 14.1 只看接口 RT 是远远不够的

RAG 系统至少要建立三类指标：

1. 1\. 运行指标
2. 2\. 质量指标
3. 3\. 成本指标

### 14.2 运行指标

- • QPS
- • p50 / p95 / p99 RT
- • TTFT
- • 检索耗时
- • Rerank 耗时
- • 生成耗时
- • 活跃 SSE 连接数
- • GPU 队列长度
- • 构建任务成功率
- • DLQ 数量

### 14.3 质量指标

- • Recall@K
- • Precision@K
- • MRR / nDCG
- • 可答率
- • 拒答率
- • 引用完整率
- • 幻觉投诉率
- • 人工验收通过率

### 14.4 成本指标

- • 单问题平均 token 成本
- • 单问题平均 GPU 占用时长
- • 单知识库索引构建成本
- • 热门问题缓存命中率
- • 不同模型路由下的成本差异

### 14.5 Retrieval Trace 表很关键

很多团队出了问题只能说“模型答错了”，但其实不知道错在：

- • 检索没召回
- • 重排顺序错了
- • 上下文装配错了
- • Prompt 约束不够

因此建议记录完整的 Retrieval Trace，包括：

- • 原始问题
- • Rewrite 后问题
- • 稠密召回 TopN
- • 稀疏召回 TopN
- • RRF 融合结果
- • Rerank 后结果
- • 最终送模上下文
- • 返回引用

只有这样，问题才能被工程化复盘。

## 十五、Kubernetes 与部署建议：不要把 AI 服务当普通 CRUD 服务部署

### 15.1 部署层的差异

RAG 平台中的不同服务，部署策略不应相同：

- • Gateway/BFF：无状态、可水平扩展
- • KB Service：典型 CRUD 服务
- • Retrieval Service：CPU 为主，适合水平扩展
- • Generation Service：通常强依赖 GPU
- • Indexing Worker：后台任务型服务，适合异步扩容

### 15.2 Generation Service 的部署关注点

- • GPU 资源隔离
- • 并发队列长度
- • Pod 预热
- • 模型加载时长
- • 长连接超时
- • 取消请求时及时中断下游推理

### 15.3 一个更实用的 HPA 指标思路

对 Retrieval Service，可以按 CPU / 内存扩容；

对 Generation Service，更建议结合：

- • 活跃请求数
- • 排队长度
- • 平均生成时长

因为 GPU 服务往往不是 CPU 先打满，而是队列先积压。

## 十六、演进路线：企业 RAG 不可能一步到位，但一定要路线正确

### 阶段一：最小闭环

目标：

- • 先打通上传、索引、检索、生成、引用闭环
- • 支持基础权限
- • 支持最小评测集

不要过早追求：

- • 多模型混战
- • 复杂 Agent 编排
- • 过度前端包装

### 阶段二：工程化稳定

重点：

- • 文档接入异步化
- • 索引版本化
- • 检索链路可观测
- • 限流、缓存、降级到位

### 阶段三：平台化治理

重点：

- • 多租户
- • 多知识域
- • 差异化配置
- • 质量评测平台
- • 灰度与 A/B 实验

### 阶段四：能力增强

重点：

- • Query Decomposition
- • GraphRAG / 实体解析
- • 多跳检索
- • Agentic Retrieval
- • 结构化工具调用

这里要特别提醒： **增强能力必须建立在基础治理稳定之后。**

如果索引版本、权限边界、评测闭环都没做好，就贸然上 Agentic RAG，系统复杂度会急剧上升，且很难解释问题根因。

## 十七、常见生产故障与处理思路

### 17.1 问题：明明文档已上传，但用户查不到

排查顺序：

1. 1\. 文档状态是否已完成索引
2. 2\. 当前问答命中的是否是最新 `active_version`
3. 3\. ACL 是否把结果过滤掉了
4. 4\. 切片是否把关键表述拆散
5. 5\. Query Rewrite 是否误伤原始语义

### 17.2 问题：答案偶尔很好，偶尔很差

常见根因：

- • 索引版本漂移
- • 新旧文档同时存在且未做优先级控制
- • Rerank 模型波动
- • Prompt 或上下文装配不稳定
- • 热缓存命中不同版本

### 17.3 问题：并发一高，RT 明显恶化

优先排查：

- • 哪一段最慢：检索、重排还是生成
- • 活跃生成请求数是否超上限
- • Rerank 候选数是否过大
- • 是否有代理缓冲 SSE
- • 是否存在重试风暴

### 17.4 问题：用户质疑“答案是编的”

处理思路：

- • 展示明确引用
- • 展示命中文档版本
- • 回放 Retrieval Trace
- • 检查是否跳过了 Answerability Gate
- • 对高风险问题启用保守拒答策略

## 十八、总结：企业级 RAG 的核心竞争力，在工程体系而不在单点模型

把 RAG 做成企业级系统，关键不在于你接了多少个模型，也不在于前端页面多炫，而在于你是否真正建立了下面这套能力：

- • 以权限边界为前提的检索体系
- • 以索引版本为核心的数据生命周期管理
- • 以混合检索、重排、上下文装配为核心的质量链路
- • 以限流、缓存、背压、隔离、灰度、回滚为核心的工程体系
- • 以评测、Tracing、审计、成本度量为核心的治理闭环

一句话总结：

**企业级 RAG 不是“大模型接知识库”，而是“围绕知识服务构建一套可持续运营的分布式系统”。**

当你用这个视角重新审视 RAG，就会发现真正重要的工作，不是把模型接进来，而是把系统建扎实。

后续如果要继续演进，这条路线最稳妥：

1. 1\. 先把权限、索引版本、检索质量、评测闭环做好
2. 2\. 再做多知识域、多租户和高并发治理
3. 3\. 最后再引入 GraphRAG、Agentic RAG、多跳规划等增强能力

这也是绝大多数企业从“RAG 可用”走向“RAG 可交付”的必经之路。

**微信扫一扫赞赏作者**

作者提示: 个人观点，仅供参考