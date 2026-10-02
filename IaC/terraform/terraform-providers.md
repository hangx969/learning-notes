---
title: Terraform基础-Provider、版本与认证
tags:
  - IaC
  - terraform
  - terraform/basics
  - azure
date: 2026-10-02
aliases:
  - Terraform Provider
  - Terraform版本锁定
---

# Terraform基础-Provider、版本与认证

## Core 与 Provider 分工

Terraform Core 读取配置、求值、构建依赖图并管理 State。Provider 插件负责平台相关的认证、API 调用和资源 schema。

例如 Core 知道 `for_each` 如何给资源分配 key，但它不知道 Azure Resource Group 的 API 参数，也不知道某个数据库字段改变后能否原地更新。这些行为由 Provider 与平台共同决定。

## required_providers 与 provider

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

provider "azurerm" {
  features {}
  environment = "china"
}
```

- `azurerm` 是当前模块的 Provider 本地名称。
- `hashicorp/azurerm` 是 Provider 的来源地址，默认对应公共 Registry。
- `version` 声明允许的版本范围。
- `provider` 块配置某一次连接所需的环境、账号和行为。

只声明 `required_providers` 不等于已经登录。另一方面，Local/Random 等 Provider 可以没有额外连接设置，因此未写显式 provider 块仍可能正常工作。

Provider 来源不能只依赖资源名称猜测。Docker 使用 `kreuzwerker/docker`；阿里云使用 `aliyun/alicloud`；这些不是 `hashicorp` 命名空间下的 Provider。

## 三种版本分别管理

| 版本 | 配置位置 | 锁定方式 |
|---|---|---|
| Terraform CLI | `required_version` 与本地/CI 安装配置 | 工具安装版本与执行环境固定 |
| Provider | `required_providers` | `.terraform.lock.hcl` 记录选中版本和校验值 |
| 外部 Module | Registry module 的 `version`，或 Git source 的 `ref` | 在模块调用中固定来源版本；Provider 锁文件不锁模块 |

### 版本约束

| 约束 | 含义 |
|---|---|
| `= 2.5.3` | 只允许该版本 |
| `>= 2.5, < 3.0` | 允许指定范围 |
| `~> 2.5` | `>= 2.5.0, < 3.0.0` |
| `~> 2.5.3` | `>= 2.5.3, < 2.6.0` |

`~>` 最后一个版本段的写法会改变升级范围。项目选择“允许小版本升级”还是“只允许补丁升级”，应与团队的升级和测试策略一致。

### 锁文件与升级

初始化时，Terraform 会选择符合全部模块约束的 Provider 版本；已有锁文件时，优先使用符合约束的已锁定版本。

```bash
terraform init
terraform init -upgrade
terraform providers
terraform providers lock -platform=darwin_arm64 -platform=linux_amd64
```

这是读者在项目目录中的命令示例。`-upgrade` 重新考虑允许范围内的版本，也会影响模块下载；不要把它当作每次 CI 都必须执行的准备动作。

`providers lock` 可为团队需要的平台补充官方包校验信息。锁文件差异要 review，不要遇到 checksum 错误就删除文件或关闭校验。

同一 Provider 来源在一个配置中使用一个选中版本。两个 alias 是两套连接配置，不是两个不同的 Provider 版本。

## Provider 认证

认证方式依平台不同，可能来自：

- 开发机 CLI 登录会话或命名 profile。
- 执行环境注入的环境变量。
- 云平台的实例身份、工作负载身份或 OIDC。
- 显式 Provider 参数。

实际优先级和支持范围查看 Provider 文档。不要把可用登录命令、长期 Access Key 和 CI 工作负载身份混为一种方案。

认证成功也不意味着授权足够。资源读取、创建、删除与 State Backend 的数据访问，可能需要不同权限。

Provider 块中的认证参数不会自动成为 Backend 配置。即使 AzureRM Provider 和 Azure Blob Backend 都能读取某些 `ARM_*` 环境变量，它们仍各自建立连接、检查自己的权限；在 `terraform init` 阶段出现的状态存储错误，应先检查 [[IaC/terraform/terraform-backends-workspaces|Backend 认证]]。

## Azure 中国区：完整资源组实验

本例保留原笔记的 Azure 中国区场景，但用自己的订阅和身份，不在文档里固定个人 tenant ID。采用 AzureRM **4.x**，不要直接混用旧 3.x 或新主版本示例。

### 1. 登录和核对目标

```bash
az cloud set --name AzureChinaCloud
az login
az account set --subscription "<你的实验订阅ID>"
az account show --query '{subscription:id,tenant:tenantId,name:name}' -o json
az account list-locations --query '[].name' -o tsv
export ARM_SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
```

Azure 全球区应使用 `AzureCloud`，并把 Provider 的 `environment` 改为 `public`。CLI 当前 cloud、身份所在 tenant、订阅和 Provider environment 必须匹配。

AzureRM 4.x 的 plan/apply 需要明确的订阅 ID；本例通过环境变量传入，避免依赖模糊的账号选择。只执行 `az account set`、却不提供 `ARM_SUBSCRIPTION_ID` 或 `subscription_id`，不能代替这项配置。这个变化来自 AzureRM Provider 4.x，与 Terraform CLI 的版本是两条独立的版本线。

### 2. 配置文件

先创建独立实验目录：

```bash
mkdir -p ~/terraform-labs/05-azure-rg
cd ~/terraform-labs/05-azure-rg
```

在其中创建 `main.tf`：

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

provider "azurerm" {
  features {}
  environment                     = "china"
  resource_provider_registrations = "none"
}

variable "location" {
  description = "当前实验订阅可用的 Azure 中国区 region 名称"
  type        = string
}

variable "resource_group_name" {
  description = "只用于本实验的资源组名称"
  type        = string
  default     = "rg-terraform-learning-dev"
}

resource "azurerm_resource_group" "lab" {
  name     = var.resource_group_name
  location = var.location
  tags = {
    purpose    = "terraform-learning"
    managed_by = "terraform"
  }
}

output "resource_group_id" {
  value = azurerm_resource_group.lab.id
}
```

`features {}` 是 AzureRM 配置的一部分。`resource_provider_registrations = "none"` 表示本例不自动注册订阅中的 Azure Resource Providers；扩展到 Compute/Storage 等服务时，需要确保相应 API 已由有权限的管理员注册。

这里的“Azure Resource Provider 注册”是 Azure 服务 API 的启用机制，和下载 Terraform Provider 插件是两个不同概念。

### 3. 赋值和运行

创建 `lab.tfvars`，将 region 改为前面查询到的可用名称：

```hcl
location            = "chinanorth3"
resource_group_name = "rg-terraform-learning-dev"
```

```bash
terraform init
terraform plan -var-file=lab.tfvars -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform output resource_group_id
```

预期计划只创建一个实验 Resource Group。该例没有创建虚拟机、磁盘或 Storage Account；扩展实验时应先核对平台价格和删除范围。

### 4. 观察一次标签更新

在 `main.tf` 的 `tags` 中补充 `environment = "dev"`，名称和 region 保持原值，再运行：

```bash
terraform plan -var-file=lab.tfvars -out=tags.tfplan
terraform show tags.tfplan
terraform apply tags.tfplan
az group show --name rg-terraform-learning-dev --query tags -o json
```

预期计划更新资源组标签，资源 ID 保持不变。如果前面改了 `resource_group_name`，查询命令也要使用自己的名称。不要用改变 region 来模拟普通更新：AzureRM 的资源组 `name` 和 `location` 改变会要求替换资源，必须先审查计划。

### 5. 清理

```bash
terraform plan -destroy -var-file=lab.tfvars -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

只在专用实验资源组中执行。不要把其他系统创建的资源放进这个实验组再照抄删除步骤。

## alias：一套配置连接多个目标

下面是多订阅连接的教学片段，需要自己声明 `primary_subscription_id` 和 `secondary_subscription_id` 变量，并确保身份有两个订阅的权限：

```hcl
provider "azurerm" {
  features {}
  subscription_id                 = var.primary_subscription_id
  environment                     = "china"
  resource_provider_registrations = "none"
}

provider "azurerm" {
  alias = "secondary"
  features {}
  subscription_id                 = var.secondary_subscription_id
  environment                     = "china"
  resource_provider_registrations = "none"
}

resource "azurerm_resource_group" "secondary" {
  provider = azurerm.secondary
  name     = "rg-terraform-learning-secondary"
  location = "chinanorth3"
}
```

- 没写 `provider` 的资源通常使用默认配置。
- 写 `provider = azurerm.secondary` 的资源使用别名配置，引用不是字符串。
- 如果所有 provider 块都有 alias，Terraform 会产生一个隐含的空默认配置；资源误用默认配置时可能缺少必需参数。
- 子模块可继承默认 Provider，别名通常要显式传递；子模块声明别名接口用 `configuration_aliases`，见 [[IaC/terraform/terraform-modules|Module]]。

## 常见排错方向

| 现象 | 优先检查 |
|---|---|
| 找不到 Provider | source 地址、网络、Registry/私有镜像配置 |
| 版本约束冲突 | 根模块与所有子模块的 required_providers |
| checksum 不匹配 | 锁文件来源、平台校验、下载镜像与缓存；保留校验机制 |
| Azure 订阅缺失 | `ARM_SUBSCRIPTION_ID`、显式配置和 Provider 主版本 |
| 登录成功但 403 | 目标订阅/资源 scope 的授权，Backend 数据访问权限 |
| 不支持某个参数 | 是否查了与锁文件一致的 Provider 文档版本 |
| Provider configuration not present | 仍被 State 引用的 Provider alias 被提前删掉 |

更换本地/远程执行方式时，Provider 认证也在新的执行环境里重新建立。开发机登录不能自动给远程 runner 授权。

## 练习

1. 根据锁文件说明当前使用哪个 AzureRM 版本，再解释 `~> 4.0` 允许的升级范围。
2. 解释切换 Azure CLI 的默认订阅后，显式配置的 `subscription_id` 为什么仍需核对。
3. 一名用户能创建 Resource Group，却在读取 State Blob 时收到 403，应该检查哪个组件、哪一类权限？

## 参考资料

- [Provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
- [Provider configuration 与 alias](https://developer.hashicorp.com/terraform/language/providers/configuration)
- [版本约束](https://developer.hashicorp.com/terraform/language/expressions/version-constraints)
- [依赖锁文件](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [AzureRM 4.x Provider 文档](https://registry.terraform.io/providers/hashicorp/azurerm/4.0.0/docs)
- [AzureRM 4.0 订阅与注册机制变更](https://registry.terraform.io/providers/hashicorp/azurerm/4.0.0/docs/guides/4.0-upgrade-guide)
- [Azure CLI 认证](https://registry.terraform.io/providers/hashicorp/azurerm/4.0.0/docs/guides/azure_cli)
- [Resource Group](https://registry.terraform.io/providers/hashicorp/azurerm/4.0.0/docs/resources/resource_group)

上一篇：[[IaC/terraform/terraform-expressions|表达式与模板]] · 下一篇：[[IaC/terraform/terraform-resources-dependencies|Resource、Data Source 与依赖]]。
