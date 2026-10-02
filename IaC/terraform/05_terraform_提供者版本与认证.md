---
title: 05_terraform_提供者版本与认证
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform Provider
  - Terraform版本锁定
---

# 05_terraform_提供者版本与认证

## Core 与 Provider 分工

Terraform Core 读取配置、计算表达式、构建依赖关系并管理 State。Provider 插件负责目标平台的认证、API 调用和资源 schema。Core 知道 `for_each` 如何形成多个实例地址，但阿里云资源参数及其更新方式由 `aliyun/alicloud` Provider 和对应服务决定。

生产代码依据：`shared/versions.tf` 声明 `aliyun/alicloud` 来源和最低版本；`shared/providers.tf` 配置不同 alias、地域和 `assume_role`。正文的 OSS 练习脱敏裁剪自 `shared/jfrog-cn.tf` 的 Bucket/ACL 关系，只留下空 Bucket 与私有 ACL。

## 三种版本分别管理

| 版本 | 配置位置 | 管理方式 |
|---|---|---|
| Terraform CLI | `required_version` 和运行环境 | 固定本机、CI 或远程 runner 版本 |
| Provider | `required_providers` | 版本约束加 `.terraform.lock.hcl` 中锁定的选择与校验和 |
| 外部 Module | `module` 块 | 使用版本约束或 Git ref；Provider 锁文件不锁 Module |

本系列统一使用 Terraform `>= 1.7, < 2.0`，教学完整版将阿里云 Provider pin 为 `1.266.0`。生产 `shared/versions.tf` 的约束是 `>= 1.266.0`，它表达最低兼容版本，不说明所有工作目录当前解析到同一个版本；旧 lock 文件也不能代表全库实际版本。

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

`alicloud` 是模块内的本地 Provider 名称，`aliyun/alicloud` 是来源地址。Registry 显示 1.266.0 版本可用；下载和校验仍要由读者在自己的实验目录执行。

| 约束 | 含义 |
|---|---|
| `= 1.266.0` | 只允许该版本 |
| `>= 1.266.0, < 2.0.0` | 允许此范围内版本 |
| `~> 1.266` | 允许 `>= 1.266.0` 且 `< 2.0.0` |
| `~> 1.266.0` | 允许 `>= 1.266.0` 且 `< 1.267.0` |

初始化时，Terraform 选择符合全部模块约束的 Provider 版本并维护锁文件。升级 Provider 需审阅锁文件差异和升级说明，不能为绕过校验错误而关闭 checksum 检查。

```bash
terraform init
terraform providers
```

只有在计划升级时才调整 Provider 约束并运行 `terraform init -upgrade`；再 review `.terraform.lock.hcl` 变化和对应版本文档。`terraform providers lock -platform=darwin_arm64 -platform=linux_amd64` 可为团队指定平台写入校验和。不要遇到 checksum 错误就删除 lock 文件或关闭校验。本篇命令是给读者的独立操作说明，并未执行；实验目录不复用生产 State、Backend 或 lock 文件。

## 阿里云认证

Provider 配置要指明 region，凭据由认证方式提供。阿里云官方文档列出的方式包括共享配置文件、环境变量、ECS RAM 角色、RAM AssumeRole 和 OIDC AssumeRole。认证身份必须同时具备所需资源权限；访问远程 State 的权限也需单独核对。

本地练习可使用已在共享配置文件中设置并核对过身份的阿里云 CLI profile：

```hcl
variable "region" {
  type = string
}

variable "profile_name" {
  type = string
}

provider "alicloud" {
  region  = var.region
  profile = var.profile_name
}
```

`<PROFILE_NAME>` 是本机共享配置文件中的 profile 名，不包含密钥。Profile 可以配置不同认证方式，Terraform 会按 Provider 设置读取它；浏览器或控制台登录状态本身不会自动变成 Provider 凭据。先通过适用的 CLI/provider 流程取得并确认当前执行身份和地域。不要把真实密钥写入 HCL、tfvars 或 shell 历史。

Provider 1.266.0 推荐使用 `ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`、`ALIBABA_CLOUD_SECURITY_TOKEN`、`ALIBABA_CLOUD_REGION` 和 `ALIBABA_CLOUD_PROFILE`；`ALICLOUD_*` 与 `ALIBABACLOUD_*` 旧前缀自 1.228.0 起弃用。若组织要求由安全凭据系统注入临时凭据，可按 Provider 支持方式设置环境变量。下方仅作变量名示意，值必须由用户自己的凭据系统提供：

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="<ACCESS_KEY_ID>"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="<ACCESS_KEY_SECRET>"
# 使用 STS 时同时设置短期凭据的三项：
export ALIBABA_CLOUD_SECURITY_TOKEN="<STS_SECURITY_TOKEN>"
export ALIBABA_CLOUD_REGION="<YOUR_REGION>"
```

长期 AK/SK 只作为理解 Provider 输入接口的示意。生产自动化应优先选择 RAM 角色、OIDC 或短时 STS 等临时凭据，遵循最小权限。将变量标记 `sensitive` 不会阻止它们进入 State 或 Plan。

## AssumeRole 和多个 alias

生产配置为不同账号和地域声明不同 Provider alias，并在相应连接中使用 `assume_role`。下面是简化形态；占位账号和角色必须替换成读者自己获准使用的值，源身份还需被目标角色信任，并有 `sts:AssumeRole` 权限。

```hcl
variable "region_primary" {
  type    = string
  default = "cn-shanghai"
}

variable "region_secondary" {
  type    = string
  default = "cn-hongkong"
}

provider "alicloud" {
  region = var.region_primary
}

provider "alicloud" {
  alias  = "secondary"
  region = var.region_secondary

  assume_role {
    role_arn = "acs:ram::<ACCOUNT_ID>:role/<ROLE_NAME>"
  }
}
```

资源通过 `provider = alicloud.secondary` 指向别名连接；alias 是另一套连接配置，不是另一份 Provider 插件。若所有 Provider 块都设置 alias，Terraform 会创建隐式空的默认 Provider 配置，误用默认配置可能缺少必要参数。将 Provider 传入子模块时，显式配置映射更清楚。

多账号示意只解释 Terraform 连接配置，不创建角色或授权策略，也不能直接复制到生产。生产源中的角色名、账号和地域安排属于其各自环境，本文不复用这些值。

## 完整实战：创建独立 OSS 空 Bucket 并设为 private

本实验可选，需要自己的阿里云测试账号、允许创建和删除 OSS Bucket 的授权、有效地域以及一个全局唯一的 Bucket 名称。它创建真实云资源，可能产生费用；不要把其他系统数据放入实验 Bucket。先阅读计划，确认只影响自己这一个空 Bucket 后再执行。

生产依据：`shared/jfrog-cn.tf` 中条件创建的 `alicloud_oss_bucket` 与 `alicloud_oss_bucket_acl`。此处移除了生产 provider alias、服务数据、RAM 用户、访问密钥、生命周期、版本控制和加密等关联项，保留 Bucket 创建—ACL 引用关系及 `force_destroy = false`。这是脱敏裁剪后的独立教学配置，不是生产模块。

### 1. 准备目录和凭据

```bash
mkdir -p ~/terraform-labs/05-oss-bucket
cd ~/terraform-labs/05-oss-bucket
```

确保阿里云 CLI profile 或组织批准的短期凭据已配置。该身份应只拥有实验所需的 OSS 权限。记录自己选用的地域，并确认 Bucket 名称全局唯一。

### 2. 编写 `main.tf`

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
  description = "自己选择且有权使用的阿里云地域"
  type        = string
}

variable "bucket_name" {
  description = "替换为符合 OSS 命名规则且全局唯一的实验 Bucket 名"
  type        = string
}

variable "tags" {
  description = "实验 Bucket 标签"
  type        = map(string)
}

provider "alicloud" {
  region = var.region
}

resource "alicloud_oss_bucket" "lab" {
  bucket          = var.bucket_name
  storage_class   = "Standard"
  redundancy_type = "LRS"
  force_destroy   = false
  tags            = var.tags
}

resource "alicloud_oss_bucket_acl" "lab" {
  bucket = alicloud_oss_bucket.lab.bucket
  acl    = "private"
}

output "bucket_name" {
  value = alicloud_oss_bucket.lab.bucket
}
```

`<YOUR_LAB_BUCKET>` 只是说明占位符：调用者必须在变量文件中填入有效、唯一并符合 OSS 规则的名称，不能原样提交计划。`force_destroy = false` 防止 Provider 为了删除 Bucket 而自动清空对象。ACL 使用独立资源管理，并通过资源引用在创建顺序上先创建 Bucket。Provider 1.266.0 文档说明，删除 `alicloud_oss_bucket_acl` 只会将其从 State 移除，远端 ACL 不会因此恢复为旧值。Bucket 自带的 `acl` 参数自 Provider 1.220.0 起弃用，本文采用独立 ACL 资源。

创建 `lab.tfvars`，填入自己选择的值：

```hcl
region      = "<YOUR_REGION>"
bucket_name = "<YOUR_LAB_BUCKET>"
tags = {
  purpose = "terraform-lab"
}
```

以上尖括号内容仍是占位符，必须替换后才能运行。

### 3. 计划并创建

```bash
terraform init
terraform plan -var-file=lab.tfvars -out=tfplan
terraform show tfplan
```

检查计划仅包含一个 Bucket 和一个 private ACL，没有删除或修改现存资源，再执行：

```bash
terraform apply tfplan
terraform output bucket_name
```

预期 OSS 控制台中的 Bucket ACL 为 `private`；本次没有执行实验或实测云端状态。

### 4. 修改标签并观察普通更新

生产代码通过 `var.jfrog_cn_tags` 把共享标签 map 传给 Bucket。本练习使用 `var.tags` 保留同一数据关系。修改 `lab.tfvars` 中 `tags` 的值，在现有标签上增加 `environment = "lab"`（保留前面的 region 和 bucket_name）：

```hcl
tags = {
  purpose     = "terraform-lab"
  environment = "lab"
}
```

重新计划并查看：

```bash
terraform plan -var-file=lab.tfvars -out=tags.tfplan
terraform show tags.tfplan
```

预期计划只原地更新 Bucket 标签，Bucket 名称、ACL 和其他属性不变。确认后应用，再次计划：

```bash
terraform apply tags.tfplan
terraform plan -var-file=lab.tfvars
```

第二次计划在没有其他变化时应显示 `No changes`。

### 5. 清理

先确认 Bucket 仍为空，再生成并审阅删除计划：

```bash
terraform plan -destroy -var-file=lab.tfvars -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
terraform state list
```

如 Bucket 含对象，`force_destroy = false` 会阻止 Terraform 自动清空它；需先按自己的数据保留要求单独处理对象。删除计划中应包含 Bucket 和 ACL 对应的状态清理。ACL 资源从 State 移除时不会重置远端 ACL；此处同时删除其所属的空 Bucket。确认 Bucket 已删除后，再撤销仅为实验建立的临时授权。

## 常见排错方向

| 现象 | 检查项 |
|---|---|
| 找不到 Provider | `aliyun/alicloud` 来源、网络和 Registry 镜像 |
| 版本约束冲突 | 所有模块对 AliCloud Provider 的约束与 lock 文件 |
| 认证失败 | CLI profile、凭据过期、region 和 Provider 支持的认证参数 |
| `AssumeRole` 拒绝 | 源身份权限、目标角色信任关系、角色 ARN 和会话时效 |
| Bucket 名称冲突 | 名称规则及 OSS 全局唯一性 |
| 创建 Bucket 成功但 ACL 报错 | ACL 权限及 Bucket 属性是否有多个管理者 |
| 登录成功但 403 | 资源权限 scope；远程 State 的数据权限需另查 |

## 练习

1. 给默认 Provider 增加第二个 alias，并让它连接另一个自己有权访问的 region；只写配置，不运行。
2. 解释 `assume_role` 中 `<ACCOUNT_ID>` 和 `<ROLE_NAME>` 分别需要替换成什么信息。
3. 解释为什么 `sensitive = true` 不能替代安全凭据注入。

## 参考资料

- [Provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
- [Provider 配置与 alias](https://developer.hashicorp.com/terraform/language/providers/configuration)
- [版本约束](https://developer.hashicorp.com/terraform/language/expressions/version-constraints)
- [依赖锁文件](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [阿里云 Provider 1.266.0 文档](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs)
- [alicloud_oss_bucket 1.266.0](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/oss_bucket)
- [alicloud_oss_bucket_acl 1.266.0](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/oss_bucket_acl)
- [阿里云 Terraform 认证方式](https://help.aliyun.com/en/terraform/terraform-authentication)
- 生产依据：`shared/versions.tf`、`shared/providers.tf`、`shared/jfrog-cn.tf`（脱敏裁剪；只保留版本来源、alias/role 连接形态和空 Bucket/private ACL 数据链）

上一篇：[[IaC/terraform/04_terraform_表达式函数与模板|表达式与模板]] · 下一篇：[[IaC/terraform/06_terraform_资源数据源与依赖|Resource、Data Source 与依赖]]。
