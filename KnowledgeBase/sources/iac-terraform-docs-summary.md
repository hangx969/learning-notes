---
title: "Terraform terraform-docs 模块文档生成 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/terraform-docs]]"
aliases:
  - "Terraformterraform-docs 模块文档生成摘要"
---

# Terraform terraform-docs 模块文档生成 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/terraform-docs]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

介绍模块接口文档提取、README 注入和自定义 Go template。保留可复用配置与调用模板，并说明工具版本、递归生成、真实输出和 CI 一致性边界。

## 关键知识点

1. 目标是模块目录，工具读取配置接口，不代表模块或云部署已经验证。
2. inject 只更新一致标记中的区域，replace 替换整个文件；人工设计说明应保留。
3. 默认文档不读取真实 State output，sensitive 标记展示不是任意内容脱敏。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
