---
title: 02_terraform_配置语法与文件结构
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform HCL
  - Terraform配置语法
---

# 02_terraform_配置语法与文件结构

## HCL 的基本结构

Terraform 配置通常放在 `.tf` 文件中。读 HCL 时，先辨认块类型、标签和参数：

```hcl
resource "terraform_data" "alarm_input" {
  input = {
    name      = "oss-capacity-lab"
    namespace = "acs_oss"
    period    = 60
  }
}
```

- `resource` 是块类型；`"terraform_data"` 和 `"alarm_input"` 是两个标签。
- `input = { ... }` 是对象值赋给参数。
- 参数接受的类型与嵌套结构取决于 Terraform 语言或对应 Provider 的 schema。

比较参数对象和嵌套块：

```hcl
resource "terraform_data" "demo" {
  input = {
    name = "demo"
  }

  lifecycle {
    prevent_destroy = true
  }
}
```

`input` 是参数赋值，`lifecycle` 是嵌套块，没有等号。判断某资源字段该写成对象还是块，应查该资源版本的 schema。

## 常见顶层块

| 块 | 作用 | 例子 |
|---|---|---|
| `terraform` | CLI 版本、Provider 要求、Backend | `required_version` |
| `provider` | 配置一次平台连接 | `provider "alicloud"` |
| `resource` | 管理对象生命周期 | `alicloud_cms_alarm` |
| `data` | 查询已有对象 | `data "alicloud_vpcs"` |
| `variable` | 声明模块输入 | `variable "alarms"` |
| `locals` | 计算可复用值 | 标签或派生告警参数 |
| `output` | 暴露模块结果 | OSS Bucket 名称 |
| `module` | 调用子模块 | CMS 告警模块 |
| `import` / `moved` / `removed` | 管理对象地址或退出管理 | State 迁移 |
| `check` | 持续检查配置对象或资源属性 | 失败通常报告 warning，不强制阻断 plan/apply |

## 基本值与集合类型

```hcl
locals {
  alarm_names = ["oss-capacity", "ack-pod-count"]
  severities  = toset(["WARNING", "CRITICAL", "WARNING"])
  common_tags = { owner = "platform", purpose = "terraform-lab" }
  alert = {
    namespace = "acs_oss"
    period    = 60
    enabled   = true
  }
}
```

| 类型 | 特征 | 类型约束 |
|---|---|---|
| list | 有序、可重复 | `list(string)` |
| set | 不承诺顺序、去重 | `set(string)` |
| map | 字符串 key，元素类型一致 | `map(string)` |
| object | 命名字段可有不同类型 | `object({ period = number })` |
| tuple | 固定位置，可有不同类型 | `tuple([string, number])` |

字面量的外观不一定就是最终集合类型，Terraform 会结合上下文推导或转换。Map/object 适合稳定命名的配置；list 适合有顺序的数据；set 适合不重复集合。

`null` 是已知的无值；unknown 是当前阶段尚不能确定的值，例如 apply 后才生成的资源 ID。二者都不同于空字符串、空列表和空对象。

## 引用、注释与模板

| 对象 | 引用 |
|---|---|
| 输入变量 | `var.region` |
| 本地值 | `local.common_tags` |
| 资源属性 | `alicloud_oss_bucket.lab.bucket` |
| Data Source 属性 | `data.alicloud_oss_buckets.existing.buckets` |
| 子模块输出 | `module.lab_contacts.group_names`（见[[IaC/terraform/10_terraform_模块开发与复用\|第 10 篇]]） |
| `count` 实例 | `alicloud_cms_alarm.example[0].id` |
| `for_each` 实例 | `alicloud_cms_alarm.example["oss"].id` |
| 当前 CLI Workspace 名 | `terraform.workspace` |

直接需要一个值时直接引用；拼接文字时再用插值：

```hcl
variable "region" {
  type = string
}

locals {
  bucket_label = "terraform-lab-${var.region}"
}
```

HCL 支持 `#`、`//` 单行注释和 `/* ... */` 多行注释。`<<-EOT` 可用于 heredoc；`${...}` 会触发插值，字面量插值符号写成 `$${...}`。生成 JSON/YAML 时优先使用 `jsonencode` / `yamlencode`。

## 一个项目中的文件

```text
example/
├── versions.tf
├── providers.tf
├── variables.tf
├── main.tf
├── outputs.tf
├── terraform.tfvars
└── modules/
    └── alerts/
```

同一目录的 `.tf` 和 `.tf.json` 合并成一个模块。文件拆分是组织约定，不代表执行顺序。子目录需由 `module` 块调用，`.tfvars` 提供输入值，不放资源定义。`.terraform.lock.hcl` 记录 Provider 选择，不是普通配置文件。Terraform 还识别 `override.tf` / `*_override.tf` 覆盖文件、`*.tftest.hcl` 测试文件和 `*.tfbackend` 后端参数文件；入门项目通常不需要用 override 文件隐藏配置差异。

生产依据：`shared/versions.tf`、`shared/providers.tf`、`shared/jfrog-cn.tf`、`monitoring/modules/cloud-monitor-alerts/variables.tf` 和 `monitoring/modules/cloud-monitor-alerts/main.tf`。正文示例做了脱敏裁剪，保留 provider、模块和 CMS 输入的块结构；没有复制真实账号、模块源地址或业务标识。

## 离线语法练习

创建完整 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

locals {
  alarms = {
    oss = { namespace = "acs_oss", period = 60, enabled = true }
    ack = { namespace = "acs_ack", period = 120, enabled = false }
  }
}

output "oss_period" {
  value = local.alarms["oss"].period
}
```

运行 Terraform Console 观察值和类型：

```bash
terraform console
```

```text
> local.alarms.oss.period
60
> type(local.alarms)
> exit
```

这是本地表达式练习，不要求 Provider 或云凭据。若目录使用远程 Backend，console 也会受到该 Backend 配置影响。

## 常见错误

- `Missing newline after argument`：检查块参数换行和大括号层级；对象成员与块参数写法不同。
- `Reference to undeclared input variable`：当前模块未声明所引用的变量。
- `Reference to undeclared resource`：资源标签或模块层级写错。
- 把嵌套块误写成对象，或反过来：检查该字段的 schema。
- 在 `.tfvars` 中写 `var.period = 60`：赋值文件应使用 `period = 60`。

## 练习

1. 把 `locals` 移入 `locals.tf`，确认同目录文件仍组成同一模块。
2. 把 `enabled` 改为字符串 `"false"`，观察布尔值和字符串的类型差异。
3. 加一个 `output` 暴露 ACK 告警的 `namespace`。

## 参考资料

- [Terraform 配置语法](https://developer.hashicorp.com/terraform/language/syntax/configuration)
- [类型约束](https://developer.hashicorp.com/terraform/language/expressions/type-constraints)
- [引用](https://developer.hashicorp.com/terraform/language/expressions/references)
- [文件与目录结构](https://developer.hashicorp.com/terraform/language/files)
- 生产依据：`monitoring/modules/cloud-monitor-alerts/variables.tf`、`monitoring/modules/cloud-monitor-alerts/main.tf`（脱敏裁剪、离线教学改编）

上一篇：[[IaC/terraform/01_terraform_基础概念与第一个项目|基础概念与第一个项目]] · 下一篇：[[IaC/terraform/03_terraform_变量与输出|变量与输出]]。
