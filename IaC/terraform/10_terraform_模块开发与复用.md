---
title: 10_terraform_模块开发与复用
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform模块
  - Terraform Module开发
---

# 10_terraform_模块开发与复用

## 模块边界与复用

Terraform 执行目录本身是 root module；由 `module` 块调用的目录是 child module。模块把一项有意义的能力封装成输入、资源和输出接口。拆分前先确认这项能力会被重复使用或需要单独维护；给每个 resource 再套一层 module 会增加接口和升级成本，却未必提升复用。

本篇从生产仓库的 Cloud Monitor 联系人与联系人组中裁剪例子。它演示模块接口与 Provider 传递，不管理完整告警配置。

生产依据：`monitoring/modules/cloud-monitor-alerts/main.tf`、`monitoring/modules/cloud-monitor-alerts/variables.tf`、`monitoring/modules/cloud-monitor-alerts/versions.tf`；Provider 配置位于 `monitoring/providers.tf`，调用与别名映射位于 `monitoring/cloud-monitor-alert.tf`。下面代码均为基于这些路径的独立教学改写，账号身份、联络资料和业务标识均为占位内容。

## 最小项目结构

在独立目录 `10-cms-contacts/` 创建：

```text
10-cms-contacts/
├── versions.tf
├── providers.tf
├── main.tf
├── outputs.tf
└── modules/cms-contacts/
    ├── versions.tf
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

### 子模块：`modules/cms-contacts/versions.tf`

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = ">= 1.266.0"
    }
  }
}
```

共享模块声明它依赖的 Provider 来源和最低版本，不放连接凭证或 `provider` 配置块。根模块和子模块的约束必须有共同可用版本；根目录的 `.terraform.lock.hcl` 记录本次安装选定的 Provider 版本。

### 子模块：`variables.tf`

```hcl
variable "contacts" {
  description = "CMS 告警联系人，key 是教学配置中的稳定标识"
  type = map(object({
    alarm_contact_name = string
    describe           = string
    channels_mail      = optional(string)
    lang               = optional(string, "zh-cn")
  }))
}

variable "contact_groups" {
  description = "CMS 联系人组，contacts 引用上面的 alarm_contact_name"
  type = map(object({
    alarm_contact_group_name = string
    contacts                 = optional(list(string))
  }))
}
```

这是从生产模块 `variables.tf` 的 `contacts` 和 `contact_groups` 接口缩小而来。生产接口还含短信、钉钉 Webhook 和更多可选项；教学模块只保留说明本例所需的邮箱和语言字段。邮件地址必须由读者替换为自己控制的测试地址。AliCloud 会向新增或修改后的邮箱发送激活链接；收件人激活前，联系人可能不会出现在有效联系人列表中。联系人 API 创建成功不等于通知已验证。

### 子模块：`main.tf`

```hcl
resource "alicloud_cms_alarm_contact" "contacts" {
  for_each           = var.contacts
  alarm_contact_name = each.value.alarm_contact_name
  describe           = each.value.describe
  channels_mail      = each.value.channels_mail
  lang               = each.value.lang
}

resource "alicloud_cms_alarm_contact_group" "contact_groups" {
  for_each                 = var.contact_groups
  alarm_contact_group_name = each.value.alarm_contact_group_name
  contacts                 = each.value.contacts

  depends_on = [alicloud_cms_alarm_contact.contacts]
}
```

`for_each` 的 map key 构成 Terraform 实例地址；资源名称来自对象字段。组资源显式依赖联系人资源，因此 Terraform 图会先完成联系人资源操作，再操作联系人组。`depends_on` 只规定 Terraform 资源顺序；邮箱激活是异步确认，不会因此自动完成，通知送达也需独立验证。

### 子模块：`outputs.tf`

```hcl
output "contact_names" {
  description = "由此模块管理的联系人名称"
  value       = { for key, contact in alicloud_cms_alarm_contact.contacts : key => contact.alarm_contact_name }
}

output "group_names" {
  description = "由此模块管理的联系人组名称"
  value       = { for key, group in alicloud_cms_alarm_contact_group.contact_groups : key => group.alarm_contact_group_name }
}
```

父模块通过 output 读取子模块公开的结果，不直接引用子模块内部的资源地址。只输出调用方需要的信息，可以降低内部实现变化对调用方的影响。

### 根模块

`versions.tf`：

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
```

`providers.tf`：

```hcl
provider "alicloud" {
  region = "cn-hongkong"
  # 使用 AliCloud CLI 环境凭证，或由受控执行环境提供的凭证。
  # 不要把 AccessKey 写入配置或提交到版本库。
}

provider "alicloud" {
  alias  = "secondary"
  region = "cn-shanghai"
}
```

这是教学 Provider 配置，不含真实账号或角色。生产 `monitoring/cloud-monitor-alert.tf` 按账号和区域配置多个 `alicloud` Provider，并由调用端挑选具体配置传给共享模块。

`main.tf`：

```hcl
module "lab_contacts" {
  source = "./modules/cms-contacts"

  providers = {
    alicloud = alicloud.secondary
  }

  contacts = {
    ops = {
      alarm_contact_name = "terraform-lab-ops"
      describe           = "terraform-lab 测试联系人"
      channels_mail      = "terraform-lab@example.invalid"
    }
  }

  contact_groups = {
    platform = {
      alarm_contact_group_name = "terraform-lab-platform"
      contacts                 = ["terraform-lab-ops"]
    }
  }
}
```

生产调用采用同一类映射：左侧是 child module 内的本地 Provider 名，右侧是 root module 中的配置名。教学示例用 `alicloud.secondary` 表示被传入的 alias；生产源中的具体 alias 可在 `monitoring/providers.tf` 和 `monitoring/cloud-monitor-alert.tf` 追溯。实例模块用统一的 `alicloud` 名称写资源，根模块决定它连接哪个账号和区域。单一默认配置时可以省略 `providers` 映射并继承默认配置；明确映射可让多账号调用关系更容易审查。

`outputs.tf`：

```hcl
output "contact_groups" {
  description = "模块管理的联系人组名称"
  value       = module.lab_contacts.group_names
}
```

## 练习步骤与预期观察

本例会通过 AliCloud API 创建 CMS 联系人和联系人组。先把 `terraform-lab@example.invalid` 换成自己控制的测试邮箱。只有在自己有明确授权的实验账号、确认 Provider 身份与目标区域后，才运行云端步骤；不要将生产 workspace、生产凭证或生产联系人用于练习。

```bash
terraform init
terraform fmt -recursive
terraform plan -out=tfplan
terraform show tfplan
```

计划应显示 `module.lab_contacts.alicloud_cms_alarm_contact.contacts["ops"]` 和 `module.lab_contacts.alicloud_cms_alarm_contact_group.contact_groups["platform"]` 待创建，具体属性及 Provider 返回值以实际配置为准。审查账号、区域、名称、通知地址及动作后，才可在授权实验环境应用：

```bash
terraform apply tfplan
terraform output contact_groups
terraform state list
```

预期输出只包含组名映射，地址类似 `module.lab_contacts.alicloud_cms_alarm_contact.contacts["ops"]`。将 map key `ops` 改名会改变 Terraform 地址；仅修改描述或邮件字段通常是属性更新，实际资源更新行为需以该 Provider 版本的 Plan 为准。

清理前生成并审查 destroy plan：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

上述是读者步骤与预期观察；本文仅静态核对配置，未连接云端或执行 plan/apply。

## 模块来源、状态与 Provider

本地模块路径相对调用方目录解析，与根项目一同版本管理；本例不涉及 Registry 发布。Registry 模块用 `source` 与 `version` 固定模块包版本，Git 模块用仓库子目录和 `ref` 选择版本。Provider 锁文件不锁远程模块内容，因此模块来源版本也要单独固定。

模块拆分不会自动隔离 State、执行权限或 apply 范围。若需独立审批或状态生命周期，应拆分 root module 并设计 Backend 边界，而不能只增加 `modules/` 子目录。

每个模块都要声明 `required_providers`，但 provider 配置块应由 root module 持有。子模块要使用同一 Provider 的多个别名时，在约束中通过 `configuration_aliases` 声明接口，再由调用方显式映射。Provider 配置仍被 State 中资源引用时，不可在资源尚未迁移/销毁前删除对应 alias。

## 常见问题与维护检查

- `Unsupported argument`：调用端传入的字段没有在子模块变量中声明；查看 `variables.tf`，不要把云资源字段当成模块输入。
- 联系人组找不到联系人：核对组中的名称与 `contacts[*].alarm_contact_name`，并确认创建依赖指向由此模块管理的联系人。
- Provider 配置不正确：确认别名指向目标区域和身份；跨账号角色信任与 RAM 授权要分别核实。
- module 地址变化导致计划重建：检查 map key、module 名称和 source 路径变化，并评估 State 地址迁移。
- 修改共享接口：检查所有调用方、Plan 和自动生成文档，避免删除仍被使用的输入或输出。

## 练习

1. 增加第二个联系人并将其放入 `platform` 组，记录新增实例地址和执行顺序。
2. 只改联系人 `describe`，再将 map key `ops` 改名；比较计划中的属性更新与地址变化。
3. 扩展已存在的 `contacts` 对象，而不是重复声明 `contacts` 变量。在 `variables.tf` 的对象类型里加入：

   ```hcl
   channels_sms = optional(string)
   ```

   再在 `main.tf` 的 `alicloud_cms_alarm_contact.contacts` 资源中加入：

   ```hcl
   channels_sms = each.value.channels_sms
   ```

   更新测试与文档，并说明未提供该字段时的行为和接口兼容性。短信号码使用授权实验资料；不要将真实联系信息写入公开示例。
4. 将 Provider 映射改为默认配置，并解释生产代码为什么仍为不同账号的模块实例显式映射别名。

## 参考资料

- [Terraform 模块](https://developer.hashicorp.com/terraform/language/modules)
- [模块内 Provider 配置](https://developer.hashicorp.com/terraform/language/modules/develop/providers)
- [Provider 映射](https://developer.hashicorp.com/terraform/language/meta-arguments/providers)
- [AliCloud CMS 告警联系人资源](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/cms_alarm_contact)
- [AliCloud CMS 告警联系人组资源](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/cms_alarm_contact_group)

上一篇：[[IaC/terraform/09_terraform_后端工作空间与多环境|Backend 与多环境]] · 下一篇：[[IaC/terraform/11_terraform_资源导入与重构|Import、moved 与 removed]]。
