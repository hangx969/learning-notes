---
title: "GitOps 落地实践：ArgoCD + Kustomize 实现声明式基础设施管理"
source: "https://mp.weixin.qq.com/s/SVZM79y7ih56kPpVM64aLg"
author:
published:
created: 2026-05-17
description: "关注「Raymond运维」公众号，并设为「星标」，也可以扫描底部二维码加入群聊，第一时间获取最新内容，不再错过"
tags:
  - "clippings"
---
*2026年5月13日 20:00*

![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/b5PbQq93ic09N2RfN7gYF9IOF5giaofTOPoR8Y9szIF5eLelR8lIXgGMn1Lh700B0dPxeeibC2VX1mAzhWvcHz0cg/640?wx_fmt=gif&from=appmsg&wxfrom=5&tp=webp&wx_lazy=1#imgIndex=0)

关注 **「Raymond运维」** 公众号，并设为 **「星标」** ，也可以扫描底部二维码加入群聊，第一时间获取最新内容，不再错过精彩内容。

## 一、概述

### 1.1 背景介绍

GitOps 作为云原生时代的运维范式，将 Git 作为基础设施和应用配置的单一事实来源，通过声明式配置和自动化同步机制，实现了配置管理的版本控制、审计追溯和快速回滚。ArgoCD 作为 CNCF 毕业项目，提供了完整的 GitOps 工作流，支持多集群管理、RBAC 权限控制、SSO 集成等企业级特性。结合 Kustomize 的配置管理能力，能够优雅地解决多环境配置差异、敏感信息管理、配置复用等问题。

在传统的 CI/CD 流程中，往往由 CI 工具直接执行 kubectl apply，这种推模式存在权限管理复杂、审计困难、状态漂移等问题。ArgoCD 采用拉模式，由运行在集群内的 Controller 主动从 Git 仓库拉取配置并应用，实现了部署权限的收敛和状态的持续同步。

### 1.2 技术特点

- **声明式部署** ：基于 Kubernetes 资源清单定义期望状态，ArgoCD 自动检测并消除实际状态与期望状态的偏差
- **多集群管理** ：单个 ArgoCD 实例可管理数百个 Kubernetes 集群，支持集群级别的 RBAC 和资源隔离
- **自动同步策略** ：支持手动同步、自动同步、自动修剪(Prune)、自愈(Self-Heal)等多种策略组合
- **回滚与审计** ：完整记录每次同步操作，支持一键回滚到任意历史版本，所有变更可追溯到 Git commit
- **健康检查** ：内置对 Deployment、StatefulSet、Service、Ingress 等资源的健康检查，支持自定义健康检查脚本
- **SSO 集成** ：支持 OAuth2、OIDC、SAML、LDAP 等多种认证方式，可与企业统一认证系统集成
- **渐进式交付** ：集成 Argo Rollouts 实现蓝绿部署、金丝雀发布、流量分析等高级发布策略

### 1.3 适用场景

- 场景一：多环境配置管理，通过 Kustomize overlay 机制管理 dev/staging/prod 等环境的配置差异，避免重复维护相似配置
- 场景二：多集群应用分发，使用 ApplicationSet 批量创建 Application，实现应用在多个集群、多个命名空间的标准化部署
- 场景三：基础设施即代码，将集群基础组件(Ingress Controller、监控栈、日志收集等)以 GitOps 方式管理，实现集群配置的版本化
- 场景四：合规审计与权限管控，所有变更通过 Git PR 审批，部署操作由 ArgoCD 执行，开发人员无需直接访问生产集群
- 场景五：灾难恢复，集群配置存储在 Git，可快速在新集群重建全部应用，Recovery Time 从小时级降至分钟级

### 1.4 环境要求

| 组件 | 版本要求 | 说明 |
| --- | --- | --- |
| 操作系统 | Linux 内核 4.x+ | 推荐 Ubuntu 20.04/22.04 或 RHEL 8+ |
| Kubernetes | 1.24+ | ArgoCD 2.9+ 要求 Kubernetes 1.24+ |
| kubectl | 与 K8s 版本匹配 | 用于初始安装和手动干预 |
| Git 仓库 | GitHub/GitLab/Gitea | 支持 HTTPS/SSH 认证，建议配置 Webhook |
| Kustomize | 内置于 kubectl | ArgoCD 内置 Kustomize 5.0+ |
| 硬件配置 | 2C4G(最小) | 生产环境推荐 4C8G，HA 部署需 3 副本 |

---

## 二、详细步骤

### 2.1 准备工作

#### 2.1.1 系统检查

```
# 验证 Kubernetes 集群状态
kubectl cluster-info
kubectl get nodes
kubectl version --short

# 检查集群资源配额
kubectl top nodes
kubectl describe quota --all-namespaces

# 验证存储类（ArgoCD 需要持久化存储）
kubectl get storageclass
```

#### 2.1.2 安装依赖

```
# 创建 ArgoCD 命名空间
kubectl create namespace argocd

# 安装 ArgoCD（使用官方稳定版本）
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 等待所有组件就绪
kubectl wait --for=condition=available --timeout=600s \
  deployment/argocd-server \
  deployment/argocd-repo-server \
  deployment/argocd-dex-server \
  deployment/argocd-redis \
  -n argocd

# 安装 ArgoCD CLI
VERSION=$(curl -s https://api.github.com/repos/argoproj/argo-cd/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -sSL -o argocd-linux-amd64 "https://github.com/argoproj/argo-cd/releases/download/${VERSION}/argocd-linux-amd64"
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64

# 验证安装
argocd version
```

### 2.2 核心配置

#### 2.2.1 暴露 ArgoCD API Server

```
# 方式一：LoadBalancer（云环境推荐）
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

# 方式二：Ingress（内网环境推荐）
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-server-ingress
  namespace: argocd
  annotations:
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  ingressClassName: nginx
  rules:
  - host: argocd.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: argocd-server
            port:
              name: https
  tls:
  - hosts:
    - argocd.example.com
    secretName: argocd-server-tls
EOF

# 方式三：端口转发（开发测试）
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

**说明** ：生产环境建议使用 Ingress + TLS 证书，避免暴露 LoadBalancer 公网 IP。SSL Passthrough 保证端到端加密，ArgoCD Server 使用自签名证书或配置自定义证书。

#### 2.2.2 初始化 ArgoCD

```
# 获取初始 admin 密码
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d)
echo"ArgoCD admin password: ${ARGOCD_PASSWORD}"

# 登录 ArgoCD
argocd login argocd.example.com --username admin --password "${ARGOCD_PASSWORD}" --grpc-web

# 修改 admin 密码
argocd account update-password

# 删除初始密码 Secret（安全加固）
kubectl -n argocd delete secret argocd-initial-admin-secret
```

#### 2.2.3 配置 Git 仓库凭证

```
# 方式一：HTTPS 认证（使用 Personal Access Token）
argocd repo add https://github.com/your-org/your-repo.git \
  --username git \
  --password ghp_xxxxxxxxxxxxxxxxxxxx \
  --name my-repo

# 方式二：SSH 认证（推荐）
# 生成 SSH 密钥对
ssh-keygen -t ed25519 -C "argocd@example.com" -f ~/.ssh/argocd_ed25519 -N ""

# 将公钥添加到 Git 仓库的 Deploy Keys
cat ~/.ssh/argocd_ed25519.pub

# 添加私钥到 ArgoCD
argocd repo add git@github.com:your-org/your-repo.git \
  --ssh-private-key-path ~/.ssh/argocd_ed25519 \
  --name my-repo

# 验证仓库连接
argocd repo list
```

**参数说明** ：

- `--insecure-skip-server-verification` ：跳过 Git 服务器 TLS 验证（自签名证书场景）
- `--proxy` ：配置代理服务器访问外部 Git 仓库
- `--enable-lfs` ：启用 Git LFS 支持大文件

### 2.3 启动和验证

#### 2.3.1 创建 Application

```
# application.yaml
apiVersion:argoproj.io/v1alpha1
kind:Application
metadata:
name:guestbook
namespace:argocd
# Finalizer 确保删除 Application 时同步删除已部署资源
finalizers:
-resources-finalizer.argocd.argoproj.io
spec:
project:default
source:
    # Git 仓库地址
    repoURL:https://github.com/argoproj/argocd-example-apps.git
    targetRevision:HEAD
    path:guestbook
destination:
    server:https://kubernetes.default.svc
    namespace:default
syncPolicy:
    automated:
      prune:true      # 自动删除 Git 中不存在的资源
      selfHeal:true   # 自动修复手动修改
      allowEmpty:false
    syncOptions:
    -CreateNamespace=true# 自动创建目标命名空间
    retry:
      limit:5
      backoff:
        duration:5s
        factor:2
        maxDuration:3m
```
```
# 应用配置
kubectl apply -f application.yaml

# 查看 Application 状态
argocd app get guestbook

# 查看同步历史
argocd app history guestbook

# 手动触发同步
argocd app sync guestbook

# 查看实时日志
argocd app logs guestbook --follow
```

#### 2.3.2 功能验证

```
# 验证 Application 健康状态
argocd app list
# 预期输出：
# NAME        CLUSTER                         NAMESPACE  PROJECT  STATUS  HEALTH   SYNCPOLICY
# guestbook   https://kubernetes.default.svc  default    default  Synced  Healthy  Auto-Prune

# 验证资源同步状态
kubectl get all -n default -l app.kubernetes.io/instance=guestbook

# 测试自愈功能（手动修改资源）
kubectl scale deployment guestbook-ui -n default --replicas=5
# 等待 3 秒，ArgoCD 自动恢复副本数

# 测试修剪功能（从 Git 删除资源）
# 1. 从 Git 仓库删除某个 YAML 文件并提交
# 2. 观察 ArgoCD 自动删除对应资源
argocd app wait guestbook --health
```

---

## 三、示例代码和配置

### 3.1 完整配置示例

#### 3.1.1 Kustomize 多环境配置结构

```
# 仓库目录结构
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── overlays/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   ├── replica-patch.yaml
│   │   └── configmap-patch.yaml
│   ├── staging/
│   │   ├── kustomization.yaml
│   │   └── resources-patch.yaml
│   └── prod/
│       ├── kustomization.yaml
│       ├── replica-patch.yaml
│       ├── hpa.yaml
│       └── pdb.yaml
```
```
# base/kustomization.yaml
apiVersion:kustomize.config.k8s.io/v1beta1
kind:Kustomization

resources:
-deployment.yaml
-service.yaml
-configmap.yaml

commonLabels:
app:myapp
managed-by:argocd

namespace:myapp

images:
-name:myapp
newName:registry.example.com/myapp
newTag:latest
```
```
# base/deployment.yaml
apiVersion:apps/v1
kind:Deployment
metadata:
name:myapp
spec:
replicas:1
selector:
    matchLabels:
      app:myapp
template:
    metadata:
      labels:
        app:myapp
    spec:
      containers:
      -name:myapp
        image:myapp
        ports:
        -containerPort:8080
        resources:
          requests:
            cpu:100m
            memory:128Mi
          limits:
            cpu:500m
            memory:512Mi
        envFrom:
        -configMapRef:
            name:myapp-config
        livenessProbe:
          httpGet:
            path:/health
            port:8080
          initialDelaySeconds:30
          periodSeconds:10
        readinessProbe:
          httpGet:
            path:/ready
            port:8080
          initialDelaySeconds:5
          periodSeconds:5
```
```
# overlays/prod/kustomization.yaml
apiVersion:kustomize.config.k8s.io/v1beta1
kind:Kustomization

namespace:myapp-prod

bases:
-../../base

patchesStrategicMerge:
-replica-patch.yaml

resources:
-hpa.yaml
-pdb.yaml

images:
-name:myapp
newTag:v1.2.3# 生产环境固定版本

configMapGenerator:
-name:myapp-config
behavior:merge
literals:
-LOG_LEVEL=info
-ENVIRONMENT=production
-DB_POOL_SIZE=50
```
```
# overlays/prod/replica-patch.yaml
apiVersion:apps/v1
kind:Deployment
metadata:
name:myapp
spec:
replicas:5
template:
    spec:
      containers:
      -name:myapp
        resources:
          requests:
            cpu:500m
            memory:1Gi
          limits:
            cpu:2000m
            memory:4Gi
```
```
# overlays/prod/hpa.yaml
apiVersion:autoscaling/v2
kind:HorizontalPodAutoscaler
metadata:
name:myapp
spec:
scaleTargetRef:
    apiVersion:apps/v1
    kind:Deployment
    name:myapp
minReplicas:5
maxReplicas:20
metrics:
-type:Resource
    resource:
      name:cpu
      target:
        type:Utilization
        averageUtilization:70
-type:Resource
    resource:
      name:memory
      target:
        type:Utilization
        averageUtilization:80
behavior:
    scaleDown:
      stabilizationWindowSeconds:300
      policies:
      -type:Percent
        value:50
        periodSeconds:60
    scaleUp:
      stabilizationWindowSeconds:0
      policies:
      -type:Percent
        value:100
        periodSeconds:30
      -type:Pods
        value:4
        periodSeconds:30
      selectPolicy:Max
```

#### 3.1.2 ApplicationSet 批量管理

```
# applicationset.yaml - 多集群部署
apiVersion:argoproj.io/v1alpha1
kind:ApplicationSet
metadata:
name:myapp-multi-cluster
namespace:argocd
spec:
generators:
-matrix:
      generators:
      -git:
          repoURL:https://github.com/your-org/your-repo.git
          revision:HEAD
          directories:
          -path:overlays/*
      -clusters:
          selector:
            matchLabels:
              environment:production
template:
    metadata:
      name:'myapp-{{path.basename}}-{{name}}'
    spec:
      project:default
      source:
        repoURL:https://github.com/your-org/your-repo.git
        targetRevision:HEAD
        path:'{{path}}'
      destination:
        server:'{{server}}'
        namespace:'myapp-{{path.basename}}'
      syncPolicy:
        automated:
          prune:true
          selfHeal:true
        syncOptions:
        -CreateNamespace=true
```

### 3.2 实际应用案例

#### 案例一：配置敏感信息管理

**场景描述** ：使用 Sealed Secrets 或 External Secrets Operator 管理数据库密码、API Key 等敏感信息，避免明文存储在 Git 仓库。

**实现代码** ：

```
# 安装 Sealed Secrets Controller
kubectlapply-fhttps://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# 创建 Secret 并加密
echo-n'my-db-password'|kubectlcreatesecretgenericdb-credentials\
--dry-run=client\
--from-file=password=/dev/stdin\
-oyaml|\
kubeseal-oyaml>sealed-secret.yaml

# sealed-secret.yaml（可安全提交到 Git）
apiVersion:bitnami.com/v1alpha1
kind:SealedSecret
metadata:
name:db-credentials
namespace:default
spec:
encryptedData:
    password:AgBy3i4OJSWK+PiTySYZZA9rO43cGDEq...
template:
    metadata:
      name:db-credentials
      namespace:default
    type:Opaque
```

**运行结果** ：

```
# ArgoCD 同步后自动解密为 Secret
kubectl get secret db-credentials -o jsonpath='{.data.password}' | base64 -d
# 输出：my-db-password
```

#### 案例二：RBAC 权限配置

**场景描述** ：为开发团队配置只读权限，仅允许查看 dev 环境应用状态，禁止同步操作；为运维团队配置全部环境的管理权限。

**实现步骤** ：

1. 创建 AppProject 隔离资源
```
# project-dev.yaml
apiVersion:argoproj.io/v1alpha1
kind:AppProject
metadata:
name:dev-project
namespace:argocd
spec:
description:Developmentenvironmentproject
sourceRepos:
-'https://github.com/your-org/*'
destinations:
-namespace:'dev-*'
    server:https://kubernetes.default.svc
clusterResourceWhitelist:
-group:''
    kind:Namespace
namespaceResourceWhitelist:
-group:'apps'
    kind:Deployment
-group:''
    kind:Service
-group:''
    kind:ConfigMap
roles:
-name:developer
    description:Read-onlyaccesstodevapps
    policies:
    -p,proj:dev-project:developer,applications,get,dev-project/*,allow
    -p,proj:dev-project:developer,logs,get,dev-project/*,allow
    groups:
    -dev-team
```
2. 配置 ArgoCD RBAC
```
# argocd-rbac-cm ConfigMap
apiVersion:v1
kind:ConfigMap
metadata:
name:argocd-rbac-cm
namespace:argocd
data:
policy.default:role:readonly
policy.csv:|
    # 运维团队全部权限
    g, ops-team, role:admin

    # 开发团队限制权限
    p,role:developer,applications,get,*/*,allow
    p,role:developer,applications,sync,dev-project/*,allow
    p,role:developer,logs,get,*/*,allow
    g,dev-team,role:developer

    # 禁止删除生产应用
    p,role:developer,applications,delete,prod-project/*,deny
```
3. 集成 OIDC SSO（以 Keycloak 为例）
```
# argocd-cm ConfigMap
apiVersion:v1
kind:ConfigMap
metadata:
name:argocd-cm
namespace:argocd
data:
url:https://argocd.example.com
oidc.config:|
    name: Keycloak
    issuer: https://keycloak.example.com/realms/master
    clientID: argocd
    clientSecret: $oidc.keycloak.clientSecret
    requestedScopes:
    - openid
    - profile
    - email
    - groups
```

---

## 四、最佳实践和注意事项

### 4.1 最佳实践

#### 4.1.1 性能优化

- **优化点一：减少 Git 轮询频率**
	```
	# argocd-cm ConfigMap
	apiVersion:v1
	kind:ConfigMap
	metadata:
	name:argocd-cm
	namespace:argocd
	data:
	timeout.reconciliation:300s# 默认 180s，大规模集群建议 300s+
	timeout.reconciliation.jitter:30s
	```
	说明：默认每 3 分钟轮询一次 Git 仓库，大规模部署建议延长间隔并配置 Webhook 实现事件驱动同步。
- **优化点二：启用资源缓存**
	```
	# 编辑 argocd-application-controller StatefulSet
	kubectl edit statefulset argocd-application-controller -n argocd
	# 添加环境变量
	env:
	- name: ARGOCD_APPLICATION_CONTROLLER_REPLICAS
	  value: "3"
	- name: ARGOCD_APPLICATION_CONTROLLER_SHARD
	  valueFrom:
	    fieldRef:
	      fieldPath: metadata.name
	```
- 配置 Redis HA 提升缓存性能
	- 启用 Application Controller 分片（处理 1000+ Application）
- **优化点三：优化 Diff 计算**
	```
	# Application 配置
	spec:
	ignoreDifferences:
	-group:apps
	    kind:Deployment
	    jsonPointers:
	    -/spec/replicas# 忽略 HPA 自动调整的副本数
	-group:""
	    kind:Secret
	    jsonPointers:
	    -/data# 忽略 External Secrets Operator 动态更新
	```

#### 4.1.2 安全加固

- **安全措施一：限制资源权限**
	```
	# AppProject 白名单机制
	spec:
	clusterResourceWhitelist:
	-group:''
	    kind:Namespace
	clusterResourceBlacklist:
	-group:''
	    kind:ResourceQuota
	-group:'rbac.authorization.k8s.io'
	    kind:ClusterRole
	```
	说明：禁止应用创建 ClusterRole、PersistentVolume 等集群级资源，防止权限提升。
- **安全措施二：启用 Admission Webhook**
	```
	# argocd-cm ConfigMap
	data:
	  resource.customizations:|
	    admissionregistration.k8s.io/MutatingWebhookConfiguration:
	      health.lua: |
	        hs = {}
	        hs.status = "Healthy"
	        return hs
	```
	配合 OPA Gatekeeper 或 Kyverno 实现策略即代码，拦截不合规资源。
- **安全措施三：Git 签名验证**
	```
	# 启用 GPG 签名验证
	argocd repo add https://github.com/your-org/your-repo.git \
	  --username git \
	  --password $TOKEN \
	  --enable-lfs \
	  --gpg-key-id 0x1234567890ABCDEF
	```

#### 4.1.3 高可用配置

- **HA方案一：组件多副本部署**
	```
	# argocd-server 副本数调整
	kubectlscaledeploymentargocd-server-nargocd--replicas=3
	kubectlscaledeploymentargocd-repo-server-nargocd--replicas=3
	# Application Controller 使用 StatefulSet，启用分片
	kubectlscalestatefulsetargocd-application-controller-nargocd--replicas=3
	```
- **HA方案二：Redis Sentinel 部署**
	```
	# 使用 Redis HA 替代单实例 Redis
	# 安装 Redis Sentinel
	kubectlapply-nargocd-fhttps://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/ha/redis-ha/redis-ha.yaml
	```
- **备份策略** ：
	```
	#!/bin/bash
	# 备份所有 Application 定义
	kubectl get applications -n argocd -o yaml > applications-backup.yaml
	# 备份所有 AppProject 定义
	kubectl get appprojects -n argocd -o yaml > appprojects-backup.yaml
	# 备份配置
	kubectl get cm argocd-cm argocd-rbac-cm argocd-cmd-params-cm -n argocd -o yaml > argocd-config-backup.yaml
	```

### 4.2 注意事项

#### 4.2.1 配置注意事项

⚠️ **警告** ：生产环境必须禁用 admin 账户，强制使用 SSO 认证，所有操作可追溯到个人账户。

- ❗ 注意事项一：syncPolicy.automated 慎用于生产环境，建议仅对基础设施组件启用自动同步，业务应用采用手动审批
- ❗ 注意事项二：prune 和 selfHeal 同时启用可能导致误删资源，务必配置 ignoreDifferences 排除动态字段
- ❗ 注意事项三：Kustomize 的 namespace 字段会覆盖所有资源的 namespace，使用 overlay 时需注意命名空间冲突

#### 4.2.2 常见错误

| 错误现象 | 原因分析 | 解决方案 |
| --- | --- | --- |
| ComparisonError: failed to unmarshal | Kustomize 构建失败，语法错误 | 本地执行 `kubectl kustomize overlays/prod` 验证配置 |
| SyncFailed: PermissionDenied | ServiceAccount 权限不足 | 检查 AppProject 的 clusterResourceWhitelist 配置 |
| OutOfSync 但实际已同步 | ignoreDifferences 配置不当 | 添加动态字段到 ignoreDifferences 列表 |
| Health status: Progressing | 资源健康检查超时 | 检查 Pod 日志，调整 health check 参数 |
| Webhook trigger failed | Webhook Secret 不匹配 | 重新生成 Webhook URL，更新 Git 仓库配置 |

#### 4.2.3 兼容性问题

- **版本兼容** ：ArgoCD 2.9+ 要求 Kubernetes 1.24+，使用旧版 K8s 需安装 ArgoCD 2.7 LTS
- **平台兼容** ：Helm Chart 需启用 `--enable-helm` ，Jsonnet 需安装 `argocd-jsonnet`
- **组件依赖** ：Kustomize 版本与 kubectl 绑定，使用高级特性（replacements）需确保 Kustomize 5.0+

---

## 五、故障排查和监控

### 5.1 故障排查

#### 5.1.1 日志查看

```
# 查看 Application Controller 日志（核心组件）
kubectl logs -n argocd deployment/argocd-application-controller --tail=100 -f

# 查看 Repo Server 日志（Git 拉取和 Kustomize 构建）
kubectl logs -n argocd deployment/argocd-repo-server --tail=100 -f

# 查看 Server 日志（API 请求）
kubectl logs -n argocd deployment/argocd-server --tail=100 -f

# 查看特定 Application 的同步日志
argocd app logs myapp --follow

# 查看详细错误信息
kubectl describe application myapp -n argocd
```

#### 5.1.2 常见问题排查

**问题一：Git 仓库连接失败**

```
# 诊断命令
argocd repo list
kubectl get secret -n argocd -l argocd.argoproj.io/secret-type=repository

# 测试 Git 连接
kubectl exec -it deployment/argocd-repo-server -n argocd -- sh
git ls-remote https://github.com/your-org/your-repo.git
```

**解决方案** ：

1. 检查凭证是否过期（PAT、SSH Key）
2. 验证网络连通性（代理、防火墙）
3. 查看 Repo Server 日志确认具体错误

**问题二：Application 一直处于 Progressing 状态**

```
# 诊断命令
argocd app get myapp --refresh
kubectl get pods -n myapp -o wide
kubectl describe pod <pod-name> -n myapp
```

**解决方案** ：

1. 检查 Pod 事件（镜像拉取失败、资源不足）
2. 验证健康检查配置（存活探针、就绪探针）
3. 调整 Application 的健康检查超时时间

**问题三：Kustomize 构建失败**

- **症状** ：Application 状态显示 ComparisonError
- **排查** ：
	```
	# 本地复现问题
	git clone <repo-url>
	cd overlays/prod
	kubectl kustomize . --enable-helm
	```
- **解决** ：修复 kustomization.yaml 语法错误，验证资源引用路径

#### 5.1.3 调试模式

```
# 开启 Application Controller 调试日志
kubectl set env deployment/argocd-application-controller \
  -n argocd \
  ARGOCD_LOG_LEVEL=debug

# 开启 Repo Server 详细日志
kubectl set env deployment/argocd-repo-server \
  -n argocd \
  ARGOCD_LOG_LEVEL=debug \
  ARGOCD_EXEC_TIMEOUT=180s

# 禁用缓存强制重新构建
argocd app get myapp --hard-refresh
```

### 5.2 性能监控

#### 5.2.1 关键指标监控

```
# Application 同步时长
argocd app list -o json | jq '.[] | {name: .metadata.name, syncTime: .status.operationState.finishedAt}'

# Repo Server CPU/内存使用
kubectl top pod -n argocd -l app.kubernetes.io/name=argocd-repo-server

# Application Controller 处理队列长度
kubectl logs -n argocd deployment/argocd-application-controller | grep "app reconciliation"

# Redis 连接数
kubectl exec -n argocd deployment/argocd-redis -- redis-cli info clients
```

#### 5.2.2 监控指标说明

| 指标名称 | 正常范围 | 告警阈值 | 说明 |
| --- | --- | --- | --- |
| argocd\_app\_sync\_total | \- | 失败率 >5% | 同步成功率，区分成功/失败 |
| argocd\_app\_reconcile\_duration | <30s | \>60s | 应用对账耗时，反映性能瓶颈 |
| argocd\_git\_request\_duration | <5s | \>15s | Git 操作耗时，检测网络问题 |
| argocd\_kubectl\_exec\_pending | <10 | \>50 | kubectl 执行队列长度 |
| argocd\_redis\_request\_total | \- | 错误率 >1% | Redis 请求统计 |

#### 5.2.3 监控告警配置

```
# Prometheus PrometheusRule
apiVersion:monitoring.coreos.com/v1
kind:PrometheusRule
metadata:
name:argocd-alerts
namespace:argocd
spec:
groups:
-name:argocd
    interval:30s
    rules:
    -alert:ArgoCDAppSyncFailed
      expr:|
        sum(increase(argocd_app_sync_total{phase="Failed"}[5m])) > 3
      for:5m
      labels:
        severity:warning
      annotations:
        summary:"ArgoCD Application 同步失败过多"
        description:"Application {{ $labels.name }} 同步失败次数 {{ $value }}"

    -alert:ArgoCDAppOutOfSync
      expr:|
        argocd_app_info{sync_status="OutOfSync"} == 1
      for:10m
      labels:
        severity:warning
      annotations:
        summary:"Application 长时间未同步"
        description:"{{ $labels.name }} 已超过 10 分钟未同步"

    -alert:ArgoCDRepoServerDown
      expr:|
        up{job="argocd-repo-server"} == 0
      for:2m
      labels:
        severity:critical
      annotations:
        summary:"ArgoCD Repo Server 不可用"
```

### 5.3 备份与恢复

#### 5.3.1 备份策略

```
#!/bin/bash
# 文件名：argocd-backup.sh
# 功能：备份 ArgoCD 所有配置

BACKUP_DIR="/backup/argocd/$(date +%Y%m%d)"
mkdir -p "${BACKUP_DIR}"

# 备份 Application
kubectl get applications -n argocd -o yaml > "${BACKUP_DIR}/applications.yaml"

# 备份 AppProject
kubectl get appprojects -n argocd -o yaml > "${BACKUP_DIR}/appprojects.yaml"

# 备份 ApplicationSet
kubectl get applicationsets -n argocd -o yaml > "${BACKUP_DIR}/applicationsets.yaml"

# 备份配置 ConfigMap
kubectl get cm -n argocd argocd-cm argocd-rbac-cm argocd-cmd-params-cm -o yaml > "${BACKUP_DIR}/configmaps.yaml"

# 备份 Secret（不含敏感数据）
kubectl get secrets -n argocd -l argocd.argoproj.io/secret-type -o yaml > "${BACKUP_DIR}/secrets.yaml"

# 备份到远程存储
tar -czf "${BACKUP_DIR}.tar.gz""${BACKUP_DIR}"
aws s3 cp "${BACKUP_DIR}.tar.gz" s3://backups/argocd/

# 清理 7 天前的备份
find /backup/argocd -name "*.tar.gz" -mtime +7 -delete

echo"Backup completed: ${BACKUP_DIR}.tar.gz"
```

#### 5.3.2 恢复流程

1. **停止 ArgoCD 同步**
```
# 暂停所有 Application 自动同步
for app in $(argocd app list -o name); do
  argocd app set$app --sync-policy none
done
```
2. **恢复配置**
```
# 解压备份
tar -xzf /backup/argocd/20240315.tar.gz -C /tmp

# 恢复 AppProject
kubectl apply -f /tmp/20240315/appprojects.yaml

# 恢复 Application
kubectl apply -f /tmp/20240315/applications.yaml

# 恢复配置
kubectl apply -f /tmp/20240315/configmaps.yaml
```
3. **验证恢复**
```
# 检查 Application 状态
argocd app list

# 触发同步验证
argocd app sync --dry-run guestbook
```
4. **重启服务**
```
# 重启 ArgoCD 组件
kubectl rollout restart deployment -n argocd argocd-server
kubectl rollout restart deployment -n argocd argocd-repo-server
kubectl rollout restart statefulset -n argocd argocd-application-controller
```

---

## 六、总结

### 6.1 技术要点回顾

- ✅ **GitOps 核心价值** ：Git 作为单一事实来源，实现配置的版本化、可审计、快速回滚，降低人为操作风险
- ✅ **ArgoCD 架构** ：拉模式实现持续同步，Application Controller 负责状态对账，Repo Server 处理 Git 和配置工具集成
- ✅ **Kustomize 配置管理** ：通过 base + overlay 机制优雅解决多环境配置差异，避免重复维护
- ✅ **安全与权限** ：AppProject 实现资源隔离，RBAC 配置细粒度权限控制，SSO 集成企业认证体系
- ✅ **高可用与性能** ：多副本部署、Redis HA、Application Controller 分片支持大规模集群管理

### 6.2 进阶学习方向

1. **Argo Rollouts 渐进式交付** ：实现蓝绿部署、金丝雀发布，结合 Istio/Nginx 实现流量分析和自动回滚
- 学习资源：https://argo-rollouts.readthedocs.io
	- 实践建议：从蓝绿部署开始，逐步过渡到基于指标的自动化金丝雀发布
3. **多租户与多集群管理** ：使用 Cluster Secret、ApplicationSet 矩阵生成器管理数百个集群
- 学习资源：https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/
	- 实践建议：设计租户隔离方案，配置跨集群资源配额和网络策略
5. **策略即代码** ：集成 OPA Gatekeeper 或 Kyverno 实现准入控制、镜像扫描、资源配额自动化
- 学习资源：https://www.openpolicyagent.org/docs/latest/kubernetes-introduction/
	- 实践建议：从镜像白名单、Label 强制策略开始，逐步覆盖安全基线

### 6.3 参考资料

- ArgoCD 官方文档 - 完整的安装、配置、操作指南
- Kustomize 官方文档 - 配置管理最佳实践和高级特性
- GitOps Working Group - CNCF GitOps 标准和原则
- Argo CD Operator - Operator 方式管理 ArgoCD 生命周期
- ArgoCD 最佳实践 - 官方推荐的生产环境配置

---

## 附录

### A. 命令速查表

```
# Application 管理
argocd app create <name> --repo <url> --path <path> --dest-server <server> --dest-namespace <ns>
argocd app get <name>                          # 查看应用详情
argocd app sync <name>                         # 手动同步
argocd app diff <name>                         # 查看配置差异
argocd app history <name>                      # 查看同步历史
argocd app rollback <name> <revision>          # 回滚到指定版本
argocd app delete <name>                       # 删除应用
argocd app set <name> --sync-policy automated  # 配置自动同步

# 仓库管理
argocd repo add <url> --username <user> --password <pass>
argocd repo list                               # 列出所有仓库
argocd repo rm <url>                           # 删除仓库

# 集群管理
argocd cluster add <context-name>              # 添加集群
argocd cluster list                            # 列出所有集群
argocd cluster get <server-url>                # 查看集群信息

# 项目管理
argocd proj create <name>                      # 创建项目
argocd proj add-source <proj> <repo>           # 添加源仓库
argocd proj add-destination <proj> <server> <ns>  # 添加目标集群
```

### B. 配置参数详解

**Application 核心参数** ：

- `source.repoURL` ：Git 仓库地址，支持 HTTPS/SSH 协议
- `source.targetRevision` ：分支/标签/Commit SHA，HEAD 表示默认分支
- `source.path` ：仓库内配置文件路径，支持 Kustomize/Helm/Plain YAML
- `destination.server` ：目标集群 API Server 地址， `https://kubernetes.default.svc` 表示当前集群
- `syncPolicy.automated.prune` ：自动删除 Git 中不存在的资源
- `syncPolicy.automated.selfHeal` ：自动修复手动修改（每 5 秒检测一次）
- `syncPolicy.syncOptions` ：同步选项，如 CreateNamespace、PruneLast、RespectIgnoreDifferences

**AppProject 权限控制** ：

- `sourceRepos` ：允许的 Git 仓库白名单，支持通配符
- `destinations` ：允许部署的目标集群和命名空间
- `clusterResourceWhitelist` ：允许创建的集群级资源（空数组表示禁止所有）
- `namespaceResourceWhitelist` ：允许创建的命名空间级资源

### C. 术语表

| 术语 | 英文 | 解释 |
| --- | --- | --- |
| 声明式配置 | Declarative Configuration | 描述期望状态而非操作步骤，系统自动消除偏差 |
| 同步 | Sync | 将 Git 中的期望状态应用到 Kubernetes 集群 |
| 对账 | Reconciliation | 周期性比较实际状态与期望状态，检测漂移 |
| 修剪 | Prune | 删除 Git 中不存在但集群中存在的资源 |
| 自愈 | Self-Heal | 自动撤销手动修改，恢复到 Git 定义的状态 |
| 健康状态 | Health Status | 资源的运行状态（Healthy/Progressing/Degraded/Suspended） |
| 同步状态 | Sync Status | 配置的同步状态（Synced/OutOfSync） |
| 应用集 | ApplicationSet | 批量生成 Application，支持多集群/多租户场景 |

**微**

**信**

**群**

WeChat group

为了方便大家更好的交流运维等相关技术问题，创建了微信交流群，需要加群的小伙伴们可以扫一扫下面的二维码加我为好友拉您进群（备注：加群）。

**代**

**码**

仓

库

| **代码仓库** | **网址** |
| --- | --- |
| Github | https://github.com/raymond999999 |
| Gitee | https://gitee.com/raymond9 |

**博**

**客**

Blog

| **博客** | **网址** |
| --- | --- |
| CSDN | https://blog.csdn.net/qq\_25599925 |
| 稀土掘金 | https://juejin.cn/user/4262187909781751 |
| 知识星球 | https://wx.zsxq.com/group/15555885545422 |
| 阿里云社区 | https://developer.aliyun.com/profile/snzh3xpxaf6sg |
| 腾讯云社区 | https://cloud.tencent.com/developer/user/11823619 |
| 华为云社区 | https://developer.huaweicloud.com/usercenter/mycommunity/dynamics |

访问博客网站，查看更多优质原创内容。

云原生 · 目录

继续滑动看下一个

Raymond运维

向上滑动看下一个