---
title: 14_terraform_容器管理实战
original_source: "https://mp.weixin.qq.com/s/b6pkgOpHn2tbEaBpOniyWw"
original_author: Hank
created: 2026-04-23
date: 2026-10-02
tags:
  - IaC
  - terraform
  - docker
  - kubernetes
  - helm
aliases:
  - Terraform容器管理
  - Terraform Container Management
---

# 14_terraform_容器管理实战

## 先确定 Terraform 管理哪一层

Terraform 可以管理云上的集群基础设施，也可以通过 Docker、Kubernetes、Helm、Nomad Provider 管理容器相关对象。不同层的认证、可用时间和资源所有权应分清。

| 层级 | 典型对象 | 连接方式 |
|---|---|---|
| 云基础设施 | VPC、集群、节点池、负载均衡 | 云 Provider 和云身份 |
| Kubernetes API | Namespace、Deployment、ConfigMap | Kubernetes Provider、kubeconfig/RBAC |
| 应用发布 | Helm Release | Helm Provider 和集群访问权限 |
| Docker Engine | 本地/远程镜像、容器、网络 | Docker Provider 和 daemon endpoint |
| Nomad | Job | Nomad Provider 和 Nomad API/ACL |

对于新建集群，通常先完成基础设施层，再运行集群资源配置层。尤其 `kubernetes_manifest` 在 plan 时可能要查询 API schema，不能只加 depends_on 就保证与新建集群、CRD 在同一轮里都能工作。

本章每个实战都使用独立目录和自己的状态。不要把以下所有配置拼进一个 main.tf，也不要把实验接到身份不明的生产集群。

## 一、Docker：管理 Nginx 镜像和容器

### 1. 确认连接的 Engine

读者先在终端检查：

```bash
docker version
docker context show
docker context inspect --format '{{ .Endpoints.docker.Host }}'
export DOCKER_HOST="$(docker context inspect --format '{{ .Endpoints.docker.Host }}')"
```

不要假定 Terraform Provider 总能自动采用 Docker CLI 当前 context。应显式传入当前 daemon endpoint；远程 TLS/SSH context 还需要按 Provider 文档准备证书或 SSH 配置。

在 macOS 上，Docker Desktop 等实现的 socket 可能位于用户目录；不要机械固定成 Linux 常见的 `/var/run/docker.sock`。

### 2. 完整 main.tf

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

variable "host_port" {
  type    = number
  default = 8080
}

resource "docker_image" "nginx" {
  name         = "nginx:1.30.5-alpine"
  keep_locally = true
}

resource "docker_container" "nginx" {
  name  = "tf-learning-nginx"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = var.host_port
    ip       = "127.0.0.1"
  }
}

output "url" {
  description = "Docker daemon 在本机时的访问地址"
  value       = "http://127.0.0.1:${var.host_port}"
}
```

- Provider 3.x 使用 `docker_image.nginx.image_id`，不要沿用旧教程中的 `.latest` 属性。
- `keep_locally = true` 表示 destroy 时保留 daemon 上的镜像，不代表“只允许使用本地镜像”或“永远不从仓库拉取”。
- `127.0.0.1` 是 daemon 所在主机的回环地址。连接远程 daemon 时，客户端 localhost 不会因此自动转发到远端容器。
- 例子使用官方镜像的固定版本标签；追求不可变制品时还应使用经过确认的 digest。

### 3. 创建、访问和清理

```bash
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
docker ps --filter name=tf-learning-nginx
curl http://127.0.0.1:8080
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
```

curl 示例假定 Engine 在本机，端口 8080 没被其他应用占用。预期删除容器后，本地镜像因 keep_locally 仍保留。

### 4. 自研镜像

已有本地镜像可以供容器引用，但需要明确镜像的生产和生命周期责任。需要 Terraform 在实验中构建镜像时，可补充下面的独立镜像资源：

```hcl
resource "docker_image" "custom" {
  name = "tf-learning-custom:1.0"

  build {
    context = "${path.module}/app"
  }

  triggers = {
    html_sha       = filesha256("${path.module}/app/index.html")
    dockerfile_sha = filesha256("${path.module}/app/Dockerfile")
  }
}
```

准备 `app/Dockerfile`：

```dockerfile
FROM nginx:1.30.5-alpine
COPY index.html /usr/share/nginx/html/index.html
```

以及 `app/index.html`：

```html
<h1>Terraform Docker lab</h1>
```

将容器的 image 改为 `docker_image.custom.image_id` 才会使用此镜像。triggers 示例观察 HTML 和 Dockerfile；构建还有其他输入时需把它们纳入变更摘要。只改构建目录中的文件，并不保证 Provider 自动发现所有变化。

审查并执行新计划后访问同一端口，应看到 `Terraform Docker lab`；然后只修改 index.html，再次 plan，观察镜像重新构建与容器更新的计划。构建目录来自执行 Terraform 的机器，即使连接的是远程 daemon，也不能把 context 理解为 daemon 上的已有路径。

生产镜像通常由构建流水线产出，Terraform 消费固定制品，避免把每次基础设施变更都变成一轮应用构建。

### 5. 同一个 tag 不自动代表新镜像

Docker image 资源不会仅因远程同名 tag 的内容变化就总能知道要拉取新层。需要跟踪仓库 digest 时，可使用下面的替换写法：

```hcl
data "docker_registry_image" "nginx" {
  name = "nginx:1.30.5-alpine"
}

resource "docker_image" "nginx" {
  name          = data.docker_registry_image.nginx.name
  pull_triggers = [data.docker_registry_image.nginx.sha256_digest]
  keep_locally  = true
}
```

此片段替换原同名 docker_image，不能重复声明。私有仓库还需配置认证；不要将密码写入笔记或资源参数。

## 二、Kubernetes：在已有集群创建应用

### 1. 认证与授权是两层

- 认证确认请求者是谁，例如 kubeconfig 中的证书、token 或 exec 插件。
- 授权确认该身份能否在目标 namespace 操作资源，通常由 Kubernetes RBAC 等决定。
- 云端 EKS/ACK/AKS 还可能有云身份接入与角色映射。云 IAM 登录成功不等于 Kubernetes API 自动授权。

先核对目标并检查必要权限：

```bash
kubectl config current-context
kubectl config get-contexts
kubectl --context "<实验context>" auth can-i create namespaces
kubectl --context "<实验context>" auth can-i create deployments -n tf-learning-k8s
```

已有 namespace 下的项目可由管理员预先创建 namespace 并授予有限权限。本例包含 namespace 创建，所以需要相应集群级权限。

这里的 can-i 命令只演示 create 权限检查。管理对象的完整生命周期还需要读取、更新和删除权限；仅通过创建权限检查，不能证明 plan、等待 Ready 和 destroy 都能成功。

### 2. 完整 main.tf

例子使用 Kubernetes Provider **2.x** 的 `_v1` 类型。在独立目录创建：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
  }
}

variable "kubeconfig_path" {
  type    = string
  default = "~/.kube/config"
}

variable "kube_context" {
  description = "显式指定的实验 context"
  type        = string
}

variable "replicas" {
  type    = number
  default = 1

  validation {
    condition     = var.replicas >= 0 && floor(var.replicas) == var.replicas
    error_message = "replicas 必须是非负整数。"
  }
}

provider "kubernetes" {
  config_path    = pathexpand(var.kubeconfig_path)
  config_context = var.kube_context
}

resource "kubernetes_namespace_v1" "lab" {
  metadata {
    name = "tf-learning-k8s"
  }
}

resource "kubernetes_deployment_v1" "web" {
  metadata {
    name      = "web"
    namespace = kubernetes_namespace_v1.lab.metadata[0].name
    annotations = {
      "example.com/managed-by" = "terraform"
    }
  }

  spec {
    replicas = tostring(var.replicas)

    selector {
      match_labels = { app = "web" }
    }

    template {
      metadata {
        labels = { app = "web" }
      }

      spec {
        container {
          name  = "nginx"
          image = "nginx:1.30.5-alpine"

          port {
            container_port = 80
          }

          resources {
            requests = { cpu = "100m", memory = "64Mi" }
            limits   = { cpu = "500m", memory = "128Mi" }
          }
        }
      }
    }
  }
}

output "namespace" {
  value = kubernetes_namespace_v1.lab.metadata[0].name
}
```

Deployment 的 selector 与 Pod labels 匹配，namespace 通过引用建立隐式依赖。Annotation 用于元信息，Label 用于选择和分组；两者用途不同。

| 字段 | 本例的含义 |
|---|---|
| `metadata[0].name` | Provider 把 metadata 建模为单个 list block，因此用 `[0]` 取对象名 |
| `spec.replicas` | Kubernetes Provider 2.x 将其建模为 string；本例把经过整数校验的 number 转为 string，Kubernetes API 中仍是整数副本数 |
| `selector.match_labels` | Deployment 选择 Pod 的标签，须与 template 中对应的标签一致 |
| `container.port.container_port` | 声明容器预期端口，不会让 Nginx 启动监听，也不会自动创建 Service |
| `resources.requests` | 调度时考虑的资源请求；不是“使用量达到下限才启动” |
| `resources.limits` | 运行时限制，CPU 常体现为限流，内存超限可能 OOM；不能把两者都理解为自动重启 |

这些 HCL 块名、类型和索引来自该版本 Provider schema，不是把 Kubernetes YAML 字段名原样换个后缀。

### 3. 运行和访问

```bash
export TF_VAR_kube_context="<实验context>"
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
kubectl --context "<实验context>" -n tf-learning-k8s get deployments,pods
kubectl --context "<实验context>" -n tf-learning-k8s port-forward deployment/web 8081:80
```

另一个终端访问：

```bash
curl http://127.0.0.1:8081
```

预期 Deployment 可用副本数为 1，Pod 为 Ready，curl 返回 Nginx 页面。若 Pod Pending/ImagePullBackOff，先用 `kubectl describe pod` 和事件检查调度、配额、镜像拉取等原因，Terraform 创建了 Deployment 不代表工作负载已经可用。

在 port-forward 终端按 Ctrl+C 停止转发，然后观察扩容：

```bash
terraform plan -var='replicas=2' -out=scale.tfplan
terraform show scale.tfplan
terraform apply scale.tfplan
kubectl --context "<实验context>" -n tf-learning-k8s rollout status deployment/web
kubectl --context "<实验context>" -n tf-learning-k8s get deployments,pods
```

预期 Deployment 更新到两个副本，不新建另一个 Terraform 地址。命令行 `-var` 只影响这次计划；若要持续维持 2 个副本，应修改配置默认值或受控 tfvars，否则下一次不传该值的 plan 会尝试恢复到 1。

改变 kube_context 不等于创建独立集群环境；同一 State 可能拿旧资源记录去操作新集群。多个集群应使用明确分开的根配置/状态。

### 4. 使用已有 YAML

在同一个实验目录创建单文档 `configmap.yaml`：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-config
data:
  log_level: info
```

补充一个独立 manifest 资源：

```hcl
locals {
  raw_configmap = yamldecode(file("${path.module}/configmap.yaml"))
}

resource "kubernetes_manifest" "config" {
  manifest = merge(local.raw_configmap, {
    metadata = merge(local.raw_configmap.metadata, {
      namespace = kubernetes_namespace_v1.lab.metadata[0].name
    })
  })
}
```

`yamldecode` 得到 Terraform 对象，`kubernetes_manifest` 根据 Kubernetes schema 管理它。`jsonencode` 可以把值编码成 JSON，但不是把 YAML 自动翻译成所有 `_v1` resource 的块结构；两种资源模型要分别理解。

Manifest 需要在 plan 阶段访问集群 schema。管理自定义资源时，CRD 应已存在；`depends_on` 不能让 plan 使用尚未安装的 CRD schema。

### 5. NetworkPolicy

可在已有实验中补充：

```hcl
resource "kubernetes_network_policy_v1" "web_ingress" {
  metadata {
    name      = "web-ingress"
    namespace = kubernetes_namespace_v1.lab.metadata[0].name
  }

  spec {
    pod_selector {
      match_labels = { app = "web" }
    }

    policy_types = ["Ingress"]

    ingress {
      from {
        pod_selector {
          match_labels = { app = "frontend" }
        }
      }

      ports {
        protocol = "TCP"
        port     = "80"
      }
    }
  }
}
```

目标是限制选中的 web Pod 入站流量，允许同 namespace 的 frontend Pod 访问 TCP 80。此例没有声明 Egress 隔离，不限制 web 的所有出站流量。

实际效果要求 CNI 支持 NetworkPolicy，并要考虑其他策略的叠加。看到 API 创建成功不等于流量边界已经验证；使用真实允许/拒绝的 Pod 流量测试，port-forward 不能代替它。

### 6. 清理边界

先查看 destroy plan，再执行：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
kubectl --context "<实验context>" get namespace tf-learning-k8s
```

正常清理后，查询 namespace 应返回 NotFound。本例会管理并删除自己的 namespace；删除 namespace 会涉及其中的所有资源，所以不要混入其他工具/团队的对象。

## 三、Helm：把 Release 纳入 State

Helm Provider 管理的是 Release。Chart 里的 Deployment、Service、ConfigMap 等由 Helm 渲染和操作，不应同时让 Terraform typed resource 或 Argo CD 管理相同对象。

本例用自己的最小 Chart，避免依赖过期公共 Chart 参数。Provider 采用 **3.x**：`kubernetes = { ... }` 是对象写法，旧版 `kubernetes { ... }` 不能不加区分地混用。

这里的 3.x 指 Terraform Helm Provider 的版本，并非本机 Helm CLI 的主版本。示例 Chart 不使用需要联网下载的子 Chart。

### 1. 目录结构

```text
14-helm/
├── main.tf
└── chart/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        └── web.yaml
```

`chart/Chart.yaml`：

```yaml
apiVersion: v2
name: learning-web
description: Terraform Helm learning chart
type: application
version: 0.1.0
appVersion: '1.30.5'
```

`chart/values.yaml`：

```yaml
replicaCount: 1
image:
  repository: nginx
  tag: 1.30.5-alpine
```

`chart/templates/web.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
        - name: nginx
          image: '{{ .Values.image.repository }}:{{ .Values.image.tag }}'
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
spec:
  selector:
    app: {{ .Release.Name }}
  ports:
    - port: 80
      targetPort: 80
```

### 2. 完整 main.tf

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "~> 3.0"
    }
  }
}

variable "kubeconfig_path" {
  type    = string
  default = "~/.kube/config"
}

variable "kube_context" {
  type = string
}

provider "helm" {
  kubernetes = {
    config_path    = pathexpand(var.kubeconfig_path)
    config_context = var.kube_context
  }
}

resource "helm_release" "web" {
  name             = "learning-web"
  namespace        = "tf-learning-helm"
  create_namespace = true
  chart            = "${path.module}/chart"
  wait             = true
  timeout          = 300

  values = [yamlencode({
    replicaCount = 1
  })]
}
```

使用 YAML 编码的 values 可以传对象和数组，也更容易避免 Helm `set` 的字符串转义。`values` 本身是 YAML 字符串列表，所以这里用 `[yamlencode(...)]`，不能直接赋一个 Terraform map。

如果希望在 Release 中覆盖一个简单值，可在该资源内部补充下面的 Provider 3.x 写法：

```hcl
set = [
  {
    name  = "replicaCount"
    value = "2"
  }
]
```

这是对象列表赋值，不是旧版重复的 `set { ... }` 块；同名值的 set 覆盖 values。本章默认实战使用 values，以下变更步骤也只改 values，避免把两个配置来源混起来。

`wait = true` 等待 Helm 支持的资源就绪条件，`timeout = 300` 是等待超时秒数；它们不能代替业务接口验收。

### 3. 检查 Chart，再执行

```bash
helm lint ./chart
helm template learning-web ./chart --namespace tf-learning-helm
export TF_VAR_kube_context="<实验context>"
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
helm --kube-context "<实验context>" list -n tf-learning-helm
kubectl --context "<实验context>" -n tf-learning-helm get deployments,services,pods
```

本地渲染预期包含一个 Deployment 和一个 Service，Nginx 镜像为 `1.30.5-alpine`；部署后 Release 应出现在 helm list 中。访问服务时可以运行：

```bash
kubectl --context "<实验context>" -n tf-learning-helm port-forward service/learning-web 8082:80
```

另一个终端运行 `curl http://127.0.0.1:8082`。把 main.tf 中 values 的 replicaCount 改为 2，停止转发并生成新的计划：

```bash
terraform plan -out=scale.tfplan
terraform show scale.tfplan
terraform apply scale.tfplan
helm --kube-context "<实验context>" status learning-web -n tf-learning-helm
kubectl --context "<实验context>" -n tf-learning-helm get deployments,pods
```

预期是同一 Release 的升级和副本数变化，不是额外创建一套 Kubernetes typed resource。

清理时 destroy Release 并核对资源：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
helm --kube-context "<实验context>" list -n tf-learning-helm
kubectl --context "<实验context>" get namespace tf-learning-helm
```

本例 Deployment 和 Service 应被卸载。`create_namespace` 创建的 namespace 不随 Helm Release 卸载自动删除，它也不是单独纳入 State 的 namespace 资源；在确认没有其他对象后，实验维护者再单独删除它。公共 Chart 的 CRD、持久卷、保留注解和 hook 对象还需按其卸载规则核对。

### 4. 公共 Chart、监控与 Secret

采用 Prometheus/Grafana 等公共 Chart 时，应固定具体 Chart 版本，查看该版本的 values schema、CRD 管理和升级说明。不要延续旧文章里随手固定的历史版本或明文 adminPassword。

密码可由外部 Secret 流程准备，再通过 Chart 支持的已有 Secret 引用接入。`set_sensitive` 能遮盖显示，但不等于密码不进入 Terraform State。

`atomic` 可提供 Helm 自身的失败清理/回滚行为；它不保证整个 Terraform 运行的其他资源都回滚。CRD、hook 和数据卷的卸载行为仍需按 Chart 核对。

## 四、Nomad：管理已有集群中的 Job

Nomad Provider 与 Kubernetes Provider 是不同接口。以下是有可用 Nomad server/client、Docker driver 的实验配置，不包含搭建 Nomad 集群。

`main.tf`：

```hcl
terraform {
  required_version = ">= 1.7, < 2.0"

  required_providers {
    nomad = {
      source  = "hashicorp/nomad"
      version = "~> 2.0"
    }
  }
}

provider "nomad" {
  address = "http://127.0.0.1:4646"
}

resource "nomad_job" "web" {
  jobspec = file("${path.module}/web.nomad.hcl")
}
```

`web.nomad.hcl`：

```hcl
job "learning-web" {
  datacenters = ["dc1"]
  type        = "service"

  group "web" {
    count = 1

    network {
      port "http" {
        to = 80
      }
    }

    task "nginx" {
      driver = "docker"

      config {
        image = "nginx:1.30.5-alpine"
        ports = ["http"]
      }

      resources {
        cpu    = 100
        memory = 128
      }
    }
  }
}
```

`jobspec` 是**文件内容字符串**，不是把文件路径交给 Nomad；因此使用 `file(...)`。Terraform Provider 默认解析 HCL2，但 `web.nomad.hcl` 仍是 Nomad 的 jobspec 语言，不能把任意 Terraform resource 写进它。

| jobspec 字段 | 含义 |
|---|---|
| `datacenters = ["dc1"]` | 调度目标数据中心，要与实际 client 所属数据中心相符 |
| `type = "service"` | 长期运行的服务型 Job |
| `group.count` | 该任务组所需的 allocation 数量 |
| `port "http" { to = 80 }` | 分配主机动态端口并映射到容器 80，不是固定主机 80 |
| Docker `ports = ["http"]` | 使用前面声明的端口标签，启用对应的映射 |
| `resources.cpu` / `memory` | CPU 以 MHz、内存按 Nomad 文档的 MB 数值表示，含义不同于 Kubernetes 的 `100m`/`128Mi` |

生产环境使用自己的 TLS endpoint，并按 ACL 配置受控的 `NOMAD_TOKEN`。实验中的 Provider endpoint 与 Nomad CLI 的 `NOMAD_ADDR` 应一致。在已有实验集群中执行：

```bash
export NOMAD_ADDR="http://127.0.0.1:4646"
nomad job validate web.nomad.hcl
terraform init
terraform plan -out=tfplan
terraform show tfplan
terraform apply tfplan
nomad job status learning-web
```

`nomad job validate` 可能访问 server 做校验，并非保证离线。Provider 的 `detach` 默认是 true，提交 Job 后可以立即返回；因此 apply 完成不代表 allocation 已经 Running。根据 job status 列出的 allocation ID 继续查看：

```bash
nomad alloc status "<allocation-id>"
curl "http://<可访问的client-IP>:<http动态主机端口>"
```

预期 task 为 Running，访问返回 Nginx 页面。访问地址是实际承载 allocation 的 client，不能因为 server 在 localhost 就假定应用也在该机。

把 jobspec 的 group count 改为 2，再走 plan/show/apply，观察 allocation 数量。实验结束后：

```bash
terraform plan -destroy -out=destroy.tfplan
terraform show destroy.tfplan
terraform apply destroy.tfplan
nomad job status learning-web
```

默认销毁会注销 Job，但 `purge_on_destroy` 默认为 false，历史 Job 记录可能仍可查询。应核对没有继续运行的实验 allocation，不能仅据“还能查到 Job 历史”判断删除失败。

## 工具所有权与常见问题

- Terraform、Helm、kubectl、Argo CD 同时声明同一对象，会互相覆盖或出现所有权冲突。明确每个对象的负责人。
- Helm Release 的资源不应再逐个声明为另一套 Terraform typed resource。
- 创建集群需要云权限，操作集群需要集群认证和授权，两者分开检查。
- 本地可用的 exec 认证插件在远程 runner 上也必须存在，短期 token 还要考虑有效期。
- 读取 Secret 或把密码写进 Helm values，可能把值存进 State；显示遮盖和持久化是不同问题。
- Terraform apply 成功后，继续核对容器运行、Pod Ready、Release 状态和实际访问。

## 练习

1. 只修改 Docker 自研镜像的 index.html，解释 triggers、image_id 与容器更新之间的关系。
2. 把 Kubernetes replicas 改为 2，说明为什么是同一 Deployment 地址的更新；再解释命令行临时赋值为何会在下一次 plan 消失。
3. 在本地用 `helm template --set replicaCount=2` 查看副本数，区分 Chart 渲染、Release 部署和应用可访问三种证据。
4. 解释 Terraform 删除 Helm Release 后 namespace、公共 Chart CRD 和持久卷为什么可能仍保留。
5. 对比 Nomad Job 的提交成功与 allocation Running，说明应查询哪一层。

## 参考资料

- [Docker Provider](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs)
- [Docker image](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs/resources/image)
- [Docker Provider 3.0.2 image schema](https://github.com/kreuzwerker/terraform-provider-docker/blob/v3.0.2/docs/resources/image.md)
- [Docker container](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs/resources/container)
- [官方 Nginx 镜像](https://hub.docker.com/_/nginx)
- [Kubernetes Provider 2.30](https://registry.terraform.io/providers/hashicorp/kubernetes/2.30.0/docs)
- [Kubernetes Deployment 2.30 schema](https://registry.terraform.io/providers/hashicorp/kubernetes/2.30.0/docs/resources/deployment_v1)
- [kubernetes_manifest](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs/resources/manifest)
- [Helm Provider 3.0](https://registry.terraform.io/providers/hashicorp/helm/3.0.0/docs)
- [helm_release](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release)
- [helm_release 3.0 对象列表示例](https://github.com/hashicorp/terraform-provider-helm/blob/v3.0.0/docs/resources/release.md)
- [Helm Chart 模板与字段](https://helm.sh/docs/topics/charts/)
- [Nomad Job 2.0](https://registry.terraform.io/providers/hashicorp/nomad/2.0.0/docs/resources/job)
- [Nomad jobspec network](https://developer.hashicorp.com/nomad/docs/job-specification/network)
- [Nomad jobspec resources](https://developer.hashicorp.com/nomad/docs/job-specification/resources)
- [Nomad job validate](https://developer.hashicorp.com/nomad/commands/job/validate)
- [Nomad allocation status](https://developer.hashicorp.com/nomad/commands/alloc/status)

相关原理：[[Docker-Kubernetes/k8s-basic-resources/k8s基础-deployment|Deployment]]、[[Docker-Kubernetes/k8s-basic-resources/k8s基础-认证-授权-准入|Kubernetes 认证授权]]。

上一篇：[[IaC/terraform/13_terraform_测试与持续集成交付|测试与协作]] · 下一篇：[[IaC/terraform/15_terraform_模块文档生成|模块文档生成]]。
