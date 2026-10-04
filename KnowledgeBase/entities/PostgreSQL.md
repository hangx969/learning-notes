---
title: PostgreSQL
tags:
  - knowledgebase/entity
  - database
date: 2026-04-17
sources:
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署postgreSQL]]"
  - "[[Python/python-运维开发/python-postgresql]]"
  - "[[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群]]"
  - "[[Docker-Kubernetes/k8s-installation-management/k8s-Backstage-内部开发者平台IDP实战]]"
  - "[[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM]]"
  - "[[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml]]"
  - "[[Azure/Jfrog-artifactory-Azure]]"
  - "[[Aliyun/数据库/关系型数据库RDS]]"
aliases:
  - Postgres
  - PG
---

## 简介

PostgreSQL 是功能最强大的开源关系型数据库，支持丰富的数据类型、扩展性和 ACID 事务。在本仓库中涉及 Helm 部署 PostgreSQL HA 集群（Pgpool + repmgr + witness 架构）、KubeBlocks 管理、Python ORM 操作（psycopg2/SQLAlchemy）以及阿里云 RDS 引擎选型。

## 核心功能

- **关系型数据库能力**：遵循 SQL 标准，支持事务、外键、视图、触发器、JSON 数据类型和并行查询
- **高可用部署**：bitnami postgresql-ha 中 Pgpool 接入流量并分发查询实现读写分离，repmgr 自动切换主从，witness 提供额外投票防止脑裂
- **远程访问控制**：通过 `pg_hba.conf` 和 `postgresql.conf` 配置允许远程连接
- **客户端与编程访问**：用 `psql` 管理库表，Python 通过 psycopg2 或 SQLAlchemy ORM 操作数据库
- **云托管服务**：阿里云 RDS、Azure Database for PostgreSQL Flexible Server 提供托管的 PostgreSQL 实例

## 使用场景

- 作为平台组件的后端数据库：Harbor、GitLab、Backstage、LiteLLM、Artifactory
- 需要复杂查询和事务的应用（笔记对比认为 PostgreSQL 更注重标准符合性和扩展性）
- 在 K8s 上通过 Helm Chart 或 KubeBlocks 部署主备或高可用集群，并验证故障自动切换
- 生产环境优先考虑云厂商托管版（Backstage 笔记中的建议）

## 相关概念与实体

- [[KnowledgeBase/entities/Helm|Helm]]：Helm Chart 部署 PostgreSQL HA
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]：K8s 上运行有状态数据库
- [[KnowledgeBase/entities/MySQL|MySQL]]：另一个主流关系型数据库，对比对象
- [[KnowledgeBase/entities/Aliyun|Aliyun]]：阿里云 RDS 托管数据库服务
- [[KnowledgeBase/entities/Harbor|Harbor]]：KubeBlocks 创建的 PostgreSQL 集群作为 Harbor 外部数据库
- [[KnowledgeBase/concepts/高可用架构|高可用架构]]：Pgpool + repmgr + witness 的主备自动切换方案
- [[KnowledgeBase/concepts/Python运维开发|Python运维开发]]：用 psycopg2 与 SQLAlchemy 操作 PostgreSQL
- [[KnowledgeBase/entities/Azure|Azure]]：Azure Database for PostgreSQL 作为 Artifactory 数据库

## 在本仓库中的覆盖

- `Docker-Kubernetes/k8s-db-middleware/` 中涉及 Helm 部署 PostgreSQL HA
- `Docker-Kubernetes/kubeblocks/` 中涉及 KubeBlocks 管理 PostgreSQL
- `Python/` 中涉及 psycopg2/SQLAlchemy 操作 PostgreSQL
- `Aliyun/` 中涉及阿里云 RDS PostgreSQL 引擎
- [[Docker-Kubernetes/k8s-db-middleware/helm部署postgreSQL|helm部署postgreSQL]]：bitnami postgresql 与 postgresql-ha Chart，HA 模式的 Pgpool、repmgr、witness 组件，以及用 repmgr 查看集群状态
- [[Python/python-运维开发/python-postgresql|python-postgresql]]：PostgreSQL 安装与远程访问配置、psql 常用操作，psycopg2 增删改查与 SQLAlchemy ORM
- [[Docker-Kubernetes/kubeblocks/kubeblocks部署高可用harbor集群|kubeblocks部署高可用harbor集群]]：KubeBlocks 创建 replication 模式 PostgreSQL 主备集群作为 Harbor 外部数据库，并模拟主节点故障验证切换
- [[Docker-Kubernetes/k8s-installation-management/k8s-Backstage-内部开发者平台IDP实战|Backstage：K8s 一站式内部开发者平台实战]]：以 StatefulSet 部署 PostgreSQL 作为 Backstage 软件目录数据库
- [[AI/企业级私有化大模型/基于K8s部署vLLM和LiteLLM|基于K8s部署vLLM和LiteLLM]]：部署高可用 PostgreSQL（postgresql-ha）作为 LiteLLM 数据库
- [[Docker-Kubernetes/k8s-CICD/Gitlab/k8s部署Gitlab(11.8.1)-基于yaml|k8s部署Gitlab(11.8.1)-基于yaml]]：以 YAML 部署 PostgreSQL 作为 GitLab 后端数据库
- [[Azure/Jfrog-artifactory-Azure|Jfrog-artifactory-Azure]]：Azure Database for PostgreSQL Flexible Server 作为 Artifactory 数据库，配置 JDBC 连接
- [[Aliyun/数据库/关系型数据库RDS|关系型数据库RDS]]：阿里云 RDS 支持 PostgreSQL 引擎，以及账号授权方面与 MySQL 的差异

## 知识空白

- 仓库中尚无 PostgreSQL 备份恢复实践（如 pg_dump、pg_basebackup、基于 WAL 的时间点恢复）
- 仓库中尚无 PostgreSQL 性能调优内容（如 shared_buffers、work_mem、VACUUM、EXPLAIN ANALYZE）
- 仓库中尚无 PostgreSQL 流复制原理与手工主从配置
- 仓库中尚无 pgvector 等扩展的安装与使用，pgvector 仅在 RAG 简历示例中作为技术栈出现
