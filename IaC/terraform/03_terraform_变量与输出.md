---
title: 03_terraform_变量与输出
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform变量
  - Terraform输入输出
---

# 03_terraform_变量与输出

## 三种值各自负责什么

| 写法 | 作用 | 从哪里获得值 |
|---|---|---|
| `variable` / `var.name` | 模块对外接受的输入 | 调用者、变量文件、环境变量或默认值 |
| `locals` / `local.name` | 模块内部复用和派生值 | 由当前配置中的表达式计算 |
| `output` | 模块对外暴露的结果 | 资源属性、表达式或子模块输出 |

例如：环境名是输入，`项目名-环境名` 是内部派生的命名规则，最终文件路径是输出。不要为了减少几次重复而把每个内部计算结果都设计成外部参数。

## 完整实验：生成一份应用配置

在独立目录 `~/terraform-labs/03-variables` 创建下面四个文件。本实验只生成一个本地 JSON 文件。

### versions.tf

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

### variables.tf：声明输入接口

```hcl
variable "project" {
  description = "用于资源命名的项目名"
  type        = string
  default     = "demo"
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*$", var.project))
    error_message = "项目名必须以小写字母开头，只包含小写字母、数字和连字符。"
  }
}

variable "environment" {
  description = "实验环境"
  type        = string
  default     = "dev"
  nullable    = false

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment 必须是 dev、staging 或 prod。"
  }
}

variable "port" {
  description = "应用监听端口"
  type        = number
  default     = 8080
  nullable    = false

  validation {
    condition     = var.port >= 1 && var.port <= 65535 && floor(var.port) == var.port
    error_message = "port 必须是 1 到 65535 之间的整数。"
  }
}

variable "extra_tags" {
  description = "调用者追加的标签"
  type        = map(string)
  default     = {}
  nullable    = false
}
```

有 `default` 的变量可以不传；没有 `default` 的变量必须由调用者提供。`nullable` 控制模块内部最终能否得到 null，它默认是 true，不能简单理解成“null 一律报错”：

| 声明方式 | 不传值 | 显式传入 null |
|---|---|---|
| 有非 null 默认值，`nullable = true` | 使用默认值 | null 覆盖默认值 |
| 有非 null 默认值，`nullable = false` | 使用默认值 | 回退到默认值 |
| 无默认值，`nullable = false` | 必须提供输入 | 报错 |

本例四个变量都需要非 null 的值，因此显式设置 `nullable = false`。例如在 tfvars 中写 `port = null`，本例得到的端口会是默认的 `8080`；写 `port = 0` 则会被 validation 拒绝。对于 object/list，`nullable = false` 只约束整体值，不会自动禁止内部字段或元素为 null。

本例 validation 只引用被校验的变量，兼容系列的 1.7 基线。**Terraform 1.9+** 才允许校验引用其他变量和配置对象，旧版本项目不能直接照搬这种写法。

### main.tf：计算派生值并使用输入

```hcl
locals {
  name = "${var.project}-${var.environment}"
  tags = merge(var.extra_tags, {
    project     = var.project
    environment = var.environment
    managed_by  = "terraform"
  })
}

resource "local_file" "app" {
  filename        = "${path.module}/${local.name}.json"
  file_permission = "0644"
  content = jsonencode({
    name = local.name
    port = var.port
    tags = local.tags
  })
}
```

`merge` 后面的 map 覆盖前面的同名 key。本例让内部标准标签最终生效，避免调用者把 `environment` 改成与变量不一致的值。若希望调用者覆盖，应有意调整顺序。

### outputs.tf：暴露关心的结果

```hcl
output "file_path" {
  description = "应用配置文件的绝对路径"
  value       = abspath(local_file.app.filename)
}

output "effective_tags" {
  description = "合并后实际使用的标签"
  value       = local.tags
}
```

根模块 output 会在 apply 后显示，保存在状态里，也可通过 `terraform output` 查看。子模块 output 是父模块的读取接口，写法为 `module.<模块名>.<输出名>`。

## variables.tf 与 tfvars 的区别

创建 `dev.tfvars`：

```hcl
project     = "demo"
environment = "dev"
port        = 8081
extra_tags = {
  owner = "platform"
}
```

- `variables.tf` 声明“允许哪些输入，类型和规则是什么”。
- `dev.tfvars` 提供“这次运行使用哪些值”。
- `.tfvars` 不能替代变量声明，也不要写 `var.port = 8081`。

读者实验步骤：

```bash
terraform init
terraform plan -var-file=dev.tfvars -out=tfplan
terraform show tfplan
terraform apply tfplan
terraform output
terraform output -raw file_path
cat demo-dev.json
```

预期文件中端口为 `8081`，标准标签和 `owner` 标签同时存在。保存的 Plan 已包含这些变量值，执行该计划时不再传 `-var-file`。

## 根模块变量怎么赋值

### 自动加载的文件

当前 root module 目录中的以下文件会自动参与赋值：

- `terraform.tfvars`
- `terraform.tfvars.json`
- `*.auto.tfvars`
- `*.auto.tfvars.json`

`dev.tfvars`、`prod.tfvars` 不因为名字中有环境名就自动加载，必须显式使用 `-var-file`。

### 环境变量

```bash
export TF_VAR_environment="staging"
export TF_VAR_port="9090"
terraform plan
unset TF_VAR_environment TF_VAR_port
```

复杂类型也可通过环境变量提供，例如 `export TF_VAR_extra_tags='{"owner":"platform"}'`。在 Bash/zsh 中用外层单引号保留 JSON 内的双引号，结束实验后执行 `unset TF_VAR_extra_tags`。团队协作中复杂 map 通常用 tfvars 更容易阅读。

`TF_VAR_port` 是 Terraform 输入变量。`ARM_SUBSCRIPTION_ID`、`AWS_PROFILE` 等通常是 Provider/Backend 的认证设置，两者不是同一层。

### 命令行

```bash
terraform plan -var-file=dev.tfvars -var='port=9090'
```

不在命令行中放真实密码或 token，避免进入 shell 历史和进程参数。自动化环境应通过受控凭证机制注入。

## 本地 CLI 的优先级

同一个根变量被重复赋值时，按以下顺序由低到高覆盖：

1. `variable` 的 `default`。
2. `TF_VAR_<name>` 环境变量。
3. `terraform.tfvars`。
4. `terraform.tfvars.json`。
5. `*.auto.tfvars` 和 `*.auto.tfvars.json`，按文件名字典序加载。
6. 命令行 `-var` / `-var-file`，按出现顺序处理。

因此上面的 `-var='port=9090'` 覆盖 `dev.tfvars` 中的 `8081`；如果交换两项顺序，后面的变量文件会覆盖前面的命令行值。自动文件按完整文件名排序，`.auto.tfvars.json` 不会整体比 `.auto.tfvars` 更晚加载。覆盖以整个变量为单位；两份文件各提供一个 `extra_tags` map 时，后面的 map 不会自动与前面的 map 合并。

HCP Terraform/Enterprise 还有 Workspace 变量、变量集和远程执行模式。该表解释本地 CLI 的赋值顺序；远程项目还应核对平台自己的优先级规则。

## 对象变量和可选字段

下面是另一种接口设计片段，展示把一组相关值收成一个对象：

```hcl
variable "service" {
  description = "单个服务的配置"
  nullable    = false
  type = object({
    name    = string
    port    = number
    enabled = optional(bool, true)
    tags    = optional(map(string), {})
  })
}
```

调用者可以只传：

```hcl
service = {
  name = "api"
  port = 9000
}
```

这里 `enabled` 和 `tags` 会获得可选属性默认值。`optional(bool, true)` 在字段缺省或显式写成 null 时都使用 true；若只写 `optional(bool)`，缺省值则是 null。可选对象属性与默认值已在 **Terraform 1.3+** 稳定支持，兼容本系列基线。该赋值片段应放进使用此接口的根模块变量文件，而不是追加到前面的四文件实验中。

明确的 object 类型能较早暴露必需字段遗漏和不兼容的类型，但额外字段在类型转换中可能被丢弃；把 `enabled` 拼成 `enabeld` 不一定报错，反而可能让真正的 `enabled` 使用默认值。`any` 是要求 Terraform 推导具体类型的占位符，通常不适合用来逃避接口设计。

## sensitive 到底保护什么

```hcl
variable "api_token" {
  description = "由执行环境提供的 API token"
  type        = string
  sensitive   = true
}

output "api_token" {
  value     = var.api_token
  sensitive = true
}
```

这是敏感值传播的教学片段，通常不应把 token 作为模块输出。`sensitive = true` 会在常规 plan/apply 展示中遮盖值，并把敏感性传播到引用它的结果。若 output 含敏感值，也必须明确标记 `sensitive = true`。这不等于加密，也不保证该值不被写入 State 或保存的 Plan。

`terraform output` 不带输出名时会隐藏敏感结果；**指定名字的 `terraform output api_token`，以及使用 `-raw` / `-json` 都可能显示明文**。真实凭证不要拿来做显示实验，读取状态或导出结果时同样要控制权限。

“敏感”和“未知”是两件事：敏感标记决定如何展示，unknown 表示 plan 时还不知道具体值。一个值可以既敏感又已知，也可以既敏感又未知；`try` 也不会把未知资源 ID 变成已知默认值。

**Terraform 1.10+** 的 ephemeral 变量/子模块输出、**1.11+** 且由 Provider 支持的 write-only 参数，是另一组不持久化能力，使用位置受限制，本文的 1.7 基线示例没有启用。不能只加上 `sensitive` 就获得“不持久化”的效果。

## 换变量文件不等于换环境

```bash
terraform plan -var-file=prod.tfvars
```

若仍是同一 root module、Backend 和 Workspace，这条命令继续使用同一份 State，可能把开发资源改成生产参数，或者删除旧名称再创建新名称。

环境隔离必须结合独立目录、独立状态 key/Workspace 和凭证设计，见 [[IaC/terraform/09_terraform_后端工作空间与多环境|Backend 与多环境]]。

## 清理完整实验

回到 `03-variables` 目录，用实验时的变量文件生成删除计划：

```bash
terraform plan -destroy -var-file=dev.tfvars -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
terraform state list
```

预期只删除 `local_file.app`，对应 JSON 文件消失，State 不再列出该资源。后面的接口示例和敏感值片段只是讲解，不需要追加到这个实验里执行。

## 常见问题和练习

- 未声明变量：tfvars 不能创建一个新的输入接口。未声明的 `TF_VAR_*` 被忽略；tfvars 中的未声明项通常警告；命令行 `-var` 传未声明项会报错。
- 子模块读不到根变量：子模块要自己声明 variable，并由父模块显式传值。
- 子模块自己的 tfvars 未生效：自动赋值机制针对当前 root module，父模块调用时不会自动读取子模块 tfvars。
- 期望值被覆盖：同时检查环境变量、自动加载文件和命令行参数。

练习：给完整实验增加 `log_level`，限制为 `debug/info/warn/error`，并把它写入 JSON。随后给出一个非法值，确认变量校验能在变更前暴露问题。

## 参考资料

- [输入变量与优先级](https://developer.hashicorp.com/terraform/language/values/variables)
- [1.7 变量语义：nullable 与默认值](https://developer.hashicorp.com/terraform/language/v1.7.x/values/variables#disallowing-null-input-values)
- [变量校验与 1.9 版本边界](https://developer.hashicorp.com/terraform/language/v1.9.x/expressions/custom-conditions#input-variable-validation)
- [本地值](https://developer.hashicorp.com/terraform/language/values/locals)
- [输出值](https://developer.hashicorp.com/terraform/language/values/outputs)
- [可选对象属性](https://developer.hashicorp.com/terraform/language/expressions/type-constraints#optional-object-type-attributes)
- [敏感数据处理](https://developer.hashicorp.com/terraform/language/manage-sensitive-data)
- [terraform output 的敏感值展示规则](https://developer.hashicorp.com/terraform/cli/commands/output)

上一篇：[[IaC/terraform/02_terraform_配置语法与文件结构|HCL 语法]] · 下一篇：[[IaC/terraform/04_terraform_表达式函数与模板|表达式、函数与模板]]。
