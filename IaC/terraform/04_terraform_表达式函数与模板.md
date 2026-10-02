---
title: 04_terraform_表达式函数与模板
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform表达式
  - Terraform函数与模板
---

# 04_terraform_表达式函数与模板

## 表达式的用途

Terraform 表达式从变量和已有配置计算值，可用于命名、过滤告警、合并标签或整理模块输入。表达式不是顺序执行的 Shell 循环；资源批量实例由 `count` 或 `for_each` 创建。

本篇离线实验中的 `map(object)`、可选字段、`for_each`、动态 escalation 块和 CMS dimensions 的 `jsonencode` 取自生产告警模块；策略处理中的 `merge` 与 `jsonencode` 时间条件来自临时授权配置。示例均经脱敏裁剪并改成离线 `terraform_data`，不调用 CMS 或 RAM API。

生产依据：`monitoring/modules/cloud-monitor-alerts/variables.tf`、`monitoring/modules/cloud-monitor-alerts/main.tf` 和 `permissions/temporary-access.tf`。下方告警标签的 `merge` 是为练习覆盖顺序而做的教学改编。

## 条件表达式

```hcl
variable "environment" {
  type = string
}

variable "enabled" {
  type = bool
}

locals {
  silence_time = var.environment == "prod" ? 3600 : 300
  bad_value    = var.enabled ? 3 : "disabled"
}
```

结构是“条件 ? 条件成立时的值 : 否则的值”。两侧应具有相同或可统一的类型。上例 `bad_value` 会让 Terraform 把数字转换成字符串，启用时得到 `"3"`，不是 number；应把启用状态和数值分成两个字段。条件和逻辑运算也不能用来掩盖不安全的 null 属性访问；先判断整个对象是否存在。

## for 表达式：筛选和转换告警 map

```hcl
locals {
  alarms = {
    oss = { namespace = "acs_oss", enabled = true, period = 60 }
    ack = { namespace = "acs_ack", enabled = false, period = 60 }
  }

  enabled_alarms = {
    for name, alarm in local.alarms : name => alarm
    if alarm.enabled
  }

  alarm_labels = {
    for name, alarm in local.enabled_alarms : name => "${name}:${alarm.namespace}"
  }
}
```

方括号形式产出序列；大括号形式产出对象，`=>` 左边为 key，右边为 value；`if` 在输出前过滤成员。从 map/object 遍历时有确定的排序规则，但不能让 set 顺序承担业务含义。

若一个 key 对应多个结果，可用分组模式：

```hcl
locals {
  alarms_by_namespace = {
    for name, alarm in local.alarms : alarm.namespace => name...
  }
}
```

末尾的 `...` 让同一 namespace 收集多个告警名称。只有确实要分组时才使用；原本应唯一的 key 重复，仍应修正输入。

## 常用函数与覆盖规则

| 函数 | 用途 |
|---|---|
| `lower` / `trimspace` | 规范字符串 |
| `format` / `join` | 组合文本 |
| `length` / `contains` | 检查集合 |
| `toset` / `tomap` | 明确转换类型 |
| `merge` | 合并 map/object，后者覆盖同名 key |
| `lookup` | 读取 map key 并为缺少的 key 提供默认值 |
| `try` / `can` | 处理动态求值错误或测试能否求值 |
| `flatten` | 展平嵌套序列 |
| `jsonencode` / `yamlencode` | 从结构化值生成文本 |
| `file` / `templatefile` | 读取运行开始前已存在的文件或模板 |

`try` 不会修复语法错误或未声明资源，也不会把 unknown 当成错误：参数中含计划阶段未知的资源属性时，结果通常仍是 unknown。`lookup` 只在 key 缺失时使用默认值；key 存在但值为 null 时，不会回退到默认值。`merge` 是浅合并：

```hcl
locals {
  merged = merge(
    { alert = { period = 60, enabled = true } },
    { alert = { period = 120 } }
  )
}
```

第二个 `alert` 对象整体覆盖第一个，不会保留 `enabled`。需要多层合并时，要按层显式调用 `merge` 并确定字段优先级。

## 离线实验：整理 CMS 告警输入

新建独立目录 `~/terraform-labs/04-cms-expressions`，并创建以下完整 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "alarms" {
  type = map(object({
    namespace         = string
    period            = number
    enabled           = optional(bool, true)
    contact_groups    = list(string)
    metric_dimensions = optional(string, null)
    escalations_warn = optional(object({
      comparison_operator = string
      statistics          = string
      threshold           = string
      times               = number
    }))
    tags = optional(map(string), {})
  }))
  default = {
    oss_capacity = {
      namespace      = "acs_oss"
      period         = 60
      contact_groups = ["<LAB_CONTACT_GROUP>"]
      escalations_warn = {
        comparison_operator = ">="
        statistics          = "Average"
        threshold           = "80"
        times               = 2
      }
      tags = { purpose = "terraform-lab" }
    }
    ack_pods = {
      namespace      = "acs_ack"
      period         = 60
      contact_groups = ["<LAB_CONTACT_GROUP>"]
      enabled        = false
    }
  }
}

locals {
  active_alarms = {
    for name, alarm in var.alarms : name => merge(alarm, {
      tags = merge(alarm.tags, { managed_by = "terraform-lab" })
    }) if alarm.enabled
  }

  alarm_documents = {
    for name, alarm in local.active_alarms : name => jsonencode({
      name           = name
      namespace      = alarm.namespace
      period         = alarm.period
      contact_groups = alarm.contact_groups
      tags           = alarm.tags
    })
  }
}

resource "terraform_data" "alarm" {
  for_each = local.active_alarms
  input    = each.value
}

output "alarm_documents" {
  value = local.alarm_documents
}
```

替换 `<LAB_CONTACT_GROUP>` 不是运行要求，因为此处不连接阿里云；字符串只是占位值。运行并观察：

```bash
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform output alarm_documents
terraform console
```

输出 JSON 应只包含 `oss_capacity`；ack 告警被过滤。Console 中可以检查 `local.active_alarms` 与 `local.alarm_documents`。以上是预期结果，文章没有实际执行这组命令。完成后退出 console，并清理本地 State：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

## templatefile：离线渲染一条 OSS 策略语句

生产临时授权配置从已经存在的策略 JSON 文件读取 `Statement`，再合并有效期条件。本实验只练习从既存模板渲染和解析 JSON，不含生产策略、Condition、RAM 资源或云端操作。它完整使用 `templatefile`、`jsondecode`、输出和清理流程。依据为 `permissions/temporary-access.tf` 中 `file()` 与 `jsondecode()` 组成的读取链；以下是脱敏改编。

创建独立目录 `~/terraform-labs/04-policy-template`。先创建 `policy.json.tftpl`：

```text
${jsonencode({
  Version = "1"
  Statement = [
    {
      Effect   = "Allow"
      Action   = ["oss:ListObjects"]
      Resource = ["acs:oss:*:*:${bucket_name}"]
    }
  ]
})}
```

再创建完整 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "bucket_name" {
  type    = string
  default = "<YOUR_LAB_BUCKET>"
}

locals {
  policy = jsondecode(templatefile("${path.module}/policy.json.tftpl", {
    bucket_name = var.bucket_name
  }))
}

resource "terraform_data" "policy" {
  input = local.policy

  lifecycle {
    precondition {
      condition = (
        length(local.policy.Statement) > 0 &&
        alltrue([for statement in local.policy.Statement : statement.Effect == "Allow"])
      )
      error_message = "练习只接受至少一条 Allow 语句。"
    }
  }
}

output "rendered_policy" {
  value = terraform_data.policy.output
}
```

模板和配置文件都准备好后运行：

```bash
cd ~/terraform-labs/04-policy-template
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform output rendered_policy
```

`<YOUR_LAB_BUCKET>` 在此只是渲染出的示意字符串，不需要替换成真实 Bucket，因为没有资源连接或 API 调用。改变它会改变本地 `terraform_data` 输入。结束后清理：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

`templatefile` 只读取 Terraform 开始运行前已存在的模板文件；增加 `depends_on` 不会让它等待某个资源生成模板。

## dynamic：生成 Provider 支持的重复块

生产 CMS 资源在 escalation 对象非 null 时才生成嵌套块，结构如下。它是针对实际 `alicloud_cms_alarm` 的脱敏片段，不属于上面的离线实验；没有合适 Provider 与输入时不要单独执行。

```hcl
dynamic "escalations_warn" {
  for_each = each.value.escalations_warn != null ? [each.value.escalations_warn] : []

  content {
    statistics          = escalations_warn.value.statistics
    comparison_operator = escalations_warn.value.comparison_operator
    threshold           = escalations_warn.value.threshold
    times               = escalations_warn.value.times
  }
}
```

`dynamic` 的 label 是目标 schema 中的块名，`content` 描述每个块的内容。它只能生成 Provider schema 已支持的嵌套块，不能凭空添加字段，也不能生成需要先处理的 `lifecycle` 或 `provisioner` 元参数块。只有一个固定块时，直接写块更容易读。

## JSON、模板和文件读取

策略、告警输入等结构化值可用 `jsonencode` 生成 JSON，避免手工维护引号和逗号。需要保留文本布局时再用 `templatefile`。模板变量必须通过其第二个参数显式传入；模板和 `file()` 读取的文件必须在 Terraform 开始运行前已存在。它们不是资源依赖图中的文件生成动作，增加 `depends_on` 也不会改变这一点。

## 练习与常见问题

1. 给实验增加一个标签，并调整 `merge` 参数顺序，使调用方覆盖或由内部标签覆盖。
2. 从告警 map 生成按 namespace 分组的名称集合。
3. 取消 `enabled` 默认值，观察调用方必须提供的字段变化。

常见错误包括 for 表达式产生重复 key、条件两侧类型不一致、把嵌套对象误当递归 merge，以及模板路径相对目录写错。`timestamp()` 每次求值都会变化，`uuid()` 也不适合直接充当持久身份；把它们放进普通资源参数可能让每次 plan 都不同。需要稳定随机值时使用对应 Provider 资源。

## 参考资料

- [条件表达式](https://developer.hashicorp.com/terraform/language/expressions/conditionals)
- [for 表达式与分组](https://developer.hashicorp.com/terraform/language/expressions/for)
- [函数索引](https://developer.hashicorp.com/terraform/language/functions)
- [templatefile](https://developer.hashicorp.com/terraform/language/functions/templatefile)
- [jsonencode](https://developer.hashicorp.com/terraform/language/functions/jsonencode)
- [dynamic blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
- 生产依据：`monitoring/modules/cloud-monitor-alerts/variables.tf`、`monitoring/modules/cloud-monitor-alerts/main.tf` 与 `permissions/temporary-access.tf`（来源关系见正文；脱敏裁剪、离线教学改编）

上一篇：[[IaC/terraform/03_terraform_变量与输出|变量与输出]] · 下一篇：[[IaC/terraform/05_terraform_提供者版本与认证|Provider、版本与认证]]。
