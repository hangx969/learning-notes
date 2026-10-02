---
title: Terraform基础-Import、moved 与 removed
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform导入已有资源
  - Terraform资源重构
---

# Terraform基础-Import、moved 与 removed

## 先区分三种意图

| 意图 | 首选机制 | 对管理关系的影响 |
|---|---|---|
| 把已有对象纳入 Terraform | `import` 块 | 建立实际 ID 到配置地址的绑定 |
| 改地址但保留原对象 | `moved` 块 | 把旧地址绑定迁移到新地址 |
| 停止管理但保留实际对象 | `removed` + `destroy = false` | 移除绑定，保留对象 |

这些操作首先处理的是资源身份和管理记录。目标配置的属性不一致时，仍可能产生更新或替换。

## 为什么写同名 resource 不能自动导入

平台中已经有 `rg-learning-import`，不意味着 Terraform 知道它对应 `azurerm_resource_group.existing`。没有 State 绑定时，Terraform 通常仍按新资源计划创建，可能遇到同名冲突或 Provider 的显式导入提示。

Data Source 可以查询已有对象，但不会因为读取它就自动承担它的生命周期。

## Azure Resource Group 导入实验

使用自己有权限的独立实验订阅和资源组。先完成 [[IaC/terraform/terraform-providers|Azure 中国区认证]]，不要导入已经由另一份 State 或其他自动化系统负责的对象。

### 1. 明确已有对象

如果需要创建一个新的、尚未交给 Terraform 的实验对象，可由读者在控制台创建专用空资源组。随后查询：

```bash
az group show --name rg-learning-import --query '{id:id,location:location,tags:tags}' -o json
```

记下实际名称、region 和 tags。导入 ID 必须按对应 Provider 资源文档规定的格式提供，不能只使用显示名。

### 2. 准备完整配置

在新目录创建 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

variable "subscription_id" {
  type = string
}

variable "location" {
  type = string
}

variable "resource_group_name" {
  type    = string
  default = "rg-learning-import"
}

variable "existing_tags" {
  type    = map(string)
  default = {}
}

provider "azurerm" {
  features {}
  subscription_id                 = var.subscription_id
  environment                     = "china"
  resource_provider_registrations = "none"
}

resource "azurerm_resource_group" "existing" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.existing_tags
}

import {
  to = azurerm_resource_group.existing
  id = "/subscriptions/${var.subscription_id}/resourceGroups/${var.resource_group_name}"
}

output "resource_group_id" {
  value = azurerm_resource_group.existing.id
}
```

创建 `import.tfvars`，使用查询所得的实际值：

```hcl
subscription_id     = "00000000-0000-0000-0000-000000000000"
location            = "chinanorth3"
resource_group_name = "rg-learning-import"
existing_tags       = {}
```

全零订阅 ID 只是占位值，必须替换。已有 tags 不为空时应填入，而不是无意清空它们。

### 3. 查看导入计划

```bash
terraform init
terraform plan -var-file=import.tfvars -out=import.tfplan
terraform show import.tfplan
```

理想结果是导入目标对象，并且没有非预期创建、修改或删除。若出现标签修改、区域变化或替换，先调整配置以符合纳管意图，再重新 plan。

### 4. 接受计划并核对

```bash
terraform apply import.tfplan
terraform state show azurerm_resource_group.existing
terraform plan -var-file=import.tfvars
```

导入本身不重新创建对象，但同一计划可以包含其他变更，所以必须阅读完整计划。正常纳管之后再 plan 应符合预期；保持相同配置时通常没有变化。

## CLI import 与 import 块

传统 CLI 写法示意：

```bash
terraform import -var-file=import.tfvars azurerm_resource_group.existing "/subscriptions/<订阅ID>/resourceGroups/<资源组名>"
```

这个命令直接修改状态，不生成完整资源配置。需要先准备 resource 定义和认证；不和前面的 import 块实验重复执行。

Terraform 1.5+ 的 import 块把导入意图放进配置，支持 plan/review 工作流。1.7+ 支持 import 块的 for_each，批量导入仍要求实例映射和导入 ID 正确。

导入完成后可以保留 import 块作为来源记录，也可按团队约定移除；移除 import 声明不等于退出资源管理，resource 和 State 绑定仍存在。

## 自动生成配置

另一种工作流是：保留 Provider 配置和 import 块，暂时没有目标 resource 定义，然后运行：

```bash
terraform plan -var-file=import.tfvars -generate-config-out=generated_resources.tf
```

这是替代前面手写 resource 的流程。输出路径必须尚不存在；生成的文件需要人工 review，可能包含不合适的默认值、冲突参数或过多属性。

生成配置不等于已导入，更不等于得到可复用模块。整理出清晰的变量与资源定义，再重新查看和执行导入计划。

## moved：保留对象的地址重命名

假设已经创建了 [[IaC/terraform/terraform-basics|本地文件实验]] 中的 `local_file.hello`。现在要把逻辑名改为 greeting，实际 filename/content 保持一致。

替换原 resource，更新 output，并补充 moved 块：

```hcl
resource "local_file" "greeting" {
  filename        = "${path.module}/hello.txt"
  content         = "Hello, Terraform!\n"
  file_permission = "0644"
}

moved {
  from = local_file.hello
  to   = local_file.greeting
}

output "file_path" {
  value = local_file.greeting.filename
}
```

Provider 要求仍沿用原项目。若之前修改过内容，迁移时应使用当前实际期望的内容，而不是机械恢复本文字符串。

```bash
terraform plan -out=move.tfplan
terraform show move.tfplan
terraform apply move.tfplan
terraform state list
```

预期计划显示地址迁移，不因单纯改名而删除文件重建。资源属性确实改变时，Provider 的更新/替换规则仍会生效。

### count 到 for_each

```hcl
moved {
  from = local_file.config[0]
  to   = local_file.config["web"]
}
```

逐项映射旧索引与新 key，并核对 filename 等真实属性一致。不能只写第一项后就假设其余实例会自动对齐。

### 根资源移入模块

```hcl
moved {
  from = local_file.greeting
  to   = module.app.local_file.config
}
```

这是地址迁移片段，目标模块必须真实存在，且对应资源参数与原对象兼容。模块化不是单纯把文件挪到目录里；module 调用会引入新的地址层级。

共享模块中的 moved 声明通常应保留，让尚未升级的调用者也能沿着旧地址迁移。是否移除要考虑所有调用者的升级路径。

## removed：停止管理但保留对象

Terraform **1.7+** 可以使用声明式退出管理。以导入实验的资源组为例：移除 resource、对应 import 和依赖它的 output，加入：

```hcl
removed {
  from = azurerm_resource_group.existing

  lifecycle {
    destroy = false
  }
}
```

Provider 和变量设置按当前项目需要保留，再生成、查看和执行计划：

```bash
terraform plan -var-file=import.tfvars -out=remove.tfplan
terraform show remove.tfplan
terraform apply remove.tfplan
terraform state list
```

预期 Terraform 忘记绑定，资源组仍存在。`destroy = false` 是这里表达保留对象的关键；不要把缺少该设置的移除行为理解为相同效果。

之后若重新添加 resource 而不 import，Terraform 又会按没有绑定的新对象处理。

## 跨 State 移交

`moved` 主要描述同一配置状态内的地址迁移，不是把任意对象自动复制到另一个 Backend。

跨项目移交需要协作流程：

1. 停止原、新项目对这些对象的并发修改，备份各自状态。
2. 核对实际 ID、新旧地址、Provider 和配置参数。
3. 原项目退出管理，新项目 import，避免两个 State 同时控制同一对象。
4. 分别查看完整计划，确认原项目不会重新创建，新项目不会意外替换。

如果需要使用 `state mv`/`state rm` 等命令，应把它们作为受控状态维护操作，而不是为了躲过一个不理解的 Plan。

## 练习

1. 比较不写 moved 和写 moved 的改名计划，说明为什么 State 地址会影响资源身份。
2. 给 count 的两个保留实例设计旧索引到新 key 的映射。
3. 解释删除 import 块、删除 resource 块、应用 removed 块三者的区别。

## 参考资料

- [Import](https://developer.hashicorp.com/terraform/language/import)
- [生成配置](https://developer.hashicorp.com/terraform/language/import/generating-configuration)
- [moved 与模块重构](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [移除资源管理](https://developer.hashicorp.com/terraform/language/resources/behavior)
- [Azure Resource Group 导入格式](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group#import)
- [CLI import](https://developer.hashicorp.com/terraform/cli/commands/import)

上一篇：[[IaC/terraform/terraform-modules|Module]] · 下一篇：[[IaC/terraform/terraform-workflow-troubleshooting|Plan 阅读与排错]]。
