---
title: "Terraform Docker、Kubernetes、Helm 与 Nomad 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/terraform-container-management]]"
aliases:
  - Terraform容器管理摘要
  - "TerraformDocker、Kubernetes、Helm 与 Nomad摘要"
---

# Terraform Docker、Kubernetes、Helm 与 Nomad 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/terraform-container-management]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-05-04
- **更新日期**：2026-10-02

## 摘要

通过 Docker 容器、已有集群 Deployment、最小本地 Helm Chart 和 Nomad Job，说明 Terraform 在各容器层的连接与所有权。修正旧镜像属性、版本语法和不完整资源示例。

## 关键知识点

1. Docker 3.x 使用 image_id；keep_locally 控制销毁时保留镜像，不表示仅用本地镜像。
2. 集群创建与集群配置分层，云身份、Kubernetes 认证和 RBAC 分别核对；manifest 需可用 schema。
3. Helm 3.x 使用 kubernetes 对象配置；Release 内对象不应被其他工具重复声明，Secret 显示遮盖不保证不入 State。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]
- [[KnowledgeBase/entities/Docker|Docker]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
