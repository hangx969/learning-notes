---
title: Ingress
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/k8s-networking-service-mesh-batch-summary|k8s-networking-service-mesh 来源批量摘要]]"
---

# Ingress

## 定义
Kubernetes Ingress 是集群对外暴露 HTTP/HTTPS 服务的 API 资源，通过 Ingress Controller（如 nginx-ingress）实现路由、负载均衡、TLS 终止等功能。本仓库有一篇 2399 行的深度长文详解 Ingress 各方面用法。

## 编译知识

### Ingress-Nginx 部署要点
- **hostNetwork 模式**：Pod 使用宿主机网络栈，直接开启 80/443 端口，适用于裸金属（Bare-metal）环境
- **ClusterFirstWithHostNet** DNS 策略：解决 hostNetwork 模式下无法解析集群内部服务名的问题
- 建议 DaemonSet 或至少 3 副本确保每个节点都能接收请求
- 通过 [[KnowledgeBase/entities/Helm|Helm]] 部署（ingress-nginx Chart）

### DNS 解析链路
- External-DNS（外部域名同步到 DNS 提供商如 Azure DNS） -> CoreDNS（集群内解析） -> Ingress-Nginx/[[KnowledgeBase/entities/Istio|Istio]] Gateway（流量入口），形成完整的 DNS 到流量转发链路

### 南北流量 vs 东西流量
- Ingress 负责集群外到集群内的**南北流量**管理
- Istio 侧重于集群内服务间的**东西流量**管理
- 两者可以协同工作，Ingress 作为外部入口，Istio 管理内部服务间通信

### 与其他组件的集成
- 多篇文章中 Ingress 与 OAuth2 Proxy 配合实现访问控制（如 Pact Broker 部署）
- Jenkins DevOps 平台中 Harbor 必须用 NodePort 而非 Ingress 暴露（JNLP Pod 内 CoreDNS 无法解析 Ingress 域名）

## 在本仓库中的位置
核心文章位于 `Docker-Kubernetes/k8s-basic-resources/`，Ingress Controller 的 Helm 部署位于 `Docker-Kubernetes/k8s-networking-service-mesh/`。

## 相关文章
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-ingress|k8s基础-ingress]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|helm部署ingress-nginx]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns|helm部署external-dns]]
- [[Docker-Kubernetes/k8s-basic-resources/k8s基础-Service|k8s基础-Service]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全|k8s集群网络安全]]

## 关联概念
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Istio|Istio]]
- [[KnowledgeBase/entities/Helm|Helm]]

## 可延展方向
- Kubernetes Gateway API 作为 Ingress 的继任者
- Ingress Controller 对比（Nginx vs Traefik vs Envoy）
- Ingress 与 Cert-Manager 自动化证书管理
