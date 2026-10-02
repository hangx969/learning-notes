---
title: "Terraform 基础学习地图"
tags:
  - knowledgebase/map
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
  - "Terraform主题地图"
  - "Terraform知识地图"
---

# Terraform 基础学习地图

## 阅读入口

[[IaC/terraform/README|Terraform 基础系列学习路线]] 包含 15 篇正文、实验约定和 GitHub 资料筛选说明，按从本地项目到实际协作的顺序组织。

## 概念与工具

- [[KnowledgeBase/concepts/基础设施即代码|基础设施即代码]]：把基础设施配置变成可审查、可复用的声明。
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform 状态管理]]：资源身份、漂移和管理记录。
- [[KnowledgeBase/concepts/Terraform模块化|Terraform 模块化]]：输入输出、复用与执行边界。
- [[KnowledgeBase/entities/Terraform|Terraform]]：工具能力、仓库覆盖和后续空白。

## 按学习顺序阅读

1. [[IaC/terraform/terraform-basics|基础概念与第一个项目]] — 从 IaC 的用途开始，用本地文件实验解释配置、State 和实际资源的关系。涵盖创建、修改、重复计划与清理的完整步骤。
2. [[IaC/terraform/terraform-hcl|HCL 语法与配置文件]] — 解释块、参数、类型、引用、模板转义和配置加载规则。以不创建平台资源的表达式实验帮助读懂后续配置。
3. [[IaC/terraform/terraform-variables-outputs|变量、locals 与 outputs]] — 通过生成应用 JSON 的完整实验，说明输入接口、派生值和输出接口。整理本地 CLI 变量优先级及敏感值的持久化边界。
4. [[IaC/terraform/terraform-expressions|表达式、函数与模板]] — 用服务集合、YAML 生成和文本模板实验介绍条件与 for 表达式。解释常用函数、dynamic、静态文件读取和不稳定值的使用陷阱。
5. [[IaC/terraform/terraform-providers|Provider、版本与认证]] — 区分 Core、Provider、来源声明和具体连接配置。保留 Azure 中国区场景，提供使用自身订阅的完整资源组实验，并解释 alias 和版本锁定。
6. [[IaC/terraform/terraform-resources-dependencies|Resource、Data Source 与依赖]] — 通过查询外部文件、生成受管理副本和 terraform_data 生命周期实验说明所有权、依赖图与变更方式。补充生命周期、条件检查和 provisioner 的边界。
7. [[IaC/terraform/terraform-count-for-each|count 与 for_each]] — 用两种批量本地文件实验解释索引和稳定 key 的区别。涵盖集合过滤、0/1 创建、链式 for_each 和地址迁移。
8. [[IaC/terraform/terraform-state|State、漂移与状态操作]] — 解释状态身份、三方比较和本地文件漂移，区分普通与 refresh-only 计划。整理状态命令、退出管理、敏感数据与恢复思路。
9. [[IaC/terraform/terraform-backends-workspaces|Backend、Workspace 与多环境]] — 介绍状态存储、权限与锁定，并给出 Azure Blob 连接、本地迁移和 S3 锁文件示例。通过内置资源实验区分 Workspace 状态隔离与环境权限隔离。
10. [[IaC/terraform/terraform-modules|Module 开发与复用]] — 实现为多个服务生成配置的完整本地模块，明确父子模块接口和 Provider 传递。比较本地、Registry 和 Git 来源及模块版本、State 和执行边界。
11. [[IaC/terraform/terraform-import-refactoring|Import、moved 与 removed]] — 以 Azure 资源组纳管和本地文件改名说明管理身份的建立与迁移。比较声明式导入、生成配置、退出管理和跨 State 移交。
12. [[IaC/terraform/terraform-workflow-troubleshooting|工作流、Plan 阅读与排错]] — 整理从写配置、审查计划到执行后验收的流程。解释计划动作、保存计划、选项、常见故障分层和部分失败恢复。
13. [[IaC/terraform/terraform-testing-cicd|测试与 CI/CD 协作]] — 区分格式、配置、逻辑、集成和真实部署验证，并给 app-config 模块增加 mock 计划测试。提供模块 CI 示例与正式计划审批执行的最小逻辑。
14. [[IaC/terraform/terraform-container-management|Docker、Kubernetes、Helm 与 Nomad]] — 通过 Docker 容器、已有集群 Deployment、最小本地 Helm Chart 和 Nomad Job，说明 Terraform 在各容器层的连接与所有权。修正旧镜像属性、版本语法和不完整资源示例。
15. [[IaC/terraform/terraform-docs|terraform-docs 模块文档生成]] — 介绍模块接口文档提取、README 注入和自定义 Go template。保留可复用配置与调用模板，并说明工具版本、递归生成、真实输出和 CI 一致性边界。

## 来源摘要

- [[KnowledgeBase/sources/iac-terraform-basics-summary|Terraform 基础概念与第一个项目 来源摘要]] — 从 IaC 的用途开始，用本地文件实验解释配置、State 和实际资源的关系。涵盖创建、修改、重复计划与清理的完整步骤。
- [[KnowledgeBase/sources/iac-terraform-hcl-summary|Terraform HCL 语法与配置文件 来源摘要]] — 解释块、参数、类型、引用、模板转义和配置加载规则。以不创建平台资源的表达式实验帮助读懂后续配置。
- [[KnowledgeBase/sources/iac-terraform-variables-outputs-summary|Terraform 变量、locals 与 outputs 来源摘要]] — 通过生成应用 JSON 的完整实验，说明输入接口、派生值和输出接口。整理本地 CLI 变量优先级及敏感值的持久化边界。
- [[KnowledgeBase/sources/iac-terraform-expressions-summary|Terraform 表达式、函数与模板 来源摘要]] — 用服务集合、YAML 生成和文本模板实验介绍条件与 for 表达式。解释常用函数、dynamic、静态文件读取和不稳定值的使用陷阱。
- [[KnowledgeBase/sources/iac-terraform-providers-summary|Terraform Provider、版本与认证 来源摘要]] — 区分 Core、Provider、来源声明和具体连接配置。保留 Azure 中国区场景，提供使用自身订阅的完整资源组实验，并解释 alias 和版本锁定。
- [[KnowledgeBase/sources/iac-terraform-resources-dependencies-summary|Terraform Resource、Data Source 与依赖 来源摘要]] — 通过查询外部文件、生成受管理副本和 terraform_data 生命周期实验说明所有权、依赖图与变更方式。补充生命周期、条件检查和 provisioner 的边界。
- [[KnowledgeBase/sources/iac-terraform-count-for-each-summary|Terraform count 与 for_each 来源摘要]] — 用两种批量本地文件实验解释索引和稳定 key 的区别。涵盖集合过滤、0/1 创建、链式 for_each 和地址迁移。
- [[KnowledgeBase/sources/iac-terraform-state-summary|Terraform State、漂移与状态操作 来源摘要]] — 解释状态身份、三方比较和本地文件漂移，区分普通与 refresh-only 计划。整理状态命令、退出管理、敏感数据与恢复思路。
- [[KnowledgeBase/sources/iac-terraform-backends-workspaces-summary|Terraform Backend、Workspace 与多环境 来源摘要]] — 介绍状态存储、权限与锁定，并给出 Azure Blob 连接、本地迁移和 S3 锁文件示例。通过内置资源实验区分 Workspace 状态隔离与环境权限隔离。
- [[KnowledgeBase/sources/iac-terraform-modules-summary|Terraform Module 开发与复用 来源摘要]] — 实现为多个服务生成配置的完整本地模块，明确父子模块接口和 Provider 传递。比较本地、Registry 和 Git 来源及模块版本、State 和执行边界。
- [[KnowledgeBase/sources/iac-terraform-import-refactoring-summary|Terraform Import、moved 与 removed 来源摘要]] — 以 Azure 资源组纳管和本地文件改名说明管理身份的建立与迁移。比较声明式导入、生成配置、退出管理和跨 State 移交。
- [[KnowledgeBase/sources/iac-terraform-workflow-troubleshooting-summary|Terraform 工作流、Plan 阅读与排错 来源摘要]] — 整理从写配置、审查计划到执行后验收的流程。解释计划动作、保存计划、选项、常见故障分层和部分失败恢复。
- [[KnowledgeBase/sources/iac-terraform-testing-cicd-summary|Terraform 测试与 CI/CD 协作 来源摘要]] — 区分格式、配置、逻辑、集成和真实部署验证，并给 app-config 模块增加 mock 计划测试。提供模块 CI 示例与正式计划审批执行的最小逻辑。
- [[KnowledgeBase/sources/iac-terraform-container-summary|Terraform Docker、Kubernetes、Helm 与 Nomad 来源摘要]] — 通过 Docker 容器、已有集群 Deployment、最小本地 Helm Chart 和 Nomad Job，说明 Terraform 在各容器层的连接与所有权。修正旧镜像属性、版本语法和不完整资源示例。
- [[KnowledgeBase/sources/iac-terraform-docs-summary|Terraform terraform-docs 模块文档生成 来源摘要]] — 介绍模块接口文档提取、README 注入和自定义 Go template。保留可复用配置与调用模板，并说明工具版本、递归生成、真实输出和 CI 一致性边界。

## 实验与验证边界

- 优先用 Local Provider、terraform_data 和 mock 理解配置逻辑，再进入云账号或集群实验。
- State/Plan 可能有敏感信息，变量文件、Workspace、Backend 和执行身份分别设计。
- 文章经 HCL 格式/语法、YAML 和链接检查，最小 Helm Chart 可离线渲染；真实平台执行与业务验收仍需相应环境。
