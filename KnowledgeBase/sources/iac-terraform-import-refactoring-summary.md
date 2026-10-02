---
title: "Terraform Import、moved 与 removed 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/terraform-import-refactoring]]"
aliases:
  - "TerraformImport、moved 与 removed摘要"
---

# Terraform Import、moved 与 removed 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/terraform-import-refactoring]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

以 Azure 资源组纳管和本地文件改名说明管理身份的建立与迁移。比较声明式导入、生成配置、退出管理和跨 State 移交。

## 关键知识点

1. import 建立实际 ID 与配置地址绑定，但同一计划仍可能包含其他资源变更。
2. moved 保留地址绑定，不取消参数变化本身要求的替换。
3. removed 的 destroy=false 用于保留对象并退出管理，跨 State 移交还需停止并发和分别核对计划。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
