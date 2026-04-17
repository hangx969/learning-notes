---
title: Grafana
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary|k8s-monitoring-logging 来源批量摘要]]"
---

# Grafana

## 定义
Grafana 是开源的数据可视化与仪表盘平台，常与 Prometheus、Loki 等数据源配合使用，提供丰富的图表、告警与面板功能。本仓库中 Grafana 始终与 Prometheus 成对出现，同时也涉及 GPU Exporter 监控场景。

## 编译知识

### 部署方式
- **K8s Deployment 部署**（v5.0.4，heapster-grafana-amd64 镜像）
- **Helm 部署**：作为 kube-prometheus-stack 的子 Chart 一键安装
- **二进制部署**：与 [[KnowledgeBase/entities/Prometheus|Prometheus]]、Node Exporter 配合的独立监控栈
- **Docker 部署**：与 Prometheus + cAdvisor 组合的容器监控方案

### 在可观测性体系中的定位
- Grafana 是可观测性三大支柱的**统一可视化层**：
  - **监控（Metrics）**: Prometheus 数据源
  - **日志（Logging）**: Loki 数据源
  - **链路追踪（Tracing）**: Tempo 数据源
- Grafana Agent 可作为轻量级采集代理，替代独立部署多个采集组件

### 告警能力
- Grafana 自带告警功能，但生产环境推荐使用 Alertmanager（更灵活的分组、路由和去重机制）

### Loki + Promtail + Tempo 全家桶
- 通过 [[KnowledgeBase/entities/Helm|Helm]] 部署的轻量级可观测性方案
- Loki 轻量化且高效，适合聚合存储 K8s Events
- K8s Events 默认只保留一小时，通过 k8s-event-logger + Promtail 持久化到 Loki

## 在本仓库中的位置
主要出现在 `Docker-Kubernetes/k8s-monitoring-logging/` 目录，以及 Docker 部署场景中。

## 相关文章
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4)|k8s部署grafana(v5.0.4)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)|k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter|二进制部署prometheus-grafana-nodeexporter]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶|helm部署Loki-promtail-tempo-grafanaAgent全家桶]]
- [[Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控|docker部署prometheus-grafana-cAdvisior监控]]

## 关联概念
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Docker|Docker]]

## 可延展方向
- Grafana Dashboard as Code（JSON Model / Grafonnet）
- Grafana Loki 日志可视化深入
- Grafana 统一告警与 OnCall 集成
