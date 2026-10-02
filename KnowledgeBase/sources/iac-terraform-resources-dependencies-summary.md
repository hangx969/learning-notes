---
title: "Terraform Resource、Data Source 与依赖 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/terraform-resources-dependencies]]"
aliases:
  - "TerraformResource、Data Source 与依赖摘要"
---

# Terraform Resource、Data Source 与依赖 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/terraform-resources-dependencies]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

通过查询外部文件、生成受管理副本和 terraform_data 生命周期实验说明所有权、依赖图与变更方式。补充生命周期、条件检查和 provisioner 的边界。

## 关键知识点

1. resource 管理生命周期，data 查询结果不自动取得对象管理权。
2. 直接引用建立隐式依赖，depends_on 用于隐藏行为依赖，不保证云端传播立即完成。
3. prevent_destroy 不能在删掉整个配置块后继续保护对象；provisioner 也不能提供整体事务回滚。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
