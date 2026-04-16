---
title: Grafana
tags:
  - knowledgebase/concept
date: 2026-04-16
---

# Grafana

## 定义
Grafana 是开源的数据可视化与仪表盘平台，常与 Prometheus、Loki 等数据源配合使用，提供丰富的图表、告警与面板功能。本仓库中 Grafana 始终与 Prometheus 成对出现，同时也涉及 GPU Exporter 监控场景。

## 在本仓库中的位置
主要出现在 `Docker-Kubernetes/k8s-monitoring-logging/` 目录，以及 Docker 部署场景中。

## 相关文章
- [k8s部署grafana(v5.0.4)](../../Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4))
- [k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)](../../Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5))
- [helm部署prometheus-stack全家桶](../../Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶.md)
- [二进制部署prometheus-grafana-nodeexporter](../../Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter.md)
- [helm部署Loki-promtail-tempo-grafanaAgent全家桶](../../Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶.md)
- [docker部署prometheus-grafana-cAdvisior监控](../../Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控.md)

## 关联概念
- [Prometheus](Prometheus.md)
- [Kubernetes](Kubernetes.md)
- [Helm](Helm.md)
- [Docker](Docker.md)

## 可延展方向
- Grafana Dashboard as Code（JSON Model / Grafonnet）
- Grafana Loki 日志可视化深入
- Grafana 统一告警与 OnCall 集成
