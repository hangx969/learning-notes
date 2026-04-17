---
title: K8s杂项专题 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/helm-operator
  - docker-kubernetes/CKA-CKS
  - docker-kubernetes/kubeblocks
  - docker-kubernetes/harbor
  - docker-kubernetes/container-platform
  - docker-kubernetes/k8s-springcloud
  - docker-kubernetes/k8s-backup-dr
  - docker-kubernetes/k8s-ai-gpu
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/helm-operator/helmv3-安装与使用]]"
  - "[[Docker-Kubernetes/helm-operator/helm部署config-syncer(kubed)]]"
  - "[[Docker-Kubernetes/helm-operator/helm部署dragonfly]]"
  - "[[Docker-Kubernetes/helm-operator/helm部署pact-broker]]"
  - "[[Docker-Kubernetes/helm-operator/helm部署reloader]]"
  - "[[Docker-Kubernetes/helm-operator/helm部署tomcat]]"
  - "[[Docker-Kubernetes/CKA-CKS/CKA-备考]]"
  - "[[Docker-Kubernetes/CKA-CKS/CKS-备考]]"
  - "[[Docker-Kubernetes/CKA-CKS/k8s-面试题汇总]]"
  - "[[Docker-Kubernetes/kubeblocks/kubeblocks部署WordPress]]"
  - "[[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群]]"
  - "[[Docker-Kubernetes/harbor/harbor-basics]]"
  - "[[Docker-Kubernetes/harbor/helm部署harbor]]"
  - "[[Docker-Kubernetes/container-platform/部署openshift(3.10)]]"
  - "[[Docker-Kubernetes/container-platform/部署轻量级的K8S平台-K3S]]"
  - "[[Docker-Kubernetes/k8s-springcloud/SpringCloud项目迁移到k8s实战]]"
  - "[[Docker-Kubernetes/k8s-backup-dr/k8s集群备份恢复-Velero]]"
  - "[[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU]]"
---

## 元信息

- **原始目录**: `Docker-Kubernetes/helm-operator/`、`Docker-Kubernetes/CKA-CKS/`、`Docker-Kubernetes/kubeblocks/`、`Docker-Kubernetes/harbor/`、`Docker-Kubernetes/container-platform/`、`Docker-Kubernetes/k8s-springcloud/`、`Docker-Kubernetes/k8s-backup-dr/`、`Docker-Kubernetes/k8s-ai-gpu/`
- **文档数量**: 18 篇（8 个子目录汇总）
- **领域**: Helm 工具链、K8s 认证备考、KubeBlocks 数据库管理、Harbor 镜像仓库、容器平台（OpenShift/K3S）、SpringCloud 迁移、备份恢复、GPU 配置
- **摄入日期**: 2026-04-17

## 整体概述

本批次文档覆盖 Kubernetes 生态的多个专题领域。Helm 工具链部分包含 Helm 本身的安装使用以及通过 Helm 部署各类运维工具（Config Syncer、Dragonfly、Pact Broker、Reloader、Tomcat）。认证备考部分涵盖 CKA/CKS 考试准备和常见面试题。KubeBlocks 展示了用统一 Operator 快速部署 WordPress 和高可用 Harbor 的方案。此外还包含 Harbor 镜像仓库基础与 Helm 部署、OpenShift 和 K3S 容器平台、SpringCloud 微服务迁移到 K8s、Velero 集群备份恢复以及 NVIDIA GPU 在 K8s 中的配置实践。

## 各文档摘要

### [[Docker-Kubernetes/helm-operator/helmv3-安装与使用|Helm v3安装与使用]]

- **核心内容**: Helm v3 的概念介绍、Linux 和 Windows（Scoop）两种安装方式以及基本使用。
- **关键知识点**:
  - Helm 是 K8s 包管理工具，核心概念为 Chart（程序包）
  - v3 版本移除了 Tiller 服务端组件
  - 支持资源管理、版本控制、依赖管理和 Go 模板化
  - Windows 下可通过 Scoop 包管理器安装 Helm、kubectl、krew

### [[Docker-Kubernetes/helm-operator/helm部署config-syncer(kubed)|Helm部署Config Syncer]]

- **核心内容**: 部署 Config Syncer（原 Kubed）实现跨 Namespace 同步 ConfigMap 和 Secret，包含因 Docker Hub 镜像移除后自行构建镜像的完整流程。
- **关键知识点**:
  - Config Syncer 用于将 ConfigMap/Secret 自动同步到其他 Namespace
  - Appscode 在 2024 年 2 月移除了 Docker Hub 镜像，需自行通过 Dockerfile 构建
  - 替代方案：kubernetes-replicator
  - 构建涉及 Go 编译环境和 Makefile 修改

### [[Docker-Kubernetes/helm-operator/helm部署dragonfly|Helm部署Dragonfly]]

- **核心内容**: Dragonfly P2P 镜像分发系统的原理和部署，解决大规模集群镜像拉取的带宽和速度问题。
- **关键知识点**:
  - CNCF 开源项目，基于 P2P 技术的容器镜像分发系统（阿里云捐赠）
  - 核心架构：Scheduler（调度器）+ Seed Client（种子节点）+ Peer（节点客户端）
  - 典型场景：100 节点拉取 2GB 镜像可节约 99% 带宽
  - 采用 BitTorrent-like 分块分发机制

### [[Docker-Kubernetes/helm-operator/helm部署pact-broker|Helm部署Pact Broker]]

- **核心内容**: 部署 Pact Broker 用于微服务契约测试管理，配置 Ingress 和 OAuth2 Proxy 认证。
- **关键知识点**:
  - 契约测试是确保微服务间通信正确性的消费者驱动测试方法
  - Pact 工具支持多语言，由消费者定义契约，提供者验证
  - Pact Broker 集中管理契约版本
  - 集成 nginx ingress 和 oauth2-proxy 进行访问控制

### [[Docker-Kubernetes/helm-operator/helm部署reloader|Helm部署Reloader]]

- **核心内容**: 部署 Stakater Reloader 工具，监控 ConfigMap/Secret 变更并自动触发工作负载滚动更新。
- **关键知识点**:
  - 解决 ConfigMap/Secret 通过 env 引用时无法热更新的问题
  - 通过 annotation `reloader.stakater.com/auto: "true"` 启用自动重启
  - 支持全局监控或指定 Namespace 监控
  - 可精确指定需要监控的 ConfigMap/Secret 名称

### [[Docker-Kubernetes/helm-operator/helm部署tomcat|Helm部署Tomcat]]

- **核心内容**: 使用 Bitnami Helm Chart 部署 Tomcat 并通过 NodePort 暴露服务。
- **关键知识点**:
  - 使用 `bitnami/tomcat` Chart，配置 Deployment 类型和 NodePort
  - 需要 bitnami/common 子 Chart
  - 持久化存储使用 NFS StorageClass

### [[Docker-Kubernetes/CKA-CKS/CKA-备考|CKA备考]]

- **核心内容**: CKA 认证考试的模拟环境搭建，包含 Ubuntu 系统初始化、Docker/containerd 安装和 K8s 集群搭建。
- **关键知识点**:
  - 基于 Ubuntu 的 K8s 集群搭建流程
  - APT 包管理器锁定问题的解决方法
  - Docker GPG 密钥和仓库配置

### [[Docker-Kubernetes/CKA-CKS/CKS-备考|CKS备考]]

- **核心内容**: CKS 认证考试知识点和模拟题，涵盖 AppArmor、kube-bench 等安全主题。
- **关键知识点**:
  - AppArmor：Linux 强制访问控制（MAC），通过配置文件限制程序的文件/网络访问
  - 两种工作模式：Enforcement（强制执行）和 Complain（仅记录）
  - 在 K8s Pod 中通过 annotation 应用 AppArmor 配置
  - `apparmor_parser` 加载配置，`apparmor_status` 检查生效状态

### [[Docker-Kubernetes/CKA-CKS/k8s-面试题汇总|K8s面试题汇总]]

- **核心内容**: K8s 面试常见问题汇总，涵盖 Pod 调度、配置更新、网络、容器运行时等主题。
- **关键知识点**:
  - Pod 调度：NodeResourceFit 插件的三种评分策略（LeastAllocated、MostAllocated、RequestedToCapacityRatio）
  - OOM 时容器重启 vs Pod 驱逐的区别
  - ConfigMap 挂载（非 subPath）支持动态更新，环境变量不支持
  - ClusterIP Service 的 connection tracking 可能导致长连接负载不均
  - K8s 不再支持 Docker 的原因：CRI 解耦，Containerd 从 Docker 剥离

### [[Docker-Kubernetes/kubeblocks/kubeblocks部署WordPress|KubeBlocks部署WordPress]]

- **核心内容**: 使用 KubeBlocks Operator 一键部署 MySQL 高可用集群作为 WordPress 后端数据库。
- **关键知识点**:
  - KubeBlocks 支持管理 30+ 种数据库和有状态中间件
  - 使用 apecloud-mysql addon 创建 RaftGroup 模式三副本 MySQL 集群
  - kbcli 命令行工具快速部署和管理集群
  - 解决 StorageClass 默认配置和 PVC 绑定问题

### [[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群|KubeBlocks部署高可用Harbor集群]]

- **核心内容**: 使用 KubeBlocks 快速创建高可用 PostgreSQL 和 Redis 集群，作为 Harbor 的后端存储。
- **关键知识点**:
  - Harbor 原生不集成高可用，需要外部 HA 的 Redis 和 PostgreSQL
  - KubeBlocks 通过 replication 模式创建主备集群，支持自动故障转移
  - PostgreSQL 和 Redis 集群创建只需一条命令

### [[Docker-Kubernetes/harbor/harbor-basics|Harbor基础]]

- **核心内容**: Harbor 企业级 Docker 镜像仓库的基础介绍、自签发证书配置和安装流程。
- **关键知识点**:
  - Harbor 由 VMware 开源，支持 RBAC、LDAP、日志审核、镜像复制
  - 基于 docker-compose 部署
  - 自签发证书流程：CA 根证书 -> 域名证书签发
  - 默认账号密码：admin/Harbor12345

### [[Docker-Kubernetes/harbor/helm部署harbor|Helm部署Harbor]]

- **核心内容**: 使用 Helm Chart 在 K8s 上部署 Harbor，配置 Ingress 和 TLS 证书。
- **关键知识点**:
  - Helm 3 支持 OCI 格式的容器注册中心存储 Chart
  - Harbor 支持存储和管理容器镜像和 Helm Chart
  - 使用 cert-manager 创建 TLS 证书
  - 支持 ingress、clusterIP、nodePort、loadBalancer 多种暴露方式

### [[Docker-Kubernetes/container-platform/部署openshift(3.10)|部署OpenShift]]

- **核心内容**: OpenShift 容器应用平台的基础概念、架构组件和与 K8s 的对比。
- **关键知识点**:
  - OpenShift 是 PaaS 平台，底层集成 Docker + K8s
  - 核心概念：Project（带注释的 Namespace）、Users、Pod
  - 内置 S2I（Source to Image）自动化流程工具
  - 提供 OpenvSwitch 原生网络方案
  - 社区版为 OKD，企业版为 OpenShift Container Platform

### [[Docker-Kubernetes/container-platform/部署轻量级的K8S平台-K3S|部署轻量级K8S平台K3S]]

- **核心内容**: K3S 轻量级 K8s 发行版的介绍、架构说明和基于 CentOS 的部署流程。
- **关键知识点**:
  - K3S 由 Rancher 开发，主要用于边缘计算和物联网场景
  - 所有控制面组件打包到单个二进制文件，仅需 512M 内存
  - 默认使用 SQLite 存储（也支持 etcd3、MySQL、PostgreSQL）
  - 内置 Containerd、Flannel、CoreDNS，无需额外安装
  - 支持单 master 和多 master 架构

### [[Docker-Kubernetes/k8s-springcloud/SpringCloud项目迁移到k8s实战|SpringCloud项目迁移到K8s实战]]

- **核心内容**: 将基于 Eureka 注册中心的 SpringCloud 前后端分离项目迁移到 K8s 的完整方案。
- **关键知识点**:
  - 迁移架构：Eureka（StatefulSet）、Receive 网关（Ingress）、Handler（内部服务）、UI（Ingress）
  - 使用 Maven Docker 容器构建 Java 项目
  - Dockerfile 基于 JDK 8 镜像
  - 前端通过域名主路径访问，网关通过 /receiveapi 路径转发

### [[Docker-Kubernetes/k8s-backup-dr/k8s集群备份恢复-Velero|K8s集群备份恢复Velero]]

- **核心内容**: Velero 备份恢复工具的介绍、与 Etcd/GitOps 方案的对比、工作原理和 Minio 对象存储部署。
- **关键知识点**:
  - 三种备份方案对比：Etcd（全量但不可选择性恢复）、GitOps（配置漂移问题）、Velero（灵活但需 S3 存储）
  - Velero 核心资源：Backup、Schedule、Restore、BackupStorageLocation
  - 不推荐用 Velero 备份数据库数据（崩溃一致性），应使用 mysqldump/pg_dump
  - 使用 Minio 作为对象存储后端

### [[Docker-Kubernetes/k8s-ai-gpu/k8s配置NVIDIA GPU|K8s配置NVIDIA GPU]]

- **核心内容**: 在裸金属 K8s 集群上配置 NVIDIA GPU 的实践指南，涵盖驱动安装、运行时配置和故障排除。
- **关键知识点**:
  - GPU 连接路径：Pod -> Kubernetes -> 容器运行时 -> 软件（CUDA） -> 硬件 -> GPU
  - 通过 `runtimeClassName: nvidia`、`resources.limits` 和 `nodeSelector` 声明 GPU 需求
  - GPU 节点通常设置 `NoSchedule` taint 防止非 GPU 工作负载调度
  - GPU 作为"扩展资源"需要 Device Plugin 向 K8s 注册

## 涉及的概念与实体

- [[KnowledgeBase/entities/Helm]] / [[KnowledgeBase/entities/Scoop]]
- [[KnowledgeBase/entities/Config-Syncer]] / [[KnowledgeBase/entities/Dragonfly]] / [[KnowledgeBase/entities/Reloader]] / [[KnowledgeBase/entities/Pact-Broker]]
- [[KnowledgeBase/entities/KubeBlocks]] / [[KnowledgeBase/entities/Harbor]]
- [[KnowledgeBase/entities/OpenShift]] / [[KnowledgeBase/entities/K3S]] / [[KnowledgeBase/entities/Rancher]]
- [[KnowledgeBase/entities/Velero]] / [[KnowledgeBase/entities/Minio]]
- [[KnowledgeBase/entities/NVIDIA]] / [[KnowledgeBase/entities/CUDA]]
- [[KnowledgeBase/entities/SpringCloud]] / [[KnowledgeBase/entities/Eureka]]
- [[KnowledgeBase/concepts/Operator模式]] / [[KnowledgeBase/concepts/CRD]]
- [[KnowledgeBase/concepts/P2P分发]] / [[KnowledgeBase/concepts/契约测试]]
- [[KnowledgeBase/concepts/AppArmor]] / [[KnowledgeBase/concepts/RBAC]]
- [[KnowledgeBase/concepts/边缘计算]] / [[KnowledgeBase/concepts/GPU调度]]
- [[KnowledgeBase/concepts/备份恢复]] / [[KnowledgeBase/concepts/崩溃一致性-vs-应用一致性]]
- [[KnowledgeBase/concepts/高可用架构]] / [[KnowledgeBase/concepts/StorageClass]]
- [[KnowledgeBase/concepts/OCI]] / [[KnowledgeBase/concepts/容器运行时]]

## 交叉主题发现

1. **Helm 作为统一部署手段**: Helm Chart 贯穿几乎所有工具和服务的部署（Harbor、Dragonfly、Reloader、Config Syncer、Tomcat、Kafka），是 K8s 生态的核心包管理基础设施。
2. **KubeBlocks 与独立部署对比**: KubeBlocks 一键部署 HA 数据库的能力（WordPress 场景的 MySQL、Harbor 场景的 PostgreSQL+Redis）与手动通过 Helm/YAML 部署形成对比，体现了更高层次的抽象和自动化。
3. **Harbor 多维度覆盖**: Harbor 在本批次中出现多次 -- 基础安装（docker-compose）、Helm 部署（K8s 上）、KubeBlocks 高可用方案，展示了同一组件在不同场景下的部署演进。
4. **安全主题链路**: CKS 备考中的 AppArmor/kube-bench 与面试题中的容器运行时安全问题相呼应，可串联为 K8s 安全知识体系。
5. **边缘与轻量化**: K3S 的边缘计算定位与 OpenShift 的企业级全栈平台形成两极对比，展示了 K8s 生态从轻量到重量级的完整光谱。
6. **数据保护全链路**: Velero 的备份恢复方案与面试题中关于日志丢失风险、Pod 稳定性的讨论互相补充，构成 K8s 数据保护的完整视角。
