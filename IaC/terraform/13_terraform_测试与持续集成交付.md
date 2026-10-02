---
title: 13_terraform_测试与持续集成交付
tags:
  - IaC
  - terraform
  - terraform/basics
  - cicd
date: 2026-10-02
aliases:
  - Terraform测试
  - Terraform CI/CD
---

# 13_terraform_测试与持续集成交付

## 检查能证明什么

生产仓库提供可供测试的联系人模块：`monitoring/modules/cloud-monitor-alerts/main.tf`、`monitoring/modules/cloud-monitor-alerts/variables.tf`、`monitoring/modules/cloud-monitor-alerts/versions.tf`。检查它能验证接口、表达式和预期资源配置；它不能代替目标账号权限检查、CMS API 调用或告警送达验证。

| 层级 | 例子 | 可以说明 | 不能说明 |
|---|---|---|---|
| 格式 | `terraform fmt -check` | HCL 可格式化且格式一致 | Provider schema 与业务行为正确 |
| 配置检查 | `terraform validate` | 初始化后的配置语法和内部引用一致 | 账号权限、配额、平台端状态 |
| 模块逻辑测试 | Terraform test + mock Provider | 已知输入形成预期地址和属性 | 云 API 的真实响应 |
| 授权实验计划/执行 | 真实 Provider 的 plan/apply | 某次身份、区域和输入下的实际行为 | 其他环境和生产可用性 |
| 执行后验收 | 云平台查询及通知测试 | 资源存在且满足用途 | 之后不会漂移 |

本生产仓库没有已查到的 `.github/workflows` 或 `.gitlab-ci` 流水线文件。下方 `.tftest.hcl` 和 CI 片段是为该模块补充的教学测试设计，不是生产已有测试或流水线。本文本轮只做静态阅读与编辑，没有运行 Terraform test。

## 给联系人模块增加离线计划测试

从 [[IaC/terraform/10_terraform_模块开发与复用|第 10 篇模块实验]] 复制 `modules/cms-contacts/` 到独立的 `~/terraform-labs/13-cms-tests/modules/cms-contacts/`，保留相同接口与资源。为固定测试版本，将这份副本的 `versions.tf` 替换为：

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

第 10 篇共享模块的最低约束 `>= 1.266.0` 不保证首次解析到 1.266.0；测试副本使用固定约束后，再初始化、审阅并提交它自己的 `.terraform.lock.hcl`。后续 CI 使用 `-lockfile=readonly`，锁文件变化单独审查。这个测试 root 的锁文件独立于调用 child module 的第 10 篇根目录锁文件。真实生产模块还有更多输入与 CMS 资源，这里仅测试裁剪后的联系人和联系人组。

目录中加入 `tests/contacts.tftest.hcl`：

```hcl
mock_provider "alicloud" {}

variables {
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

run "plans_contact_and_group" {
  command = plan

  assert {
    condition     = alicloud_cms_alarm_contact.contacts["ops"].alarm_contact_name == "terraform-lab-ops"
    error_message = "联系人资源应使用输入中的联系人名称。"
  }

  assert {
    condition     = toset(alicloud_cms_alarm_contact_group.contact_groups["platform"].contacts) == toset(["terraform-lab-ops"])
    error_message = "联系人组应引用本模块联系人名称。"
  }
}
```

`command = plan` 避免测试 run 默认使用 apply。`mock_provider` 让测试使用模拟 Provider 行为而不调用 CMS API；Terraform 仍需取得 Provider schema，所以测试初始化会解析并安装 Provider。断言只检查由输入直接决定的属性，不依赖模拟出来的资源 ID。

若要运行这个独立子模块的教学测试，目录准备后使用：

```bash
terraform -chdir="$HOME/terraform-labs/13-cms-tests/modules/cms-contacts" init -backend=false
# 首次初始化并审阅所生成的 .terraform.lock.hcl 后，将它纳入教学测试代码
terraform -chdir="$HOME/terraform-labs/13-cms-tests/modules/cms-contacts" test
```

预期一个 run 通过。本文没有执行上述命令，具体 Terraform 和 Provider 组合仍须在教学项目自身验证。Mock 测试不能证明邮箱有效、CMS 接受联系人组成员、别名身份正确或通知实际送达。生产中加入或修改邮箱后还需由接收者完成激活，测试代码不能代替该步骤。

## CI 流程示意

以下流程以 `13-cms-tests/` 为教学仓库根目录，检查其中的模块副本；它不代表生产仓库当前配置。锁文件应提交在受控项目中，CI 固定 Terraform 版本，PR 阶段不需要生产密钥：

```yaml
name: terraform-module-checks
on: [pull_request]
jobs:
  module:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.7.5
      - run: terraform -chdir=modules/cms-contacts fmt -check -recursive
      - run: terraform -chdir=modules/cms-contacts init -backend=false -lockfile=readonly
      - run: terraform -chdir=modules/cms-contacts validate
      - run: terraform -chdir=modules/cms-contacts test
```

这是一个教学草稿：读者需按组织批准的 action 来源与版本策略固定 CI action，并确认 Terraform patch 版本、依赖锁文件和初始化行为。没有配置 AliCloud 凭证，且 mock 测试不会创建云资源。使用 GitHub Actions 是示意选择，不表示生产仓库采用该平台。

真实环境集成计划、apply 和平台验收应走单独授权路径：核对 workspace、Backend、AliCloud Provider alias、region 与角色权限；由审批系统审查保存的计划；只在已授权的隔离环境执行。不要把 PR 流水线的成功当作生产变更批准。

## 发布流程与退出码

本地或 CI 的保存计划可以用退出码把“没有差异”“有差异”和“错误”分开。下例需在包含授权 root module 的环境运行；它只捕获 `terraform plan` 的退出码，不会自动批准或 Apply：

```bash
set +e
terraform -chdir="$HOME/terraform-labs/10-cms-contacts" plan -detailed-exitcode -out=tfplan
plan_rc=$?
set -e

case "$plan_rc" in
  0)
    echo "No changes"
    exit 0
    ;;
  2)
    echo "Changes require review"
    terraform -chdir="$HOME/terraform-labs/10-cms-contacts" show tfplan
    ;;
  *)
    echo "Plan failed with exit code $plan_rc" >&2
    exit "$plan_rc"
    ;;
esac
```

退出码 0 表示无差异，1 表示错误，2 表示有差异。人工审查通过后，在同一 root、Workspace 和状态上应用刚审查的 `tfplan`。代码、Provider 锁文件、变量、执行身份或 State 在计划后改变时，丢弃旧文件、重新生成并重新审批；不要让另一个并发运行同时写同一状态。后端状态锁可协助串行化写入，但不能替代团队的运行排队和审批流程。TFE/Cloud remote execution 则由 Workspace Run 承载计划与批准，不要假设可用本地 `tfplan` 文件替代平台流程。

测试和正常部署应使用不同 State。测试若使用 `command = apply`，仍可能真实创建资源，之后清理也可能失败；不能把测试结束等同于资源已删除。

## 常见测试错误

- 测试意外调用云端：确认 `mock_provider` 名称与 child module 的 Provider local name 一致，检查 run 是否明确为 `command = plan`。
- `Unsupported argument`：module 调用字段与 `variables.tf` 不一致。
- 属性在 Plan 中未知：选择由输入直接决定的断言，或为测试设计明确的 mock/override。
- CI 与本地不一致：比对 Terraform 版本、`.terraform.lock.hcl`、工作目录和 init 参数。
- CI 权限失败：确认是不是误把远程计划/Apply 混进静态 PR 检查；检查 TFE workspace 的执行角色、跨账号信任和 RAM 权限。

## 练习

1. 给测试增加第二个联系人和联系人组成员断言，说明它覆盖的是配置值还是云端行为。
2. 将 run 改为 apply，分析测试可能触发的副作用；不要在未授权账号实际运行。
3. 为 CI 设计一个处理 `detailed-exitcode` 的步骤，并区分错误与待审差异。
4. 将 CI 计划发布至独立 TFE workspace 时，分别列出 Backend、Provider 身份和 Provider 缓存需要核对的内容。

## 参考资料

- [Terraform 测试](https://developer.hashicorp.com/terraform/language/tests)
- [测试中的 Mock Provider](https://developer.hashicorp.com/terraform/language/tests/mocking)
- [terraform test 命令](https://developer.hashicorp.com/terraform/cli/commands/test)
- [terraform plan 退出码](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [AliCloud Provider 1.266.0 联系人组资源实现（contacts 为 TypeSet）](https://github.com/aliyun/terraform-provider-alicloud/blob/v1.266.0/alicloud/resource_alicloud_cms_alarm_contact_group.go)
- [Terraform 自动化](https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform)

上一篇：[[IaC/terraform/12_terraform_工作流计划阅读与排错|工作流与 Plan]] · 下一篇：[[IaC/terraform/14_terraform_容器管理实战|ACK、Kubernetes 与 Helm]]。
