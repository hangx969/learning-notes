---
title: "Terraform State、漂移与状态操作 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/terraform-state]]"
aliases:
  - "TerraformState、漂移与状态操作摘要"
---

# Terraform State、漂移与状态操作 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/terraform-state]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

解释状态身份、三方比较和本地文件漂移，区分普通与 refresh-only 计划。整理状态命令、退出管理、敏感数据与恢复思路。

## 关键知识点

1. State 是管理记录，不包含数据库业务数据或完整基础设施备份。
2. refresh-only 更新记录与根输出，不修改 .tf 目标，也不替代普通资源变更。
3. state rm 忘记绑定，destroy 删除对象；两份 State 不应同时管理同一实际对象。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
