---
title: 15_terraform_模块文档生成
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform Docs
  - terraform-docs
---

# 15_terraform_模块文档生成

## 从 CMS 教学模块生成接口文档

`terraform-docs` 从 Terraform 模块声明中提取依赖、Provider、资源、输入和输出，适合保持 README 中的接口表与代码同步。它不能解释设计背景、通知验证或升级步骤，也不会执行 Terraform Plan 或访问云端。

本篇使用 [[IaC/terraform/10_terraform_模块开发与复用|第 10 篇]] 同一个 `modules/cms-contacts/` 模块，接口统一如下：必需输入 `contacts` 和 `contact_groups`；输出 `contact_names` 与 `group_names`。生产来源是 `monitoring/modules/cloud-monitor-alerts/main.tf`、`monitoring/modules/cloud-monitor-alerts/variables.tf`、`monitoring/modules/cloud-monitor-alerts/versions.tf`，已裁剪为 CMS 联系人和联系人组能力。文档配置与调用示例为教学新增，terraform-docs 生成命令尚未执行。

## 模块 README 与调用示例

在模块目录 `10-cms-contacts/modules/cms-contacts/README.md` 手工维护说明和生成标记。完整示例保存于模块内的 `10-cms-contacts/modules/cms-contacts/examples/basic/main.tf`：

```markdown
# cms-contacts

管理 AliCloud CMS 告警联系人及联系人组。组成员通过联系人名称引用由模块管理的联系人。

完整调用例子见模块内的 `examples/basic/main.tf`。联系人邮箱需由收件人按 AliCloud 流程激活；API 创建成功不代表邮箱已激活或通知已送达。

<!-- BEGIN_AUTOMATED_TF_DOCS_BLOCK -->
<!-- END_AUTOMATED_TF_DOCS_BLOCK -->

## Design and operational notes

- Provider 配置由 root module 提供；调用方通过 providers 映射选择目标账号与区域。
- 请勿在 README 或提交的输出中记录真实邮箱、账号 ID 或凭证。
- 在授权环境中审查计划并核对联系人激活状态。
```

`examples/basic/main.tf`：

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

provider "alicloud" {
  region = "cn-shanghai"
  # 读取受控环境中的 ALIBABA_CLOUD_* 凭证，不要在示例中填写密钥。
}

module "lab_contacts" {
  source = "../.."

  contacts = {
    ops = {
      alarm_contact_name = "terraform-lab-ops"
      describe           = "terraform-lab 测试联系人"
      channels_mail      = "terraform-lab@example.invalid"
    }
  }

  contact_groups = {
    platform = {
      alarm_contact_group_name = "terraform-lab-platform"
      contacts                 = ["terraform-lab-ops"]
    }
  }
}

output "contact_names" {
  description = "示例中创建的联系人名称"
  value       = module.lab_contacts.contact_names
}

output "group_names" {
  description = "示例中创建的联系人组名称"
  value       = module.lab_contacts.group_names
}
```

该例是一个独立 root module，文件位于 `10-cms-contacts/modules/cms-contacts/examples/basic/main.tf`，`source = "../.."` 相对示例目录指向模块根目录。如果把示例改放在项目根的 `10-cms-contacts/examples/basic/main.tf`，则 `source` 应改为 `../../modules/cms-contacts`。若读者运行它，会管理测试名称的 CMS 联系人与组；不要使用生产工作区或生产联系资料；运行前将 `.invalid` 邮箱替换为自己控制的测试邮箱。邮箱加入联系人后可能需要收件人完成激活流程，模块与 API 成功不代表通知已经验证。

## 配置自动注入

在 `modules/cms-contacts/.terraform-docs.yml` 放置：

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

output-values:
  enabled: false
```

在 `10-cms-contacts/` 项目根目录执行如下命令时，配置路径和输入模块目录均明确指定：

```bash
terraform-docs --config ./modules/cms-contacts/.terraform-docs.yml ./modules/cms-contacts
git diff -- modules/cms-contacts/README.md
```

`output.file` 相对被处理的模块目录定位 README。匹配的 begin/end 标记之间会替换成生成表格；人工说明保留在标记之外。标记不一致时，inject 可能追加另一块表格，因此生成后要检查 diff 和 README 结构。

## 使用 Go template 排列生成内容

当需要调整章节顺序并在接口表前加入可运行示例时，在前面的 `.terraform-docs.yml` 配置中添加以下 `content`。这是前一份配置的扩展，保留既有 `sections.show` 与 `output.template`：

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

`include` 的文件路径相对被处理的模块目录，因此这里引用 `modules/cms-contacts/examples/basic/main.tf`。README 会显示该文件的实际 HCL；当维护者把示例目录移动到项目根目录时，还需一并调整 include 路径和 HCL `source`。`sections.show` / `hide` 优先决定哪些数据可用：若关闭 Providers，模板中的 `{{ .Providers }}` 不会恢复该章节。

若只需要待填写的参数骨架，可以将上面的 `content` **替换**为以下模板：

````yaml
content: |-
  {{ .Requirements }}

  ## Parameter skeleton

  ```hcl
  module "example" {
    source = "<module-path>"
    {{- if .Module.RequiredInputs }}
    # Required inputs: replace placeholders with actual values
    {{- range .Module.RequiredInputs }}
    {{ .Name }} = <REQUIRED_VALUE>
    {{- end }}
    {{- end }}
    {{- if .Module.OptionalInputs }}
    # Optional inputs: defaults come from the module declarations
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

此骨架对本模块会列出 `contacts` 与 `contact_groups` 必需输入，`<REQUIRED_VALUE>` 是提示而非有效 HCL。terraform-docs 0.20 的 `GetValue` 提供选填输入的声明默认值；对象形状、互斥字段或敏感内容仍由维护者核对。完整的 `examples/basic/main.tf` 更适合作为可运行调用示例。

预期生成区域列出 AliCloud Provider 需求、联系人与联系人组资源、两个复杂类型输入及 `contact_names`、`group_names` 输出。具体 Markdown 格式由所固定的 terraform-docs 版本决定。本篇未安装或运行工具，也没有生成一份假装真实产出的表格。

## 配置含义与边界

| 配置 | 用途 |
|---|---|
| `formatter` | 选择 Markdown 表格格式 |
| `version` | 限制 terraform-docs 工具自身版本，不选择 Terraform 或 Provider 版本 |
| `sections.show` | 指定生成章节 |
| `output.file` / `mode` | 写入 README 并仅替换标记内区域 |
| `output.template` | 提供注入边界 |
| `sort.by` | 名称排序，减少无关 diff |
| `settings.required/type/sensitive` | 展示输入是否必需、类型与敏感标记 |
| `output-values.enabled` | 关闭真实 State output 值读取 |

`sensitive = true` 影响文档标记，不会扫描或脱敏人工文本。接口文档不需要真实联系人、组名或 State 输出值；避免打开实际 output-values 或把敏感输出复制进 README。

如果模块增加必需变量，terraform-docs 可以列在 Inputs 表中，但无法选择业务值。完整调用例子应随接口一并更新；不要用空赋值生成看似可运行的示例。若需使用 Go template 输出调用骨架，应明确必填项为占位符，并说明它不是完整可执行配置。

## 在持续集成中检查文档一致性

在教学项目中可增加下列文档一致性检查；生产仓库目前没有已确认的 CI 配置，因此这是新增设计示意：

```bash
terraform-docs --config ./modules/cms-contacts/.terraform-docs.yml ./modules/cms-contacts
git diff --exit-code -- modules/cms-contacts/README.md
```

第一条命令按当前模块接口刷新文档；第二条命令在工作树文档不一致时失败。该流程不等于 Terraform 配置验证、Provider 权限检查或部署测试。CI 中应固定 terraform-docs 版本、配置路径和工作目录，并确保示例、README 和实际变量定义一起审查。

## 常见问题

- 没有变量或输出章节：目标目录不对，或 `.terraform-docs.yml` 隐藏了相关 section。
- README 被整份覆盖：使用了 `replace`，或目标文件/标记配置不正确。
- 连续生成反复变化：核对工具版本、排序、行尾和配置文件。
- 输出表中没有描述：在 Terraform variable/output 声明中补全准确的 `description`。
- README 泄漏联系资料或凭证：自动生成工具不会代替内容脱敏；立即从源文档与提交 diff 中清除，再按相关凭证处理流程执行。

## 练习

1. 只修改 `contacts` 的 description，再生成文档；说明接口描述变化为何不等于 CMS 资源行为变化。
2. 给模块增加可选输入，比较 README 输入表和 `examples/basic/main.tf`，确保默认行为有说明。
3. 连续生成两次并审查 `git diff`；指出稳定生成与云端配置正确性分别由什么证据支持。
4. 解释为什么不能把联系人真实邮箱、State output 值或密钥放进生成模板。

## 参考资料

- [terraform-docs 项目](https://github.com/terraform-docs/terraform-docs)
- [配置文件](https://terraform-docs.io/user-guide/configuration/)
- [输出注入配置](https://terraform-docs.io/user-guide/configuration/output/)
- [内容模板](https://terraform-docs.io/user-guide/configuration/content/)
- [terraform-docs 0.20.0 Input.GetValue 实现](https://github.com/terraform-docs/terraform-docs/blob/v0.20.0/terraform/input.go)
- [工具版本约束](https://terraform-docs.io/user-guide/configuration/version/)
- [输出值配置](https://terraform-docs.io/user-guide/configuration/output-values/)

上一篇：[[IaC/terraform/14_terraform_容器管理实战|ACK、Kubernetes 与 Helm]] · 返回：[[IaC/terraform/README|系列学习路线]]。
