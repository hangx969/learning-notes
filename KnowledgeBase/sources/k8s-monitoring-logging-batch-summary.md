---
title: k8s-monitoring-logging 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/monitoring-logging
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.2.1)]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s监控alertmanager(v0.14.0)]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4)]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s部署elasticsearch集群]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/k8s部署全链路追踪-Skywalking]]"
  - "[[Docker-Kubernetes/k8s-monitoring-logging/helm部署jaeger]]"
---

# k8s-monitoring-logging 来源批量摘要

## 元信息
- **原始目录**：`Docker-Kubernetes/k8s-monitoring-logging/`
- **文档数量**：20 篇
- **领域**：Docker-Kubernetes
- **摄入日期**：2026-04-17

## 整体概述
本批次文档系统性地覆盖了 Kubernetes 集群可观测性的三大支柱：监控（Metrics）、日志（Logging）和链路追踪（Tracing）。监控方面以 Prometheus 为核心，包含基础概念、多版本部署（容器化和二进制）、联邦集群、Operator/Helm 部署、Alertmanager 告警配置以及对 K8s 控制面组件和外部服务的监控方案。日志方面覆盖了 EFK/ELK 技术栈的多种部署形态（K8s 容器化、二进制、ECK Operator），以及轻量级 Loki 方案。链路追踪方面包含 Skywalking 和 Jaeger 两大工具的 Helm 部署实践。

## 各文档摘要

### [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus基础|Prometheus基础]]
- 核心内容：Prometheus 的基础概念、架构特点、数据模型、PromQL 查询语言和服务发现机制的系统性介绍。
- 关键知识点：
  - Prometheus 是 CNCF 第二个托管项目，本身也是时序数据库（TSDB）
  - 多维度数据模型：metric name + labels 组成时间序列
  - 拉取（Pull）模式为主，支持 Pushgateway 推送短生命周期 job 数据
  - 高效存储：每个采样数据约 3.5 bytes，300 万时间序列 30s 间隔保留 60 天约消耗 200G

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.2.1)|K8s部署Prometheus v2.2.1]]
- 核心内容：在 K8s 中部署 Prometheus v2.2.1，包含 node-exporter、Prometheus Server 和高可用方案介绍。
- 关键知识点：
  - Prometheus 三种高可用部署模式：基本 HA、HA+远程存储、HA+远程存储+联邦集群
  - K8s 监控体系五个层面：节点状态、节点资源、容器监控、应用监控、K8s 组件监控
  - node-exporter 以 DaemonSet 方式部署，使用 hostNetwork 共享宿主机网络

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控Prometheus(v2.33.5)+Grafana(v8.4.5)|K8s部署Prometheus v2.33.5+Grafana v8.4.5]]
- 核心内容：在 K8s 中部署较新版本的 Prometheus v2.33.5 和 Grafana v8.4.5，包含详细的 DaemonSet 配置。
- 关键知识点：
  - node-exporter 使用 hostPID、hostIPC、hostNetwork 获取宿主机完整信息
  - 容器开启 privileged 特权模式以访问 /proc、/sys 等系统目录
  - 配置容忍 control-plane 污点以在控制节点上也部署 node-exporter

### [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署prometheus-grafana-nodeexporter|二进制部署Prometheus-Grafana-NodeExporter]]
- 核心内容：在非 K8s 环境中以二进制方式部署 Prometheus、Grafana 和 Node Exporter 监控栈。
- 关键知识点：
  - Prometheus 推荐使用 LTS 稳定版本
  - 使用 systemd 管理 Prometheus 和 Node Exporter 服务
  - 配置文件中按 job_name 分组定义监控目标，支持 labels 标注

### [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署Prometheus(v2.32.1)联邦集群|二进制部署Prometheus联邦集群]]
- 核心内容：以二进制方式搭建 Prometheus v2.32.1 联邦集群，实现多数据中心监控数据汇聚。
- 关键知识点：
  - 联邦集群核心：每个 Prometheus 提供 /federate 接口，上层 Prometheus 从中拉取数据
  - 架构：主节点 + 多个联邦子节点，每个子节点监控各自数据中心
  - 各节点分别部署 node-exporter 采集主机指标

### [[Docker-Kubernetes/k8s-monitoring-logging/helm部署prometheus-stack全家桶|Helm部署Prometheus-Stack全家桶]]
- 核心内容：使用 Helm 部署 kube-prometheus-stack，一键安装 Prometheus、Alertmanager、Grafana、kube-state-metrics、node-exporter 等全套组件。
- 关键知识点：
  - kube-prometheus-stack 是 Prometheus Operator 的 Helm Chart 封装
  - 子 Chart 依赖：kube-state-metrics（容器指标）、node-exporter（宿主机指标）、grafana
  - 前提条件：需要 StorageClass 持久化存储和 Ingress Controller
  - 需将镜像源替换为国内镜像（如阿里云）

### [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控k8s系统组件|Prometheus监控K8s系统组件]]
- 核心内容：使用 Prometheus 监控 K8s 控制面组件（etcd、kube-proxy、kube-scheduler、kube-controller-manager），包含 ServiceMonitor 配置。
- 关键知识点：
  - 监控 etcd 需要使用证书认证访问 /metrics 接口
  - 需手动为 etcd 创建 Service 和 Endpoints
  - 将 etcd 证书创建为 Secret 并挂载到 Prometheus Pod

### [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控外部k8s集群|Prometheus监控外部K8s集群]]
- 核心内容：在独立机器上部署 Prometheus，通过 ServiceAccount Token 远程监控外部 K8s 集群。
- 关键知识点：
  - 创建 SA 并绑定 cluster-admin ClusterRole 获取集群访问权限
  - 手动创建 kubernetes.io/service-account-token 类型的 Secret 获取 Token
  - 部署 kube-state-metrics 采集容器级别指标

### [[Docker-Kubernetes/k8s-monitoring-logging/Prometheus监控非云原生应用-主机|Prometheus监控非云原生应用和主机]]
- 核心内容：使用 Exporter 监控未提供 Metrics 接口的服务（如 MySQL、Redis），以及通过 ServiceMonitor 和 ScrapeConfig 接入 Prometheus。
- 关键知识点：
  - 一个 Exporter 建议只监控一个实例，避免单点故障影响多个服务
  - MySQL Exporter 配置：创建专用用户并授予 PROCESS、REPLICATION CLIENT 权限
  - 通过 ServiceMonitor 或 ScrapeConfig CRD 将 Exporter 接入 Prometheus Operator

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控alertmanager(v0.14.0)|K8s部署Alertmanager v0.14.0]]
- 核心内容：在 K8s 中部署 Alertmanager v0.14.0，配置邮件告警通知，以及告警规则和工作流程。
- 关键知识点：
  - Alertmanager 工作流程：PENDING -> FIRING -> 分组等待 -> 发送通知
  - 关键参数：group_wait（组等待时间）、group_interval（组间隔）、repeat_interval（重复发送间隔）
  - 配置 SMTP 邮件告警：smtp_smarthost、smtp_auth_password（授权码）
  - 使用 ConfigMap 挂载 alertmanager.yml 和 prometheus rules

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署grafana(v5.0.4)|K8s部署Grafana v5.0.4]]
- 核心内容：在 K8s 中以 Deployment 方式部署 Grafana v5.0.4 可视化监控面板。
- 关键知识点：
  - 使用 heapster-grafana-amd64 镜像
  - 配置匿名访问和 Admin 角色以简化实验环境
  - Grafana 自带告警功能但生产环境推荐使用 Alertmanager

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s日志管理|K8s日志管理]]
- 核心内容：K8s 容器日志的保存机制、生命周期管理和持久化方案，涵盖 kubelet 日志管控策略。
- 关键知识点：
  - kubelet 默认日志限制：containerLogMaxSize 10Mi，containerLogMaxFiles 5，每容器最多约 50MiB
  - Docker 和 containerd 运行时的日志存储路径差异
  - 容器删除时日志同步删除，轮转仅基于文件大小而非时间
  - 生产环境必须部署集中式日志系统（ELK/EFK/Loki 等）

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控ES(7.2)+Kibana(7.2)+Fluentd(v1.4.2)|K8s部署EFK日志收集]]
- 核心内容：在 K8s 中部署 EFK（Elasticsearch 7.2 + Kibana 7.2 + Fluentd v1.4.2）日志收集方案，包含日志基础知识。
- 关键知识点：
  - 日志四个级别：DEBUG、INFO、WARNING、ERROR，生产环境通常开启 INFO 级别
  - EFK vs ELK 区别：F（Fluentd/Filebeat）轻量级 vs L（Logstash）重量级
  - 多种日志方案对比：ELK、EFK、ELK+Filebeat 等

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s监控EFK+logstash+kafka|K8s部署EFK+Logstash+Kafka]]
- 核心内容：在 K8s 中部署 Fluentd + Kafka + Logstash + ES 高吞吐量日志收集架构，适用于 TB 级日志场景。
- 关键知识点：
  - 架构流程：Fluentd 采集 -> Kafka 缓冲 -> Logstash 格式转换 -> ES -> Kibana
  - Fluentd 通过 DaemonSet 部署，使用节点标签选择器控制日志收集范围
  - Kafka 作为缓冲层防止大量日志导致延迟

### [[Docker-Kubernetes/k8s-monitoring-logging/二进制部署efk+logstash+kafka日志收集平台|二进制部署EFK+Logstash+Kafka日志平台]]
- 核心内容：以二进制方式搭建 Filebeat + Kafka + Logstash + ES + Kibana 完整日志收集平台，含 Zookeeper 集群部署。
- 关键知识点：
  - Zookeeper 集群部署：奇数台（3/5/7 台），支持过半机制选举
  - Zookeeper 角色：leader（发起选举）、follower（参与投票）、observer（不参与选主）
  - Filebeat 比 Logstash 更轻量但格式转换不便，两者配合使用效果最佳

### [[Docker-Kubernetes/k8s-monitoring-logging/基于helm+operator部署ECK日志收集平台|Helm+Operator部署ECK日志收集平台]]
- 核心内容：使用 Helm 和 Elastic Cloud on Kubernetes（ECK）Operator 部署企业级日志收集平台，包含全面的日志技术栈对比。
- 关键知识点：
  - 需要收集的三类日志：操作系统日志、K8s 组件日志、业务应用程序日志
  - 日志收集器对比：Logstash（重量级）、Fluentd（K8s 原生）、Fluent-bit（超轻量）、Filebeat（推荐）
  - Loki 轻量架构适合小规模，EFK 传统架构适合大规模日志场景
  - Filebeat 是 K8s 上收集日志的最推荐组件

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署elasticsearch集群|K8s部署Elasticsearch集群]]
- 核心内容：在 K8s 中以 StatefulSet 方式部署 Elasticsearch 集群，使用 NFS StorageClass 持久化存储。
- 关键知识点：
  - ES 适合 StatefulSet 类型部署，数据库类应用需要稳定的存储和网络标识
  - 通过 ConfigMap 挂载 elasticsearch.yml 配置集群发现、节点角色等
  - 使用环境变量 MY_POD_NAME 动态设置 node.name

### [[Docker-Kubernetes/k8s-monitoring-logging/helm部署Loki-promtail-tempo-grafanaAgent全家桶|Helm部署Loki+Promtail+Tempo+GrafanaAgent全家桶]]
- 核心内容：使用 Helm 部署 Loki + Promtail + Tempo + Grafana Agent 轻量级可观测性全家桶，以及 K8s Events 持久化方案。
- 关键知识点：
  - K8s Events 默认只保留一小时，需要持久化存储以支持长期分析
  - Loki 轻量化且高效，适合聚合存储 K8s Events
  - k8s-event-logger 监听 K8s API 将事件以 JSON 日志写入，通过 Promtail 进入 Loki
  - Events 类型：Failed、Evicted、Failed scheduling、Volume、Node、OOM 等

### [[Docker-Kubernetes/k8s-monitoring-logging/k8s部署全链路追踪-Skywalking|K8s部署Skywalking全链路追踪]]
- 核心内容：在 K8s 中部署 Apache SkyWalking APM 平台，涵盖链路追踪核心概念和主流工具对比。
- 关键知识点：
  - 核心概念：Trace（完整请求流程）、Span（一次操作）、Trace ID 和 Span ID
  - SkyWalking 特性：低侵入性（字节码注入）、多语言支持、自动生成服务拓扑图
  - 链路追踪工具对比：SkyWalking vs Pinpoint vs CAT vs Zipkin vs Jaeger
  - SkyWalking 是 Apache 顶级项目，国人开发，社区活跃度高

### [[Docker-Kubernetes/k8s-monitoring-logging/helm部署jaeger|Helm部署Jaeger]]
- 核心内容：使用 Helm 部署 Jaeger 分布式追踪系统（all-in-one 模式），使用 Badger 本地存储。
- 关键知识点：
  - Jaeger 是 CNCF 项目，由 Uber 开发并开源
  - all-in-one 模式适合测试和小规模部署
  - 使用 Badger 本地存储替代 Cassandra/ES，配置 TTL 72 小时
  - 支持 OTLP gRPC 和 HTTP 协议接收追踪数据

## 涉及的概念与实体
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[KnowledgeBase/entities/Grafana|Grafana]]
- [[KnowledgeBase/entities/Alertmanager|Alertmanager]]
- [[KnowledgeBase/entities/Elasticsearch|Elasticsearch]]
- [[KnowledgeBase/entities/Kibana|Kibana]]
- [[KnowledgeBase/entities/Fluentd|Fluentd]]
- [[KnowledgeBase/entities/Filebeat|Filebeat]]
- [[KnowledgeBase/entities/Logstash|Logstash]]
- [[KnowledgeBase/entities/Kafka|Kafka]]
- [[KnowledgeBase/entities/Loki|Loki]]
- [[KnowledgeBase/entities/Promtail|Promtail]]
- [[KnowledgeBase/entities/Tempo|Tempo]]
- [[KnowledgeBase/entities/SkyWalking|SkyWalking]]
- [[KnowledgeBase/entities/Jaeger|Jaeger]]
- [[KnowledgeBase/entities/Zookeeper|Zookeeper]]
- [[KnowledgeBase/entities/kube-state-metrics|kube-state-metrics]]
- [[KnowledgeBase/entities/node-exporter|node-exporter]]
- [[KnowledgeBase/concepts/可观测性|可观测性]]
- [[KnowledgeBase/concepts/链路追踪|链路追踪]]
- [[KnowledgeBase/concepts/联邦集群|联邦集群]]
- [[KnowledgeBase/concepts/ServiceMonitor|ServiceMonitor]]
- [[KnowledgeBase/concepts/日志收集架构|日志收集架构]]
- [[KnowledgeBase/concepts/PromQL|PromQL]]
- [[KnowledgeBase/concepts/时序数据库|时序数据库 (TSDB)]]

## 交叉主题发现
- **Prometheus 部署形态演进**：从手动创建 YAML 部署单个组件，到二进制部署联邦集群，再到 Helm 一键部署 kube-prometheus-stack 全家桶，部署方式随云原生生态成熟而不断简化。
- **日志收集器轻量化趋势**：从重量级 Logstash 到 Fluentd，再到 Filebeat 和 Fluent-bit，日志收集器呈现明显的轻量化趋势；Logstash 逐渐定位为日志格式转换器而非采集器。
- **EFK 与 Loki 双轨并行**：EFK/ELK 适合大规模（TB 级）日志场景，Loki 适合轻量级场景，两者互补而非替代关系。
- **Kafka 作为日志缓冲层**：多篇文档反复出现 Kafka 作为日志管道缓冲层的架构模式，解决高吞吐场景下的日志延迟问题。
- **可观测性三大支柱覆盖**：监控（Prometheus+Grafana）、日志（EFK/Loki）、链路追踪（SkyWalking/Jaeger）构成完整的可观测性体系，多篇文档之间存在紧密的架构关联。
- **Operator 模式普及**：从手动部署 YAML 到使用 Prometheus Operator（ServiceMonitor CRD）和 ECK Operator，声明式运维模式在监控日志领域全面普及。
