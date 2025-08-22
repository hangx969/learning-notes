# Helm介绍

- Helm是kubernetes的包管理工具，相当于linux环境下的yum/apt-get命令。
- Helm可以解决的问题：运维人员写好资源文件模板，交给开发人员填写参数即可
- Helm中的一些概念：
  - helm：命令行客户端工具，主要用于Kubernetes应用中的chart的创建、打包、发布和管理。
  - Chart：helm程序包，一系列用于描述k8s资源相关文件的集合，比方说我们部署nginx，需要deployment、svc的yaml，这两个清单文件就是一个helm程序包，在k8s中把这些yaml清单文件叫做chart图表。
- 功能：
  - 资源管理：helm chart预定义yaml文件，描述各个组件的配置和模板
  - 版本控制：支持一键回滚到先前的版本
  - 依赖管理：声明依赖关系，自动解析并安装这些依赖
  - 模板化：charts可以受用go模板语言，动态生成资源文件


## 官网地址

- 中文：https://v3.helm.sh/zh/docs/

- 英文：https://helm.sh/

- helm 官方的chart站点：https://hub.kubeapps.com/

- helm与k8s的版本支持策略：[Helm | Helm版本支持策略](https://helm.sh/zh/docs/topics/version_skew/)

## 教程文章

- https://mp.weixin.qq.com/s/S_4QK6pLSrmu0PgShOZEjw

## Helm v3版本变化

- 2019年11月13日，Helm团队发布Helm v3的第一个稳定版本。
- 该版本主要变化是架构变化：
  - Helm服务端Tiller被删除（v2版本中，需要装一个Tiller服务端作为通信桥梁才能与k8s交互。v3版不需要了。）

# 安装helm v3.12.3

## 下载安装包

- 下载地址：https://github.com/helm/helm/releases

### Linux安装

~~~sh
# 对于k8s 1.23版本，小于等于3.11.x版本的helm是支持的
wget https://get.helm.sh/helm-v3.16.2-linux-amd64.tar.gz 
tar zxvf helm-v3.16.2-linux-amd64.tar.gz
cp linux-amd64/helm /bin/  #/bin/是默认的环境变量路径之一，所以移动后你可以在任何位置运行这个二进制文件。
# 查看helm版本
helm version
~~~

### Windows安装-基于scoop

#### scoop

Scoop是一款适用于Windows平台的命令行软件（包）管理工具，这里是[Github介绍页](https://link.zhihu.com/?target=https%3A//github.com/ScoopInstaller/Scoop)。简单来说，就是可以通过命令行工具（PowerShell、CMD等）实现软件（包）的安装管理等需求，**通过简单的一行代码实现软件的下载、安装、卸载、更新等操作**。

先安装scoop：[Scoop](https://scoop.sh/)

~~~powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# 更改默认安装目录
$env:SCOOP='D:\0Software\scoop'
[Environment]::SetEnvironmentVariable('SCOOP', $env:SCOOP, 'User')
# 安装
Invoke-Expression (New-Object System.Net.WebClient).DownloadString('https://get.scoop.sh')
~~~

**设置scoop代理：**

- 方法1：`scoop config proxy 127.0.0.1:7078` (根据实际代理端口修改)
- 方法2：修改配置文件：`C:\Users\username\.config\scoop\config.json`，添加`“proxy”: “127.0.0.1:7078”`

**基本使用：**

在实际使用过程中，我们可以先通过`search`命令查询一下是否有相应软件，软件名称是否正确，然后通过`install`命令完成软件的安装。另外，有两个必备的软件需要安装——git和7zip，建议完成Scoop安装后先执行以下命令：`scoop install git 7zip`（Scoop支持多个软件同时依次安装），虽然后续操作中未安装这两个软件时也会提醒用户安装就是了。

- search——搜索仓库中是否有相应软件。
- install——安装软件。
- uninstall——卸载软件。
- update——更新软件。可通过`scoop update *`更新所有已安装软件，或通过`scoop update`更新所有软件仓库资料及Scoop自身而不更新软件。
- hold——锁定软件阻止其更新。
- info——查询软件简要信息。
- home——打开浏览器进入软件官网。

**软件仓库：**

软件仓库是Scoop软件管理的重要基础，通过json文件记录仓库中每一个软件的信息，从而实现软件的管理等便捷命令行操作，并由仓库管理员（其实开源项目都是大家用爱发电）负责软件信息的更新。

前面提到，默认安装Scoop后仅有`main`仓库，其中主要是面向程序员的工具，对于一般用户而言并不是那么实用。好在Scoop本身考虑到了这一点，添加了面向一般用户的软件仓库`extras`，其中收录大量好用的小软件，足够日常的使用。

Scoop添加软件仓库的命令是`scoop bucket add bucketname (+ url可选)`。如添加`extras`的命令是`scoop bucket add extras`，执行此命令后会在scoop文件夹中的buckets子文件夹中添加extras文件夹。

除了官方的软件仓库，Scoop也支持用户自建仓库并共享，于是又有很多大佬提供了许多好用的软件仓库。这里强推[dorado](https://link.zhihu.com/?target=https%3A//github.com/chawyehsu/dorado)仓库，里面有许多适合中国用户的软件，或者你有兴趣可以去看看仓库作者[关于Scoop更多技术方面的探讨](https://link.zhihu.com/?target=https%3A//chawyehsu.com/blog/talk-about-scoop-the-package-manager-for-windows-again)。添加`dorado`仓库的命令如下：`scoop bucket add dorado https://github.com/chawyehsu/dorado`。

#### helm

一行命令安装：`scoop install helm`

# helm仓库类型

## ChartMuseum

- 访问方式：HTTP/HTTPS
- 命令：helm repo add添加仓库，helm install安装应用

## OCI

- 访问方式：OCI规范（helm 3.8之后加进来的，相当于用镜像仓库存储helm chart）

- helm registry去登录仓库，登录完用helm pull可以直接拉chart包，或者helm install安装

  ~~~sh
  helm pull oci://registry-1.docker.io/bitnamicharts/schema-registry
  ~~~

  > 官方仓库：https://artifacthub.io

# helm基本使用

## 添加chart仓库

- 配置国内存放chart仓库的地址:

  - 阿里云仓库（https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts）

  - 官方仓库（https://hub.kubeapps.com/charts/incubator）官方chart仓库，国内可能无法访问。

  - 微软仓库（http://mirror.azure.cn/kubernetes/charts/）这个仓库推荐，基本上官网有的chart这里都有。

~~~sh
#添加阿里云chart仓库，aliyun参数就是要加的仓库所起的别名。根据自己的需要来命名，在你的 Helm 仓库列表中是唯一的就可以。
helm repo add aliyun https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
#添加bitnami的chart仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
#更新chart仓库。更新 Helm chart 仓库的索引。这个索引包含了 Helm chart 仓库中所有包的信息。当你添加新的仓库或者已有的仓库中有新的包发布时，你需要运行这个命令来更新本地的索引，以便 Helm 能够获取到最新的包信息。
helm repo update
#查看配置的chart仓库有哪些
helm repo list
#删除chart仓库地址
helm repo remove aliyun
#从指定仓库搜索chart
helm search repo aliyun
~~~

- chart仓库保存位置

  如果需要转移到另一台机器，复制这个文件即可

  ~~~sh
  cat /root/.config/helm/repositories.yaml 
  ~~~

## 搜索和下载chart

- 查看阿里云chart仓库中的memcached

~~~sh
helm search repo aliyun | grep memcached
helm search repo aliyun/memcached -l # 查看chart所有版本
~~~

- 查看chart信息

~~~sh
helm show chart aliyun/memcached
~~~

- 下载chart包到本地

~~~sh
helm pull aliyun/memcached
tar zxvf memcached-2.0.1.tgz
~~~

- 一键下载helm chart并解压

~~~sh
helm fetch stable/mysql --version 0.2.8 --untar
~~~

## 部署chart

~~~sh
# 指定chart: 
helm install stable/mariadb
# 指定打包的chart: 
helm install ./nginx-1.2.3.tgz
# 指定打包目录: 
helm install ./nginx
# 当前已经在chart目录里面了，直接在当前目录部署helm chart
helm install .
# 指定chart包URL: 
helm install https://example.com/charts/nginx-1.2.3.tgz
~~~

## release管理

~~~sh
# 查看release发布状态
helm list
# 查看release提示信息
helm status memcached
# 查看release历史版本
helm history memcached
# 查看修改了哪些values（仅在使用了--set设置values的情况下才会显示）
helm get values memcached
# 回滚到指定版本
helm rollback memcached 3
# 删除release，会把release对应的资源全部删除
helm uninstall memcached
~~~

## helm管理crds

- crd在helm中的管理过程：https://helm.sh/zh/docs/topics/charts/#%E7%94%A8%E6%88%B7%E8%87%AA%E5%AE%9A%E4%B9%89%E8%B5%84%E6%BA%90crd

- crd不会被升级的说明：https://helm.sh/zh/docs/topics/charts/#crd%E7%9A%84%E9%99%90%E5%88%B6

- crd最佳实践说明：https://helm.sh/docs/chart_best_practices/custom_resource_definitions/#some-caveats-and-explanations

> 不像大部分的Kubernetes对象，CRD是全局安装的。因此Helm管理CRD时会采取非常谨慎的方式。 CRD受到以下限制：
>
> - CRD从不重新安装。如果Helm确定`crds/`目录中的CRD已经存在（忽略版本），Helm不会安装或升级。
> - CRD从不会在升级或回滚时安装。Helm只会在安装时创建CRD。
> - CRD从不会被删除。自动删除CRD会删除集群中所有命名空间中的所有CRD内容。因此Helm不会删除CRD。

## 把k8s资源加入helm管理

- 某项资源是手动创建出来的，现在需要加到某个helm release里面，变成helm去管理，需要给这个资源加上label和annotations：
  - `label： "app.kubernetes.io/managed-by"="Helm"`
  - `annotation： "meta.helm.sh/release-name"="xxxx" "meta.helm.sh/release-namespace"="xxxx"`
- 命令行操作：

~~~sh
kubectl label certificate app01 "app.kubernetes.io/managed-by"="Helm"
kubectl annotate certificate app01 "meta.helm.sh/release-name"="xxx" "meta.helm.sh/release-namespace"="xxx"
~~~

- 脚本批量操作，以更新crd为例：

~~~sh
kubectl get crd --no-headers -o custom-columns=":metadata.name" | grep kyverno | xargs -I {} kubectl annotate crd {} meta.helm.sh/release-name=kyverno
kubectl get crd --no-headers -o custom-columns=":metadata.name" | grep kyverno | xargs -I {} kubectl annotate crd {} meta.helm.sh/release-namespace=kyverno
kubectl get crd --no-headers -o custom-columns=":metadata.name" | grep kyverno | xargs -I {} kubectl label crd {} app.kubernetes.io/managed-by=Helm
~~~

# 自定义chart模板

## helm chart目录结构

~~~sh
#当我们安装好helm之后我们可以开始自定义chart，那么我们需要先创建出一个模板如下：
helm create myapp
cd myapp/
tree ./

├── charts # 用于存放依赖的子chart
├── Chart.yaml # 描述这个 Chart 的相关信息、包括名字、描述信息、版本等
|     apiVersion # Chart的apiVersion，目前默认都是v2
|     name # chart的名称
|     type # Chart的类型，一般都用application
|     version # Chart自己的版本号
|     appVersion # Chart内应用的版本号
|     description # Chart的描述信息
├── templates # 模板目录，保留创建k8s的资源清单文件
│   ├── deployment.yaml # deployment资源的go模板文件
│   ├── _helpers.tpl # 自定义的模板或者函数
│   ├── hpa.yaml 
│   ├── ingress.yaml
│   ├── NOTES.txt # Chart安装完成后输出到控制台的提示信息
│   ├── serviceaccount.yaml
│   ├── service.yaml
│   └── tests # 存放测试文件的目录
│       └── test-connection.yaml
└── values.yaml # 模板的值文件，这些值会在安装时应用到 GO 模板生成部署文件
~~~

## 编写Chart.yaml

> Helm 使用的 Go 模板是 Go 语言的一个内置包，它提供了数据驱动的模板，用于生成可读的输出。这种模板语言被广泛应用于 Go web 框架和生成文本文件。
>
> 在 Helm 中，Go 模板被用于动态生成 Kubernetes 的配置文件。这意味着你可以在模板中使用变量，然后在 Helm 安装 chart 时，根据提供的值文件（values.yaml）或者直接的命令行参数，动态替换这些变量，生成最终的 Kubernetes 配置文件。
>
> 例如，你可以在模板中定义一个变量来表示镜像的版本：
>
> ```yaml
> image: "{{ .Values.image.tag }}"
> ```
>
> 然后在 values.yaml 文件或者 helm 命令行参数中提供这个变量的值：
>
> ```yaml
> image: 
>     tag: "v1.0.0"
> ```
>
> 这样，Helm 在安装 chart 时，会将模板中的 `{{ .Values.image.tag }}` 替换为 "v1.0.0"，生成最终的 Kubernetes 配置文件。

~~~yaml
apiVersion: v2 #Helm Chart的API版本，这里使用的是v2版本。在 v2 版本的 Helm 中，apiVersion 是 v1，而在 v3 版本的 Helm 中，apiVersion 升级为 v2
name: myapp # 指定Chart的名称，这个名称将用于在Helm中引用这个Chart
description: A Helm chart for Kubernetes
version: 0.0.1 # Chart的版本号。每当对Chart和其模板（templates）进行更改时，包括应用版本，都应该递增这个版本号。版本号遵循语义化版本（Semantic Versioning）规范
appVersion: "latest" #镜像标签的版本号
type: application #指定Chart的类型，可以是'application'或'library'。在这个示例中，类型为'application'，意味着这是一个可以部署的应用程序Chart
maintainers:
- name: xxx
  wechat: xxx #自定义联系方式
~~~

## 编写deployment.yaml

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }} #include开头的变量，都是来自于helpers.tpl
  labels:
    {{- include "myapp.labels" . | nindent 4 }} # 首行缩进4字符，用于符合yaml文件格式
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }} 
  #.Values开头的来自于Values.yaml
  # 如果 autoscaling.enabled 参数没有启用，副本数将使用配置文件中 .Values.replicaCount 设置。如果启用了自动扩展，则不会应用这个副本数设置，而是由自动扩展机制根据负载动态调整副本数。
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }} #条件判断，有就去下面抓换，没有就跳过。
      annotations:
        {{- toYaml . | nindent 8 }} # 将 .Values.podAnnotations 参数转换为 YAML 格式，并通过 nindent 8 命令进行缩进。toYaml 是一个 Helm 函数，它将参数转换为 YAML 格式。nindent 8 是一个 Helm 函数，用于对生成的 YAML 进行缩进，使其适应于 YAML 文件中的正确位置。
      {{- end }}
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}" # | 代表默认值的判断，如果values.yaml定义了image.tag就沿用，没定义就用默认的Chart.yaml里面的appversion
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /
              port: http
          readinessProbe:
            httpGet:
              path: /
              port: http
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
~~~

## helpers.hpl

~~~yaml
{{/*
Expand the name of the chart.
*/}} # Helm 模板中的注释标记
{{- define "myapp.name" -}} #使用 define 定义了一个名为 "myapp.name" 的模板函数。它意味着我们正在创建一个可以在其他模板中调用的函数，并且函数名是 "myapp.name"
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }} # 模板函数的结束标记，表示 "myapp.name" 模板函数的定义结束

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
# 使用 if 语句检查是否在 Helm 部署时提供了 .Values.fullnameOverride。如果提供了，将会使用这个值来覆盖生成的应用名称。
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
# 如果生成的名称超过了 63 个字符，这一步会截断名称，确保它不会超过 Kubernetes 资源名称的长度限制。如果名称末尾有 - 符号，则会将其删除
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
#使用 Helm 模板函数的 default 来选择默认值。它会先尝试使用 .Values.nameOverride，如果未定义，则使用 .Chart.Name作为默认值。
{{- if contains $name .Release.Name }} #检查 .Release.Name 是否包含在名称中，如果包含，说明 .Release.Name 已经在名称中，不需要重复添加。
{{- .Release.Name | trunc 63 | trimSuffix "-" }} # 如果 .Release.Name 已经在名称中，就直接使用 .Release.Name 作为完整名称。Release是helm install的时候的实例名称。
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
# 如果 .Release.Name 不包含在名称中，就使用 .Release.Name 和 $name 的组合来生成一个完整的名称，确保不超过 63 个字符
# printf "%s-%s"：这是一个格式化字符串的函数，它将 .Chart.Name和 .Chart.Version连接在一起，中间用 "-" 分隔。
# 注意：release name只有在helm install部署完之后才指定了release name
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "myapp.chart" -}} # 生成 Chart 的名称和版本的组合，作为一个通用的标签。
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }} #将 Chart 的名称和版本用 - 符号连接在一起，并将版本中的 + 替换为 _，
{{- end }}

{{/*
Common labels
*/}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ include "myapp.chart" . }} # 这里直接定义key: value。将之前定义的"myapp.chart"模板函数的结果作为 helm.sh/chart的value。
{{ include "myapp.selectorLabels" . }}
{{- if .Chart.AppVersion }} # 检查 .Chart.AppVersion 是否存在
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }} #如果应用版本存在，这一行生成一个标签，将应用版本作为 app.kubernetes.io/version 标签的value，并使用 quote 函数将值引用起来。这个标签用于表示应用程序的版本。
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "myapp.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
#用条件语句来检查是否应该创建服务账户。这里是根据用户在value中是否设置了 .Values.serviceAccount.create 来判断是否需要创建。
{{- default (include "myapp.fullname" .) .Values.serviceAccount.name }}
# 如果需要创建服务账户，将 .Values.serviceAccount.name 作为服务账户的名称。如果没有提供这个值，将使用默认值 myapp.fullname
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
# 将 .Values.serviceAccount.name 作为服务账户的名称。如果没有提供这个值，将使用默认值 "default"。
{{- end }}
{{- end }}
~~~

## values.yaml

- 比如我们要引用values.yaml文件中的image字段下的tag字段的值
  - 可以在模板文件中写成{{ .Values.image.tag }}；
  - 如果在命令行使用--set选项来应用我们可以写成 image.tag；
- 修改对应的值可以直接编辑对应values.yaml文件中对应字段的值，也可以直接使用--set 指定对应字段的对应值即可；默认情况在命令行使用--set选项给出的值，都会直接被替换；没有给定的值，默认还是使用values.yaml文件中给定的默认值；

~~~yaml
# Default values for myapp.
# This is a YAML-formatted file.
# Declare variables to be passed into your templates.

replicaCount: 1

image:
  repository: nginx
  pullPolicy: IfNotPresent
  # Overrides the image tag whose default is the chart appVersion.
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  # Specifies whether a service account should be created
  create: true
  # Annotations to add to the service account
  annotations: {}
  # The name of the service account to use.
  # If not set and create is true, a name is generated using the fullname template
  name: ""

podAnnotations: {}

podSecurityContext: {}
  # fsGroup: 2000

securityContext: {}
  # capabilities:
  #   drop:
  #   - ALL
  # readOnlyRootFilesystem: true
  # runAsNonRoot: true
  # runAsUser: 1000

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []
  #  - secretName: chart-example-tls
  #    hosts:
  #      - chart-example.local

resources: {}
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  # limits:
  #   cpu: 100m
  #   memory: 128Mi
  # requests:
  #   cpu: 100m
  #   memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80
  # targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}
~~~

## 部署chart

~~~sh
cd ~/myapp/
helm install nginx ./ #Chart.yaml在当前目录下，就用 ./去部署
~~~

# Helm常用命令演示

- 官网地址：[Helm | Helm](https://helm.sh/zh/docs/helm/helm/)

## helm调试命令

### helm template

- 如果想根据Chart导出yaml，可以使用template字段，一键导出所有部署的yaml文件

  ~~~sh
  helm template mamcached . --output-dir yaml # 导出所有
  helm template cert-manager jetstack/cert-manager -n cert-manager -f values.yaml > cert-manager.yaml # 导出单个
  ~~~

### helm diff

- 用于展示helm upgrade将会带来哪些变化：https://github.com/databus23/helm-diff?tab=readme-ov-file

  ~~~sh
  #比较升级会带来哪些变化
  helm diff upgrade <release name> -n <namespace> <source-chart-location> --version $VERSION -f values.yaml --set xxx=$xxx
  #比较两个chart版本的变化
  helm diff revision nginx-chart 1 2
  ~~~

### helm lint

- 用来检查chart格式是否有问题

  ~~~sh
  helm lint mysql
  helm lint /root/myapp/
  
  ==> Linting /root/myapp/
  [INFO] Chart.yaml: icon is recommended
  
  1 chart(s) linted, 0 chart(s) failed
  ~~~

### helm install --dry-run

- 模拟安装到集群中，看看是否会有报错

## 部署chart

~~~sh
#指定chart: 
helm install stable/mariadb
#指定打包的chart: 
helm install ./nginx-1.2.3.tgz
#指定打包目录: 
helm install ./nginx
#指定chart包URL: 
helm install https://example.com/charts/nginx-1.2.3.tgz
~~~

## 调整参数

~~~sh
helm upgrade --set service.type="NodePort" nginx .
~~~

> - 在 Helm 命令中，`.` 表示当前目录。
>
> - 命令 `helm upgrade --set service.type="NodePort" nginx .` 中，`.` 表示 Helm chart 的位置是当前目录。Helm 将在这个目录下查找 `Chart.yaml` 文件以及其他相关的模板文件来部署或升级你的应用。

## 回滚版本

~~~sh
#查看历史版本号
helm history nginx
#简写为hist
helm hist nginx
# 回滚到指定版本号
helm rollback nginx 1
~~~

## 查看部署状态

~~~sh
helm status nginx
~~~

## 打包chart

~~~sh
helm package /root/myapp/
~~~

## 查看chart

~~~sh
#inspect和show互为alias
helm inspect chart ~/myapp/
helm show chart ~/myapp/
~~~

# 可视化管理工具-helm dashboard

- 一款开源helm ui插件：https://github.com/komodorio/helm-dashboard

- 安装插件

  ~~~sh
  helm plugin install https://github.com/komodorio/helm-dashboard.git
  ~~~

- 更新插件

  ~~~sh
  helm plugin update dashboard
  ~~~

- 卸载

  ~~~sh
  helm plugin uninstall dashboard
  ~~~

- 使用插件

  ~~~sh
   设置服务运行绑定 ipv4 ,否则只能本地访问
  export HD_BIND=0.0.0.0
  # 设置 web 端口，默认8080
  export HD_PORT=9000
  
  # 设置1是不打开浏览器，否则默认打开浏览器
  #export HD_NOBROWSER=1
  # 后台运行
  setsid helm dashboard &
  ~~~

> helm安装helm dashboard：https://github.com/komodorio/helm-charts/tree/master/charts/helm-dashboard

# 实战-自定义chart部署flask应用并推送到harbor

## 应用代码

~~~python
#这里使用python基于flask开发一个web服务器，该服务通过读取环境变量 USERNAME 获得用户自己定义的名称，然后监听 80 端口。对于任意 HTTP 请求，返回 Hello ${USERNAME}。比如如果设置USERNAME=world（默认场景），该服务会返回 Hello world。
tee app.py <<'EOF'
from flask import Flask
import os

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    username = os.getenv("USERNAME", "world")
    return f"Hello {username}!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
EOF
~~~

## 构建容器镜像

~~~dockerfile
# 使用官方 Python 基础镜像
FROM python:3.10-slim
# 设置工作目录
WORKDIR /app
# 复制当前目录内容到工作目录
COPY . /app
# 安装依赖
RUN pip install --no-cache-dir Flask -i https://mirrors.aliyun.com/pypi/simple/
# 设置环境变量
ENV USERNAME world
# 暴露应用运行的端口
EXPOSE 80
# 运行 Flask 应用
CMD ["python", "app.py"]
~~~

~~~sh
docker build -t my-hello .
#镜像可以推送到harbor
~~~

## 构建helm chart

~~~sh
helm create my-hello
#这个命令会生成一个名为 my-hello 的目录，里面包含了 Helm Chart 的基本结构。
#需要注意的是，Chart 里面的 my-hello名称需要和生成的 Chart 文件夹名称一致。如果修改 my-hello，则需要做一致的修改。
~~~

- 在根目录下的 Chart.yaml 文件内，声明了当前 Chart 的名称、版本等基本信息，这些信息会在该 Chart 被放入仓库后，供用户浏览检索。

~~~yaml
apiVersion: v2
name: my-hello
description: My hello app Helm chart for Kubernetes      # helm chart描述信息

# A chart can be either an 'application' or a 'library' chart.
#
# Application charts are a collection of templates that can be packaged into versioned archives
# to be deployed.
#
# Library charts provide useful utilities or functions for the chart developer. They're included as
# a dependency of application charts to inject those utilities and functions into the rendering
# pipeline. Library charts do not define any templates and therefore cannot be deployed.
type: application

# This is the chart version. This version number should be incremented each time you make changes
# to the chart and its templates, including the app version.
# Versions are expected to follow Semantic Versioning (https://semver.org/)
version: 1.0   #Chart 的版本

# This is the version number of the application being deployed. This version number should be
# incremented each time you make changes to the application. Versions are not expected to
# follow Semantic Versioning. They should reflect the version the application is using.
# It is recommended to use it with quotes.
appVersion: "1.16.0"   # 应用的版本
~~~

- 编辑values.yaml

~~~yaml
#根目录下有一个values.yaml文件，这个文件提供了应用在安装时的默认参数。编辑 values.yaml 文件，定义 Chart 的默认值：
#这里主要修改values.yaml内的 image.repository,image.tag，并添加Username: helm。其他保持默认。
replicaCount: 1

image:
  repository: harbor.test.com/library/my-hello
  pullPolicy: IfNotPresent
  tag: "v1.0"

service:
  type: ClusterIP
  port: 80
...
Username: helm
~~~

- 编辑模板文件templates/deployment.yaml

~~~sh
#在templates文件夹内存放了应用部署所需要使用的YAML文件，比如Deployment 和 Service。在我当前的应用内，只需要一个 deployment，而有的应用可能包含不同组件，需要多个deployment，就需要在 templates 文件夹下放置不同deployment的YAML文件。
#增加env部分：
...
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            - name: USERNAME
              value: {{ .Values.Username }}
...
~~~

- 编辑 templates/service.yaml

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "my-hello.fullname" . }}
  labels:
    {{- include "my-hello.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "my-hello.selectorLabels" . | nindent 4 }}
~~~

## 打包应用

~~~sh
#使用Helm lint校验Chart有无语法问题。
helm lint
==> Linting .
[ERROR] Chart.yaml: version should be of type string but it's of type float64
[INFO] Chart.yaml: icon is recommended
Error: 1 chart(s) linted, 1 chart(s) failed
# 上面提示，version应该为string，而不是float64。将Chart.yaml中的version字段改为字符串，version: "1.0"。重新校验通过：

helm lint
==> Linting .
[INFO] Chart.yaml: icon is recommended
1 chart(s) linted, 0 chart(s) failed
~~~

~~~sh
#使用helm package对已经创建好的chart应用进行打包，即得到我们厂家的tgz格式的chart包。
helm package ./my-hello/
~~~

## 部署应用

~~~sh
#部署 Chart进行测试使用以下命令部署你创建的 Helm Chart
helm install my-hello my-hello-1.0.tgz
#也可以根据部署后的提示，配置端口转发到宿主机的8080端口进行测试：
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=my-hello,app.kubernetes.io/instance=my-hello" -o jsonpath="{.items[0].metadata.name}")
export CONTAINER_PORT=$(kubectl get pod --namespace default $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
echo "Visit http://127.0.0.1:8080 to use your application"
kubectl --namespace default port-forward $POD_NAME 8080:$CONTAINER_PORT
#此时节点处于监听8080端口状态，任何访问8080端口的流量都会转发到my-hello容器的80端口 ：
#新开终端
curl localhost:8080
~~~

## 参数重载

~~~sh
#应用开发者在 values 配置中只是提供了默认的安装参数，用户也可以在安装时指定自己的配置，通过set参数传递参数。如果应用已经部署，可以用upgrade命令替代install，实现在原有部署好的应用的基础上变更配置。
# 全新安装
helm install my-hello my-hello-1.0.tgz --set Username="K8S"
# 也可以通过配置文件进行传参
helm install my-hello2 my-hello-1.0.tgz -f my-values.yaml
# 升级更新。基于新的value.yaml或者set更新参数
helm upgrade my-hello my-hello-1.0.tgz -f my-new-values.yaml
helm upgrade my-hello my-hello-1.0.tgz --set Username="K8S"
~~~

## 修改提示信息

~~~sh
#修改提示信息部署chart后的提示信息来自templates目录下的NOTES.txt文件：
#根据需要可以自定义输出。
cat my-hello/templates/NOTES.txt
1. Get the application URL by running these commands:
{{- if .Values.ingress.enabled }}
{{- range $host := .Values.ingress.hosts }}
  {{- range .paths }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}{{ .path }}
  {{- end }}
{{- end }}
{{- else if contains "NodePort" .Values.service.type }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "my-hello.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if contains "LoadBalancer" .Values.service.type }}
     NOTE: It may take a few minutes for the LoadBalancer IP to be available.
           You can watch its status by running 'kubectl get --namespace {{ .Release.Namespace }} svc -w {{ include "my-hello.fullname" . }}'
  export SERVICE_IP=$(kubectl get svc --namespace {{ .Release.Namespace }} {{ include "my-hello.fullname" . }} --template "{{"{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}"}}")
  echo http://$SERVICE_IP:{{ .Values.service.port }}
{{- else if contains "ClusterIP" .Values.service.type }}
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "my-hello.name" . }},app.kubernetes.io/instance={{ .Release.Name }}" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace {{ .Release.Namespace }} $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:$CONTAINER_PORT
{{- end }}
~~~

## 清理部署

~~~sh
helm ls
helm uninstall my-hello
~~~
