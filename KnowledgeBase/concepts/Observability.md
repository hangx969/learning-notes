---
title: Observability
tags:
  - knowledgebase/concept
date: 2026-04-16
---

# Observability

## 定义
可观测性（Observability）是通过日志（Logs）、指标（Metrics）和链路追踪（Traces）三大支柱来理解系统内部状态的能力。本仓库覆盖 Prometheus、Grafana、Loki、Jaeger、Skywalking、EFK 等主流可观测性工具栈的部署与实践。

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-monitoring-logging/` 目录下，共 20 篇文章，涵盖指标监控、日志收集、全链路追踪三大方向。

## 相关文章
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.2.1)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控alertmanager(v0.14.0)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署jaeger]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署全链路追踪-Skywalking]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署elasticsearch集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台]]
- [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台]]

## 关联概念
- [[KnowledgeBase/concepts/日志系统]]
- [[KnowledgeBase/concepts/AKS]]
- [[KnowledgeBase/concepts/服务网格]]
- [[KnowledgeBase/concepts/CICD]]

## 可延展方向
- OpenTelemetry 统一采集标准
- Grafana LGTM 全家桶（Loki + Grafana + Tempo + Mimir）
- SLO/SLI 定义与告警策略设计
- eBPF 无侵入式可观测性
- 云平台原生监控集成（Azure Monitor、阿里云 SLS）
