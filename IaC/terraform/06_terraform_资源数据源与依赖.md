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

```hcl
resource "local_file" "app" {
  filename = "${path.module}/app.conf"
  content  = "port=8080\n"
}
```

声明 resource 不只是查询一个文件，而是让 Terraform 管理该对象的生命周期。配置变化时可能更新或替换它，配置删除或 destroy 时可能删除它。

`local_file.app` 是配置地址，`filename` 是实际对象的参数，`id` 是 Provider 暴露的身份属性。云资源名称和 Terraform 逻辑名也同样需要区分。

### 参数与导出属性

- 参数是调用者设置的值，例如 `filename`、`content`。
- 导出属性是 Provider 读回或计算的值，例如内容摘要、云资源 ID、分配的 IP。
- 某些字段既可设置，又会被平台规范化或计算。具体行为查看 Provider schema。

资源地址确定后，Terraform 仍需通过 State 将地址与实际对象绑定。只写一个与已有云资源同名的 resource，不会自动完成导入。

## Data Source 表示查询

```hcl
data "local_file" "existing" {
  filename = "${path.module}/existing.txt"
}

output "existing_content" {
  value = data.local_file.existing.content
}
```

这个配置读取已有文件，删除 data 块或执行 destroy 不会因为这段查询而删除那个文件。数据源用于读取配置所需的外部信息；查询到对象不等于接管对象。

严格说，具体数据源的行为仍由 Provider 实现，不能把“data”当成对任意第三方插件无副作用的保证。使用官方文档明确说明的查询接口。

## 完整实验：已有文件与被管理文件

创建独立目录，先创建一个 Terraform 外部维护的文件 `existing.txt`：

```text
shared setting maintained outside Terraform
```

`main.tf` 完整内容：

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

data "local_file" "existing" {
  filename = "${path.module}/existing.txt"
}

resource "local_file" "copy" {
  filename        = "${path.module}/managed-copy.txt"
  content         = data.local_file.existing.content
  file_permission = "0644"
}

output "paths" {
  value = {
    queried = data.local_file.existing.filename
    managed = local_file.copy.filename
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
cat managed-copy.txt
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

预期 `managed-copy.txt` 被删除，`existing.txt` 保留。State 中可以出现 data source 的缓存记录，但那不意味着 Terraform 对查询对象拥有删除责任。

## 隐式依赖：通过引用表达关系

上一例中，`local_file.copy.content` 引用数据源内容，已经表达了“先有查询结果，才能计算文件内容”。

云资源常见的写法也是如此：

```hcl
resource "azurerm_resource_group" "app" {
  name     = "rg-learning-app"
  location = var.location
}

resource "azurerm_storage_account" "app" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.app.name
  location                 = azurerm_resource_group.app.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

Storage Account 引用 Resource Group，Core 可从表达式构建依赖。`storage_account_name` 必须自己声明并提供符合 Azure 命名规则且全局唯一的值；此片段不是可直接执行的完整云项目。

仅把资源组名字重复写成一个相同字符串，不会表达两个 resource 之间的关系。需要依赖时应引用被管理资源的属性。

```mermaid
flowchart LR
    RG[Resource Group] --> SA[Storage Account]
    SA --> OUT[Output]
```

没有依赖关系的节点可以并行处理，所以 `.tf` 中的上下书写顺序不是 API 执行顺序。删除时会考虑反向依赖，先删除依赖者，再删除其前置对象。

## depends_on：表达看不见的行为依赖

有些依赖不是某个参数值的输入，例如服务创建前，某条权限授权必须已完成。此时可以使用 `depends_on`。

```hcl
resource "terraform_data" "permission_ready" {
  input = "教学用前置节点"
}

resource "terraform_data" "service" {
  input      = "教学用后置节点"
  depends_on = [terraform_data.permission_ready]
}
```

这段可用于观察图关系，不代表它真正创建了云权限或服务。`terraform_data` 是内置资源，不需要下载一个名为 `terraform_data` 的外部 Provider。

使用 depends_on 的原则：

- 值依赖能表达时，优先直接引用。
- 隐藏依赖要写注释，说明哪项行为需要等待。
- 不要把所有资源串成一条链；会削弱并行性。
- 对整个模块添加宽泛 depends_on，可能让更多数据源延后到 apply 读取，增加 unknown 和保守替换计划。
- 依赖完成不保证云 API 的授权传播或外部系统可用性立即完成；有些问题需要 Provider 重试或更合理的分层部署。

## Data Source 什么时候读取

查询参数和依赖都可用时，数据源通常在 plan 阶段读取。如果参数依赖尚未创建的值，或有上游待变更的依赖，读取可能推迟到 apply。

因此 plan 中的 `will be read during apply` 不是自动故障。不过它意味着部分下游值暂时 unknown，需要检查是否引入了过宽的依赖。

可以在上面的文件查询实验中观察这种差别：向 `main.tf` 补充下面两个块，并用这里的 data 块替换原来的 `data "local_file" "existing"`：

```hcl
variable "lookup_revision" {
  type    = string
  default = "v1"
}

resource "terraform_data" "lookup_gate" {
  input = var.lookup_revision
}

data "local_file" "existing" {
  filename = "${path.module}/existing.txt"
  # 教学用隐藏依赖：查询必须等 lookup_gate 完成本次操作。
  depends_on = [terraform_data.lookup_gate]
}
```

`existing.txt` 应仍存在；Provider、被管理副本和 output 沿用前面的完整配置。先建立新的基线，再只改变前置节点：

```bash
terraform plan -out=dependency.tfplan
terraform show dependency.tfplan
terraform apply dependency.tfplan
terraform plan -var='lookup_revision=v2'
```

虽然 `filename` 早已确定、文件也没有改，`lookup_gate` 在本次计划中需要更新，显式依赖仍可能让读取推迟到 apply。副本的 `content` 因而成为 unknown，Provider 可能给出保守的替换计划；这不证明原文件内容已经变化。

再用默认 `lookup_revision=v1` 运行普通 plan，前置节点没有待执行的变化时，不能把“写了 depends_on”理解成“每次查询都必然推迟到 apply”。这个实验用于理解计划成本，真实文件查询没有这项隐藏依赖时应去掉它。收尾沿用文件实验的 destroy 流程，清理副本和教学节点，外部文件保留。

## lifecycle：控制资源变更方式

### 用 terraform_data 观察更新与替换

在新实验目录中使用完整 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "release" {
  type    = string
  default = "v1"
}

resource "terraform_data" "app" {
  input            = { release = var.release }
  triggers_replace = var.release
}

output "instance_id" {
  value = terraform_data.app.id
}
```

运行并记录第一次的逻辑实例 ID：

```bash
terraform init
terraform plan -out=release-v1.tfplan
terraform show release-v1.tfplan
terraform apply release-v1.tfplan
terraform output instance_id
terraform plan -var='release=v2' -out=release-v2.tfplan
terraform show release-v2.tfplan
terraform apply release-v2.tfplan
terraform output instance_id
```

预期第二个计划包含替换，apply 后的实例 ID 与第一次不同。原因是 `triggers_replace` 改变；单独改变 `input` 通常只是该逻辑资源的更新。

实验结束时使用相同变量生成删除计划：

```bash
terraform plan -destroy -var='release=v2' -out=release-destroy.tfplan
terraform show release-destroy.tfplan
terraform apply release-destroy.tfplan
```

这个资源适合解释 Terraform 生命周期，不能替代 Provider 管理实际云资源。

### 常见生命周期设置

| 设置 | 作用 | 边界 |
|---|---|---|
| `create_before_destroy = true` | 替换时先创建新对象，再删除旧对象 | 平台必须允许新旧对象并存，名称与配额不能冲突 |
| `prevent_destroy = true` | 配置保留该规则时阻止 Terraform 的删除计划 | 删除整个 resource 配置块后不能靠它继续保护对象 |
| `ignore_changes = [tags]` | 创建后，在更新判断中忽略指定属性的外部变化 | 被忽略的值仍可在首次创建时配置；不代表忽略整个资源删除 |
| `replace_triggered_by = [...]` | 指定管理资源发生相关变更时替换当前资源 | 接受资源引用，不直接接受任意字符串或变量 |

示例片段：

```hcl
resource "terraform_data" "revision" {
  input = var.release
}

resource "terraform_data" "consumer" {
  input = "consumer"

  lifecycle {
    create_before_destroy = true
    replace_triggered_by  = [terraform_data.revision]
  }
}
```

`var.release` 应来自同一实验的变量声明。通过 terraform_data 把普通值变化转成可引用的资源操作，才能用于 `replace_triggered_by`。

生命周期规则在较早阶段处理，很多设置必须用字面值，不能随意改成 `var.*` 条件。`create_before_destroy` 还可能传播到依赖节点，应阅读最终计划。

## precondition / postcondition

条件适合表达输入校验之外的资源约束。下面在另一个独立实验目录创建完整 `main.tf`，观察操作前条件与结果条件：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

variable "replicas" {
  type    = number
  default = 1
}

resource "terraform_data" "checked" {
  input = var.replicas

  lifecycle {
    precondition {
      condition     = var.replicas >= 1
      error_message = "副本数必须至少为 1。"
    }

    postcondition {
      condition     = self.output >= 1
      error_message = "逻辑资源记录的副本数必须至少为 1。"
    }
  }
}
```

变量 validation 验证接口输入，precondition 可验证资源操作前的条件，postcondition 可验证操作或读取后的结果。`self` 表示当前资源，不能把它当成全局变量使用。这里的 `terraform_data` 只记录一个数值，没有真正创建一组副本；对于仅检查 `var.replicas` 的规则，实际项目通常放在变量 validation 中更直接。

先初始化并观察一个失败输入：

```bash
terraform init
terraform plan -var='replicas=0'
```

预期前置条件失败。改回有效输入后，计划、创建并清理：

```bash
terraform plan -var='replicas=1' -out=checked.tfplan
terraform show checked.tfplan
terraform apply checked.tfplan
terraform plan -destroy -out=checked-destroy.tfplan
terraform show checked-destroy.tfplan
terraform apply checked-destroy.tfplan
```

新资源的 `output` 在计划中可能未知，结果条件便要等值确定后检查。条件涉及 unknown 时，检查可能推迟到 apply。

条件失败会阻止对应操作或依赖它的后续操作，但不是一次基础设施事务的整体回滚。若 postcondition 在 apply 时才失败，已经完成的创建或更新不会因此自动撤销。删除计划也只针对这个独立目录中的教学资源。

## provisioner 为什么应少用

`local-exec` 在 Terraform 执行机器上运行命令，`remote-exec` 通常通过远程连接执行配置。它们不是 Terraform 对“任意脚本内容”的完整状态管理。

```hcl
resource "terraform_data" "message" {
  triggers_replace = "v1"

  provisioner "local-exec" {
    command = "echo learning-bootstrap"
  }
}
```

这个例子只是演示生命周期内的命令执行。创建阶段 provisioner 通常不会在每次 plan/apply 都运行；修改输入也不自动等于再次执行脚本。失败还可能使资源被标记为需替换，已经产生的外部副作用不能靠 State 自动撤销。

主机初始化优先考虑 cloud-init、user_data、预制镜像或专用配置管理工具。Shell 执行缺少可审查的资源差异，凭证、重试和幂等性都要额外设计。

## 练习

1. 在文件查询实验中修改 `existing.txt`，查看为什么被管理副本的计划发生变化。
2. 在 terraform_data 实验中删除 `triggers_replace`，比较修改 release 时的计划。
3. 解释“依赖图里等到授权资源创建完”和“云端权限已经传播到所有 API”为什么不是同一保证。

## 参考资料

- [Resource 语法](https://developer.hashicorp.com/terraform/language/resources/syntax)
- [Data sources](https://developer.hashicorp.com/terraform/language/data-sources)
- [depends_on](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on)
- [lifecycle](https://developer.hashicorp.com/terraform/language/meta-arguments/lifecycle)
- [自定义条件](https://developer.hashicorp.com/terraform/language/expressions/custom-conditions)
- [terraform_data](https://developer.hashicorp.com/terraform/language/resources/terraform-data)
- [Provisioners](https://developer.hashicorp.com/terraform/language/resources/provisioners/syntax)
- [Local file 数据源](https://registry.terraform.io/providers/hashicorp/local/latest/docs/data-sources/file)

上一篇：[[IaC/terraform/05_terraform_提供者版本与认证|Provider]] · 下一篇：[[IaC/terraform/07_terraform_循环与批量资源|count 与 for_each]]。
