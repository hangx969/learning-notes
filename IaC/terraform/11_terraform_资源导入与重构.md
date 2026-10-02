---
title: 11_terraform_资源导入与重构
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform导入已有资源
  - Terraform资源重构
---

# 11_terraform_资源导入与重构

## 先区分三种意图

| 意图 | 机制 | State 与实际对象 |
|---|---|---|
| 纳管已存在对象 | `import` 块或 CLI import | 建立实际 ID 与配置地址绑定 |
| 同一 State 内改地址 | `moved` 块 | 迁移绑定，保留实际对象 |
| 停止管理并保留对象 | `removed` 加 `destroy = false` | 移除绑定，不请求删除实际对象 |

导入或迁移后，资源配置属性仍需与实际对象相符。目标参数差异可能令计划包含更新或替换。

生产来源：`monitoring/import.tf` 中存在阿里云 CMS 集成资源导入声明；`monitoring/moved.tf` 中将 CMS 告警从拼错的 module 地址迁到新地址，并以 `removed` 的 `destroy = false` 让重复共享的联系人和联系人组退出旧地址管理。本文依据这两份文件改写地址迁移示例，原 module 名与业务 key 均换成教学名称。

## 为什么写同名 resource 不能自动导入

在阿里云已有一个名称看起来相同的 OSS Bucket，不代表 Terraform 已知它对应 `alicloud_oss_bucket.lab`。没有 State 绑定时，Terraform 会把该地址视为新实例；同名冲突或 Provider 提示都不等同于自动纳管。Data Source 查询对象也不会建立 resource 的管理关系。

## OSS Bucket 导入实验

只使用自己有权限的独立实验账号，以及专门创建、为空且允许删除的教学 Bucket。禁止将生产 Bucket、真实业务桶或由其他 State 管理的对象用作目标。若没有这样的对象，本节只阅读 HCL 和计划流程，不执行导入。

### 1. 准备专用空 Bucket

先按阿里云官方控制台或 API 操作指南，在教学账号中创建独立 Bucket，并记录准确 Bucket 名、地域和访问控制。名字应符合 OSS 命名规则且全局唯一。此预置动作不是 Terraform 导入，也不是已在本仓库执行的操作。确认 Bucket 中没有需保留的对象。

### 2. 准备完整配置

在单独目录创建 `main.tf`：

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
  region = var.region
}

variable "region" {
  type        = string
  description = "教学 Bucket 所在地域"
}

variable "bucket_name" {
  type        = string
  description = "仅填写本实验专用空 Bucket 名"
}

resource "alicloud_oss_bucket" "lab" {
  bucket        = var.bucket_name
  force_destroy = false
}

resource "alicloud_oss_bucket_acl" "lab" {
  bucket = alicloud_oss_bucket.lab.bucket
  acl    = "private"
}

import {
  to = alicloud_oss_bucket.lab
  id = var.bucket_name
}

import {
  to = alicloud_oss_bucket_acl.lab
  id = var.bucket_name
}

output "bucket_id" {
  value = alicloud_oss_bucket.lab.id
}
```

`alicloud_oss_bucket` 与 `alicloud_oss_bucket_acl` 的 Provider 1.266.0 导入实现都以 Bucket 名为 ID；ACL resource 对象也以该 ID 定位桶。本文同时声明并导入两个地址，避免将已存在的 ACL 误判为新建。Provider 认证由本机或执行环境的受控配置提供，不写入 HCL、tfvars 或命令历史。Provider 1.266.0 支持 `ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`，可选 `ALIBABA_CLOUD_SECURITY_TOKEN`，以及 `ALIBABA_CLOUD_REGION` / profile 配置。`force_destroy = false` 可避免 Terraform 为删除 Bucket 而清空其中对象。ACL 作为单独资源配置，符合 Provider 文档对旧 Bucket `acl` 参数的弃用说明。

### 3. 查看导入计划

将真实的教学值放在本地受控的 `lab.tfvars`（不要提交）：

```hcl
region      = "<教学 Bucket 地域>"
bucket_name = "<本实验专用空 Bucket 名>"
```

运行：

```bash
terraform init
terraform plan -var-file=lab.tfvars -out=import.tfplan
terraform show import.tfplan
```

检查计划中的目标 ID 与地址。导入目标应指向已核对的教学 Bucket；属性计划不能包含意料外修改、替换或删除。如果出现这些动作，调整配置或停止，不要 apply。本文未连接云端，这些是预期操作说明，不是验证结果。

### 4. 接受计划并核对

只有在已确认操作账号、Bucket 名和完整计划后，才在自己的教学环境应用导入计划：

```bash
terraform apply import.tfplan
terraform state show alicloud_oss_bucket.lab
terraform state show alicloud_oss_bucket_acl.lab
terraform plan -var-file=lab.tfvars
```

导入本身建立绑定，不重新创建对象；后续普通计划仍可能包含属性变更。维持配置与现状一致时，后续计划预期无意外变化。

## CLI import 与 import 块

旧式 CLI 用法的形式为：

```bash
terraform import -var-file=lab.tfvars alicloud_oss_bucket.lab '<Bucket 名>'
terraform import -var-file=lab.tfvars alicloud_oss_bucket_acl.lab '<Bucket 名>'
```

CLI import 直接更新 State，不生成资源配置；必须预先写好 resource、Provider 和认证配置。不要对同一个地址再执行这一命令与上面的 import block 流程。

声明式 import block 将目标地址与 ID 纳入 plan/review 流程，也支持对已知 map/set 使用 `for_each` 批量导入。导入结束后可按团队约定移除 import 块；移除该声明不会解除 resource 与 State 绑定。

## 自动生成配置

对于 Terraform 尚无 resource 配置的对象，可在受控教学目录里通过 import block 和 `terraform plan -generate-config-out=generated.tf` 请求生成候选配置。目标路径必须尚不存在。生成结果需人工检查 Provider 参数、默认值与敏感字段，再与导入计划一起审阅。生成配置并不等于已导入，也不能与手写的同地址 resource 同时保留。

## moved：保留对象的地址重命名

若只是逻辑地址改变而资源属性不变，可添加：

```hcl
moved {
  from = alicloud_cms_alarm.example["cpu"]
  to   = alicloud_cms_alarm.rules["cpu"]
}
```

目标地址必须对应真实配置。先审阅计划，确认 Terraform 将原绑定迁到新地址，且没有意外删除或重建。

### count 到 for_each

逐个映射旧索引与新 key：

```hcl
moved {
  from = alicloud_cms_alarm.example[0]
  to   = alicloud_cms_alarm.rules["cpu"]
}
```

旧索引和新 key 必须代表同一个实际告警。不能添加一条映射后就假定其余索引自动识别。

### 根资源移入模块

```hcl
moved {
  from = alicloud_oss_bucket.lab
  to   = module.storage.alicloud_oss_bucket.this
}
```

示例要求目标模块与资源确实存在、参数仍指向同一个教学 Bucket。移动到 module 会改变 Terraform 地址层级；仅在 `.tf` 文件间移动代码不会改变地址。若实际属性发生变化，Provider 仍可能提出更新。

生产重构出处：`monitoring/moved.tf`（脱敏裁剪/教学改编）展示了 CMS alarm 的模块地址迁移。原文件按实例逐条写明映射。它还展示重复的联系人与联系人组从旧 module 地址 `removed` 并设置 `destroy = false`；教学时应按自己的 State 关系设计，不复制真实地址或成员名。

## removed：停止管理但保留对象

当要退出管理但保留专用实验 Bucket 时，先移除两个 `resource` 块、两个 import 块和依赖它们的 output；不能只删 Bucket resource 而保留仍引用它的 ACL resource。随后在同一 root 配置中添加两个 removed 块：

```hcl
removed {
  from = alicloud_oss_bucket.lab
  lifecycle {
    destroy = false
  }
}

removed {
  from = alicloud_oss_bucket_acl.lab
  lifecycle {
    destroy = false
  }
}
```

先查看计划确认 Bucket 与 ACL 两个 State 绑定都退出管理且没有 Bucket 删除动作，再应用。ACL resource 被移除时 Provider 只会清掉 State 记录，ACL 设置可能留在 OSS。缺少 `destroy = false` 不能表达保留 Bucket 的意图。退出管理后 Terraform 不再负责该对象；重新添加 resource 时，如没有重新导入，Terraform 会按尚无绑定的新实例处理。

## 跨 State 移交

`moved` 适用于同一 State 内的地址变化，不会自动在两个 Backend 或 Workspace 间迁移部分对象。跨 State 移交应先停止双方并发变更、备份状态、核对 ID 与地址，再由原项目退出绑定，新项目导入同一对象，并分别审阅计划。原项目若仍保留 resource 配置，后续可能重新创建对象。锁只作用于各自 State，不防止两份状态管理同一云 ID。

## 实验收尾

如果对象仍由实验 State 管理且它是本次专门创建的空 Bucket，可在当前教学目录生成并审阅 destroy 计划：

```bash
terraform plan -destroy -var-file=lab.tfvars -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

执行前再次核对 Bucket 名与账号。若已应用 `removed` 退出管理，Terraform 不再能通过该 State 删除 Bucket；如需清理，只能先确认 Bucket 仍为空，再用阿里云管理界面/API 删除该教学对象。生产 Bucket 和其真实内容永远不是本练习的清理目标。

## 练习

1. 区分 import 块、删除 import 块、删除 resource 配置、`removed destroy=false` 的结果。
2. 将示例地址改名，写出 moved 块并说明哪些属性变化仍会产生更新或替换。
3. 对比同一 State 地址迁移与两个 State 间所有权移交。
4. 解释为什么生产中的 CMS alarm 可以迁移地址，而重复联系人需要确认是否已被新地址管理后再决定 `moved` 或 `removed`。

## 参考资料

- [Import block](https://developer.hashicorp.com/terraform/language/block/import)
- [Terraform import](https://developer.hashicorp.com/terraform/language/import)
- [生成导入配置](https://developer.hashicorp.com/terraform/language/import/generating-configuration)
- [moved 与模块重构](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [removed block](https://developer.hashicorp.com/terraform/language/block/removed)
- [CLI import](https://developer.hashicorp.com/terraform/cli/commands/import)
- [阿里云 OSS Bucket（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/oss_bucket)
- [阿里云 OSS ACL（Provider 1.266.0）](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/resources/oss_bucket_acl)
- [阿里云 Provider 1.266.0 认证文档](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs)
- [OSS ACL Provider 1.266.0 实现（State passthrough）](https://github.com/aliyun/terraform-provider-alicloud/blob/v1.266.0/alicloud/resource_alicloud_oss_bucket_acl.go)

上一篇：[[IaC/terraform/10_terraform_模块开发与复用|Module]] · 下一篇：[[IaC/terraform/12_terraform_工作流计划阅读与排错|Plan 阅读与排错]]。
