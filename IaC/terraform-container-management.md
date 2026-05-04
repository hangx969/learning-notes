---
title: Terraform 容器管理
source: "https://mp.weixin.qq.com/s/b6pkgOpHn2tbEaBpOniyWw"
author:
  - "[[Hank]]"
created: 2026-04-23
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

# Terraform 容器管理

容器（Container）已经成为现代软件交付的核心。无论是 Docker 还是 Kubernetes，Terraform 都能通过 Provider 插件实现资源的统一管理，将容器基础设施纳入基础设施即代码（IaC）的体系中。这样不仅能带来一致性，还能借助版本控制、自动化测试与审查机制，大大提升团队的交付效率。

本章围绕以下几个主题展开：

- Docker 镜像与容器的本地/远程管理
- Kubernetes 集群的部署与配置
- 集群操作的认证与授权
- 使用 YAML 与 HCL 定义 Kubernetes 资源
- 网络策略与注解管理
- Helm 在容器部署与监控中的应用
- 使用 Nomad 调度容器

---

## 5.1 使用本地与远程 Docker 镜像

在 Terraform 中既可以使用远程仓库镜像（如 Docker Hub），也可以直接引用本地镜像。

```hcl
# Docker Provider
provider "docker" {}

# 使用远程镜像
resource "docker_image" "remote_image" {
  name = "nginx:latest"
}
resource "docker_container" "remote_container" {
  name  = "remote_nginx"
  image = docker_image.remote_image.latest
}

# 使用本地镜像
resource "docker_image" "local_image" {
  name         = "custom-app:1.0"
  keep_locally = true
}
resource "docker_container" "local_container" {
  name  = "local_app"
  image = docker_image.local_image.latest
}
```

- **远程镜像**：适合使用最新版本或共享的公共镜像。
- **本地镜像**：适合自研镜像或无公网访问的环境。

> 💡 在企业级环境中常用私有镜像仓库（Harbor、ECR、GCR 等），Terraform 同样可以管理。

---

## 5.2 区分集群部署与配置

**部署（Deployment）**：新建集群（例如 AWS EKS）。
**配置（Configuration）**：在现有集群中添加资源（如命名空间）。

```hcl
# 部署 EKS 集群
provider "aws" { region = "us-east-1" }

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  cluster_name    = "demo-cluster"
  cluster_version = "1.20"
  vpc_id          = "vpc-xxxxxx"
  subnets         = ["subnet-1", "subnet-2"]

  node_groups = {
    eks_nodes = {
      desired_capacity = 3
      instance_type    = "t3.medium"
    }
  }
}

# 配置集群：创建 namespace
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_ca_data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}
data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_id
}
resource "kubernetes_namespace" "demo" {
  metadata { name = "demo-namespace" }
}
```

---

## 5.3 授权 Terraform 操作 Kubernetes 集群

Terraform 需要通过认证和权限才能操作集群。例如在 EKS 中：

```hcl
provider "aws" { region = "us-east-1" }

data "aws_eks_cluster" "cluster" { name = "demo-cluster" }
data "aws_eks_cluster_auth" "cluster" { name = "demo-cluster" }

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
  load_config_file       = false
}
```

> ⚠️ 需要在 AWS IAM 中为 Terraform 执行角色授予访问 EKS 的权限。

---

## 5.4 使用 YAML 调度容器

Terraform 可以直接加载现有 Kubernetes YAML 配置：

```hcl
resource "kubernetes_manifest" "app" {
  manifest = yamldecode(file("${path.module}/deployment.yaml"))
}
```

**deployment.yaml**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: my-image:latest
        ports:
        - containerPort: 8080
```

---

## 5.5 使用 HCL 调度容器

同样可以直接在 Terraform 中用 HCL 编写：

```hcl
resource "kubernetes_deployment" "app" {
  metadata { name = "my-app" }
  spec {
    replicas = 3
    selector { match_labels = { app = "my-app" } }
    template {
      metadata { labels = { app = "my-app" } }
      spec {
        container {
          name  = "app"
          image = "my-image:latest"
          port { container_port = 8080 }
        }
      }
    }
  }
}
```

---

## 5.6 YAML 转 HCL

可使用 `terraform console` 将 YAML 转换为 HCL：

```hcl
terraform console
> jsonencode({
  resource = {
    kubernetes_manifest = {
      example = {
        manifest = yamldecode(file("deployment.yaml"))
      }
    }
  }
})
```

---

## 5.7 调整 Kubernetes 注解

```hcl
resource "kubernetes_deployment" "example" {
  metadata {
    name = "my-app"
    annotations = {
      "example.com/version" = "v1.0"
    }
  }
}
```

注解（Annotation）与标签（Label）的区别：

- **Label**：用于选择和分组资源。
- **Annotation**：存放元数据，如构建信息、监控配置。

---

## 5.8 动态调整 Deployment 配置

```hcl
variable "replica_count" { default = 5 }
variable "image_version" { default = "v2" }

resource "kubernetes_deployment" "example" {
  spec {
    replicas = var.replica_count
    template {
      spec {
        container {
          name  = "my-app"
          image = "my-image:${var.image_version}"
          env {
            name  = "ENV_VAR"
            value = "demo"
          }
        }
      }
    }
  }
}
```

执行时可动态覆盖参数：

```bash
terraform apply -var="replica_count=3" -var="image_version=v3"
```

---

## 5.9 应用 Kubernetes 网络策略 (NetworkPolicy)

```hcl
resource "kubernetes_network_policy" "db_policy" {
  metadata { name = "db-policy" namespace = "default" }
  spec {
    pod_selector { match_labels = { role = "db" } }
    policy_types = ["Ingress", "Egress"]

    ingress {
      from { pod_selector { match_labels = { role = "frontend" } } }
      ports { protocol = "TCP" port = 6379 }
    }
    egress {
      to { pod_selector { match_labels = { role = "replica" } } }
      ports { protocol = "TCP" port = 6379 }
    }
  }
}
```

> 💡 仅允许 frontend → db，db → replica 的流量。

---

## 5.10 使用 Helm 部署应用

```hcl
provider "helm" {
  kubernetes {}
}

resource "helm_release" "redis" {
  name       = "redis"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "redis"
  version    = "17.3.14"

  set {
    name  = "architecture"
    value = "standalone"
  }
}
```

Helm Provider 结合 Terraform，能将 Helm Release 纳入 Terraform 的状态管理。

---

## 5.11 使用 Helm 部署监控 (Prometheus + Grafana)

```hcl
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus"
  version    = "15.10.1"
}

resource "helm_release" "grafana" {
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  version    = "6.43.1"
  set {
    name  = "adminPassword"
    value = "StrongPassword123!"
  }
}
```

这样可以快速为 Kubernetes 部署可视化监控体系。

---

## 5.12 使用 HashiCorp Nomad 调度容器

除了 Kubernetes，Terraform 还支持 **Nomad**：

```hcl
provider "nomad" {
  address = "http://localhost:4646"
}

resource "nomad_job" "redis" {
  jobspec = file("${path.module}/redis.nomad")
}
```

**redis.nomad**:

```hcl
job "redis" {
  datacenters = ["dc1"]
  group "cache" {
    task "redis" {
      driver = "docker"
      config { image = "redis:latest" }
    }
  }
}
```

Nomad 更适合混合调度（容器+非容器化应用）。

---

## 总结

- Terraform 能管理 **Docker** 和 **Kubernetes** 的容器工作负载，也能支持 **Nomad**。
- 在 Kubernetes 场景下，可以灵活选择 **YAML / HCL / Helm**。
- 网络策略（NetworkPolicy）、注解（Annotation）、环境变量等，都能通过 Terraform 精细化管理。
- Helm Provider 将 Helm Chart 纳入 Terraform 生命周期。
- Terraform 的统一入口让 **容器编排与基础设施管理一致化**，非常适合企业 DevOps 流程。
