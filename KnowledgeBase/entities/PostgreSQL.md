---
title: PostgreSQL
tags:
  - knowledgebase/entity
  - database
date: 2026-04-17
aliases:
  - Postgres
  - PG
---

## 简介

PostgreSQL 是功能最强大的开源关系型数据库，支持丰富的数据类型、扩展性和 ACID 事务。在本仓库中涉及 Helm 部署 PostgreSQL HA 集群（Pgpool + repmgr + witness 架构）、KubeBlocks 管理、Python ORM 操作（psycopg2/SQLAlchemy）以及阿里云 RDS 引擎选型。

## 在本仓库中的位置

- `Docker-Kubernetes/k8s-db-middleware-UI/` 中涉及 Helm 部署 PostgreSQL HA
- `Docker-Kubernetes/k8s-misc/` 中涉及 KubeBlocks 管理 PostgreSQL
- `Python/` 中涉及 psycopg2/SQLAlchemy 操作 PostgreSQL
- `Aliyun/` 中涉及阿里云 RDS PostgreSQL 引擎

## 相关概念与实体

- [[KnowledgeBase/entities/Helm|Helm]]：Helm Chart 部署 PostgreSQL HA
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s 上运行有状态数据库
- [[KnowledgeBase/entities/MySQL|MySQL]]：另一个主流关系型数据库，对比对象
- [[KnowledgeBase/entities/Aliyun|Aliyun]]：阿里云 RDS 托管数据库服务
