---
title: 04_terraform_表达式函数与模板
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform表达式
  - Terraform函数与模板
---

# 04_terraform_表达式函数与模板

## 表达式解决什么问题

参数不必总是固定值。命名规则、环境开关、配置清单和模块输入，都可以由表达式从原始输入中计算出来。

Terraform 表达式负责计算值。它没有 Shell 那样的一连串赋值执行流程；也不要把 for 表达式理解成“循环执行创建命令”。资源实例的批量创建由 `count` / `for_each` 负责。

## 条件表达式

```hcl
locals {
  replica_count = var.environment == "prod" ? 3 : 1
}
```

结构为 `条件 ? true时的值 : false时的值`。`var.environment` 需要在当前模块声明，两侧结果必须具有相同类型或能转换为兼容类型。

下面是常见误区：

```hcl
# 避免用字符串表示未启用的副本数
locals {
  replicas = var.enabled ? 3 : "disabled"
}
```

Terraform 可以把这里的数字转换为字符串，因此启用时可能得到 `"3"`，而非预期的 number。让“是否启用”和“副本数”保持不同字段更容易理解。对于本系列的 1.7 基线，不要依靠 `&&` / `||` 保护可空对象的属性访问，应先用明确的条件表达式判断整体是否为 null。

## for 表达式：变换集合

以下 locals 可以在空实验目录中独立使用：

```hcl
locals {
  services = {
    web = { port = 8080, enabled = true }
    api = { port = 9000, enabled = true }
    old = { port = 7000, enabled = false }
  }

  names = [for name, service in local.services : upper(name)]

  enabled_services = {
    for name, service in local.services : name => service
    if service.enabled
  }

  endpoints = {
    for name, service in local.enabled_services : name => "127.0.0.1:${service.port}"
  }
}
```

- 方括号形式产出 tuple，可按上下文转换为 list。
- 大括号形式产出 object，`=>` 左边是 key，右边是 value。
- `if` 在产出元素前做过滤。
- 从 map/object 按 key 遍历时，结果有确定的 key 排序规则；不要让 set 的顺序承担业务意义。

在包含这些 locals 的目录中打开 `terraform console`。预期 `local.names` 为 `["API", "OLD", "WEB"]`，`local.endpoints` 只有 api 和 web 两项。`local.services` 是原始输入，没有因为表达式变换而被修改。

### 重复 key 和分组

```hcl
locals {
  users = {
    alice = { role = "reader" }
    bob   = { role = "reader" }
    carol = { role = "writer" }
  }

  users_by_role = {
    for name, user in local.users : user.role => name...
  }
}
```

同一角色可能对应多个用户。末尾的 `...` 开启分组模式，得到 `reader` 对应一组用户名，而不是因重复 key 报错。业务要求唯一 key 时，应修正输入，不要用分组掩盖错误。

## 常用函数

| 函数 | 用途 | 例子 |
|---|---|---|
| `lower` / `upper` / `trimspace` | 字符串标准化 | `lower(var.project)` |
| `format` / `join` | 组装文本 | `join(",", ["web", "api"])` |
| `length` / `contains` | 集合检查 | `contains(["dev", "prod"], var.env)` |
| `toset` / `tolist` / `tomap` | 明确类型转换 | `toset(var.names)` |
| `merge` | 合并 map/object，后者覆盖同名 key | `merge(local.defaults, var.tags)` |
| `lookup` | 从 map 读取 key 并提供默认值 | `lookup(var.tags, "owner", "unknown")` |
| `try` | 捕获表达式求值时的动态错误 | `try(local.raw.port, 8080)` |
| `can` | 判断表达式能否成功求值 | `can(regex("^[a-z]+$", var.name))` |
| `coalesce` | 第一个非 null、非空字符串的值 | `coalesce(var.name, "demo")` |
| `flatten` | 展平嵌套序列 | `flatten([["a"], ["b", "c"]])` |
| `jsonencode` / `yamlencode` | 从结构化值生成文本 | `jsonencode(local.config)` |
| `file` / `templatefile` | 读取静态文件或渲染模板 | `templatefile("${path.module}/app.tftpl", {...})` |
| `cidrsubnet` | 从网段计算子网 | `cidrsubnet("10.0.0.0/16", 8, 2)` |

`try` 不能让未声明资源或非法语法变合法，也不会把 unknown 当成错误：`try(新资源的未知属性, 默认值)` 通常仍是 unknown。它适合在一个局部位置把可选结构规范化，不适合包住所有字段来吞掉设计错误。`lookup` 的默认值针对不存在的 key；key 存在但 value 为 null 时，不会自动改用默认值。

### 浅合并，不是递归合并

```hcl
locals {
  merged = merge(
    { app = { port = 8080, log_level = "info" } },
    { app = { port = 9000 } }
  )
}
```

第二个对象会整体覆盖结果中的 `app`，不会自动保留 `log_level`。如果需要递归合并，应按层次显式调用 merge，并说明字段覆盖规则。

## 完整实验：生成 Kubernetes YAML

本实验只生成 YAML 文件，不连接或修改集群。创建独立目录：

```bash
mkdir -p ~/terraform-labs/04-expressions-yaml
cd ~/terraform-labs/04-expressions-yaml
```

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

### main.tf

```hcl
variable "environment" {
  type     = string
  default  = "dev"
  nullable = false
}

variable "service_name" {
  type     = string
  default  = "web"
  nullable = false
}

locals {
  labels = {
    app         = var.service_name
    environment = var.environment
  }

  deployment = {
    apiVersion = "apps/v1"
    kind       = "Deployment"
    metadata = {
      name   = var.service_name
      labels = local.labels
    }
    spec = {
      replicas = var.environment == "prod" ? 3 : 1
      selector = {
        matchLabels = { app = var.service_name }
      }
      template = {
        metadata = { labels = local.labels }
        spec = {
          containers = [{
            name  = var.service_name
            image = "nginx:1.30.5-alpine"
            ports = [{ containerPort = 80 }]
          }]
        }
      }
    }
  }
}

resource "local_file" "deployment" {
  filename        = "${path.module}/deployment.yaml"
  content         = yamlencode(local.deployment)
  file_permission = "0644"
}

output "replicas" {
  value = local.deployment.spec.replicas
}
```

实验步骤：

```bash
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
cat deployment.yaml
terraform console
```

预期首次计划创建一个 `local_file.deployment`。apply 后目录中出现 `deployment.yaml`，其 Deployment 名为 web，副本数为 1；`yamlencode` 可能为 key 加上双引号，应按 YAML 的值与层级阅读，不必与手写排版逐字一致。

在 console 中验证往返转换：

```text
> yamldecode(yamlencode(local.deployment)).spec.replicas
1
> cidrsubnet("10.0.0.0/16", 8, 2)
"10.0.2.0/24"
> exit
```

退出 console 后，改变环境输入并审查计划：

```bash
terraform plan -var='environment=prod' -out=prod.tfplan
terraform show prod.tfplan
terraform apply prod.tfplan
terraform output replicas
cat deployment.yaml
```

预期文件中的副本数变成 3，environment 标签也变为 prod。`local_file` 因 content 变化被替换，这仍然只是生成本地文件；集群部署见 [[IaC/terraform/14_terraform_容器管理实战|容器管理实战]]。

`yamldecode` 解析一个 YAML 文档，不能直接把包含多个 `---` 文档的文件当成单个 manifest。应用多份资源时应显式拆分和管理各个对象。

实验结束后清理生成文件：

```bash
terraform plan -destroy -var='environment=prod' -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

## templatefile：保留文本模板

JSON/YAML 优先编码函数，Nginx 配置、cloud-init 或脚本等文本可使用模板。

创建另一个独立目录，复制刚才只含 Provider 要求的 `versions.tf`：

```bash
mkdir -p ~/terraform-labs/04-templates
cd ~/terraform-labs/04-templates
cp ~/terraform-labs/04-expressions-yaml/versions.tf versions.tf
```

先创建 `app.conf.tftpl`：

```text
service=${service_name}
port=${port}
%{ for name in upstreams ~}
upstream=${name}
%{ endfor ~}
```

使用相同的 Local Provider 要求，`main.tf` 完整内容：

```hcl
resource "local_file" "config" {
  filename        = "${path.module}/app.conf"
  file_permission = "0644"
  content = templatefile("${path.module}/app.conf.tftpl", {
    service_name = "web"
    port         = 8080
    upstreams    = ["api", "worker"]
  })
}
```

模板中的变量来自第二个参数，不会自动继承所有 `var.*` 和 `local.*`。`~` 用于控制模板指令周围的空白。

文件都准备好后再运行：

```bash
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
cat app.conf
```

预期文本为：

```text
service=web
port=8080
upstream=api
upstream=worker
```

结束时同样生成、查看并执行删除计划：`terraform plan -destroy -out=destroy.tfplan`、`terraform show destroy.tfplan`、`terraform apply destroy.tfplan`。生成的 `app.conf` 应被删除，作为输入的 `app.conf.tftpl` 仍保留。

`file` 和 `templatefile` 读取的文件必须在 Terraform 运行开始时已经存在。它们不会因为增加 `depends_on` 就变成“等待某个资源创建文件后再读”的资源操作。

## dynamic：生成重复嵌套块

for 表达式生成值，dynamic 生成资源 schema 已支持的重复嵌套块。

下面是 Docker 容器资源内部的替换片段，需要容器实战中的 Provider、`docker_image.nginx` 和一个已声明的 `port_mappings` 变量：

```hcl
dynamic "ports" {
  for_each = var.port_mappings
  iterator = mapping

  content {
    internal = mapping.value.internal
    external = mapping.value.external
    ip       = "127.0.0.1"
  }
}
```

对应变量声明：

```hcl
variable "port_mappings" {
  type = map(object({
    internal = number
    external = number
  }))
  default = {
    http = { internal = 80, external = 8080 }
  }
}
```

- dynamic 的 label 是目标嵌套块名，本例为 `ports`。
- `iterator` 指定每次迭代的引用名，避免多层动态块中名称难以辨认。
- dynamic 不能凭空增加 Provider 不支持的字段。
- 不能用 dynamic 生成 `lifecycle`、`provisioner` 等需要先处理的元参数块。
- 只有一个固定块时，直接写出块更容易阅读。

## 时间和文件函数的变更陷阱

- `timestamp()` 会变化，把它写到普通资源参数可能导致每次 plan 都有差异。它不适合充当稳定的资源命名。
- `uuid()` 不是持久身份；需要稳定随机值时使用 Random Provider 资源。
- `file()` 的依赖来自运行前文件，而不是 Terraform 图中的资源创建顺序。
- `path.module` 是当前模块的位置；远程模块缓存不适合当多人共享的可写工作区。

## 练习

1. 给 YAML 实验增加一个 `labels` map，明确用户标签和内部标签谁优先。
2. 从三个服务的 map 中筛选 enabled 服务，返回一个服务名到端口的 map。
3. 用 `terraform console` 观察 merge 嵌套对象为什么会丢失字段。

## 常见问题

- 模板文件找不到：先检查当前实验目录和 `path.module`，模板必须提前写入磁盘。
- `Duplicate object key`：for 表达式生成了重复 key，按业务需要修正输入或明确使用分组模式。
- `Inconsistent conditional result types`：条件两侧返回了不能统一的结构，先设计清楚输出类型。
- YAML 文件没变化：只运行 plan 不会改写文件；apply 保存的计划后再检查磁盘内容。

## 参考资料

- [条件表达式](https://developer.hashicorp.com/terraform/language/expressions/conditionals)
- [for 表达式与分组](https://developer.hashicorp.com/terraform/language/expressions/for)
- [函数索引](https://developer.hashicorp.com/terraform/language/functions)
- [try 的错误捕获范围](https://developer.hashicorp.com/terraform/language/functions/try)
- [lookup 的默认值](https://developer.hashicorp.com/terraform/language/functions/lookup)
- [templatefile](https://developer.hashicorp.com/terraform/language/functions/templatefile)
- [yamldecode](https://developer.hashicorp.com/terraform/language/functions/yamldecode)
- [dynamic blocks](https://developer.hashicorp.com/terraform/language/expressions/dynamic-blocks)

上一篇：[[IaC/terraform/03_terraform_变量与输出|变量与输出]] · 下一篇：[[IaC/terraform/05_terraform_提供者版本与认证|Provider、版本与认证]]。
