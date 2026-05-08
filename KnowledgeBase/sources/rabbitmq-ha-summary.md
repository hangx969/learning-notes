---
title: Helm 部署 RabbitMQ HA 摘要
tags:
  - knowledgebase/source
  - docker-kubernetes/middleware
  - rabbitmq
date: 2026-05-08
sources:
  - "[[Docker-Kubernetes/k8s-db-middleware/helm部署rabbitmq-ha]]"
aliases:
  - RabbitMQ HA Summary
---

# Helm 部署 RabbitMQ 高可用集群摘要

## 元信息

- **原始文档**：[[Docker-Kubernetes/k8s-db-middleware/helm部署rabbitmq-ha]]
- **领域**：Kubernetes 中间件部署
- **摄入日期**：2026-05-08

## 摘要

使用 aliyun/rabbitmq-ha Helm Chart 在 Kubernetes 上部署 RabbitMQ 高可用集群（StatefulSet 模式）。文档覆盖 Chart 下载、values 配置（认证、镜像、持久化存储）、旧版 API 兼容性修复、安装与管理界面访问。

## 关键知识点

1. **Chart 来源**：使用 `aliyun/rabbitmq-ha` Chart（版本 1.0.0），基于 rabbitmq:3.7-alpine 镜像
2. **关键配置**：`rabbitmqUsername/Password` 认证、NodePort 服务暴露、`persistentVolume.enabled` 控制数据持久化（默认关闭）
3. **API 版本兼容**：旧版 Chart 需手动修改 `rbac.authorization.k8s.io/v1beta1` → `v1`、`apps/v1beta1` → `apps/v1`，并为 StatefulSet 添加 `spec.selector.matchLabels`
4. **部署方式**：`helm install rabbitmq-ha ./rabbitmq-ha`，通过 NodePort 访问管理界面

## 涉及的概念与实体

- [[KnowledgeBase/entities/Kubernetes]]：运行平台
- [[KnowledgeBase/entities/Helm]]：包管理与部署工具
- [[KnowledgeBase/concepts/高可用架构]]：RabbitMQ 集群实现高可用

## 值得注意

- 该 Chart 版本较旧（1.0.0，基于 RabbitMQ 3.7），API 版本需手动适配新版 K8s，生产环境建议评估 Bitnami 维护的 `bitnami/rabbitmq` Chart（更活跃、支持更新版本）
- 默认关闭持久化存储、使用明文默认密码，仅适合测试环境快速验证
