---
title: "Terraform 基础概念与第一个项目 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/01_terraform_基础概念与第一个项目]]"
aliases:
  - "Terraform基础概念与第一个项目摘要"
---

# Terraform 基础概念与第一个项目 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/01_terraform_基础概念与第一个项目]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02
- **更新日期**：2026-10-02

## 摘要

从 IaC 的用途开始，用本地文件实验解释配置、State 和实际资源的关系。涵盖创建、修改、重复计划与清理的完整步骤。

## 关键知识点

1. 核心工作流为 Write → Plan → Apply，init 负责准备 Backend、模块和 Provider。
2. 同一目录的配置组成根模块，State 负责资源身份映射，不是资源数据备份。
3. 本地文件例子提供计划审查、执行和清理步骤；示例输出注明为预期观察。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- 技术出处在原始笔记中按官方文档和 Provider 文档列出；实验输出标为预期观察，云端执行未验证。
- 学习顺序与相关章节见 [[KnowledgeBase/maps/terraform-map|Terraform 主题地图]]。
