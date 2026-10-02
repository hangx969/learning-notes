---
title: "Terraform count 与 for_each 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/07_terraform_循环与批量资源]]"
aliases:
  - "Terraformcount 与 for_each摘要"
---

# Terraform count 与 for_each 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/07_terraform_循环与批量资源]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

用 `terraform_data` 承载 CMS 告警形状的本地练习，比较 `count` 索引与 `for_each` 稳定 key；生产 CMS 配置片段解释真实告警 map、dynamic block 和可选 OSS Bucket 的 count 条件。

## 关键知识点

1. `count` 地址由列表索引决定，中间增删或重排可能令后续地址代表不同对象。
2. `for_each` 用 map key 或字符串集合成员作为地址身份；key 应预先已知且不能泄露敏感信息。
3. Resource/module 上的 `for_each` 产生独立实例；dynamic block 只生成 Provider resource 内部的嵌套配置。
4. `moved` 可迁移 State 地址，但不会免除实际属性变化带来的更新或替换。
5. 生产 `shared/jfrog-cn.tf` 用 `count` 实现可选 OSS Bucket 的零/一实例模式。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform 状态管理]]

## 值得注意

- CMS 配置基于 `monitoring/modules/cloud-monitor-alerts/main.tf` 与 `variables.tf` 脱敏裁剪/教学改编；本地逻辑 resource 只是练习 wrapper，不会创建 CMS 资源。
- 实验命令只操作各自本地 State；未调用云端。
- 学习顺序见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
