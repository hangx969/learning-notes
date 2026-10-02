---
title: "Terraform 基础学习地图"
tags:
  - knowledgebase/map
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
  - "Terraform主题地图"
  - "Terraform知识地图"
---

# Terraform 基础学习地图

## 阅读入口

[[IaC/terraform/README|Terraform 基础系列学习路线]] 包含 15 篇正文、实验约定和 GitHub 资料筛选说明，以 `alicloud-operations` 的生产结构为依据，按从离线输入检查到阿里云与 ACK 实验的顺序组织。

## 概念与工具

- [[KnowledgeBase/concepts/基础设施即代码|基础设施即代码]]：把基础设施配置变成可审查、可复用的声明。
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform 状态管理]]：资源身份、漂移和管理记录。
- [[KnowledgeBase/concepts/Terraform模块化|Terraform 模块化]]：输入输出、复用与执行边界。
- [[KnowledgeBase/entities/Terraform|Terraform]]：工具能力、仓库覆盖和后续空白。

## 按学习顺序阅读

1. [[IaC/terraform/01_terraform_基础概念与第一个项目|基础概念与第一个项目]] — 用临时策略的离线校验实验理解配置、State 和资源，再观察创建、变更与清理。
2. [[IaC/terraform/02_terraform_配置语法与文件结构|配置语法与文件结构]] — 借 CMS 输入读懂 HCL 块、类型和引用，区分文件组织与资源执行顺序。
3. [[IaC/terraform/03_terraform_变量与输出|变量与输出]] — 用 CMS 风格 map 输入解释变量赋值、nullable/optional、输出与敏感值边界。
4. [[IaC/terraform/04_terraform_表达式函数与模板|表达式函数与模板]] — 通过告警筛选、标签合并和 OSS 策略模板学习 for、函数、JSON 编码与 dynamic。
5. [[IaC/terraform/05_terraform_提供者版本与认证|提供者版本与认证]] — 核对 AliCloud 版本、STS/AssumeRole 和 alias，用空 OSS Bucket 练习 ACL、标签更新与清理。
6. [[IaC/terraform/06_terraform_资源数据源与依赖|资源数据源与依赖]] — 从账号查询、EIP 过滤和 CMS 依赖链区分 Data Source、资源所有权与生命周期。
7. [[IaC/terraform/07_terraform_循环与批量资源|循环与批量资源]] — 用 CMS 告警对象比较 count 索引与 for_each key，并解释 dynamic 和地址迁移。
8. [[IaC/terraform/08_terraform_状态漂移与状态操作|状态漂移与状态操作]] — 观察 OSS 标签漂移和外部删除，区分普通计划、refresh-only 与退出管理。
9. [[IaC/terraform/09_terraform_后端工作空间与多环境|后端工作空间与多环境]] — 说明生产 TFE remote Backend、OSS Backend 的区别，以及状态迁移和多环境权限边界。
10. [[IaC/terraform/10_terraform_模块开发与复用|模块开发与复用]] — 从生产 CMS 联系人与组裁剪模块，贯穿输入、输出、Provider 映射和状态边界。
11. [[IaC/terraform/11_terraform_资源导入与重构|资源导入与重构]] — 以 OSS Bucket/ACL 导入和 CMS 地址重构说明 import、moved、removed 与跨 State 移交。
12. [[IaC/terraform/12_terraform_工作流计划阅读与排错|工作流计划阅读与排错]] — 用 CMS 项目阅读计划、诊断部分失败，并区分本地保存计划与 TFE Workspace Run。
13. [[IaC/terraform/13_terraform_测试与持续集成交付|测试与持续集成交付]] — 为 CMS 教学模块补充 mock 计划测试、固定版本的 CI 和计划退出码、审批执行流程。
14. [[IaC/terraform/14_terraform_容器管理实战|ACK、Kubernetes 与 Helm]] — 沿 ACK 凭据连接链管理实验 Namespace 与 Helm Release，用 Chart 校验和触发更新。
15. [[IaC/terraform/15_terraform_模块文档生成|模块文档生成]] — 为 CMS 模块生成接口文档，保留人工说明，并提供注入、Go template 与 CI 检查配置。

## 来源摘要

- [[KnowledgeBase/sources/iac-terraform-basics-summary|Terraform 基础概念与第一个项目 来源摘要]] — 用临时策略的离线校验实验理解配置、State 和资源，再观察创建、变更与清理。
- [[KnowledgeBase/sources/iac-terraform-hcl-summary|Terraform HCL 语法与配置文件 来源摘要]] — 借 CMS 输入读懂 HCL 块、类型和引用，区分文件组织与资源执行顺序。
- [[KnowledgeBase/sources/iac-terraform-variables-outputs-summary|Terraform 变量、locals 与 outputs 来源摘要]] — 用 CMS 风格 map 输入解释变量赋值、nullable/optional、输出与敏感值边界。
- [[KnowledgeBase/sources/iac-terraform-expressions-summary|Terraform 表达式、函数与模板 来源摘要]] — 通过告警筛选、标签合并和 OSS 策略模板学习 for、函数、JSON 编码与 dynamic。
- [[KnowledgeBase/sources/iac-terraform-providers-summary|Terraform Provider、版本与认证 来源摘要]] — 核对 AliCloud 版本、STS/AssumeRole 和 alias，用空 OSS Bucket 练习 ACL、标签更新与清理。
- [[KnowledgeBase/sources/iac-terraform-resources-dependencies-summary|Terraform Resource、Data Source 与依赖 来源摘要]] — 从账号查询、EIP 过滤和 CMS 依赖链区分 Data Source、资源所有权与生命周期。
- [[KnowledgeBase/sources/iac-terraform-count-for-each-summary|Terraform count 与 for_each 来源摘要]] — 用 CMS 告警对象比较 count 索引与 for_each key，并解释 dynamic 和地址迁移。
- [[KnowledgeBase/sources/iac-terraform-state-summary|Terraform State、漂移与状态操作 来源摘要]] — 观察 OSS 标签漂移和外部删除，区分普通计划、refresh-only 与退出管理。
- [[KnowledgeBase/sources/iac-terraform-backends-workspaces-summary|Terraform Backend、Workspace 与多环境 来源摘要]] — 说明生产 TFE remote Backend、OSS Backend 的区别，以及状态迁移和多环境权限边界。
- [[KnowledgeBase/sources/iac-terraform-modules-summary|Terraform Module 开发与复用 来源摘要]] — 从生产 CMS 联系人与组裁剪模块，贯穿输入、输出、Provider 映射和状态边界。
- [[KnowledgeBase/sources/iac-terraform-import-refactoring-summary|Terraform Import、moved 与 removed 来源摘要]] — 以 OSS Bucket/ACL 导入和 CMS 地址重构说明 import、moved、removed 与跨 State 移交。
- [[KnowledgeBase/sources/iac-terraform-workflow-troubleshooting-summary|Terraform 工作流、Plan 阅读与排错 来源摘要]] — 用 CMS 项目阅读计划、诊断部分失败，并区分本地保存计划与 TFE Workspace Run。
- [[KnowledgeBase/sources/iac-terraform-testing-cicd-summary|Terraform 测试与 CI/CD 协作 来源摘要]] — 为 CMS 教学模块补充 mock 计划测试、固定版本的 CI 和计划退出码、审批执行流程。
- [[KnowledgeBase/sources/iac-terraform-container-summary|Terraform ACK、Kubernetes 与 Helm 来源摘要]] — 沿 ACK 凭据连接链管理实验 Namespace 与 Helm Release，用 Chart 校验和触发更新。
- [[KnowledgeBase/sources/iac-terraform-docs-summary|Terraform terraform-docs 模块文档生成 来源摘要]] — 为 CMS 模块生成接口文档，保留人工说明，并提供注入、Go template 与 CI 检查配置。

## 实验与验证边界

- 优先用 `terraform_data` 和 mock 理解生产配置中的输入与依赖，再进入自己的阿里云账号、TFE Workspace 或 ACK 集群。
- 账号、Role ARN、资源 ID、域名、联系人和凭据使用占位符；State/Plan 和 ACK 客户端私钥仍可能保存敏感值。
- 本轮只核对源码依据、配置语法、链接与示例一致性；实际云部署、远程执行和业务验收需在相应实验环境完成。
