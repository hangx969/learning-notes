---
title: "Terraform 变量、locals 与 outputs 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/terraform-variables-outputs]]"
aliases:
  - "Terraform变量、locals 与 outputs摘要"
---

# Terraform 变量、locals 与 outputs 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/terraform-variables-outputs]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

通过生成应用 JSON 的完整实验，说明输入接口、派生值和输出接口。整理本地 CLI 变量优先级及敏感值的持久化边界。

## 关键知识点

1. variables.tf 声明变量，tfvars 提供值，子模块输入由父模块显式传递。
2. 本地 CLI 依次处理默认值、环境变量、自动变量文件和按顺序提供的命令行赋值。
3. sensitive 隐藏默认汇总显示，不保证值不进入 State/Plan；按名字读取 output 或使用 -raw/-json 仍可得到明文。换 tfvars 也不自动换状态。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- nullable=false 且提供非 null 默认值时，显式 null 会回退到默认值；该设置只约束整体值，不自动禁止对象内部字段为 null。
- 自动文件按完整文件名排序；后赋值覆盖整个变量，不会自动合并两个 map。
- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
