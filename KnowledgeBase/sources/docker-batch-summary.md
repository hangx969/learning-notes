---
title: Docker 来源批量摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/docker
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

# Docker 来源批量摘要

## 元信息
- **原始目录**：`Docker-Kubernetes/docker/`
- **文档数量**：12 篇
- **领域**：Docker-Kubernetes
- **摄入日期**：2026-04-17

## 整体概述
本批次文档涵盖 Docker 的基础知识与实战部署场景。内容从 Docker 安装配置（CentOS/Ubuntu）、镜像管理、Dockerfile 编写、docker-compose 编排入手，延伸到多种常见服务的容器化部署实践，包括 Web 服务（Nginx、Tomcat、LNMP）、DevOps 工具（GitLab、Portainer）、监控与日志系统（Prometheus、Grafana、Loki）、以及 GPU 支持和网络代理等高级配置。整体构成了一套从入门到生产实践的 Docker 操作手册。

## 各文档摘要

### [[Docker-Kubernetes/docker/docker基础|Docker基础]]
- 核心内容：Docker 在 CentOS/Ubuntu 上的安装流程、镜像加速配置、内核参数调优，以及 Docker 基础概念（镜像、容器、Dockerfile、docker-compose、Harbor 仓库）的全面介绍。
- 关键知识点：
  - CentOS 上 Docker CE 安装与阿里云镜像源配置
  - 内核参数 `bridge-nf-call-iptables` 与 `ip_forward` 开启
  - Dockerfile 指令与 docker-compose 编排基础
  - Harbor 私有镜像仓库搭建

### [[Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel|Docker部署Portainer与Redis-Sentinel]]
- 核心内容：使用 docker-compose 部署 Portainer 容器管理 UI 工具，并基于 Portainer 搭建 Redis 一主二从 + 三哨兵高可用架构。
- 关键知识点：
  - Portainer docker-compose 部署与多节点 Agent 环境管理
  - Redis 主从复制与 Sentinel 哨兵选举机制
  - docker-compose 编排 Redis 集群的端口与密码配置

### [[Docker-Kubernetes/docker/docker部署gitlab|Docker部署GitLab]]
- 核心内容：通过 docker-compose 部署 GitLab CE，包括端口映射、数据持久化、性能优化（关闭内置 Prometheus/Grafana），以及 root 密码修改。
- 关键知识点：
  - GitLab 容器最低 4G 内存要求
  - `external_url` 与宿主机端口必须一致
  - 通过 `gitlab.rb` 关闭不必要的 exporter 加速启动
  - `gitlab-rails console` 修改 root 密码

### [[Docker-Kubernetes/docker/docker部署lnmp网站|Docker部署LNMP网站]]
- 核心内容：使用 docker-compose 编排 Linux+Nginx+MySQL+PHP (LNMP) 网站环境，涵盖镜像准备、Nginx 配置挂载、MySQL 初始化与 PHP 连接配置。
- 关键知识点：
  - docker-compose 编排多服务（Nginx、MySQL、PHP）
  - Nginx 配置文件挂载与静态页面托管
  - docker-compose 常用命令（up/down/ps/start/stop）

### [[Docker-Kubernetes/docker/docker部署loki|Docker部署Loki日志系统]]
- 核心内容：介绍 Grafana Loki 日志系统的架构与特性，使用 docker-compose 部署 Loki + Promtail + Grafana 三组件日志收集与查询平台。
- 关键知识点：
  - Loki 基于标签索引而非全文索引，成本低于 ELK
  - Loki 架构：Loki（存储与查询）、Promtail（采集）、Grafana（展示）
  - LogQL 查询语法与 Grafana 数据源配置
  - 与 Prometheus 标签体系兼容，可对接 alertmanager

### [[Docker-Kubernetes/docker/docker部署nginx-tomcat-httpd-go-python服务|Docker部署Nginx-Tomcat-Httpd-Go-Python服务]]
- 核心内容：演示在 Docker 容器中分别部署 Nginx、Tomcat、Httpd、Go、Python 等 Web 服务，从手动容器内配置到 Dockerfile 自动化构建。
- 关键知识点：
  - 基于 CentOS 基础镜像手动安装 Nginx 并映射端口
  - 宿主机高位端口到容器端口的映射原理（docker0 网桥 + veth pair）
  - Dockerfile 构建多种语言的 Web 服务镜像

### [[Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控|Docker部署Prometheus-Grafana-cAdvisor监控]]
- 核心内容：在 Docker 中部署 Prometheus + Grafana + cAdvisor 监控体系，包括 node_exporter 安装、Prometheus 配置与 Grafana Dashboard 导入。
- 关键知识点：
  - node_exporter 安装与 systemd 服务配置
  - Prometheus 配置文件 `scrape_configs` 编写
  - cAdvisor 容器级监控指标采集
  - Grafana Dashboard 模板导入与数据源配置

### [[Docker-Kubernetes/docker/docker部署仓库平台homebox|Docker部署Homebox仓库平台]]
- 核心内容：使用 docker-compose 部署 Homebox 家庭库存管理系统，一个基于 Go 语言和 SQLite 的轻量级自托管应用。
- 关键知识点：
  - Homebox 设计理念：简洁、极速（<50MB 内存）、便携
  - docker-compose 单容器部署，数据持久化至本地目录
  - 自定义端口映射配置

### [[Docker-Kubernetes/docker/docker部署定时任务工具gocron|Docker部署GoCron定时任务工具]]
- 核心内容：部署 GoCron 可视化定时任务调度系统，基于 Go 后端与 Vue.js 前端，通过 YAML 配置文件定义定时任务。
- 关键知识点：
  - GoCron 配置文件结构：defaults（全局 cron 与环境变量）、jobs（任务列表与命令）
  - Docker 单容器运行，挂载配置目录
  - 支持环境变量继承与自定义覆盖

### [[Docker-Kubernetes/docker/docker部署路由监控工具NextTrace|Docker部署NextTrace路由监控工具]]
- 核心内容：使用 Docker 一键部署 NextTrace 可视化路由追踪工具，支持 IPv4/IPv6 网络路径分析。
- 关键知识点：
  - NextTrace 由 Go 开发，支持可视化路由追踪
  - 使用 `--network host` 和 `--privileged` 模式运行
  - Web UI 通过 30080 端口访问

### [[Docker-Kubernetes/docker/docker配置NVIDIA GPU|Docker配置NVIDIA GPU]]
- 核心内容：在 Docker 容器中配置 NVIDIA GPU 支持的完整流程，包括 NVIDIA 驱动安装、CUDA 驱动安装、nvidia-docker2 安装与验证。
- 关键知识点：
  - nvidia-docker2 原理：通过 nvidia-container-runtime-hook 检测 `NVIDIA_VISIBLE_DEVICES` 环境变量挂载 GPU
  - 依赖链：libnvidia-container -> nvidia-container-toolkit -> nvidia-container-runtime
  - 使用 `--gpus all` 参数启动 GPU 容器
  - CUDA Toolkit 环境变量配置

### [[Docker-Kubernetes/docker/docker配置代理|Docker配置代理]]
- 核心内容：为 Docker daemon 配置 HTTP/HTTPS 代理以拉取镜像，需通过 systemd 配置而非 daemon.json 或 `~/.docker/config.json`。
- 关键知识点：
  - Docker daemon 代理需在 `docker.service` 的 `[Service]` 段配置 `HTTP_PROXY` / `HTTPS_PROXY`
  - `~/.docker/config.json` 仅为容器内进程配置代理，不影响镜像拉取
  - Chrome 插件 Docker Image Downloader 可直接下载 docker.io/gcr.io 镜像

## 涉及的概念与实体
- [[KnowledgeBase/entities/Docker|Docker]]
- [[KnowledgeBase/entities/Docker Compose|Docker Compose]]
- [[KnowledgeBase/entities/Dockerfile|Dockerfile]]
- [[KnowledgeBase/entities/Nginx|Nginx]]
- [[KnowledgeBase/entities/Prometheus|Prometheus]]
- [[KnowledgeBase/entities/Grafana|Grafana]]
- [[KnowledgeBase/entities/GitLab|GitLab]]
- [[KnowledgeBase/entities/Redis|Redis]]
- [[KnowledgeBase/entities/Loki|Loki]]
- [[KnowledgeBase/entities/NVIDIA GPU|NVIDIA GPU]]
- [[KnowledgeBase/entities/Harbor|Harbor]]

## 交叉主题发现
- **docker-compose 是核心编排工具**：12 篇文档中绝大多数使用 docker-compose 进行服务编排，体现了 compose 在单机多容器场景下的核心地位。
- **监控与日志形成闭环**：Prometheus+Grafana+cAdvisor 提供指标监控，Loki+Promtail+Grafana 提供日志收集，两者共用 Grafana 展示层，形成统一的可观测性方案。
- **生产环境关注点**：多篇文档涉及安全配置（密码设置、端口规划）、性能优化（关闭不必要服务、资源限制）和持久化（数据卷挂载），反映了从实验到生产的关注点转移。
- **GPU 与代理属于进阶配置**：这两篇文档针对特定场景（深度学习、网络受限环境），是 Docker 基础之上的高级运维实践。
