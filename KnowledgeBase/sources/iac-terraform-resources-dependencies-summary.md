---
title: "Terraform Resource、Data Source 与依赖 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/06_terraform_资源数据源与依赖]]"
aliases:
  - "TerraformResource、Data Source 与依赖摘要"
---

# Terraform Resource、Data Source 与依赖 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/06_terraform_资源数据源与依赖]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

以 AliCloud 当前账号 Data Source、生产网络告警的 EIP/NAT 查询过滤链，以及 CMS 联系人、联系人组和告警资源说明查询、管理和依赖的边界。用内置逻辑资源介绍 Terraform lifecycle、条件与 provisioner。

## 关键知识点

1. `data.alicloud_account.current` 读取当前账号，不管理或创建账号；resource 地址与实际对象 ID 由 State 绑定。
2. 生产告警代码由 root Data Source 查询、标签过滤、本地值转换和模块参数传递组成；这条数据链本身不管理 EIP/NAT 对象。
3. CMS 联系人、联系人组、CMS 1.0 告警是独立 map 输入。`depends_on` 表达顺序，不同步联系人组成员与告警组名；CMS 2.0 规则输入独立。
4. dynamic block 生成告警资源内部的嵌套阈值块，不产生独立资源地址。Lifecycle 规则不提供整体回滚。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/Terraform状态管理|Terraform 状态管理]]

## 值得注意

- 生产代码来源为 `tool/data.tf`、`monitoring/cloud-monitor-alert.tf`、`monitoring/modules/cloud-monitor-alerts/main.tf` 与 `variables.tf` 的脱敏裁剪/教学改编；没有保留联系人或真实业务 key。
- AliCloud 数据源和 CMS resource 文档链接固定到 Provider 1.266.0；未执行云端读取或修改。
- 学习顺序见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
