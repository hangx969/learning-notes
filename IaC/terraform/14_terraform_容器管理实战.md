---
title: 14_terraform_容器管理实战
tags:
  - IaC
  - terraform
  - terraform/basics
date: 2026-10-02
aliases:
  - Terraform容器管理
  - Terraform ACK实战
---

# 14_terraform_容器管理实战

## 本篇的管理边界

本篇沿用生产 ACK 管理链路，部署目标是一个**已存在的 ACK 集群**：通过 `alicloud_cs_cluster_credential` 读取连接材料，配置 Kubernetes 与 Helm Provider，创建 namespace，再用 Helm 安装本地 Chart。它不会创建或删除 ACK 集群。

生产依据：`tool/data.tf` 中 `alicloud_cs_cluster_credential` 数据源、`tool/providers.tf` 中 Kubernetes/Helm Provider、`tool/helm.tf` 中 namespace 与 `helm_release`，以及 `tool/external-secrets.tf` 对 Namespace 和 CRD 的依赖。生产还管理集群的 `tool/ack.tf`。`monitoring/ack-addons-log-pipeline.tf` 配置的是 Datadog 日志解析 pipeline，不是 ACK add-on 或集群组件部署源；本文据此只裁剪现有集群上的 Namespace 和一个教学 Helm release。代码是教学改写，敏感连接值不会展示为输出。

实验目录：`14-ack-helm/`。只对自己有明确授权的**隔离 ACK 实验集群**运行；不要把示例连接到生产 TFE workspace 或生产集群。

## 目录结构

```text
14-ack-helm/
├── versions.tf
├── variables.tf
├── data.tf
├── providers.tf
├── main.tf
├── lab.tfvars
└── charts/terraform-lab/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── deployment.yaml
        └── service.yaml
```

## 配置 Terraform 与集群身份

`versions.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    alicloud = {
      source  = "aliyun/alicloud"
      version = "= 1.266.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "= 2.38.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "= 2.17.0"
    }
  }
}
```

以上是本系列统一的教学版本，不代表生产仓库每个 root module 使用相同版本。生产 `shared/versions.tf` 约束 AliCloud Provider `>= 1.266.0`，`monitoring/versions.tf` 约束 `>= 1.258.0`，`monitoring/modules/cloud-monitor-alerts/versions.tf` 也有独立约束；应以运行目录的锁文件确定具体安装版本。

`variables.tf`：

```hcl
variable "ack_cluster_id" {
  description = "已存在的授权实验 ACK 集群 ID"
  type        = string
}

variable "region" {
  description = "实验 ACK 集群所在区域"
  type        = string
  default     = "cn-hongkong"
}

variable "ack_api_server_endpoint" {
  description = "ACK 集群 API Server endpoint；从授权实验集群信息取得"
  type        = string
}
```

`data.tf`：

```hcl
provider "alicloud" {
  region = var.region
  # 通过本地 CLI profile 或受控运行环境注入凭证；不要将 AccessKey 写入文件。
}

data "alicloud_cs_cluster_credential" "lab" {
  cluster_id                 = var.ack_cluster_id
  temporary_duration_minutes = 60
}
```

输入中使用占位符，例如 `ack_cluster_id = "<ACK_CLUSTER_ID>"`、`ack_api_server_endpoint = "https://ack-lab.example.invalid"` 是 `example.invalid` 占位域名，实际运行前须替换为授权实验集群 endpoint；生产 `tool/providers.tf` 从 ACK 集群资源的 `connections.api_server_internet` 取值。本教学分离出的变量表达同一 endpoint 关系。临时凭证时长可设 15 至 4320 分钟，示例取 60 分钟。本文不包含真实 ID、证书内容或 kubeconfig。生产源中还用 `alicloud_account` 和 KMS 数据源等其他数据读取，本例不需要这些资源。

在 `lab.tfvars` 中提供实验集群参数；所有值都是占位符，使用前必须替换为已授权隔离集群的实际值：

```hcl
ack_cluster_id          = "<ACK_CLUSTER_ID>"
ack_api_server_endpoint = "https://ack-lab.example.invalid"
region                  = "cn-hongkong"
```

`providers.tf`：

```hcl
provider "kubernetes" {
  host                   = var.ack_api_server_endpoint
  client_certificate     = base64decode(data.alicloud_cs_cluster_credential.lab.certificate_authority.client_cert)
  client_key             = base64decode(data.alicloud_cs_cluster_credential.lab.certificate_authority.client_key)
  cluster_ca_certificate = base64decode(data.alicloud_cs_cluster_credential.lab.certificate_authority.cluster_cert)
}

provider "helm" {
  kubernetes {
    host                   = var.ack_api_server_endpoint
    client_certificate     = base64decode(data.alicloud_cs_cluster_credential.lab.certificate_authority.client_cert)
    client_key             = base64decode(data.alicloud_cs_cluster_credential.lab.certificate_authority.client_key)
    cluster_ca_certificate = base64decode(data.alicloud_cs_cluster_credential.lab.certificate_authority.cluster_cert)
  }
}
```

Helm Provider 采用 2.x 的 `kubernetes {}` 嵌套块语法，与生产 `tool/providers.tf` 一致。本例把 ACK 凭证数据源连接到两个 Provider；不要将证书、私钥或整份 kubeconfig 输出到终端、日志或文档；不要设置数据源的 `output_file`，该参数会在 `terraform plan` 时写出 kubeconfig。Terraform state 仍可能包含敏感数据源属性或 Provider 读取值。本例未声明 Backend，默认使用本地 State；实验目录、plan/state 文件和备份需要访问控制。使用远程 State 时还应核对加密与访问权限，见第 09 篇。CLI 显示为 sensitive 也不等于 State 中不存在这些值。

如果集群刚刚创建，凭证数据源和 Provider 在同一次运行中的初始化可能遇到尚未知的连接信息。本练习直接使用一个已存在且 API endpoint 可用的集群，避开首次创建集群时的连接初始化问题；不能据此推断生产 root 的所有资源都已按独立 State 拆分。

## 创建 Namespace 与 Helm Release

`main.tf`：

```hcl
resource "kubernetes_namespace_v1" "lab" {
  metadata {
    name = "terraform-lab"
  }
}

resource "helm_release" "sample" {
  name      = "terraform-lab"
  chart     = "${path.module}/charts/terraform-lab"
  namespace = kubernetes_namespace_v1.lab.metadata[0].name
  timeout   = 300

  # 将本地 Chart 文件变化转换成 Release 输入变化。
  set {
    name = "chartChecksum"
    value = sha1(join("", [
      for f in sort(fileset(path.module, "charts/terraform-lab/**")) :
      filesha1("${path.module}/${f}")
    ]))
  }

  depends_on = [kubernetes_namespace_v1.lab]
}
```

从 namespace 的属性引用已形成隐式依赖；显式 `depends_on` 也展示生产 `tool/helm.tf` 中依赖 Namespace 的写法。Helm release 是应用安装的所有者；不要再用另一 Terraform 资源或独立清单重复管理 Helm 已安装的 Deployment 和 Service。

Chart 最小文件：

`charts/terraform-lab/Chart.yaml`：

```yaml
apiVersion: v2
name: terraform-lab
version: 0.1.0
appVersion: "1.27.0"
type: application
```

`charts/terraform-lab/values.yaml`：

```yaml
replicaCount: 1
image:
  repository: nginx
  tag: "1.27.0"
service:
  port: 80
```

`charts/terraform-lab/templates/deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  namespace: {{ .Release.Namespace }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ .Chart.Name }}
    spec:
      containers:
        - name: nginx
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - name: http
              containerPort: 80
```

`charts/terraform-lab/templates/service.yaml`：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
  namespace: {{ .Release.Namespace }}
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: {{ .Chart.Name }}
  ports:
    - name: http
      port: {{ .Values.service.port }}
      targetPort: http
```

`nginx:1.27.0` 默认在容器内监听 80，因此 Deployment 的 `containerPort` 固定为 80。Service 的 `port` 可改为其他服务端口，`targetPort: http` 会通过命名端口转发到该 80 端口；单独修改 `containerPort` 不会改变 Nginx 实际监听端口。镜像地址和 tag 是教学输入。实验集群须能拉取该镜像；如果使用私有镜像仓库，应由集群已有的凭证机制提供访问，不要把 registry 凭证放进明文 values 或 State。

Helm Provider 不会因为 `chart` 指向本地目录就自动把任意文件内容变化识别为 Terraform 输入差异。本例像生产 `tool/helm.tf` 一样，用 `fileset` 收集 chart 文件、`sort` 固定顺序、`filesha1` 计算各文件摘要，再汇总为 `chartChecksum` 传入 release。任一 Chart、values 或模板文件变化都会改变该输入，让 `helm_release.sample` 产生可审查的更新；该 checksum 是触发更新的输入，不会代替 Plan 或确认 chart 行为。

## 执行步骤与观察

设置授权实验集群的 ID 和凭证后，先确认执行目录、Workspace、Provider 依赖和计划：

```bash
terraform init
terraform workspace show
terraform providers
terraform fmt -recursive
terraform plan -var-file=lab.tfvars -out=tfplan
terraform show tfplan
```

计划应包含一个 `kubernetes_namespace_v1.lab` 和一个 `helm_release.sample`；ACK 集群本身仅作为数据源读取，不应出现创建/删除 `alicloud_cs_managed_kubernetes` 的动作。计划还可能读取或保存集群连接材料，应按敏感文件处理。只有确认身份、集群、权限和差异均属实验范围后，才可执行：

```bash
terraform apply tfplan
kubectl --context '<AUTHORIZED_LAB_CONTEXT>' -n terraform-lab get deployment,service
helm --kube-context '<AUTHORIZED_LAB_CONTEXT>' -n terraform-lab status terraform-lab
```

期望观察到一个 Deployment 和一个 ClusterIP Service，Helm release 状态为 deployed。命令中的 kube context 是用户自己配置的实验上下文；替换占位符时保留 shell 引号。本篇 Chart 已通过离线 Helm lint/template 检查；未查询集群或执行资源变更，集群认证、镜像拉取和实际部署尚未验证。

## 清理与敏感信息边界

先生成并审查删除计划，再应用：

```bash
terraform plan -destroy -var-file=lab.tfvars -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

预期删除 Helm release 中由 chart 安装的 Kubernetes 对象，以及本例创建的 Namespace；不会删除既有 ACK 集群。数据源记录随 State 清理不等于撤销云端凭据，凭据有效期仍按 ACK 的机制管理。若 Namespace 中有其他工作负载，Terraform 删除 Namespace 会连带删除其内容，执行前必须确认它由本实验独占。

凭证数据源用于配置 Provider，不要新增敏感输出。敏感变量的界面遮盖不提供 State 加密。遇到证书、私钥或 kubeconfig 出现在日志时，停止分享并按对应账号/集群的凭证轮换程序处理。

## 常见问题

- 集群 ID 不可用：确认它来自获准的实验集群，区域与 AliCloud Provider 配置一致。
- AccessDenied 或 Kubernetes 403：AliCloud 查询凭证权限、ACK RAM 身份映射、Kubernetes RBAC 是不同授权层，应分别核实。
- Kubernetes Provider 连不上：检查 endpoint 可达性、集群状态、证书和执行机网络；不能仅凭 AliCloud API 查询成功推断 Kubernetes API 可访问。
- `helm_release` 认证失败：核对 Helm Provider 的 `kubernetes {}` 连接字段和对应依赖版本。
- `namespace already exists`：确认该 namespace 是否已由其他系统管理，不能直接删除外部对象或把资源导入 State 而不先审查归属。
- chart 内容变化未触发预期更新：确认 checksum 的 `fileset` pattern 包含被修改文件，再检查 checksum 与 Helm release 的 Plan 差异。

## 练习

1. 将 `charts/terraform-lab/values.yaml` 中 `replicaCount` 从 1 改为 2；checksum 随文件内容变化，Plan 应显示 `helm_release.sample` 更新。只有在授权实验集群执行后，才核对 Deployment 副本数。
2. 将 Service `port` 从 80 改为 8080，确认 `targetPort: http` 仍映射到容器命名端口 80；说明改 Service 端口不会改变 Nginx 的监听端口。
3. 说明 `alicloud_cs_cluster_credential`、AliCloud 凭证、ACK RAM 映射与 Kubernetes RBAC 的职责差异。
4. 解释为何删除 Namespace 可能影响 namespace 中其他对象，以及正式管理前应如何确认所有权。

## 参考资料

- [AliCloud ACK 集群凭证数据源](https://registry.terraform.io/providers/aliyun/alicloud/1.266.0/docs/data-sources/cs_cluster_credential)
- [Kubernetes Provider 2.38.0](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs)
- [Helm Provider 2.17.0](https://registry.terraform.io/providers/hashicorp/helm/2.17.0/docs)
- [Helm Release 资源](https://registry.terraform.io/providers/hashicorp/helm/2.17.0/docs/resources/release)
- [Kubernetes Namespace v1 资源](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/namespace_v1)

上一篇：[[IaC/terraform/13_terraform_测试与持续集成交付|测试与 CI/CD 协作]] · 下一篇：[[IaC/terraform/15_terraform_模块文档生成|模块文档生成]]。
