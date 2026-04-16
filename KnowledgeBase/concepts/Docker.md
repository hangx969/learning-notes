---
title: Docker
tags:
  - knowledgebase/concept
date: 2026-04-16
---

# Docker

## 定义
Docker 是一种容器运行时技术，提供镜像构建、容器编排（Compose）、GPU 支持等能力。本仓库记录了 Docker 基础知识与大量服务部署实战，是进入 Kubernetes 生态的前置基础。

## 在本仓库中的位置
主要集中在 `Docker-Kubernetes/docker/` 目录，共 12 篇文章，覆盖基础、代理配置、GPU、各类服务部署。

## 相关文章
- [docker基础](../../Docker-Kubernetes/docker/docker基础.md)
- [docker配置代理](../../Docker-Kubernetes/docker/docker配置代理.md)
- [docker配置NVIDIA GPU](../../Docker-Kubernetes/docker/docker配置NVIDIA%20GPU.md)
- [docker部署prometheus-grafana-cAdvisior监控](../../Docker-Kubernetes/docker/docker部署prometheus-grafana-cAdvisior监控.md)
- [docker部署loki](../../Docker-Kubernetes/docker/docker部署loki.md)
- [docker部署gitlab](../../Docker-Kubernetes/docker/docker部署gitlab.md)
- [docker部署nginx-tomcat-httpd-go-python服务](../../Docker-Kubernetes/docker/docker部署nginx-tomcat-httpd-go-python服务.md)
- [docker部署lnmp网站](../../Docker-Kubernetes/docker/docker部署lnmp网站.md)
- [docker部署UI工具portainer-部署redis-sentinel](../../Docker-Kubernetes/docker/docker部署UI工具portainer-部署redis-sentinel.md)
- [docker部署仓库平台homebox](../../Docker-Kubernetes/docker/docker部署仓库平台homebox.md)
- [docker部署定时任务工具gocron](../../Docker-Kubernetes/docker/docker部署定时任务工具gocron.md)
- [docker部署路由监控工具NextTrace](../../Docker-Kubernetes/docker/docker部署路由监控工具NextTrace.md)

## 关联概念
- [Kubernetes](Kubernetes.md)
- [Helm](Helm.md)
- [Prometheus](Prometheus.md)
- [Grafana](Grafana.md)

## 可延展方向
- Docker 多阶段构建与镜像优化
- Docker 与 containerd 的关系及迁移
- Docker Compose V2 与 Kubernetes 的对比
