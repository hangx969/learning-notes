---
title: Loki
tags:
  - knowledgebase/entity
  - observability
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/docker/docker部署loki]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理-采集方案与审计日志]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/OpenTelemetry实战-统一Traces-Metrics-Logs]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台]]"
aliases:
  - Grafana Loki
---

## 简介

Grafana Loki 是轻量级日志聚合系统，与 Prometheus 设计理念一致，只索引标签而不索引日志内容，从而大幅降低存储和运维成本。

## 核心功能

- **标签索引**：不对日志内容做全文索引，而是用与 Prometheus 相同的标签（键值对）索引和分组日志流
- **LogQL 查询**：先按标签选择日志流，再按内容过滤（如筛选含 error 的日志）
- **多种接入方式**：Promtail 作为代理采集日志并推送到 Loki 的 push 接口；也可由 OTel Collector 导出，或由应用通过 SDK 直推
- **Grafana 集成**：Grafana 内置 Loki 数据源，在 Explore 中查询日志，并可与 Tempo 数据源关联实现 Trace 到日志的跳转
- **存储方式**：单机模式可直接使用文件存储，多副本模式依赖对象存储持久化数据

## 使用场景

- 中小规模集群的轻量日志方案（Fluent Bit 或 Promtail + Loki + Grafana），替代较重的 ELK/EFK
- 持久化存储 Kubernetes Events，弥补其默认保留时间短的问题，便于长期分析和排障
- 与 Prometheus、Tempo 等组成 Grafana 统一可观测平台（LGTM）
- 采集宿主机 `/var/log` 等文件日志

## 相关概念与实体

- [[KnowledgeBase/entities/Grafana|Grafana]]：Loki 的查询与可视化入口，Grafana 内置 Loki 数据源
- [[KnowledgeBase/entities/Prometheus|Prometheus]]：Loki 沿用 Prometheus 的标签模型；Prometheus 告警规则监控 Loki 的存储空间
- [[KnowledgeBase/concepts/日志系统|日志系统]]：相比 ELK/EFK 更轻量的日志聚合方案
- [[KnowledgeBase/entities/Helm|Helm]]：用 Helm 部署 Loki（singleBinary）与 Promtail
- [[KnowledgeBase/entities/Docker-Compose|Docker Compose]]：用 Compose 部署 Loki、Promtail 与 Grafana
- [[KnowledgeBase/concepts/Observability|Observability]]：在 OpenTelemetry + LGTM 架构中负责日志存储

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-monitoring-logging/` 目录中涉及 Loki 的部署与配置
- `Docker-Kubernetes/docker/` 目录中包含 Loki 容器化部署相关笔记
- [[Docker-Kubernetes/docker/docker部署loki|docker部署loki]]：Loki 特性、优缺点与 Loki/Promtail/Grafana 架构，Compose 部署与 Promtail 采集配置（文末标注该流程尚未跑通）
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶|helm部署Loki-promtail-tempo-grafanaAgent全家桶]]：Helm 部署 Loki（singleBinary + 持久化）与 Promtail，用 k8s-event-logger 或 Event Exporter 把 Kubernetes Events 写入 Loki
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理-采集方案与审计日志|k8s日志管理-采集方案与审计日志]]：应用直推 Loki、高基数标签导致查询超时的避坑，以及 PLG 选型建议
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|helm部署prometheus-stack全家桶]]：在 Grafana 中添加 Loki 数据源并与 Tempo 关联，以及 Loki 存储空间告警规则
- [[Docker-Kubernetes/k8s-monitoring-logging/OpenTelemetry实战-统一Traces-Metrics-Logs|OpenTelemetry实战-统一Traces-Metrics-Logs]]：OTel Collector 将日志导出到 Loki，以及 LGTM 技术栈与传统方案的对比
- [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台|基于helm+operator部署ECK日志收集平台]]：Loki 轻量架构与 ELK/EFK 传统架构的对比

## 知识空白

- 仓库中尚无 Loki 分布式或可扩展部署模式（组件拆分部署）的实践，现有 Helm 部署仅为 singleBinary
- 仓库中尚无 Loki 对接对象存储以及日志保留（retention）策略的具体配置
- 仓库中尚无 LogQL 聚合类查询和基于 Loki 的日志告警规则
