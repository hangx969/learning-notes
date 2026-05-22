---
title: "为什么 Claude Code 不用 RAG 检索代码，而是 grep？"
source: "https://mp.weixin.qq.com/s/TGBfhrvC_7dtGxy1GAurBQ"
created: 2026-05-22
tags:
  - claude-code
  - RAG
  - grep
  - agentic-search
---

# 为什么 Claude Code 不用 RAG 检索代码，而是 grep？

Claude Code 的代码搜索又快又准，核心只用三个工具：**Glob、Grep、Read**。没有向量数据库，没有 Embedding 模型，没有索引构建过程。Anthropic 内部称之为 **Agentic Search**（智能体搜索）。

## 一、Claude Code 怎么查找代码

三个工具：

| 工具 | 职责 | 底层实现 |
| --- | --- | --- |
| **Glob** | 按文件名模式匹配（如 `**/*.java`） | 文件系统扫描，按修改时间排序 |
| **Grep** | 在文件内搜索关键词 | ripgrep（Rust 写的高性能搜索） |
| **Read** | 读取具体文件内容 | 支持图片/PDF/Jupyter，可指定行号范围 |

三个工具都是 `isConcurrencySafe = true` 的只读工具，可以并行执行。Claude Code 经常同时发起多个 Grep 搜索，一次性扫描多个关键词。

**Agentic Search 核心思路**：不预先构建任何索引，而是让 Agent 在执行任务过程中，根据当前上下文和目标，动态决定搜什么、怎么搜、搜到之后下一步干什么。

工作流程：Glob 看目录结构 → Grep 搜关键词 → Read 读相关文件 → LLM 判断 → 决定下一步搜什么。

## 二、RAG 检索代码的五个问题

### 2.1 代码不是自然语言，语义相似度不管用

RAG 的核心逻辑是把文本转成向量，用余弦相似度找"语义最接近"的内容。但代码不一样：

- `createD1HttpClient` 和 `buildD1HttpClient` 语义接近，但可能是两个完全不同的函数。要找的是精确的函数名，不是"差不多的"
- `handleAuth` 和 `validateJwtToken` 语义不相关，但后者可能是前者内部调用的关键逻辑。向量相似度找不到调用关系，但 `grep validateJwtToken` 能精确定位

代码世界里，**精确匹配比语义匹配重要得多**。变量名、方法签名、import 路径，要么完全匹配，要么就是找错了。没有"大概对"这回事。

### 2.2 索引同步成本很高

代码不断变化——改了方法名，RAG 索引里还是旧名字；新增文件，索引里没有；删了类，索引里还在。保持索引实时同步需要增量更新、文件监听、冲突处理，复杂度比 RAG 本身还高。

而 grep 天然不存在这个问题——搜索的永远是磁盘上此时此刻的文件内容。

### 2.3 安全和隐私

RAG 需要 Embedding 模型：要么本地跑（消耗计算资源），要么调用远程 API（代码发到外部服务器）。代码库是高度敏感的资产。

grep 直接在本地磁盘搜索，从安全角度看是碾压级优势。

### 2.4 搜索精度

向量检索返回的是"相关"片段，Agent 还得二次理解和筛选。grep 返回的是精确的代码行和文件路径，Agent 拿到就能直接用。

### 2.5 依赖链路

RAG 流程：查询→Embedding→向量数据库 KNN→Rerank→生成（至少 8 个步骤、四五个服务）。grep：一个二进制文件、一次磁盘扫描。

## 三、ripgrep 为什么这么猛

Claude Code 用的不是 GNU grep，而是 **ripgrep**——Rust 写的现代搜索工具。

ripgrep 作者 Andrew Gallant 在 Rust 正则表达式引擎上花了两年半。引擎用 SIMD 指令集加速，搜索速度能逼近内存带宽的极限。

**性能对比**：几万个文件的中型仓库，ripgrep 全文搜索约 **200 毫秒**。同样任务走 RAG 流程需要多次网络往返，耗时数倍。

ripgrep 对 Agent 友好的特性：

- 默认递归搜索整个目录
- 自动跳过 `.gitignore` 文件和二进制文件
- 输出自带文件名和行号

Claude Code 的 Grep 工具在 ripgrep 之上的封装：

- 默认最多返回 250 行（`head_limit` 控制），防止上下文窗口撑爆
- ripgrep 超时但有部分结果时，丢掉最后不完整行，返回已有部分
- 完全没有结果才抛超时错误

**"尽力返回结果"** 的设计哲学，vs RAG 的"要么成功要么失败"。

## 四、Anthropic 官方怎么说

来源：Boris Cherny（Claude Code 首席工程师）2025 年 5 月 7 日在 Latent Space 播客原话。

**Claude Code 早期版本确实用过 RAG**——Voyage 的 Embedding 模型，做了本地向量索引。效果"还行"。但后来试了 Glob + Grep + Read 的 Agentic Search，结果在各项指标上全面碾压 RAG。

Boris 原话："**outperformed everything, by a lot**"（全面超越，而且差距很大）。

放弃 RAG 的两个核心原因：

1. **性能**：Agentic Search 搜索质量更高。grep 返回精确代码行和文件路径，Agent 直接用；RAG 返回"相关"片段，需要二次筛选
2. **简洁**：RAG 需要维护索引同步、增量更新、向量数据库生命周期。Agentic Search 不需要预处理，打开仓库直接搜

## 五、亚马逊论文实锤

2025 年 12 月，亚马逊科学团队论文：**"Keyword search is all you need: Achieving RAG-Level Performance without vector databases using agentic tool use"**

研究方法：标准 RAG 系统 vs 只有关键词搜索工具的 Agent 系统，相同问答任务对比。

结论：**基于关键词搜索的 Agent 系统可以达到传统 RAG 系统 90% 以上的性能指标。**

关键发现：对于代码这种符号精确的结构化文本，关键词搜索的表现实际上**比语义检索还要好**。因为代码的命名约定通常一致，函数名、变量名、类名本身就携带了足够的语义信息。

## 六、Cursor 的反面论证

Cursor 训练了自己的 Embedding 模型，用 Turbopuffer 做向量数据库。A/B 测试结果：加入语义搜索后，Agent 准确率提升不少。超过 1000 个文件的大型仓库中，代码留存率增加了 2.6%。

但几个关键区别：

1. **Cursor 是 IDE 产品**，用户在 IDE 里工作时仓库相对稳定，索引同步压力小。Claude Code 是命令行工具，用户可能随时切换仓库
2. **Cursor 用的是混合检索**（grep + 向量搜索），不是只用向量搜索。结论是"两者配合最好"——**反过来证明 grep 是不可或缺的基础能力**

## 七、LLM 就是最好的 Reranker

传统 RAG 流程：Embedding → 向量检索 → Rerank → 生成。Rerank 是为了弥补向量检索精度不够的问题。

在 Claude Code 的架构里，grep 返回确定性结果。Agent 拿到精确搜索结果后，用 LLM 自身的推理能力判断哪些有用、接下来应该读哪个文件、还需要搜什么关键词。

LLM 做的不是简单的 Rerank，而是**理解 + 决策 + 行动**。它会根据第一轮搜索结果调整后续搜索策略——发现一个关键函数调用后，顺藤摸瓜去搜被调用的函数定义。这种**多轮迭代的搜索能力**，是 RAG 的"一次检索"模式做不到的。

类比：

- **RAG** 像去图书馆让管理员帮忙找书——管理员根据描述找了几本"可能相关"的放桌上，对不对得自己翻
- **Agentic Search** 像自己去图书馆——先看楼层指引（Glob 看目录），再去书架找（Grep 搜内容），找到翻开看看（Read 读文件），不对就换关键词再找
