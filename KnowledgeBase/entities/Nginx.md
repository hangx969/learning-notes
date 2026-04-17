---
title: Nginx
tags:
  - knowledgebase/entity
  - web-server
  - load-balancer
date: 2026-04-17
---

## 简介

Nginx 是高性能的 Web 服务器和反向代理，广泛用于负载均衡、静态资源服务和 API 网关。在 Kubernetes 生态中，ingress-nginx 是最流行的 Ingress 控制器实现。在本仓库中还涉及 LNMP 架构部署、Keepalived + Nginx 高可用方案、OAuth2 Proxy 集成等场景。

## 在本仓库中的位置

- `Docker-Kubernetes/k8s-networking-service-mesh/` 中涉及 ingress-nginx 控制器部署（hostNetwork 模式）
- `Docker-Kubernetes/docker/` 中涉及 Nginx Dockerfile 部署和 LNMP 栈
- `Python/` 中涉及 Python 自动化运维 Nginx 的脚本
- `Docker-Kubernetes/k8s-security-auth/` 中涉及 Nginx + OAuth2 Proxy 认证

## 相关概念与实体

- [[KnowledgeBase/entities/Ingress|Ingress]]：ingress-nginx 是最常用的 Ingress 控制器
- [[KnowledgeBase/entities/Docker|Docker]]：LNMP 栈容器化部署
- [[KnowledgeBase/entities/Docker-Compose|Docker Compose]]：LNMP 栈编排
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s 集群流量入口
