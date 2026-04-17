---
title: Terraform
tags:
  - knowledgebase/entity
date: 2026-04-16
---

# Terraform

## 定义
Terraform 是 HashiCorp 开发的基础设施即代码（Infrastructure as Code, IaC）工具，使用声明式的 HCL（HashiCorp Configuration Language）语言来定义和管理云资源及本地基础设施的完整生命周期。

## 在本仓库中的位置
主要出现在 `IaC/` 目录下，涵盖 Terraform 基础用法和文档编写。与 [Azure](Azure.md) 和 [Aliyun](Aliyun.md) 等云平台配合使用，实现多云环境的自动化资源编排。

## 相关文章
- [terraform-basics](../../IaC/terraform-basics.md)
- [terraform-docs](../../IaC/terraform-docs.md)

## 关联概念
- [Azure](Azure.md)
- [Aliyun](Aliyun.md)
- [自动化运维](自动化运维.md)
- [AKS](AKS.md)

## 可延展方向
- Terraform Module 开发与最佳实践
- Terraform State 管理与远程后端（Azure Storage / Aliyun OSS）
- Terraform 与 CI/CD 管道集成（GitHub Actions、Azure DevOps Pipeline）
- Terragrunt 多环境管理
- HCL 语言进阶语法与动态块
