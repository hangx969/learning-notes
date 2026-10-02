---
title: 07_terraform_循环与批量资源
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform批量资源
  - Terraform for_each
---

# 07_terraform_循环与批量资源

## 为什么需要批量创建

`count` 与 `for_each` 让一个 resource 或 module 块管理多个实例。实例身份可能取自列表位置，也可能取自业务 key；选哪种写法会影响增删、重排时 Terraform 如何匹配实例。同一 resource 或 module 块不能同时设置 `count` 与 `for_each`。

| 比较项 | count | for_each |
|---|---|---|
| 输入 | 非负整数 | map 或 `set(string)` |
| 实例身份 | 从 0 开始的索引 | map key 或 set 成员 |
| 循环内引用 | `count.index` | `each.key`、`each.value` |
| 地址示例 | `terraform_data.cms_alarm[0]` | `terraform_data.cms_alarm["cpu"]` |
| 常见用途 | 固定数量、0/1 条件创建 | 以稳定名称区分的一组对象 |

生产来源：`monitoring/modules/cloud-monitor-alerts/main.tf` 中 `alicloud_cms_alarm.cms_alarms` 用 alarm map 的 key 作为实例身份；`shared/jfrog-cn.tf` 用 `count = var.jfrog_cn_oss_config != null ? 1 : 0` 选择创建零个或一个可选 OSS Bucket。以下本地实验用 `terraform_data` 承载 CMS 告警对象，只为观察 Terraform 地址和状态，不是生产 CMS 资源。

## 实验一：按 count 索引观察 CMS 告警对象

在 `~/terraform-labs/07-count/` 创建完整 `main.tf`。Terraform Core 内置 `terraform_data`，本实验不需要 Provider、不连接云。

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "cms_alarms" {
  description = "教学用 CMS 告警对象列表；不是生产阈值"
  type = list(object({
    key            = string
    namespace      = string
    metric         = string
    period         = number
    contact_groups = list(string)
  }))
  default = [
    { key = "cpu", namespace = "acs_ecs_dashboard", metric = "CPUUtilization", period = 60, contact_groups = ["ops"] },
    { key = "memory", namespace = "acs_ecs_dashboard", metric = "memory_usedutilization", period = 60, contact_groups = ["ops"] },
    { key = "disk", namespace = "acs_ecs_dashboard", metric = "diskusage_utilization", period = 60, contact_groups = ["ops"] },
  ]
}

resource "terraform_data" "cms_alarm" {
  count = length(var.cms_alarms)

  input            = var.cms_alarms[count.index]
  triggers_replace = var.cms_alarms[count.index].key
}

output "instances" {
  value = [
    for index, alarm in terraform_data.cms_alarm : {
      address = "terraform_data.cms_alarm[${index}]"
      key     = alarm.output.key
      period  = alarm.output.period
    }
  ]
}
```

按顺序运行并查看状态：

```bash
terraform init
terraform plan -out=count.tfplan
terraform show count.tfplan
terraform apply count.tfplan
terraform state list
terraform state show 'terraform_data.cms_alarm[1]'
terraform output instances
```

预期创建三个逻辑实例，`[0]`、`[1]`、`[2]` 分别对应 cpu、memory、disk。`triggers_replace` 只是让本地练习清楚显示 key 改变导致的替换，不代表 CMS Provider 的具体更新行为。

### 从中间删除 memory 会怎样

把 `cms_alarms` 列表改成只留 cpu 与 disk，再运行：

```bash
terraform plan -out=count-delete-middle.tfplan
terraform show count-delete-middle.tfplan
```

新列表的 `[1]` 变成 disk，旧 `[1]` 是 memory；旧 `[2]` 不再存在。由于本教学资源的 `triggers_replace` 绑定对象 key，计划会提出 `[1]` 替换并删除 `[2]`。这说明地址身份由索引决定，删除、插入或重排中间项可能导致后续地址指向不同对象。此时不要 apply；恢复原列表，再 plan 检查基线。

实际云资源会按 Provider schema 决定原地更新或替换，但 Terraform 地址仍然按索引匹配。若生产对象应由稳定业务 key 标识，map/`for_each` 通常更合适。

## 实验二：按 map key 管理同一组 CMS 告警

在独立目录 `~/terraform-labs/07-for-each/` 保存完整 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "cms_alarms" {
  description = "以稳定告警 key 标识的教学对象；不是生产告警配置"
  type = map(object({
    namespace      = string
    metric         = string
    period         = number
    contact_groups = list(string)
    enabled        = optional(bool, true)
  }))
  default = {
    cpu = {
      namespace = "acs_ecs_dashboard", metric = "CPUUtilization", period = 60, contact_groups = ["ops"]
    }
    memory = {
      namespace = "acs_ecs_dashboard", metric = "memory_usedutilization", period = 60, contact_groups = ["ops"]
    }
    disk = {
      namespace = "acs_ecs_dashboard", metric = "diskusage_utilization", period = 60, contact_groups = ["ops"]
    }
  }
}

locals {
  enabled_cms_alarms = {
    for key, alarm in var.cms_alarms : key => alarm if alarm.enabled
  }
}

resource "terraform_data" "cms_alarm" {
  for_each = local.enabled_cms_alarms
  input = {
    key            = each.key
    namespace      = each.value.namespace
    metric         = each.value.metric
    period         = each.value.period
    contact_groups = each.value.contact_groups
  }
}

output "instances" {
  value = {
    for key, alarm in terraform_data.cms_alarm : key => {
      address = "terraform_data.cms_alarm[${jsonencode(key)}]"
      period  = alarm.output.period
    }
  }
}
```

运行 init、plan、show、apply、state list，并用 `terraform state show 'terraform_data.cms_alarm["cpu"]'` 查看实例。预期 key 形成三个独立地址。

- 改 cpu 的 period：地址保持不变，只改变该逻辑资源的 input。
- 把 memory 的 `enabled` 改为 false：计划只移除 memory 实例。
- 删除 memory key：同样只移除该实例。
- 将 key `cpu` 改名为 `cpu_usage`：旧地址消失、新地址出现；若这只是逻辑改名，可用 `moved` 迁移状态地址。

此 `terraform_data` 包装只模拟地址和状态行为，不会创建 CMS alarm，也不能代替真实 Provider 的参数校验或行为。

## set(string) 的写法

当每个对象只有一个稳定 key、无需附加属性时，可给 `for_each` 一个字符串集合：

```hcl
variable "alarm_keys" {
  type    = set(string)
  default = ["cpu", "memory", "cpu"]
}

resource "terraform_data" "alarm_key" {
  for_each = var.alarm_keys
  input    = each.key
}
```

Set 不保留顺序并会去重，例中只得到 cpu 和 memory 两个实例。若每个告警还需 namespace、周期、指标和联系人组，应使用 map(object)。

## plan 时必须知道哪些值

`for_each` 的 map key 或 set 成员必须在 Terraform 开始远端资源操作前已知。可用已知的业务标识作为 key，把 apply 后才取得的 ID 放到 map value 中。不能用本轮 apply 才生成的 ID 决定本轮实例地址，也不应使用敏感值作为 key，因为地址会把 key 显示出来。

下面是概念性反例，不要并入上述实验：若 `terraform_data.bucket_id.id` 只有 apply 后才能确定，则 `for_each = toset([terraform_data.bucket_id.id])` 在同一轮计划不能确定集合成员。改为 `for_each = { bucket = terraform_data.bucket_id.id }` 后 key 是已知的 `bucket`，未知 ID 可以留在 value。

## 条件创建：0 或 1 个实例

生产来源：`shared/jfrog-cn.tf`（脱敏裁剪/教学改编）的可选 OSS Bucket 结构按输入对象是否为空选择 `count` 为 1 或 0。下面保留这一条件模式，但使用逻辑资源展示：

```hcl
variable "enable_cms_summary" {
  type    = bool
  default = false
}

resource "terraform_data" "cms_summary" {
  count = var.enable_cms_summary ? 1 : 0
  input = { enabled = true }
}
```

`count = 0` 时没有实例；设为 true 后地址为 `terraform_data.cms_summary[0]`。引用这类资源时要处理空列表。实际 OSS 示例与风险控制见 05 篇；不要把本地逻辑练习 apply 到生产 Bucket。

## 链式 for_each

如果两个资源集合一一对应且共享同一组 key，下游可以使用上游 map 作为 `for_each`，再按 `each.key` 读取上游属性。这样两个资源集合的身份保持一致。key 仍须事先可知；不要用上游创建后才产生的 ID 作为 key。

## dynamic 与 for_each 的区别

Resource/module 块上的 `for_each` 会创建有独立地址的实例。`dynamic` block 则生成 Provider schema 中资源内部可重复的嵌套块，没有单独 State 地址。

生产片段出处：`monitoring/modules/cloud-monitor-alerts/main.tf`。以下仅展示现有 CMS alarm resource 内一个可选 escalation block；它需要外层 `alicloud_cms_alarm` 与 `each.value` 输入上下文，不能单独运行：

```hcl
resource "alicloud_cms_alarm" "cms_alarms" {
  for_each = var.alarms != null ? var.alarms : {}

  dynamic "escalations_critical" {
    for_each = each.value.escalations_critical != null ? [each.value.escalations_critical] : []
    content {
      statistics          = escalations_critical.value.statistics
      comparison_operator = escalations_critical.value.comparison_operator
      threshold           = escalations_critical.value.threshold
      times               = escalations_critical.value.times
    }
  }
}
```

外层 map key 决定独立告警地址；dynamic block 决定这个告警资源中有零个或一个阈值子块。生产阈值与告警 key 未复用。

## 从 count 迁移到 for_each

应逐个把旧索引映射到代表同一个对象的新 key，例如：

```hcl
moved {
  from = terraform_data.cms_alarm[0]
  to   = terraform_data.cms_alarm["cpu"]
}
```

memory 与 disk 也各需一条对应映射。若在 count 实验原目录中替换成 map 配置，还应在新资源中保留 `triggers_replace = each.key`，使其值与旧实例中的 key 一致；移除或改变触发值本身也可能要求替换。先审阅计划，确认 Terraform 将原绑定迁到新地址，没有意外创建或删除。若资源实际属性也变化，Provider 仍可能提出更新或替换。CMS 实例要迁移时，目标地址必须匹配真实配置和 State，不能照抄这个本地教学地址。

## 清理两个实验

对 count 和 for_each 两个独立目录分别运行，并确认当前路径属于对应教学实验：

```bash
terraform plan -destroy -out=cleanup.tfplan
terraform show cleanup.tfplan
terraform apply cleanup.tfplan
terraform state list
```

预期仅清理本地 `terraform_data` 实例，无云资源被创建或删除。关闭实验前保留的计划文件可以删除；State 只属于各自教学目录。

## 练习

1. 在 count 实验中删除中间的 memory，列出旧、新索引分别对应的告警 key，并解释地址错位。
2. 在 for_each 实验中只修改一个 `period`，再停用 memory，比较计划的地址范围。
3. 说明什么时候用字符串集合、什么时候用 map(object)。
4. 为三个实例写完整 moved 映射，并说明资源输入改变仍可能导致更新。
5. 用 CMS dynamic 片段指出独立资源的地址由什么决定，嵌套阈值块由什么决定。

## 参考资料

- [count](https://developer.hashicorp.com/terraform/language/meta-arguments/count)
- [for_each](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
- [dynamic blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
- [for 表达式](https://developer.hashicorp.com/terraform/language/expressions/for)
- [moved 与模块重构](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [terraform_data](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
- [阿里云 CMS Alarm（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/cms_alarm)

上一篇：[[IaC/terraform/06_terraform_资源数据源与依赖|Resource、Data Source 与依赖]] · 下一篇：[[IaC/terraform/08_terraform_状态漂移与状态操作|State 与漂移]]。
