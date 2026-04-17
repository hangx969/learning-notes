---
title: k8s-networking-service-mesh 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/networking
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/helm安装istio]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/k8s部署istio(1.13.1)]]"
  - "[[Docker-Kubernetes/k8s-networking-service-mesh/企业项目接入istio实战]]"
---

## 元信息

- **原始目录**: `Docker-Kubernetes/k8s-networking-service-mesh/`
- **文档数量**: 7 篇
- **领域**: Kubernetes 网络、Ingress 控制器、服务网格（Istio）、DNS 与网络安全
- **摄入日期**: 2026-04-17

## 整体概述

本目录覆盖了 Kubernetes 集群网络层面的核心主题，包括 Ingress 控制器（ingress-nginx）部署与配置、外部 DNS 自动同步（External-DNS）、服务网格 Istio 的多种部署方式与流量管理实践，以及集群网络安全工具（kube-bench、kube-hunter 等）。文档从基础概念到企业级落地实战，完整展示了从南北流量到东西流量的精细化管理方案。

## 各文档摘要

### [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署external-dns|Helm 部署 External-DNS]]

**核心内容**: External-DNS 将 K8s Service 和 Ingress 资源的域名自动同步到外部 DNS 提供商（如 Azure DNS），实现域名记录的自动化管理。

- 不是 DNS 服务器本身，而是对接外部 DNS 提供商的同步工具
- 支持 Azure DNS 集成，通过 SPN、Managed Identity 或 Workload Identity 认证
- 通过 source 字段监控 Ingress/Service，通过 provider 字段指定 DNS 服务商

### [[Docker-Kubernetes/k8s-networking-service-mesh/helm部署ingress-nginx|Helm 部署 Ingress-Nginx]]

**核心内容**: 在 K8s 中部署 ingress-nginx 控制器作为七层代理，支持 hostNetwork 模式和 ClusterFirstWithHostNet DNS 策略。

- hostNetwork 模式：Pod 使用宿主机网络栈，开启 80/443 端口
- ClusterFirstWithHostNet：解决 hostNetwork 模式下无法解析集群内部服务名的问题
- 建议 DaemonSet 或至少 3 副本确保每个节点都能接收请求
- 适用于裸金属（Bare-metal）环境的部署方案

### [[Docker-Kubernetes/k8s-networking-service-mesh/k8s集群网络安全|K8s 集群网络安全]]

**核心内容**: 介绍 Docker 容器逃逸漏洞（CVE-2019-5736）原理和 K8s 集群安全测试工具集（kube-bench、kube-hunter、kubeaudit、Polaris）。

- CVE-2019-5736：Docker 18.09.2 以下 runC 漏洞，攻击者可覆写宿主机 runc 二进制文件提权
- kube-bench：检查集群是否符合 CIS 安全标准
- kube-hunter：自动化查找集群安全漏洞
- kubeaudit/Polaris：评估 Pod 和 Deployment 配置安全性

### [[Docker-Kubernetes/k8s-networking-service-mesh/helm安装istio|Helm 安装 Istio]]

**核心内容**: 通过 Helm 分步安装 Istio（v1.27.1）的三个组件：base chart、istiod 控制面、gateway 网关。

- 安装顺序：istio-base -> istiod -> gateway
- istiod 配置：Prometheus 指标合并、JSON 格式访问日志、资源请求
- Gateway 配置：NodePort 类型暴露，适用于本地集群
- 使用 daocloud 镜像代理解决国内镜像拉取问题

### [[Docker-Kubernetes/k8s-networking-service-mesh/k8s精细化流量管理-istio|Istio 精细化流量管理]]

**核心内容**: 系统性介绍服务网格背景、核心功能以及 Istio 在微服务流量治理中的定位，对比了 Linkerd 等竞品。

- 服务网格解决的问题：服务间通信、流量精细化管理、安全通信、多语言治理、可观测性
- 核心功能：负载均衡、服务发现、熔断降级、动态路由、故障注入、错误重试、安全通信
- 架构演变：单体应用 -> 微服务 -> 服务网格，流量治理功能下沉到基础设施
- 对比 SpringCloud/Nacos：服务网格语言无关，无需侵入业务代码

### [[Docker-Kubernetes/k8s-networking-service-mesh/k8s部署istio(1.13.1)|Istio 1.13.1 部署与架构]]

**核心内容**: 详细介绍 Istio 基础架构（数据平面 Envoy + 控制平面 istiod），包含流量管理（熔断、超时、重试）的深入讲解。

- Istio 1.5+ 将原有多组件（Pilot、Mixer、Citadel）整合为 istiod 单体
- Pilot：服务发现与配置分发；Envoy：Sidecar 代理拦截所有流量
- 熔断机制：快速失败返回、故障隔离、恢复机制、自动重试
- 超时控制：防止请求无限期等待，提高系统稳定性

### [[Docker-Kubernetes/k8s-networking-service-mesh/企业项目接入istio实战|企业项目接入 Istio 实战]]

**核心内容**: 企业项目接入 Istio 的两种场景（Sidecar 东西流量管理 vs IngressGateway 南北流量管理）及完整实战案例。

- 新项目按 Istio 规范创建 Deployment/Service 和核心资源
- 已部署项目需修改 Deployment/Service，按需转换为 IngressGateway
- 测试架构：前端 UI + 后端 Receive/Order/Handler Service + MySQL
- 建议所有 Deployment 配置 version 标签

## 涉及的概念与实体

- [[KnowledgeBase/concepts/ServiceMesh]]: 服务网格架构，流量治理下沉到基础设施
- [[KnowledgeBase/entities/Ingress|Ingress]]: K8s 七层代理入口，南北流量管理
- [[KnowledgeBase/concepts/Sidecar]]: Envoy 代理注入模式
- [[KnowledgeBase/concepts/流量管理]]: 熔断、超时、重试、金丝雀发布、蓝绿部署
- [[KnowledgeBase/entities/Istio]]: 服务网格平台
- [[KnowledgeBase/entities/Envoy]]: 数据面代理
- [[KnowledgeBase/entities/Ingress-Nginx]]: K8s Ingress 控制器
- [[KnowledgeBase/entities/External-DNS]]: DNS 自动同步工具
- [[KnowledgeBase/entities/CoreDNS]]: K8s 集群 DNS 服务
- [[KnowledgeBase/entities/Pilot]]: Istio 控制面服务发现组件

## 交叉主题发现

1. **南北流量 vs 东西流量**: Ingress-Nginx 负责集群外到集群内的南北流量，Istio 侧重于集群内服务间的东西流量管理，两者可以协同工作。
2. **DNS 解析链路**: External-DNS（外部域名同步） -> CoreDNS（集群内解析） -> Ingress-Nginx/Istio Gateway（流量入口），形成完整的 DNS 到流量转发链路。
3. **安全多层防护**: 集群网络安全工具（kube-bench 等）提供基础安全检测，Istio 提供 mTLS 全链路加密，与 `k8s-security-auth` 目录的 Kyverno 策略引擎形成多层安全体系。
4. **hostNetwork 与 DNS 策略**: Ingress-Nginx 的 hostNetwork 模式需要 ClusterFirstWithHostNet DNS 策略，这与 ArgoCD DNS 排查（k8s-CICD 目录）的 CoreDNS 问题密切相关。
5. **微服务架构演进**: 从 SpringCloud/Nacos 到 Istio 的服务治理演进，反映了基础设施层面的关注点分离趋势。
