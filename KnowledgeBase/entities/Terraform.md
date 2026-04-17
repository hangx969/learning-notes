---
title: Terraform
tags:
  - knowledgebase/entity
date: 2026-04-17
sources:
  - "[[IaC/terraform-basics]]"
  - "[[IaC/terraform-docs]]"
---

# Terraform

## 定义
Terraform 是 HashiCorp 开发的基础设施即代码（Infrastructure as Code, IaC）工具，基于 Go 语言编写，使用声明式的 HCL（HashiCorp Configuration Language）语言来定义和管理云资源及本地基础设施的完整生命周期。

## 核心工作流

Terraform 采用三阶段工作流：
1. **`terraform init`**：初始化工作目录，下载 Provider 插件
2. **`terraform plan`**：计算当前状态与目标状态的差异，生成执行计划
3. **`terraform apply`**：执行变更，将基础设施调整至目标状态

## 核心文件结构
- **main.tf**：资源定义主文件
- **variable.tf**：变量声明
- **terraform.tfvars**：变量赋值
- **terraform.tfstate**：状态文件，记录已部署资源的实际状态

## 与 ARM Template/Bicep 的对比
Terraform 与 Azure 原生的 ARM Template / Bicep 均可实现 IaC，但 Terraform 的优势在于**多云支持**，通过不同的 Provider 即可管理 [[KnowledgeBase/entities/Azure|Azure]]、[[KnowledgeBase/entities/Aliyun|Aliyun]] 等多个云平台的资源。

## terraform-docs 文档工具
terraform-docs 是 Terraform Module 的文档自动生成工具，可自动提取 Requirements、Usage、Resources、Inputs、Outputs 等信息生成 Markdown 文档。支持通过配置模板自定义输出格式和注入模式。

## 在本仓库中的位置
主要出现在 `IaC/` 目录下，涵盖 Terraform 基础用法和文档编写。与 [[KnowledgeBase/entities/Azure|Azure]] 和 [[KnowledgeBase/entities/Aliyun|Aliyun]] 等云平台配合使用，实现多云环境的自动化资源编排。仓库中包含 Azure 资源组创建示例（azurerm Provider 配置、az login 认证流程）。

## 相关文章
- [[IaC/terraform-basics|terraform-basics]]
- [[IaC/terraform-docs|terraform-docs]]

## 关联概念
- [[KnowledgeBase/entities/Azure|Azure]]
- [[KnowledgeBase/entities/Aliyun|Aliyun]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]
- [[KnowledgeBase/entities/AKS|AKS]]

## 可延展方向
- Terraform Module 开发与最佳实践
- Terraform State 管理与远程后端（Azure Storage / Aliyun OSS）
- Terraform 与 CI/CD 管道集成（GitHub Actions、Azure DevOps Pipeline）
- Terragrunt 多环境管理
- HCL 语言进阶语法与动态块
