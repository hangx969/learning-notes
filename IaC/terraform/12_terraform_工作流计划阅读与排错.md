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

## 从配置到验收

可靠的变更过程包括写配置、检查输入和身份、生成计划、逐项审查、在授权环境执行、核对真实结果。生产依据来自 `monitoring/modules/cloud-monitor-alerts/` 联系人与组资源，以及 `monitoring/cloud-monitor-alert.tf` 的调用方式；以下计划片段均是**示意输出**，不是在生产或实验账号执行所得。

| 步骤 | 工具或证据 | 能回答的问题 |
|---|---|---|
| 格式与静态检查 | `terraform fmt -check -recursive`、代码审阅 | HCL 格式、接口与依赖是否清楚 |
| 依赖检查 | `terraform providers`、`.terraform.lock.hcl` | Provider 来源和锁定版本是什么 |
| Plan | 目标 Backend、Workspace、变量和身份下的 `terraform plan` | 本次状态和输入将触发哪些操作 |
| Apply | 经审查的同一计划 | 计划中的动作是否实际完成 |
| 执行后核对 | Terraform State 与平台查询 | 资源是否存在并满足需求 |

Plan 不验证所有 apply 阶段条件。网络、配额、API 服务、RAM 授权、跨账号信任以及后端锁权限都可能在执行中失败。格式检查通过也不证明配置语义或远程身份正确。

## 生成与审查计划

以下命令是面向**已授权的隔离实验 workspace**的示范流程。这里的 CMS 例子会创建联系人与联系人组；不得指向生产 workspace。按第 10 篇内容将完整 root module 建在 `$HOME/terraform-labs/10-cms-contacts/`。它没有必需 root 输入变量，也没有配置远程 Backend，因此该目录默认使用本地 State。命令不会把 child module 单独当作根目录：

```bash
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" version
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" workspace show
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" providers
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" fmt -check -recursive
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" plan -out=tfplan
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" show tfplan
```

首次准备或依赖约束变化时才需要初始化；首次运行前执行 `terraform -chdir="$HOME/terraform-labs/10-cms-contacts" init`。不要将 `init -upgrade` 作为每次运行的固定步骤。远程 Backend 身份和 AliCloud Provider 身份可能不同；`terraform providers` 只显示依赖来源，不会证明当前调用属于预期账号。

示意计划：

```text
# module.lab_contacts.alicloud_cms_alarm_contact.contacts["ops"] will be created
+ resource "alicloud_cms_alarm_contact" "contacts" {
    + alarm_contact_name = "terraform-lab-ops"
    + channels_mail      = "terraform-lab@example.invalid"
  }

# module.lab_contacts.alicloud_cms_alarm_contact_group.contact_groups["platform"] will be created
+ resource "alicloud_cms_alarm_contact_group" "contact_groups" {
    + alarm_contact_group_name = "terraform-lab-platform"
    + contacts                 = ["terraform-lab-ops"]
  }
```

这是根据教学配置写出的示意文本，不保证实际 Provider 输出完全一致。审查要确认地址、区域、账号、输入、敏感字段及依赖顺序。确认授权后才应用保存的计划：

```bash
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" apply tfplan
```

保存计划可能包含敏感值，按敏感文件保存和传递。计划应绑定已审查的代码版本、锁文件、变量、Workspace 与执行身份。上述任一项或 State 在计划后发生变化，都应重新生成计划并重新审批；不要把旧计划当作长期有效的审批记录。执行保存计划时不会重新询问交互式 `yes`。

若 root module 使用 Terraform Cloud/Enterprise 的 remote execution，Plan 与 Apply 由 Workspace Run 管理，按当前平台版本和 Workspace 设置在平台审查、批准与执行。不要默认所有 TFE 版本或执行模式都接受本地 `tfplan` 文件；本地文件流程和平台 Run 的批准/执行流程应按实际 Terraform/TFE 版本确认。

## 动作符号和未知值

| 符号 | 说明 |
|---|---|
| `+` | 创建 |
| `~` | 原地更新 |
| `-` | 删除 |
| `-/+` | 删除后重建 |
| `+/-` | 先创建再删除 |
| `<=` | 读取数据源 |

替换会同时计入创建和删除。`(known after apply)` 常见于新资源 ID 等只有执行后才有的值。对于联系人模块，map key 决定 `for_each` 实例地址；改 key 会让旧地址消失、新地址出现，应先判明是否需要 State 地址迁移。不要仅凭 Plan 汇总行判断影响。

“No changes” 仅表示此次输入与读取到的状态没有待执行差异，不等同于告警通知正常、集群健康或服务可用。

## 常用选项的边界

```bash
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" plan -lock-timeout=5m -detailed-exitcode
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" plan -replace='module.lab_contacts.alicloud_cms_alarm_contact.contacts["ops"]'
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" plan -refresh-only
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" plan -destroy
```

`-chdir` 是全局选项，应放在子命令前；命令参数中的相对文件路径按实际执行目录解析。`-detailed-exitcode` 的 2 表示存在差异，不是命令失败。`-replace` 会明确要求替换指定地址；`-refresh-only` 只更新状态与输出，destroy plan 则展示当前 State 管理对象的删除方案。`-target` 和 `-refresh=false` 可能隐藏完整变更，不作为日常发布捷径。

## 排错要先找执行边界

| 现象 | 结合本仓库代码优先检查 |
|---|---|
| Provider 身份错误或 401/403 | `monitoring/cloud-monitor-alert.tf` 中的 Provider alias 到 module 映射；本地 `ALIBABA_CLOUD_*` 凭证或 TFE workspace/Agent 身份；目标账号和 region；跨账号角色信任及 RAM 权限分别核验 |
| 找不到资源、类型或字段 | `monitoring/modules/cloud-monitor-alerts/versions.tf` 的最低 Provider 约束、根锁文件选定版本，以及目标 Provider 文档 |
| 版本解析失败 | 各 module 的 `required_providers` 是否有交集；`.terraform.lock.hcl` 与执行环境的 Provider 缓存是否一致 |
| Backend 初始化、锁失败 | Backend endpoint、状态位置、网络、锁服务权限和是否有并发运行；不能切换到空本地 State 继续 apply |
| `Invalid index` / `Invalid for_each argument` | 实际 map/list key 和集合值是否在计划期已知，避免用 `try` 掩盖无效输入 |
| `Cycle` | 资源、数据源、模块之间的真实引用；只为有隐藏依赖的场景补 `depends_on` |
| 429 / 限流 | AliCloud API 限制、执行并发和 Provider 重试；不要无间隔重放大量请求 |
| TFE runner 下载/校验异常 | 找到实际运行 workspace 的 Agent/runner、其锁文件和 Provider 缓存目录；本地缓存不能代表远程执行环境 |

如果 apply 中途失败，Terraform 不是跨平台原子事务。例如联系人可能已创建，联系人组请求因权限失败，后续资源尚未执行。先保留错误和日志，核对 State 与实际 CMS 对象，确定部分成功对象是否已写入 State；再修复账号/alias、跨账号信任或 RAM 权限，重新生成完整计划，审查剩余动作后再执行。不要盲目重放旧计划、删除 State 或依赖 Git 回退来撤销云端动作。若确认实际对象存在而 State 中没有，再按 Provider 文档核对并考虑导入。State 写回 Backend 失败时保留紧急本地 State 文件并停止并发，由有权限的运维流程评估恢复。

调试日志和 JSON 计划可能包含敏感值。只在受控目录短时收集，分享前删去 token、证书、账号 ID、内部主机名、联系信息和资源标识。

## Console、State、依赖图和日志

在第 10 篇本地 State 实验根目录，以下命令可帮助检查值、地址和资源依赖；State 命令可能显示保存的敏感属性：

```bash
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" console
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" state list
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" state show 'module.lab_contacts.alicloud_cms_alarm_contact.contacts["ops"]'
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" graph
```

`console` 适合检查表达式和集合 key；`state list/show` 用于核对 Terraform 中的地址和值，不是云端健康检查；`graph` 输出依赖图结构，不执行资源变更，也不能替代 Plan。

如需诊断 Provider/API 错误，可在受控目录短时写日志：

```bash
TF_LOG=DEBUG TF_LOG_PATH="$HOME/terraform-labs/10-cms-contacts/terraform-debug.log" \
  terraform -chdir="$HOME/terraform-labs/10-cms-contacts" plan -out=tfplan
```

要机器读取资源动作，可在受控目录查看 JSON 计划摘要：

```bash
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" show -json tfplan \
  | jq '.resource_changes[]? | {address, actions: .change.actions}'
```

日志、计划及 `terraform show -json tfplan` 可能包含证书、凭证和资源信息。远程 TFE 错误则应查看对应 Workspace Run、Agent/runner 日志、运行身份、锁文件及其缓存；本机的 Console、State 文件和 Provider 缓存不能代表远端运行状态。

## 练习

1. 在授权隔离配置中先为 `terraform-lab-ops` 生成创建计划，解释为何需要同时核对 Provider alias 和 Backend workspace。
2. 将 `contacts` map key 从 `ops` 改为 `operations`，观察计划地址变化；说明名称字段和 Terraform 实例身份的区别。
3. 假设联系人已创建、联系人组因 RAM 权限失败，列出核对 State、实际对象、权限并重新计划的恢复步骤。
4. 对比本地检查与 TFE 运行错误，指出两边分别使用的锁文件和 Provider 缓存证据。

## 参考资料

- [terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [terraform apply 与保存计划](https://developer.hashicorp.com/terraform/cli/commands/apply)
- [Provider 身份与配置](https://developer.hashicorp.com/terraform/language/providers/configuration)
- [依赖锁文件](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [Terraform 命令环境变量](https://developer.hashicorp.com/terraform/cli/config/environment-variables)

上一篇：[[IaC/terraform/11_terraform_资源导入与重构|导入与重构]] · 下一篇：[[IaC/terraform/13_terraform_测试与持续集成交付|测试与 CI/CD 协作]]。
