---
title: Terraform基础-Module 开发与复用
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform模块
  - Terraform Module开发
---

# Terraform基础-Module 开发与复用

## 什么是模块

一个目录中的 Terraform 配置构成一个 Module。直接运行 Terraform 命令的目录是 root module，通过 `module` 块调用的是 child module。

Module 组织一组相关资源，接受输入，并通过 output 暴露需要的结果。它不是单独创建一个“模块云对象”；子模块中的资源仍由当前根配置的 State 管理。

### 模块应该按什么边界拆

一个模块可以表达“应用配置文件”“带标准标签的资源组”或“网络基础层”。边界应围绕有意义的能力和接口，不必给每个单独 resource 都套一层模块。

模块复用能减少复制粘贴，但会增加接口维护、版本升级和地址迁移成本。先提炼真实重复的模式，再决定哪些细节应暴露给调用者。

## 完整实验：应用配置模块

本实验通过一个本地子模块为 web/api 生成配置，不需要云账号。

先在笔记目录之外建立 `10-modules/`，以下“根模块”文件均放在这个目录；“子模块”文件放在 `modules/app-config/`。运行命令时始终留在 `10-modules/`。

```text
10-modules/
├── versions.tf
├── main.tf
├── variables.tf
├── outputs.tf
└── modules/
    └── app-config/
        ├── versions.tf
        ├── variables.tf
        ├── main.tf
        └── outputs.tf
```

### 子模块 versions.tf

```hcl
terraform {
  required_version = ">= 1.7"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = ">= 2.5"
    }
  }
}
```

子模块声明自己需要的 Provider 来源与最低兼容版本，不在这里写连接凭证。最终实际版本还要满足根模块与其他子模块的全部约束。

同一根配置内，同一个 Provider 来源只选择一个版本；不是根模块装一个 2.x、子模块再装一个 3.x。若各模块的版本范围没有交集，初始化会失败，应调整兼容性要求或升级模块。

### 子模块 variables.tf

```hcl
variable "name" {
  description = "服务名，同时作为配置文件名的一部分"
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*$", var.name))
    error_message = "name 必须使用小写字母、数字和连字符，并以字母开头。"
  }
}

variable "environment" {
  description = "配置所属环境"
  type        = string
}

variable "port" {
  description = "应用端口"
  type        = number

  validation {
    condition     = var.port >= 1 && var.port <= 65535 && floor(var.port) == var.port
    error_message = "port 必须是合法整数端口。"
  }
}

variable "output_directory" {
  description = "调用者指定的生成目录，避免写入模块下载缓存"
  type        = string
}
```

### 子模块 main.tf

```hcl
resource "local_file" "config" {
  filename        = "${var.output_directory}/${var.name}.json"
  file_permission = "0644"
  content = jsonencode({
    name        = var.name
    environment = var.environment
    port        = var.port
  })
}
```

模块由调用者指定生成路径。同一个本地或远程模块可能被重复调用，写 `${path.module}/output.json` 容易让多个调用共用路径，也可能污染 `.terraform/modules` 缓存。

### 子模块 outputs.tf

```hcl
output "file_path" {
  description = "配置文件路径"
  value       = local_file.config.filename
}

output "content_sha256" {
  description = "配置内容摘要"
  value       = local_file.config.content_sha256
}
```

父模块不能直接用子模块内的 `local_file.config` 地址取值；应经由 output。只暴露调用者真正需要的结果，可以减少模块内部结构对外部调用的影响。

### 根模块 versions.tf

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
```

### 根模块 variables.tf

```hcl
variable "environment" {
  description = "本次实验环境"
  type        = string
  default     = "dev"
}

variable "services" {
  description = "服务端口配置"
  type        = map(number)
  default = {
    web = 8080
    api = 9000
  }
}
```

### 根模块 main.tf

```hcl
module "app" {
  source   = "./modules/app-config"
  for_each = var.services

  name             = each.key
  port             = each.value
  environment      = var.environment
  output_directory = abspath("${path.root}/generated/${var.environment}")
}
```

`source` 是模块调用的元参数；`name`、`port` 等是子模块声明的输入。Provider 资源字段不能自动成为模块参数，必须查模块接口。

### 根模块 outputs.tf

```hcl
output "config_files" {
  description = "服务名到配置文件路径的映射"
  value = {
    for name, app in module.app : name => app.file_path
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
terraform output config_files
```

预期地址类似：

```text
module.app["web"].local_file.config
module.app["api"].local_file.config
```

预期生成 `generated/dev/web.json`、`generated/dev/api.json`。模块实例 key 来自根模块 map，不是子模块中自动发现的服务名。

查看生成内容：

```bash
cat generated/dev/web.json
cat generated/dev/api.json
```

JSON 的字段顺序不必与 HCL 一致，但 `web.json` 应包含 `name=web`、`environment=dev`、`port=8080`；`api.json` 的 port 应为 `9000`。根输出 `config_files` 是一个 map，key 为服务名，value 为文件的绝对路径。

### 观察输入与资源身份的关系

在根模块的 `services` 默认值中把 `web` 端口改为 `8081`，保留原 key，然后重新生成并审查计划：

```bash
terraform plan -out=port-change.tfplan
terraform show port-change.tfplan
terraform apply port-change.tfplan
cat generated/dev/web.json
```

资源地址仍是 `module.app["web"].local_file.config`。Local Provider 会因文件内容变化替换该文件资源；这与 `for_each` key 被改名造成地址变化是两种原因，读 Plan 时应分别确认。把 key 从 `web` 改为 `frontend`，则会出现旧模块实例退出、新实例创建。

`moved` 能迁移地址与状态绑定，但不能抵消资源参数变化。本例 `name = each.key` 会同时改变文件路径和内容，即使补了 moved，Local Provider 仍可能要求替换。只有实际对象参数保持兼容时，地址迁移才可能保留原对象；完整方法见下一篇 [[IaC/terraform/terraform-import-refactoring|Import、moved 与 removed]]。

将 environment 改为 `staging` 同样会改变生成路径，但**不会自动换一份 State**。在同一状态下运行，Terraform 会把原路径文件移除并管理新路径文件。此实验只是观察路径变化，多环境项目的执行隔离仍见 [[IaC/terraform/terraform-backends-workspaces|Backend 与多环境]]。

### 清理实验

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
terraform state list
```

预期销毁当前 State 中的配置文件资源，源码和父目录可能仍保留。Local Provider 操作的是 Terraform **执行机**上的文件；把实验搬到另一台 runner，不会自动读取开发机上的 `generated/`。

## source 与模块版本

### 本地模块

```hcl
module "app" {
  source = "./modules/app-config"
  # 还需要传入该模块定义的必需变量
}
```

此片段只展示 source 写法。路径相对调用模块的位置；本地模块版本随当前 Git 提交一起管理，没有 Registry 风格的 `version` 参数。

### Registry 模块

来源一般写为 `命名空间/模块名/Provider`，并使用 `version` 固定发布版本。以下只展示 Registry 调用格式，来源、版本和输入应替换成目标模块真实发布的接口：

```hcl
module "network" {
  source  = "namespace/network/azurerm"
  version = "1.2.3"
  # 还需要传入所选模块定义的必需变量
}
```

`version` 仅适用于 Registry 模块；它是模块包版本，和 Provider 的版本不是同一个值。`1.2.3` 是固定单一版本，`~> 1.2` 是允许一个版本范围。选择具体模块后，先查看它自己的 Inputs、Outputs、Provider 要求和示例。

模块名看起来像某个资源，不代表模块接受该资源的所有字段。例如资源的 `account_tier` 不能未经确认就传给任意“storage”模块。

### Git 模块

下面是格式示意，仓库和 ref 需替换成真实来源：

```hcl
module "app" {
  source = "git::https://github.com/example/terraform-modules.git//modules/app?ref=v1.2.0"
  # 还需要传入实际模块的必需变量
}
```

`//modules/app` 指定仓库内子目录，`?ref=` 指定 tag/commit/branch。复现要求高时固定不可变提交，并保留对应的发布记录；浮动 branch 会让相同 source 得到不同代码。

为兼容本系列 **Terraform 1.7 基线**，示例里的 `source` 和 `version` 使用字面量；1.7 不支持用普通变量或 locals 计算它们。**Terraform 1.15+** 新增了来源与版本表达式，但引用的输入变量必须声明 `const = true`，并在初始化阶段已有确定值，不能依赖 plan/apply 才产生的资源属性。本系列不把这项新语法混入基础实验。

`.terraform.lock.hcl` 锁 Provider，不锁远程模块包，因此模块来源版本也要明确管理。根项目的锁文件控制所有子模块共同使用的 Provider；子模块独立运行测试时会成为自己的 root module，才使用其目录中的独立锁文件。

## Provider 怎么传给子模块

### 默认继承

完整实验未写子模块 provider 块，Local Provider 默认配置从根层继承。子模块仍必须声明 `required_providers`，让本地名称对应正确来源。

### 显式映射

可以在根模块补充以下配置，并将 providers map 加入前面的 module 块：

```hcl
provider "local" {
  alias = "execution"
}

module "app" {
  source   = "./modules/app-config"
  for_each = var.services

  providers = {
    local = local.execution
  }

  name             = each.key
  port             = each.value
  environment      = var.environment
  output_directory = abspath("${path.root}/generated/${var.environment}")
}
```

这是替换原 module 块的版本，不能保留两个同名块。map 左边是子模块看到的 Provider 名称，右边是父模块的配置引用。

### 子模块本身需要多个别名

子模块使用 `azurerm.primary`、`azurerm.secondary` 等内部别名时，在其 `required_providers` 中声明：

```hcl
terraform {
  required_providers {
    azurerm = {
      source                = "hashicorp/azurerm"
      configuration_aliases = [azurerm.primary, azurerm.secondary]
    }
  }
}
```

根模块声明两份 Azure Provider 配置后，调用端应显式对应到子模块的接口名。以下是映射片段，假定默认配置 `azurerm` 与别名配置 `azurerm.secondary` 已按 [[IaC/terraform/terraform-providers|Provider 别名]] 配置，且 `./modules/dual-subscription` 是实际存在的模块：

```hcl
module "dual_subscription" {
  source = "./modules/dual-subscription"

  providers = {
    azurerm.primary   = azurerm
    azurerm.secondary = azurerm.secondary
  }

  # 其余输入由 dual-subscription 模块的 variables.tf 定义
}
```

子模块中对应的 resource 通过 `provider = azurerm.primary` 或 `provider = azurerm.secondary` 选择配置。`configuration_aliases` 只是声明“调用者必须提供这些配置名”，不会自动新建凭证或订阅连接；别名配置也不会像默认配置那样自动继承。map 两边的名字可以不同，因为它们分别属于子模块和父模块。

这是另一个 Azure 模块接口片段，不属于本地文件实验。不要在可复用子模块中硬编码 provider 连接和凭证；旧式子模块自带 provider 结构会限制 module 的 count/for_each/depends_on 用法。

## Module 不自动隔离 State

把配置拆成 `modules/network` 和 `modules/app`，仍可能共享同一根 State、执行权限和 apply 范围。要按团队职责或变更频率分开状态，需要独立 root module 和 Backend 设计。

模块更适合表达复用边界；独立根配置更适合表达执行和管理边界。两种边界可以配合，但不能互相替代。

## 模块接口与升级检查

- 变量有明确类型、描述、默认值和业务校验。
- 输出有描述，只包含调用者需要的信息。
- Provider 约束反映实际兼容范围，不随意把根项目策略强加给所有调用者。
- 有最小调用示例、变更说明和必要测试。
- 改 resource label、for_each key 或模块路径时，提供 `moved` 迁移。
- 删除输出或改变输入类型可能影响调用者，应作为接口变更审查。

模块文档可以自动生成接口表，但“为什么这样设计”和升级边界仍要人工说明，见 [[IaC/terraform/terraform-docs|terraform-docs]]。

## 常见问题

- `Unsupported argument`：传入的名字不是该子模块声明的变量；不要把 resource 字段直接当模块输入。
- 找不到 `module.app.file_path`：本例使用 `for_each`，`module.app` 是按服务名组织的 map，应读取 `module.app["web"].file_path` 或遍历它。
- Provider 来源或版本冲突：各模块要明确声明 `required_providers`，再核对版本范围是否有交集。
- 多个实例写入同一路径：模块 key 不会自动让文件名唯一，需要检查路径表达式中是否包含实例输入。
- 更新模块代码但没有预期 diff：先确认 `source`、Registry 版本或 Git ref，以及实际下载的模块；本地模块直接随目录代码变化。

## 练习

1. 给 services 增加 `worker = 7000`，观察新增地址、文件和根输出；原 web/api 的身份是否改变？
2. 只改 web 的端口，再只改它的 map key，说明两个计划差异的原因。
3. 给子模块新增一个有默认值的变量，并在测试与文档中体现它；再讨论删除已有 output 对调用者的影响。
4. 解释根模块锁文件、Registry 模块 `version`、Git `ref` 分别固定什么。

## 参考资料

- [Modules 概念](https://developer.hashicorp.com/terraform/language/modules)
- [模块来源](https://developer.hashicorp.com/terraform/language/modules/sources)
- [模块与 Provider 传递](https://developer.hashicorp.com/terraform/language/modules/develop/providers)
- [模块标准结构](https://developer.hashicorp.com/terraform/language/modules/develop/structure)
- [Provider 依赖锁文件](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [Terraform 1.15 模块来源表达式变更](https://github.com/hashicorp/terraform/blob/v1.15.0/CHANGELOG.md)
- [Local file 资源行为](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file)
- [社区目录组织经验](https://github.com/antonbabenko/terraform-best-practices/blob/master/code-structure.md)

上一篇：[[IaC/terraform/terraform-backends-workspaces|Backend 与多环境]] · 下一篇：[[IaC/terraform/terraform-import-refactoring|Import、moved 与 removed]]。
