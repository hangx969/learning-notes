---
title: ModelScope
tags:
  - knowledgebase/entity
  - ai/model-registry
date: 2026-09-13
sources:
  - "[[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]"
  - "[[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]"
  - "[[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]"
aliases:
  - 魔搭社区
  - ModelScope 魔搭
---

# ModelScope

## 简介

ModelScope（魔搭社区）是模型、数据集和 AI 应用的开放平台，可通过网页、CLI、SDK 或 Git 获取模型资产。在国内网络环境中，它可作为 Hugging Face 之外的模型下载来源，但生产交付仍需固定版本并记录校验信息。

## 核心功能

- 模型与数据集托管、检索和下载；
- `modelscope download --model ... --local_dir ...` CLI；
- Python SDK 的 `snapshot_download`；
- 支持将模型下载到显式目录，便于离线复制和平台接入。

## 使用场景

- 国内环境中的模型下载与缓存；
- 向离线 GPU 服务器准备模型资产；
- 为 vLLM、SGLang、KServe 等 Serving 平台准备完整模型仓库；
- 对模型 Revision、许可证和校验和做资产登记。

## 相关概念与实体

- [[KnowledgeBase/entities/vLLM]]：加载模型仓库并提供高吞吐推理 API。
- [[KnowledgeBase/entities/Ollama]]：另一种集模型获取、管理和运行于一体的本地入口。
- [[KnowledgeBase/entities/Docker]]：与模型资产一起组成离线交付物。
- [[KnowledgeBase/entities/Kubernetes]]：承载模型服务和 GPU Worker。

## 在本仓库中的覆盖

- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]：为 Kubernetes 推理服务准备模型文件。
- [[AI/企业级私有化大模型/一个 Deployment 就能跑 vLLM，为什么还需要 KServe？]]：模型来源与 PVC 加载链路。
- [[AI/企业级私有化大模型/大模型本地部署选型-Ollama-vLLM-SGLang-vLLM-Omni]]：下载、目录规划、rsync 和离线镜像交付。

## 知识空白

- 企业内部 Model Registry 与 ModelScope 同步机制；
- 模型供应链签名、SBOM、恶意代码审查和许可证准入；
- 大规模模型缓存、去重与生命周期策略。
