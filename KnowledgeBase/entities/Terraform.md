---
title: "Terraform"
tags:
  - knowledgebase/entity
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/README]]"
  - "[[IaC/terraform/terraform-basics]]"
  - "[[IaC/terraform/terraform-hcl]]"
  - "[[IaC/terraform/terraform-variables-outputs]]"
  - "[[IaC/terraform/terraform-expressions]]"
  - "[[IaC/terraform/terraform-providers]]"
  - "[[IaC/terraform/terraform-resources-dependencies]]"
  - "[[IaC/terraform/terraform-count-for-each]]"
  - "[[IaC/terraform/terraform-state]]"
  - "[[IaC/terraform/terraform-backends-workspaces]]"
  - "[[IaC/terraform/terraform-modules]]"
  - "[[IaC/terraform/terraform-import-refactoring]]"
  - "[[IaC/terraform/terraform-workflow-troubleshooting]]"
  - "[[IaC/terraform/terraform-testing-cicd]]"
  - "[[IaC/terraform/terraform-container-management]]"
  - "[[IaC/terraform/terraform-docs]]"
aliases:
  - "terraform"
  - "TF"
  - "HashiCorp Terraform"
---

# Terraform

## 简介

Terraform 是 HashiCorp 的基础设施即代码工具，通过声明式 HCL、Provider 插件和状态记录管理资源生命周期。统一的是配置语言与工作流，各云平台、容器系统的资源 schema 和授权仍需分别理解。

## 核心功能

- Write → Plan → Apply：编写声明、审查变更动作、执行并核对结果；init 负责准备 Backend、Provider 和模块。
- 变量、表达式与模块：参数化配置、复用命名和结构，并通过输入输出形成接口。
- State 与 Backend：跟踪资源身份、漂移和状态访问，支持 import、moved、removed 等管理关系变更。
- Provider：连接 Azure、阿里云、Docker、Kubernetes、Helm、Nomad 等系统，版本和认证分别管理。
- 测试与协作：从格式和配置检查到 mock 测试、真实计划、审批执行与平台验收。

## 使用场景

- 以可 review 的配置管理云网络、计算、存储、权限等资源。
- 用共享 Module 构建结构相近的环境，配合独立状态和身份表达隔离边界。
- 管理容器基础资源或 Helm Release，明确与应用交付工具的资源所有权。

## 相关概念与实体

- [[KnowledgeBase/concepts/基础设施即代码|基础设施即代码]]：声明和版本管理的基础。
- [[KnowledgeBase/concepts/Terraform状态管理|状态管理]]：配置地址、实际 ID 和漂移处理。
- [[KnowledgeBase/concepts/Terraform模块化|模块化]]：复用与接口边界。
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]：把基础设施变更融入协作流程。
- [[KnowledgeBase/entities/Azure|Azure]]、[[KnowledgeBase/entities/Aliyun|Aliyun]]：云平台资源管理。
- [[KnowledgeBase/entities/Docker|Docker]]、[[KnowledgeBase/entities/Kubernetes|Kubernetes]]、[[KnowledgeBase/entities/Helm|Helm]]：容器相关 Provider 场景。

## 在本仓库中的覆盖

- [[IaC/terraform/README|基础系列学习路线]]：15 篇中文正文、实验约定和 GitHub 学习资料入口。
- [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]：按依赖顺序关联正文和逐篇来源摘要。
- [[IaC/terraform/terraform-basics|基础概念]]：本地文件创建、变更和清理。
- [[IaC/terraform/terraform-providers|Provider]]：版本锁定、alias、认证和 Azure 中国区资源组实验。
- [[IaC/terraform/terraform-state|State]]、[[IaC/terraform/terraform-backends-workspaces|Backend 与多环境]]：漂移、锁定和环境边界。
- [[IaC/terraform/terraform-modules|Module]]、[[IaC/terraform/terraform-import-refactoring|导入与重构]]：复用接口与身份迁移。
- [[IaC/terraform/terraform-testing-cicd|测试与协作]]：模块 mock 测试和 CI 示例。
- [[IaC/terraform/terraform-container-management|容器管理]]、[[IaC/terraform/terraform-docs|文档生成]]：扩展实战。

## 知识空白

- 云端和集群中的完整部署、故障恢复与实际业务验收证据。
- HCP Terraform/Enterprise 的组织权限、策略执行和私有模块发布实战。
- 大规模 State 分层、跨团队移交与多账号设计。
- Terragrunt 等编排方式与本系列基础结构的比较。
