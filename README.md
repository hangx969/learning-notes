# 云原生与基础设施学习笔记

涵盖云原生技术、基础设施自动化、编程语言、AI/ML 和现代 DevOps 实践的综合知识库。

> **~460 篇文档 · 17 个技术领域 · 109 篇知识编译层文件**

## 🧭 知识库导航（KnowledgeBase）

本仓库在原始文档之上构建了一个 **知识编译层**（[Karpathy LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)），提供全局导航、概念网络和分析报告，无需逐篇翻找。

**→ [进入知识库首页](./KnowledgeBase/INDEX.md)**

| 类型 | 说明 | 入口 |
| --- | --- | --- |
| 📋 全库盘点 | 文档逐一索引 | [repository-inventory](./KnowledgeBase/inventory/repository-inventory.md) |
| 🗺️ 领域地图 | 按技术领域导航 | [domain-map](./KnowledgeBase/maps/domain-map.md) |
| 🔧 工具地图 | 按工具/平台聚合 | [tool-map](./KnowledgeBase/maps/tool-map.md) |
| ☸️ K8s 专题 | 151 篇 K8s 生态导航 | [kubernetes-map](./KnowledgeBase/maps/kubernetes-map.md) |
| 🤖 AI 专题 | Claude Code + OpenClaw + Hermes Agent | [ai-workflow-map](./KnowledgeBase/maps/ai-workflow-map.md) |
| ☁️ 云平台专题 | Aliyun vs Azure 对标 | [cloud-platform-map](./KnowledgeBase/maps/cloud-platform-map.md) |
| 🐧 Linux 运维 | 系统管理 + HPC + GPU | [linux-ops-map](./KnowledgeBase/maps/linux-ops-map.md) |
| 🐍 Python 运维 | 27 篇 Python 开发导航 | [python-devops-map](./KnowledgeBase/maps/python-devops-map.md) |
| 📈 覆盖分析 | 主题深度与缺口识别 | [topic-coverage-analysis](./KnowledgeBase/analysis/topic-coverage-analysis.md) |
| ✏️ 写作建议 | 推荐补写方向 | [next-writing-suggestions](./KnowledgeBase/analysis/next-writing-suggestions.md) |

## 📊 领域概览

| 领域 | 篇数 | 成熟度 | 亮点 |
| --- | ---: | :---: | --- |
| Docker-Kubernetes | 151 | 🟢 | 基础资源→安装管理→监控日志→CI/CD→网络→安全→扩缩容→存储→中间件，全生命周期 |
| AI | 128 | 🟢 | Claude Code（9 篇深度）+ OpenClaw（8 篇）+ Hermes Agent（4 篇）+ RAG + 视觉 + 行业动态 |
| Python | 27 | 🟢 | 基础→运维开发→网络编程→数据分析→项目实战 |
| Linux-Shell | 24 | 🟡 | 系统管理 + Shell 脚本 + SSH/网络 + 存储/LVM/NFS |
| Azure | 21 | 🟢 | VM/VMSS + AKS + 网络/存储 + DevOps Pipeline + Policy |
| Aliyun | 19 | 🟢 | ECS/ESS + VPC/SLB/WAF + OSS + RDS/DTS + Landing Zone |
| Go | 9 | 🟡 | 环境配置→变量→控制流→OOP→云原生选型 |
| HPC + Cloud + GPU | 18 | 🟡 | Slurm/PBS + 云原生/微服务 + CUDA/驱动 |
| 杂项 | 18 | 🟡 | Database + Middlewares + OS + Networking + IaC + Git + C++ |

## 🚀 推荐阅读路径

### 云原生入门
1. [云原生概念](./CloudComputing/云原生.md) → 理解云原生哲学
2. [Docker 基础](./Docker-Kubernetes/docker/docker基础.md) → 容器基础
3. [K8s 架构](./Docker-Kubernetes/k8s-basic-resources/k8s基础-架构-组件-资源.md) → K8s 架构总览
4. [API Server 深度剖析](./Docker-Kubernetes/k8s-basic-resources/k8s-APIServer深度剖析-请求链路-认证授权-生产调优.md) → 请求链路与认证授权
5. [Prometheus 全家桶](./Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md) → 可观测性
6. [OpenTelemetry 统一可观测性](./Docker-Kubernetes/k8s-monitoring-logging/OpenTelemetry实战-统一Traces-Metrics-Logs.md) → 下一代可观测性
7. [K8s 成本优化](./Docker-Kubernetes/k8s-scaling/k8s成本优化方案-FinOps实战.md) → FinOps 实战

### AI 赋能运维
1. [Claude Code 指南](Claude%20Code%20基础指南.md) → 入门必读
2. [扩展体系（MCP/Skills/Plugin）](./AI/ClaudeCode/Claude%20Code%20扩展体系.md) → 四层扩展机制
3. [CLAUDE.md 12 条规则](./AI/ClaudeCode/CLAUDE.md最佳实践-12条规则模板.md) → 错误率 41%→3%
4. [为什么 grep 不用 RAG](./AI/ClaudeCode/Claude-Code为什么用grep不用RAG.md) → Agentic Search 架构
5. [OpenClaw 安装](./AI/OpenClaw/OpenClaw-基础-安装.md) → 开源 AI 工具平台
6. [OpenClaw K8s 智能运维](./AI/OpenClaw/OpenClaw-K8s智能运维实战.md) → 三阶段渐进式 AIOps

### 云平台实战
1. [VPC](./Aliyun/网络/VPC.md) + [Azure 网络](./Azure/6_Azure-Networking.md) → 云网络对比
2. [AKS 基础](./Azure/2_AKS-basics.md) → 托管 K8s 服务
3. [FinOps 云成本优化](./Aliyun/资源管理/FinOps-云成本优化实战.md) → 降本增效

## 📁 目录结构

```
learning-notes/
├── CLAUDE.md                      ← 知识库 Schema（三层架构规约）
├── KnowledgeBase/                 ← 知识编译层（LLM 维护）
│   ├── index.md                   ← 全库内容目录
│   ├── log.md                     ← 操作日志
│   ├── sources/                   ← 原始来源摘要页
│   ├── concepts/                  ← 概念页（14 篇）
│   ├── entities/                  ← 实体页（35 篇）
│   ├── maps/                      ← 主题地图（8 篇）
│   ├── analysis/                  ← 分析报告
│   ├── inventory/                 ← 文档盘点
│   └── maintenance/               ← 维护报告
│
├── AI/                            ← AI 工具与实践（128 篇）
│   ├── ClaudeCode/                ← Claude Code 深度文章
│   ├── OpenClaw/                  ← OpenClaw 多智能体平台
│   ├── Hermes-agent/              ← Hermes Agent 框架
│   ├── RAG-Agent-项目/            ← RAG 知识库项目
│   ├── AI-视觉/                   ← PPT/动画/HTML 生成
│   └── 行业动态/                   ← AI 趋势与洞察
│
├── Docker-Kubernetes/             ← K8s 全生态（151 篇）
│   ├── docker/                    ← Docker 基础
│   ├── k8s-basic-resources/       ← K8s 核心资源 + API Server
│   ├── k8s-installation-management/ ← 安装管理 + cgroup v2
│   ├── k8s-monitoring-logging/    ← 监控日志 + OTel + 审计
│   ├── k8s-CICD/                  ← CI/CD（ArgoCD/Jenkins/Tekton）
│   ├── k8s-networking-service-mesh/ ← 网络 + Istio
│   ├── k8s-security-auth/         ← 安全认证
│   ├── k8s-scaling/               ← 扩缩容 + FinOps 成本优化
│   └── ...                        ← 存储/中间件/Helm/Harbor/GPU
│
├── Azure/                         ← Azure 云平台（21 篇）
├── Aliyun/                        ← 阿里云（19 篇）
├── Python/                        ← Python 开发（27 篇）
├── Linux-Shell/                   ← Linux 运维（24 篇）
├── Go/                            ← Go 语言（9 篇）
└── ...                            ← HPC/GPU/Database/IaC 等
```

## 🏗️ 架构说明

本知识库采用 **三层架构**（基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 模式）：

| 层级 | 说明 | 所有权 |
| --- | --- | --- |
| **Raw Sources** | 顶层主题目录中的 markdown 文件 | 人类策划，只读不改 |
| **Wiki** | `KnowledgeBase/` 目录下的所有内容 | LLM 创建和维护 |
| **Schema** | `CLAUDE.md` 规约文件 | 人类与 LLM 共同演进 |

详见 [CLAUDE.md](./CLAUDE.md) 了解完整的页面模板、操作流程和命名约定。
