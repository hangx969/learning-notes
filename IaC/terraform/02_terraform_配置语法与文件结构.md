---
title: 02_terraform_配置语法与文件结构
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform HCL
  - Terraform配置语法
---

# 02_terraform_配置语法与文件结构

## HCL 的基本结构

Terraform 配置通常保存在 `.tf` 文件中，并使用 HCL 原生语法。阅读时先识别三部分：块（block）、块的标签（label）和块内的参数（argument）。

```hcl
resource "local_file" "config" {
  filename = "${path.module}/app.conf"
  content  = "port=8080\n"
}
```

- `resource` 是块类型。
- `"local_file"` 与 `"config"` 是这个块的两个标签。
- `filename = ...` 和 `content = ...` 是参数赋值。
- 大括号围住块的主体，右侧可以是常量、引用或表达式。

不同块的标签数量由 Terraform 语言规定。资源内部支持什么参数、什么嵌套块，则由该资源所属 Provider 的 schema 决定。

### 不要混淆对象与嵌套块

下面的 `input` 是对象值，成员之间可以用逗号分隔：

```hcl
resource "terraform_data" "app" {
  input = {
    name = "web"
    port = 8080
  }
}
```

下面的 `lifecycle` 是嵌套块，没有 `=`：

```hcl
resource "terraform_data" "protected" {
  input = "demo"

  lifecycle {
    prevent_destroy = true
  }
}
```

是否写成 `field = { ... }`，不能只凭外观猜。例如 Helm Provider 3.x 的 `kubernetes` 是对象参数，旧版本教程可能使用嵌套块。应查对应版本的 Provider 文档。

## 常见顶层块

| 块 | 作用 | 使用时关注 |
|---|---|---|
| `terraform` | CLI、Provider 要求、Backend 或 cloud 设置 | 初始化阶段需要的信息 |
| `provider` | Provider 的具体配置 | 账号、区域、认证、别名 |
| `resource` | 管理一个实际对象或逻辑资源 | 生命周期与资源地址 |
| `data` | 查询外部信息 | 查询条件和读取时间 |
| `variable` | 声明输入变量 | 类型、默认值、校验 |
| `locals` | 定义可复用的本地表达式 | 派生值，不是可重新赋值的变量 |
| `output` | 暴露结果或模块接口 | 引用值、描述、敏感性 |
| `module` | 调用子模块 | 来源、版本、输入、Provider 传递 |
| `import` / `moved` / `removed` | 声明纳管、地址迁移或退出管理 | 身份与状态迁移 |
| `check` | 持续检查条件 | 检查失败通常报告警告，不作为强制阻断 |

大多数日常配置只需要前八类。后面的块适合在已理解 State 后学习。

## 基本值和类型

### 字符串、数字、布尔值

```hcl
locals {
  name    = "web"
  port    = 8080
  enabled = true
}
```

- 字符串使用双引号，不能用 shell 风格的单引号代替。
- `true`、`false` 是布尔值；`"true"` 是字符串。
- 数字类型统一为 `number`，不要依靠隐式转换表达业务意图。

### list、set、map、object、tuple

| 类型 | 主要特征 | 类型约束例子 |
|---|---|---|
| list | 有顺序，元素类型一致，可重复 | `list(string)` |
| set | 不保证顺序，去重，元素类型一致 | `set(string)` |
| map | 字符串 key，value 类型一致 | `map(string)` |
| object | 一组有名称和各自类型的字段 | `object({ name = string, port = number })` |
| tuple | 固定位置、各位置可有不同类型 | `tuple([string, number])` |

```hcl
locals {
  names = ["web", "api", "web"]
  roles = toset(["reader", "writer", "reader"])
  tags  = { owner = "platform", env = "dev" }
  app   = { name = "web", port = 8080, enabled = true }
}
```

`[ ... ]` 与 `{ ... }` 是字面量写法，Terraform 会结合目标类型进行转换。字面量本身可先形成 tuple/object，不能看到方括号就断言它已经是 `list(string)`。

当配置需要稳定 key 时使用 map/object；当顺序重要时使用 list；当只关心不重复的成员集合时使用 set。`for_each` 如何利用 key，见 [[IaC/terraform/07_terraform_循环与批量资源|批量资源管理]]。

### null 与 unknown

这两个状态经常出现在变量和 Plan 中，但含义不同。

- `null` 是已知的“没有值”。对普通资源参数，常用于表示不设置，之后是否采用默认值由 schema 决定。
- unknown 是当前阶段还不知道值，例如待创建资源的 ID，在 plan 中显示 `(known after apply)`。

`null` 不等于空字符串 `""`、空列表 `[]` 或空 map `{}`。unknown 也不是“报错了”，但它不能出现在要求 plan 时确定的实例数量或 key 中。

## 引用怎么写

| 想引用什么 | 写法 |
|---|---|
| 输入变量 | `var.environment` |
| 本地值 | `local.common_tags` |
| 资源属性 | `local_file.config.filename` |
| Data Source 属性 | `data.local_file.existing.content` |
| 子模块输出 | `module.app.file_path` |
| count 实例属性 | `local_file.config[0].filename` |
| for_each 实例属性 | `local_file.config["web"].filename` |
| 当前 CLI Workspace 名 | `terraform.workspace` |

只需要一个值时直接引用：

```hcl
output "name" {
  value = terraform_data.app.input.name
}
```

需要拼接文字时才使用字符串插值：

```hcl
output "message" {
  value = "service=${terraform_data.app.input.name}"
}
```

旧教程中的 `"${var.name}"` 仍可见，但直接赋值时写 `var.name` 更清楚，还能保留原始值类型。

## 注释、多行文本和转义

```hcl
# 单行注释
// 另一种单行注释
/* 多行注释 */

locals {
  config = <<-EOT
    server {
      listen 8080;
    }
  EOT

  literal_template = "$${HOME}"
}
```

- `<<-EOT` 允许按公共缩进处理 heredoc 文本；结束标记单独占一行。
- `\n` 是换行，`\"` 用于字符串内的双引号。
- 要在模板中输出字面量 `${HOME}`，写 `$${HOME}`；否则 Terraform 会尝试把它当成插值。
- 需要 JSON/YAML 时优先用 `jsonencode`/`yamlencode`，避免自己维护引号和缩进。

## 一个项目里的文件怎么拆

```text
example/
├── versions.tf        # required_version / required_providers
├── providers.tf       # provider 配置
├── main.tf            # 资源、数据源或模块调用
├── variables.tf       # 变量声明
├── outputs.tf         # 输出声明
├── terraform.tfvars   # 根模块变量值
└── modules/
    └── app/           # 独立的子模块目录
```

### 文件名不决定执行顺序

同一目录内的 `.tf` 和 `.tf.json` 配置会组成一个模块。`versions.tf`、`main.tf`、`variables.tf` 是组织约定，不是不同执行阶段。

不能在两个文件中各声明一个同名资源来“覆盖前面的定义”。Terraform 不按文件名顺序执行创建操作，而是根据引用关系生成依赖图。

子目录不会因为放在 `modules/` 下就被自动加载；必须通过 `module` 块调用。`.tfvars` 也不是资源定义文件，不能把 `resource` 块写在其中。

### 特殊文件需要谨慎

Terraform 支持 `override.tf` 和 `*_override.tf` 的特殊合并机制。入门项目不需要依赖它，应通过变量和模块接口表达差异，避免同一配置的行为藏在隐式覆盖里。

`*.tftest.hcl` 是测试文件，`*.tfbackend` 可用于 Backend 参数，`.terraform.lock.hcl` 是 Provider 依赖锁文件；这些都不按普通 `.tf` 资源定义加载。

## 不创建资源的语法练习

在一个空实验目录中创建如下完整 `main.tf`，只包含 locals 和 outputs：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"
}

locals {
  services = {
    web = { port = 8080, enabled = true }
    api = { port = 9000, enabled = false }
  }
}

output "web_port" {
  value = local.services["web"].port
}
```

可以用 console 观察类型与值：

```bash
terraform console
```

```text
> local.services.web.port
8080
> type(local.services)
> toset(["web", "web", "api"])
> exit
```

控制台适合检查表达式，不会把 `terraform_data` 或 Provider 资源自动创建出来。若当前目录使用远程 Backend 或外部 Provider，console 的环境准备要求也会随之改变。

## 常见错误

- `Missing newline after argument`：把多个块内参数挤在一行，或大括号层级错误。对象里的逗号写法不等于块内参数的写法。
- `Reference to undeclared input variable`：引用了 `var.name`，却未在当前模块声明它。
- `Reference to undeclared resource`：资源的类型、逻辑名或模块层级不对。
- 把块写成对象：例如 `lifecycle = { ... }`，不符合该字段的语法。
- 在 `.tfvars` 中写 `var.name = ...`：赋值文件直接写 `name = ...`。

## 练习

1. 把上面的 outputs 移入 `outputs.tf`，解释为什么取值不变。
2. 比较 `local.services.web.port`、`local.services["web"].port` 的结果。
3. 说明为什么不能用 `null` 代表一个还没创建资源的 ID。

## 参考资料

- [配置语法](https://developer.hashicorp.com/terraform/language/syntax/configuration)
- [文件与模块](https://developer.hashicorp.com/terraform/language/files)
- [类型与值](https://developer.hashicorp.com/terraform/language/expressions/types)
- [引用](https://developer.hashicorp.com/terraform/language/expressions/references)
- [字符串与模板](https://developer.hashicorp.com/terraform/language/expressions/strings)
- [Console 命令](https://developer.hashicorp.com/terraform/cli/commands/console)

上一篇：[[IaC/terraform/01_terraform_基础概念与第一个项目|基础与第一个项目]] · 下一篇：[[IaC/terraform/03_terraform_变量与输出|变量、locals 与 outputs]]。
