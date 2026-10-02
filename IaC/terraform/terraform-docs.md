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
# Terraform基础-terraform-docs 模块文档生成

为单个服务生成 JSON 配置。生成路径由调用者提供，模块不写入自己的下载缓存。

## Usage

示例调用和环境约定由维护者编写。

<!-- BEGIN_AUTOMATED_TF_DOCS_BLOCK -->
<!-- END_AUTOMATED_TF_DOCS_BLOCK -->

## Design and upgrade notes

说明命名规则、输入约束和地址迁移要求。
```

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

### 自动拼出调用参数示例

下例展示基于 RequiredInputs/OptionalInputs 的模板。替换模块来源占位符后才能作为实际调用示例，复杂对象默认值仍应人工核对。

````yaml
content: |-
  {{ .Requirements }}

  ## Usage

  ```hcl
  module "example" {
    source = "<module-path>"
    {{- if .Module.RequiredInputs }}
    # Required variables
    {{- range .Module.RequiredInputs }}
    {{ .Name }} = {{ .GetValue }}
    {{- end }}
    {{- end }}
    {{- if .Module.OptionalInputs }}
    # Optional variables
    {{- range .Module.OptionalInputs }}
    {{ .Name }} = {{ .GetValue }}
    {{- end }}
    {{- end }}
  }
  ```

  {{ .Resources }}

  {{ .Inputs }}

  {{ .Outputs }}
````

自动生成的 Usage 可以帮助发现接口变化，但不代替一份实际可运行的模块示例。占位值、敏感输入、可选对象和互斥参数要根据模块语义处理。

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

## 参考资料

- [terraform-docs GitHub](https://github.com/terraform-docs/terraform-docs)
- [配置文件](https://terraform-docs.io/user-guide/configuration/)
- [Output 注入配置](https://terraform-docs.io/user-guide/configuration/output/)
- [Content 模板](https://terraform-docs.io/user-guide/configuration/content/)
- [工具版本约束](https://terraform-docs.io/user-guide/configuration/version/)

上一篇：[[IaC/terraform/terraform-container-management|容器实战]] · 返回：[[IaC/terraform/README|系列学习路线]]。
