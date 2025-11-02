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
3. 还需要将 ArgoCD Image Updater 与 Git 集成，这也是重点，这样 ArgoCD Image Updater 就可以将镜像更新直接提交回源 Git 仓库。可以在 ArgoCD 的 Dashboard 中先添加一个 Git 仓库 `https://github.com/hangx969/local-k8s-platform-tools#`

   
4. 