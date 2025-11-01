# ArgoCD介绍

Argo CD 是一个专为 Kubernetes 环境设计的声明式、GitOps 持续交付 (CD) 工具。它隶属于 [CNCF](https://www.cncf.io/) 旗下的 [Argo 项目](https://argoproj.github.io/)，是一个被广泛采用的开源项目。

Argo CD 的核心思想是将 Git 仓库作为应用部署和基础设施配置的**唯一事实来源** (Single Source of Truth)。

它自动同步 Git 仓库中定义的期望应用状态（通常是 Kubernetes 清单 YAML 文件、Helm Charts、Kustomize 目录等）与目标 Kubernetes 集群中的实际运行状态，确保两者始终保持一致。这种模式被称为 GitOps。

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

# 安装ArgoCD-基于yaml

参考：[快速开始 - Argo CD 中文文档 平台工程 Devops](https://argocd.devops.gold/getting_started/#1-argo-cd)

~~~sh
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
~~~

用NodePort svc访问UI界面：

~~~sh
kubectl edit svc argocd-server -n argocd
# type: ClusterIP改成type: NodePort
~~~

查看该svc的高位端口，访问登录界面。默认用户名admin，密码获取：

~~~sh
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath="{.data.password}" | base64 -d
~~~

# 安装ArgoCD-基于helm chart

> 注意：目前argocd helm chart仅支持非高可用安装方式。
>
> 如需高可用安装，参考：[ArgoCD-HA](https://argocd.devops.gold/operator-manual/installation/#_4)

github release：[argoproj/argo-helm: ArgoProj Helm Charts](https://github.com/argoproj/argo-helm)

artifactHub：[argo-cd 3.9.0 · argoproj/argo](https://artifacthub.io/packages/helm/argo/argo-cd/3.9.0)

~~~sh
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update argo
helm pull argo/argo-cd --version 8.3.0
~~~

修改values.yaml文件：

~~~yaml

~~~

安装：
~~~sh
cd argo-cd
helm install argocd . -n argocd --create-namespace --set server.service.type=NodePort
~~~


# 基本使用
## 安装argocd cli【可选】
```sh
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
```
常用命令：
~~~sh
# 登录命令
領菘项argocd login localhost:8080#假设通过 8080 端口转发
#创建新的 Argo CD 应用8
argocd app create myapp --repo https://your-git-repo.com/repo.git --pa拗4
#列出所有已管理的应用筈5
argocd app list6
#获取指定应用的详细信息
argocd app get <app-name>S
#手动同步应用，使其与 Git 中定义的状态一致9
argocd app sync <app-name>
#删除一个 ArgoCD 应用
argocd app delete <app-name>
#列出Argo CD 当前管理的所有 Kubernetes 集群
argocd cluster list14
#将 kubeconfig 中的集群上下文添加到 Argo CD 进行管理15
argocd cluster add <context-name>
#更新当前登录用户的密码17
argocd account update-password
#显示 Argo CD 客户端和服务器的版本信息19
argocd version
#查看所有命令的帮助信息
argocd help
#生成 Bash 自动补全脚本
argocd completion bash
~~~

## 访问web-UI
获取初始密码：
```sh
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```


## 基于gitee仓库部署yaml

参考官网教程部署示例：https://argocd.devops.gold/getting_started/

