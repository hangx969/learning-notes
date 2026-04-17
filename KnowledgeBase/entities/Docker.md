---
title: Docker
tags:
  - knowledgebase/entity
  - docker-kubernetes
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/docker/docker基础]]"
  - "[[Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel]]"
  - "[[Docker-Kubernetes/docker/docker部署gitlab]]"
  - "[[Docker-Kubernetes/docker/docker部署lnmp网站]]"
  - "[[Docker-Kubernetes/docker/docker部署loki]]"
  - "[[Docker-Kubernetes/docker/docker部署nginx-tomcat-httpd-go-python服务]]"
  - "[[Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控]]"
  - "[[Docker-Kubernetes/docker/docker部署仓库平台homebox]]"
  - "[[Docker-Kubernetes/docker/docker部署定时任务工具gocron]]"
  - "[[Docker-Kubernetes/docker/docker部署路由监控工具NextTrace]]"
  - "[[Docker-Kubernetes/docker/docker配置NVIDIA GPU]]"
  - "[[Docker-Kubernetes/docker/docker配置代理]]"
---

# Docker

## 简介

Docker 是一种容器化技术，提供镜像构建、容器运行、网络管理和存储编排能力。本仓库记录了 Docker 从安装配置到生产级服务部署的 12 篇实战文档，是进入 [[KnowledgeBase/entities/Kubernetes|Kubernetes]] 生态的前置基础。所有源文档的详细摘要见 [[KnowledgeBase/sources/docker-batch-summary|Docker 来源批量摘要]]。

## 核心功能

### 安装与基础配置
- **系统支持**：覆盖 CentOS 和 Ubuntu 两种主流 Linux 发行版的安装流程
- **镜像加速**：阿里云镜像源配置，解决国内拉取速度问题
- **内核参数调优**：开启 `bridge-nf-call-iptables` 和 `ip_forward`，确保容器网络正常工作
- **私有仓库**：[[KnowledgeBase/entities/Harbor|Harbor]] 私有镜像仓库搭建，企业级镜像管理

### 镜像构建与编排
- **Dockerfile**：支持多种语言（Nginx、Tomcat、Httpd、Go、Python）的镜像构建，从手动容器内配置到 Dockerfile 自动化构建
- **docker-compose**：12 篇文档中绝大多数使用 [[KnowledgeBase/entities/Docker Compose|Docker Compose]] 进行服务编排，是单机多容器场景的核心工具
- **网络原理**：宿主机高位端口到容器端口的映射通过 docker0 网桥 + veth pair 实现

### 高级配置
- **GPU 支持**：通过 nvidia-docker2 实现 GPU 容器化，依赖链为 libnvidia-container -> nvidia-container-toolkit -> nvidia-container-runtime，使用 `--gpus all` 参数启动 GPU 容器
- **代理配置**：Docker daemon 代理需在 `docker.service` 的 `[Service]` 段配置 `HTTP_PROXY`/`HTTPS_PROXY`，`~/.docker/config.json` 仅为容器内进程配置代理，不影响镜像拉取

## 部署实践总结

本仓库记录了大量基于 Docker 的服务部署实战，按场景分类如下：

### 监控与日志（可观测性闭环）
- **指标监控**：[[KnowledgeBase/entities/Prometheus|Prometheus]] + [[KnowledgeBase/entities/Grafana|Grafana]] + cAdvisor，node_exporter 安装与 systemd 服务配置，Grafana Dashboard 模板导入
- **日志系统**：[[KnowledgeBase/entities/Loki|Loki]] + Promtail + Grafana 轻量级日志平台，基于标签索引而非全文索引，成本低于 ELK，LogQL 查询语法与 Prometheus 标签体系兼容

### DevOps 与管理工具
- **代码仓库**：[[KnowledgeBase/entities/GitLab|GitLab]] CE 部署，最低 4G 内存要求，通过 `gitlab.rb` 关闭不必要的 exporter 加速启动
- **容器管理**：Portainer docker-compose 部署与多节点 Agent 环境管理

### Web 服务与数据库
- **Web 服务**：Nginx、Tomcat、Httpd、Go、Python 等多种 Web 服务的容器化部署
- **LNMP 架构**：docker-compose 编排 Linux + Nginx + MySQL + PHP 完整网站环境
- **Redis 高可用**：一主二从 + 三哨兵架构，通过 docker-compose 编排

### 轻量级工具
- **Homebox**：基于 Go + SQLite 的家庭库存管理系统，<50MB 内存占用
- **GoCron**：可视化定时任务调度系统，支持 YAML 配置文件定义任务
- **NextTrace**：Go 开发的可视化路由追踪工具，需 `--network host` 和 `--privileged` 模式

### 生产环境关注点
- 多篇文档涉及安全配置（密码设置、端口规划）、性能优化（关闭不必要服务、资源限制）和持久化（数据卷挂载），反映了从实验到生产的关注点转移

## 相关概念与实体

| 类型 | 实体 |
|------|------|
| 编排工具 | [[KnowledgeBase/entities/Docker Compose|Docker Compose]]、[[KnowledgeBase/entities/Kubernetes|Kubernetes]] |
| 构建工具 | [[KnowledgeBase/entities/Dockerfile|Dockerfile]] |
| 镜像仓库 | [[KnowledgeBase/entities/Harbor|Harbor]] |
| 监控生态 | [[KnowledgeBase/entities/Prometheus|Prometheus]]、[[KnowledgeBase/entities/Grafana|Grafana]]、[[KnowledgeBase/entities/Loki|Loki]] |
| 运行时 | [[KnowledgeBase/entities/containerd|containerd]]（Docker 引擎中剥离的核心运行时） |
| DevOps | [[KnowledgeBase/entities/GitLab|GitLab]]、[[KnowledgeBase/entities/Redis|Redis]] |
| GPU | [[KnowledgeBase/entities/NVIDIA GPU|NVIDIA GPU]] |

## 知识空白

- Docker 多阶段构建与镜像体积优化实践
- Docker 与 containerd 的关系及运行时迁移路径
- Docker Compose V2 与 Kubernetes 的功能对比
- Docker 网络模式（bridge/host/overlay/macvlan）深入对比
- Docker 安全加固（Seccomp、AppArmor、rootless 模式）
- Docker BuildKit 高级构建功能
