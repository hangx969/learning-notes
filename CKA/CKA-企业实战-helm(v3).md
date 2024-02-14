# Helm介绍

- Helm是kubernetes的包管理工具，相当于linux环境下的yum/apt-get命令。

- Helm可以解决的问题：运维人员写好资源文件模板，交给开发人员填写参数即可

- Helm中的一些概念：
  - helm：命令行客户端工具，主要用于Kubernetes应用中的chart的创建、打包、发布和管理。
  - Chart：helm程序包，一系列用于描述k8s资源相关文件的集合，比方说我们部署nginx，需要deployment、svc的yaml，这两个清单文件就是一个helm程序包，在k8s中把这些yaml清单文件叫做chart图表。

## 官网地址

- 中文：https://v3.helm.sh/zh/docs/

- 英文：https://helm.sh/

- helm 官方的chart站点：https://hub.kubeapps.com/

- helm与k8s的版本支持策略：[Helm | Helm版本支持策略](https://helm.sh/zh/docs/topics/version_skew/)

## Helm v3版本变化

- 2019年11月13日，Helm团队发布Helmv3的第一个稳定版本。

- 该版本主要变化是架构变化：
  - Helm服务端Tiller被删除（v2版本中，需要装一个Tiller才能与k8s交互。v3版不需要了。）

# 安装helm v3.12.3

## 下载安装包

- 下载地址：https://github.com/helm/helm/releases

~~~sh
#对于k8s 1.23版本，小于等于3.11.x版本的helm是支持的
tar zxvf helm-v3.11.3-linux-amd64.tar.gz
cp linux-amd64/helm /bin/  #/bin/是默认的环境变量路径之一，所以移动后你可以在任何位置运行这个二进制文件。
#查看helm版本
helm version
~~~

## 配置chart仓库

- 配置国内存放chart仓库的地址:

  - 阿里云仓库（https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts）

  - 官方仓库（https://hub.kubeapps.com/charts/incubator）官方chart仓库，国内可能无法访问。

  - 微软仓库（http://mirror.azure.cn/kubernetes/charts/）这个仓库推荐，基本上官网有的chart这里都有，国内可能无法访问。

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

# helm基本使用

## 搜索和下载chart

- 查看阿里云chart仓库中的memcached

~~~sh
helm search repo aliyun | grep memcached
~~~

- 查看chart信息

~~~sh
helm show chart aliyun/memcached
~~~

- 下载chart包到本地

~~~sh
helm pull aliyun/memcached
tar zxvf memcached-2.0.1.tgz
cd memcached
ls
#Chart.yaml: chart的基本信息，包括版本名字之类
#templates: 存放k8s的部署资源模板，通过渲染变量得到部署文件
#values.yaml：存放全局变量，templates下的文件可以调用
~~~

## 部署chart

### 示例-helm部署memcached服务

~~~sh
docker load -i memcache_1_4_36.tar.gz
#如果k8s用的是docker做容器运行时，用docker load -i导出镜像
#如果k8s用的是containerd做容器运行时，用ctr -n=k8s.io images导出镜像
#修改statefulset.yaml文件
cd memcached
rm -f templates/pdb.yaml
cat templates/statefulset.yaml
#apiVersion后面的value值变成apps/v1
#spec下添加selector字段
selector:
  matchLabels:
    app: {{ template "memcached.fullname" . }}
    chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
    release: "{{ .Release.Name }}"
    heritage: "{{ .Release.Service }}"
#删除spec.affinity亲和性配置
#部署
helm install memcached ./
#验证服务可用性
yum install nc -y
#If you'd like to test your instance, forward the port locally:
export POD_NAME=$(kubectl get pods --namespace default -l "app=memcached-memcached" -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward $POD_NAME 11211
#In another tab, attempt to set a key:
echo -e 'set mykey 0 60 5\r\nhello\r' | nc localhost 11211
#You should see:
#STORED
~~~

- statefulset的yaml文件

~~~yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {{ template "memcached.fullname" . }}
  labels:
    app: {{ template "memcached.fullname" . }}
    chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
    release: "{{ .Release.Name }}"
    heritage: "{{ .Release.Service }}"
spec:
  selector:
    matchLabels:
      app: {{ template "memcached.fullname" . }}
      chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
      release: "{{ .Release.Name }}"
      heritage: "{{ .Release.Service }}"
  serviceName: {{ template "memcached.fullname" . }}
  replicas: {{ .Values.replicaCount }}
  template:
    metadata:
      labels:
        app: {{ template "memcached.fullname" . }}
        chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
        release: "{{ .Release.Name }}"
        heritage: "{{ .Release.Service }}"
    spec:
      containers:
      - name: {{ template "memcached.fullname" . }}
        image: {{ .Values.image }}
        imagePullPolicy: {{ default "" .Values.imagePullPolicy | quote }}
        command:
        - memcached
        - -m {{ .Values.memcached.maxItemMemory  }}
        {{- if .Values.memcached.extendedOptions }}
        - -o
        - {{ .Values.memcached.extendedOptions }}
        {{- end }}
        {{- if .Values.memcached.verbosity }}
        - -{{ .Values.memcached.verbosity }}
        {{- end }}
        ports:
        - name: memcache
          containerPort: 11211
        livenessProbe:
          tcpSocket:
            port: memcache
          initialDelaySeconds: 30
          timeoutSeconds: 5
        readinessProbe:
          tcpSocket:
            port: memcache
          initialDelaySeconds: 5
          timeoutSeconds: 1
        resources:
{{ toYaml .Values.resources | indent 10 }}
~~~

> - 这句 Helm 模板代码 `name: {{ template "memcached.fullname" . }}` 是在调用一个名为 "memcached.fullname" 的模板。
>
> - 在 Helm 中，你可以定义自己的模板，并在其他地方调用。这些自定义模板通常定义在 `_helpers.tpl` 文件中。例如，"memcached.fullname" 可能在 `_helpers.tpl` 文件中定义如下：
>
> ```yaml
> {{- define "memcached.fullname" -}}
> {{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
> {{- end -}}
> ```
>
> - 这个模板会生成一个由 Helm 的 release 名称和 chart 名称组成的字符串，然后将其长度截断到 63 个字符，并去除末尾的 "-"。
>
> - 当你在其他地方使用 `{{ template "memcached.fullname" . }}` 时，Helm 会找到这个 "memcached.fullname" 模板，并用当前的上下文（`.`）来渲染它。这样，你就可以在多个地方复用这个模板，而不需要每次都写出完整的逻辑。

## release操作

~~~sh
#查看release发布状态
helm list
#删除release，会把release对应的资源全部删除
helm uninstall memcached
~~~

# 自定义chart模板

## 创建模板

~~~sh
#当我们安装好helm之后我们可以开始自定义chart，那么我们需要先创建出一个模板如下：
helm create myapp
cd myapp/
tree ./

├── charts # 用于存放所依赖的子chart
├── Chart.yaml # 描述这个 Chart 的相关信息、包括名字、描述信息、版本等
├── templates # 模板目录，保留创建k8s的资源清单文件
│   ├── deployment.yaml # deployment资源的go模板文件
│   ├── _helpers.tpl # 模板助手文件，定义的值可在模板中使用
│   ├── hpa.yaml 
│   ├── ingress.yaml
│   ├── NOTES.txt #做补充说明的notes
│   ├── serviceaccount.yaml
│   ├── service.yaml
│   └── tests
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
>   tag: "v1.0.0"
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
- name: xianchao
  wechat: luckylucky421302
~~~

## 编写deployment.yaml

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }} #
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
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
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
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

