# 介绍

- github地址：https://github.com/terraform-docs/terraform-docs。
- 官网地址：https://terraform-docs.io/user-guide/configuration/content/

terraform-docs可以生成terraform module的说明文档，可以以markdown的形式输出。

# 安装

```sh
# 从github release下载压缩包：https://github.com/terraform-docs/terraform-docs/releases/tag/v0.20.0
# tar zxvf解压
# 直接把可执行文件挪到执行目录
sudo cp terraform-docs /usr/local/bin/
```

# 使用

## 模板文件

定义terraform-docs怎么输出module里面的信息：

~~~yaml
formatter: "markdown table" # this is required
version: "0.20"
header-from: main.tf
footer-from: ""
recursive:
  enabled: false
  path: ""
  sections:
  hide: []
  show: []
  hide-all: false # deprecated in v0.13.0, removed in v0.15.0
  show-all: true  # deprecated in v0.13.0, removed in v0.15.0
content: |-
  {{ .Requirements }}
  ## Usage
  Basic usage of this module is as follows:
  ```hcl
  module "example" {
    {{"\t"}} source  = "<module-path>"
      {{- if .Module.RequiredInputs }}
          {{"\n\t"}} # Required variables
          {{- range .Module.RequiredInputs }}
          {{"\t"}} {{ .Name }}  = {{ .GetValue }}
          {{- end }}
          {{- end }}

      {{- if .Module.OptionalInputs }}
          {{"\n\t"}} # Optional variables
          {{- range .Module.OptionalInputs }}
          {{"\t"}} {{ .Name }}  = {{ .GetValue | printf "%s" }}
          {{- end }}
          {{- end }}
  }
  ```
  {{ .Resources }}

  {{ .Inputs }}

  {{ .Outputs }}

output:
  file: README.md
  mode: inject
  template: |-
      <!-- BEGIN_AUTOMATED_TF_DOCS_BLOCK -->
      {{ .Content }}
      <!-- END_AUTOMATED_TF_DOCS_BLOCK -->

output-values:
  enabled: false
  from: ""

sort:
  enabled: true
  by: name

settings:
  anchor: true
  color: true
  default: true
  description: true
  escape: true
  hide-empty: false
  html: true
  indent: 2
  lockfile: true
  read-comments: true
  required: true
  sensitive: true
  type: true
~~~

## 生成README

在命令行中需要指定module目录，才能读取module的信息

```sh
terraform-docs -c .terraform-docs.yml ../modules/build-agents
```

运行后会自动在module目录下生成README.md文件

