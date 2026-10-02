---
title: "Terraform 测试与 CI/CD 协作 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/13_terraform_测试与持续集成交付]]"
aliases:
  - "Terraform测试与 CI/CD 协作摘要"
---

# Terraform 测试与 CI/CD 协作 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/13_terraform_测试与持续集成交付]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02

## 摘要

使用生产 CMS 联系人模块的教学裁剪版，演示 Terraform 原生测试的 mock plan 断言和 CI 检查骨架。明确区分代码检查、模拟测试、授权云端执行和执行后验收，并指出生产仓库当前没有查到原生 CI 配置。

## 关键知识点

1. 测试验证 `contacts`、`contact_groups` 的输入如何形成预期资源属性；Mock Provider 不调用 CMS API，也不证明真实联系人、权限或通知行为。
2. `terraform test` 的 run 默认可能 apply；示例指定 `command = plan` 并使用 `mock_provider "alicloud" {}`。AliCloud 1.266.0 源码中联系人组 `contacts` 是 TypeSet，断言以 `toset` 统一类型；本轮未运行测试命令。
3. CI 示例属于为该模块新增的教学设计，不是生产仓库已有流水线；独立测试副本先固定 `= 1.266.0` 约束，再审阅并提交自己的 `.terraform.lock.hcl` 锁定解析版本，CI 以 `-lockfile=readonly` 使用它；真实 Plan 和 Apply 需要独立 workspace、身份核验和审批。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]
- [[KnowledgeBase/concepts/Terraform模块化]]

## 值得注意

- AliCloud 邮箱联系人需要收件人激活；离线测试不验证邮箱和告警投递。
- 测试目录、Provider 锁文件和运行版本需在具体教学项目中准备；此处 CI action 和版本流程均未运行验证。
