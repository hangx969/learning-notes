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

这套笔记以 `alicloud-operations` 的实际配置为依据，从临时权限策略的离线检查开始，逐步学习声明式配置、资源身份、状态管理和模块复用，再进入 OSS、CMS 和 ACK 的实验。

每篇围绕一个主题展开：说明解决的问题，给出配置和操作步骤，解释关键字段，再通过变更实验观察行为。阅读时可以在一个独立实验目录中动手，不必一开始就准备云账号。

## 示例来源与脱敏约定

生产参考仓库为 `/Users/hang.xu/github-repo-ds/CloudOps-AliCloud/alicloud-operations`，本轮只读查看。下面的文件路径都相对于这个仓库，核对日期为 2026-10-02。每篇正文列出对应路径，并说明保留了哪些配置关系。

| 教学内容 | 生产依据 | 示例如何改编 |
|---|---|---|
| 输入校验、表达式和内置资源 | `permissions/temporary-access.tf`、`shared/ecs.tf` | 保留对象输入、派生值和条件检查，先用 `terraform_data` 在本地观察配置与 State |
| Provider、OSS 和资源依赖 | `shared/providers.tf`、`shared/versions.tf`、`shared/jfrog-cn.tf` | 保留多账号连接及 Bucket → private ACL 的引用关系，改成独立空桶实验 |
| 批量资源与模块接口 | `monitoring/cloud-monitor-alert.tf`、`monitoring/modules/cloud-monitor-alerts/` | 裁剪 CMS 联系人与联系人组，解释根输入 → 模块参数 → 子变量 → 资源的传值链 |
| 远程状态与重构 | 各目录的 `backend.tf`、`monitoring/moved.tf`、`domains/import.tf` | 使用实验 TFE Workspace 和脱敏资源，说明状态边界与地址迁移 |
| ACK 与 Helm | `tool/data.tf`、`tool/providers.tf`、`tool/helm.tf`、`tool/external-secrets.tf` | 使用已有实验 ACK 集群，保留凭据读取与 Provider 连接链，裁剪 Namespace 和 Release |
| 模块测试、CI 与文档生成 | CMS 模块的输入和资源接口 | 基于裁剪后的模块补充教学测试、流水线与 README；这些新增文件不代表生产仓库已有相同配置 |

账号 ID、RAM Role ARN、ACK/VPC/交换机 ID、内部域名、联系人和凭据均须替换。`<ACCOUNT_ID>`、`<ACK_CLUSTER_ID>`、`<YOUR_LAB_BUCKET>` 等是占位符；`tfe.example.invalid`、`ops@example.invalid` 是保留域名下的示意值。它们只能帮助阅读结构，调用云 API 前必须换成自己实验环境中的合法值。公开 Region 名称和 Provider 字段名保留原样。

文档中的代码是脱敏裁剪或教学改编。私有 Registry 模块、业务策略、生产 Workspace 和真实凭据不会成为实验默认值。State、保存的 Plan、ACK 客户端私钥和敏感输出也需要按凭据处理。

## 学习顺序

### 第一阶段：能写出并读懂一个项目

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 01 | [[IaC/terraform/01_terraform_基础概念与第一个项目\|01_terraform_基础概念与第一个项目]] | 解释配置、State、真实资源的关系，完成创建、修改、删除流程 |
| 02 | [[IaC/terraform/02_terraform_配置语法与文件结构\|02_terraform_配置语法与文件结构]] | 读懂 block、argument、类型和引用，正确拆分 `.tf` 文件 |
| 03 | [[IaC/terraform/03_terraform_变量与输出\|03_terraform_变量与输出]] | 参数化配置，区分声明与赋值，理解输入优先级和敏感值 |
| 04 | [[IaC/terraform/04_terraform_表达式函数与模板\|04_terraform_表达式函数与模板]] | 用条件、for 表达式、函数和模板生成配置 |
| 05 | [[IaC/terraform/05_terraform_提供者版本与认证\|05_terraform_提供者版本与认证]] | 区分版本约束和锁文件，配置阿里云认证、AssumeRole 别名与 OSS 实验 |

### 第二阶段：理解资源如何变更

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 06 | [[IaC/terraform/06_terraform_资源数据源与依赖\|06_terraform_资源数据源与依赖]] | 区分资源所有权和查询，解释依赖图、生命周期与 provisioner 的边界 |
| 07 | [[IaC/terraform/07_terraform_循环与批量资源\|07_terraform_循环与批量资源]] | 批量管理资源，识别索引变化和 key 变化造成的重建 |
| 08 | [[IaC/terraform/08_terraform_状态漂移与状态操作\|08_terraform_状态漂移与状态操作]] | 观察漂移，区分修改配置、刷新状态、移除管理和删除资源 |
| 09 | [[IaC/terraform/09_terraform_后端工作空间与多环境\|09_terraform_后端工作空间与多环境]] | 迁移远程状态，解释状态锁，设计 dev/prod 的隔离方式 |

### 第三阶段：组织和维护实际项目

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 10 | [[IaC/terraform/10_terraform_模块开发与复用\|10_terraform_模块开发与复用]] | 编写有清晰输入输出的模块，正确传递 Provider 和固定模块版本 |
| 11 | [[IaC/terraform/11_terraform_资源导入与重构\|11_terraform_资源导入与重构]] | 纳管已有资源，在改名或拆模块时保留资源身份 |
| 12 | [[IaC/terraform/12_terraform_工作流计划阅读与排错\|12_terraform_工作流计划阅读与排错]] | 审查变更计划，理解保存计划、失败恢复和常用诊断命令 |
| 13 | [[IaC/terraform/13_terraform_测试与持续集成交付\|13_terraform_测试与持续集成交付]] | 区分检查层级，编写原生测试，处理 Plan 退出码和审批后的执行 |

### 第四阶段：扩展实战

| 顺序 | 文章 | 学完应该能做到 |
|---|---|---|
| 14 | [[IaC/terraform/14_terraform_容器管理实战\|14_terraform_容器管理实战]] | 连接已有 ACK 集群，用 Kubernetes/Helm 管理实验资源并明确所有权 |
| 15 | [[IaC/terraform/15_terraform_模块文档生成\|15_terraform_模块文档生成]] | 生成模块接口文档，并保留人工编写的设计说明 |

## 实验环境和版本约定

- **Terraform CLI**：基础例子以 `>= 1.7, < 2.0` 为基线。使用更高版本时，仍需遵守项目和 Provider 的版本约束。
- **操作系统**：命令以 macOS/Linux 的 Bash 或 zsh 为例。PowerShell 的环境变量和引号写法不同，不直接照抄 shell 命令。
- **本地实验**：优先用内置 `terraform_data` 观察来自生产结构的输入、校验和状态，不需要云账号。
- **阿里云实验**：完整云实验的根模块固定 `aliyun/alicloud` **1.266.0**，可复用子模块声明最低兼容版本。这是教学选择；生产各目录约束不同，例如 `shared/versions.tf` 为 `>=1.266.0`，`monitoring/versions.tf` 为 `>=1.258.0`，需要分别结合自己的锁文件判断。
- **ACK 与 Helm**：使用已有、授权的实验集群；连接示例固定 Kubernetes Provider **2.38.0**、Helm Provider **2.17.0**，Helm 的 `kubernetes {}`、`set {}` 沿用 2.x 块语法。
- **版本边界**：`removed` 与 mock 测试要求 Terraform 1.7+；涉及 1.9+ 的变量交叉校验时，正文单独说明版本要求。

文中的 `~>` 约束用于说明允许的版本范围，实际安装版本由 `.terraform.lock.hcl` 记录。不要把本文示例的版本范围理解为对所有项目的升级建议。

> [!note] 示例验证范围
> 本轮完成 Markdown、HCL、Shell、YAML、内部链接与示例一致性检查，ACK 实验 Chart 通过离线 Helm lint/template。未执行 Terraform init/validate/plan/apply/test，也未访问云端、TFE 或集群；云 API、远程执行和实际部署仍需在自己的实验环境验证。

## 动手时怎么组织目录

建议把实验代码放在笔记目录之外，避免状态文件、计划文件和生成文件进入知识库。

```text
terraform-labs/
├── 01-policy-guard/
├── 03-cms-input/
├── 05-oss-bucket/
├── 07-count/
├── 07-for-each/
├── 10-cms-contacts/
├── 13-cms-tests/
└── 14-ack-helm/
```

一个独立实验使用一个目录和一份状态。后文写“替换 main.tf”时，表示在该实验中替换原配置；写“补充”时才是在已有配置里追加。不要把不同文章中的同名 `variable`、`resource` 块全部粘贴到同一个目录。

每次实验都应能回答：

1. 哪个目录是当前 root module？
2. 用的是哪份状态、哪个 Workspace？
3. 将访问哪个阿里云账号、Region、TFE Workspace 或 ACK 集群？
4. Plan 中是创建、原地更新，还是替换？原因是什么？
5. 实验结束后怎样清理自己创建的资源？

## 找到的 GitHub 学习资料

以下公开资料用于参考学习顺序与项目组织，最初查询与核对日期为 **2026-10-02**。本文的资源示例取自上面的生产结构，字段和命令行为再与 Terraform、AliCloud 及 Kubernetes/Helm Provider 文档核对。

| 资料 | 内容与适合的用途 | 阅读时注意 |
|---|---|---|
| [iam-veeramalla/terraform-zero-to-hero](https://github.com/iam-veeramalla/terraform-zero-to-hero) | 从 IaC、工作流到变量、模块、状态、多环境的分阶段课程；适合参考实验顺序 | 仅参考分题与学习顺序，资源代码以本系列的阿里云示例为准 |
| [ari-hacks/terraform-study-guide](https://github.com/ari-hacks/terraform-study-guide) | 按基础概念、CLI、模块、状态、配置语言组织的学习提纲 | README 标明面向 2020 年认证；用于查漏补缺，不作为当前版本规范 |
| [antonbabenko/terraform-best-practices](https://github.com/antonbabenko/terraform-best-practices) | 目录结构、命名、模块边界与协作经验；提供简体中文译本入口 | 社区实践包含取舍，不能把某一种目录结构当成 Terraform 强制要求 |
| [hashicorp-education/learn-terraform-locals](https://github.com/hashicorp-education/learn-terraform-locals) | 官方教程配套代码，展示 locals 如何减少重复 | 读配套教程并核对 Provider 版本；不要仅复制片段 |
| [hashicorp-education/learn-terraform-troubleshooting](https://github.com/hashicorp-education/learn-terraform-troubleshooting) | 官方排错练习，按语言、状态、Core、Provider 区分问题 | 练习包含故意制造的错误；云实验可能创建收费资源 |

英文课程帮助确定“先学什么”，社区最佳实践帮助讨论“项目怎么组织”，官方文档负责确认“这个字段和命令到底怎么工作”。

## 官方资料怎么查

- [Terraform 文档](https://developer.hashicorp.com/terraform/docs)：CLI、语言、状态和工作流。
- [Terraform 语言参考](https://developer.hashicorp.com/terraform/language)：遇到 `for_each`、`lifecycle`、`module` 等语法时先查这里。
- [Terraform CLI 参考](https://developer.hashicorp.com/terraform/cli)：查询命令选项、退出码、状态操作。
- [AliCloud Provider 1.266.0](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs)：查询阿里云 resource/data source 的参数、导入 ID 与认证方式。
- [Terraform Registry](https://registry.terraform.io/)：查询其他 Provider 和模块接口。
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

下一篇：[[IaC/terraform/01_terraform_基础概念与第一个项目|Terraform 基础概念与第一个项目]]。

知识层导航：[[KnowledgeBase/maps/terraform-map|Terraform 主题地图]] · [[KnowledgeBase/entities/Terraform|Terraform 实体页]]。
