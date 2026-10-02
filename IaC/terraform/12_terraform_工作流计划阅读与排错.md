---
title: 12_terraform_工作流计划阅读与排错
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform工作流
  - Terraform排错
---

# 12_terraform_工作流计划阅读与排错

## 一个可审查的工作流

日常变更围绕 **写配置 → 检查 → 计划 → 审查 → 执行 → 核对结果** 展开。不同命令回答不同问题：

| 命令 | 回答的问题 |
|---|---|
| `terraform fmt -check -diff` | 格式是否符合约定？ |
| `terraform validate` | 初始化后的配置语法和内部引用是否一致？ |
| `terraform test` | 我写下的行为断言是否成立？是否会实际创建资源取决于测试设置 |
| `terraform plan` | 在当前输入、状态与环境下，计划做什么？ |
| `terraform apply` | 实际执行计划的结果是什么？ |
| 平台查询和业务检查 | 资源和服务是否真的达到使用要求？ |

`validate` 不能代替真实 plan；plan 成功也不能保证权限、配额、网络和外部依赖在 apply 时都没问题。

## 一个根目录里的标准操作

以下是独立实验或已授权代码项目的操作示例。先确认目录、目标账号、Backend 和 Workspace：

```bash
terraform version
terraform workspace show
terraform providers
terraform fmt -check -diff
terraform validate
terraform plan -var-file=dev.tfvars -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform plan -var-file=dev.tfvars
```

初始化应在首次准备或配置变化需要时完成，不必把 `init -upgrade` 当成每次运行的固定动作。最后一个 plan 检查预期之外的残留差异，但不代替业务验收。

`terraform providers` 能帮助确认依赖的 Provider 来源，不能证明当前凭证对应哪个账号。账号、Docker daemon 或集群 context 还要用对应平台工具核对，Backend 与 Provider 可能使用不同身份。

## 本地实验：区分更新和替换

新建独立目录 `12-plan-reading/`，不要覆盖前一章的实验。创建完整 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "message" {
  description = "可以原地更新的数据"
  type        = string
  default     = "config-v1"
}

variable "release" {
  description = "变化时显式要求替换的标记"
  type        = string
  default     = "v1"
}

resource "terraform_data" "app" {
  input            = { message = var.message }
  triggers_replace = var.release
}

output "record" {
  description = "逻辑实例身份及保存的数据"
  value = {
    id      = terraform_data.app.id
    message = terraform_data.app.output.message
  }
}
```

`terraform_data` 是内置资源，不调用云 API。`input` 保存数据，`triggers_replace` 指定变化时应替换实例的值，`id` 是该逻辑实例的身份。步骤如下：

```bash
terraform init
terraform plan -out=create.tfplan
terraform show create.tfplan
terraform apply create.tfplan
terraform output record
```

第一次预期创建一个实例，id 在 apply 前未知。然后按以下顺序观察：

| 修改 | Plan 中的重点 | 执行后观察 |
|---|---|---|
| 只把 message 默认值改为 `config-v2` | `input` 的原地更新，通常显示 `~` | message 改变，id 保持 |
| 保留新 message，再把 release 改为 `v2` | `triggers_replace` 变化触发替换，通常显示 `-/+` | message 相同，id 改变 |
| 保持源码不变再 plan | 没有待执行的资源变更 | 输出仍对应最后一次实例 |

每次修改后，完整生成、审查并执行新的计划：

```bash
terraform plan -out=change.tfplan
terraform show change.tfplan
terraform apply change.tfplan
terraform output record
```

实验结束后生成并审查删除计划，再执行 `terraform apply destroy.tfplan`：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

以上都是供读者执行的步骤和预期观察，不是已完成的运行记录。

## 怎么读 Plan

### 动作符号

| 符号 | 含义 |
|---|---|
| `+` | 创建 |
| `~` | 原地更新 |
| `-` | 删除 |
| `-/+` | 先删除，再创建替换对象 |
| `+/-` | 先创建，再删除旧对象 |
| `<=` | 读取 Data Source |

替换会同时计入创建和删除数量。不要只看最后一行 “to add”，忽略前面的删除和替换原因。

### 属性差异与 unknown

```text
  # terraform_data.app must be replaced
-/+ resource "terraform_data" "app" {
      ~ id               = "旧ID" -> (known after apply)
      ~ triggers_replace = "v1" -> "v2" # forces replacement
    }
```

这是示意输出，不是实际运行日志。

- `forces replacement` 指出触发替换的字段。
- `(known after apply)` 表示此时值未知，常见于新对象的 ID。
- 资源删除原因可能是配置块被移除、count 变小、for_each key 消失或地址改名未迁移。
- outputs 的变化可能只是展示接口变化，不一定意味着实际对象变化。

### 审查时看哪些内容

先确认变更对象属于预期环境，再核对每个删除/替换及其原因。尤其要看：

- 云资源 ID、订阅/账号、region、namespace 等是否符合目标。
- 是否发生由地址改名、模块升级或 key 变化造成的非预期替换。
- 有状态数据、网络接入、权限和外部依赖是否受影响。
- 默认值、自动加载 tfvars、Provider 版本是否改变了输入。

“No changes” 只说明当前配置和此次读到的状态之间没有计划差异，不证明业务一定健康。

## 保存计划与直接 apply

```bash
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
```

执行保存的计划时：

- 不重新传入另一套 `-var` / `-var-file`。
- 不再要求终端确认 `yes`，计划文件本身就代表待执行的决定。
- 状态已被其他运行修改时，可能报 `Saved plan is stale`。
- 计划不是永久有效的 API 承诺，外部资源和权限仍可能变化。

直接运行 `terraform apply` 会先生成新的计划，再等待交互确认。`-auto-approve` 会跳过这一步的确认，适合已经有其他审查与授权机制的受控自动化。

保存的 Plan 可能包含明文敏感值，不要把它当成可公开分享的 diff。review 后代码、输入、状态或执行身份变了，应重新生成并审查计划。源码的后续修改不会被偷偷合入旧计划，执行旧文件仍是执行那份计划中的决定，所以还应确认计划所属的提交和环境。

## 常用命令选项

| 选项 | 用途 | 使用边界 |
|---|---|---|
| `-input=false` | 禁止交互询问变量 | 自动化中缺值应明确失败 |
| `-lock-timeout=5m` | 等待 State 锁 | 不能修复缺少锁权限或残留锁 |
| `-detailed-exitcode` | 区分错误、无变化、有变化 | 有变化返回 2，应正确处理 |
| `-replace=ADDRESS` | 明确要求替换某个管理实例 | 先看完整影响范围，优先于旧 taint 工作流 |
| `-target=ADDRESS` | 聚焦目标及必要依赖 | 异常恢复工具，不作为长期日常发布方式 |
| `-refresh=false` | 跳过实际对象刷新 | 可能漏掉外部变化，不作为默认提速方案 |
| `-parallelism=N` | 限制图遍历并发 | 帮助处理 API 限速，不能改变逻辑依赖 |
| `-chdir=DIR` | 指定工作目录 | 是全局选项，放在子命令前 |

```bash
terraform -chdir=environments/dev plan -var-file=dev.tfvars
terraform plan -replace='local_file.config["web"]' -out=replace.tfplan
```

这里 `-var-file` 等命令选项的相对路径按实际执行目录解析；代码中的 `path.module` 等路径表达式另有自己的含义。replace 示例要使用真实存在的地址，不能把方括号里的 key 当成任意显示名。

## 三种计划模式

| 模式 | 命令 | 目标 |
|---|---|---|
| 普通 | `terraform plan` | 让资源符合配置 |
| Refresh-only | `terraform plan -refresh-only` | 让状态记录和根输出符合实际对象 |
| Destroy | `terraform plan -destroy` | 清理当前 State 管理的对象 |

refresh-only 不会更新 `.tf`，destroy 也不会删除 `.tf`。完整示例见 [[IaC/terraform/08_terraform_状态漂移与状态操作|State]]。

## 排错先分层

官方排错教程把问题分为语言、状态、Core、Provider 四层。实际操作时，再结合 Backend、认证和平台错误判断：

| 现象 | 优先排查 | 避免的处理 |
|---|---|---|
| HCL 语法/引用错误 | 行号、块结构、变量与地址是否声明 | 直接改 State |
| `Invalid index` | count=0、list 越界、map key 不存在 | 在所有引用外面包 try 隐藏问题 |
| `Invalid for_each argument` | key 是否已知，类型是否为 map/set(string) | 盲目 target 强行分次运行 |
| `Cycle` | 资源、数据源和模块的循环引用 | 为所有资源追加 depends_on |
| Backend 初始化失败 | 状态位置、endpoint、网络、Backend 认证 | 切到空本地状态直接 apply |
| 获取锁失败 | 是否有活跃运行，锁文件/Blob lease 权限 | `-lock=false` 继续并发 |
| 401/403 | 执行身份、token 时效、目标 scope 权限 | 删除资源或移除状态“修权限” |
| 429/QPS/Rate Limit | API 限速、Provider 重试和并发 | 反复无间隔重跑大量请求 |
| Provider 配置缺失 | 仍被 State 引用的 alias 是否被删 | 批量 state rm |
| checksum 错误 | 锁文件、下载渠道、实际执行环境缓存 | 关闭校验或删除整个依赖约束 |

先保存错误、版本、操作目录和相关地址，再调整配置。debug 日志可能含敏感信息，公开 issue 只提供脱敏后的最小复现。

本地、CI runner 与远程 Terraform 执行平台不一定使用同一套凭证、工具和缓存。错误出现在远程 runner 时，要检查实际执行环境；删除开发机缓存不能证明远程问题已解决。

## apply 中途失败

Terraform 不是把所有平台 API 包装成一个原子事务。一个运行中，A 可能已成功创建，B 因权限失败，C 尚未执行。

恢复步骤：

1. 查看原错误和实际已完成的动作。
2. 检查当前 State、平台资源与账号，确认部分成功对象的管理记录。
3. 修复具体原因，例如权限、输入或资源配额。
4. 重新生成完整 plan，审查剩余动作，再执行。

通常不要拿旧计划反复执行，也不要先删除 State“从头开始”。若出现实际已创建但未被记录的对象，需要按 Provider 文档核对后 import，而不是建立第二个同名对象。

如果状态写入 Backend 失败，Terraform 可能保存紧急本地状态文件。应停止并发、保留文件，并按错误提示评估受控恢复；不要把它当作可删除的普通临时文件。

## 代码回退不等于资源回滚

Git revert 能恢复声明，不会自动恢复已删除的数据或对象身份。重新 plan 后，可能出现新的创建、替换或无法原地还原的参数变更。

需要备份恢复、流量切换、数据迁移的变更，应在执行前设计相应的业务恢复方式。`create_before_destroy` 也不能单独保证零停机，平台并存能力和流量入口必须配合。

## 诊断工具

```bash
terraform version
terraform providers
terraform workspace show
terraform state list
terraform state show 'local_file.config["web"]'
terraform console
```

console 适合验证表达式、类型和 key；state 命令适合看身份记录；平台 CLI 适合确认真实对象。

要查看当前依赖图，可使用 `terraform graph`，它输出图结构而不执行资源变更。图中没有表达式求值结果，也不能代替 Plan 的动作审查。

深入排查时可在受控目录保存日志：

```bash
TF_LOG=DEBUG TF_LOG_PATH=./terraform-debug.log terraform plan -out=debug.tfplan
```

这是一次真实 plan，可能读取平台 API。`TF_LOG` 控制日志级别，`TF_LOG_PATH` 指定文件；按问题需要短暂启用，日志与计划都按敏感文件保管。`terraform output <敏感输出名>` 或 `output -json` 也可能明文显示结果，不能把终端遮盖当成日志脱敏。

需要机器读取计划动作时，可在受控环境中使用：

```bash
terraform show -json tfplan | jq '.resource_changes[]? | {address, actions: .change.actions}'
```

JSON 中的其他字段可能含敏感值，不能因为抽取结果只显示地址，就把原始计划 JSON 公开。

## 练习

1. 在本章 terraform_data 实验中，分别观察 input 更新与 triggers_replace 替换，记录 id 是否改变。
2. 给 count=0 的资源增加错误的 `[0]` 引用，观察并修复 Invalid index。
3. 模拟 A 成功、B 失败的执行过程，说明重新 plan 为什么比“删 State 重跑”更合理。

## 参考资料

- [Plan 命令与退出码](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Apply 与保存计划](https://developer.hashicorp.com/terraform/cli/commands/apply)
- [官方排错教程](https://developer.hashicorp.com/terraform/tutorials/configuration-language/troubleshooting-workflow)
- [官方排错练习仓库](https://github.com/hashicorp-education/learn-terraform-troubleshooting)
- [全局 chdir 选项](https://developer.hashicorp.com/terraform/cli/commands)
- [环境变量与日志](https://developer.hashicorp.com/terraform/cli/config/environment-variables)
- [terraform_data 的更新与替换](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
- [Plan JSON 格式](https://developer.hashicorp.com/terraform/internals/json-format)
- [依赖图命令](https://developer.hashicorp.com/terraform/cli/commands/graph)

上一篇：[[IaC/terraform/11_terraform_资源导入与重构|导入与重构]] · 下一篇：[[IaC/terraform/13_terraform_测试与持续集成交付|测试与 CI/CD 协作]]。
