---
title: Ingress
tags:
  - knowledgebase/entity
date: 2026-04-16
---

# Ingress

## 定义
Kubernetes Ingress 是集群对外暴露 HTTP/HTTPS 服务的 API 资源，通过 Ingress Controller（如 nginx-ingress）实现路由、负载均衡、TLS 终止等功能。本仓库有一篇 2399 行的深度长文详解 Ingress 各方面用法。

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
