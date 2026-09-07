---
title: 一个 Deployment 就能跑 vLLM，为什么还需要 KServe？
tags:
  - knowledgebase/source
  - ai/inference
  - kubernetes/kserve
date: 2026-09-07
aliases:
  - KServe 部署 vLLM 来源摘要
---

# 一个 Deployment 就能跑 vLLM，为什么还需要 KServe？

## 元信息

- **原始文档**：[[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]
- **剪藏来源**：[[0raw/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]
- **领域**：企业级大模型推理、Kubernetes
- **摄入日期**：2026-09-07

## 摘要

单个 vLLM 服务可以直接由 Kubernetes Deployment 承载，但多模型场景会重复处理模型来源、Runtime、GPU、网络暴露等配置。文章以 KServe 0.18.0 的 InferenceService Standard 模式为主线，完整演示 cert-manager、Envoy Gateway、KServe Runtime、PVC 模型存储、GPU 资源声明和 OpenAI 兼容 API 验证，说明 KServe 的核心价值是将模型服务纳入统一、声明式的生命周期管理。

## 关键知识点

1. KServe 不负责模型计算，而是根据 `InferenceService` 选择 Runtime，并创建 Deployment、Service、HTTPRoute 等底层资源。
2. 单 GPU、常驻 vLLM 服务优先考虑 InferenceService Standard；需要 Scale to Zero 和请求驱动伸缩时考虑 Knative；需要 Prefill/Decode 分离和智能路由时使用独立的 LLMInferenceService API。
3. 部署前必须确认 Kubernetes 暴露 `nvidia.com/gpu`；否则推理 Pod 会因无法调度而持续 Pending。
4. 示例使用 PVC 加载 Qwen2.5-0.5B-Instruct，通过 HuggingFaceServer 调用 vLLM，并由 Envoy Gateway 提供 OpenAI 兼容接口。
5. hostPath 静态 PV 只适合单节点验证；生产环境应采用 CephFS、NFS、JuiceFS 等共享存储。
6. 首次启动包含模型读取、CUDA 初始化和 CUDA Graph 预热，慢磁盘环境可能耗时十几分钟，需要留足启动等待时间。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]
- [[KnowledgeBase/entities/Prometheus]]
- [[KnowledgeBase/concepts/KV Cache]]
- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]
- [[Docker-Kubernetes/k8s-scaling/KServe+KEDA实战-基于请求指标实现服务自动扩缩容]]

## 值得注意

- KServe 与 vLLM 不是替代关系：vLLM 是推理引擎，KServe 是模型服务控制与编排层。
- Standard、Knative 是 InferenceService 的部署模式；LLMInferenceService 是另一套 API，不能把三者视为同一层级的三种模式。
- 示例中的 Qwen2.5-0.5B-Instruct 用于验证部署链路，不代表生产模型质量。
