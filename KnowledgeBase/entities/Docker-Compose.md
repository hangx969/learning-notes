---
title: Docker Compose
tags:
  - knowledgebase/entity
  - container-orchestration
date: 2026-04-17
aliases:
  - docker-compose
---

## 简介

Docker Compose 是 Docker 官方的单机多容器编排工具，通过 `docker-compose.yml` 文件声明式定义多个服务及其依赖关系，实现一键启停。V2 版本已集成为 `docker compose` 子命令。常用于本地开发环境和简单部署场景（如 LNMP 栈）。

## 在本仓库中的位置

- `Docker-Kubernetes/docker/` 目录下有 Docker Compose 部署实践（LNMP 栈等）
- 与 Kubernetes 的多容器编排能力形成对比

## 相关概念与实体

- [[KnowledgeBase/entities/Docker|Docker]]：Docker Compose 是 Docker 生态的编排工具
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：生产级容器编排，比 Compose 更强大
- [[KnowledgeBase/entities/Nginx|Nginx]]：LNMP 栈中的 Web 服务器组件
