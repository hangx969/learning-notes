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

用两种批量本地文件实验解释索引和稳定 key 的区别。涵盖集合过滤、0/1 创建、链式 for_each 和地址迁移。

## 关键知识点

1. count 按索引分配实例身份，中间增删或重排可能影响后续实例。
2. for_each 使用 map/set(string)，key 要在 plan 时已知且不能是敏感值。
3. moved 迁移同一 State 内的地址，但不能取消真实参数变化要求的替换；for 表达式和 dynamic 不等于创建独立资源实例。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
