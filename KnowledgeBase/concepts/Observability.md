---
title: Observability
tags:
  - knowledgebase/concept
date: 2026-04-16
sources: []
aliases:
  - 可观测性
  - 监控
---

# Observability

## 定义
可观测性（Observability）是通过日志（Logs）、指标（Metrics）和链路追踪（Traces）三大支柱来理解系统内部状态的能力。本仓库覆盖 Prometheus、Grafana、Loki、Jaeger、Skywalking、EFK 等主流可观测性工具栈的部署与实践。

## 核心要点
- 三大支柱互补：Metrics 告诉你"出了问题"，Logs 告诉你"哪里出了问题"，Traces 告诉你"为什么出了问题"
- Prometheus + Grafana 是 K8s 生态的事实标准监控栈，通过 ServiceMonitor CRD 实现自动服务发现
- 日志方案从 EFK 向 Loki 演进：Loki 不索引日志内容，成本显著降低
- OpenTelemetry 正在统一三大支柱的数据采集标准（OTLP 协议）
- 可观测性不等于监控：监控是已知问题的检测，可观测性是未知问题的探索

## 在本仓库中的覆盖
主要集中在 `Docker-Kubernetes/k8s-monitoring-logging/` 目录下，共 20 篇文章，涵盖指标监控、日志收集、全链路追踪三大方向。


- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础|Prometheus基础]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件|Prometheus监控k8s系统组件]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群|Prometheus监控外部k8s集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机|Prometheus监控非云原生应用-主机]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群|二进制部署Prometheus(v2.32.1)联邦集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter|二进制部署prometheus-grafana-nodeexporter]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.2.1)|k8s监控Prometheus(v2.2.1)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)|k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控alertmanager(v0.14.0)|k8s监控alertmanager(v0.14.0)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4)|k8s部署grafana(v5.0.4)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶|helm部署Loki-promtail-tempo-grafanaAgent全家桶]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署jaeger|helm部署jaeger]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署全链路追踪-Skywalking|k8s部署全链路追踪-Skywalking]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理-采集方案与审计日志|k8s日志管理综合]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka|k8s监控EFK+logstash+kafka]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)|k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署elasticsearch集群|k8s部署elasticsearch集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台|二进制部署efk+logstash+kafka日志收集平台]]
- [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台|基于helm+operator部署ECK日志收集平台]]

## 与其他概念的关系
- [[KnowledgeBase/concepts/日志系统|日志系统]]
- [[KnowledgeBase/entities/AKS|AKS]]
- [[KnowledgeBase/concepts/服务网格|服务网格]]
- [[KnowledgeBase/concepts/CICD|CICD]]

## 知识空白
- OpenTelemetry 统一采集标准
- Grafana LGTM 全家桶（Loki + Grafana + Tempo + Mimir）
- SLO/SLI 定义与告警策略设计
- eBPF 无侵入式可观测性
- 云平台原生监控集成（Azure Monitor、阿里云 SLS）
