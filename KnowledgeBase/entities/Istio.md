---
title: Istio
tags:
  - knowledgebase/concept
date: 2026-04-16
---

# Istio

## 定义
Istio 是 Kubernetes 生态中最主流的服务网格（Service Mesh）实现，提供流量管理、可观测性、安全通信等能力。本仓库以 7 篇文章记录了 Istio 的部署、精细化流量管理与企业项目接入实战。

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-networking-service-mesh/` 目录。

## 相关文章
- [k8s部署istio(1.13.1)](../../Docker-Kubernetes/k8s-networking-service-mesh/k8s部署istio(1.13.1.md))
- [helm安装istio](../../Docker-Kubernetes/k8s-networking-service-mesh/helm安装istio.md)
- [k8s精细化流量管理-istio](../../Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio.md)
- [企业项目接入istio实战](../../Docker-Kubernetes/k8s-networking-service-mesh/企业项目接入istio实战.md)
- [helm部署ingress-nginx](../../Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx.md)
- [helm部署external-dns](../../Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns.md)
- [k8s集群网络安全](../../Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全.md)

## 关联概念
- [Kubernetes](Kubernetes.md)
- [Ingress](Ingress.md)
- [Helm](Helm.md)
- [Prometheus](Prometheus.md)

## 可延展方向
- Istio Ambient Mesh（无 Sidecar 模式）
- Istio 与 Gateway API 的集成
- 多集群 Istio 服务网格
