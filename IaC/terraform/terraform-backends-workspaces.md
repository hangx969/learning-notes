---
title: Terraform基础-Backend、Workspace 与多环境
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform远程状态
  - Terraform多环境管理
---

# Terraform基础-Backend、Workspace 与多环境

## Backend 与 Provider 的区别

Provider 决定怎样管理资源，Backend 决定状态存储和访问方式。两者的认证与权限是独立问题。

例如：资源由 AzureRM Provider 在订阅 A 创建，State 可以放在订阅 B 的 Azure Storage；资源也可以是本地文件，状态仍放在远程存储中。

| 组件 | 主要对象 | 失败时常见现象 |
|---|---|---|
| Provider | 云资源、集群、数据库等 API | 资源读取/创建权限不足 |
| Backend | State、锁、存储 endpoint | 初始化、读写状态或获取锁失败 |

能在控制台创建虚拟机，不意味着能读取存状态的 Blob。反过来，能访问 State 也不意味着有权限创建资源。

## 远程状态应该具备什么

- 共享一个明确的状态位置，让执行者读取同一份记录。
- 限制状态读取和写入权限，并按实际敏感性配置加密与存储访问。
- 使用 Backend 支持的锁定，避免并发写同一状态。
- 保留可恢复的状态版本，配合执行日志排查误操作。

远程存储本身不自动提供上述全部能力。锁定取决于 Backend 支持和具体配置，不能只因状态在对象存储里就认定有锁。

## Backend 配置的特点

```hcl
terraform {
  backend "azurerm" {}
}
```

- Backend 类型属于 Terraform CLI 的能力，不是通过 `required_providers` 下载的 Provider。
- 一个根配置只选择一个 Backend。
- Backend 配置在早期初始化阶段处理，不能引用普通 `var.*`、`local.*` 或资源属性。
- 可通过 `-backend-config` 提供部分配置，但不应把凭证放进命令行或可提交文件。
- `.terraform/` 可能保存 Backend 配置信息，保存的 Plan 也可能包含相关信息。
- `cloud` 块用于 HCP Terraform/Enterprise 工作流，不能与 `backend` 块同时配置。

## Azure Blob Backend：配置示例

这是已有 Backend 存储的连接示例，不包含创建存储账号的资源。存储账号和 container 必须先准备好，不能要求同一份未初始化的配置先创建自己的 Backend。

前提：

1. 已有用于 State 的 Storage Account 和 Blob container；已按 [[IaC/terraform/terraform-providers|Azure 中国区认证]] 登录目标 cloud，Backend 要访问的存储账号可以与资源所在订阅不同。
2. 当前身份能访问它，使用 Entra ID 认证时具有相应的 Blob 数据权限，例如适当 scope 的 `Storage Blob Data Contributor`。
3. 已明确状态 key 和 cloud environment；中国区与全球区 endpoint 不同。

本节显式 `use_cli` 参数要求 **Terraform 1.11+**。先把已有本地实验的 `required_version` 改为 `">= 1.11, < 2.0"`，再在同一 `terraform` 块中补充 `backend "azurerm" {}`。不要额外复制出两个重复的 Backend 声明。

创建 `dev.tfbackend`，替换为自己的存储名称：

```hcl
storage_account_name = "youruniquetfstateaccount"
container_name       = "tfstate"
key                  = "learning/dev/terraform.tfstate"
environment          = "china"
use_azuread_auth     = true
use_cli              = true
```

字段解释：

| 字段 | 作用 |
|---|---|
| `storage_account_name` / `container_name` | 找到实际存储账号和 Blob container |
| `key` | 为这份 State 选择明确的 Blob 名称，不是 Terraform 资源 ID |
| `environment` | 选择 Azure cloud 的存储和认证 endpoint |
| `use_azuread_auth` | 使用 Entra ID 访问 Blob 数据面 |
| `use_cli` | 让 Backend 使用已登录的 Azure CLI 会话 |

此例使用本地 Azure CLI 会话和 Entra ID 数据面认证，不在文件里存 Storage Account Key。Provider 中同名或类似的认证字段不会自动替这个 Backend 配置这些参数。Azure Blob Backend 利用 Blob lease 进行锁定，获取 lease 仍需相应权限。

对使用特殊 DNS endpoint 的存储账号，可能还要开启 endpoint lookup 并授予管理面读取权限；按目标账号的实际配置查询官方文档。

## 从本地 State 迁移到远程

迁移的是现有管理记录，应在停止该项目并发运行后操作。

### 1. 先确认和备份

```bash
terraform workspace show
terraform state list
umask 077
terraform state pull > ../state-before-migration.json
```

备份放在受控位置，后续不要提交 Git。确认当前记录确实是准备迁移的状态，而不是别的实验。`state pull` 导出的是当前选中 Workspace 的状态；如果项目已有多个 Workspace，应先逐个核对和备份，不把一份快照当成整个项目所有环境的备份。

### 2. 修改 Backend 并迁移

```bash
terraform init -migrate-state -backend-config=dev.tfbackend
```

查看交互提示中的旧、新位置，确认再继续。`-migrate-state` 尝试复制已有 State；迁移内容也可能涉及多个 Workspace 的状态，必须核对每个提示。普通 init 不应被理解为总会自动搬迁任何本地文件。

`-reconfigure` 是重新建立 Backend 配置，不迁移已有 State。两者不能在需要迁移时随意互换。初始化一个已经有目标状态的目录时，可用 reconfigure 连接，但应确认它不会错误地指向空状态位置。

### 3. 迁移后核对

```bash
terraform state list
terraform workspace show
terraform plan
```

核对资源地址和预期计划。迁移后突然出现“全部创建”，先检查状态 key、Backend 和 Workspace，不要直接 apply。

团队所有执行者都应切到同一远程状态，并停止使用旧本地快照继续修改资源。迁移的是 State 存储位置，`local_file` 生成的文件仍位于原执行机器上；换一台 runner 时，Local Provider 可能发现文件不存在并提出创建，远程 State 不会把本地文件自动分发给其他机器。

## S3 Backend 与原生锁文件

以下例子要求 **Terraform 1.10+**，不是 1.7 基线中可直接使用的设置：

```hcl
terraform {
  required_version = ">= 1.10, < 2.0"

  backend "s3" {
    bucket       = "your-existing-unique-tfstate-bucket"
    key          = "learning/dev/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

已有 Bucket 应开启版本控制等恢复能力，并由执行身份获得所需权限。启用 `use_lockfile` 后，除了状态对象读写，还需要对对应 `.tflock` 对象执行 Get/Put/Delete 等操作。

官方已将 DynamoDB 锁定标为弃用，并给出迁移期同时配置的兼容方案。旧课程常使用 `dynamodb_table`；新项目应根据 CLI 版本评估原生锁文件，而不是把旧配置当成唯一方案。

**不要因为锁失败就设置 `-lock=false`。** 权限不足、网络失败和真正的残留锁需要分别诊断。

## CLI Workspace 是什么

同一配置使用的不同 CLI Workspace，拥有各自的 State。默认 Workspace 名为 `default`，Backend 是否支持多个 Workspace 及其具体存储路径由类型决定。

```bash
terraform workspace list
terraform workspace show
terraform workspace new dev
terraform workspace select dev
```

`terraform.workspace` 可在普通配置中读取当前 Workspace 名。它不是普通输入变量，也不适合拿来替代所有账号、网络和环境参数。

## 完整实验：观察 Workspace 状态隔离

在新目录中创建 `main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

resource "terraform_data" "environment" {
  input = {
    name = "demo-${terraform.workspace}"
  }
}

output "identity" {
  value = {
    workspace = terraform.workspace
    id        = terraform_data.environment.id
    name      = terraform_data.environment.output.name
  }
}
```

此例只管理内置逻辑资源，不创建云对象。

```bash
terraform init
terraform workspace new dev
terraform plan -out=dev.tfplan
terraform show dev.tfplan
terraform apply dev.tfplan
terraform state list
terraform workspace new prod
terraform state list
terraform plan
```

预期 prod 最初没有 dev 的资源记录，普通 plan 会提出创建自己的逻辑实例。这里只查看 prod 的计划，不应用它。切回 dev 观察记录，再清理本次创建的实例与两个空 Workspace：

```bash
terraform workspace select dev
terraform output identity
terraform plan -destroy -out=dev-destroy.tfplan
terraform show dev-destroy.tfplan
terraform apply dev-destroy.tfplan
terraform workspace select default
terraform workspace delete dev
terraform workspace delete prod
```

`workspace delete` 删除的是一个已经清空的状态空间，不代替资源 destroy，也不能删除当前正在选中的 Workspace。若自行扩展实验并在 prod 中 apply 过，应先切到 prod、查看并执行它自己的删除计划，再删除 Workspace。

保存的计划也属于生成它的状态上下文。不要切到 prod 后拿 dev 的计划尝试 apply；每次生成和执行计划时，都先核对当前 Backend 与 Workspace。

### Workspace 隔离了什么

State 分开了，代码、Backend 配置、执行权限和许多认证设置仍可共用。如果两个 Workspace 的真实资源名称和参数相同，仍可能争抢同一个对象或名称。

因此 Workspace 不是 IAM 权限隔离，也不自动隔离订阅、网络或 Kubernetes namespace。对要求不同权限和审核边界的生产环境，独立根目录、Backend 和执行身份通常更清晰。

## 三种多环境方案

| 方案 | 好处 | 需要注意 |
|---|---|---|
| 同目录 + 多个 tfvars | 配置差异集中，容易阅读 | 单独使用时仍共享 State，不能实现独立环境 |
| 同目录 + CLI Workspace | 快速创建结构相近的实例 | 参数和凭证仍要隔离，切错 Workspace 风险较高 |
| 独立根目录 + 独立状态 key | 环境、执行边界更明显 | 通过共享 Module 避免资源代码重复 |

一个较容易理解的团队目录：

```text
infrastructure/
├── modules/
│   └── app/
└── environments/
    ├── dev/
    │   ├── main.tf
    │   ├── dev.tfvars
    │   └── dev.tfbackend
    └── prod/
        ├── main.tf
        ├── prod.tfvars
        └── prod.tfbackend
```

每个环境目录都是独立 root module，有独立锁文件和状态。共享的业务资源定义放进 Module，下一篇会实现这一结构的基本思想。

## CLI Workspace 与 HCP Workspace

- **CLI Workspace**：同一配置下不同的状态实例。
- **HCP Terraform/Enterprise Workspace**：包含配置来源、变量、状态、执行记录和运行设置的平台管理单元。

两者可以在特定配置中建立映射，但概念不等同。远程保存 State 和由平台执行 plan/apply 也是不同能力；采用哪一种，决定凭证和代码在哪台执行机上使用。

## 锁故障怎么判断

1. 看锁信息中的执行者、时间和操作，确认是否还有运行中的命令/CI job。
2. 区分“无法获取锁的权限/网络错误”与“另一个运行持有锁”。
3. 真正残留的锁，在停止并发和确认归属后再按 Backend/CLI 的恢复方式处理。

`force-unlock` 是恢复工具，不是例行准备步骤。错误释放活跃锁可能让两个执行者同时写状态；它也不能替代恢复丢失的状态内容。

## 练习

1. 为什么仅换 `dev.tfvars` 为 `prod.tfvars`，不会自动得到两份 State？
2. 本地文件实验迁移到 Azure Blob Backend 后，文件会随 State 复制到 Azure 吗？换一台执行机时会发生什么？
3. 当 dev/prod 需要不同身份和审批边界时，比较 CLI Workspace 与独立根目录方案。

## 参考资料

- [Backend 配置](https://developer.hashicorp.com/terraform/language/backend)
- [AzureRM Backend](https://developer.hashicorp.com/terraform/language/backend/azurerm)
- [Terraform 1.11 Azure Backend 参数实现](https://github.com/hashicorp/terraform/blob/v1.11.0/internal/backend/remote-state/azure/backend.go)
- [S3 Backend 与锁文件](https://developer.hashicorp.com/terraform/language/backend/s3)
- [初始化与迁移](https://developer.hashicorp.com/terraform/cli/commands/init)
- [State locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [CLI Workspace](https://developer.hashicorp.com/terraform/cli/workspaces)
- [HCP Terraform Workspace](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)
- [删除 CLI Workspace](https://developer.hashicorp.com/terraform/cli/commands/workspace/delete)
- [force-unlock](https://developer.hashicorp.com/terraform/cli/commands/force-unlock)

上一篇：[[IaC/terraform/terraform-state|State]] · 下一篇：[[IaC/terraform/terraform-modules|Module 开发与复用]]。
