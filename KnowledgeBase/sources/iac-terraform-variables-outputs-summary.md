---
title: "Terraform 变量、locals 与 outputs 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
  - alicloud
date: 2026-10-02
sources:
  - "[[IaC/terraform/03_terraform_变量与输出]]"
aliases:
  - "Terraform变量、locals 与 outputs摘要"
---

# Terraform 变量、locals 与 outputs 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/03_terraform_变量与输出]]
- **领域**：IaC / Terraform / 阿里云
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

以生产 CMS 告警模块的 map(object) 输入和 optional 字段为依据，完整构建一个不连接云端的告警数据实验。说明 variable、locals 和 output 的职责、对象输入校验、CLI 赋值优先级、敏感值及 State 的边界。

## 关键知识点

1. `variables.tf` 声明接口，变量文件或运行环境提供值，locals 派生数据，子模块输入由父模块显式传递。
2. 本地 CLI 变量赋值按默认值、环境变量、自动变量文件和命令行参数等顺序覆盖；相同 map 变量整体替换，不会自动合并。
3. `nullable` 与默认值共同决定省略值和显式 null 的结果；object optional 有字段默认值语义，跨变量 validation 从 Terraform 1.9 起可用。
4. 敏感 input 的输出必须显式声明 `sensitive = true`；常规输出会遮盖值，但具名 output、`-raw`、`-json` 仍可能显示明文，State/Plan 也可能保存该值。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 生产依据：`monitoring/modules/cloud-monitor-alerts/variables.tf` 和 `monitoring/modules/cloud-monitor-alerts/main.tf`；示例为脱敏裁剪和离线改编。
- 认证环境变量与 `TF_VAR_*` 输入变量属于不同接口；阿里云认证的版本边界见第五篇及官方 Provider 文档。
- 练习结果为预期观察，本次仅做静态核对，未初始化项目或执行 plan/apply/test。
