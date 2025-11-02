# 介绍
`Argo CD Image Updater` 是一种自动更新由 Argo CD 管理的 k8s 容器镜像的工具。
该工具可以检查与 Kubernetes 工作负载一起部署的容器镜像的新版本，并使用 Argo CD 自动将其更新到允许的最新版本。它通过为 Argo CD 应用程序设置适当的应用程序参数来工作，类似于 `argocd app set --helm-set image.tag=v1.0.1`，但以完全自动化的方式。

Argo CD Image Updater 会定期轮询 Argo CD 中配置的应用程序，并查询相应的镜像仓库以获取可能的新版本。如果在仓库中找到新版本的镜像，并且满足版本约束，Argo CD 镜像更新程序将指示 Argo CD 使用新版本的镜像更新应用程序。

根据您的应用程序自动同步策略，Argo CD 将自动部署新的镜像版本或将应用程序标记为不同步，您可以通过同步应用程序来手动触发镜像更新。

## 工作原理
Image Updater 程序通过读取 ArgoCD 应用程序资源中的 `annotations` 来工作，这些注解指定应自动更新哪些镜像。它会检查指定镜像仓库中是否有较新的标签，如果它们与预定义的模式或规则匹配，则使用这些较新的标签更新应用程序清单。此自动化过程可确保您的应用程序始终运行最新版本的镜像，遵循 GitOps 的一致性和可追溯性原则。

Image Updater 基本的工作流程如下所示：
1. Annotation 配置：开发人员注解 ArgoCD 应用程序以告诉 Image Updater 要跟踪哪些镜像，包括标签过滤和更新策略的规则。
2. 镜像仓库轮询：Image Updater 定期轮询配置的镜像仓库以查找符合指定条件的新标签。
3. 自动更新：当找到新的匹配标签时，Image Updater 会自动更新应用程序的 Kubernetes 清单中的镜像标签，并将更改提交回源 Git 存储库。
4. 同步变更：ArgoCD 检测到提交的更改，同步更新的清单，并将它们应用到 Kubernetes 集群。

特征：
- 更新由 Argo CD 管理且由 Helm 或 Kustomize 工具生成的应用程序镜像
- 根据不同的更新策略更新应用镜像：
	- `semver`：根据给定的镜像约束更新到允许的最高版本
	- `latest`：更新到最近创建的镜像标签
	- `name`：更新到按字母顺序排序的列表中的最后一个标签
	- `digest`：更新到可变标签的最新推送版本
- 支持广泛使用的容器镜像仓库
- 通过配置支持私有容器镜像仓库
- 可以将更改写回 Git
- 能够使用匹配器函数过滤镜像仓库返回的标签列表
- 在 Kubernetes 集群中运行，或者可以从命令行独立使用
- 能够执行应用程序的并行更新

## 限制
另外需要注意的是使用该工具目前有几个限制：
- 想要更新容器镜像的应用程序必须使用 Argo CD 进行管理。不支持未使用 Argo CD 管理的工作负载。
- Argo CD 镜像更新程序只能更新其清单使用 Kustomize 或 Helm 呈现的应用程序的容器镜像，特别是在 Helm 的情况下，模板需要支持使用参数（即`image.tag`）。
- 镜像拉取密钥必须存在于 Argo CD Image Updater 运行（或有权访问）的同一 Kubernetes 集群中。目前无法从其他集群获取这些机密信息。

# 安装
建议在运行 Argo CD 的同一个 Kubernetes 命名空间集群中运行 Argo CD Image Updater：
~~~sh
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
~~~

# 配置镜像库
要充分利用 ArgoCD 镜像更新程序，将其配置连接到镜像仓库至关重要，尤其是在使用私有仓库或公共仓库上的私有存储库时。以下是如何配置必要的凭据并了解可用的不同方法。

## 密钥配置
ArgoCD Image Updater 可以使用以下方法获取凭据：

### docker-registry secret
从 Kubernetes Secret 中获取凭据：标准的 Docker Pull Secret 或自定义 Secret，凭证格式为 `<username>:<password>` ，比如我们可以用下面的命令来创建一个：
~~~sh
kubectl create -n argocd secret docker-registry dockerhub-secret \  
  --docker-username someuser \  
  --docker-password s0m3p4ssw0rd \  
  --docker-server "https://registry-1.docker.io"
~~~
这个 secret 可以被引用为 `pullsecret:<namespace>/<secret_name>` (`pullsecret:argocd/dockerhub-secret`)
### generic secret
通用 Secret 是包含单个键值对的 Secret，键值对可以是任何格式，比如我们可以用下面的命令来创建一个：
~~~sh
kubectl create -n argocd secret generic some-secret \  
  --from-literal=creds=someuser:s0m3p4ssw0rd
~~~
### 环境变量
将凭证存储在环境变量中，该变量可以传递到 ArgoCD Image Updater pod，我们可以在 pod 的配置中设置：
~~~yaml
env:  
  - name: DOCKER_HUB_CREDS  
    value: "someuser:s0m3p4ssw0rd"
~~~
该 secret 可以用 `env:<name_of_environment_variable>` (`env:DOCKER_HUB_CREDS`) 的方式引用。
### Script脚本
使用以 `<username>:<password>` 格式输出凭据的脚本。
~~~bash
#!/bin/sh  
echo "someuser:s0m3p4ssw0rd"
~~~
将其引用为 `ext:<full_path_to_script>`。

# Image Updater与ghcr集成

## 配置ghcr仓库

1. Github个人设置页面中创建PAT，权限要包括 `write:packages` 和 `read:packages`。
2. 终端登录GitHub Container Registry
   ~~~sh
   export PAT=<your-token>
   echo $PAT | docker login ghcr.io -u <your-github-username> --password-stdin
   ~~~

3. 登录成功后我们可以使用以下命令将 Docker 镜像标记为 GitHub Container Registry 镜像：

   ```sh
   docker tag busybox:1.28 ghcr.io/<your-github-username>/busybox:1.28
   ```


4. 然后使用以下命令将 Docker 镜像推送到 GitHub Container Registry 即可：

   ```sh
   docker push ghcr.io/<your-github-username>/busybox:1.28
   ```

5. 完成以上步骤后，就可以在 GitHub 个人账号的 的 `Packages` 部分看到 Docker 镜像了，但是该镜像默认为 private 镜像，Pull 使用时需要先登录。

## Image Updater连接ghcr
1. 创建secret给image updater用：
   ~~~sh
   kubectl create -n argocd secret docker-registry ghcr-secret \
     --docker-username=<github-suer-name> \
     --docker-password=$PAT \
     --docker-server="https://ghcr.io"
   ~~~
2. 设置凭据后，将它们配置在 image updater 的 configMap 中，以通过镜像仓库进行身份验证，我们可以修改镜像更新程序的配置:
   ~~~yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: argocd-image-updater-config
     namespace: argocd
   data:
     registries.conf: |
       registries:
         - name: ghcr-hub
           api_url: https://ghcr.io # 镜像仓库地址
           credentials: pullsecret:argocd/ghcr-secret # 凭据
           defaultns: library # 默认命名空间
           default: true # 默认仓库
   ~~~

   指定了 GitHub 镜像仓库的凭据为 `pullsecret:argocd/ghcr-secret`，这样 ArgoCD Image Updater 在访问 `ghcr.io` 时就会使用这个凭据。

3. 还需要将 ArgoCD Image Updater 与 Git 集成。这样 ArgoCD Image Updater 就可以将镜像更新直接提交回源 Git 仓库。

   - 可以在 ArgoCD 的 Dashboard 中先添加一个 Git 仓库 `https://github.com/hangx969/local-k8s-platform-tools`

   - 输入用户名和PAT

## 创建ApplicationProject

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

## 创建Application

注意：在需要部署应用的namespace中添加Image Pull Secret才能从ghcr下载镜像

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
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: my-channel # 通知配置，当应用状态变化时发送通知
    argocd-image-updater.argoproj.io/image-list: myalias=ghcr.io/hanx969/gitops-demo # 指定镜像仓库  
    argocd-image-updater.argoproj.io/myalias.allow-tags: regexp:^.*$ # 允许所有标签  
    argocd-image-updater.argoproj.io/myalias.pull-secret: pullsecret:argocd/ghcr-secret # 指定凭据  
    argocd-image-updater.argoproj.io/myalias.update-strategy: latest # 指定更新策略  
    # argocd-image-updater.argoproj.io/myalias.ignore-tags: latest, master # 指定忽略的标签  
    argocd-image-updater.argoproj.io/write-back-method: git # 指定写回方法  
    argocd-image-updater.argoproj.io/git-branch: main # 指定 Git 分支  
    argocd-image-updater.argoproj.io/myalias.force-update: "true" # 强制更新
    
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
    path: guestbook-helm
    # Git 仓库 URL
    repoURL: "https://github.com/argoproj/argocd-example-apps"
    # 目标版本：可以是分支名、标签或 commit SHA
    # HEAD 表示跟踪默认分支（通常是 main 或 master）的最新提交
    # 也可以指定具体的分支名（如 "main"）、标签（如 "v1.0.0"）或 commit SHA（如 "abc123"）
    targetRevision: HEAD
    helm:
      # values 文件路径
      valueFiles:
        - values.yaml
        - values-prod.yaml
      # 覆盖 values 参数
      parameters:
        - name: image.tag
          value: "1.0.0"
      # 直接指定 values（会覆盖 values 文件）
      values: |
        replicaCount: 2
        image:
          tag: "1.0.0"
      # Release 名称
      releaseName: my-release
      # 跳过 CRD 安装
      skipCrds: false

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

## 自动更新镜像
接下来我们只需要重新推送一个新的镜像到 GitHub Container Registry 即可自动触发 ArgoCD Image Updater 更新镜像。

推送新的镜像后，然后 `Argo CD Image Updater` 将会每 2 分钟从镜像仓库去检索镜像版本变化，一旦发现有新的镜像版本，它将自动使用新版本来更新集群内工作负载的镜像，并将镜像版本回写到 Git 仓库中去，我们可以去查看 Argo CD Image Updater 的日志变化：`kubectl logs -f argocd-image-updater-57b7-d45 -n argocd`

## 自动Git提交
然后在 Git 仓库中我们也可以看到有一条新的 commit 提交记录，可以看到在回写时，`ArgoCD Image Updater` 并不会直接修改仓库的 `values.yaml` 文件，而是会创建一个专门用于覆盖 Helm Chart `values.yaml` 的 `.argocd-source-devops-demo.yaml` 文件。

另外我们可以注意到每次 Git 提交都与作者的姓名和电子邮件地址相关联。如果未配置，Argo CD 镜像更新程序执行的提交将使用 `argocd-image-updater <noreply@argoproj.io>` 作为作者。您可以使用 `--git-commit-user` 和 `--git-commit-email` 命令行开关覆盖作者，或在 `argocd-image-updater-config ConfigMap` 中设置 `git.user` 和 `git.email` 即可。

同样我们可以将 Argo CD Image Updater 使用的默认提交消息更改为适合你的方式。可以创建一个简单的模板（使用 Golang Template），并通过将 `argocd-image-updater-config` ConfigMap 中的密钥 `git.commit-message-template` 设置为模板的内容来使其可用，例如：

~~~yaml
data:  
  git.commit-message-template: |  
    build: automatic update of {{ .AppName }}  
  
    {{ range .AppChanges -}}  
    updates image {{ .Image }} tag '{{ .OldTag }}' to '{{ .NewTag }}'  
    {{ end -}}
~~~

