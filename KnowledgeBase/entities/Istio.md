---
title: Istio
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary|k8s-networking-service-mesh 来源批量摘要]]"
---

# Istio

## 定义
Istio 是 Kubernetes 生态中最主流的服务网格（Service Mesh）实现，提供流量管理、可观测性、安全通信等能力。本仓库以 7 篇文章记录了 Istio 的部署、精细化流量管理与企业项目接入实战。

## 编译知识

### 核心架构
- **数据平面**：Envoy Sidecar 代理注入到每个 Pod，拦截所有进出流量
- **控制平面**：Istio 1.5+ 将原有多组件（Pilot、Mixer、Citadel）**整合为 istiod 单体**
- Pilot 负责服务发现与配置分发；Envoy 作为 Sidecar 代理执行流量策略

### 服务网格解决的问题
- 服务间通信、流量精细化管理、安全通信（mTLS）、多语言治理、可观测性
- 核心功能：负载均衡、服务发现、**熔断降级**、动态路由、故障注入、错误重试、安全通信
- 架构演变：单体应用 -> 微服务 -> 服务网格，流量治理功能**下沉到基础设施**
- 对比 SpringCloud/Nacos：服务网格语言无关，无需侵入业务代码

### 部署方式
- **[[KnowledgeBase/entities/Helm|Helm]] 分步安装**（v1.27.1）：istio-base -> istiod -> gateway，三个 Chart 按顺序安装
- **istioctl 安装**（v1.13.1）：命令行一键部署
- Gateway 配置 NodePort 类型暴露，适用于本地裸金属集群

### 流量管理
- **熔断机制**：快速失败返回、故障隔离、恢复机制、自动重试
- **超时控制**：防止请求无限期等待，提高系统稳定性
- 南北流量通过 IngressGateway 管理，东西流量通过 Sidecar 管理

### 企业项目接入
- 两种场景：Sidecar 东西流量管理 vs IngressGateway 南北流量管理
- 新项目按 Istio 规范创建 Deployment/Service 和核心资源（VirtualService、DestinationRule、Gateway）
- 已部署项目需修改 Deployment/Service，按需转换为 IngressGateway
- 建议所有 Deployment 配置 **version 标签**以支持流量分割

### 与 Ingress 的协同
- [[KnowledgeBase/entities/Ingress|Ingress]]-Nginx 负责集群外到集群内的**南北流量**，Istio 侧重于集群内服务间的**东西流量**管理，两者可以协同工作

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-networking-service-mesh/` 目录。

## 相关文章
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s部署istio(1.13.1)|k8s部署istio(1.13.1)]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm安装istio|helm安装istio]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio|k8s精细化流量管理-istio]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/企业项目接入istio实战|企业项目接入istio实战]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|helm部署ingress-nginx]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns|helm部署external-dns]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全|k8s集群网络安全]]

## 关联概念
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Ingress|Ingress]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]

## 可延展方向
- Istio Ambient Mesh（无 Sidecar 模式）
- Istio 与 Gateway API 的集成
- 多集群 Istio 服务网格
