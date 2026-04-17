---
title: Helm
tags:
  - knowledgebase/entity
date: 2026-04-16
---

# Helm

## 定义
Helm 是 Kubernetes 的包管理器，通过 Chart 模板化管理 K8s 资源的安装、升级与回滚。本仓库中有 20+ 篇使用 Helm 部署各类组件的文章，是 K8s 生态中最高频的部署工具。

## 在本仓库中的位置
Helm 基础位于 `Docker-Kubernetes/helm-operator/`，同时大量 helm 部署文章分布在监控、CI/CD、安全、网络、存储等各子目录中。

## 相关文章
- [[Docker-Kubernetes/helm-operator/helmv3-安装与使用|helmv3-安装与使用]]
- [[Docker-Kubernetes/helm-operator/helm部署dragonfly|helm部署dragonfly]]
- [[Docker-Kubernetes/helm-operator/helm部署reloader|helm部署reloader]]
- [[Docker-Kubernetes/helm-operator/helm部署config-syncer(kubed)|helm部署config-syncer(kubed)]]
- [[Docker-Kubernetes/helm-operator/helm部署tomcat|helm部署tomcat]]
- [[Docker-Kubernetes/helm-operator/helm部署pact-broker|helm部署pact-broker]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶|helm部署Loki-promtail-tempo-grafanaAgent全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署jaeger|helm部署jaeger]]
- [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台|基于helm+operator部署ECK日志收集平台]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|helm部署ingress-nginx]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm安装istio|helm安装istio]]
- [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns|helm部署external-dns]]
- [[Docker-Kubernetes/k8s-CICD/Jenkins/helm部署jenkins|helm部署jenkins]]
- [[Docker-Kubernetes/harbor/helm部署harbor|helm部署harbor]]
- [[Docker-Kubernetes/k8s-security-auth/helm部署certmanager|helm部署certmanager]]
- [[Docker-Kubernetes/k8s-security-auth/helm部署kyverno和policy-reporter|helm部署kyverno和policy-reporter]]
- [[Docker-Kubernetes/k8s-security-auth/helm部署trivy-operator|helm部署trivy-operator]]
- [[Docker-Kubernetes/k8s-scaling/helm部署vpa|helm部署vpa]]
- [[Docker-Kubernetes/k8s-scaling/helm部署goldilocks|helm部署goldilocks]]

## 关联概念
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/ArgoCD|ArgoCD]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[KnowledgeBase/entities/Istio|Istio]]
- [[KnowledgeBase/entities/Ingress|Ingress]]

## 可延展方向
- Helm Chart 开发与测试最佳实践
- Helm vs Kustomize 对比
- Helm Secrets 与敏感数据管理
