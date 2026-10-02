---
title: "Terraform Backend、Workspace 与多环境 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/09_terraform_后端工作空间与多环境]]"
aliases:
  - "TerraformBackend、Workspace 与多环境摘要"
---

# Terraform Backend、Workspace 与多环境 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/09_terraform_后端工作空间与多环境]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

介绍状态存储、权限与锁定，并给出 Azure Blob 连接、本地迁移和 S3 锁文件示例。通过内置资源实验区分 Workspace 状态隔离与环境权限隔离。

## 关键知识点

1. Backend 与 Provider 的目标和认证独立，Backend 不引用普通运行变量和资源。
2. init -migrate-state 尝试迁移记录，reconfigure 不迁移；迁移后须核对地址与计划。
3. 显式 Azure use_cli 要求 1.11+，S3 use_lockfile 要求 1.10+；DynamoDB 锁定已弃用；CLI Workspace 不等同于 HCP Workspace。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
