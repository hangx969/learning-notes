---
title: "Terraform terraform-docs 模块文档生成 来源摘要"
tags:
  - knowledgebase/source
  - IaC/terraform
date: 2026-10-02
sources:
  - "[[IaC/terraform/15_terraform_模块文档生成]]"
aliases:
  - "Terraform terraform-docs 模块文档生成摘要"
---

# Terraform terraform-docs 模块文档生成 来源摘要

## 元信息

- **原始文档**：[[IaC/terraform/15_terraform_模块文档生成]]
- **领域**：IaC / Terraform
- **摄入日期**：2026-10-02

## 摘要

以第 10 篇的 `modules/cms-contacts/` 教学模块为唯一接口来源，说明 README 注入标记、`terraform-docs` 配置、完整调用示例和文档一致性检查。输出表只描述模块接口，不读取真实 State output 或联系资料。

## 关键知识点

1. 文档目标为模块目录；固定工具版本与配置可减少格式差异，`inject` 只替换 README 标记区域。
2. 自动表格从 `contacts`、`contact_groups`、`contact_names` 和 `group_names` 声明生成；必填输入的业务值仍需维护者提供。
3. `content` 使用 Go template 排列章节，也可 include 模块内的完整调用示例；必填参数骨架需明确标出占位值。
4. terraform-docs 不运行 Terraform 或访问云端，CI diff 检查只能证明生成文档与代码一致，不能证明部署有效。

## 涉及的概念与实体

- [[KnowledgeBase/entities/Terraform|Terraform]]
- [[KnowledgeBase/concepts/Terraform模块化]]
- [[KnowledgeBase/concepts/自动化运维|自动化运维]]

## 值得注意

- terraform-docs 生成命令尚未执行；正文说明接口表的预期内容。
- `sensitive` 展示标记不会扫描或脱敏任意文本，State output 值关闭读取；不要把真实邮箱、账号 ID、凭证或部署结果加入 README。
