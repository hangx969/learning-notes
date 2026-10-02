---
title: Terraform基础-terraform-docs 模块文档生成
tags:
  - IaC
  - terraform
  - terraform-docs
date: 2026-10-02
aliases:
  - Terraform Docs
  - terraform-docs
---

# Terraform基础-terraform-docs 模块文档生成

## terraform-docs 做什么

[terraform-docs](https://github.com/terraform-docs/terraform-docs) 从 Terraform 模块代码中提取接口信息，生成 Markdown、JSON 等文档格式。

常见生成内容包括：

- Terraform/Provider 版本要求。
- Provider 和模块调用列表。
- 管理的资源类型。
- 输入变量的类型、默认值、描述、是否必需。
- 输出的名称和描述。

它是独立工具，不是 Terraform CLI 的一个子命令，也不是访问云端资源的验证工具。它不会自动解释模块的设计意图、部署风险和升级步骤。

## 安装与版本确认

macOS 可使用：

```bash
brew install terraform-docs
terraform-docs version
```

其他系统从 [官方 Releases](https://github.com/terraform-docs/terraform-docs/releases) 下载匹配系统和 CPU 架构的包，核对校验信息，将二进制加入 `PATH`。

本篇配置按 0.20+ 的格式编写。团队应固定经过检查的工具版本，避免同一份代码在不同执行环境生成不同表格。

下文 `.terraform-docs.yml` 中的 `version` 是**对运行中的 terraform-docs 的版本约束**，不会替你安装或选择二进制；它也不是 Terraform CLI 或模块版本。

## 先生成到终端

使用 [[IaC/terraform/terraform-modules|模块实验]] 的 app-config：

```bash
terraform-docs markdown table ./modules/app-config
```

目标是模块目录，不是某个 `.tf` 文件。默认处理目标目录的模块接口，不需要初始化远程 Backend，也不需要云凭证。

变量和 output 没有 description 时，工具不能凭空补上准确说明。先把接口描述写好，再自动生成，效果比生成后手工修表格更稳定。

## 将生成结果注入 README

人工说明与自动接口表应分开，让重复生成只更新指定区域。

在 `modules/app-config/README.md` 写入：

```markdown
# app-config

为单个服务生成 JSON 配置。生成路径由调用者提供，模块不写入自己的下载缓存。

完整调用示例维护在 examples/basic/main.tf。

<!-- BEGIN_AUTOMATED_TF_DOCS_BLOCK -->
<!-- END_AUTOMATED_TF_DOCS_BLOCK -->

## Design and upgrade notes

说明命名规则、输入约束和地址迁移要求。
```

然后创建 `modules/app-config/examples/basic/main.tf`，让用法与 [[IaC/terraform/terraform-modules|模块接口]] 保持一致：

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

module "web" {
  source = "../../"

  name             = "web"
  environment      = "dev"
  port             = 8080
  output_directory = abspath("${path.root}/generated")
}

output "file_path" {
  description = "示例生成的配置文件路径"
  value       = module.web.file_path
}
```

此 source 相对 examples/basic 目录定位到 app-config。文档生成不执行这个例子；读者单独运行它时，它是一个独立 root module，有自己的状态和执行目录。

### 最小可用配置

在模块目录创建 `.terraform-docs.yml`：

```yaml
formatter: markdown table
version: '>= 0.20.0'
header-from: main.tf
footer-from: ''

sections:
  show:
    - requirements
    - providers
    - resources
    - inputs
    - outputs

output:
  file: README.md
  mode: inject
  template: |-
    <!-- BEGIN_AUTOMATED_TF_DOCS_BLOCK -->
    {{ .Content }}
    <!-- END_AUTOMATED_TF_DOCS_BLOCK -->

sort:
  enabled: true
  by: name

settings:
  anchor: true
  default: true
  description: true
  escape: true
  hide-empty: false
  html: true
  indent: 2
  lockfile: true
  required: true
  sensitive: true
  type: true
```

执行：

```bash
terraform-docs --config ./modules/app-config/.terraform-docs.yml ./modules/app-config
git diff -- modules/app-config/README.md
```

`output.file` 相对被处理的模块目录解析。输出模板中的 begin/end 标记必须与 README 一致；保留原来的自定义标记可以避免误把另一块区域当作生成区域。

| 配置 | 用途 |
|---|---|
| `formatter` | 选择输出形式，本例为 Markdown 接口表 |
| `version` | 检查 terraform-docs 本身的版本是否允许运行 |
| `sections.show` | 明确保留哪些章节；没有列出的章节不进入本例生成区 |
| `output.file` / `mode` | 指定文件和注入方式，控制人工区是否保留 |
| `output.template` | 指定注入标记和生成内容的位置 |
| `sort.by` | 用名称稳定排序，减少无关 diff |
| `settings.required` / `type` / `sensitive` | 在接口表中显示是否必需、类型和敏感标记 |

其他 settings 控制表格的转义、锚点、默认值等展示形式，不会替模块补充业务校验。

预期生成区包含四个必需输入 `name`、`environment`、`port`、`output_directory`，以及 `file_path`、`content_sha256` 两个输出。人工编写的开头和 Design and upgrade notes 应保留。连续生成两次时，第二次应没有新 diff。

如果原文件没有匹配的标记，inject 会追加生成区；目标文件不存在时则会创建它。因此标记不一致常表现为重复文档，而不是立即报错。

### inject 与 replace

| 模式 | 行为 | 使用场景 |
|---|---|---|
| `inject` | 替换标记之间的生成内容 | README 同时有人工作品和自动表格 |
| `replace` | 用生成结果替换整个目标文件 | 单独维护全自动生成文档 |

使用 replace 前应明确整个文件属于生成内容。接口表改动直接修改 `.tf` 中的声明，再生成，不在自动区手工写长期需要保留的信息。

## 自定义内容模板

需要调整章节顺序时可以增加 content。例如在前面的配置中补充：

```yaml
content: |-
  {{ .Requirements }}

  {{ .Providers }}

  {{ .Resources }}

  {{ .Inputs }}

  {{ .Outputs }}
```

这些字段是 terraform-docs 的 Go template 内容，不是 Terraform 的 `${...}` 插值。

### 把真实调用示例嵌入生成区

可以使用 `include` 读取前面维护的可运行示例，避免把没有默认值的 RequiredInputs 自动拼成看似完整、实际缺少业务参数的调用。把前面的 content 替换为：

````yaml
content: |-
  {{ .Requirements }}

  ## Usage

  ```hcl
  {{ include "examples/basic/main.tf" }}
  ```

  {{ .Providers }}

  {{ .Resources }}

  {{ .Inputs }}

  {{ .Outputs }}
````

include 路径相对被处理的模块目录。README 中展示的是 examples/basic/main.tf 的内容，所以其中 `source = "../../"` 仍对应示例目录的位置；从其他目录复制运行时需要调整 source。

`sections.show` / `hide` 优先于 content 模板。模板里写了 `{{ .Providers }}`，但配置隐藏了 providers 时，仍不会显示该节。工具还提供 `.Module` 原始接口对象供复杂模板使用；输入值该怎么选、哪些参数互斥仍需维护者根据模块语义编写。

### 可选：生成参数骨架

只想列出模块的必需和可选参数时，可以遍历 `.Module.RequiredInputs` / `.Module.OptionalInputs`。下面的 content 是前一个 content 的**替代模板**，输出的是待填写骨架，不是可运行调用；`<module-path>`、`<REQUIRED_VALUE>` 都必须由维护者替换。

````yaml
content: |-
  {{ .Requirements }}

  ## Parameter skeleton

  ```hcl
  module "example" {
    source = "<module-path>"
    {{- if .Module.RequiredInputs }}
    # Required variables: fill in actual values
    {{- range .Module.RequiredInputs }}
    {{ .Name }} = <REQUIRED_VALUE>
    {{- end }}
    {{- end }}
    {{- if .Module.OptionalInputs }}
    # Optional variables: defaults from module code
    {{- range .Module.OptionalInputs }}
    {{ .Name }} = {{ .GetValue }}
    {{- end }}
    {{- end }}
  }
  ```

  {{ .Providers }}

  {{ .Resources }}

  {{ .Inputs }}

  {{ .Outputs }}
````

按 terraform-docs 0.20 的接口，GetValue 输出声明的默认值；必需输入没有默认值时，GetValue 返回空字符串。直接把所有必需参数写成 `{{ .Name }} = {{ .GetValue }}`，可能生成 `name =` 这样的缺值行，因此上面明确放置占位符。复杂对象、显式 null、敏感默认值和互斥参数仍需人工核对；骨架只帮助发现接口变化，完整调用优先维护为 examples 中的代码。

## 不读取实际 State 输出

接口文档通常只需要 outputs 的描述，不需要部署时的真实值：

```yaml
output-values:
  enabled: false
```

不要为了 README 打开真实 output-values，再把资源地址、内部域名或敏感值提交出去。生成文档与读取部署结果是不同用途。

`settings.sensitive` 控制变量敏感性标记展示，不是对任意文档内容做脱敏。

## 递归生成

多个模块可按工具约定开启递归模式：

```yaml
recursive:
  enabled: true
  path: modules
```

采用前先确认调用根目录、子模块配置发现方式和目标文件范围。目录复杂时逐个模块生成更容易观察差异；不要第一次就对整个仓库 replace。

工具会自动发现 `.terraform-docs.yml`，优先查模块根目录及其 `.config/`，再查当前目录及其 `.config/`，最后查用户级配置；命令行选项可覆盖配置。开始使用统一模板时，显式 `--config` 更容易确认读取的是哪份文件。添加配置后再次运行先前的 `markdown table` 命令，也可能按配置写入 README，不能再假定所有调用都只输出终端。

旧模板中的 `sections.hide-all` / `show-all` 已在历史版本中移除。本系列使用 `sections.show` / `hide`，不要复制旧字段再假定仍生效。

## 在协作流程里使用

1. 修改变量、outputs 或版本要求。
2. 运行 terraform-docs。
3. review README 和源码差异。
4. 重复生成，确认结果稳定。
5. 在 CI 中检查生成区是否与代码一致。

简单 CI 检查片段：

```bash
terraform-docs --config ./modules/app-config/.terraform-docs.yml ./modules/app-config
git diff --exit-code -- modules/app-config/README.md
```

这是文档一致性检查，不是 Terraform 配置验证或真实部署测试。生成过程中如工具版本不同，先核对 formatter、配置和版本，避免无意义的整页重排。

## 常见问题

- 没有生成输入变量：目标目录不对，或变量实际在另一个模块中。
- 说明缺失：对应 variable/output 没有 description，或 sections 设置隐藏了部分内容。
- README 人工说明被覆盖：使用了 replace 或错误的标记范围。
- 反复产生 diff：工具版本、排序、行尾或模板不一致。
- 变量默认值被误认为运行值：工具提取的是配置接口，不是某次 tfvars 或真实部署的最终输入。

## 练习

1. 只修改 port 的 description，再生成文档，说明它是否改变资源行为。
2. 给模块增加一个有默认值的输入，观察接口表与参数骨架，补充实际调用示例。
3. 连续生成两次，确认第二次没有 diff，且 README 的人工设计说明仍存在。

## 参考资料

- [terraform-docs GitHub](https://github.com/terraform-docs/terraform-docs)
- [配置文件](https://terraform-docs.io/user-guide/configuration/)
- [Output 注入配置](https://terraform-docs.io/user-guide/configuration/output/)
- [Content 模板](https://terraform-docs.io/user-guide/configuration/content/)
- [工具版本约束](https://terraform-docs.io/user-guide/configuration/version/)
- [output-values 配置](https://terraform-docs.io/user-guide/configuration/output-values/)
- [递归生成配置](https://terraform-docs.io/user-guide/configuration/recursive/)
- [terraform-docs 0.20 Input.GetValue 实现](https://github.com/terraform-docs/terraform-docs/blob/v0.20.0/terraform/input.go)
- [terraform-docs 0.20 Module 模板接口](https://github.com/terraform-docs/terraform-docs/blob/v0.20.0/terraform/module.go)

上一篇：[[IaC/terraform/terraform-container-management|容器实战]] · 返回：[[IaC/terraform/README|系列学习路线]]。
