# ArgoCD介绍

Argo CD 是一个专为 Kubernetes 环境设计的声明式、GitOps 持续交付 (CD) 工具。它隶属于 [CNCF](https://www.cncf.io/) 旗下的 [Argo 项目](https://argoproj.github.io/)，是一个被广泛采用的开源项目。

Argo CD 的核心思想是将 Git 仓库作为应用部署和基础设施配置的**唯一事实来源** (Single Source of Truth)。-- GitOps理念

它自动同步 Git 仓库中定义的期望应用状态（通常是 Kubernetes 清单 YAML 文件、Helm Charts、Kustomize 目录等），与目标 Kubernetes 集群中的实际运行状态，用一些自动化工具，确保两者始终保持一致。这种模式被称为 GitOps。

官网地址：[Argo CD 中文文档 平台工程 Devops](https://argocd.devops.gold/)

## 核心概念与工作原理

1. **声明式配置：** 用户通过在 Git 仓库中定义应用程序的期望状态（使用 YAML、Helm、Kustomize     等）。Argo CD 不关心 *如何* 达到这个状态，只关心集群当前状态是否与 Git 中定义的期望状态匹配。
2. **Git 作为事实源 (Source of Truth)：** Git 仓库存储了所有配置的版本历史，提供了审计追踪、回滚能力和协作基础。
3. **持续同步：** Argo CD 持续监控：
   - **源仓库 (Source Repository)：** 包含应用清单的 Git 仓库（或 Helm Chart 仓库、OCI 仓库）。
   - **目标集群 (Target Cluster)：** 运行应用程序的一个或多个 Kubernetes 集群。
4. **状态比对与自动协调：** 当检测到 Git 中的期望状态与集群中的实际状态存在差异时：
   - Argo CD 会计算出一个差异列表 (Diff)。
   - 根据配置的同步策略（自动或手动），Argo CD 可以自动或由用户触发**同步 (Sync)** 操作。
   - 同步操作会调用 Kubernetes API，应用必要的更改（创建、更新、删除资源），使集群状态收敛到 Git 中定义的状态。
5. **健康状态分析：** Argo CD 不仅检查资源是否存在，还利用内置的或自定义的健康检查来分析部署的应用是否真正“健康”运行（例如，Pod 是否 Running 且 Ready，Deployment 是否达到期望副本数等）。

## 主要功能与特性

1. 自动化部署与同步：自动将 Git 中的更改应用到 Kubernetes 集群，实现持续部署流水线。
2. 可视化状态管理：
   - 直观的 Web UI：提供清晰的界面查看应用状态、资源拓扑图、同步状态、健康状态、事件日志和历史记录。
   - 强大的 CLI (argocd): 提供命令行工具进行所有操作和管理。
   - 丰富的 API： 支持与其他工具和自动化流程集成。
3. 多集群/多环境管理：集中管理部署到多个 Kubernetes 集群（开发、测试、预发布、生产）和多个命名空间中的应用。
4. 灵活的配置来源： 支持多种方式定义应用：
   - Kubernetes 清单 (YAML/JSON)
   - Helm Charts (来自 Chart 仓库或 Git)
   - Kustomize 应用
   - Jsonnet 文件
   - 自定义配置管理工具插件
5. 回滚与历史记录：利用 Git 的版本控制能力，轻松回滚到任何先前提交的应用状态。
6. 访问控制与安全性：
	- 基于角色的访问控制 (RBAC)：精细控制用户/组对项目和应用的访问权限。
	- 单点登录 (SSO) 集成：支持 OIDC (如 Google, GitHub, GitLab, Dex, Keycloak)、SAML 2.0、LDAP。
	- Git 仓库认证：支持 HTTPS (用户名/密码)、SSH 私钥等方式安全访问源仓库。
	- 集群访问管理：安全地存储和管理目标集群的访问凭证。
7. 同步策略与钩子：
	- 自动/手动同步：可配置为自动应用 Git 更改，或需要手动审批。
	- 同步波次 (Sync Waves)：控制资源同步的顺序（例如，先创建 CRD，再创建依赖它的 CR）。
	- 同步钩子 (Sync Hooks)：在同步操作的生命周期中（PreSync, Sync, PostSync, SyncFail）执行自定义操作（如数据库迁移、通知）。
8. 应用健康状态分析：内置对常见 Kubernetes 资源（Deployment, StatefulSet, DaemonSet, Service, Ingress 等）的健康检查，支持自定义健康检查逻辑。
9. 参数覆盖：支持在 Argo CD 层面覆盖 Helm/Kustomize 参数，便于管理不同环境（如 values-production.yaml）的差异化配置，而无需修改主 Git 仓库。
10. Webhook 集成：支持 Git 仓库的 Webhook（如 GitHub, GitLab, Bitbucket），在代码推送后立即触发同步，实现更快的反馈循环。
11. 项目组织： 通过 Projects 对应用进行逻辑分组，并应用共享的策略（如源仓库白名单、目标集群/命名空间白名单、角色权限）。

## 组件
### API Server


### Repository

### Application Controller

# 安装ArgoCD-基于yaml-非HA
## 文档
参考：[快速开始 - Argo CD 中文文档 平台工程 Devops](https://argocd.devops.gold/getting_started/#1-argo-cd)

## 安装
~~~sh
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.1.9/manifests/install.yaml
~~~
> 如果你对 UI、SSO、多集群管理这些特性不感兴趣，只想把应用变更同步到集群中，那么可以直接安装核心组件即可：
>
> `kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.1.9/manifests/core-install.yaml`

## 访问UI

### 方法1: NodePort
用NodePort svc访问UI界面：

~~~sh
kubectl edit svc argocd-server -n argocd
# type: ClusterIP改成type: NodePort
~~~

查看该svc的高位端口，访问登录界面。

默认用户名admin，密码获取：
~~~sh
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
~~~
### 方法2: Istio
官网提供了基于yaml安装的argocd用istio访问UI的配置方法： https://argocd.devops.gold/operator-manual/ingress/#istio

### 方法3：端口转发
可以使用`kubectl` 端口转发功能连接到 API 服务器，而无需暴露服务：`kubectl port-forward svc/argocd-server -n argocd 8080:443`。然后可以通过`https://localhost:8080` 访问 API 服务器。

# 安装ArgoCD-HA
高可用安装参考： https://argocd.devops.gold/operator-manual/installation/#_4
~~~sh
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.1.9/manifests/ha/install.yaml
~~~

# 安装ArgoCD-基于helm chart

> 注意：目前argocd helm chart仅支持非高可用安装方式。
>
> 如需高可用安装，参考：[ArgoCD-HA](https://argocd.devops.gold/operator-manual/installation/#_4)

## 文档
github release：[argoproj/argo-helm: ArgoProj Helm Charts](https://github.com/argoproj/argo-helm)
artifactHub：[argo-cd 3.9.0 · argoproj/argo](https://artifacthub.io/packages/helm/argo/argo-cd/3.9.0)

## 下载
~~~sh
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update argo
helm pull argo/argo-cd --version 8.3.0
~~~

## 配置
修改values.yaml文件【暂无，直接装】：

~~~yaml

~~~

## 安装
~~~sh
cd argo-cd
helm upgrade -i argocd . -n argocd --create-namespace
~~~

## 访问UI
argocd默认开了tls，svc的80端口会被重定向到443端口。
### 方法1：NodePort
- 将argo-server这个svc改成NodePort，用http://节点IP+高位端口访问。（弹证书信任，直接点信任证书就行）
- 默认用户名admin，密码获取：
~~~sh
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
~~~

### 方法2：Istio
集群安装了istio，自定义一套gateway和virtual service访问。
- 首先需要把argocd的tls关掉：
	- 找到cm：`kubectl edit cm -n argocd argocd-cmd-params-cm`
	- 加一项data：`server.insecure: "true"`
	- rollout restart deployment argocd-server
- 创建gateway：
  ~~~yaml
  apiVersion: networking.istio.io/v1 
  kind: Gateway 
  metadata: 
    name: argocd-gateway 
    namespace: argocd
  spec:
    # The selector matches the ingress gateway pod labels.
    # If you installed Istio using Helm following the standard documentation, this would be "istio=ingress"
    selector: 
      istio: gateway # 匹配的是ingressgateway pod的label 
    servers: 
    - port: 
        number: 80 
        name: http 
        protocol: HTTP 
      hosts: 
      - "argocd.hanxux.local" # 发布域名
  ~~~
- 创建virtual service：
  ~~~yaml
  apiVersion: networking.istio.io/v1 
  kind: VirtualService 
  metadata: 
    name: argocd-vs
    namespace: argocd
  spec: 
    hosts: 
    - "argocd.hanxux.local" 
    gateways: 
    - argocd-gateway 
    http: 
    - match:
      - uri:
          prefix: /
      route: 
      - destination: 
          host: argocd-server.argocd.svc.cluster.local 
          port: 
            number: 80
  ~~~
- 宿主机加上hosts解析，通过 域名 + [istio ingress gateway高位端口] 访问（argocd.hanxux.local:30080）
- 默认用户名admin，密码获取：
~~~sh
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
~~~

### 方法3：端口转发
可以使用`kubectl` 端口转发功能连接到 API 服务器，而无需暴露服务：`kubectl port-forward svc/argocd-server -n argocd 8080:443`。然后可以通过`https://localhost:8080` 访问 API 服务器。

# argocd ingress说明
Argo CD 会运行一个 gRPC 服务（由 CLI 使用）和 HTTP/HTTPS 服务（由 UI 使用），这两种协议都由 `argocd-server` 服务在以下端口进行暴露：
- 443 - gRPC/HTTPS
- 80 - HTTP（重定向到 HTTPS）

我们可以通过配置 Ingress 的方式来对外暴露服务，其他 Ingress 控制器的配置可以参考官方文档 https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/ 进行配置。

Argo CD 在同一端口 (443) 上提供多个协议 (gRPC/HTTPS)，所以当我们为 argocd 服务定义单个 nginx ingress 对象和规则的时候有点麻烦，因为 `nginx.ingress.kubernetes.io/backend-protocol` 这个 annotation 只能接受一个后端协议（例如 HTTP、HTTPS、GRPC、GRPCS）。
## 方法1: 单个Ingress+SSL PassThrough
为了使用单个 ingress 规则和主机名来暴露 Argo CD APIServer，必须使用 `nginx.ingress.kubernetes.io/ssl-passthrough` 这个 `annotation` 来传递 TLS 连接并校验 Argo CD APIServer 上的 TLS。
~~~yaml
apiVersion: networking.k8s.io/v1  
kind: Ingress  
metadata:  
  name: argocd-server-ingress  
  namespace: argocd  
  annotations:  
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"  
    nginx.ingress.kubernetes.io/ssl-passthrough: "true"  
spec:  
  ingressClassName: nginx-default
  rules:  
    - host: argocd.hanxux.local  
      http:  
        paths:  
          - path: /  
            pathType: Prefix  
            backend:  
              service:  
                name: argocd-server  
                port:  
                  name: https
~~~

上述规则在 Argo CD APIServer 上校验 TLS，该服务器检测到正在使用的协议，并做出适当的响应。**请注意，`nginx.ingress.kubernetes.io/ssl-passthrough` 注解要求将 `--enable-ssl-passthrough` 标志添加到 `nginx-ingress-controller` 的命令行参数中。**

## 方法2: 多个ingress
由于 `ingress-nginx` 的每个 Ingress 对象仅支持一个协议，因此另一种方法是定义两个 Ingress 对象。一个用于 HTTP/HTTPS，另一个用于 gRPC。

如下所示为 HTTP/HTTPS 的 Ingress 对象：
~~~yaml
apiVersion: networking.k8s.io/v1  
kind: Ingress  
metadata:  
  name: argocd-server-http-ingress  
  namespace: argocd  
  annotations:  
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"  
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"  
spec:  
  ingressClassName: nginx  
  rules:  
    - http:  
        paths:  
          - path: /  
            pathType: Prefix  
            backend:  
              service:  
                name: argocd-server  
                port:  
                  name: http  
      host: argocd.k8s.local  
  tls:  
    - hosts:  
        - argocd.k8s.local  
      secretName: argocd-secret # do not change, this is provided by Argo CD
~~~

gRPC 协议对应的 Ingress 对象如下所示:
~~~yaml
apiVersion: networking.k8s.io/v1  
kind: Ingress  
metadata:  
  name: argocd-server-grpc-ingress  
  namespace: argocd  
  annotations:  
    nginx.ingress.kubernetes.io/backend-protocol: "GRPC"  
spec:  
  ingressClassName: nginx  
  rules:  
    - http:  
        paths:  
          - path: /  
            pathType: Prefix  
            backend:  
              service:  
                name: argocd-server  
                port:  
                  name: https  
      host: grpc.argocd.k8s.local  
  tls:  
    - hosts:  
        - grpc.argocd.k8s.local  
      secretName: argocd-secret # do not change, this is provided by Argo CD
~~~

## 禁用TLS
然后我们需要在禁用 TLS 的情况下运行 APIServer：
- 方法1：编辑 argocd-server 这个 Deployment 以将 `--insecure` 标志添加到 argocd-server 命令
- 方法2：在 `argocd-cmd-params-cm` ConfigMap 中设置 `server.insecure: "true"` 即可。

创建完成后，我们就可以通过 `argocd.k8s.local` 来访问 Argo CD 服务了，不过需要注意我们这里配置的证书是自签名的，所以在第一次访问的时候会提示不安全，强制跳转即可。

# 基本使用
## 安装argocd cli【可选】
可以在本地安装argocd cli方便管理
```sh
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/download/v3.1.9/argocd-darwin-arm64
chmod +x /usr/local/bin/argocd
```
## 常用命令
~~~sh
# 登录命令 -- 在宿主机
argocd login grpc.argocd.hanxux.local
# 登录命令 -- 在master节点
argocd login 10.96.23.131
#将 kubeconfig 中的集群上下文添加到 Argo CD 进行管理
argocd cluster add <context-name>
#更新当前登录用户的密码
#在更改密码后，您应该从 argocd 命名空间中删除 `argocd-initial-admin-secret`。该 Secret 除存储初始生成的明文密码外没有其他用途，可以随时安全删除。如果需要重新生成管理员密码，argocd 将按需重新创建该Secret。
argocd account update-password
#显示 Argo CD 客户端和服务器的版本信息
argocd version
#查看所有命令的帮助信息
argocd help
#生成 Bash 自动补全脚本
argocd completion bash
#创建新的 Argo CD 应用
argocd app create myapp --repo https://your-git-repo.com/repo.git --pa拗4
#列出所有已管理的应用筈
argocd app list
#获取指定应用的详细信息
argocd app get <app-name>
#手动同步应用，使其与 Git 中定义的状态一致
argocd app sync <app-name>
#删除一个 ArgoCD 应用
argocd app delete <app-name>
#列出Argo CD 当前管理的所有 Kubernetes 集群
argocd cluster list
~~~

## 登录web-UI
默认用户名admin，获取初始密码：
```sh
kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## 配置集群
### 外部集群
- 由于 Argo CD 支持部署应用到多集群，所以如果你要将应用部署到外部集群的时候，需要先将外部集群的认证信息注册到 Argo CD 中。
### 内部集群
- 如果是在内部部署（运行 Argo CD 的同一个集群，默认不需要配置），直接使用 `https://kubernetes.default.svc` 作为应用的 K8S APIServer 地址即可。

# 应用部署示例 -- 基于yaml
Git 仓库 https://github.com/argoproj/argocd-example-apps.git 是一个包含留言簿应用程序的示例库，我们可以用该应用来演示 Argo CD 的工作原理。

## 创建Application
### 手动同步
~~~yaml
apiVersion: argoproj.io/v1alpha1  
kind: Application  
metadata:  
  name: guestbook  
spec:  
  destination:  
    namespace: default  
    server: "https://kubernetes.default.svc"  
  source:  
    path: guestbook  
    repoURL: "https://github.com/cnych/argocd-example-apps"  
    targetRevision: HEAD  
  project: default  
  syncPolicy:  
    automated: null # null 表示手动同步
~~~
#### 查看状态
- 创建完可以在UI上看到状态。
- 也可以用命令行：`argocd app get argocd/guestbook`。
应用程序状态为初始 `OutOfSync` 状态，因为应用程序尚未部署，并且尚未创建任何 Kubernetes 资源。
#### 执行Sync
- 方法1: 要同步（部署）应用程序，可以执行如下所示命令：
~~~sh
argocd app sync argocd/guestbook
~~~

- 方法2: 直接点击 UI 界面上应用的 `Sync` 按钮也可开始同步

### 自动同步

设置sync policy参数就是自动同步

~~~yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  # Application 所在的命名空间，通常是 argocd
  namespace: argocd
  labels:
    app: guestbook
    env: dev
  annotations:
    # 通知配置，当应用状态变化时发送通知
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: my-channel
  # Finalizers 确保在删除 Application 时同时删除相关资源
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  # 目标集群和命名空间配置
  destination:
    # 目标命名空间，应用将部署到这个命名空间
    namespace: guestbook
    # 目标 Kubernetes 集群的 API Server 地址
    # 使用 "https://kubernetes.default.svc" 表示 ArgoCD 所在的集群
    server: "https://kubernetes.default.svc"
    # 也可以使用集群名称代替 server
    # name: in-cluster

  # Git 仓库源配置
  source:
    # Git 仓库路径，指向应用的 manifests 所在目录
    path: guestbook
    # Git 仓库 URL
    repoURL: "https://github.com/argoproj/argocd-example-apps"
    # 目标版本：可以是分支名、标签或 commit SHA
    # HEAD 表示跟踪默认分支（通常是 main 或 master）的最新提交
    # 也可以指定具体的分支名（如 "main"）、标签（如 "v1.0.0"）或 commit SHA（如 "abc123"）
    targetRevision: HEAD

    # Helm 配置（如果使用 Helm Chart）
    # helm:
    #   # values 文件路径
    #   valueFiles:
    #     - values.yaml
    #     - values-prod.yaml
    #   # 覆盖 values 参数
    #   parameters:
    #     - name: image.tag
    #       value: "1.0.0"
    #   # 直接指定 values（会覆盖 values 文件）
    #   values: |
    #     replicaCount: 2
    #     image:
    #       tag: "1.0.0"
    #   # Release 名称
    #   releaseName: my-release
    #   # 跳过 CRD 安装
    #   skipCrds: false

    # Kustomize 配置（如果使用 Kustomize）
    # kustomize:
    #   # kustomization.yaml 所在路径
    #   namePrefix: prod-
    #   nameSuffix: -v1
    #   images:
    #     - name: myapp
    #       newTag: v1.0.0
    #   commonLabels:
    #     env: production

    # 目录配置（用于纯 YAML manifests）
    # directory:
    #   recurse: true  # 递归查找子目录
    #   jsonnet: {}    # Jsonnet 配置

  # 所属项目，用于 RBAC 和多租户管理
  project: default

  # 同步策略配置
  syncPolicy:
    # 自动同步配置（null 表示手动同步）
    automated:
      # 自动修剪：删除 Git 中不存在的资源
      prune: true
      # 自动自愈：当资源在集群中被修改时，自动恢复到 Git 状态
      selfHeal: true
      # 允许清空：允许删除所有资源
      allowEmpty: false

    # 同步选项
    syncOptions:
      # 创建命名空间（如果不存在）
      - CreateNamespace=true
      # 验证资源
      - Validate=true
      # 使用 kubectl apply 而不是 kubectl create/patch
      - ApplyOutOfSyncOnly=false
      # PrunePropagationPolicy: 资源删除策略
      - PrunePropagationPolicy=foreground
      # PruneLast: 最后删除资源
      - PruneLast=true
      # Replace: 使用 kubectl replace 而不是 apply（谨慎使用）
      # - Replace=true
      # ServerSideApply: 使用服务端应用
      # - ServerSideApply=true
      # RespectIgnoreDifferences: 尊重忽略差异配置
      - RespectIgnoreDifferences=true

    # 重试策略：同步失败时的重试配置
    retry:
      # 最大重试次数
      limit: 5
      # 退避策略
      backoff:
        # 初始重试间隔
        duration: 5s
        # 最大重试间隔
        maxDuration: 3m
        # 重试间隔增长因子
        factor: 2

  # 忽略差异配置：某些字段在集群中可能被修改，忽略这些差异
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas  # 忽略副本数差异（例如 HPA 修改）
    # - group: "*"
    #   kind: "*"
    #   managedFieldsManagers:
    #     - kube-controller-manager  # 忽略某些管理器的修改

  # 信息配置：在 UI 中显示的额外信息
  info:
    - name: "Owner"
      value: "platform-team"

  # 修订历史限制：保留的历史版本数量
  revisionHistoryLimit: 10

  # 健康评估配置
  # sources: []  # 多源支持（高级功能，用于从多个仓库部署）
~~~

> guestbook这个镜像有问题，在arm64机器上拉下来的镜像，docker inspect里面居然是"Architecture": "amd64"，pod根本跑不起来：exec /usr/local/bin/docker-php-entrypoint: exec format error

# 应用部署示例 --- 基于helm

## 创建AppProject
如果有多个团队，每个团队都要在同一集群内维护大量的应用，就需要用到 Argo CD 的另一个概念：项目（Project）。

Argo CD 中的项目（Project）可以用来对 Application 进行分组，不同的团队使用不同的项目，这样就实现了多租户环境。

项目还支持更细粒度的访问权限控制：
- 限制部署内容（受信任的 Git 仓库）；
- 限制目标部署环境（目标集群和 namespace）；
- 限制部署的资源类型（例如 RBAC、CRD、DaemonSets、NetworkPolicy 等）；
- 定义项目角色，为 Application 提供 RBAC（例如 OIDC group 或者 JWT 令牌绑定）。

比如我们这里创建一个名为 `demo` 的项目，将该应用创建到该项目下，只需创建一个如下所示的 `AppProject` 对象即可：

~~~yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: appprj-demo
  namespace: argocd
  annotations:
    # 同步波次：控制 ArgoCD 同步顺序，数字越小越先执行
    # "1" 表示此项目会在第一波被创建，确保项目在应用之前就绪
    argocd.argoproj.io/sync-wave: "1"

  # 终结器（Finalizer）：防止项目被意外删除
  # 确保在删除项目之前，所有引用此项目的应用都已被删除
  finalizers:
    - resources-finalizer.argocd.argoproj.io

spec:
  description: Demo project for learning ArgoCD features.
  # 说明：定义允许从哪些仓库部署应用清单（manifests），只有列在这里的仓库才能作为 ArgoCD 应用的源
  sourceRepos:
    # 允许从此 Git 仓库拉取应用配置
    - "https://github.com/argoproj/argocd-example-apps"
    # 也可以使用通配符允许所有仓库（生产环境不推荐）
    # - '*'

  # 说明：定义应用可以部署到哪些集群和命名空间
  # 目标集群可以通过 'server'（API Server URL）或 'name'（集群名称）来识别
  destinations:
    # 允许部署到任意命名空间（'*' 表示通配符）
    - namespace: "*"
      # 允许部署到当前集群（ArgoCD 所在的集群）
      server: https://kubernetes.default.svc
    # 也可以使用集群名称代替 server
    # - namespace: "*"
    #   name: in-cluster

  # 说明：定义允许创建哪些集群级别的资源（非命名空间资源）
  # 默认情况下会拒绝所有集群范围资源，除非在此列出
  # 集群资源包括：Namespace、ClusterRole、ClusterRoleBinding、CRD 等
  clusterResourceWhitelist:
    - group: '*'  # 允许所有 API 组的资源
      kind: '*'   # 允许所有资源类型
  # 生产环境建议明确指定允许的资源类型，例如：
  # - group: ''
  #   kind: Namespace
  # - group: 'rbac.authorization.k8s.io'
  #   kind: ClusterRole

  # ============================================================
  # 命名空间范围资源白名单（可选）
  # ============================================================
  # 说明：定义允许在命名空间中创建哪些资源
  # 如果不设置此字段，默认允许所有命名空间资源
  # namespaceResourceWhitelist:
  #   - group: '*'
  #     kind: '*'

  # ============================================================
  # 资源黑名单（可选）
  # ============================================================
  # 说明：明确禁止创建的资源类型，优先级高于白名单
  # namespaceResourceBlacklist:
  #   - group: ''
  #     kind: ResourceQuota
  # clusterResourceBlacklist:
  #   - group: ''
  #     kind: Namespace

  # ============================================================
  # 孤立资源监控
  # ============================================================
  # 说明：启用对命名空间中孤立资源的监控
  # 孤立资源是指存在于集群中但不在 Git 仓库中定义的资源
  # 这有助于发现手动创建或遗留的资源
  orphanedResources:
    warn: true  # 启用警告模式：发现孤立资源时会显示警告，但不会自动删除
    # ignore: []  # 可选：忽略某些孤立资源，不显示警告

  # ============================================================
  # 项目范围集群限制
  # ============================================================
  # 说明：控制应用是否只能部署到此项目范围内的集群
  # false：允许应用部署到 destinations 字段指定的任何集群
  # true：限制应用只能部署到显式绑定到此项目的集群（更严格的安全控制）
  permitOnlyProjectScopedClusters: false

  # ============================================================
  # 角色和权限（可选）
  # ============================================================
  # 说明：定义项目级别的 RBAC 权限，控制谁可以访问此项目
  # roles:
  #   # 定义一个只读角色
  #   - name: read-only
  #     description: Read-only privileges to the demo project
  #     policies:
  #       - p, proj:demo:read-only, applications, get, demo/*, allow
  #     groups:
  #       - demo-viewers
  #   # 定义一个管理员角色
  #   - name: admin
  #     description: Admin privileges to the demo project
  #     policies:
  #       - p, proj:demo:admin, applications, *, demo/*, allow
  #     groups:
  #       - demo-admins

  # ============================================================
  # 同步窗口（可选）
  # ============================================================
  # 说明：定义允许或禁止同步的时间窗口，用于变更管理
  # syncWindows:
  #   # 定义一个允许同步的时间窗口
  #   - kind: allow
  #     schedule: '0 9 * * 1-5'  # Cron 表达式：工作日早上9点
  #     duration: 8h             # 持续8小时
  #     applications:
  #       - '*'                  # 应用于所有应用
  #     manualSync: true         # 允许手动同步
  #   # 定义一个禁止同步的时间窗口（例如：生产环境变更冻结期）
  #   - kind: deny
  #     schedule: '0 0 * * 0,6'  # Cron 表达式：周末
  #     duration: 24h
  #     applications:
  #       - '*'
~~~

更多配置信息可以前往文档 https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/ 查看.

## 创建Application

项目创建完成后，在该项目下创建一个 Application，代表环境中部署的应用程序实例。

~~~yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: gitops-demo
  namespace: argocd
spec:
  destination:
    namespace: default
    server: "https://kubernetes.default.svc"
  project: demo
  syncPolicy:
    automated:
      prune:  # git repo里面删资源，自动在环境中删资源
      selfHeal: true # 强制以 Git Repo 状态为准，手动在环境中修改不会生效
  source:
    path: helm-guestbook # 从 Helm 存储库创建应用程序时，chart 必须指定 path
    repoURL: "https://github.com/argoproj/argocd-example-apps"
    targetRevision: HEAD
    helm:
      parameters:
        - name: replicaCount
          value: "2"
      valueFiles:
        - values.yaml
~~~

# 配置git webhook
由于 Argo CD 默认并不是实时去监测 Config Repo 的变化的，如果要更快的检测到变化我们可以使用 Git Webhook 的方式。默认情况下 Argo CD 每三分钟轮询一次 Git 存储库，以检测清单的更改。为了消除轮询延迟，可以将 API 服务器配置为接收 Webhook 事件。

## 支持的provider
Argo CD 支持来自 GitHub、GitLab、Bitbucket、Bitbucket Server 和 Gogs 的 Git webhook 通知。
然后在 `argocd-secret` 这个 Kubernetes Secret 中，使用上面配置的 Git 提供商的 Webhook 密钥配置以下密钥之一。

| Provider         | k8s 密钥                           |
|------------------|------------------------------------|
| GitHub           | `webhook.github.secret`            |
| GitLab           | `webhook.gitlab.secret`            |
| BitBucket        | `webhook.bitbucket.uuid`           |
| BitBucketServer  | `webhook.bitbucketserver.secret`   |
| Gogs             | `webhook.gogs.secret`              |
| Azure DevOps     | `webhook.azuredevops.username`     |
| Azure DevOps     | `webhook.azuredevops.password`     |
## 添加secret
为了方便输入秘密，Kubernetes 支持在 `stringData` 字段中输入秘密，这样就省去了对值进行 base64 编码并复制到 `data` 字段的麻烦。
只需将步创建的共享 webhook key复制到 `stringData` 字段下相应的 GitHub/GitLab/BitBucket 密钥中即可：

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: argocd-secret
  namespace: argocd
type: Opaque
data:
...
stringData:
  # github webhook secret
  webhook.github.secret: shhhh! it's a GitHub secret
  # gitlab webhook secret
  webhook.gitlab.secret: shhhh! it's a GitLab secret
  # bitbucket webhook secret
  webhook.bitbucket.uuid: your-bitbucket-uuid
  # bitbucket server webhook secret
  webhook.bitbucketserver.secret: shhhh! it's a Bitbucket server secret
  # gogs server webhook secret
  webhook.gogs.secret: shhhh! it's a gogs server secret
  # azuredevops username and password
  webhook.azuredevops.username: admin
  webhook.azuredevops.password: secret-password
~~~

保存后自动生效。
## 基于gitee仓库部署yaml
参考官网教程部署示例： https://argocd.devops.gold/getting_started/

# ApplicationSet
`ApplicationSet` 用于简化多集群应用编排，它可以基于单一应用编排并根据用户的编排内容自动生成一个或多个 `Application`。

核心概念：
- ApplicationSet：ArgoCD 的"应用工厂"，可以根据模板批量创建 Application
- 一个 ApplicationSet 可以生成多个 Application（每个对应一个环境）
- 使用生成器（Generators）自动发现或定义需要部署的应用

~~~yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: appset-guestbook
  labels:
    app: guestbook      # 应用标识
    deployment: helm    # 部署类型：使用 Helm
  annotations:
    # 同步波次：控制 ArgoCD 同步顺序，数字越小越先执行
    # 0 表示默认优先级，业务应用通常使用默认值或正数
    # 基础设施组件使用负数（如 -100）确保优先部署
    argocd.argoproj.io/sync-wave: "0"

spec:
  # ============================================================
  # 模板引擎配置
  # ============================================================
  goTemplate: true  # 启用 Go 模板语法（推荐，功能更强大）
  goTemplateOptions: ["missingkey=error"]  # 严格模式：如果模板变量缺失则报错，避免静默失败

  # ============================================================
  # 生成器配置（Generators）
  # ============================================================
  # 生成器的作用：定义如何生成 Application 列表
  # 每个生成器会产生一组参数，这些参数会被传递给下面的 template
  generators:
    # --------------------------------------------------
    # 列表生成器（List Generator）
    # --------------------------------------------------
    # 作用：手动定义一个静态列表，每个元素代表一个要创建的 Application
    # 适用场景：环境数量固定且不常变化
    - list:
        elements:  # 元素列表：每个元素会生成一个 Application
          # 开发环境
          - cluster: dev           # 集群/环境名称
            url: https://1.2.3.4   # 集群 API Server 地址
            env: development       # 环境标识

          # 预发布环境
          - cluster: staging
            url: https://9.8.7.6
            env: staging

          # 生产环境
          - cluster: prod
            url: https://kubernetes.default.svc  # 使用集群内部地址
            env: production

  # ============================================================
  # 应用模板（Template）
  # ============================================================
  # 这个模板会被应用到生成器产生的每个元素上
  # 例如：上面定义了 3 个环境，会生成 3 个 Application
  template:
    metadata:
      # 应用名称：使用集群名称作为前缀
      # 生成的应用名称示例：
      #   - dev-guestbook
      #   - staging-guestbook
      #   - prod-guestbook
      name: "{{.cluster}}-guestbook"
      labels:
        cluster: "{{.cluster}}"  # 集群标识
        env: "{{.env}}"          # 环境标识
        app: guestbook           # 应用名称

      # 终结器（Finalizer）
      # 作用：确保删除 Application 时会先删除所有部署的资源
      # 防止孤立资源残留在集群中
      finalizers:
        - resources-finalizer.argocd.argoproj.io

    spec:
      # 引用之前定义的 AppProject，继承其权限和限制
      # 确保应用只能访问项目允许的仓库和集群
      project: appprj-demo

      # 定义应用的来源：从哪里获取 Kubernetes 资源定义
      source:
        # Git 仓库 URL
        repoURL: "https://github.com/argoproj/argocd-example-apps"
        # 目标版本：可以是分支名、标签或 commit SHA
        # HEAD 表示跟踪默认分支（通常是 main 或 master）的最新提交
        targetRevision: HEAD
        # Helm Chart 所在路径
        path: helm-guestbook

        # --------------------------------------------------
        # Helm 配置
        # --------------------------------------------------
        helm:
          # Helm Release 名称：指定 Helm 安装时的 release 名称
          # 如果不指定，默认使用 Application 名称
          releaseName: guestbook

          # 值文件（Values Files）加载顺序
          # 后面的文件会覆盖前面的配置
          valueFiles:
            - "values.yaml"         # 1. 默认值文件（所有环境通用）
            - "{{.cluster}}.yaml"   # 2. 环境特定值文件（如 dev.yaml, prod.yaml）
                                    #    如果存在，会覆盖 values.yaml 中的配置

          # 如果指定的 values 文件不存在，不报错
          # 允许某些环境没有特定配置文件
          ignoreMissingValueFiles: true

          # 可选：通过参数直接覆盖 values
          # parameters:
          #   - name: image.tag
          #     value: "{{.version}}"
          #   - name: replicaCount
          #     value: "{{.replicas}}"

          # 可选：直接指定 values（优先级最高）
          # values: |
          #   replicaCount: 3
          #   image:
          #     tag: latest

      # --------------------------------------------------
      # 目标配置（Destination）
      # --------------------------------------------------
      # 定义应用部署到哪个集群的哪个命名空间
      destination:
        # 目标集群的 API Server 地址（从生成器元素中获取）
        server: "{{.url}}"
        # 也可以使用集群名称代替 server
        # name: "{{.cluster}}"

        # 目标命名空间
        namespace: guestbook

      # --------------------------------------------------
      # 同步策略（Sync Policy）
      # --------------------------------------------------
      # 定义如何将 Git 中的配置同步到集群
      syncPolicy:
        # 自动同步配置
        automated:
          # 自动修剪：删除 Git 中不存在的资源
          prune: true
          # 自动自愈：当资源在集群中被修改时，自动恢复到 Git 状态
          selfHeal: true
          # 允许清空：允许删除所有资源
          allowEmpty: false

        # 同步选项
        syncOptions:
          # 创建命名空间（如果不存在）
          - CreateNamespace=true
          # 仅应用不同步的资源：只更新有变化的资源，减少不必要的操作
          - ApplyOutOfSyncOnly=true
          # 验证资源
          - Validate=true
          # 资源删除策略：前台删除（等待依赖资源先删除）
          - PrunePropagationPolicy=foreground

        # 重试策略：同步失败时的重试配置
        retry:
          # 最大重试次数
          limit: 5
          # 退避策略
          backoff:
            # 初始重试间隔
            duration: 5s
            # 最大重试间隔
            maxDuration: 3m
            # 重试间隔增长因子
            factor: 2

      # --------------------------------------------------
      # 忽略差异配置（可选）
      # --------------------------------------------------
      # 某些字段在集群中可能被其他控制器修改，忽略这些差异
      # ignoreDifferences:
      #   - group: apps
      #     kind: Deployment
      #     jsonPointers:
      #       - /spec/replicas  # 忽略副本数差异（例如 HPA 修改）

      # --------------------------------------------------
      # 信息配置（可选）
      # --------------------------------------------------
      # 在 ArgoCD UI 中显示的额外信息
      # info:
      #   - name: "Environment"
      #     value: "{{.env}}"
      #   - name: "Owner"
      #     value: "platform-team"

  # ============================================================
  # 模板补丁（Template Patch）- 可选
  # ============================================================
  # 针对特定应用添加额外配置（条件性补丁）
  # 根据生成器参数的值，为特定环境添加特殊配置
  # templatePatch: |
  #   # 如果是生产环境，添加更严格的配置
  #   {{ if eq .cluster "prod" }}
  #     spec:
  #       # 生产环境禁用自动同步，需要手动审批
  #       syncPolicy:
  #         automated: null
  #       # 忽略某些字段的差异
  #       ignoreDifferences:
  #         - group: apps
  #           kind: Deployment
  #           jsonPointers:
  #             - /spec/replicas
  #   {{- end }}
  #
  #   # 如果是开发环境，允许更激进的自动化
  #   {{ if eq .cluster "dev" }}
  #     spec:
  #       syncPolicy:
  #         automated:
  #           prune: true
  #           selfHeal: true
  #   {{- end }}
~~~

# argocd健康检查机制
部署应用之后，应用虽然已经是 `Synced` 状态，但是 `APP HEALTH` 一直显示为 `Progressing` 状态。

这是因为 ArgoCD 的健康状态机制引起的，我们可以在源码 https://github.com/argoproj/gitops-engine/blob/master/pkg/health/health_ingress.go#L7 中看到健康状态的检查逻辑：
~~~go
func getIngressHealth(obj *unstructured.Unstructured) (*HealthStatus, error) {  
 ingresses, _, _ := unstructured.NestedSlice(obj.Object, "status", "loadBalancer", "ingress")  
 health := HealthStatus{}  
 if len(ingresses) > 0 {  
  health.Status = HealthStatusHealthy  
 } else {  
  health.Status = HealthStatusProgressing  
 }  
 return &health, nil  
}
~~~

他需要检查 Ingress 资源对象的 `status.loadBalancer.ingress` 字段是否为空，如果为空则表示健康状态为 `Progressing`，否则为 `Healthy`。
但并不是所有的 Ingress 资源对象都会自动生成 `status.loadBalancer.ingress` 字段。

这个时候我们可以通过配置 `argocd-cm` 的配置资源来修改健康状态检查逻辑，添加如下所示的配置：

~~~yaml
apiVersion: v1  
kind: ConfigMap  
metadata:  
  name: argocd-cm  
  namespace: argocd  
data:  
  resource.customizations: |  
    networking.k8s.io/Ingress:  
      health.lua: |  
        hs = {}  
        if obj.metadata ~= nil and obj.metadata.creationTimestamp ~= nil then  
          hs.status = "Healthy"  
          hs.message = "Ingress 已创建"  
        else  
          hs.status = "Progressing"  
          hs.message = "Ingress 正在创建中"  
        end  
        return hs
~~~

上面的配置表示如果 Ingress 资源对象的 `metadata.creationTimestamp` 字段不为空，则表示健康状态为 `Healthy`，否则为 `Progressing`，更新上面的配置后，我们再次查看应用的健康状态就会发现已经变成了 `Healthy` 状态。
