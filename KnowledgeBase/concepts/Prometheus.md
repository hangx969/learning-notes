---
title: Prometheus
tags:
  - knowledgebase/concept
date: 2026-04-16
---

# Prometheus

## 定义
Prometheus 是开源的系统监控与告警工具，采用拉取（pull）模式采集指标，支持 PromQL 查询语言、Alertmanager 告警管理、联邦集群等特性。本仓库记录了 10+ 篇相关文章，覆盖从二进制部署到 Helm 全家桶。

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-monitoring-logging/` 目录，也有 Docker 场景的部署文章在 `Docker-Kubernetes/docker/` 中。

## 相关文章
- [Prometheus基础](../../Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础.md)
- [Prometheus监控k8s系统组件](../../Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件.md)
- [Prometheus监控外部k8s集群](../../Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群.md)
- [Prometheus监控非云原生应用-主机](../../Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机.md)
- [k8s监控Prometheus(v2.2.1)](../../Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.2.1))
- [k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)](../../Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5))
- [k8s监控alertmanager(v0.14.0)](../../Docker-Kubernetes/k8s-monitoring-logging/k8s监控alertmanager(v0.14.0))
- [二进制部署Prometheus(v2.32.1)联邦集群](../../Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群)
- [二进制部署prometheus-grafana-nodeexporter](../../Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter.md)
- [helm部署prometheus-stack全家桶](../../Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md)
- [docker部署prometheus-grafana-cAdvisior监控](../../Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控.md)

## 关联概念
- [Grafana](Grafana.md)
- [Kubernetes](Kubernetes.md)
- [Helm](Helm.md)
- [Docker](Docker.md)

## 可延展方向
- Prometheus 长期存储方案（Thanos / Mimir）
- Prometheus Operator 与 ServiceMonitor 深入
- PromQL 高级查询与告警规则设计
