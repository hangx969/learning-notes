---
title: Terraform基础-测试与 CI/CD 协作
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

# Terraform基础-测试与 CI/CD 协作

## 检查分几层

| 层级 | 例子 | 能证明什么 | 不能证明什么 |
|---|---|---|---|
| 格式 | `fmt -check` | HCL 能被格式工具处理，格式一致 | Provider schema 和业务行为正确 |
| 配置检查 | `validate` | 初始化后配置语法和内部一致性 | 实际云权限、配额和资源可用性 |
| 逻辑测试 | 原生 test + mock/plan | 输入、表达式、命名与接口断言 | 云 API 的真实实现行为 |
| 集成测试 | 真实 Provider 的 apply 测试 | 在具体实验环境创建和读取结果 | 所有环境和生产流量都可用 |
| 真实计划 | 目标 Backend/身份下 plan | 这次输入下计划的资源动作 | 执行时 API 一定成功 |
| 执行后验收 | 平台查询、业务探测 | 对象存在且满足实际使用要求 | 未来不会漂移 |

把这些层级分清，比往流水线里堆很多工具更重要。一次 mock 测试通过不能写成“云部署验证通过”。

## Terraform 原生测试

Terraform 1.6+ 提供原生测试框架，1.7+ 提供 Provider/resource/data source mock。测试文件通常放在 `tests/`，后缀为 `.tftest.hcl`。

测试通过一个或多个 `run` 执行操作，再通过 assert 检查结果。**默认 run 使用 apply**，可能创建资源；`command = plan` 表示只生成计划。

即使使用 plan，真实 Provider 也可能做认证和读取 API。mock 则模拟 Provider 行为，适合验证模块自己的计算规则，但仍需要安装匹配 schema 的 Provider。

## 给 app-config 模块写测试

使用 [[IaC/terraform/terraform-modules|Module 实验]] 中的 `modules/app-config`。在该子模块中创建：

```text
modules/app-config/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
└── tests/
    └── app.tftest.hcl
```

`app.tftest.hcl` 完整内容：

```hcl
mock_provider "local" {}

variables {
  name             = "web"
  environment      = "dev"
  port             = 8080
  output_directory = "/virtual-test-output"
}

run "renders_expected_configuration" {
  command = plan

  variables {
    port = 9000
  }

  assert {
    condition     = output.file_path == "/virtual-test-output/web.json"
    error_message = "模块输出应指向调用者指定目录中的服务配置。"
  }

  assert {
    condition     = jsondecode(local_file.config.content).port == 9000
    error_message = "配置应使用调用者传入的端口。"
  }

  assert {
    condition     = jsondecode(local_file.config.content).environment == "dev"
    error_message = "配置应保留环境字段。"
  }
}

run "rejects_invalid_port" {
  command = plan

  variables {
    port = 0
  }

  expect_failures = [var.port]
}
```

文件级 `variables` 给出各 run 的公共输入，run 内的 port 覆盖本次输入。assert 中的 `output.file_path` 指的是**当前被测试模块**的输出；这里直接在 app-config 中运行，所以不是根模块的 `config_files`。

这两个测试验证了路径输出接口、传参和非法端口拒绝行为，没有依赖随机 ID 或 mock 的自动生成字符串。`expect_failures = [var.port]` 期望变量的 validation 失败：port=0 被拒绝时该 run 才通过；若误删了校验，测试反而会失败。它不会把所有语法、类型或 Provider 错误都当成成功。

### 运行

读者在模块代码目录执行：

```bash
terraform -chdir=modules/app-config init
terraform -chdir=modules/app-config test
```

`/virtual-test-output` 是供 mock 断言使用的字符串，不需要创建实际目录。mock Provider 不会真的写该文件。

预期两个 run 均通过，目录命名或 port 传递逻辑出错时会显示对应 error_message。这里是预期结果，本文没有执行该测试。此前仅从 `10-modules/` 初始化根模块，并不等于子模块目录已准备好独立运行，因此命令中的模块路径不能省略。

测试状态与正常部署状态分开。真实 apply 测试仍可能创建收费资源，并在结束时尝试清理；清理失败需要人工跟进，不能把“测试结束”当成所有资源已删除。

## 哪些断言适合 plan

- 来自输入变量的名称、端口和标签。
- 已知输入生成的 JSON/YAML 内容。
- 资源/模块实例数量和已知 key。
- validation、precondition 等应拒绝的输入。

新对象的真实 ID、平台计算的地址、实际服务状态，通常不能在 plan 中获得。用真实 apply 或明确的 mock/override 设计断言，并说明测试到底覆盖了哪部分。

本例的 filename、content 都由已知输入配置，plan 可求值；`local_file.config.content_sha256` 则是 Provider 计算属性。mock 不会自动运行真实 Local Provider 的哈希算法，默认也不会让所有 computed 值在 plan 时变成已知值。因此不要在上述 plan run 中把 `output.content_sha256` 当成已完成文件写入的证据，或断言它必然等于真实文件摘要。

Mock 的字符串不会自动具有合法 ARN、IP 或资源路径格式，不能拿任意生成值来测试平台语义。

## check 与强制校验

```hcl
check "nonempty_service_names" {
  assert {
    condition     = length(var.services) > 0
    error_message = "当前没有配置服务。"
  }
}
```

这是引用模块实验根变量 `var.services` 的检查片段。check 不通过通常报告警告，允许其他操作继续；它不等于强制禁止创建的 variable validation 或 precondition。

`check` 从 Terraform 1.5 起可用。上面的警告行为描述普通 plan/apply；在 `terraform test` 中，check 条件失败也会使测试失败，除非该 run 明确把它列为预期失败。

用什么机制取决于意图：输入接口错误应拒绝；部署后探测可能适合告警；资源操作前必须满足的条件应明确阻断。

## 一个模块仓库的 GitHub Actions 检查

将模块实验目录作为代码仓库根目录后，可使用如下 `.github/workflows/terraform-checks.yml`。该流程只检查 `modules/app-config`，不会给 PR 提供云端部署身份。

```yaml
name: Terraform module checks

on:
  pull_request:
    paths:
      - 'modules/app-config/**'
      - '.github/workflows/terraform-checks.yml'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  module-checks:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: modules/app-config
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: '1.10.5'
          terraform_wrapper: false
      - name: Format check
        run: terraform fmt -check -recursive
      - name: Initialize without remote backend
        run: terraform init -backend=false -input=false -lockfile=readonly
      - name: Validate module
        run: terraform validate
      - name: Run mocked plan tests
        run: terraform test
```

`1.10.5` 是固定执行版本的示例，采用时使用团队验证的 CLI 版本。实际仓库还应按团队要求固定 Action 提交，并以锁文件约束 Provider。

本例要求模块目录已经有经过 review 的 `.terraform.lock.hcl`，包括 CI 使用的 Linux 平台校验信息。因为原实验初始化发生在根目录，第一次建立模块独立检查环境时，需由维护者在模块目录初始化并记录该锁文件，再提交检查流程。

`-lockfile=readonly` 避免 CI 悄悄升级依赖；它不是禁止所有磁盘写入。模块更新后应通过专门升级变更更新锁文件和测试。

格式检查、配置检查、测试是三个独立步骤，任一步失败就停止该 job。`terraform_wrapper: false` 让后续 shell 直接获取 CLI 退出码；启用 wrapper 的项目则还需理解 Action 提供的 `exitcode` 输出，不要混用两套判断方法。

## 正式部署流水线的最小逻辑

```mermaid
flowchart LR
    PR[配置变更] --> Q[格式与配置检查、测试]
    Q --> P[目标环境 Plan]
    P --> R[审查计划与授权]
    R --> A[执行同一保存计划]
    A --> V[平台和业务核对]
```

真实计划和执行应关联同一代码提交、输入、Backend、Workspace、Provider 版本与环境身份。审查后不能偷偷重新 plan，再把一份不同的计划当作已批准结果执行。

CI 并发控制应以实际环境/State 为单位，同时使用 Backend 锁。以 PR 编号分组只能防止同一个 PR 重复运行，不能防止两个 PR 同时改同一环境。

### Plan 退出码不能误判

使用 `-detailed-exitcode` 时：

- `0`：成功，无变化。
- `1`：错误。
- `2`：成功，有变化。

示例 Bash 片段，假定执行目录、环境输入与身份已准备好：

```bash
set +e
terraform plan -input=false -lock-timeout=5m -detailed-exitcode -out=tfplan
plan_status=$?
set -e

case "$plan_status" in
  0) echo "Plan succeeded: no changes" ;;
  2) echo "Plan succeeded: changes require review" ;;
  *) echo "Plan failed"; exit "$plan_status" ;;
esac
```

不要使用 `terraform plan || true` 掩盖真正失败，也不要把 2 一律视为错误。Plan 文件须按敏感 artifact 管理，限定保存时长与访问权限。

保存计划的协作边界也要写清楚：

- 只有成功生成的计划才能进入审查；错误运行可能仍留下文件，不能据“文件存在”判断 plan 成功。
- artifact 对应确定的代码提交、目标 State 与输入，批准后执行 `terraform apply -input=false tfplan`；不要在 apply 步骤再传另一套变量。
- 应用保存计划不再询问 `yes`，授权步骤应在下载和执行它之前完成。
- 计划文件及 `terraform show -json tfplan` 都可能带明文敏感值，访问和保留策略应覆盖原文件、JSON、日志及备份。
- 环境已被其他运行修改、计划过期或授权范围变化时，重新 plan 和审查。

这些是部署流程应实现的逻辑，不是上面 PR mock 检查工作流已经具有的发布能力。

## 自动漂移检测

定期在正确身份和状态下 plan，可以检测非预期差异。退出码 2 只说明“有差异”，还需确认差异来自外部漂移、待发布配置、变量还是版本变化。

漂移检测与自动恢复是两个独立决定。没有明确恢复策略时，应先报告可审查差异，避免定时任务覆盖运维人员有意做出的应急修改。

## 凭证与运行环境

开发机 CLI 会话不会自动出现在 CI。自动化可通过平台工作负载身份/OIDC 等方式获取短期身份，并分别满足资源 API 与 Backend 访问要求。

PR 的格式/mock 测试通常不需要真实云凭证。需要真实读取权限的 Plan 应按代码信任范围、目标环境和审批策略设计，避免把高权限身份暴露给任意贡献代码。

## 练习

1. 故意让模块不使用传入 port，确认测试能识别行为错误。
2. 增加对非法服务名的 expect_failures 测试。
3. 给 Plan 脚本模拟退出码 0、1、2，说明流水线下一步应是什么。
4. 比较“mock 通过”“真实 Plan 通过”“真实 Apply 完成”各自的证据。

## 参考资料

- [原生测试](https://developer.hashicorp.com/terraform/language/tests)
- [Mocking](https://developer.hashicorp.com/terraform/language/tests/mocking)
- [Checks](https://developer.hashicorp.com/terraform/language/checks)
- [Plan 退出码](https://developer.hashicorp.com/terraform/cli/commands/plan#other-options)
- [hashicorp/setup-terraform](https://github.com/hashicorp/setup-terraform)
- [actions/checkout](https://github.com/actions/checkout)
- [依赖锁文件与跨平台校验](https://developer.hashicorp.com/terraform/language/files/dependency-lock)
- [执行保存计划](https://developer.hashicorp.com/terraform/cli/commands/apply)
- [GitHub Actions 并发控制](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)

上一篇：[[IaC/terraform/terraform-workflow-troubleshooting|工作流与排错]] · 下一篇：[[IaC/terraform/terraform-container-management|容器管理实战]]。
