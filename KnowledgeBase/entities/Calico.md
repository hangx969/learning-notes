---
title: Calico
tags:
  - knowledgebase/entity
  - kubernetes/networking
  - cni
date: 2026-04-17
---

## 简介

Calico 是 Kubernetes 生态中最流行的 CNI（Container Network Interface）网络插件之一，支持 IPIP 隧道和 BGP 直连两种网络模式。它提供网络策略（NetworkPolicy）支持，与 Service 网络和 Ingress 形成 K8s 三层网络协作体系。

## 在本仓库中的位置

- `Docker-Kubernetes/k8s-installation/` 中涉及 Calico CNI 部署
- `Docker-Kubernetes/k8s-basic-resources/` 中涉及 K8s 三层网络协作（Calico + Service + Ingress）
- ArgoCD 部署中涉及 Calico 与 CoreDNS 的 DNS 解析问题排查

## 相关概念与实体

- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：Calico 作为 K8s CNI 插件
- [[KnowledgeBase/entities/Ingress|Ingress]]：与 Calico 协作的三层网络之一
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]：部署中涉及 Calico DNS 问题
- [[KnowledgeBase/concepts/ServiceMesh|ServiceMesh]]：东西流量管理的上层方案
