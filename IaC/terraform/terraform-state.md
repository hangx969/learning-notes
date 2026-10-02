---
title: Terraform基础-State、漂移与状态操作
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform State
  - Terraform状态与漂移
---

# Terraform基础-State、漂移与状态操作

## State 不是基础设施的备份

State 记录资源地址与实际对象的绑定，以及已知属性、依赖和 Provider 关联等元数据。Terraform 借助它找到“配置中的这个对象”在平台上对应什么。

State 通常使用 JSON 表示；保存的 Plan 是另一种不透明格式，二者不要混淆。不要手工改 State JSON，也不要把它当成数据库数据、磁盘内容或完整云环境的备份。

例如 State 知道某个数据库实例的 ID，不代表它包含数据库中的业务记录。恢复 State 和恢复实际资源是两件事。

## 资源地址与实际 ID

```text
azurerm_resource_group.app
local_file.config["web"]
module.app.local_file.config
module.app["api"].local_file.config
```

这些是 Terraform 地址。真实 ID 可能是 Azure 资源路径、云对象 ID、文件内容摘要等，由 Provider 定义。

移动 `.tf` 文件不改变地址；改资源逻辑名、模块路径、count 索引或 for_each key 会改变地址。State 不会凭“名称看起来很像”自动推断所有改名关系。

## 一次普通 plan 中的三方比较

1. 读取配置，了解目标状态。
2. 读取 State，找到当前由配置管理的对象身份。
3. 通常通过 Provider 读取实际对象，检查外部变化。
4. 结合刷新得到的信息和配置，生成创建、更新、替换、删除动作。

State 是上次已知记录，实际资源可能已被手工修改。普通 plan 的读取和计算不等于执行资源变更，也不能简单等同于已永久提交刷新后的 State。

## 漂移是什么

漂移是 Terraform 管理之外的修改，使实际资源与配置或之前记录的状态不一致。例如：

- 控制台修改云资源标签。
- 其他工具更改同一个 Deployment 的副本数。
- 实验文件被手工删掉或改了内容。
- 平台为资源规范化了某个属性，Provider 读回值与旧记录不同。

不是所有 plan 差异都来自漂移。变量值变化、Provider 升级、模块修改同样会产生差异。

## 本地漂移实验

使用 [[IaC/terraform/terraform-basics|第一个项目]] 的 `local_file.hello` 配置，先完成创建。

### 1. 确认基线

```bash
terraform plan
terraform state list
terraform state show local_file.hello
```

在无其他变化时，预期为 No changes。记下配置地址，而不是只看文件名。

### 2. 在 Terraform 外修改文件

在当前实验目录中修改自己的 `hello.txt`，然后查看计划：

```bash
printf '%s\n' 'changed outside Terraform' > hello.txt
terraform plan -out=drift.tfplan
terraform show drift.tfplan
```

Local Provider 对内容不符可能表现为检测到原对象缺失、提出重新创建，以恢复配置内容。不能把这个实验的具体动作直接推广到所有云资源；标签等字段可能原地更新。

查看计划后执行并核对：

```bash
terraform apply drift.tfplan
cat hello.txt
```

文件会回到配置要求的内容。若希望手工修改成为新目标，应先修改 `.tf`，再计划和执行。

### 3. 在 Terraform 外删除文件

只删除这个实验文件，再查看恢复目标的计划：

```bash
rm hello.txt
terraform plan -out=missing-file.tfplan
terraform show missing-file.tfplan
```

预期 Terraform 会提出创建，使目标对象重新存在。先保留这个观察，下一节用同一外部删除比较 refresh-only 的目标。

删除磁盘文件与删除 resource 块恰好是两种不同意图：前者通常导致重建，后者通常导致清理仍在管理的对象。

## refresh-only：接受现实到记录中

```bash
terraform plan -refresh-only -out=refresh.tfplan
terraform show refresh.tfplan
terraform apply refresh.tfplan
```

refresh-only 模式主要更新 State 与根输出，让它们反映实际资源，不以修改远程对象来实现配置目标。接着上节的删除实验，预期刷新计划移除已经不存在的文件绑定；应用刷新计划后，文件仍不存在。普通计划中提出的“创建文件”没有在这个模式下执行。

需要区分：

- **同步记录**：承认手工变更已经发生，记录新的状态。
- **改变目标**：更新 `.tf` 或变量，让以后也期望这个变更。

refresh-only 不会自动修改配置。之后再普通 plan，如果配置仍是旧值，Terraform 仍可能提出恢复旧值。

对于已被外部删除、或 Local Provider 判断原对象不再匹配的资源，刷新可能移除原映射，而不是读取手工内容成为新的声明。理解 Provider 的读回规则再使用。

完成观察后，重新生成普通计划来恢复实验基线：

```bash
terraform state list
terraform plan -out=restore.tfplan
terraform show restore.tfplan
terraform apply restore.tfplan
cat hello.txt
```

预期 `local_file.hello` 重新进入 State，文件恢复配置内容。状态已经经过刷新更新，此时重新 plan，不再沿用之前的 `missing-file.tfplan`。

旧的 `terraform refresh` 命令会直接刷新并接受状态更新，缺少同样清晰的 review 步骤。新工作流优先先 plan refresh-only，再执行已查看的计划。

## 常用 State 命令

| 命令 | 作用 | 是否等同于删除真实资源 |
|---|---|---|
| `terraform state list` | 列出当前状态中的地址 | 否 |
| `terraform state show ADDRESS` | 查看某个对象的记录 | 否 |
| `terraform state pull` | 导出当前 State 快照 | 否，但会暴露潜在敏感值 |
| `terraform state mv A B` | 修改对象的状态地址绑定 | 否 |
| `terraform state rm ADDRESS` | 忘记该对象的管理绑定 | 否 |
| `terraform state push FILE` | 将本地快照写回 Backend | 否，但可能覆盖管理记录，应谨慎恢复 |

### 引号保护地址

```bash
terraform state show 'local_file.config["web"]'
```

在 Bash/zsh 中，把含方括号和双引号的地址用单引号包住，避免 shell 通配或引号解释改变地址。PowerShell 应按其转义规则处理。

### 导出备份

```bash
mkdir -p ~/terraform-labs/state-backups
umask 077
terraform state pull > ~/terraform-labs/state-backups/state-before-change.json
```

这只是在执行有意的状态操作前保存快照。备份应在受控存储中保存，不能提交 Git、贴到公开 issue 或上传成无访问控制的 CI artifact。

## state rm 与 destroy 的区别

假设 State 管理着一个已有云对象：

- `destroy` 或删除配置后 apply：向平台发起删除，按结果更新 State。
- `state rm`：只忘记绑定，对象继续在平台上存在。

如果忘记绑定后仍保留 resource 配置，下一次 plan 会尝试创建一个新的目标对象。云端可能出现同名冲突、重复资源；Local Provider 还可能覆盖同一路径的已有文件。

先只核对将匹配哪些地址，可以使用不修改 State 的预览：

```bash
terraform state rm -dry-run local_file.hello
```

预期列出当前实验文件的绑定，不会删除文件，也不会忘记它。如果匹配范围超出预期，应先修正地址；正式的 state rm 会直接修改状态，没有普通 plan/apply 的审查阶段。

因此 state rm 不是解决权限失败或不明 drift 的通用方法。希望退出管理时，优先用可 review 的 `removed { lifecycle { destroy = false } }`，见 [[IaC/terraform/terraform-import-refactoring|导入与重构]]。

## 为什么同一个对象不能被两份 State 管理

两个项目分别认为自己是同一资源的负责人，可能互相覆盖参数、互相删除，或者在一个项目里丢失对象后创建替代对象。

拆分项目时应明确移交：原项目停止修改并退出绑定，新项目纳管对象。不要一边继续原流水线，一边在另一个项目对同一对象 import。

锁通常只协调同一 Backend 状态的访问，不会自动识别另一个 State 也在控制同一个云 ID。

## 本地状态与协作

默认 Local Backend 在 `default` Workspace 中把状态保存为当前工作目录下的 `terraform.tfstate`；其他 CLI Workspace 默认使用 `terraform.tfstate.d/<workspace>/terraform.tfstate`。具体位置也可由 Backend 配置调整。对于单人的短期实验容易理解；多人协作需要共享且受控的远程 State。

把 JSON 文件放进 Git 不是可靠的共享方式：Git merge 不能代替运行锁，历史里还会永久保存敏感值。发给同事一份文件也不能保证两个人运行时使用同一份最新状态。

远程 Backend 的存储、权限、版本恢复和锁定设计见 [[IaC/terraform/terraform-backends-workspaces|Backend 与 Workspace]]。

## 敏感数据会出现在哪里

- 资源参数和数据源结果可能保存在 State 中。
- 根 output 也可保存在 State 中，标记 sensitive 不代表移除。具名 `terraform output <输出名>` 也会明文显示敏感值，不只有 `-raw` 或 `-json` 才会显示。
- 保存的 Plan 包含完整配置及变量值等信息。
- `terraform show -json`、状态导出和 debug 日志可能输出敏感数据。

外部 Secret Manager 的好处是集中发放和控制凭证，但如果把读取出的密码传进会持久化的普通资源参数，密码仍可能进入 State。应分别设计输入来源、持久化行为和访问权限。

## 状态损坏或丢失时怎么办

1. 停止对该状态的并发运行，确认当前账号、Backend 和 Workspace。
2. 检查远程存储版本、历史状态和执行日志，优先从已知有效快照评估恢复。
3. 对照实际资源，确认哪些绑定已存在、哪些需要 import。
4. 查看恢复后的完整 Plan，不把“能读取 State”当作“已经和现实一致”。

不要直接恢复一份旧 State 来尝试“回滚云资源”。旧快照记录的是过去的身份和属性，平台上的对象可能已经删除、重建或被其他系统修改。

State 操作解决记录问题，业务恢复还需要资源和数据层面的备份方案。

## 清理本地实验

完成状态观察后，在最初的专用本地文件目录生成并查看删除计划：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

预期仅删除仍被管理的实验文件。受控保存的 State 快照用于记录恢复，不会随这次资源删除自动消失。

## 练习

1. 解释删除本地实验文件为什么通常导致“创建”，删除 resource 块为什么通常导致“删除”。
2. 比较普通 plan 和 refresh-only plan 的目标，说明后者为什么不会替你改 `.tf`。
3. 在专用实验目录中研究 state rm，但先推演下一次普通 plan 会怎样，不直接用于团队项目。

## 参考资料

- [State 的用途](https://developer.hashicorp.com/terraform/language/state/purpose)
- [State 命令](https://developer.hashicorp.com/terraform/cli/commands/state)
- [state rm](https://developer.hashicorp.com/terraform/cli/commands/state/rm)
- [Refresh-only 与计划模式](https://developer.hashicorp.com/terraform/cli/commands/plan#planning-modes)
- [refresh 命令](https://developer.hashicorp.com/terraform/cli/commands/refresh)
- [敏感数据与状态](https://developer.hashicorp.com/terraform/language/state/sensitive-data)
- [output 命令与敏感值](https://developer.hashicorp.com/terraform/cli/commands/output)
- [CLI Workspace 的状态位置](https://developer.hashicorp.com/terraform/cli/workspaces)
- [Local Provider 的文件行为](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file)

上一篇：[[IaC/terraform/terraform-count-for-each|count 与 for_each]] · 下一篇：[[IaC/terraform/terraform-backends-workspaces|Backend 与多环境]]。
