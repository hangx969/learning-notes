---
title: "Terraform ACK、Kubernetes 与 Helm 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/14_terraform_容器管理实战]]"
aliases:
  - Terraform容器管理摘要
  - "Terraform ACK、Kubernetes 与 Helm 摘要"
---

# Terraform ACK、Kubernetes 与 Helm 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/14_terraform_容器管理实战]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02

## 摘要

以生产 `tool/data.tf`、`tool/providers.tf`、`tool/helm.tf` 和 `tool/external-secrets.tf` 为依据，演示对既有 ACK 实验集群读取凭证、配置 Kubernetes 与 Helm Provider，再创建 Namespace 和本地 Helm Chart release。生产配置关系被改写为独立教学项目；集群本身不由此练习创建或删除。

## 关键知识点

1. AliCloud 身份访问 ACK 凭证数据源；集群 API endpoint 与临时证书、私钥、CA 配置 Kubernetes/Helm Provider；随后资源管理 namespace 和 Helm release。Helm 的本地 chart 文件摘要用于把模板/values变化纳入 release 的计划差异。
2. Helm 2.17 使用生产源中的 `kubernetes {}` Provider 嵌套块语法；教学固定 Helm 2.17.0、Kubernetes 2.38.0 与 AliCloud 1.266.0。
3. Terraform state、计划和数据源仍可能保存敏感凭证；不要输出 kubeconfig/client key，不启用会在 Plan 时落盘 kubeconfig 的 `output_file`，State 应加密并限制访问。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]
- [[KnowledgeBase/entities/Helm|Helm]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 生产依据分别位于 `tool/` Terraform 文件；`monitoring/ack-addons-log-pipeline.tf` 是 Datadog 日志 pipeline，不是 ACK add-on 部署定义。示例 Chart、endpoint 输入和资源名称是教学新增。
- 只有授权的隔离 ACK 集群可用于练习；本轮只做 HCL 静态检查及 Helm Chart 的离线 lint/template，未运行 plan/apply、kubectl 或云端操作。
