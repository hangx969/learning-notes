---
title: "Terraform模块化"
tags:
  - knowledgebase/concept
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/10_terraform_模块开发与复用]]"
  - "[[IaC/terraform/05_terraform_提供者版本与认证]]"
  - "[[IaC/terraform/11_terraform_资源导入与重构]]"
  - "[[IaC/terraform/15_terraform_模块文档生成]]"
aliases:
  - "Terraform Module概念"
---

# Terraform模块化

## 定义

Terraform 模块化把一组相关配置组织成具有输入、输出和版本要求的复用单元。子模块资源仍属于调用它的根配置 State，因此代码复用边界与独立执行边界需要分别设计。

## 核心要点

- 通过 variable/output 暴露接口，调用者不应耦合模块内部资源细节。
- 可复用子模块声明 Provider 来源，连接和凭证配置通常由根模块传递。
- 外部模块来源与版本要固定，Provider 锁文件不能替代模块版本约束。

## 与其他概念的关系

- [[KnowledgeBase/concepts/基础设施即代码|基础设施即代码]]：模块复用基础设施声明。
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform 状态管理]]：拆模块可能改变地址，需提供迁移路径。
- [[KnowledgeBase/entities/Terraform|Terraform]]：模块是 Terraform 的配置组织机制。

## 在本仓库中的覆盖

以下文章都覆盖该概念的定义、配置或维护步骤：

- [[IaC/terraform/10_terraform_模块开发与复用|Module 开发与复用]]
- [[IaC/terraform/05_terraform_提供者版本与认证|Provider、版本与认证]]
- [[IaC/terraform/11_terraform_资源导入与重构|Import、moved 与 removed]]
- [[IaC/terraform/15_terraform_模块文档生成|terraform-docs 模块文档生成]]

## 知识空白

- 大型模块接口兼容、发布版本和调用者升级的实际演练。
- Terragrunt 等编排工具与独立根状态分层的对照案例。
