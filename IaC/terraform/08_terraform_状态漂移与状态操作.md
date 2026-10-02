---
title: 08_terraform_状态漂移与状态操作
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform State
  - Terraform状态与漂移
---

# 08_terraform_状态漂移与状态操作

## State 不是基础设施的备份

State 保存 Terraform 地址与远端对象的绑定，以及 Provider 关联和已知属性等元数据。它帮助 Terraform 找到配置管理的是哪个对象，不包含数据库业务记录、磁盘文件内容或完整环境备份。Terraform 也提供状态命令，不应直接编辑 State JSON。保存的计划文件是另一种格式，不要与 State 混淆。

生产代码出处：`shared/jfrog-cn.tf`（脱敏裁剪/教学改编）中的 `alicloud_oss_bucket` 与 `alicloud_oss_bucket_acl` 是独立资源；ACL 的 `bucket` 属性引用 Bucket 名称，Bucket 设置 `force_destroy = false`。05 篇在此基础上建立自己的空教学 Bucket。本实验只操作该教学资源，不触及生产 Bucket。Provider 文档说明，ACL 资源从 State 移除时，ACL 设置可能继续留在 OSS。

## 资源地址与实际 ID

```text
alicloud_oss_bucket.lab
alicloud_oss_bucket_acl.lab[0]
module.alerts.alicloud_cms_alarm.rules["cpu"]
```

这些是不同配置下的地址形式，包含单实例、count 和模块内 for_each 示例，并非第 05 篇的 State 清单。实际 ID 格式由 Provider 定义，例如 OSS Bucket 的导入 ID 是 Bucket 名称。移动 `.tf` 文件不会改变地址；修改逻辑名、模块路径、count 索引或 for_each key 会改变地址。State 不会按名称相似程度推断迁移关系。

## 一次普通 plan 中的三方比较

Terraform 读取配置了解目标状态，读取 State 找到先前绑定，再通常通过 Provider 查询实际对象，最后生成让实际对象趋近配置的计划。普通 `plan` 会进行刷新读取，但读取和计划计算本身不等于资源变更；需审阅并执行计划才会应用目标变更。

## 漂移是什么

漂移是 Terraform 管理之外发生的变化，导致实际对象与配置或 State 记录不同。它可能来自控制台改属性、其他自动化修改对象、对象被删除，或 Provider 读回经过服务端规范化的值。并非每个计划差异都是漂移；变量、Provider 或 `.tf` 变化也会产生差异。

## OSS Bucket 漂移实验

本实验沿用 [[IaC/terraform/05_terraform_提供者版本与认证|05 篇]] 的空 OSS Bucket 与 ACL。若已完成该篇清理，先按其步骤重新创建这两个教学资源，再进入本节；不要在实验开始前销毁它们。保持在同一个目录、Backend 与 Workspace；命令均使用本地受控的 `lab.tfvars`，变量名与 05 篇一致：`region`、`bucket_name` 和 `tags`；其中只填自己的教学地域、全局唯一 Bucket 名和教学标签，不要保存生产值。

### 1. 确认基线

```bash
terraform plan -var-file=lab.tfvars
terraform state list
terraform state show alicloud_oss_bucket.lab
terraform state show alicloud_oss_bucket_acl.lab
```

配置与教学 Bucket 一致时，普通计划预期没有变更。Bucket 与 ACL 是两个状态地址；ACL 资源的导出 ID 与 Bucket ID 基于相同 Bucket 名，但承担不同配置责任。

### 2. 在控制台修改 Bucket 标签

在 OSS 控制台只修改此教学 Bucket 的 `purpose` 标签，改成与 `lab.tfvars` 不同的教学值。随后查看普通计划：

```bash
terraform plan -var-file=lab.tfvars -out=tag-drift.tfplan
terraform show tag-drift.tfplan
```

预期 Terraform 计划将标签恢复为配置中的值。确认差异只涉及教学 Bucket 标签后，应用并核对：

```bash
terraform apply tag-drift.tfplan
terraform plan -var-file=lab.tfvars
```

预期标签恢复后计划无变更。生产 Bucket 的标签来自 `var.jfrog_cn_tags`，教学项目的输入变量名为 `tags`；来源为 `shared/jfrog-cn.tf`，但此处只修改 05 篇建立的个人实验标签。

### 3. 在控制台删除专用空 Bucket

先核对 Bucket 名与账号，并确认只含可删除的教学对象。05 篇配置 `force_destroy = false`，因此不要向桶内上传文件。通过 OSS 控制台删除这个实验 Bucket 后，分别观察普通计划和 refresh-only 计划：

```bash
terraform plan -var-file=lab.tfvars -out=missing-bucket.tfplan
terraform show missing-bucket.tfplan
terraform plan -refresh-only -var-file=lab.tfvars -out=refresh.tfplan
terraform show refresh.tfplan
```

普通计划预期提出重新创建缺失的 Bucket，并处理关联的 ACL。先不要应用普通计划；refresh-only 的目标是反映外部删除，应用后不创建 Bucket：

```bash
terraform apply refresh.tfplan
terraform state list
```

预期不存在的 Bucket/ACL 绑定从 State 移除，实际 Bucket 仍保持删除。Provider 报告结果决定具体绑定变化。然后用新的普通计划恢复教学基线：

```bash
terraform plan -var-file=lab.tfvars -out=restore.tfplan
terraform show restore.tfplan
terraform apply restore.tfplan
terraform plan -var-file=lab.tfvars
```

预期恢复 Bucket 与 private ACL，最后的普通计划无变更。不要沿用 `missing-bucket.tfplan` 或 `refresh.tfplan` 做其他状态操作。

## refresh-only：接受现实到记录中

上面的 OSS 实验显示两种目标：普通计划要让实际资源回到配置；refresh-only 计划只更新 State 与根输出，使其反映外部删除。refresh-only 不修改 `.tf`；刷新后，Bucket 仍处于删除状态，下一次普通计划会再次提出创建。

外部删除后，Provider 对不存在对象的报告方式决定哪些 State 绑定会被移除。旧 `terraform refresh` 会直接应用状态刷新，缺少明确的计划审阅；先运行 `plan -refresh-only` 并检查结果，再应用审核过的刷新计划。

## 常用 State 命令

| 命令 | 作用 | 会否直接删除实际对象 |
|---|---|---|
| `terraform state list` | 列出地址 | 否 |
| `terraform state show ADDRESS` | 查看对象记录 | 否 |
| `terraform state pull` | 输出当前快照 | 否，但可能显示敏感值 |
| `terraform state mv A B` | 修改状态地址绑定 | 否 |
| `terraform state rm ADDRESS` | 忘记管理绑定 | 否 |
| `terraform state push FILE` | 写回快照 | 不直接删除对象，但可能覆盖记录 |

### 引号保护地址

```bash
terraform state show 'alicloud_cms_alarm.cms_alarms["<教学告警key>"]'
```

Bash/zsh 下用单引号保护方括号和内层双引号；`<教学告警key>` 仅是占位符，应替换为自己配置里的 key。PowerShell 按其自己的转义规则处理。

### 导出备份

```bash
mkdir -p ~/terraform-labs/state-backups
umask 077
terraform state pull > ~/terraform-labs/state-backups/before-change.json
```

State 可能含敏感属性，备份放在有访问控制的位置，不能提交 Git 或放进公开 CI artifact。以上命令仅用于自己的隔离实验状态。

## state rm 与 destroy 的区别

`destroy` 或删除配置后应用计划会请求 Provider 删除实际对象；`state rm` 只移除 State 绑定，对象继续存在。若删绑定后保留 resource 配置，下次计划会尝试创建新对象，可能导致名称冲突或重复资源。`terraform state rm -dry-run ADDRESS` 可先看将命中的状态地址，实际 `state rm` 会直接修改状态，没有常规 plan/apply 审阅阶段。

希望通过配置声明停止管理且保留对象，可考虑第 11 篇的 `removed { lifecycle { destroy = false } }`。

## 为什么同一个对象不能被两份 State 管理

Terraform 预期一个远端对象只绑定到一个 resource instance。两个独立 State 都认为自己负责同一对象，可能互相覆盖、删除，或在一个 State 丢失绑定后创建替代对象。拆分项目应安排一次明确的所有权移交：停止旧项目对对象的写操作，再由新项目纳管。State 锁只协调对应 Backend 状态的并发访问，不识别另一份 State 是否管理同一云 ID。

## 本地状态与协作

默认 Local Backend 把 `default` Workspace 状态保存在工作目录的 `terraform.tfstate`，其他 CLI Workspace 默认放在 `terraform.tfstate.d/<workspace>/terraform.tfstate`。多人协作需共享且受控的远程 State；Git 不能提供状态锁，且会在历史记录里长期保留敏感值。远程状态详见 [[IaC/terraform/09_terraform_后端工作空间与多环境|Backend 与 Workspace]]。

## 敏感数据会出现在哪里

资源属性、数据源结果、输出和保存的计划可能包含敏感值。标注 `sensitive` 通常会遮蔽部分终端显示，不会保证从 State 或计划文件中移除。`terraform state pull`、`terraform show -json` 和 debug 日志也可能输出值。Secret Manager 集中存放凭证并不意味着将读取结果写入普通资源参数后就不会进入 State。

## 状态损坏或丢失时怎么办

先暂停该状态的并发运行并确认账户、Backend 与 Workspace；检查受控的版本历史和运行日志；将可恢复快照与当前实际资源逐项对照；需要时再评估导入。恢复旧 State 不会回滚云资源，旧状态可能引用已删除、重建或被外部修改的对象。管理记录恢复与资源、业务数据恢复是不同工作。

## 清理 OSS 实验

对 05 篇自己的空教学 Bucket 项目生成并审阅销毁计划，再执行：

```bash
terraform plan -destroy -var-file=lab.tfvars -out=cleanup.tfplan
terraform show cleanup.tfplan
terraform apply cleanup.tfplan
```

预期仅删除自己仍纳管的教学 Bucket；ACL 资源退出状态时可能仍保留 ACL 设置。执行前须再次核对 Bucket 名和桶内对象。受控保存的 State 快照不会随销毁自动删除。

## 练习

1. 比较在控制台删除教学 Bucket 与从配置删除 Bucket resource 的计划目标。
2. 说明 refresh-only 计划为何不会修改 `.tf`，以及何时普通 plan 仍会有创建动作。
3. 在专用目录里用 dry-run 查看 `state rm` 匹配范围，并推演保留 resource 配置后的下一次计划；不要对生产状态操作。

## 参考资料

- [State 的用途](https://developer.hashicorp.com/terraform/language/state/purpose)
- [State 命令](https://developer.hashicorp.com/terraform/cli/commands/state)
- [state rm](https://developer.hashicorp.com/terraform/cli/commands/state/rm)
- [plan 与 refresh-only](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [terraform refresh（已弃用）](https://developer.hashicorp.com/terraform/cli/commands/refresh)
- [敏感数据与 State](https://developer.hashicorp.com/terraform/language/state/sensitive-data)
- [CLI Workspace](https://developer.hashicorp.com/terraform/cli/workspaces)
- [alicloud_oss_bucket（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/oss_bucket)
- [alicloud_oss_bucket_acl（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/oss_bucket_acl)

上一篇：[[IaC/terraform/07_terraform_循环与批量资源|count 与 for_each]] · 下一篇：[[IaC/terraform/09_terraform_后端工作空间与多环境|Backend 与多环境]]。
