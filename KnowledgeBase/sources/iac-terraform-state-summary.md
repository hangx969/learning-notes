---
title: "Terraform State、漂移与状态操作 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/08_terraform_状态漂移与状态操作]]"
aliases:
  - "TerraformState、漂移与状态操作摘要"
---

# Terraform State、漂移与状态操作 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/08_terraform_状态漂移与状态操作]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

以第 05 篇自有的空 OSS Bucket 和 ACL 观察普通计划、外部标签变化、外部删除及 refresh-only。补充 Terraform 状态命令、状态备份、停止管理和恢复的边界。

## 关键知识点

1. State 保存 Terraform 地址与实际 ID 的绑定，不是云对象、业务数据或 Bucket 内容的备份。
2. 普通计划在外部标签变化后按配置提出恢复；外部删除后提出创建。Refresh-only 只更新状态记录，之后普通计划仍可能提出恢复资源。
3. `state rm` 忘记绑定而不删除对象；destroy 会请求 Provider 删除受管对象。一个云对象应由唯一 State 管理。
4. OSS Bucket 与 ACL 是独立资源；生产 Bucket 设置 `force_destroy = false`，ACL 解绑后其 OSS ACL 设置可能留存。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform 状态管理]]

## 值得注意

- 生产依据为 `shared/jfrog-cn.tf`（脱敏裁剪/教学改编）；演练目标只限第 05 篇创建的空教学 Bucket，全部计划命令使用 `lab.tfvars`。
- Bucket 与 ACL 资源事实引用 AliCloud Provider 1.266.0 文档；未访问 OSS 或执行状态变更。
- 学习顺序见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
