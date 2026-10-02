---
title: "Terraform"
tags:
  - knowledgebase/entity
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/README]]"
  - "[[IaC/terraform/01_terraform_基础概念与第一个项目]]"
  - "[[IaC/terraform/02_terraform_配置语法与文件结构]]"
  - "[[IaC/terraform/03_terraform_变量与输出]]"
  - "[[IaC/terraform/04_terraform_表达式函数与模板]]"
  - "[[IaC/terraform/05_terraform_提供者版本与认证]]"
  - "[[IaC/terraform/06_terraform_资源数据源与依赖]]"
  - "[[IaC/terraform/07_terraform_循环与批量资源]]"
  - "[[IaC/terraform/08_terraform_状态漂移与状态操作]]"
  - "[[IaC/terraform/09_terraform_后端工作空间与多环境]]"
  - "[[IaC/terraform/10_terraform_模块开发与复用]]"
  - "[[IaC/terraform/11_terraform_资源导入与重构]]"
  - "[[IaC/terraform/12_terraform_工作流计划阅读与排错]]"
  - "[[IaC/terraform/13_terraform_测试与持续集成交付]]"
  - "[[IaC/terraform/14_terraform_容器管理实战]]"
  - "[[IaC/terraform/15_terraform_模块文档生成]]"
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
- Provider：本系列通过阿里云、Kubernetes 和 Helm 说明资源 API、版本和认证的边界。
- 测试与协作：从格式和配置检查到 mock 测试、真实计划、审批执行与平台验收。

本系列参考 `alicloud-operations` 的实际配置，并使用脱敏裁剪与教学新增代码；具体生产路径和占位符约定见 [[IaC/terraform/README|系列入口]]。

## 使用场景

- 以可 review 的配置管理云网络、计算、存储、权限等资源。
- 用共享 Module 构建结构相近的环境，配合独立状态和身份表达隔离边界。
- 管理容器基础资源或 Helm Release，明确与应用交付工具的资源所有权。

## 相关概念与实体

- [[KnowledgeBase/concepts/基础设施即代码|基础设施即代码]]：声明和版本管理的基础。
- [[KnowledgeBase/concepts/Terraform状态管理|状态管理]]：配置地址、实际 ID 和漂移处理。
- [[KnowledgeBase/concepts/Terraform模块化|模块化]]：复用与接口边界。
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]：把基础设施变更融入协作流程。
- [[KnowledgeBase/entities/Aliyun|Aliyun]]：OSS、CMS、RAM 与 ACK 的示例来源。
- [[KnowledgeBase/entities/Kubernetes|Kubernetes]]、[[KnowledgeBase/entities/Helm|Helm]]：已有 ACK 集群中的连接与资源管理。

## 在本仓库中的覆盖

- [[IaC/terraform/README|基础系列学习路线]]：15 篇中文正文、实验约定和 GitHub 学习资料入口。
- [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]：按依赖顺序关联正文和逐篇来源摘要。
- [[IaC/terraform/01_terraform_基础概念与第一个项目|基础概念]]：从临时策略条件检查裁剪出的内置资源实验。
- [[IaC/terraform/05_terraform_提供者版本与认证|Provider]]：版本锁定、AssumeRole alias、认证和独立 OSS 空桶实验。
- [[IaC/terraform/08_terraform_状态漂移与状态操作|State]]、[[IaC/terraform/09_terraform_后端工作空间与多环境|Backend 与多环境]]：漂移、锁定和环境边界。
- [[IaC/terraform/10_terraform_模块开发与复用|Module]]、[[IaC/terraform/11_terraform_资源导入与重构|导入与重构]]：复用接口与身份迁移。
- [[IaC/terraform/13_terraform_测试与持续集成交付|测试与协作]]：基于 CMS 模块接口补充的教学 mock 测试与 CI。
- [[IaC/terraform/14_terraform_容器管理实战|容器管理]]、[[IaC/terraform/15_terraform_模块文档生成|文档生成]]：生产 ACK 连接链的教学改编，以及 CMS 模块接口文档生成。

## 知识空白

- 云端和集群中的完整部署、故障恢复与实际业务验收证据。
- HCP Terraform/Enterprise 的组织权限、策略执行和私有模块发布实战。
- 大规模 State 分层、跨团队移交与多账号设计。
- Terragrunt 等编排方式与本系列基础结构的比较。
