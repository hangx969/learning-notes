---
title: Terraform基础-count与for_each
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform批量资源
  - Terraform for_each
---

# Terraform基础-count与for_each

## 为什么需要批量创建

多个同类资源如果只复制粘贴，命名、标签和参数容易不一致。Terraform 通过 `count` 或 `for_each` 让一个 resource/module 块对应多个实例。

选择它们之前先考虑资源身份：一个实例是“第几个”，还是“哪一个服务”？这决定输入列表变化后，Terraform 会认为谁发生了变化。

| 比较项 | count | for_each |
|---|---|---|
| 输入 | 非负整数 | map 或 set(string) |
| 实例身份 | 从 0 开始的索引 | map key 或 set 成员 |
| 循环内引用 | `count.index` | `each.key`、`each.value` |
| 地址 | `local_file.app[0]` | `local_file.app["web"]` |
| 常见用途 | 固定数量、0/1 条件创建 | 按服务名、用户、区域等稳定 key 管理 |

同一个块不能同时使用 count 和 for_each。二者通常必须在 plan 阶段就能确定实例数量或 key。

## 实验一：用 count 管理三份配置

新建 `~/terraform-labs/07-count`，完整 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

variable "service_names" {
  type    = list(string)
  default = ["web", "api", "worker"]
}

resource "local_file" "config" {
  count = length(var.service_names)

  filename        = "${path.module}/${var.service_names[count.index]}.conf"
  content         = "service=${var.service_names[count.index]}\n"
  file_permission = "0644"
}

output "paths" {
  value = local_file.config[*].filename
}
```

初始化并查看计划后执行。State 中预期有以下三个地址：

```text
local_file.config[0]  -> web.conf
local_file.config[1]  -> api.conf
local_file.config[2]  -> worker.conf
```

### 从中间删除 api 会怎样

把默认列表改为：

```hcl
default = ["web", "worker"]
```

此时 `[1]` 的目标由 api 变成 worker，原来 `[2]` 不再有配置：

```text
[0] web    -> web
[1] api    -> worker
[2] worker -> 不存在
```

Provider 会决定这些参数变化是更新还是替换。核心问题是实例身份按索引对应；中间删除、插入或重新排序都可能影响后续实例。

本地文件例子可能还出现不同实例试图处理同一路径的风险。先阅读计划，不要把该迁移当作生产资源的安全缩容步骤。

## 实验二：用 for_each 保持服务身份

使用独立的 `~/terraform-labs/07-for-each` 目录，沿用上面的 Local Provider 声明。以下内容构成其余完整配置，不与 count 实验追加合并。

```hcl
variable "services" {
  description = "以服务名作为稳定实例 key"
  type = map(object({
    port    = number
    enabled = optional(bool, true)
  }))
  default = {
    web    = { port = 8080 }
    api    = { port = 9000 }
    worker = { port = 7000 }
  }
}

locals {
  enabled_services = {
    for name, service in var.services : name => service
    if service.enabled
  }
}

resource "local_file" "config" {
  for_each = local.enabled_services

  filename        = "${path.module}/${each.key}.conf"
  file_permission = "0644"
  content         = <<-EOT
    service=${each.key}
    port=${each.value.port}
  EOT
}

output "paths" {
  value = {
    for name, config in local_file.config : name => config.filename
  }
}
```

实验步骤：

```bash
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform state list
terraform state show 'local_file.config["web"]'
```

State 中的资源身份为：

```text
local_file.config["web"]
local_file.config["api"]
local_file.config["worker"]
```

从 map 中删除 `api`，或把它的 enabled 改为 false，再 plan，预期只移除 api 实例，web/worker 不会因为排序改变而获得别的身份。

### 修改 key 和修改 value

- 把 web 的 port 改成 `8081`：web 地址不变，属性按 Provider 规则变更。
- 把 key 从 web 改成 frontend：旧 web 地址消失，新 frontend 地址出现；普通计划会提出删除旧实例、创建新实例。
- 需要保留地址绑定时，应使用 `moved`，而不是把 key 改名当成普通参数更新。

云资源也一样：key 不是随便改的显示标题，它是资源地址的一部分。

## set(string) 的写法

```hcl
variable "names" {
  type    = set(string)
  default = ["web", "api", "web"]
}

resource "terraform_data" "service" {
  for_each = var.names
  input    = each.key
}
```

这是独立示例，不需要 Local Provider。set 会去重，不保证顺序；这里 `each.key` 和 `each.value` 是同一个成员值。

不能直接把一个 list 当成 for_each 输入。明确使用 `toset` 转换，并确认去重和顺序丢失符合意图；复杂对象集合通常应整理成 map。

## plan 时必须知道哪些值

for_each 的 key 必须已知；value 中的某些资源属性可以在 apply 时才知道。

```hcl
# 反例片段：新建资源的 ID 在 plan 时未知，不适合做实例 key
resource "terraform_data" "bad" {
  for_each = toset([terraform_data.created.id])
  input    = each.value
}
```

即使声明了 `terraform_data.created`，上面仍可能因新 ID 未知而失败。应该用调用者提供的稳定逻辑 key，把未知的 ID 放在 value 中。

敏感值不能作为 for_each 实例身份，因为 key 会出现在地址和日志里。也不要用 `timestamp`、`uuid` 等变化值生成实例 key。

count 的数量也不能依赖一个新资源 apply 后才获得的未知数量。

## 条件创建：0 或 1 个实例

下面是独立示例：

```hcl
variable "enabled" {
  type    = bool
  default = false
}

resource "terraform_data" "optional" {
  count = var.enabled ? 1 : 0
  input = "optional feature"
}

output "optional_value" {
  value = one(terraform_data.optional[*].output)
}
```

数量为 0 时不能无条件读取 `[0]`。本例 `one` 在零个元素时返回 null，在一个元素时返回该值；超过一个元素会报错。

可选资源并不只是“设置上游变量为 false”；关闭开关可能删除已经存在的实例，应审查删除计划。

## 链式 for_each

在 map 实验中，可以补充下面的资源：

```hcl
resource "terraform_data" "summary" {
  for_each = local_file.config
  input    = each.value.filename
}
```

资源 map 的 key 已由输入服务名确定，因此下游可以按同样的 key 创建逻辑节点，引用则自然建立依赖。

父子模块批量创建时也可用 module 的 for_each：`module.app["web"].file_path`。子模块的 Provider 结构必须兼容此用法，见 [[IaC/terraform/terraform-modules|模块开发]]。

## dynamic 与 for_each 的区别

| 写法 | 增加的是什么 | 身份表现 |
|---|---|---|
| resource/module 上的 `for_each` | 多个资源或模块实例 | State 有多个独立地址 |
| resource 内的 `dynamic` | 同一个资源中的重复嵌套块 | 通常仍是一个资源地址 |
| 普通 for 表达式 | 一个计算后的集合值 | 本身不创建资源 |

增加三条网络规则和创建三个网络资源是不同的模型，先查 schema，再决定用哪种写法。

## 从 count 迁移到 for_each

已经 apply 的资源不能只改语法。需要为旧索引和新 key 明确建立映射，例如：

```hcl
moved {
  from = local_file.config[0]
  to   = local_file.config["web"]
}
```

为每个保留的实例建立正确映射，并同时保持真实资源参数一致。`moved` 解决地址变化，不会取消属性变化本来要求的替换。

完整流程见 [[IaC/terraform/terraform-import-refactoring|导入与重构]]。

## 练习

1. 在 count 实验中交换 web/api 的顺序，只看计划并解释结果。
2. 在 for_each 实验中交换 map 的书写顺序，比较资源地址。
3. 将 worker 关闭，确认计划的移除范围；再恢复它观察创建计划。
4. 根据 map 生成服务名到文件路径的 output，避免用错误的 `[*]` 读取 map。

## 参考资料

- [count](https://developer.hashicorp.com/terraform/language/meta-arguments/count)
- [for_each](https://developer.hashicorp.com/terraform/language/meta-arguments/for_each)
- [Splat expressions](https://developer.hashicorp.com/terraform/language/expressions/splat)
- [one 函数](https://developer.hashicorp.com/terraform/language/functions/one)
- [模块重构与 moved](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)

上一篇：[[IaC/terraform/terraform-resources-dependencies|资源与依赖]] · 下一篇：[[IaC/terraform/terraform-state|State 与漂移]]。
