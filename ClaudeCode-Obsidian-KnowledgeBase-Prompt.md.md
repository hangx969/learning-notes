# Claude Code 执行稿：基于 learning-notes 仓库构建 Obsidian AI 知识库

你现在是我的知识库编译助手。请基于当前仓库 `learning-notes` 执行一轮“最小侵入、增量增强”的 Obsidian AI 知识库建设。

## 背景

这个仓库已经有大量现成目录结构和 Markdown 文档，分类体系已经比较成熟。
你的任务不是重构仓库，也不是大规模迁移文件，而是在 **尽量不改动现有目录结构** 的前提下，增加一层适合 Obsidian + Claude Code 使用的“知识编译层”。

## 绝对约束

1. **不要大规模改动现有目录结构**
   - 不要批量移动已有 Markdown 文件
   - 不要大规模重命名目录
   - 不要重建一套替代当前仓库的分类体系
   - 不要复制全部原文到新目录

2. **只允许新增一个顶层目录：`KnowledgeBase/`**
   所有新增的知识编译产物都放在这个目录下。

3. **现有文档继续作为原始知识源**
   原则上不要重写原文，只做必要的轻量增强。

4. **新增页面优先使用 Obsidian 风格**
   - 使用 `[[wikilink]]`
   - 合理使用标题层级
   - 页面结构清晰，适合导航和分析

## 新增目录结构

请新增以下结构：

```text
KnowledgeBase/
  INDEX.md
  inventory/
  concepts/
  maps/
  analysis/
  maintenance/
```

## 总体目标

完成后，这个仓库应该具备以下能力：

1. 能盘点全库内容
2. 能按领域、工具、主题导航
3. 能通过概念页形成知识网络
4. 能识别高价值知识空白
5. 能支持后续新增文档的增量维护

---

# 执行阶段

请严格按顺序执行。

## 阶段 1：全库扫描与盘点

目标：先理解仓库，不急着生成大量页面。

请完成：

1. 扫描整个仓库中的 Markdown 文件
2. 识别主要顶层目录及其主题
3. 统计各领域文档数量与内容密度
4. 提取每篇文档的基本信息：
   - 标题
   - 路径
   - 所属领域
   - 粗略主题
   - 是否有 frontmatter
   - 是否已有 Obsidian 双链痕迹
5. 输出以下文件：
   - `KnowledgeBase/inventory/repository-inventory.md`
   - `KnowledgeBase/inventory/domain-summary.md`

要求：
- `repository-inventory.md` 按主要目录组织文档概览
- `domain-summary.md` 总结各领域内容特点、强项、关联性、是否适合优先编译

---

## 阶段 2：建立知识库入口和基础地图

目标：为整个仓库建立统一导航入口。

请创建以下文件：

- `KnowledgeBase/INDEX.md`
- `KnowledgeBase/maps/domain-map.md`
- `KnowledgeBase/maps/tool-map.md`

要求：

### `KnowledgeBase/INDEX.md`
至少包含：
- 知识库说明
- 主要入口链接
- 按领域导航
- 推荐优先阅读主题
- 分析报告入口

### `KnowledgeBase/maps/domain-map.md`
按现有顶层目录建立领域地图，例如：
- [[AI]]
- [[Docker-Kubernetes]]
- [[Linux-Shell]]
- [[Python]]
- [[Azure]]
- [[Aliyun]]
- [[CloudComputing]]
- [[Networking]]
- [[Database]]
- [[HPC]]
- [[IaC]]

每个领域下说明：
- 覆盖范围
- 重点子目录
- 代表性文章
- 关联领域

### `KnowledgeBase/maps/tool-map.md`
按工具/平台聚合知识，例如：
- [[Claude Code]]
- [[OpenClaw]]
- [[MCP]]
- [[Obsidian]]
- [[Docker]]
- [[Kubernetes]]
- [[Helm]]
- [[Prometheus]]
- [[Grafana]]
- [[Terraform]]
- [[Python]]

要求：列出与这些工具相关的现有文档路径与推荐入口。

---

## 阶段 3：提取高频概念并生成概念页

目标：构建仓库的概念层，而不是复制原文。

请完成：

1. 从仓库中提取高频概念、工具名、平台名、关键主题词
2. 做命名去重和标准化
3. 首轮只生成 **20~30 个高价值概念页**
4. 输出到：
   - `KnowledgeBase/concepts/`

优先概念：
- Claude Code
- OpenClaw
- MCP
- Obsidian
- Docker
- Kubernetes
- Helm
- Prometheus
- Grafana
- Terraform
- Azure
- Aliyun
- AKS
- CI/CD
- Observability
- 容器运行时
- 服务网格
- 日志系统
- 自动化运维
- Python 运维开发

每个概念页使用如下模板：

```md
# 概念名称

## 定义
用简洁语言解释该概念在本仓库语境中的含义。

## 在本仓库中的位置
它主要出现在哪些目录、主题、场景中。

## 相关文章
- [[相关文章 A]]
- [[相关文章 B]]

## 关联概念
- [[概念 X]]
- [[概念 Y]]

## 可延展方向
- 后续还可以扩展的主题
```

要求：
- 高价值优先，低频噪音不要强行建页
- 统一命名，避免同一概念多种写法
- 多使用 `[[wikilink]]`

---

## 阶段 4：建立专题地图页

目标：围绕高密度知识区生成导航型专题页。

请优先生成以下专题地图：

- `KnowledgeBase/maps/ai-workflow-map.md`
- `KnowledgeBase/maps/claude-code-openclaw-map.md`
- `KnowledgeBase/maps/kubernetes-map.md`
- `KnowledgeBase/maps/linux-ops-map.md`
- `KnowledgeBase/maps/python-devops-map.md`
- `KnowledgeBase/maps/cloud-platform-map.md`

每个专题地图页包含：
1. 专题范围说明
2. 核心概念
3. 推荐阅读顺序
4. 代表性文章
5. 相关工具
6. 相关领域之间的连接关系

要求：
- 这些页面是导航层，不是重写教材
- 重点是帮助快速定位内容和发现知识链路

---

## 阶段 5：分析内容覆盖与知识缺口

目标：发现已经覆盖的重点和未来值得继续写的空白。

请生成以下文件：

- `KnowledgeBase/analysis/topic-coverage-analysis.md`
- `KnowledgeBase/analysis/high-value-gaps.md`
- `KnowledgeBase/analysis/next-writing-suggestions.md`

要求：

### `topic-coverage-analysis.md`
分析：
- 当前仓库最密集的主题
- 已形成体系的主题
- 仍然零散、未系统化的主题

### `high-value-gaps.md`
识别：
- 多次提到但没有专门概念页/专题页的主题
- 应该存在但当前明显偏空白的领域
- 高价值但低连接的知识孤岛

### `next-writing-suggestions.md`
给出 10 个值得继续补写或系统化的主题，并说明：
- 为什么值得写
- 与当前仓库哪些内容相关
- 能补上哪块知识空白

---

## 阶段 6：断链检查与命名规范

目标：让双链网络更稳定，但不要过度造页。

请完成：

1. 扫描 `KnowledgeBase/` 中所有 `[[wikilink]]`
2. 找出没有对应页面的断链
3. 区分高频断链与低频断链
4. 输出：
   - `KnowledgeBase/maintenance/broken-links-report.md`
   - `KnowledgeBase/maintenance/naming-normalization.md`

规则：
- 高频断链：建议补建页
- 低频断链：记录即可
- 遇到同义命名时统一规范，例如：
  - ClaudeCode → Claude Code
  - k8s → Kubernetes（必要时说明别名）
  - OpenClaw / openclaw 统一写法

---

## 阶段 7：增量维护机制

目标：让知识编译层以后可持续更新。

请创建：

- `KnowledgeBase/maintenance/update-workflow.md`

该文件应说明：
1. 新增一篇文档后，如何更新知识库
2. 何时补概念页
3. 何时更新专题地图
4. 何时更新索引页
5. 何时做断链巡检
6. 哪些步骤适合自动化，哪些步骤适合人工确认

---

# 执行风格要求

1. 先观察，再生成
2. 以“新增增强”为主，不推翻现有结构
3. 避免制造大量模板化废页
4. 新增页面要有真正的导航和分析价值
5. 每完成一个阶段：
   - 简要总结结果
   - 列出新增文件
   - 再继续下一个阶段

---

# 最终交付要求

至少完成以下内容：

- `KnowledgeBase/INDEX.md`
- `KnowledgeBase/inventory/repository-inventory.md`
- `KnowledgeBase/inventory/domain-summary.md`
- `KnowledgeBase/maps/domain-map.md`
- `KnowledgeBase/maps/tool-map.md`
- 20~30 个高价值概念页
- 4~6 个专题地图页
- `KnowledgeBase/analysis/topic-coverage-analysis.md`
- `KnowledgeBase/analysis/high-value-gaps.md`
- `KnowledgeBase/analysis/next-writing-suggestions.md`
- `KnowledgeBase/maintenance/broken-links-report.md`
- `KnowledgeBase/maintenance/naming-normalization.md`
- `KnowledgeBase/maintenance/update-workflow.md`

---

# 现在开始

请从 **阶段 1：全库扫描与盘点** 开始。

先做这三件事：
1. 用你自己的话总结当前仓库结构和主要领域
2. 给出你准备新增的 `KnowledgeBase/` 目录方案
3. 列出阶段 1 将要生成的文件和内容提纲

等我确认后，再开始实际写入文件。
