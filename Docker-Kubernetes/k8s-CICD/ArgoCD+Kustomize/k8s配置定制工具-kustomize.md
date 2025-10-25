# kustomize介绍

Kustomize是一个无需模板的配置定制工具，专门用于k8s资源管理。与传统的基于模板的引擎helm不同，他直接操作k8s原生资源文件，通过叠加（overlay）和变异（mutation）等机制，让用户以声明式的风格对资源进行个性化定制。

## 原生支持

Kustomize 从一开始就是为 Kubernetes 量身打造的，它紧密集成在 kubectl 命令行工具中，自 Kubernetes 1.14 版本起成为默认的配置管理方式。这意味着，只要你熟悉 kubectl，就能毫无阻碍地使用 Kustomize，无需额外安装复杂的插件或依赖，极大地简化了工具链的复杂度，让整个配置管理流程更加流畅、高效。

例如，当你需要部署一个应用到不同的命名空间，只需在对应的 Kustomize 目录下修改 namespace 相关的配置，然后使用 `kubectl apply -k` 命令即可轻松完成部署，就像原生的 Kubernetes 操作一样自然。

## 声明式定制

采用声明式的配置风格是 Kustomize 的一大亮点。用户只需明确指定想要的最终状态，Kustomize 会自动处理如何从基础配置达到这个状态的过程。

假设你有一个基础的 Deployment 资源用于运行 Web 应用，在测试环境下，你需要增加副本数、调整资源请求和限制，以确保应用在压力测试下的稳定性。使用 Kustomize，你只需在测试环境对应的 overlay 目录下创建一个 kustomization.yaml 文件，声明副本数、资源值的变化，而无需关心底层的实现细节。这种方式使得配置意图一目了然，无论是对于后续的维护还是团队成员之间的交流，都变得更加容易。

## 分层管理

Kustomize 支持分层配置，通过基础层（Base）和覆盖层（Overlay）的组合，实现了配置的高度复用。

以一个多租户的 SaaS 应用为例，基础层可以定义通用的 Deployment、Service、ConfigMap 等资源，涵盖了应用的核心功能和默认配置。而每个租户作为一个覆盖层，可以根据自身的需求，如定制域名、数据库连接字符串、特定的环境变量等，对基础层进行个性化扩展。这种分层架构不仅减少了重复配置，提高了配置的一致性，还能快速适应不同场景下的变化，当基础应用升级时，只需更新基础层配置，各个覆盖层就能平滑继承新特性。

## 环境感知

在不同的运行环境中，应用往往需要不同的配置参数。Kustomize 能够很好地适应这种需求，通过识别不同的环境目录（如 dev、prod、qa 等），自动加载相应环境下的配置覆盖。

比如，在开发环境，你可能希望启用详细的日志输出以便调试，而生产环境则需要关闭调试日志，优化性能。利用 Kustomize，你可以在 dev 目录下的 kustomization.yaml 中添加开启调试日志的配置补丁，在 prod 目录下则相反，确保应用在每个环境下都能以最佳状态运行，同时又能在统一的框架下进行管理，避免了因环境差异导致的配置混乱。

# kustomize使用

## 创建基础配置--Base

首先，你需要创建一个基础配置目录，里面存放着应用的原始 Kubernetes 资源文件，例如 deployment.yaml、service.yaml、configmap.yaml 等。这些文件定义了应用的基本架构和默认参数，就像是构建房屋的蓝图。

以一个简单的 Node.js 应用为例，在 base 目录下，deployment.yaml 可能如下：

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nodejs-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nodejs-app
  template:
    metadata:
      labels:
        app: nodejs-app
    spec:
      containers:
      - name: nodejs-app
        image: your-nodejs-image:latest
        ports:
        - containerPort: 3000
~~~

service.yaml 用于暴露服务：

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: nodejs-app-service
spec:
  selector:
    app: nodejs-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
~~~

同时，还可以有一个 configmap.yaml 来存储应用的配置参数：

~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nodejs-app-config
data:
  NODE_ENV: "development"
~~~

## 构建覆盖层--Overlay

接下来，针对不同的环境或需求，创建覆盖层目录，如 dev、prod 等。在每个覆盖层目录下，都需要创建一个 kustomization.yaml 文件，用于定义对基础配置的修改。

在 dev 目录下，kustomization.yaml 示例如下：

> 这里通过 patches 对 Deployment 的副本数进行了修改，同时利用 configMapGenerator 更新了 ConfigMap 中的环境变量，开启调试模式，以适应开发环境的需求。

~~~yaml
tee ./dev/kustomization.yaml <<'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
# 指向基础配置目录
bases:
-../base
# 定义资源补丁，这里增加副本数为 3
patches:
- patch: |
    - op: replace
      path: /spec/replicas
      value: 3
    target:
      kind: Deployment
      name: nodejs-app
# 修改 ConfigMap 中的环境变量
configMapGenerator:
- name: nodejs-app-config
  behavior: merge
  literals:
  - NODE_ENV=development
  - DEBUG=true
EOF
~~~

在 prod 目录下，配置则会有所不同，可能会减少副本数，关闭调试，优化资源请求等：

~~~yaml
tee ./prod/kustomization.yaml <<'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
-../base
patches:
- patch: |
    - op: replace
      path: /spec/replicas
      value: 2
    target:
      kind: Deployment
      name: nodejs-app
configMapGenerator:
- name: nodejs-app-config
  behavior: merge
  literals:
  - NODE_ENV=production
  - DEBUG=false
EOF
~~~

## 应用配置

完成基础配置和覆盖层的创建后，就可以使用 kubectl 来应用配置了。在对应的覆盖层目录下，执行命令：

> 这个命令会根据当前目录下的 kustomization.yaml 以及相关的基础配置，生成最终的 Kubernetes 资源清单，并将其应用到集群中。如果后续需要更新配置，只需修改覆盖层的相应内容，再次执行该命令即可，Kustomize 会智能地处理资源的变更，确保平滑过渡。

~~~sh
kubectl apply -k.
~~~

# kustomize高级特性

## 变量替换与Secret管理

在实际应用中，经常需要处理敏感信息，如数据库密码、API 密钥等。Kustomize 提供了便捷的 Secret 管理机制，允许你在配置中使用变量，并在部署时将其替换为真实的值。

首先，你可以在 kustomization.yaml 中定义变量，例如：

~~~yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
-../base
vars:
- name: db_password #定义变量名称
  obj:
    kind: Secret #变量的值来自secret
    name: my-db-secret #secret名字
    apiVersion: v1
  fieldref:
    fieldPath: data.password #secret里面的password字段
~~~

然后，在资源配置文件中，如 deployment.yaml，可以使用这个变量：

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: my-app
        env:
        - name: DB_PASSWORD
          valueFrom:
            fieldRef:
              fieldPath: $(db_password)
~~~

这样，在应用部署时，Kustomize 会自动将变量替换为 Secret 中的真实密码，既保证了安全性，又方便了配置的管理，避免了明文存储敏感信息带来的风险。

## 跨文件资源引用与合并

当应用变得复杂，资源之间的依赖和关联增多时，Kustomize 允许跨文件进行资源引用和合并，确保配置的完整性。

例如，你可能有多个不同用途的 ConfigMap，一个用于存储应用的通用配置，另一个用于特定模块的配置。在 kustomization.yaml 中，可以通过 resources 和 configMapGenerator 的组合来实现合并：

~~~yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
-../base
resources:
-../common-config/configmap.yaml #这是一个保存基础配置的configMap
configMapGenerator:
- name: module-specific-config #需要生成的新configMap名字
  files:
  - module-config.properties #加载一个specific的configMap合并进去
~~~

> 这里不仅引用了基础目录下的资源，还生成了一个新的 `module-specific-config`，并将本地的 `module-config.properties` 文件内容合并进去，使得应用能够一站式获取所需的所有配置，减少了配置分散带来的管理难题。

## Generator和Transformer

Kustomize 内置了多种生成器（Generator）和变压器（Transformer），如 configMapGenerator、secretGenerator、imageTagTransformer 等，用于自动化创建和修改资源。

以 imageTagTransformer 为例，在应用升级时，你无需手动修改每个 Deployment 中的镜像标签。只需在 kustomization.yaml 中配置：

~~~yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
-../base
imageTagTransformer:
  name: my-app-image
  newTag: v2.0
~~~

> 这个配置会自动查找所有引用 my-app-image 的资源，并将其镜像标签更新为 v2.0，大大简化了版本升级的流程，确保了整个应用集群的一致性更新。同时，你还可以根据自己的需求编写自定义的生成器和变压器，深度定制 Kustomize 的功能，满足复杂多变的业务场景。
