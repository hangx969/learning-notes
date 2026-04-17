---
title: Prometheus
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[KnowledgeBase/sources/k8s-monitoring-logging-batch-summary|k8s-monitoring-logging 来源批量摘要]]"
---

# Prometheus

## 定义
Prometheus 是开源的系统监控与告警工具，采用拉取（pull）模式采集指标，支持 PromQL 查询语言、Alertmanager 告警管理、联邦集群等特性。本仓库记录了 10+ 篇相关文章，覆盖从二进制部署到 Helm 全家桶。

## 编译知识

### 核心架构
- **CNCF 第二个托管项目**，本身也是时序数据库（TSDB）
- 多维度数据模型：metric name + labels 组成时间序列
- **拉取（Pull）模式**为主，支持 Pushgateway 推送短生命周期 job 数据
- 高效存储：每个采样数据约 3.5 bytes，300 万时间序列 30s 间隔保留 60 天约消耗 200G

### 高可用部署模式
- 三种模式：基本 HA、HA + 远程存储、HA + 远程存储 + 联邦集群
- **联邦集群**：每个 Prometheus 提供 `/federate` 接口，上层 Prometheus 从中拉取数据，实现多数据中心监控汇聚

### K8s 监控体系
- 五个监控层面：节点状态、节点资源、容器监控、应用监控、K8s 组件监控
- **node-exporter** 以 DaemonSet 部署，使用 hostNetwork/hostPID/hostIPC 获取宿主机信息
- 监控 etcd 需要证书认证访问 `/metrics` 接口
- 远程监控外部集群通过 ServiceAccount Token 实现

### 部署形态演进
- 手动 YAML 部署单个组件 -> 二进制部署联邦集群 -> **Helm 一键部署 kube-prometheus-stack 全家桶**
- kube-prometheus-stack 是 Prometheus Operator 的 [[KnowledgeBase/entities/Helm|Helm]] Chart 封装，包含 Prometheus、Alertmanager、[[KnowledgeBase/entities/Grafana|Grafana]]、kube-state-metrics、node-exporter
- **Operator 模式**：通过 ServiceMonitor / ScrapeConfig CRD 声明式管理监控目标

### Alertmanager
- 工作流程：PENDING -> FIRING -> 分组等待 -> 发送通知
- 关键参数：group_wait、group_interval、repeat_interval
- 支持邮件（SMTP）告警通知

### 监控非云原生应用
- 通过 Exporter 监控未提供 Metrics 接口的服务（MySQL、Redis 等）
- 一个 Exporter 建议只监控一个实例，避免单点故障

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/k8s-monitoring-logging/` 目录，也有 Docker 场景的部署文章在 `Docker-Kubernetes/docker/` 中。

## 相关文章
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础|Prometheus基础]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件|Prometheus监控k8s系统组件]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群|Prometheus监控外部k8s集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机|Prometheus监控非云原生应用-主机]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.2.1)|k8s监控Prometheus(v2.2.1)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)|k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控alertmanager(v0.14.0)|k8s监控alertmanager(v0.14.0)]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群|二进制部署Prometheus(v2.32.1)联邦集群]]
- [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter|二进制部署prometheus-grafana-nodeexporter]]
- [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|helm部署prometheus-stack全家桶]]
- [[Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控|docker部署prometheus-grafana-cAdvisior监控]]

## 关联概念
- [[KnowledgeBase/entities/Grafana|Grafana]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/entities/Docker|Docker]]

## 可延展方向
- Prometheus 长期存储方案（Thanos / Mimir）
- Prometheus Operator 与 ServiceMonitor 深入
- PromQL 高级查询与告警规则设计
