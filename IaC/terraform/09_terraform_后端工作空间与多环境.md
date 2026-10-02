---
title: 09_terraform_后端工作空间与多环境
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform远程状态
  - Terraform多环境管理
---

# 09_terraform_后端工作空间与多环境

## Backend 与 Provider 的区别

Provider 访问并管理资源 API；Backend 选择 State 的存储和访问方式，并可能提供锁定或远程执行能力。两者的认证和权限是独立问题：能管理阿里云资源不等于能访问 TFE State，能访问 TFE workspace 也不等于有阿里云资源权限。

生产代码出处：`shared/backend.tf`、`monitoring/backend.tf` 与 `permissions/backend.tf`（脱敏裁剪/教学改编）使用 `backend "remote"`，每个根目录指向组织内的单一 workspace。实际 hostname、组织名和 workspace 名均已用示意值替换。

## 远程状态应该具备什么

选择唯一共享位置、限制读取和写入权限、确认 Backend 锁能力，并保留可恢复版本与运行记录。远程位置本身不能保证所有特性都已配置。HashiCorp 的 remote backend 可仅保存 State，也可将 plan/apply 放到 HCP Terraform/Enterprise 远端运行环境；二者是不同执行模式。[remote Backend 文档](https://developer.hashicorp.com/terraform/language/backend/remote)

## Backend 配置的特点

Backend 是 Terraform CLI 的能力，不需放入 `required_providers`。每个根配置选择一种 Backend。Backend 在初始化阶段读取，不能引用 `var.*`、`local.*` 或资源属性。凭证不应写进 backend 块或 `.tfbackend` 文件；`backend "remote"` 可从 Terraform CLI 凭据配置读取登录凭证。

## Terraform Enterprise remote Backend：配置示例

本例使用明显的示意 endpoint、组织和 workspace 名，不指向真实服务。只有在组织管理员已提供实验权限、空的教学 workspace 与 endpoint 后，才可用自己的实验环境替换它们；本文未连接或验证该环境。

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "= 1.266.0"
    }
  }

  backend "remote" {
    hostname     = "tfe.example.invalid"
    organization = "example-org"
    workspaces {
      name = "terraform-lab-monitoring"
    }
  }
}
```

`.invalid` 是示例域名，不可用于真实连接。provider 版本固定为 `1.266.0`，满足生产 `shared/versions.tf` 所设的 AliCloud Provider 最低版本 `>=1.266.0`，但生产没有在本文中被改写成这一精确 pin。真实 Token 通过 `terraform login` 或 CLI credentials 配置提供，不能写入配置或提交的文件。

`backend "remote"` 指定状态所在的 TFE workspace。若 workspace 使用远程运行，Provider 会在 TFE 执行环境中调用；若只用它远程存储 State，CLI 可在本机执行操作。选择 remote Backend 不会自动决定是哪一种。

## 从本地 State 迁移到远程

迁移会移动管理记录。可以选第 01 篇的内置资源实验作为源 State，并确认目标是自己获准使用的空 TFE 教学 Workspace；迁移前停止双方的并发执行。此步骤只迁移当前实验 root 的 State；增加一个指向空 workspace 的 Backend 不会复制生产 root module 配置，也不会把生产 State 或资源自动带入教学项目。

### 1. 先确认和备份

```bash
terraform workspace show
terraform state list
umask 077
terraform state pull > ../state-before-migration.json
```

备份保存在受控本地目录，不提交 Git。检查当前目录、workspace 与绑定地址，避免备份了另一项实验。

### 2. 配置 Backend 并迁移

先在该实验根配置中加入上例 Backend 块，登录已授权的教学 TFE 后运行：

```bash
terraform init -migrate-state
```

确认 CLI 显示的旧、新状态位置后再继续。`-migrate-state` 用于尝试复制已有状态；`-reconfigure` 会重新配置 Backend，但不迁移状态。若远端 workspace 已有状态，先核对来源与归属，不能盲目覆盖或合并。

### 3. 迁移后核对

```bash
terraform workspace show
terraform state list
terraform plan
```

确认原地址仍在远程状态中，计划符合预期。若计划突然提出全部创建，先检查 hostname、organization、workspace 和 CLI workspace 映射，不要应用。

状态迁移只转移 State，源代码与本地文件仍需单独分发。例如第 14 篇的本地 Helm Chart 不会随 State 上传；切换到远程 runner 前，应通过代码仓库或运行平台提供相同的 Chart 文件。

## OSS Backend：Terraform CLI 也可用阿里云存储状态

Terraform CLI 提供 `oss` Backend，可把状态保存在 Alibaba Cloud OSS；配置 TableStore 时也可获得状态锁与一致性检查。它属于 Terraform Backend，与 `aliyun/alicloud` Provider 是不同组件。Provider 1.266.0 文档列出 `ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`、可选 `ALIBABA_CLOUD_SECURITY_TOKEN`、`ALIBABA_CLOUD_REGION` 与 `ALIBABA_CLOUD_PROFILE` 等认证配置。OSS Backend 是 Terraform CLI 的独立组件，不应仅凭 Provider 文档推断它支持相同字段、环境变量或旧名称；分别查当前 CLI 版本的 OSS Backend 文档。[OSS Backend 文档](https://developer.hashicorp.com/terraform/language/backend/oss)

生产来源只用于讨论应用资源：`shared/jfrog-cn.tf`（脱敏裁剪/教学改编）配置 OSS Bucket 与 ACL；`shared/backend.tf` 指向 TFE remote Backend，因此这些资源归该远端 workspace 的 State 管理。应用 Bucket 资源与 OSS Terraform Backend 是不同用途，不能把前者误认为后者。若要使用 OSS State Backend，应单独按实际 Terraform CLI 版本对应的 OSS Backend 文档检查其字段、认证方式与锁定能力。

## CLI Workspace 是什么

CLI Workspace 是同一配置下的不同 State；默认名为 `default`。它不自动隔离凭证、账号权限、代码或网络。生产 `backend "remote"` 的 `workspaces { name = ... }` 选定一个 TFE Workspace；若采用 `prefix` 映射多个远程 Workspace，CLI 的短名称与 TFE 完整名称有关联，但概念仍需区分。

## 完整实验：观察 Workspace 状态隔离

此内置资源实验使用默认 Local Backend，不连接云端或 TFE；它只展示 CLI Workspace 的状态隔离。生产中的 TFE remote Backend 是前一节的另一个配置示例，且 `workspaces { name = ... }` 指向单一远程 Workspace，不应在这个配置上运行 `workspace new dev/prod`。给空实验 workspace 添加 Backend 块只会改变状态位置，不会复制或提供生产 root module 的资源配置。

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

resource "terraform_data" "environment" {
  input = "demo-${terraform.workspace}"
}

output "identity" {
  value = {
    workspace = terraform.workspace
    id        = terraform_data.environment.id
    name      = terraform_data.environment.output
  }
}
```

运行时先确认当前 Backend 与 Workspace：

```bash
terraform init
terraform workspace show
terraform workspace new dev
terraform plan -out=dev.tfplan
terraform show dev.tfplan
terraform apply dev.tfplan
terraform state list
terraform workspace new prod
terraform state list
terraform plan
```

预期 `prod` 一开始没有 `dev` 的资源，计划只提出创建该 workspace 自己的逻辑资源；先不 apply prod 计划。切回 dev 核对后清理：

```bash
terraform workspace select dev
terraform output identity
terraform plan -destroy -out=dev-cleanup.tfplan
terraform show dev-cleanup.tfplan
terraform apply dev-cleanup.tfplan
terraform workspace select default
terraform workspace delete dev
terraform workspace delete prod
```

若自行扩展并在 prod apply 了资源，先切到 prod，审阅并执行该 workspace 自己的 destroy 计划，再删除 Workspace。保存的计划要在生成它的 Backend 和 Workspace 状态上下文中使用。

### Workspace 隔离了什么

各 Workspace 有各自状态，但仍共享配置与执行环境。若两个环境的命名、参数指向同一远端对象，仍会发生冲突。不同权限边界需要不同凭证和访问控制，不能靠 workspace 名实现。

## 三种多环境方案

| 方案 | 特点 | 需要注意 |
|---|---|---|
| 同根目录、不同 tfvars | 集中管理配置参数 | 单独更换 tfvars 不会创建独立 State |
| CLI Workspace | 同一配置有多份 State | 账号、凭证和资源命名仍需正确隔离 |
| 独立根目录与 Backend | 执行边界清楚 | 通过共享 module 避免重复资源代码 |

要求不同权限、审批或账号的环境，独立根目录、Backend 和执行身份通常更易审阅。

## CLI Workspace 与 TFE Workspace

CLI Workspace 是 Terraform CLI 当前配置的状态实例；TFE Workspace 还承载远端 State、变量、运行设置和运行记录。Remote Backend 可在本地运行 Terraform 并仅存 State，也可将操作交给远端运行环境。认证变量应放在执行环境的受控设置中，而非提交到 Terraform 配置。

## 锁故障怎么判断

先看锁信息、执行者与时间，核对是否还有本地命令或 CI/TFE 运行；再区分访问权限或网络失败与确有残留锁。只在确认锁属于已结束的本方操作、且未有其他运行时，按 Backend 恢复方式处理。`force-unlock` 不是日常步骤；错误释放活跃锁可能造成并发写入。

## 练习

1. 为什么换 tfvars 不会自动产生独立 State？
2. 将第 14 篇的 State 放到远程后，runner 是否会自动拿到本地 Helm Chart？说明状态迁移与代码分发的区别。
3. 对比使用 TFE workspace 远程执行与仅远程存储 State 时，Provider 凭证分别由哪里消费。
4. 区分生产 OSS Bucket 资源、OSS State Backend、TFE remote Backend 三者的职责。

## 参考资料

- [Backend 配置](https://developer.hashicorp.com/terraform/language/backend)
- [Remote Backend](https://developer.hashicorp.com/terraform/language/backend/remote)
- [Alibaba Cloud OSS Backend](https://developer.hashicorp.com/terraform/language/backend/oss)
- [初始化与状态迁移](https://developer.hashicorp.com/terraform/cli/commands/init)
- [State locking](https://developer.hashicorp.com/terraform/language/state/locking)
- [CLI Workspace](https://developer.hashicorp.com/terraform/cli/workspaces)
- [TFE Workspace](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)

上一篇：[[IaC/terraform/08_terraform_状态漂移与状态操作|State]] · 下一篇：[[IaC/terraform/10_terraform_模块开发与复用|Module 开发与复用]]。
