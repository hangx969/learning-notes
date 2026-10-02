---
title: "Terraform状态管理"
tags:
  - knowledgebase/concept
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/terraform-state]]"
  - "[[IaC/terraform/terraform-backends-workspaces]]"
  - "[[IaC/terraform/terraform-import-refactoring]]"
  - "[[IaC/terraform/terraform-count-for-each]]"
aliases:
  - "Terraform状态概念"
---

# Terraform状态管理

## 定义

Terraform 状态管理维护配置地址与实际对象之间的绑定，以及运行所需的已知属性和元数据。状态用于变更计算与身份跟踪，不等于完整基础设施或业务数据备份。

## 核心要点

- 地址由资源逻辑名、模块路径和实例 key 等组成，改地址时需考虑 moved。
- refresh-only 同步记录但不改变配置目标；退出管理与删除对象是不同操作。
- 远程 State 的存储、权限、恢复和锁定独立于资源 Provider 认证。

## 与其他概念的关系

- [[KnowledgeBase/concepts/基础设施即代码|基础设施即代码]]：声明需借助状态找到已有对象。
- [[KnowledgeBase/concepts/Terraform模块化|Terraform 模块化]]：模块调用改变地址层级，不自动隔离 State。
- [[KnowledgeBase/entities/Terraform|Terraform]]：通过 Backend 和状态命令维护这些记录。

## 在本仓库中的覆盖

- [[IaC/terraform/terraform-state|State、漂移与状态操作]]：覆盖该概念的定义、配置或维护步骤。
- [[IaC/terraform/terraform-backends-workspaces|Backend、Workspace 与多环境]]：覆盖该概念的定义、配置或维护步骤。
- [[IaC/terraform/terraform-import-refactoring|Import、moved 与 removed]]：覆盖该概念的定义、配置或维护步骤。
- [[IaC/terraform/terraform-count-for-each|count 与 for_each]]：覆盖该概念的定义、配置或维护步骤。

## 知识空白

- 真实故障中的状态恢复与跨 Backend 移交演练。
- 多团队权限和状态拆分的完整落地案例。
