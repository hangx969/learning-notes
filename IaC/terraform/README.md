---
title: Terraform 基础系列学习路线
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform学习路线
  - Terraform基础系列
---

# Terraform 基础系列学习路线

这套笔记从“把一个本地文件交给 Terraform 管理”开始，逐步学习声明式配置、资源身份、状态管理和模块复用。先理解 Terraform 为什么这样工作，再把同一套思路迁移到 Azure、Docker、Kubernetes 等平台。

每篇围绕一个主题展开：说明解决的问题，给出配置和操作步骤，解释关键字段，再通过变更实验观察行为。阅读时可以在一个独立实验目录中动手，不必一开始就准备云账号。

## 学习顺序

### 第一阶段：能写出并读懂一个项目

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 01 | [[IaC/terraform/terraform-basics\|基础概念与第一个项目]] | 解释配置、State、真实资源的关系，完成创建、修改、删除流程 |
| 02 | [[IaC/terraform/terraform-hcl\|HCL 语法与配置文件]] | 读懂 block、argument、类型和引用，正确拆分 `.tf` 文件 |
| 03 | [[IaC/terraform/terraform-variables-outputs\|变量、locals 与 outputs]] | 参数化配置，区分声明与赋值，理解输入优先级和敏感值 |
| 04 | [[IaC/terraform/terraform-expressions\|表达式、函数与模板]] | 用条件、for 表达式、函数和模板生成配置 |
| 05 | [[IaC/terraform/terraform-providers\|Provider、版本与认证]] | 区分版本约束和锁文件，配置认证、别名与 Azure 中国区实验 |

### 第二阶段：理解资源如何变更

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 06 | [[IaC/terraform/terraform-resources-dependencies\|Resource、Data Source 与依赖]] | 区分资源所有权和查询，解释依赖图、生命周期与 provisioner 的边界 |
| 07 | [[IaC/terraform/terraform-count-for-each\|count 与 for_each]] | 批量管理资源，识别索引变化和 key 变化造成的重建 |
| 08 | [[IaC/terraform/terraform-state\|State、漂移与状态操作]] | 观察漂移，区分修改配置、刷新状态、移除管理和删除资源 |
| 09 | [[IaC/terraform/terraform-backends-workspaces\|Backend、Workspace 与多环境]] | 迁移远程状态，解释状态锁，设计 dev/prod 的隔离方式 |

### 第三阶段：组织和维护实际项目

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 10 | [[IaC/terraform/terraform-modules\|Module 开发与复用]] | 编写有清晰输入输出的模块，正确传递 Provider 和固定模块版本 |
| 11 | [[IaC/terraform/terraform-import-refactoring\|Import、moved 与 removed]] | 纳管已有资源，在改名或拆模块时保留资源身份 |
| 12 | [[IaC/terraform/terraform-workflow-troubleshooting\|工作流、Plan 阅读与排错]] | 审查变更计划，理解保存计划、失败恢复和常用诊断命令 |
| 13 | [[IaC/terraform/terraform-testing-cicd\|测试与 CI/CD 协作]] | 区分检查层级，编写原生测试，处理 Plan 退出码和审批后的执行 |

### 第四阶段：扩展实战

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 14 | [[IaC/terraform/terraform-container-management\|Docker、Kubernetes、Helm 与 Nomad]] | 将基础知识用于容器资源，明确认证和多工具资源所有权 |
| 15 | [[IaC/terraform/terraform-docs\|terraform-docs 模块文档生成]] | 生成模块接口文档，并保留人工编写的设计说明 |

## 实验环境和版本约定

- **Terraform CLI**：基础例子以 `>= 1.7, < 2.0` 为基线。使用更高版本时，仍需遵守项目和 Provider 的版本约束。
- **操作系统**：命令以 macOS/Linux 的 Bash 或 zsh 为例。PowerShell 的环境变量和引号写法不同，不直接照抄 shell 命令。
- **本地实验**：使用 `hashicorp/local` 2.x、`hashicorp/random` 3.x 或内置的 `terraform_data`；不需要云账号。
- **Docker 实验**：需要可访问的 Docker Engine，例子使用 `kreuzwerker/docker` 3.x。
- **云与集群实验**：需要自己的账号、独立资源范围和必要权限。资源 ID、订阅和 context 均使用读者自己的值。
- **版本例外**：Azure CLI Backend 的显式 use_cli 示例要求 Terraform 1.11+；S3 原生锁文件示例要求 1.10+；`removed` 和测试 mock 要求 1.7+；Helm 示例明确采用 Provider 3.x 的对象语法。

文中的 `~>` 约束用于说明允许的版本范围，实际安装版本由 `.terraform.lock.hcl` 记录。不要把本文示例的版本范围理解为对所有项目的升级建议。

> [!note] 示例验证范围
> 本系列完成了 Markdown、链接和 HCL 格式/语法检查。云 API、Docker、Kubernetes、Helm 和 Nomad 示例需在读者自己的实验环境中执行验证；静态检查通过不代表已部署成功。

## 动手时怎么组织目录

建议把实验代码放在笔记目录之外，避免状态文件、计划文件和生成文件进入知识库。

```text
terraform-labs/
├── 01-local-file/
├── 03-variables/
├── 07-for-each/
├── 10-modules/
├── 14-docker/
└── 14-kubernetes/
```

一个独立实验使用一个目录和一份状态。后文写“替换 main.tf”时，表示在该实验中替换原配置；写“补充”时才是在已有配置里追加。不要把不同文章中的同名 `variable`、`resource` 块全部粘贴到同一个目录。

每次实验都应能回答：

1. 哪个目录是当前 root module？
2. 用的是哪份状态、哪个 Workspace？
3. 将访问哪个账号、区域、Docker daemon 或 Kubernetes context？
4. Plan 中是创建、原地更新，还是替换？原因是什么？
5. 实验结束后怎样清理自己创建的资源？

## 找到的 GitHub 学习资料

以下是本系列参考的公开资料，查询与核对日期为 **2026-10-02**。正文是围绕本仓库学习路线重新编写的中文笔记，技术行为以 Terraform 和 Provider 官方文档为准。

| 资料 | 内容与适合的用途 | 阅读时注意 |
|---|---|---|
| [iam-veeramalla/terraform-zero-to-hero](https://github.com/iam-veeramalla/terraform-zero-to-hero) | 从 IaC、工作流到变量、模块、状态、多环境的分阶段课程；适合参考实验顺序 | AWS 场景较多，旧 S3/DynamoDB 锁定写法需对照当前文档 |
| [ari-hacks/terraform-study-guide](https://github.com/ari-hacks/terraform-study-guide) | 按基础概念、CLI、模块、状态、配置语言组织的学习提纲 | README 标明面向 2020 年认证；用于查漏补缺，不作为当前版本规范 |
| [antonbabenko/terraform-best-practices](https://github.com/antonbabenko/terraform-best-practices) | 目录结构、命名、模块边界与协作经验；提供简体中文译本入口 | 社区实践包含取舍，不能把某一种目录结构当成 Terraform 强制要求 |
| [hashicorp-education/learn-terraform-locals](https://github.com/hashicorp-education/learn-terraform-locals) | 官方教程配套代码，展示 locals 如何减少重复 | 读配套教程并核对 Provider 版本；不要仅复制片段 |
| [hashicorp-education/learn-terraform-troubleshooting](https://github.com/hashicorp-education/learn-terraform-troubleshooting) | 官方排错练习，按语言、状态、Core、Provider 区分问题 | 练习包含故意制造的错误；云实验可能创建收费资源 |

英文课程帮助确定“先学什么”，社区最佳实践帮助讨论“项目怎么组织”，官方文档负责确认“这个字段和命令到底怎么工作”。

## 官方资料怎么查

- [Terraform 文档](https://developer.hashicorp.com/terraform/docs)：CLI、语言、状态和工作流。
- [Terraform 语言参考](https://developer.hashicorp.com/terraform/language)：遇到 `for_each`、`lifecycle`、`module` 等语法时先查这里。
- [Terraform CLI 参考](https://developer.hashicorp.com/terraform/cli)：查询命令选项、退出码、状态操作。
- [Terraform Registry](https://registry.terraform.io/)：查询具体 Provider 的 resource/data source 参数，以及模块输入输出。
- [官方入门教程](https://developer.hashicorp.com/terraform/tutorials)：需要按步骤完成实验时使用。

查看 Registry 时先选择项目使用的 Provider 版本。Terraform CLI 文档解释通用语法，Provider 文档解释具体 API 的参数、导入 ID 和替换规则，两者不能互相代替。

## 一组贯穿全系列的判断题

读完后应能说明理由，而不只是背命令：

- 改了 `.tf` 文件名，资源会重建吗？改 resource 的第二个 label 呢？
- `sensitive = true` 能阻止密码进入状态吗？
- `data` 查询到一个资源，就意味着 Terraform 会删除它吗？
- 换一个 `-var-file`，就有一份新的 State 吗？
- 只把本地状态上传到对象存储，就有可靠的并发锁了吗？
- `terraform plan` 通过，是否代表 apply 一定成功？
- `terraform state rm` 与 `terraform destroy` 有什么区别？
- 为什么删掉 count 列表中间一项，可能影响后面的实例？
- 为什么把资源移动到模块里，要先处理地址迁移？
- 一个 Helm Release 和它创建的 Deployment，应该由几个工具负责期望状态？

下一篇：[[IaC/terraform/terraform-basics|Terraform 基础概念与第一个项目]]。

知识层导航：[[KnowledgeBase/maps/terraform-map|Terraform 主题地图]] · [[KnowledgeBase/entities/Terraform|Terraform 实体页]]。
