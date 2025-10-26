# Tekton介绍

Tekton是一个云原生的CICD解决方案，是CNCF很流行的开源项目之一。Tekton以K8s CRD资源的形式部署在集群上。

Tekton的核心资源包括StepAction、Task、TaskRun、Pipeline、PipelineRun等。可以使用Kubectl直接管理Tekton资源，配置和执行流水线。

核心功能：

1. 云原生：完全基于K8s云原生，不依赖其他组件，所有任务均以容器运行，按需创建和销毁
2. 标准化：所有资源均以CRD定义，符合IaC标准
3. 可移植性：基于标准CRD资源构建，可以一键式跨集群迁移
4. 可扩展性：随集群扩展，无需修改即可增加工作负载
5. 事件驱动：可以接收外部webhook事件触发流水线
6. 社区生态：具备社区和Task Hub，可以用现成的Task

## 核心资源

- StepAction: 最小的工作单元。定义可以复用的工作单元的资源，一般用于定义具体的执行步骤，比如构建、扫描等。可以被task调用
- Task: 用于定义一系列有序的步骤，每个步骤用于调用特定的工具处理特定的任务，可以指定具体的命令，也可以绑定StepActions
- Tekton Pipeline: 集成多个Task，按顺序执行。
- Tekton Triggers: Tekton事件触发组件，可以用于接收外部系统的事件，之后进行流水线的执行
- Tekton CLI: Tekton提供的客户端工具，可以使用tkn与Tekton交互。（推荐kubectl来管理，不用这个）
- Tekton Dashboard: Tekton提供的基于Web的图形界面
- TaskRun: 用于实例化特定任务(Task)，相当于真正执行Task
- PipelineRun: 用于实例化特定流水线(Pipeline)，相当于执行Pipeline中定义的任务

## 工作模式

- 先定义好Pipeline，集成了多个Task：Task A --> Task B | Task C --> Task D

- 再创建TaskRun实例化Pipeline

这样定义的原因是：Pipeline是一个通用模板，里面不定义真实的命令；PipelineRun中传入实际的参数。

## 最佳实践

1. 推荐把Task作为最小单元就行了，不要再定义StepAction作为最小单元了，因为一层一层参数传递实在是太麻烦了。
2. 推荐一个Task就定义一个Step就行了。
3. workspace都写一个名字就行了免得搞混 

# 部署Tekton

- Tekton官网：https://tekton.dev/

要部署三个组件：

1. Tekton Pipeline：https://tekton.dev/docs/installation/pipelines/
2. Tekton Triggers：https://tekton.dev/docs/installation/triggers/#installation
3. Tekton Dashboard：https://tekton.dev/docs/dashboard/install/#installing-tekton-dashboard-on-kubernetes

## Pipeline部署

~~~sh
kubectl apply --filename https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
~~~

如果镜像拉不下来：

- 源文件里面的镜像是带sha256的：`ghcr.io/tektoncd/pipeline/resolversff86b24f130c42b88983d3c13993056d:v1.5.0@sha256:a17d58d4f7f6fcf2e7c88cfd867ff4001ebf7be68b0e2e0be2f354d706568c25`

- 这样必须是新鲜现拉的镜像才行，去下一个`ghcr.io/tektoncd/pipeline/resolversff86b24f130c42b88983d3c13993056d:v1.5.0`镜像，sha256和他要求的不一样，不能用。

- 所以要去下载下来源文件，去里面改掉镜像地址后面的sha256后缀：

~~~sh
curl -o tekton-pipeline.yaml https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml
~~~

## Dashboard部署

~~~sh
kubectl apply --filename https://storage.googleapis.com/tekton-releases/dashboard/latest/release.yaml
~~~

部署完成之后，去把dashboard的svc改成NodePort来访问

## 测试Task和TaskRun

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: hello 
spec: 
  steps: 
    - name: echo 
      image: registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.9-tomcat 
      script: | 
        #!/bin/sh 
        echo "Hello World"   
~~~

~~~yaml
apiVersion: tekton.dev/v1 
kind: TaskRun 
metadata: 
  name: hello-task-run # taskrun name 
spec: 
  taskRef: 
    name: hello # task name
~~~

taskrun创建之后，tekton会自动创建一个pod去运行task。这个pod有：

- 两个init container，是tekton自动注入的
- 一个main container是task指定的镜像

## 测试Pipeline

Task：可以定义参数，脚本里面引用参数

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: goodbye 
spec: 
  params: # 可以接收taskRun和pipeline的参数 
  - name: username 
    type: string 
  steps: 
    - name: goodbye 
      image: registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.9-tomcat 
      script: | 
        #!/bin/sh 
        echo "Goodbye $(params.username)!" 
~~~

TaskRun：引用task，可以传task定义的参数进去

~~~yaml
apiVersion: tekton.dev/v1 
kind: TaskRun 
metadata: 
  name: goodbye-task-run # taskrun name 
spec: 
  taskRef: 
    name: goodbye # task name 
  params: 
  - name: username 
    value: "demo"
~~~

Pipeline：定义模板，定义参数给pipelinerun用；同时可以传参数给调用的task

~~~yaml
apiVersion: tekton.dev/v1 
kind: Pipeline 
metadata: 
  name: hello-goodbye 
spec: 
  params: # 也可以接收pipelineRun的参数 
  - name: username 
    type: string 
  tasks: 
    - name: hello 
      taskRef: 
        name: hello 
    - name: goodbye 
      runAfter: # 在上个task结束之后运行 
        - hello 
      taskRef: 
        name: goodbye 
      params: # 传递参数 
      - name: username 
        value: $(params.username) # 参数来自spec.params下面的参数，也就是pipelineRun传递的参数 
~~~

PipelineRun：

~~~yaml
apiVersion: tekton.dev/v1 
kind: PipelineRun 
metadata: 
  name: hello-goodbye-run 
spec: 
  pipelineRef: 
    name: hello-goodbye 
  params: # 传递参数 
  - name: username 
    value: "Tekton"
~~~

# 常用task

Tekton 官方提供了很多开箱即用的Task，可以在 https://hub.tekton.dev/ 中获取。

## 拉代码Task

~~~sh
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.6/git-clone.yaml
# github地址：https://github.com/tektoncd/catalog/blob/main/task/git-clone/0.6/git-clone.yaml
~~~

### 下载模板

也可以先下载下来：

~~~yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: git-clone
  labels:
    app.kubernetes.io/version: "0.6"
  annotations:
    tekton.dev/pipelines.minVersion: "0.29.0"
    tekton.dev/categories: Git
    tekton.dev/tags: git
    tekton.dev/displayName: "git clone"
    tekton.dev/platforms: "linux/amd64,linux/s390x,linux/ppc64le,linux/arm64"
    tekton.dev/deprecated: "true"
spec:
  description: >-
    These Tasks are Git tasks to work with repositories used by other tasks
    in your Pipeline.

    The git-clone Task will clone a repo from the provided url into the
    output Workspace. By default the repo will be cloned into the root of
    your Workspace. You can clone into a subdirectory by setting this Task's
    subdirectory param. This Task also supports sparse checkouts. To perform
    a sparse checkout, pass a list of comma separated directory patterns to
    this Task's sparseCheckoutDirectories param.
  workspaces:
    - name: output
      description: The git repo will be cloned onto the volume backing this Workspace.
    - name: ssh-directory
      optional: true
      description: |
        A .ssh directory with private key, known_hosts, config, etc. Copied to
        the user's home before git commands are executed. Used to authenticate
        with the git remote when performing the clone. Binding a Secret to this
        Workspace is strongly recommended over other volume types.
    - name: basic-auth
      optional: true
      description: |
        A Workspace containing a .gitconfig and .git-credentials file. These
        will be copied to the user's home before any git commands are run. Any
        other files in this Workspace are ignored. It is strongly recommended
        to use ssh-directory over basic-auth whenever possible and to bind a
        Secret to this Workspace over other volume types.
    - name: ssl-ca-directory
      optional: true
      description: |
        A workspace containing CA certificates, this will be used by Git to
        verify the peer with when fetching or pushing over HTTPS.
  params:
    - name: url
      description: Repository URL to clone from.
      type: string
    - name: revision
      description: Revision to checkout. (branch, tag, sha, ref, etc...)
      type: string
      default: ""
    - name: refspec
      description: Refspec to fetch before checking out revision.
      default: ""
    - name: submodules
      description: Initialize and fetch git submodules.
      type: string
      default: "true"
    - name: depth
      description: Perform a shallow clone, fetching only the most recent N commits.
      type: string
      default: "1"
    - name: sslVerify
      description: Set the `http.sslVerify` global git config. Setting this to `false` is not advised unless you are sure that you trust your git remote.
      type: string
      default: "true"
    - name: subdirectory
      description: Subdirectory inside the `output` Workspace to clone the repo into.
      type: string
      default: ""
    - name: sparseCheckoutDirectories
      description: Define the directory patterns to match or exclude when performing a sparse checkout.
      type: string
      default: ""
    - name: deleteExisting
      description: Clean out the contents of the destination directory if it already exists before cloning.
      type: string
      default: "true"
    - name: httpProxy
      description: HTTP proxy server for non-SSL requests.
      type: string
      default: ""
    - name: httpsProxy
      description: HTTPS proxy server for SSL requests.
      type: string
      default: ""
    - name: noProxy
      description: Opt out of proxying HTTP/HTTPS requests.
      type: string
      default: ""
    - name: verbose
      description: Log the commands that are executed during `git-clone`'s operation.
      type: string
      default: "true"
    - name: gitInitImage
      description: The image providing the git-init binary that this Task runs.
      type: string
      default: "ghcr.io/tektoncd/github.com/tektoncd/pipeline/cmd/git-init:v0.29.0"
    - name: userHome
      description: |
        Absolute path to the user's home directory. Set this explicitly if you are running the image as a non-root user or have overridden
        the gitInitImage param with an image containing custom user configuration.
      type: string
      default: "/tekton/home"
  results:
    - name: commit
      description: The precise commit SHA that was fetched by this Task.
    - name: url
      description: The precise URL that was fetched by this Task.
  steps:
    - name: clone
      image: "$(params.gitInitImage)"
      env:
      - name: HOME
        value: "$(params.userHome)"
      - name: PARAM_URL
        value: $(params.url)
      - name: PARAM_REVISION
        value: $(params.revision)
      - name: PARAM_REFSPEC
        value: $(params.refspec)
      - name: PARAM_SUBMODULES
        value: $(params.submodules)
      - name: PARAM_DEPTH
        value: $(params.depth)
      - name: PARAM_SSL_VERIFY
        value: $(params.sslVerify)
      - name: PARAM_SUBDIRECTORY
        value: $(params.subdirectory)
      - name: PARAM_DELETE_EXISTING
        value: $(params.deleteExisting)
      - name: PARAM_HTTP_PROXY
        value: $(params.httpProxy)
      - name: PARAM_HTTPS_PROXY
        value: $(params.httpsProxy)
      - name: PARAM_NO_PROXY
        value: $(params.noProxy)
      - name: PARAM_VERBOSE
        value: $(params.verbose)
      - name: PARAM_SPARSE_CHECKOUT_DIRECTORIES
        value: $(params.sparseCheckoutDirectories)
      - name: PARAM_USER_HOME
        value: $(params.userHome)
      - name: WORKSPACE_OUTPUT_PATH
        value: $(workspaces.output.path)
      - name: WORKSPACE_SSH_DIRECTORY_BOUND
        value: $(workspaces.ssh-directory.bound)
      - name: WORKSPACE_SSH_DIRECTORY_PATH
        value: $(workspaces.ssh-directory.path)
      - name: WORKSPACE_BASIC_AUTH_DIRECTORY_BOUND
        value: $(workspaces.basic-auth.bound)
      - name: WORKSPACE_BASIC_AUTH_DIRECTORY_PATH
        value: $(workspaces.basic-auth.path)
      - name: WORKSPACE_SSL_CA_DIRECTORY_BOUND
        value: $(workspaces.ssl-ca-directory.bound)
      - name: WORKSPACE_SSL_CA_DIRECTORY_PATH
        value: $(workspaces.ssl-ca-directory.path)
      script: |
        #!/usr/bin/env sh
        set -eu

        if [ "${PARAM_VERBOSE}" = "true" ] ; then
          set -x
        fi


        if [ "${WORKSPACE_BASIC_AUTH_DIRECTORY_BOUND}" = "true" ] ; then
          cp "${WORKSPACE_BASIC_AUTH_DIRECTORY_PATH}/.git-credentials" "${PARAM_USER_HOME}/.git-credentials"
          cp "${WORKSPACE_BASIC_AUTH_DIRECTORY_PATH}/.gitconfig" "${PARAM_USER_HOME}/.gitconfig"
          chmod 400 "${PARAM_USER_HOME}/.git-credentials"
          chmod 400 "${PARAM_USER_HOME}/.gitconfig"
        fi

        if [ "${WORKSPACE_SSH_DIRECTORY_BOUND}" = "true" ] ; then
          cp -R "${WORKSPACE_SSH_DIRECTORY_PATH}" "${PARAM_USER_HOME}"/.ssh
          chmod 700 "${PARAM_USER_HOME}"/.ssh
          chmod -R 400 "${PARAM_USER_HOME}"/.ssh/*
        fi

        if [ "${WORKSPACE_SSL_CA_DIRECTORY_BOUND}" = "true" ] ; then
           export GIT_SSL_CAPATH="${WORKSPACE_SSL_CA_DIRECTORY_PATH}"
        fi
        CHECKOUT_DIR="${WORKSPACE_OUTPUT_PATH}/${PARAM_SUBDIRECTORY}"

        cleandir() {
          # Delete any existing contents of the repo directory if it exists.
          #
          # We don't just "rm -rf ${CHECKOUT_DIR}" because ${CHECKOUT_DIR} might be "/"
          # or the root of a mounted volume.
          if [ -d "${CHECKOUT_DIR}" ] ; then
            # Delete non-hidden files and directories
            rm -rf "${CHECKOUT_DIR:?}"/*
            # Delete files and directories starting with . but excluding ..
            rm -rf "${CHECKOUT_DIR}"/.[!.]*
            # Delete files and directories starting with .. plus any other character
            rm -rf "${CHECKOUT_DIR}"/..?*
          fi
        }

        if [ "${PARAM_DELETE_EXISTING}" = "true" ] ; then
          cleandir
        fi

        test -z "${PARAM_HTTP_PROXY}" || export HTTP_PROXY="${PARAM_HTTP_PROXY}"
        test -z "${PARAM_HTTPS_PROXY}" || export HTTPS_PROXY="${PARAM_HTTPS_PROXY}"
        test -z "${PARAM_NO_PROXY}" || export NO_PROXY="${PARAM_NO_PROXY}"

        /ko-app/git-init \
          -url="${PARAM_URL}" \
          -revision="${PARAM_REVISION}" \
          -refspec="${PARAM_REFSPEC}" \
          -path="${CHECKOUT_DIR}" \
          -sslVerify="${PARAM_SSL_VERIFY}" \
          -submodules="${PARAM_SUBMODULES}" \
          -depth="${PARAM_DEPTH}" \
          -sparseCheckoutDirectories="${PARAM_SPARSE_CHECKOUT_DIRECTORIES}"
        cd "${CHECKOUT_DIR}"
        RESULT_SHA="$(git rev-parse HEAD)"
        EXIT_CODE="$?"
        if [ "${EXIT_CODE}" != 0 ] ; then
          exit "${EXIT_CODE}"
        fi
        printf "%s" "${RESULT_SHA}" > "$(results.commit.path)"
        printf "%s" "${PARAM_URL}" > "$(results.url.path)"
~~~

### 关注的参数

该Task需要关注的参数:

- url: 仓库的url
- revision：需要拉取的branch或者tag
- gitinitimage：；默认是gcr.io的，可以换成自己的

需要关注的workspace：

~~~yaml
  workspaces:
    - name: output # 代码拉下来存的位置
      description: The git repo will be cloned onto the volume backing this Workspace.
    - name: ssh-directory # 如果拉私有仓库代码，需要ssh密钥。（或者下面的 basic-auth，ssl-ca）
      optional: true
      description: |
        A .ssh directory with private key, known_hosts, config, etc. Copied to
        the user's home before git commands are executed. Used to authenticate
        with the git remote when performing the clone. Binding a Secret to this
        Workspace is strongly recommended over other volume types.
    - name: basic-auth 
      optional: true
      description: |
        A Workspace containing a .gitconfig and .git-credentials file. These
        will be copied to the user's home before any git commands are run. Any
        other files in this Workspace are ignored. It is strongly recommended
        to use ssh-directory over basic-auth whenever possible and to bind a
        Secret to this Workspace over other volume types.
    - name: ssl-ca-directory
      optional: true
      description: |
        A workspace containing CA certificates, this will be used by Git to
        verify the peer with when fetching or pushing over HTTPS.
~~~

注意版本问题：

git-clone task的版本和对应的pipelines.minVersion版本（即git-init镜像版本）是有依赖的。

- 对于0.6版本的git-clone，要用至少0.29的git-init镜像
- 对于0.10版本的git-clone，要用至少0.38的git-init镜像

版本太低会有bug

~~~yaml
  labels:
    app.kubernetes.io/version: "0.6"
  annotations:
    tekton.dev/pipelines.minVersion: "0.29.0"
    
  labels:
    app.kubernetes.io/version: "0.10"
  annotations:
    tekton.dev/pipelines.minVersion: "0.38.0"
~~~

### 创建workspace PVC

首先需要用到的 workspace 是 output，下载的代码会保存在该 workspace。接下来给 tekton 创建一个专用的用来存储代码及工作目录的PVC：
~~~yaml
apiVersion: v1 
kind: PersistentVolumeClaim 
metadata: 
  name: tekton-workspace 
  namespace: default 
spec: 
  resources: 
    requests: 
      storage: 1Gi 
  volumeMode: Filesystem 
  storageClassName: cfs-sc
  accessModes: 
  - ReadWriteMany
~~~

### 拉取公有仓库代码

直接创建一个TaskRun运行Task：

~~~yaml
apiVersion: tekton.dev/v1 
kind: TaskRun 
metadata: 
  name: git-clone-run # taskrun name 
spec: 
  workspaces: 
  - name: output # 要和模板里面的workspace name一致
    persistentVolumeClaim: 
      claimName: tekton-workspace 
  taskRef: 
    name: git-clone # task name 
  params: 
  - name: url
    value: "https://gitee.com/dukuan/krm.git" 
  - name: gitInitImage
    value: "registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0" 
  - name: revision
    value: main
~~~

### 拉取私有仓库代码

1. 需要配置ssh私钥并挂载到task里面。在master节点上，如果没有ssh key，先创建一个：

~~~sh
ssh-keygen -t ed25519 -C "1003665363@qq.com"
# ed25519 是一种现代的椭圆曲线加密算法，比传统的 RSA 算法更安全、更快、密钥更短
~~~

2. 查看公钥：

~~~sh
cat ~/.ssh/id_ed25519
~~~

比如是从gitlab拉代码，那就把公钥放到gitlab上。

3. 创建Secret保存私钥：

~~~sh
kubectl create secret generic git-ssh-auth --from-file=id_ed25519=/root/.ssh/id_ed25519 --dry-run=client -o yaml > git-secret.yaml
~~~

4. 在secret中添加一段config配置：

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: git-ssh-auth
data:
  config: U3RyaWN0SG9zdEtleUNoZWNraW5nIG5vIApVc2VyS25vd25Ib3N0c0ZpbGUgL2Rldi9udWxsCg==
  id_ed25519: LS0t
~~~

是base64编码过的，解码之后是：

- **`StrictHostKeyChecking no`**:
  - 关闭严格的主机密钥检查
  - SSH 连接时不会提示 "Are you sure you want to continue connecting (yes/no)?"
  - 自动接受未知主机的密钥
- **`UserKnownHostsFile /dev/null`**:
  - 将已知主机文件重定向到 `/dev/null`(黑洞)
  - 不保存主机密钥到 `~/.ssh/known_hosts` 文件
  - 每次连接都当作新主机处理

5. 创建taskrun，拉取私有仓库代码：

~~~yaml
apiVersion: tekton.dev/v1 
kind: TaskRun 
metadata: 
  name: git-clone-private-run # taskrun name 
spec: 
  workspaces: 
  - name: output 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
  - name: ssh-directory  
    secret: 
      secretName: git-ssh-auth
  taskRef: 
    name: git-clone # task name 
  params: 
  - name: url 
    value: "git@192.168.40.183:local-k8s-platform-tools/spring-boot-project.git" 
  - name: gitInitImage 
    value: "registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0" # 注意这里的image版本必须符合task版本要求的最低版本。达不到的话就注释掉，用默认的git-init镜像
  - name: revision 
    value: master
~~~

### 自定义工作目录

上述定义了工作目录PVC，但是拉取代码时，全部下载到了同一个目录。此时多个任务同时处理时会产生冲突。后来拉的代码会覆盖掉当前目录中的内容。

所以不同服务或者不同任务的工作目录应该独立。此时可以在TaskRun的PVC中指定subPath：

~~~yaml
apiVersion: tekton.dev/v1 
kind: TaskRun 
metadata: 
  name: git-clone-run-subpath # taskrun name 
spec: 
  workspaces: 
  - name: output 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    subPath: "git-clone-run-subpath" 
  taskRef: 
    name: git-clone # task name 
  params: 
  - name: url 
    value: "https://gitee.com/dukuan/krm.git" 
  - name: gitInitImage 
    value: "registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0" 
  - name: revision 
    value: main 
~~~

指定subPath后，代码会下载到PVC的git-clone-run-subpath目录。

除了上述手动指定工作目录，也可以使用Tekton的内置变量自动配置subPath。比如使用 PipelineRun和TaskRun的名字作为子目录。

所有可用的变量可以在https://tekton.dev/docs/pipelines/variables/#variables-available-in-a-pipeline中获取。

## 初始化Task

下载代码后，可能需要进行一些初始化操作，比如获取Commit信息、生成镜像的TAG等。

此时可以单独创建一个用来初始化的Task：

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: init 
spec: 
  description: "生成初始化信息" 
  # 定义一个workspace，后续需要把拉取代码的工作目录挂载到该workspace 
  workspaces: 
  - name: source 
  steps: 
  - name: read 
    image: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0 
    # 指定当前task的工作目录为workspace的路径  
    workingDir: $(workspaces.source.path) 
    script: |  
      #!/usr/bin/env sh 
      ls 
      ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; echo "Asia/Shanghai" > /etc/timezone 
      CUR_DATE=`TZ='Asia/Shanghai' date '+%Y%m%d-%H%M%S'` 
      # 获取本次提交的Commit信息 
      COMMIT_MESSAGE=`git log -1 --pretty=format:'%h : %an  %s'` 
      CUR_DATE=`date '+%Y%m%d-%H%M%S'` 
      SHORT_COMMIT=`git log -n 1 --pretty=format:'%h'` 
      TAG=`echo "${CUR_DATE}-${SHORT_COMMIT}"` 
      echo $TAG 
~~~

创建taskrun运行一下：

~~~yaml
apiVersion: tekton.dev/v1 
kind: TaskRun 
metadata: 
  name: init-taskrun # taskrun name 
spec: 
  workspaces: 
  - name: source 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    subPath: "git-clone-run-subpath" 
  taskRef: 
    name: init # task name 
~~~

### 结果存储Results

有时候在一个task执行某个操作后，需要记录一下结果，然后根据这个结果去判定是否应该继续执行；或者要使用这个结果去执行其它的动作。

比如根据上个task生成的tag进行镜像的构建，此时由初始化生成的tag需要传递到构建镜像的task，这个需求可以使用results去实现。

Results一般用于存储各个过程产生的临时数据，比如由初始化task产生的数据，可以保留 在results中，其他task可以通过results获取数据。

接下来修改初始化Task，添加results，把tag结果保存： 

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: init 
spec: 
  description: "生成初始化信息" 
  # 定义一个workspace，后续需要把拉取代码的工作目录挂载到该workspace 
  workspaces: 
  - name: source 
  results: 
  - name: tag 
    description: result for tag 
  steps: 
  - name: read 
    image: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0 
    # 指定当前task的工作目录为workspace的路径。workspace会在taskrun的时候指定
    workingDir: $(workspaces.source.path) 
    script: |  
      #!/usr/bin/env sh 
      ls 
      # 获取本次提交的Commit信息 
      COMMIT_MESSAGE=`git log -1 --pretty=format:'%h : %an  %s'` 
      CUR_DATE=`date '+%Y%m%d-%H%M%S'` 
      SHORT_COMMIT=`git log -n 1 --pretty=format:'%h'` 
      TAG=`echo "${CUR_DATE}-${SHORT_COMMIT}"` 
      echo $TAG 
      # 把TAG的值，写入到results中 
      # tag是结果的变量名，可以自定义 
      # results和path是固定格式 
      echo $TAG | tee $(results.tag.path) 
~~~

保存之后的results，就能在pipeline中使用如下方式获取：

~~~yaml
 params: 
      - name: tag 
        # tasks固定写法，init为产生result的task名字，tag是result名字 
        value: $(tasks.init.results.tag)
~~~

### 串联多任务Pipeline

接下来创建一个Pipeline，结合上述测试的task，进行联合工作。并且使用results传递数据。

先创建一个额外的task，用来接收tag参数并展示：

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: show-tag 
spec: 
  description: Read and display TAG. 
  # 通过params获取pipeline传递过来的results值 
  params: 
    - name: tag 
  steps: 
  - name: read
    image: registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.9-tomcat 
    script: |  
      #!/usr/bin/env sh 
      echo $(params.tag)
~~~

创建Pipeline，把各个Task串在一起：

~~~yaml
apiVersion: tekton.dev/v1 
kind: Pipeline 
metadata: 
  name: git-init-show  
spec: 
  description: |  
    下载代码，初始化并存储数据. 
  # 以下为pipeline可以接收的参数，使用pipelineRun可以进行传参 
  params: 
  - name: url # 用于接收代码地址 
    type: string 
    description: The git repo URL to clone from. 
  - name: gitInitImage 
    type: string 
    # 配置一个默认值后续Run的时候就不需要再次传递 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0  
  # 定义pipeline的workspace 
  workspaces: 
  - name: share-data # 配置一个workspace保留共享数据 
    description: |  
      This workspace contains the cloned repo files, so they can be read by the next task. 
  # 拉取代码ssh配置 
  - name: ssh-directory 
    description: My ssh credentials 
  # 定义该pipeline指定的task 
  tasks: 
  - name: fetch-source
    taskRef: 
      name: git-clone
    workspaces: # 把pipeline的share-data workspace挂载到git-clone的output的workspace 
    - name: output # 这里是task定义的workspace名字
      workspace: share-data # 这里是pipeline自己声明的workspace，传进去
    - name: ssh-directory 
      workspace: ssh-directory # 把pipeline接收到的ssh-directory传递给task的ssh-directory
    # 传递给task的参数 
    params:
    - name: url 
      value: $(params.url) # 从pipeline的params获取参数并传递 
    - name: gitInitImage 
      value: $(params.gitInitImage) 
  - name: init 
    # 等代码拉取task结束后执行初始化 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: init 
    workspaces: 
    - name: source # init task定义的workspace name就叫source
      workspace: share-data 
  - name: show-tag 
    # 等待init结束获取tag的值 
    runAfter: ["init"] 
    taskRef: 
      name: show-tag 
    params: 
    - name: tag 
    # 通过$(tasks.生产result的task的名字.results.result名字)获取result结果 
      value: $(tasks.init.results.tag) 
~~~

### PipelineRun

创建PipelineRun运行Pipeline：

~~~yaml
apiVersion: tekton.dev/v1beta1 
kind: PipelineRun 
metadata: 
  # 自动生成名字 
  generateName: clone-and-init- 
spec: 
  pipelineRef: 
    name: git-init-show 
  # 定义workspace 
  workspaces: 
  # 把K8s的PVC挂载到shared-data workspace 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 使用当前pipelineRun的名字作为子目录 
    subPath: $(context.pipelineRun.name) 
  # 把K8s的secret挂载到git-credentials workspace 
  - name: ssh-directory 
    secret: 
      secretName: git-ssh-auth 
  # 传递参数给pipeline 
  params: 
  - name: url 
    value: git@192.168.40.183:local-k8s-platform-tools/spring-boot-project.git  
  - name: revision 
    value: "master"
~~~

## 代码构建Task

### Task

上述任务已经实现了代码下载、初始化和数据传递的功能，接下来再添加代码构建的Task。

需要注意构建任务针对不同的语言需要的环境和命令是不同的，所以该Task需要从参数获取构建命令和构建的基础镜像： 

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: build 
spec: 
  description: Code Build 
  workspaces: 
  - name: source 
  params: # 参数也可以大写 
  - name: BUILD_COMMAND 
  - name: BUILD_IMAGE 
  steps: 
  - name: build 
    image: $(params.BUILD_IMAGE)  
    workingDir: $(workspaces.source.path) 
    script: |  
      #!/usr/bin/env sh 
      pwd 
      ls 
      echo $(params.BUILD_COMMAND) 
      $(params.BUILD_COMMAND) 
~~~

### Pipeline

基于之前的pipeline，把添加build task加进去：

~~~yaml
apiVersion: tekton.dev/v1 
kind: Pipeline 
metadata: 
  name: git-init-build  
spec: 
  description: |  
    下载代码，初始化并存储数据. 
  # 以下为pipeline可以接收的参数，使用pipelineRun可以进行传参 
  params: 
  - name: url # 用于接收代码地址 
    type: string 
    description: The git repo URL to clone from. 
  - name: gitInitImage 
    type: string 
    # 配置一个默认值后续Run的时候就不需要再次传递 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0  
  - name: BUILD_IMAGE 
    type: string 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.9-tomcat 
  - name: BUILD_COMMAND
    type: string 
    default: ls 
  # 定义workspace 
  workspaces: 
  - name: share-data # 配置一个workspace保留共享数据 
    description: |  
      This workspace contains the cloned repo files, so they can be read by the next task. 
  # 拉取代码ssh配置 
  - name: ssh-directory 
    description: My ssh credentials 
  # 定义改pipeline指定的task 
  tasks: 
  - name: fetch-source 
    taskRef: 
      name: git-clone 
    workspaces: 
    - name: output 
      workspace: share-data 
    # 把接收到的ssh-directory传递给task的ssh-directory 
    - name: ssh-directory 
      workspace: ssh-directory 
    # 传递给task 的参数 
    params: 
    - name: url 
      value: $(params.url) # 从pipeline的params获取参数并传递 
    - name: gitInitImage 
      value: $(params.gitInitImage) 
  - name: init 
    # 等代码拉取task结束后执行初始化 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: init 
    workspaces: 
    - name: source 
      workspace: share-data 
  - name: build # 代码下载后即可开始编译 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: build 
    workspaces: 
    - name: source 
      workspace: share-data 
    params: 
    - name: BUILD_COMMAND 
      value: $(params.BUILD_COMMAND) 
    - name: BUILD_IMAGE 
      value: $(params.BUILD_IMAGE)
~~~

### PipelineRun

创建pipelinerun运行pipeline：

~~~yaml
apiVersion: tekton.dev/v1 
kind: PipelineRun 
metadata: 
  # 自动生成名字，注意创建的时候要用kubectl create -f
  generateName: clone-and-init-build-
spec: 
  pipelineRef: 
    name: git-init-build 
  # 定义workspace 
  workspaces: 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 使用pipelineRun的名字作为子目录 
    subPath: $(context.pipelineRun.name) 
  # 把K8s的secret挂载到git-credentials workspace 
  - name: ssh-directory 
    secret: 
      secretName: git-ssh-auth 
  # 传递参数给pipeline 
  params: 
  - name: url 
    value: git@gitee.com:dukuan/vue-project.git  
  - name: revision 
    value: "master" 
  - name: BUILD_IMAGE 
    value: registry.cn-beijing.aliyuncs.com/dotbalo/node:16.17.0-apline-cnpm 
  - name: BUILD_COMMAND 
    value: |- 
       cnpm install 
       npm run build  
       ls 
       ls dist
~~~

## 镜像构建Task

上述已经执行了代码构建，并且生成了产物，接下来可以创建一个Kaniko的Task，用于构建镜像和上传镜像，同时记录镜像地址。

### Task

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: kaniko  
spec: 
  description: >- 
    This Task builds a simple Dockerfile with kaniko and pushes to a registry. 
    This Task stores the image name and digest as results, allowing Tekton Chains to pick up that an image was built & sign it. 
  params: 
    - name: IMAGE_URL 
      type: string 
    - name: DOCKERFILE 
      description: Path to the Dockerfile to build. 
      default: ./Dockerfile 
    - name: CONTEXT 
      description: The build context used by Kaniko. 
      default: ./ 
    - name: EXTRA_ARGS 
      type: array 
      default: [] 
    - name: BUILDER_IMAGE 
      description: The image on which builds will run (default latest) 
      default: registry.cn-beijing.aliyuncs.com/dotbalo/executor:v1.22.0  
  workspaces: 
    - name: source 
      description: Holds the context and Dockerfile 
    # 挂载docker的配置文件，用于访问镜像仓库 
    - name: docker-credentials  
      description: Includes a docker `config.json` 
      optional: true 
      mountPath: /kaniko/.docker 
  results: 
    - name: IMAGE_URL 
      description: URL of the image just built. 
  steps: 
    - name: build-and-push 
      workingDir: $(workspaces.source.path) 
      image: registry.cn-beijing.aliyuncs.com/dotbalo/kaniko-executor:debug  
      script: | 
        executor -c . --insecure --skip-tls-verify -d $(params.IMAGE_URL) 
      securityContext: 
        runAsUser: 0 
    - name: write-url 
      image: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.1  
      script: | 
        set -e 
        image="$(params.IMAGE_URL)" 
        echo -n "${image}" | tee "$(results.IMAGE_URL.path)"
~~~

### 私有仓库认证

如果推送镜像到私有仓库，需要添加docker认证信息。Kaniko连接harbor用的配置文件就是docker连接harbor的配置文件。

1. 在有docker客户端的机器上，配置docker连接harbor：

   ~~~sh
   # 配置docker daemon.json
   tee /etc/docker/daemon.json <<'EOF'
   {
    "registry-mirrors":["https://x6j7eqtq.mirror.aliyuncs.com","https://docker.lmirror.top","https://docker.m.daocloud.io", "https://hub.uuuadc.top","https://docker.anyhub.us.kg","https://dockerhub.jobcher.com","https://dockerhub.icu","https://docker.ckyl.me","https://docker.awsl9527.cn","https://docker.laoex.link"],
   "insecure-registries":["harbor.hanxux.local","192.168.40.180:32002"] 
   } 
   EOF
   
   systemctl daemon-reload && systemctl restart docker.service
   ~~~

2. 用docker登录一次harbor，生成一个登录harbor的配置文件：

   ~~~sh
   docker login 192.168.40.180:32002
   # admin/Harbor12345
   ~~~

3. 查看生成的配置文件：

   ~~~sh
   cat ~/.docker/config.json
   ~~~

4. 创建secret

   ~~~sh
   kubectl create secret generic docker-credentials --from-file=/root/.docker/config.json 
   ~~~

### Pipeline

~~~yaml
apiVersion: tekton.dev/v1 
kind: Pipeline 
metadata: 
  name: git-init-build-kaniko  
spec: 
  description: |  
    下载代码，初始化并存储数据. 
  # 以下为pipeline可以接收的参数，使用pipelineRun可以进行传参 
  params: 
  - name: url # 用于接收代码地址 
    type: string 
    description: The git repo URL to clone from. 
  - name: revision 
    type: string 
  - name: gitInitImage 
    type: string 
    # 配置一个默认值后续Run的时候就不需要再次传递 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0  
  - name: BUILD_IMAGE 
    type: string 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.9-tomcat 
  - name: BUILD_COMMAND 
    type: string 
    default: ls 
  # 添加用于镜像的参数 
  - name: DOCKERFILE 
    type: string 
    default: ./Dockerfile 
  - name: REGISTRY 
    type: string 
  - name: REPOSTORY 
    type: string 
  - name: IMAGE_NAME 
    type: string 
  # 定义workspace 
  workspaces: 
  - name: share-data # 配置一个workspace保留共享数据 
    description: |  
      This workspace contains the cloned repo files, so they can be read by the next task. 
  # 拉取代码ssh配置 
  - name: ssh-directory 
    description: My ssh credentials 
  # 添加docker认证 
  - name: docker-credentials 
    description: docker credentials 
  # 定义改pipeline指定的task 
  tasks: 
  - name: fetch-source 
    taskRef: 
      name: git-clone 
    workspaces: 
    - name: output 
      workspace: share-data 
    # 把接收到的ssh-directory传递给task的ssh-directory 
    - name: ssh-directory 
      workspace: ssh-directory 
    # 传递给task 的参数 
    params: 
    - name: url 
      value: $(params.url) # 从pipeline的params获取参数并传递 
    - name: gitInitImage 
      value: $(params.gitInitImage) 
    - name: revision 
      value: $(params.revision) 
  - name: init 
    # 等代码拉取task结束后执行初始化 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: init 
    workspaces: 
    - name: source 
      workspace: share-data 
  - name: build 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: build 
    workspaces: 
    - name: source 
      workspace: share-data 
    params: 
    - name: BUILD_COMMAND 
      value: $(params.BUILD_COMMAND) 
    - name: BUILD_IMAGE 
      value: $(params.BUILD_IMAGE) 
  # 添加kaniko task 
  - name: kaniko 
    runAfter: ["build"] 
    taskRef: 
      name: kaniko  
    workspaces: 
    - name: source 
      workspace: share-data 
    - name: docker-credentials 
      workspace: docker-credentials 
    params: 
    - name: IMAGE_URL 
      value: $(params.REGISTRY)/$(params.REPOSTORY)/$(params.IMAGE_NAME):$(tasks.init.results.tag) 
~~~

### PipelineRun

~~~yaml
apiVersion: tekton.dev/v1 
kind: PipelineRun 
metadata: 
  # 自动生成名字 
  generateName: build-push- 
spec: 
  pipelineRef: 
    name: git-init-build-kaniko 
  # 定义workspace 
  workspaces: 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 使用pipelineRun的名字作为子目录 
    subPath: $(context.pipelineRun.name) 
  # 把K8s的secret挂载到git-credentials workspace 
  - name: ssh-directory 
    secret: 
      secretName: git-ssh-auth 
  - name: docker-credentials 
    secret: 
      secretName: docker-credentials 
  # 传递参数给pipeline 
  params: 
  - name: url 
    value: "git@192.168.40.183:local-k8s-platform-tools/vue-project.git"   
  - name: revision 
    value: "tekton" 
  - name: BUILD_IMAGE 
    value: registry.cn-beijing.aliyuncs.com/dotbalo/node:16.17.0-apline-cnpm 
  - name: BUILD_COMMAND 
    value: |- 
       cnpm install 
       npm run build  
       ls 
       ls dist 
  - name: REGISTRY 
    value: 192.168.40.180:32002
  - name: REPOSTORY 
    value: platform-tools-local 
  - name: IMAGE_NAME 
    value: vue-project-tekton
~~~

## 服务发版Task

最后就可以通过一个发版的Task，把最新的镜像发布到Kubernetes。 

### Task

这里示例是kubectl发版，如果有其他发版方式比如helm等，那就创建多个task对应不同发版方式

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: deploy 
spec: 
  description: deploy to kubernetes by kubectl 
  workspaces: 
  - name: kubeconfig 
    mountPath: /mnt/kubeconfig 
  params: 
    - name: IMAGE_URL 
      type: string 
    - name: NAMESPACE 
      type: string 
      default: default 
    - name: DEPLOY_NAME 
      type: string 
    - name: CONTAINER_NAME 
      type: string 
    - name: KUBECONFIG_PATH 
      type: string 
  steps: 
  - name: deploy 
    image: registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest
    script: |  
      pwd 
      ls /mnt/kubeconfig 
      echo "Deploy version: $(params.IMAGE_URL)" 
      echo "kubectl --kubeconfig /mnt/kubeconfig/$(params.KUBECONFIG_PATH) -n $(params.NAMESPACE) set image deploy $(params.DEPLOY_NAME) $(params.CONTAINER_NAME)=$(params.IMAGE_URL)" 
      kubectl --kubeconfig /mnt/kubeconfig/$(params.KUBECONFIG_PATH) -n $(params.NAMESPACE) set image deploy $(params.DEPLOY_NAME) $(params.CONTAINER_NAME)=$(params.IMAGE_URL) 
      kubectl --kubeconfig /mnt/kubeconfig/$(params.KUBECONFIG_PATH) -n $(params.NAMESPACE) get po 
~~~

### 挂载kubeconfig

~~~sh
kubectl create secret generic kubeconfig --from-file=study-kubeconfig=/root/.kube/config  
~~~

### 创建deployment

创建一个承接镜像用的deployment，后面Pipeline会覆盖掉当前镜像为业务镜像：

~~~sh
kubectl create deploy vue-project --image=registry.cn-beijing.aliyuncs.com/dotbalo/vue-project:20250824-040945-e929446 
~~~

### Pipeline

~~~yaml
apiVersion: tekton.dev/v1 
kind: Pipeline 
metadata: 
  name: deploy
spec: 
  description: |  
    下载代码，初始化并存储数据. 
  # 以下为pipeline可以接收的参数，使用pipelineRun可以进行传参 
  params: 
  - name: url # 用于接收代码地址 
    type: string 
    description: The git repo URL to clone from. 
  - name: revision 
    type: string 
  - name: gitInitImage 
    type: string 
    # 配置一个默认值后续Run的时候就不需要再次传递 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0  
  - name: BUILD_IMAGE 
    type: string 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.9-tomcat 
  - name: BUILD_COMMAND 
    type: string 
    default: ls 
  # 添加用于镜像的参数 
  - name: DOCKERFILE 
    type: string 
    default: ./Dockerfile 
  - name: REGISTRY 
    type: string 
  - name: REPOSTORY 
    type: string 
  - name: IMAGE_NAME 
    type: string 
  - name: NAMESPACE 
    type: string 
    default: default 
  - name: DEPLOY_NAME 
    type: string 
  - name: CONTAINER_NAME 
    type: string 
  - name: KUBECONFIG_PATH 
    type: string 
  # 定义workspace 
  workspaces: 
  - name: share-data # 配置一个workspace保留共享数据 
    description: |  
      This workspace contains the cloned repo files, so they can be read by the next task. 
  # 拉取代码ssh配置 
  - name: ssh-directory 
    description: My ssh credentials 
  # 添加docker认证 
  - name: docker-credentials 
    description: docker credentials 
  - name: kubeconfig 
    description: kubernetes kubeconfig 
  # 定义pipeline指定的task 
  tasks: 
  - name: fetch-source 
    taskRef: 
      name: git-clone 
    workspaces: 
    - name: output 
      workspace: share-data 
    # 把接收到的ssh-directory传递给task的ssh-directory 
    - name: ssh-directory 
      workspace: ssh-directory 
    # 传递给task 的参数 
    params: 
    - name: url 
      value: $(params.url) # 从pipeline的params获取参数并传递 
    - name: gitInitImage 
      value: $(params.gitInitImage) 
    - name: revision 
      value: $(params.revision) 
  - name: init 
    # 等代码拉取task结束后执行初始化 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: init 
    workspaces: 
    - name: source 
      workspace: share-data 
  - name: build 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: build 
    workspaces: 
    - name: source 
      workspace: share-data 
    params: 
    - name: BUILD_COMMAND 
      value: $(params.BUILD_COMMAND) 
    - name: BUILD_IMAGE 
      value: $(params.BUILD_IMAGE) 
  # 添加kaniko task 
  - name: kaniko 
    runAfter: ["build"] 
    taskRef: 
     name: kaniko  
    workspaces: 
    - name: source 
      workspace: share-data 
    - name: docker-credentials 
      workspace: docker-credentials 
    params: 
    - name: IMAGE_URL 
      value: $(params.REGISTRY)/$(params.REPOSTORY)/$(params.IMAGE_NAME):$(tasks.init.results.tag) 
  # 添加deploy task 
  - name: deploy 
    runAfter: ["build"] 
    taskRef: 
      name: deploy 
    workspaces: 
    - name: kubeconfig 
      workspace: kubeconfig 
    params: 
    - name: IMAGE_URL 
      value: $(params.REGISTRY)/$(params.REPOSTORY)/$(params.IMAGE_NAME):$(tasks.init.results.tag) 
    - name: NAMESPACE 
      value: $(params.NAMESPACE) 
    - name: DEPLOY_NAME 
      value: $(params.DEPLOY_NAME) 
    - name: CONTAINER_NAME 
      value: $(params.CONTAINER_NAME) 
    - name: KUBECONFIG_PATH 
      value: $(params.KUBECONFIG_PATH)
~~~

### PipelineRun

~~~yaml
apiVersion: tekton.dev/v1 
kind: PipelineRun 
metadata: 
  # 自动生成名字 
  generateName: deploy- 
spec: 
  pipelineRef: 
    name: deploy 
  # 定义workspace 
  workspaces: 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 使用pipelineRun的名字作为子目录 
    subPath: $(context.pipelineRun.name) 
  # 把K8s的secret挂载到git-credentials workspace 
  - name: ssh-directory 
    secret: 
      secretName: git-ssh-auth 
  - name: docker-credentials 
    secret: 
      secretName: docker-credentials 
  - name: kubeconfig 
    secret: 
      secretName: kubeconfig 
  # 传递参数给pipeline 
  params: 
  - name: url 
    value: "git@192.168.40.183:local-k8s-platform-tools/vue-project.git"
  - name: revision 
    value: "tekton" # branch名称
  - name: BUILD_IMAGE 
    value: registry.cn-beijing.aliyuncs.com/dotbalo/node:16.17.0-apline-cnpm
  - name: BUILD_COMMAND 
    value: |- 
      cnpm install 
      npm run build  
      ls 
      ls dist 
  - name: REGISTRY # harbor地址
    value: 192.168.40.180:32002
  - name: REPOSTORY 
    value: platform-tools-local 
  - name: IMAGE_NAME 
    value: vue-project-tekton
  - name: NAMESPACE 
    value: default 
  - name: DEPLOY_NAME 
    value: vue-project 
  - name: CONTAINER_NAME 
    value: vue-project 
  - name: KUBECONFIG_PATH 
    value: study-kubeconfig 
~~~

# Tekton企业落地实战

## tekton必备资源

### 代码拉取secret

1. 需要配置ssh私钥并挂载到task里面。在master节点上，如果没有ssh key，先创建一个：

~~~sh
ssh-keygen -t ed25519 -C "1003665363@qq.com"
# ed25519 是一种现代的椭圆曲线加密算法，比传统的 RSA 算法更安全、更快、密钥更短
~~~

2. 查看公钥：

~~~sh
cat ~/.ssh/id_ed25519
~~~

比如是从gitlab拉代码，那就把公钥放到gitlab上。

3. 创建Secret保存私钥：

~~~sh
kubectl create secret generic git-ssh-auth --from-file=id_ed25519=/root/.ssh/id_ed25519 --dry-run=client -o yaml > git-secret.yaml
~~~

4. 在secret中添加一段config配置：

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: git-ssh-auth
data:
  config: U3RyaWN0SG9zdEtleUNoZWNraW5nIG5vIApVc2VyS25vd25Ib3N0c0ZpbGUgL2Rldi9udWxsCg==
  id_ed25519: LS0t
~~~

是base64编码过的，解码之后是：

- **`StrictHostKeyChecking no`**:
  - 关闭严格的主机密钥检查
  - SSH 连接时不会提示 "Are you sure you want to continue connecting (yes/no)?"
  - 自动接受未知主机的密钥
- **`UserKnownHostsFile /dev/null`**:
  - 将已知主机文件重定向到 `/dev/null`(黑洞)
  - 不保存主机密钥到 `~/.ssh/known_hosts` 文件
  - 每次连接都当作新主机处理

### 镜像仓库secret

如果推送镜像到私有仓库，需要添加docker认证信息。Kaniko连接harbor用的配置文件就是docker连接harbor的配置文件。

1. 在有docker客户端的机器上，配置docker连接harbor：

   ~~~sh
   # 配置docker daemon.json
   tee /etc/docker/daemon.json <<'EOF'
   {
    "registry-mirrors":["https://x6j7eqtq.mirror.aliyuncs.com","https://docker.lmirror.top","https://docker.m.daocloud.io", "https://hub.uuuadc.top","https://docker.anyhub.us.kg","https://dockerhub.jobcher.com","https://dockerhub.icu","https://docker.ckyl.me","https://docker.awsl9527.cn","https://docker.laoex.link"],
   "insecure-registries":["harbor.hanxux.local","192.168.40.180:32002"] 
   } 
   EOF
   
   systemctl daemon-reload && systemctl restart docker.service
   ~~~

2. 用docker登录一次harbor，生成一个登录harbor的配置文件：

   ~~~sh
   docker login 192.168.40.180:32002
   # admin/Harbor12345
   ~~~

3. 查看生成的配置文件：

   ~~~sh
   cat ~/.docker/config.json
   ~~~

4. 创建secret

   ~~~sh
   kubectl create secret generic docker-credentials --from-file=/root/.docker/config.json 
   ~~~

### k8s集群secret

~~~sh
kubectl create secret generic kubeconfig --from-file=study-kubeconfig=/root/.kube/config  
~~~

这些secret：

- 在task里面指定workspace挂载路径，在task里面的shell命令里面使用对应路径的文件
- 在pipelinerun里面指定workspace的实体（secret、PVC等）

### 代码存放workspace

首先需要用到的 workspace 是 output，下载的代码会保存在该 workspace。接下来给 tekton 创建一个专用的用来存储代码及工作目录的PVC：

~~~yaml
apiVersion: v1 
kind: PersistentVolumeClaim 
metadata: 
  name: tekton-workspace 
  namespace: default 
spec: 
  resources: 
    requests: 
      storage: 1Gi 
  volumeMode: Filesystem 
  storageClassName: cfs-sc
  accessModes: 
  - ReadWriteMany
~~~

pipelinerun中绑定workspace和PVC：

~~~yaml
  workspaces: 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 使用pipelineRun的名字作为子目录 
    subPath: $(context.pipelineRun.name) 
~~~

### 缓存workspace

用作构建缓存的PVC：

~~~yaml
apiVersion: v1 
kind: PersistentVolumeClaim 
metadata: 
  name: tekton-cache  
  namespace: default 
spec: 
  resources: 
    requests: 
      storage: 100Gi 
  volumeMode: Filesystem 
  storageClassName: nfs-csi 
  accessModes: 
    - ReadWriteMany 
~~~

后面是作为volume挂载到task里面。这个值不能写死，做成params，传参数进去。

## tekton必备Task

### git-clone

github地址：https://github.com/tektoncd/catalog/blob/main/task/git-clone/0.6/git-clone.yaml

注意git-clone版本，保证git-init镜像的版本符合最低要求。

~~~yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: git-clone
  labels:
    app.kubernetes.io/version: "0.6"
  annotations:
    tekton.dev/pipelines.minVersion: "0.29.0"
    tekton.dev/categories: Git
    tekton.dev/tags: git
    tekton.dev/displayName: "git clone"
    tekton.dev/platforms: "linux/amd64,linux/s390x,linux/ppc64le,linux/arm64"
    tekton.dev/deprecated: "true"
spec:
  description: >-
    These Tasks are Git tasks to work with repositories used by other tasks
    in your Pipeline.

    The git-clone Task will clone a repo from the provided url into the
    output Workspace. By default the repo will be cloned into the root of
    your Workspace. You can clone into a subdirectory by setting this Task's
    subdirectory param. This Task also supports sparse checkouts. To perform
    a sparse checkout, pass a list of comma separated directory patterns to
    this Task's sparseCheckoutDirectories param.
  workspaces:
    - name: output
      description: The git repo will be cloned onto the volume backing this Workspace.
    - name: ssh-directory
      optional: true
      description: |
        A .ssh directory with private key, known_hosts, config, etc. Copied to
        the user's home before git commands are executed. Used to authenticate
        with the git remote when performing the clone. Binding a Secret to this
        Workspace is strongly recommended over other volume types.
    - name: basic-auth
      optional: true
      description: |
        A Workspace containing a .gitconfig and .git-credentials file. These
        will be copied to the user's home before any git commands are run. Any
        other files in this Workspace are ignored. It is strongly recommended
        to use ssh-directory over basic-auth whenever possible and to bind a
        Secret to this Workspace over other volume types.
    - name: ssl-ca-directory
      optional: true
      description: |
        A workspace containing CA certificates, this will be used by Git to
        verify the peer with when fetching or pushing over HTTPS.
  params:
    - name: url
      description: Repository URL to clone from.
      type: string
    - name: revision
      description: Revision to checkout. (branch, tag, sha, ref, etc...)
      type: string
      default: ""
    - name: refspec
      description: Refspec to fetch before checking out revision.
      default: ""
    - name: submodules
      description: Initialize and fetch git submodules.
      type: string
      default: "true"
    - name: depth
      description: Perform a shallow clone, fetching only the most recent N commits.
      type: string
      default: "1"
    - name: sslVerify
      description: Set the `http.sslVerify` global git config. Setting this to `false` is not advised unless you are sure that you trust your git remote.
      type: string
      default: "true"
    - name: subdirectory
      description: Subdirectory inside the `output` Workspace to clone the repo into.
      type: string
      default: ""
    - name: sparseCheckoutDirectories
      description: Define the directory patterns to match or exclude when performing a sparse checkout.
      type: string
      default: ""
    - name: deleteExisting
      description: Clean out the contents of the destination directory if it already exists before cloning.
      type: string
      default: "true"
    - name: httpProxy
      description: HTTP proxy server for non-SSL requests.
      type: string
      default: ""
    - name: httpsProxy
      description: HTTPS proxy server for SSL requests.
      type: string
      default: ""
    - name: noProxy
      description: Opt out of proxying HTTP/HTTPS requests.
      type: string
      default: ""
    - name: verbose
      description: Log the commands that are executed during `git-clone`'s operation.
      type: string
      default: "true"
    - name: gitInitImage
      description: The image providing the git-init binary that this Task runs.
      type: string
      default: "ghcr.io/tektoncd/github.com/tektoncd/pipeline/cmd/git-init:v0.29.0"
    - name: userHome
      description: |
        Absolute path to the user's home directory. Set this explicitly if you are running the image as a non-root user or have overridden
        the gitInitImage param with an image containing custom user configuration.
      type: string
      default: "/tekton/home"
  results:
    - name: commit
      description: The precise commit SHA that was fetched by this Task.
    - name: url
      description: The precise URL that was fetched by this Task.
  steps:
    - name: clone
      image: "$(params.gitInitImage)"
      env:
      - name: HOME
        value: "$(params.userHome)"
      - name: PARAM_URL
        value: $(params.url)
      - name: PARAM_REVISION
        value: $(params.revision)
      - name: PARAM_REFSPEC
        value: $(params.refspec)
      - name: PARAM_SUBMODULES
        value: $(params.submodules)
      - name: PARAM_DEPTH
        value: $(params.depth)
      - name: PARAM_SSL_VERIFY
        value: $(params.sslVerify)
      - name: PARAM_SUBDIRECTORY
        value: $(params.subdirectory)
      - name: PARAM_DELETE_EXISTING
        value: $(params.deleteExisting)
      - name: PARAM_HTTP_PROXY
        value: $(params.httpProxy)
      - name: PARAM_HTTPS_PROXY
        value: $(params.httpsProxy)
      - name: PARAM_NO_PROXY
        value: $(params.noProxy)
      - name: PARAM_VERBOSE
        value: $(params.verbose)
      - name: PARAM_SPARSE_CHECKOUT_DIRECTORIES
        value: $(params.sparseCheckoutDirectories)
      - name: PARAM_USER_HOME
        value: $(params.userHome)
      - name: WORKSPACE_OUTPUT_PATH
        value: $(workspaces.output.path)
      - name: WORKSPACE_SSH_DIRECTORY_BOUND
        value: $(workspaces.ssh-directory.bound)
      - name: WORKSPACE_SSH_DIRECTORY_PATH
        value: $(workspaces.ssh-directory.path)
      - name: WORKSPACE_BASIC_AUTH_DIRECTORY_BOUND
        value: $(workspaces.basic-auth.bound)
      - name: WORKSPACE_BASIC_AUTH_DIRECTORY_PATH
        value: $(workspaces.basic-auth.path)
      - name: WORKSPACE_SSL_CA_DIRECTORY_BOUND
        value: $(workspaces.ssl-ca-directory.bound)
      - name: WORKSPACE_SSL_CA_DIRECTORY_PATH
        value: $(workspaces.ssl-ca-directory.path)
      script: |
        #!/usr/bin/env sh
        set -eu

        if [ "${PARAM_VERBOSE}" = "true" ] ; then
          set -x
        fi


        if [ "${WORKSPACE_BASIC_AUTH_DIRECTORY_BOUND}" = "true" ] ; then
          cp "${WORKSPACE_BASIC_AUTH_DIRECTORY_PATH}/.git-credentials" "${PARAM_USER_HOME}/.git-credentials"
          cp "${WORKSPACE_BASIC_AUTH_DIRECTORY_PATH}/.gitconfig" "${PARAM_USER_HOME}/.gitconfig"
          chmod 400 "${PARAM_USER_HOME}/.git-credentials"
          chmod 400 "${PARAM_USER_HOME}/.gitconfig"
        fi

        if [ "${WORKSPACE_SSH_DIRECTORY_BOUND}" = "true" ] ; then
          cp -R "${WORKSPACE_SSH_DIRECTORY_PATH}" "${PARAM_USER_HOME}"/.ssh
          chmod 700 "${PARAM_USER_HOME}"/.ssh
          chmod -R 400 "${PARAM_USER_HOME}"/.ssh/*
        fi

        if [ "${WORKSPACE_SSL_CA_DIRECTORY_BOUND}" = "true" ] ; then
           export GIT_SSL_CAPATH="${WORKSPACE_SSL_CA_DIRECTORY_PATH}"
        fi
        CHECKOUT_DIR="${WORKSPACE_OUTPUT_PATH}/${PARAM_SUBDIRECTORY}"

        cleandir() {
          # Delete any existing contents of the repo directory if it exists.
          #
          # We don't just "rm -rf ${CHECKOUT_DIR}" because ${CHECKOUT_DIR} might be "/"
          # or the root of a mounted volume.
          if [ -d "${CHECKOUT_DIR}" ] ; then
            # Delete non-hidden files and directories
            rm -rf "${CHECKOUT_DIR:?}"/*
            # Delete files and directories starting with . but excluding ..
            rm -rf "${CHECKOUT_DIR}"/.[!.]*
            # Delete files and directories starting with .. plus any other character
            rm -rf "${CHECKOUT_DIR}"/..?*
          fi
        }

        if [ "${PARAM_DELETE_EXISTING}" = "true" ] ; then
          cleandir
        fi

        test -z "${PARAM_HTTP_PROXY}" || export HTTP_PROXY="${PARAM_HTTP_PROXY}"
        test -z "${PARAM_HTTPS_PROXY}" || export HTTPS_PROXY="${PARAM_HTTPS_PROXY}"
        test -z "${PARAM_NO_PROXY}" || export NO_PROXY="${PARAM_NO_PROXY}"

        /ko-app/git-init \
          -url="${PARAM_URL}" \
          -revision="${PARAM_REVISION}" \
          -refspec="${PARAM_REFSPEC}" \
          -path="${CHECKOUT_DIR}" \
          -sslVerify="${PARAM_SSL_VERIFY}" \
          -submodules="${PARAM_SUBMODULES}" \
          -depth="${PARAM_DEPTH}" \
          -sparseCheckoutDirectories="${PARAM_SPARSE_CHECKOUT_DIRECTORIES}"
        cd "${CHECKOUT_DIR}"
        RESULT_SHA="$(git rev-parse HEAD)"
        EXIT_CODE="$?"
        if [ "${EXIT_CODE}" != 0 ] ; then
          exit "${EXIT_CODE}"
        fi
        printf "%s" "${RESULT_SHA}" > "$(results.commit.path)"
        printf "%s" "${PARAM_URL}" > "$(results.url.path)"
~~~

### init

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: init 
spec: 
  description: "生成初始化信息" 
  # 定义一个workspace，后续需要把拉取代码的工作目录挂载到该workspace 
  workspaces: 
  - name: source 
  steps: 
  - name: read 
    image: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0 
    # 指定当前task的工作目录为workspace的路径  
    workingDir: $(workspaces.source.path) 
    script: |  
      #!/usr/bin/env sh 
      ls 
      ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime; echo "Asia/Shanghai" > /etc/timezone 
      CUR_DATE=`TZ='Asia/Shanghai' date '+%Y%m%d-%H%M%S'` 
      # 获取本次提交的Commit信息 
      COMMIT_MESSAGE=`git log -1 --pretty=format:'%h : %an  %s'` 
      CUR_DATE=`date '+%Y%m%d-%H%M%S'` 
      SHORT_COMMIT=`git log -n 1 --pretty=format:'%h'` 
      TAG=`echo "${CUR_DATE}-${SHORT_COMMIT}"` 
      echo $TAG 
~~~

### build

加上前面创建的缓存PVC：

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: build 
spec: 
  description: Code Build 
  workspaces: 
  - name: source 
  params: 
  - name: BUILD_COMMAND 
  - name: BUILD_IMAGE 
  - name: CACHE_DIR 
    default: "/root/.m2" # 默认是maven缓存目录 
  steps: 
  - name: build 
    image: $(params.BUILD_IMAGE)  
    workingDir: $(workspaces.source.path) 
    volumeMounts: 
    - name: cache-volume 
      mountPath: $(params.CACHE_DIR) 
    script: |  
      #!/usr/bin/env sh 
      pwd 
      ls 
      echo $(params.BUILD_COMMAND) 
      $(params.BUILD_COMMAND) 
  volumes: 
  - name: cache-volume 
    persistentVolumeClaim: 
      claimName: tekton-cache
~~~

### kaniko

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: kaniko  
spec: 
  description: >- 
    This Task builds a simple Dockerfile with kaniko and pushes to a registry. 
    This Task stores the image name and digest as results, allowing Tekton Chains to pick up that an image was built & sign it. 
  params: 
    - name: IMAGE_URL 
      type: string 
    - name: DOCKERFILE 
      description: Path to the Dockerfile to build. 
      default: ./Dockerfile 
    - name: CONTEXT 
      description: The build context used by Kaniko. 
      default: ./ 
    - name: EXTRA_ARGS 
      type: array 
      default: [] 
    - name: BUILDER_IMAGE 
      description: The image on which builds will run (default latest) 
      default: registry.cn-beijing.aliyuncs.com/dotbalo/executor:v1.22.0  
  workspaces: 
    - name: source 
      description: Holds the context and Dockerfile 
    # 挂载docker的配置文件，用于访问镜像仓库 
    - name: docker-credentials  
      description: Includes a docker `config.json` 
      optional: true 
      mountPath: /kaniko/.docker 
  results: 
    - name: IMAGE_URL 
      description: URL of the image just built. 
  steps: 
    - name: build-and-push 
      workingDir: $(workspaces.source.path) 
      image: registry.cn-beijing.aliyuncs.com/dotbalo/kaniko-executor:debug  
      script: | 
        executor -c . --insecure --skip-tls-verify -d $(params.IMAGE_URL) 
      securityContext: 
        runAsUser: 0 
    - name: write-url 
      image: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.1  
      script: | 
        set -e 
        image="$(params.IMAGE_URL)" 
        echo -n "${image}" | tee "$(results.IMAGE_URL.path)"
~~~

### deploy

~~~yaml
apiVersion: tekton.dev/v1 
kind: Task 
metadata: 
  name: deploy 
spec: 
  description: deploy to kubernetes by kubectl 
  workspaces: 
  - name: kubeconfig 
    mountPath: /mnt/kubeconfig 
  params: 
    - name: IMAGE_URL 
      type: string 
    - name: NAMESPACE 
      type: string 
      default: default 
    - name: DEPLOY_NAME 
      type: string 
    - name: CONTAINER_NAME 
      type: string 
    - name: KUBECONFIG_PATH 
      type: string 
  steps: 
  - name: deploy 
    image: registry.cn-beijing.aliyuncs.com/dotbalo/kubectl:latest
    script: |  
      pwd 
      ls /mnt/kubeconfig 
      echo "Deploy version: $(params.IMAGE_URL)" 
      echo "kubectl --kubeconfig /mnt/kubeconfig/$(params.KUBECONFIG_PATH) -n $(params.NAMESPACE) set image deploy $(params.DEPLOY_NAME) $(params.CONTAINER_NAME)=$(params.IMAGE_URL)" 
      kubectl --kubeconfig /mnt/kubeconfig/$(params.KUBECONFIG_PATH) -n $(params.NAMESPACE) set image deploy $(params.DEPLOY_NAME) $(params.CONTAINER_NAME)=$(params.IMAGE_URL) 
      kubectl --kubeconfig /mnt/kubeconfig/$(params.KUBECONFIG_PATH) -n $(params.NAMESPACE) get po 
~~~

## tekton必备pipeline

用一个pipeline串联起所有tasks。后续对于不同语言的项目，只需要在pipelinerun中传入params中的必须参数即可。

~~~yaml
apiVersion: tekton.dev/v1 
kind: Pipeline 
metadata: 
  name: deploy
spec: 
  description: |  
    下载代码，初始化并存储数据. 
  # 以下为pipeline可以接收的参数，使用pipelineRun可以进行传参 
  params: 
  - name: url # 用于接收代码地址 
    type: string 
    description: The git repo URL to clone from. 
  - name: revision 
    type: string 
  - name: gitInitImage 
    type: string 
    # 配置一个默认值后续Run的时候就不需要再次传递 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/git-init:v0.29.0  
  - name: BUILD_IMAGE 
    type: string 
    default: registry.cn-beijing.aliyuncs.com/dotbalo/alpine:3.9-tomcat 
  - name: BUILD_COMMAND 
    type: string 
    default: ls 
  - name: CACHE_DIR 
    type: string 
    default: /root/.m2 
  # 添加用于镜像的参数 
  - name: DOCKERFILE 
    type: string 
    default: ./Dockerfile 
  - name: REGISTRY 
    type: string 
  - name: REPOSTORY 
    type: string 
  - name: IMAGE_NAME 
    type: string 
  - name: NAMESPACE 
    type: string 
    default: default 
  - name: DEPLOY_NAME 
    type: string 
  - name: CONTAINER_NAME 
    type: string 
  - name: KUBECONFIG_PATH 
    type: string 
  # 定义workspace 
  workspaces: 
  - name: share-data # 配置一个workspace保留共享数据 
    description: |  
      This workspace contains the cloned repo files, so they can be read by the next task. 
  # 拉取代码ssh配置 
  - name: ssh-directory 
    description: My ssh credentials 
  # 添加docker认证 
  - name: docker-credentials 
    description: docker credentials 
  - name: kubeconfig 
    description: kubernetes kubeconfig 
  # 定义pipeline指定的task 
  tasks: 
  - name: fetch-source 
    taskRef: 
      name: git-clone 
    workspaces: 
    - name: output 
      workspace: share-data 
    # 把接收到的ssh-directory传递给task的ssh-directory 
    - name: ssh-directory 
      workspace: ssh-directory 
    # 传递给task 的参数 
    params: 
    - name: url 
      value: $(params.url) # 从pipeline的params获取参数并传递 
    - name: gitInitImage 
      value: $(params.gitInitImage) 
    - name: revision 
      value: $(params.revision) 
  - name: init 
    # 等代码拉取task结束后执行初始化 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: init 
    workspaces: 
    - name: source 
      workspace: share-data 
  - name: build 
    runAfter: ["fetch-source"] 
    taskRef: 
      name: build 
    workspaces: 
    - name: source 
      workspace: share-data 
    params: 
    - name: BUILD_COMMAND 
      value: $(params.BUILD_COMMAND) 
    - name: BUILD_IMAGE 
      value: $(params.BUILD_IMAGE) 
    - name: CACHE_DIR 
      value: $(params.CACHE_DIR)
  # 添加kaniko task 
  - name: kaniko 
    runAfter: ["build"] 
    taskRef: 
     name: kaniko  
    workspaces: 
    - name: source 
      workspace: share-data 
    - name: docker-credentials 
      workspace: docker-credentials 
    params: 
    - name: IMAGE_URL 
      value: $(params.REGISTRY)/$(params.REPOSTORY)/$(params.IMAGE_NAME):$(tasks.init.results.tag) 
  # 添加deploy task 
  - name: deploy 
    runAfter: ["build"] 
    taskRef: 
      name: deploy 
    workspaces: 
    - name: kubeconfig 
      workspace: kubeconfig 
    params: 
    - name: IMAGE_URL 
      value: $(params.REGISTRY)/$(params.REPOSTORY)/$(params.IMAGE_NAME):$(tasks.init.results.tag) 
    - name: NAMESPACE 
      value: $(params.NAMESPACE) 
    - name: DEPLOY_NAME 
      value: $(params.DEPLOY_NAME) 
    - name: CONTAINER_NAME 
      value: $(params.CONTAINER_NAME) 
    - name: KUBECONFIG_PATH 
      value: $(params.KUBECONFIG_PATH)
~~~

## 自动化部署Java应用

### 创建Java测试用例

这里用一个示例项目：https://gitee.com/dukuan/spring-boot-project.git。需要导入到gitlab中

1. 找到之前创建的Gitlab Group: local-k8s-platform-tools
2. 点New Project - Import Project - Repository by URL
3. 输入gitee项目的URL，点击导入即可。

### 创建deployment

需要先把deployment apply出来，镜像随便写一个，后面流水线会替换成最新编译出来的镜像

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: spring-boot-project
  namespace: demo
  labels:
    app: spring-boot-project
spec:
  selector:
    app: spring-boot-project
  type: ClusterIP
  ports:
  - name: web
    port: 8761
    protocol: TCP
    targetPort: 8761

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: spring-boot-project
  namespace: demo
spec:
  rules:
  - host: spring-boot-project.hanxux.local
    http:
      paths:
      - backend:
          service:
            name: spring-boot-project
            port:
              number: 8761
        path: /
        pathType: ImplementationSpecific

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spring-boot-project
  namespace: demo
  labels: # deployment label和流水线中的set -l指定的一致
    app: spring-boot-project
spec:
  replicas: 1
  selector:
    matchLabels:
      app: spring-boot-project
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: spring-boot-project
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - spring-boot-project
              topologyKey: kubernetes.io/hostname
            weight: 100
      imagePullSecrets:
      - name: harborkey # harbor仓库秘钥，需要和之前创建的secret名称保持一致
      containers:
      - name: spring-boot-project # container名称，需要和流水线中set命令指定的容器名称保持一致
        image: nginx # 一开始先用nginx占位，后续流水线构建完成后替换为实际镜像
        imagePullPolicy: IfNotPresent
        env:
        - name: TZ
          value: Asia/Shanghai
        - name: LANG
          value: C.UTF-8
        ports:
        - name: web
          containerPort: 8761
          protocol: TCP
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8761
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8761
          timeoutSeconds: 2
        resources:
          limits:
            cpu: 994m
            memory: 1170Mi
          requests:
            cpu: 10m
            memory: 55Mi
~~~

创建之后pod可能无法启动，等到流水线创建完成，替换了镜像后就可以了。

### 创建Dockerfile

在执行流水线过程时，需要将代码的编译产物做成镜像。本次示例是Java项目，只需要把编译出来的Jar包放在有jre环境的镜像中，然后启动该Jar包即可：

~~~sh
#  基础镜像可以按需修改，可以更改为公司自有镜像 
FROM registry.cn-beijing.aliyuncs.com/dotbalo/jre:8u211-data 
# jar包名称改成实际的名称，本示例为spring-cloud-eureka-0.0.1-SNAPSHOT.jar 
COPY target/spring-cloud-eureka-0.0.1-SNAPSHOT.jar ./ 
# 启动Jar包 
CMD java -jar spring-cloud-eureka-0.0.1-SNAPSHOT.jar 
~~~

同样在gitlab项目根目录中添加这个Dockerfile。注意：Dockerfile必须文件名是Dockerfile，否则Kaniko识别不出来

### pipelinerun自动发版

~~~yaml
apiVersion: tekton.dev/v1beta1 
kind: PipelineRun 
metadata: 
  # 自动生成名字 
  generateName: spring-boot-project- 
spec: 
  pipelineRef: 
    name: deploy 
  # 定义workspace 
  workspaces: 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 按照项目-服务名字-环境当做workspace 
    subPath: spring-boot-project-dev 
  # 把K8s的secret挂载到git-credentials workspace 
  - name: ssh-directory 
    secret: 
      secretName: git-ssh-auth 
  - name: docker-credentials 
    secret: 
      secretName: docker-credentials 
  - name: kubeconfig 
    secret: 
      secretName: kubeconfig 
  # 传递参数给pipeline 
  params: 
  - name: url 
    value: "git@192.168.40.183:local-k8s-platform-tools/vue-project.git"
  - name: revision 
    value: "master" 
  - name: BUILD_IMAGE 
    value: registry.cn-beijing.aliyuncs.com/dotbalo/maven:3.5.3  
  - name: BUILD_COMMAND 
    value: |- 
      mvn clean install -DskipTests 
      ls target/* 
  - name: REGISTRY # harbor地址
    value: 192.168.40.180:32002
  - name: REPOSTORY 
    value: platform-tools-local 
  - name: IMAGE_NAME 
    value: spring-boot-project-tekton
  - name: NAMESPACE 
    value: demo
  - name: DEPLOY_NAME 
    value: spring-boot-project 
  - name: CONTAINER_NAME 
    value: spring-boot-project 
  - name: KUBECONFIG_PATH 
    value: study-kubeconfig 
  - name: CACHE_DIR 
    value: "/root/.m2" 
~~~

## 自动化部署Go应用

### 创建测试项目

测试项目地址：https://gitee.com/dukuan/go-project.git。导入到Gitlab中

### 创建deployment

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: go-project
  namespace: demo
  labels:
    app: go-project
spec:
  selector:
    app: go-project
  type: ClusterIP
  ports:
  - name: web
    port: 8080
    protocol: TCP
    targetPort: 8080

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: go-project
  namespace: demo
spec:
  rules:
  - host: go-project.hanxux.local
    http:
      paths:
      - backend:
          service:
            name: go-project
            port:
              number: 8080
        path: /
        pathType: ImplementationSpecific

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: go-project
  namespace: demo
  labels: # deployment label和流水线中的set -l指定的一致
    app: go-project
spec:
  replicas: 1
  selector:
    matchLabels:
      app: go-project
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: go-project
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - go-project
              topologyKey: kubernetes.io/hostname
            weight: 100
      imagePullSecrets:
      - name: harborkey # harbor仓库秘钥，需要和之前创建的secret名称保持一致
      containers:
      - name: go-project # container名称，需要和流水线中set命令指定的容器名称保持一致
        image: nginx # 一开始先用nginx占位，后续流水线构建完成后替换为实际镜像
        imagePullPolicy: IfNotPresent
        env:
        - name: TZ
          value: Asia/Shanghai
        - name: LANG
          value: C.UTF-8
        ports:
        - name: web
          containerPort: 8080
          protocol: TCP
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 8080
          timeoutSeconds: 2
        resources:
          limits:
            cpu: 994m
            memory: 1170Mi
          requests:
            cpu: 10m
            memory: 55Mi
~~~

### 创建Dockerfile

创建到代码仓库根目录。pipeline agent拉完代码，执行go build编译后，在代码目录的go-project会生成一个二进制文件。拷贝到一个linux环境就可以直接执行，所以基础镜像用一个alpine或者其他小镜像即可。

~~~sh
FROM registry.cn-beijing.aliyuncs.com/dotbalo/alpine-glibc:alpine-3.9 

# 如果定义了单独的配置文件，可能需要拷贝到镜像中 
# COPY conf/  ./conf  

# 包名按照实际情况进行修改 
COPY ./go-project ./ 

# 启动该应用 
ENTRYPOINT [ "./go-project"] 
~~~

### pipelinerun自动发版

~~~yaml
apiVersion: tekton.dev/v1beta1 
kind: PipelineRun 
metadata: 
  # 自动生成名字 
  generateName: go-project-dev- 
spec: 
  pipelineRef: 
    name: deploy 
  # 定义workspace 
  workspaces: 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 按照项目-服务名字-环境当做workspace 
    subPath: go-project-dev 
  # 把K8s的secret挂载到git-credentials workspace 
  - name: ssh-directory 
    secret: 
      secretName: git-ssh-auth 
  - name: docker-credentials 
    secret: 
      secretName: docker-credentials 
  - name: kubeconfig 
    secret: 
      secretName: kubeconfig 
  # 传递参数给pipeline 
  params: 
  - name: url 
    value: "git@192.168.40.183:local-k8s-platform-tools/go-project.git"
  - name: revision 
    value: "master" 
  - name: BUILD_IMAGE 
    value: registry.cn-beijing.aliyuncs.com/dotbalo/golang:1.15  
  - name: BUILD_COMMAND 
    value: |- 
      export GO111MODULE=on 
      export CGO_ENABLED=0 
      go env -w GOPROXY=https://goproxy.cn,direct 
      go build 
  - name: REGISTRY # harbor地址
    value: 192.168.40.180:32002
  - name: REPOSTORY 
    value: platform-tools-local 
  - name: IMAGE_NAME 
    value: go-project-tekton
  - name: NAMESPACE 
    value: demo
  - name: DEPLOY_NAME 
    value: go-project 
  - name: CONTAINER_NAME 
    value: go-project 
  - name: KUBECONFIG_PATH 
    value: study-kubeconfig 
  - name: CACHE_DIR 
    value: "/go/pkg/" 
~~~

## 自动化构建前端应用

### 创建测试项目

测试项目地址在：https://gitee.com/dukuan/vue-project.git。需要导入到Gitlab的group中：New Project - Import Project

### 定义deployment

相比Java应用，只需要更改资源名称和端口号即可：

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: vue-project
  namespace: demo
  labels:
    app: vue-project
spec:
  selector:
    app: vue-project
  type: ClusterIP
  ports:
  - name: web
    port: 80
    protocol: TCP
    targetPort: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vue-project
  namespace: demo
spec:
  rules:
  - host: vue-project.hanxux.local
    http:
      paths:
      - backend:
          service:
            name: vue-project
            port:
              number: 80
        path: /
        pathType: ImplementationSpecific
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vue-project
  namespace: demo
  labels: # deployment label和流水线中的set -l指定的一致
    app: vue-project
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vue-project
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: vue-project
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - vue-project
              topologyKey: kubernetes.io/hostname
            weight: 100
      imagePullSecrets:
      - name: harborkey # harbor仓库秘钥，需要和之前创建的secret名称保持一致
      containers:
      - name: vue-project # container名称，需要和流水线中set命令指定的容器名称保持一致
        image: nginx # 一开始先用nginx占位，后续流水线构建完成后替换为实际镜像
        imagePullPolicy: IfNotPresent
        env:
        - name: TZ
          value: Asia/Shanghai
        - name: LANG
          value: C.UTF-8
        ports:
        - name: web
          containerPort: 80
          protocol: TCP
        livenessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 2
        readinessProbe:
          failureThreshold: 2
          initialDelaySeconds: 30
          periodSeconds: 10
          successThreshold: 1
          tcpSocket:
            port: 80
          timeoutSeconds: 2
        resources:
          limits:
            cpu: 994m
            memory: 1170Mi
          requests:
            cpu: 10m
            memory: 55Mi
~~~

### 创建Dockerfile

创建到仓库根目录。前端应用构建之后一般会在dist目录下产生html文件，只需要拷贝到nginx目录下即可。编译镜像就找一个nginx镜像就行。

~~~sh
FROM registry.cn-beijing.aliyuncs.com/dotbalo/nginx:1.15.12 
COPY dist/* /usr/share/nginx/html/ 
~~~

### pipelinerun自动发版

~~~yaml
apiVersion: tekton.dev/v1beta1 
kind: PipelineRun 
metadata: 
  # 自动生成名字 
  generateName: vue-project-dev- 
spec: 
  pipelineRef: 
    name: deploy 
  # 定义workspace 
  workspaces: 
  - name: share-data 
    persistentVolumeClaim: 
      claimName: tekton-workspace 
    # 按照项目-服务名字-环境当做workspace 
  subPath: vue-project-dev 
  # 把K8s的secret挂载到git-credentials workspace 
  - name: ssh-directory 
    secret: 
      secretName: git-ssh-auth 
  - name: docker-credentials 
    secret: 
      secretName: docker-credentials 
  - name: kubeconfig 
    secret: 
      secretName: kubeconfig 
  # 传递参数给pipeline 
  params: 
  - name: url 
    value: "git@192.168.40.183:local-k8s-platform-tools/go-project.git"
  - name: revision 
    value: "master" 
  - name: BUILD_IMAGE 
    value: registry.cn-beijing.aliyuncs.com/dotbalo/node:lts  
  - name: BUILD_COMMAND 
    value: |- 
      npm install --registry=https://registry.npmmirror.com/ 
      npm run build 
  - name: REGISTRY # harbor地址
    value: 192.168.40.180:32002
  - name: REPOSTORY 
    value: platform-tools-local 
  - name: IMAGE_NAME 
    value: vue-project-tekton
  - name: NAMESPACE 
    value: demo
  - name: DEPLOY_NAME 
    value: vue-project 
  - name: CONTAINER_NAME 
    value: vue-project 
  - name: KUBECONFIG_PATH 
    value: study-kubeconfig 
  - name: CACHE_DIR 
    value: "/go/pkg/" # nodejs的node_modules都在当前目录无需特殊指定 
~~~

