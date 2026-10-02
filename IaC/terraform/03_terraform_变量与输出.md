---
title: 03_terraform_变量与输出
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform变量
  - Terraform输入输出
---

# 03_terraform_变量与输出

## 输入、派生值与输出

| 写法 | 作用 | CMS 告警示例 |
|---|---|---|
| `variable` / `var.name` | 模块输入接口 | 告警名称、周期和联系人组 |
| `locals` / `local.name` | 模块内部派生值 | 补默认标签、过滤已启用告警 |
| `output` | 暴露模块结果 | 返回告警名称或对象 ID |

不要把每个内部计算结果都变成调用者输入。一个输入可以驱动多个内部值，模块输出则应只暴露调用者真正需要的接口。

## 完整离线实验：构造 CMS 告警输入

生产模块接受以名称为 key 的 `alarms` map，对每项声明 namespace、period、联系人组，并允许一些字段使用 optional 默认值。本实验保留 `map(object(...))` 以及 namespace、period 和联系人组字段，去掉 CMS Provider 和生产对象，用 `terraform_data` 检查并记录输入。`tags` 和标准标签合并是为演示表达式增加的教学字段，生产 CMS 告警接口不包含这个字段。整个实验不连接云端。

生产依据：`monitoring/modules/cloud-monitor-alerts/variables.tf` 中 `variable "alarms"`，以及 `monitoring/modules/cloud-monitor-alerts/main.tf` 中 `alicloud_cms_alarm.cms_alarms` 对 `each.value` 的读取。以下为脱敏裁剪、离线教学改编，不是可直接运行的 CMS 告警。

创建 `~/terraform-labs/03-cms-input/`，并放入下面四个文件。

### versions.tf

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}
```

### variables.tf

```hcl
variable "alarms" {
  description = "练习用的 CMS 风格告警输入"
  type = map(object({
    namespace      = string
    period         = number
    contact_groups = list(string)
    enabled        = optional(bool, true)
    metric         = optional(string, "")
    tags           = optional(map(string), {})
  }))
  default = {
    oss_capacity = {
      namespace      = "acs_oss"
      period         = 60
      contact_groups = ["<LAB_CONTACT_GROUP>"]
      tags           = { purpose = "terraform-lab" }
    }
  }

  validation {
    condition = alltrue([
      for alarm in values(var.alarms) :
      alarm.period > 0 && length(alarm.contact_groups) > 0
    ])
    error_message = "每条练习告警都必须有正数 period 和至少一个联系人组名称。"
  }
}
```

`<LAB_CONTACT_GROUP>` 是占位文本；这里仅练习输入类型，不会检查这个名字是否存在于阿里云。

### main.tf

```hcl
locals {
  effective_alarms = {
    for name, alarm in var.alarms : name => merge(alarm, {
      tags = merge(alarm.tags, {
        managed_by = "terraform"
        purpose    = "terraform-lab"
      })
    })
  }
}

resource "terraform_data" "alarm" {
  for_each = local.effective_alarms
  input    = each.value
}
```

`merge` 后面的标准标签覆盖调用者提供的同名标签。若要让调用者优先，应调换两个参数的顺序。

### outputs.tf

```hcl
output "effective_alarms" {
  description = "练习中经默认值和标准标签处理后的告警对象"
  value       = { for name, alarm in terraform_data.alarm : name => alarm.output }
}
```

### 运行与观察

```bash
cd ~/terraform-labs/03-cms-input
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform output effective_alarms
terraform console
```

计划应包含一个本地 `terraform_data.alarm["oss_capacity"]` 实例。Console 中可查询 `var.alarms.oss_capacity.period`。这仅是预期观察；文档作者没有在此执行该命令。实验结束后退出 console，再清理：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

## 根模块变量如何取得值

`variables.tf` 声明模块允许接收的输入；变量文件为本次运行赋值；`locals` 负责模块内部计算；`output` 是根模块结果或子模块接口。子模块要自行声明输入，再由父模块显式传值，子目录里的 tfvars 不会自动参与根模块运行。

本实验的 `lab.tfvars` 内容如下，键和值都对应前文已声明的 `alarms` 变量：

```hcl
alarms = {
  oss_capacity = {
    namespace      = "acs_oss"
    period         = 60
    contact_groups = ["<LAB_CONTACT_GROUP>"]
    tags           = { purpose = "terraform-lab" }
  }
}
```

读取文件并运行：

```bash
terraform plan -var-file=lab.tfvars -out=tfplan
```

优先级示例只覆盖已声明的 `alarms` 变量：

```bash
terraform plan -var-file=lab.tfvars -var='alarms={oss_capacity={namespace="acs_oss",period=120,contact_groups=["<LAB_CONTACT_GROUP>"],tags={purpose="terraform-cli"}}}'
```

本地 CLI 对同一个输入按以下顺序由低到高赋值，后面的值覆盖前面的值：

1. `variable` 的默认值。
2. `TF_VAR_<name>` 环境变量。
3. `terraform.tfvars`。
4. `terraform.tfvars.json`。
5. `*.auto.tfvars` 和 `*.auto.tfvars.json`，按完整文件名字典序加载。
6. 命令行 `-var` 和 `-var-file`，按参数出现顺序处理。

因此示例中的命令行 map 覆盖 `lab.tfvars` 里的 `alarms`。覆盖按完整变量进行，不会合并嵌套对象或 map 中的字段。显式命名的 `dev.tfvars`、`prod.tfvars` 不会自动加载；命令行也不适合放真实密码或 token，因为参数可能进入 shell 历史和进程列表。HCP Terraform/Enterprise 的 Workspace 变量和变量集另有平台优先级规则。

### 自动变量文件会整体替换同一 map

为了观察自动加载行为，把 `03-cms-input` 中的 `versions.tf`、`variables.tf`、`main.tf` 和 `outputs.tf` 复制到独立目录 `~/terraform-labs/03-variable-precedence`，再创建下面两个文件。

`10-first.auto.tfvars`：

```hcl
alarms = {
  oss_capacity = {
    namespace      = "acs_oss"
    period         = 60
    contact_groups = ["<LAB_CONTACT_GROUP>"]
    tags           = { purpose = "terraform-lab", owner = "first-file" }
  }
}
```

`20-second.auto.tfvars`：

```hcl
alarms = {
  oss_capacity = {
    namespace      = "acs_oss"
    period         = 120
    contact_groups = ["<LAB_CONTACT_GROUP>"]
    tags           = { purpose = "terraform-lab-override" }
  }
}
```

先在该目录运行 `terraform init`，再执行 `terraform console` 并查看 `var.alarms.oss_capacity`。第二份文件里的整个 `alarms` map 覆盖第一份；所以 `period` 是 120，`owner` 标签也不保留。若希望合并标签，需在 HCL 中显式用 `merge`，变量文件不会自动深度合并。

## object、nullable 与 optional 字段

生产 ECS 和 CMS 输入使用 `map(object(...))`，必需字段明确声明类型，次要字段使用 `optional` 默认值。下面的 period 校验示意保留了 CMS 输入形状：

```hcl
variable "alert" {
  description = "单条 CMS 风格告警输入"
  type = object({
    namespace      = string
    period         = number
    contact_groups = list(string)
    enabled        = optional(bool, true)
    tags           = optional(map(string), {})
  })
  nullable = false

  validation {
    condition     = var.alert.period > 0
    error_message = "告警 period 必须是正数。"
  }
}
```

有 `default` 的变量可以不传；没有 `default` 的变量必须提供。`nullable` 默认是 `true`，不能简单理解成“显式 null 一律报错”：

| 声明 | 不传值 | 显式传入 `null` |
|---|---|---|
| 有非 null 默认值，`nullable = true` | 使用默认值 | null 覆盖默认值 |
| 有非 null 默认值，`nullable = false` | 使用默认值 | 回退到默认值 |
| 无默认值，`nullable = true` | 提示输入；非交互运行时因缺值报错 | 变量值为 null |
| 无默认值，`nullable = false` | 提示输入；非交互运行时因缺值报错 | 报错，必需输入不能为 null |

可选对象属性从 Terraform 1.3 起稳定支持。`optional(bool, true)` 在字段缺省或显式为 null 时都使用 `true`；只写 `optional(bool)` 时，缺省值为 null。显式 object 类型转换会丢弃未声明的额外字段，因此拼错可选字段名可能让字段默默采用默认值。顶层 `nullable = false` 只约束整体值，不会自动禁止对象内部成员为 null。

`any` 是让 Terraform 推导具体类型的占位符，不是逃避接口设计的通用类型。优先声明真实的 `map(object(...))` 结构，让 Terraform 尽早指出缺少字段或类型不匹配。

### 跨变量校验的版本边界

本系列的最低 CLI 版本是 1.7。在 1.7 中，变量 `validation` 只能引用当前被校验变量；不能直接在 `maximum_period` 的 validation 中比较另一个变量。Terraform 1.9 起才允许变量校验引用其他变量和配置对象。下面是 **1.9+ 专用片段**，不要放入本系列 1.7 基线实验：

```hcl
variable "minimum_period" {
  type = number
}

variable "maximum_period" {
  type = number

  validation {
    condition     = var.maximum_period >= var.minimum_period
    error_message = "maximum_period 不能小于 minimum_period。"
  }
}
```

## sensitive：隐藏显示不等于不保存

以下使用假 webhook 值说明敏感输入与敏感 output 的声明方式；`.invalid` 是示例域名，不代表真实联系人或凭据。真实阿里云认证仍由第五篇介绍的 Provider/profile/环境凭据机制提供，不要自行建立 AK/SK 的 Terraform 输入变量。

```hcl
variable "lab_webhook" {
  description = "仅用于说明 sensitive 行为的假值"
  type        = string
  default     = "https://example.invalid/terraform-lab"
  sensitive   = true
}

output "lab_webhook" {
  value     = var.lab_webhook
  sensitive = true
}
```

如果 output 引用了敏感值，必须显式写 `sensitive = true`，否则 Terraform 会拒绝该配置。标记后，常规 plan/apply 和不带名称的 `terraform output` 会遮盖值，但 `terraform output lab_webhook`、`-raw` 或 `-json` 仍可能显示明文。`sensitive` 不是加密，也不保证值不会写入 State 或保存的 Plan；真实凭据不要用于输出演示，State 和 Plan 也需要访问控制。

“敏感”和“未知”是两件事：敏感性控制展示，unknown 表示 plan 时尚不知道具体值。一个值可以既敏感又已知，也可以既敏感又未知；`try` 不会把 unknown 资源 ID 转换成已知默认值。

Terraform 1.10+ 增加 ephemeral 变量/子模块 output；Terraform 1.11+ 对 Provider 支持的 write-only 参数增加不持久化能力。这些功能有使用位置限制，本系列 1.7 基线没有使用。单独加 `sensitive` 不会获得不持久化效果。

## 换变量文件不等于换环境

```bash
terraform plan -var-file=prod.tfvars
```

只换变量文件不会自动换 Backend、Workspace、Provider 凭据或 State。若仍使用同一状态，这条命令可能计划修改现有对象。环境隔离还要设计独立状态位置和权限，见 [[IaC/terraform/09_terraform_后端工作空间与多环境|Backend 与多环境]]。

## 常见问题与练习

- tfvars 不能声明变量；当前模块必须先定义 `variable`。
- 子模块不会自动读取自己的 tfvars，由父模块传值。
- 输入值被覆盖时，依次检查环境变量、自动变量文件和命令行赋值。
- 给实验增加 `severity`，限制为 `CRITICAL`、`WARNING` 或 `INFO`；尝试一个非法值，观察 validation。
- 按本节建立两个自动变量文件，检查后加载的 `alarms` 整体替换结果，并说明第一份 map 中 `owner` 标签为何消失。

## 参考资料

- [输入变量与优先级](https://developer.hashicorp.com/terraform/language/values/variables)
- [Terraform 1.7 nullable 语义](https://developer.hashicorp.com/terraform/language/v1.7.x/values/variables#disallowing-null-input-values)
- [Terraform 1.9 变量校验边界](https://developer.hashicorp.com/terraform/language/v1.9.x/expressions/custom-conditions#input-variable-validation)
- [可选对象属性](https://developer.hashicorp.com/terraform/language/expressions/type-constraints#optional-object-type-attributes)
- [本地值](https://developer.hashicorp.com/terraform/language/values/locals)
- [输出值](https://developer.hashicorp.com/terraform/language/values/outputs)
- [敏感数据处理](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)
- [阿里云 Terraform 认证方式](https://help.aliyun.com/en/terraform/terraform-authentication)
- 生产依据：`monitoring/modules/cloud-monitor-alerts/variables.tf`、`monitoring/modules/cloud-monitor-alerts/main.tf` 与 `shared/ecs.tf`（脱敏裁剪、离线教学改编）

上一篇：[[IaC/terraform/02_terraform_配置语法与文件结构|HCL 语法]] · 下一篇：[[IaC/terraform/04_terraform_表达式函数与模板|表达式、函数与模板]]。
