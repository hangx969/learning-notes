---
title: 06_terraform_资源数据源与依赖
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform资源依赖
  - Terraform生命周期
---

# 06_terraform_资源数据源与依赖

## Resource 表示管理所有权

`resource` 声明让 Terraform 通过 Provider 管理对象的生命周期。创建、更新、替换和删除由配置、State 与 Provider 共同决定。`alicloud_cms_alarm_contact.contacts["ops"]` 是 Terraform 地址；CMS 中真实联系人的 ID 由 Provider 记录到 State。仅写一个和现存对象同名的 resource，不会自动纳管该对象。

生产代码出处：`monitoring/modules/cloud-monitor-alerts/main.tf`（脱敏裁剪/教学改编）以 map key 管理联系人、联系人组和告警实例；联系人信息与生产业务 key 已替换。

## Data Source 表示查询

`data` 块查询 Provider 支持读取的对象，并把返回值交给其他配置使用。查询结果不是 resource 的所有权绑定；删除 data 块不会因此删除被查询对象。各 Data Source 的读取内容与时机由 Provider 实现。

生产代码出处：`tool/data.tf`（脱敏裁剪/教学改编）使用 `data "alicloud_account" "current" {}` 读取当前账号 ID；`monitoring/cloud-monitor-alert.tf` 使用 EIP 与 NAT Gateway Data Source 查询监控目标。它们都只查询对象，不声明被查账号或实例的生命周期。

## 资源参数与导出属性

- 参数是 Terraform 传入的值，例如联系人组名称、告警周期或 Bucket 标签。
- 导出属性由 Provider 读回或计算，例如资源 ID、创建时间或 endpoint。
- 有些参数会被服务端规范化。能否更新或是否替换对象，要查对应 Provider 版本的资源文档并审阅计划。

## 完整实验：查询当前账号

此独立实验只调用 `alicloud_account` Data Source，不创建或修改云资源。使用具有只读账号查询权限的教学凭证；认证信息从 Provider 推荐的受控环境变量或 credentials profile 提供，不写入 Terraform 文件。创建 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "= 1.266.0"
    }
  }
}

variable "region" {
  type = string
}

provider "alicloud" {
  region = var.region
}

data "alicloud_account" "current" {}

output "current_account_id" {
  value = data.alicloud_account.current.id
}
```

在同一实验目录创建 `lab.tfvars`，将占位符换成自己有权使用的地域：

```hcl
region = "<YOUR_REGION>"
```

凭证仍由受控环境或 profile 提供，变量文件只设置地域。按顺序观察：

```bash
terraform init
terraform plan -var-file=lab.tfvars -out=account.tfplan
terraform show account.tfplan
terraform apply account.tfplan
terraform output current_account_id
terraform state list
```

Data Source 在计划时读取当前账号信息；输出是 Provider 返回的账号 ID。State 可记录查询结果，但这不表示 Terraform 创建或拥有该账号。此目录没有待销毁的云资源，完成后可归档或删除实验文件和本地状态。生产中的只读查询示例见 `tool/data.tf`。

如需对比 Resource 管理，请继续第 05 篇在独立账号创建的空 OSS Bucket 与 ACL 实验。Bucket 是显式 resource，拥有独立 State 地址；账号 Data Source 只读取账号信息。不要把生产 OSS Bucket 当练习目标。

## 生产数据流：Data Source、过滤与模块输入

生产代码将不同地域查询到的 EIP 列表合并，按配置的排除标签过滤 ID，再把结果传给告警子模块。以下以 `monitoring/cloud-monitor-alert.tf` 为基础做脱敏裁剪/教学改编；region/provider aliases 减至两个教学 alias，必要输入变量接口在片段中展示，其他地域与完整 resource object 字段省略，不能单独复制运行：

```hcl
data "alicloud_eip_addresses" "network_cn_shanghai" {
  provider = alicloud.network_cn_shanghai
}

data "alicloud_eip_addresses" "network_cn_hongkong" {
  provider = alicloud.network_cn_hongkong
}

variable "account_alert_contacts_base" {
  description = "教学接口形状；详细对象字段见生产 monitoring/cloud-monitor-alert.tf"
  type = object({
    contacts       = map(any)
    contact_groups = map(any)
  })
}

variable "account_alarms" {
  description = "按账户区分排除标签和告警输入；省略生产对象的完整字段结构"
  type = map(object({
    exclude_tags = optional(map(string), {})
    alarms       = map(any)
  }))
}

locals {
  all_eips = concat(
    data.alicloud_eip_addresses.network_cn_shanghai.addresses,
    data.alicloud_eip_addresses.network_cn_hongkong.addresses,
  )

  filtered_eip_ids = [
    for eip in local.all_eips : eip.id
    if length([
      for key, value in var.account_alarms["network"].exclude_tags : key
      if try(eip.tags[key], null) == value
    ]) == 0
  ]
}

module "network_alerts" {
  source           = "./modules/cloud-monitor-alerts"
  contacts         = var.account_alert_contacts_base.contacts
  contact_groups   = var.account_alert_contacts_base.contact_groups
  alarms           = var.account_alarms["network"].alarms
  eip_instance_ids = local.filtered_eip_ids
}
```

上例中 `exclude_tags` 是 `map(string)`，`contacts`、`contact_groups` 与 `alarms` 的类型见子模块 `monitoring/modules/cloud-monitor-alerts/variables.tf`。Data Source 读取对象，`local` 只转换返回值，module 调用将值传入子模块；这些步骤本身不把 EIP 纳入 Terraform 管理。

生产代码使用多个 Provider alias 跨账户和地域查询。Data Source 列表的具体成员取决于运行身份、alias 与云端当前数据，不能仅凭源码推断当前查询结果。确切代码位置：`monitoring/cloud-monitor-alert.tf`。

## CMS 联系人到告警的资源依赖

子模块收到 `contacts`、`contact_groups` 与 `alarms` 三份独立 map 输入。生产资源之间的关系（摘自 `monitoring/modules/cloud-monitor-alerts/main.tf`，已脱敏裁剪/教学改编）：

```hcl
resource "alicloud_cms_alarm_contact" "contacts" {
  for_each               = var.contacts
  alarm_contact_name     = each.value.alarm_contact_name
  describe               = each.value.describe
  channels_mail          = each.value.channels_mail
  channels_ding_web_hook = each.value.channels_ding_web_hook
  channels_sms           = each.value.channels_sms
  lang                   = each.value.lang
}

resource "alicloud_cms_alarm_contact_group" "contact_groups" {
  for_each                 = var.contact_groups
  alarm_contact_group_name = each.value.alarm_contact_group_name
  contacts                 = each.value.contacts
  depends_on               = [alicloud_cms_alarm_contact.contacts]
}

resource "alicloud_cms_alarm" "cms_alarms" {
  for_each       = var.alarms != null ? var.alarms : {}
  name           = each.key
  contact_groups = each.value.contact_groups
  depends_on     = [alicloud_cms_alarm_contact_group.contact_groups]
}
```

片段省略了各 resource 的其他必要 Provider 参数。子模块完整变量结构以生产 `variables.tf` 为准；联系人 channels 和任何实际联系人/告警信息都未复制。模块根配置 `monitoring/cloud-monitor-alert.tf` 将共享的 contacts 与 contact groups 输入，以及每个账户自己的 alarms 输入传入各子模块。

联系人组资源显式等待联系人资源，告警资源显式等待联系人组资源。`contact_groups` 和 `contacts` 是不同输入：依赖仅决定 Terraform 图的顺序，不会把告警中的组名转换成组成员，也不会自动同步 CMS 1.0 与 CMS 2.0 的联系人配置。CMS 2.0 `cms2_alert_rules` 是独立输入；不可从代码推断云端成员、组名是否一致。

## 隐式依赖：通过引用表达关系

若资源属性引用另一个对象的属性，Terraform 可从表达式推断数据依赖。生产 OSS Bucket ACL 资源引用 `alicloud_oss_bucket` 的名称，因此 ACL 使用对应 Bucket。生产网络告警则通过 Data Source 的返回值和本地表达式把 ID 传到 module。无关节点可并行执行；文件书写顺序不等于 API 执行顺序。删除时依赖顺序反转，先处理使用方。

## depends_on：表达看不见的行为依赖

只有资源行为依赖无法通过属性引用表达时才用 `depends_on`，并写清楚原因。它控制 Terraform 依赖图的先后关系，不保证云端授权传播或外部系统就绪。宽泛依赖会减少并行性，也可能使读取延迟到 apply，增加 unknown 值。

生产源码中的联系人组等待联系人，以及 CMS 1.0 alarm 等待联系组，属于显式依赖。若使用模块级 `depends_on`，它会扩展到该模块关联的资源和 data source，应先检查计划影响。

## Data Source 什么时候读取

查询参数和依赖已知时，Data Source 通常在 plan 阶段读取。若读取依赖本次尚未创建或更新的资源，读取可能延后到 apply，计划提示 `will be read during apply`，下游值暂时 unknown。不要仅为强制执行顺序而对整个 module 加依赖；先确认隐式依赖是否已足够。

可在当前账号实验上观察 Data Source 计划输出。这里的数据源没有 Terraform 管理的上游 resource，也无需为了读账号添加 `depends_on`。

## dynamic：按条件生成嵌套块

CMS 告警资源中的 `dynamic "escalations_critical"`、`dynamic "escalations_warn"` 与 `dynamic "prometheus"` 根据每项输入是否为 null，生成一个或零个资源内部配置块。它们不是可独立寻址或单独纳管的 Terraform resource 实例。出处为 `monitoring/modules/cloud-monitor-alerts/main.tf`（脱敏裁剪/教学改编）。

## lifecycle：控制资源变更方式

Lifecycle 元参数改变 Terraform 处理资源变更的方式，不替代计划审阅。

| 设置 | 用途 | 边界 |
|---|---|---|
| `create_before_destroy` | 替换时先创建新对象 | 服务端需允许新旧对象同时存在 |
| `prevent_destroy` | 配置块保留时阻止删除计划 | 删除整个 resource 块后规则也消失 |
| `ignore_changes` | 更新时忽略指定属性差异 | 不等于忽略整个资源删除 |
| `replace_triggered_by` | 指定其他资源变化触发替换 | 需要资源引用；普通值可由 `terraform_data` 包装 |

用内置资源观察 `triggers_replace`：

```hcl
variable "revision" {
  type    = string
  default = "v1"
}

resource "terraform_data" "release" {
  input            = var.revision
  triggers_replace = var.revision
}
```

在专用本地目录中先 init、plan 并审阅，再 apply。把 `revision` 改成 `v2` 后生成并阅读新计划，预期该逻辑资源被替换；这个例子不代表生产发布动作。实验后对该目录执行 `terraform plan -destroy`，审阅后再清理。

## precondition / postcondition

在本系列的 Terraform 1.7 基线中，变量 validation 只校验该变量自身；`precondition` 和 `postcondition` 可表达资源上下文中的前置条件和结果保证。条件失败会阻止关联操作或依赖操作，但不会回滚已完成的其他云端动作。

在另一个独立本地目录中使用完整示例：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "period" {
  type    = number
  default = 60
}

resource "terraform_data" "checked_period" {
  input = var.period
  lifecycle {
    precondition {
      condition     = var.period >= 60
      error_message = "教学周期必须至少为 60 秒。"
    }
    postcondition {
      condition     = self.output >= 60
      error_message = "记录的周期必须至少为 60 秒。"
    }
  }
}
```

运行 `terraform init` 后执行 `terraform plan -var='period=30'`，预期 precondition 失败。再用默认 `period=60` 生成、审阅并应用计划，随后生成并审阅 destroy 计划，清理这个逻辑资源。`terraform_data` 只记录一个数字，不会创建 CMS 告警；生产 CMS 阈值需遵循对应的产品与 Provider schema。

## provisioner 为什么应少用

生产监控模块没有用以下命令式初始化 demo。`local-exec` 在运行 Terraform 的机器上执行命令，`remote-exec` 通过远程连接执行。Provisioner 不是资源差异的完整描述，失败也不能撤销已发生的外部副作用。

若要在独立本地目录演示，可使用：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

resource "terraform_data" "message" {
  triggers_replace = "v1"
  provisioner "local-exec" {
    command = "echo learning-bootstrap"
  }
}
```

先运行 init、plan 并审阅，再 apply；预期首次创建时打印 `learning-bootstrap`。普通 plan 不会因为存在 provisioner 就重复执行。修改触发值导致替换时命令才会再次运行。完成演示后为该目录生成、审阅和应用 destroy 计划。主机初始化优先使用云初始化数据、镜像或配置管理工具；只有适用时才谨慎采用 provisioner，并设计好凭证、重试和幂等性。

## 练习

1. 画出 `data.alicloud_eip_addresses` → `local.filtered_eip_ids` → `module.network_alerts` 的数据流，指出哪些节点会创建云资源。
2. 画出 CMS contact → contact group → CMS 1.0 alarm 的依赖图，并指出成员数据由哪个输入控制。
3. 解释为什么 CMS 2.0 规则中的联系人组名不会因 `depends_on` 与 CMS 1.0 联系人组成员同步。
4. 对比 `depends_on` 与属性引用，说明 Data Source 在什么情况下会延迟到 apply 读取。
5. 对两个本地 `terraform_data` 示例分别测试有效值、无效值和 destroy 流程；不要将学习 demo 当作生产配置。

## 参考资料

- [资源配置与依赖](https://developer.hashicorp.com/terraform/language/resources/configure)
- [Data Sources](https://developer.hashicorp.com/terraform/language/data-sources)
- [depends_on](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on)
- [Dynamic Blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)
- [Lifecycle](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
- [自定义条件](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)
- [terraform_data](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
- [alicloud_account（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/data-sources/account)
- [alicloud_cms_alarm_contact（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/cms_alarm_contact)
- [alicloud_cms_alarm_contact_group（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/cms_alarm_contact_group)
- [alicloud_cms_alarm（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/cms_alarm)

上一篇：[[IaC/terraform/05_terraform_提供者版本与认证|Provider]] · 下一篇：[[IaC/terraform/07_terraform_循环与批量资源|count 与 for_each]]。
