---
title: "Terraform Import、moved 与 removed 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/11_terraform_资源导入与重构]]"
aliases:
  - "TerraformImport、moved 与 removed摘要"
---

# Terraform Import、moved 与 removed 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/11_terraform_资源导入与重构]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

以阿里云 OSS 空教学 Bucket 讲解导入 ID、声明式导入计划、地址迁移、退出管理和跨 State 移交。生产 CMS 重构作为 moved 与 removed 的关系案例。

## 关键知识点

1. import 建立实际对象 ID 与 resource 地址绑定；后续计划仍可能更新或替换属性。
2. `moved` 迁移同一 State 的绑定；resource 参数变化仍按 Provider 规则处理。
3. `removed` 加 `destroy = false` 声明退出管理并保留对象；CLI import 直接改状态，不能与同一地址的声明式流程重复执行。
4. 跨 State 移交需停写、备份与协调新旧双方计划，Terraform 锁不会发现两份状态管理同一云对象。
5. OSS Bucket 与 OSS ACL 的 Provider 1.266.0 实现均以 Bucket 名作为状态 ID；两份配置都需导入，避免计划新设 ACL。ACL 解绑不一定撤销 OSS ACL 设置。停止管理时需同时移除 Bucket 与 ACL resource，避免悬空引用。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform 状态管理]]

## 值得注意

- 教学资源基于 `shared/jfrog-cn.tf` 中 OSS Bucket / ACL 配置和 `monitoring/moved.tf`、`monitoring/import.tf` 的脱敏裁剪与改编；不含生产 ID、名称或地址。
- Bucket destroy 示例限定于自己创建且为空的教学对象；生产对象不作为清理目标。
- 导入格式和资源行为依阿里云 Provider 1.266.0 文档和实现核对，未连接云端。
