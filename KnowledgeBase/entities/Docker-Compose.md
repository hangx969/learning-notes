---
title: Docker Compose
tags:
  - knowledgebase/entity
  - container-orchestration
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/docker/docker基础]]"
  - "[[Docker-Kubernetes/docker/docker部署lnmp网站]]"
  - "[[Docker-Kubernetes/docker/docker部署gitlab]]"
  - "[[Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel]]"
  - "[[Docker-Kubernetes/docker/docker部署loki]]"
  - "[[Docker-Kubernetes/k8s-image-management/Harbor 部署与使用指南]]"
  - "[[AI/企业级私有化大模型/基于docker部署vLLM和LiteLLM私有化大模型]]"
  - "[[Docker-Kubernetes/k8s-db-middleware/k8s部署springcloud电商项目]]"
aliases:
  - docker-compose
  - docker compose
---

## 简介

Docker Compose 是 Docker 官方的单机多容器编排工具，通过 `docker-compose.yml` 文件声明式定义多个服务及其依赖关系，实现一键启停。V2 版本已集成为 `docker compose` 子命令。常用于本地开发环境和简单部署场景（如 LNMP 栈）。

## 核心功能

- **声明式多服务定义**：在一个 `docker-compose.yml` 中把一组关联容器定义为一个项目，配置镜像、端口映射、数据卷、环境变量和重启策略
- **项目生命周期管理**：`docker-compose up -d` 一键启动全部服务，`ps`、`stop`、`start`、`restart`、`down` 管理整个项目
- **自定义网络**：服务加入同一自定义网络后可按容器名互访（如 LNMP 中 PHP 通过 MySQL 容器名连接数据库）
- **GPU 设备预留**：通过 `deploy.resources.reservations.devices` 让容器使用宿主机 GPU
- **两种安装方式**：随 Docker 安装 `docker-compose-plugin`（`docker compose`），或下载独立二进制（`docker-compose`）

## 使用场景

- 单机部署多容器 Web 栈，如 LNMP（Nginx + PHP-FPM + MySQL）
- 单机部署平台工具：GitLab CE、Portainer、Harbor（离线安装依赖 Compose）、Pinpoint
- 快速搭建中间件与日志实验环境：Redis 主从 + Sentinel、Loki + Promtail + Grafana
- 在单台 GPU 服务器上运行 vLLM 模型推理服务

## 相关概念与实体

- [[KnowledgeBase/entities/Docker|Docker]]：Docker Compose 是 Docker 生态的编排工具
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：生产级容器编排，比 Compose 更强大
- [[KnowledgeBase/entities/Nginx|Nginx]]：LNMP 栈中的 Web 服务器组件
- [[KnowledgeBase/entities/Harbor|Harbor]]：离线安装基于 Docker Compose，通过 `docker-compose stop/start` 启停
- [[KnowledgeBase/entities/GitLab|GitLab]]：可用 Compose 单机部署 GitLab CE
- [[KnowledgeBase/entities/Redis|Redis]]：用 Compose 部署 Redis 主从与哨兵
- [[KnowledgeBase/entities/vLLM|vLLM]]：用 Compose 编排 vLLM 模型服务并预留 GPU

## 在本仓库中的覆盖

- `Docker-Kubernetes/docker/` 目录下有 Docker Compose 部署实践（LNMP 栈等）
- 与 Kubernetes 的多容器编排能力形成对比
- [[Docker-Kubernetes/docker/docker基础|docker基础]]：Compose 的背景与三步使用流程、插件与独立二进制两种安装方式，以及基于 Compose 安装 Harbor
- [[Docker-Kubernetes/docker/docker部署lnmp网站|Docker部署LNMP网站]]：Compose 常用命令，用 docker-compose.yml 编排 Nginx、PHP、MySQL 及自定义网络
- [[Docker-Kubernetes/docker/docker部署gitlab|docker部署gitlab]]：用 Compose 部署 GitLab CE，配置 `GITLAB_OMNIBUS_CONFIG`、端口映射、数据卷与日志驱动
- [[Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel|docker部署UI工具portainer-部署redis-sentinel]]：用 Compose 部署 Portainer，以及 Redis 主从与哨兵集群
- [[Docker-Kubernetes/docker/docker部署loki|docker部署loki]]：用官方 Compose 文件部署 Loki、Promtail、Grafana，并在新服务器上单独运行 Promtail
- [[Docker-Kubernetes/k8s-image-management/Harbor 部署与使用指南|Harbor 部署与使用指南]]：单机实验与离线环境使用 Docker Compose 部署 Harbor 及启停
- [[AI/企业级私有化大模型/基于docker部署vLLM和LiteLLM私有化大模型|基于docker部署vLLM和LiteLLM私有化大模型]]：用 Compose 编排 vLLM 模型服务，配置共享内存、健康检查与 GPU 设备预留
- [[Docker-Kubernetes/k8s-db-middleware/k8s部署springcloud电商项目|k8s部署springcloud电商项目]]：安装 docker-compose，用于部署 Harbor 与 Pinpoint

## 知识空白

- 仓库中尚无 Compose 文件语法的系统说明（如 `depends_on` 与健康检查条件、`profiles`、多文件覆盖、`env_file`）
- 仓库中尚无 Docker Swarm 或 `docker stack` 多主机编排的内容
- 仓库中尚无将 Compose 应用迁移到 Kubernetes（如 kompose 转换）的实践
