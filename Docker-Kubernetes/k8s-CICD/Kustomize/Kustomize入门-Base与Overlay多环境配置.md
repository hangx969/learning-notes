---
title: Kustomize 入门：用 Base 和 Overlay 管理 Kubernetes 多环境配置
source: https://mp.weixin.qq.com/s/WRzeIOTqi7vYdYkBhWi0Zg
created: 2026-09-12
updated: 2026-09-12
tags:
  - kubernetes
  - cicd
  - kustomize
  - configuration-management
aliases:
  - Kustomize Base Overlay 入门
  - Kustomize 多环境配置
---

# Kustomize 入门：用 Base 和 Overlay 管理 Kubernetes 多环境配置

> [!note] 来源与版本边界
> 本文由 [[0raw/Kustomize 入门：用 Base 和 Overlay 管理 Kubernetes 多环境配置|原始剪藏]] 清洗整理。字段支持情况取决于独立 Kustomize 与 `kubectl` 内置版本；新项目优先使用 `resources`、`labels` 和统一的 `patches` 字段，遇到兼容问题先执行 `kubectl version --client` 并核对对应版本文档。

在学习 Kubernetes 时，我们通常会先编写 `deployment.yaml` 、 `service.yaml` 等资源清单。

当只有一个环境时，这种方式没有什么问题。但随着测试环境、预发布环境和生产环境逐渐增加，一个新的问题就出现了：不同环境的大部分配置相同，只有少量内容不一样。

例如，测试环境和生产环境可能只有以下差异：

- Namespace 不同；
- 镜像仓库或镜像版本不同；
- Deployment 副本数不同；
- 环境标签不同；
- CPU、内存等资源限制不同。

最直接的做法，是为每个环境复制一套完整的 YAML。但是随着项目迭代，这种方式很容易出现配置不一致的问题。

例如，Deployment 新增了健康检查，如果只修改了测试环境的 YAML，却忘记同步修改生产环境，那么两套配置就会逐渐产生偏差。

Kustomize 要解决的，正是这个问题：

> 保留一份公共 Kubernetes 配置，只单独描述不同环境之间的差异。

## 一、Kustomize 是什么

Kustomize 是一个用于定制 Kubernetes 配置的工具。

它可以读取普通的 Kubernetes YAML，然后根据 `kustomization.yaml` 中声明的规则，对资源进行组合和修改，最终生成一份新的 Kubernetes YAML。

整个过程可以简单理解为：

```text
原始 Kubernetes YAML
        +
kustomization.yaml 中的定制规则
        ↓
最终 Kubernetes YAML
```

Kustomize 官方将这种方式称为“template-free”，也就是不依赖传统模板。

例如，使用模板工具时，可能会在 YAML 中写入变量占位符：

```yaml
image: ${IMAGE_NAME}:${IMAGE_TAG}
```

而 Kustomize 通常保留正常的 Kubernetes YAML：

```yaml
image: nginx:latest
```

然后在 `kustomization.yaml` 中使用 `images` 、 `replicas` 、 `namespace` 、 `labels` 、 `patches` 等字段对它进行修改。

这样做的一个好处是：Base 中的 YAML 仍然是普通的 Kubernetes YAML，不需要先替换变量才能阅读和分析。

Kustomize 可以作为独立命令使用，也已经集成进 `kubectl` 。根据 Kubernetes 官方文档， `kubectl` 从 1.14 版本开始支持通过 Kustomize 管理 Kubernetes 对象，因此已经安装 `kubectl` 的情况下，通常可以直接使用：

```bash
kubectl kustomize <目录>
kubectl apply -k <目录>
```

本文主要介绍 `kubectl` 内置的使用方式。

## 二、Kustomize 不是什么

在继续学习之前，需要先明确 Kustomize 的能力边界。

### 1. Kustomize 不是 Kubernetes 控制器

Kustomize 通常在客户端执行。

运行下面的命令时：

```bash
kubectl kustomize overlays/test
```

Kustomize 只会读取本地文件、执行定制规则，并把最终 YAML 输出到终端，不会在 Kubernetes 集群中创建资源。

只有继续执行 `kubectl apply -k` ，生成的资源才会被提交给 Kubernetes API Server。

### 2. Kustomize 不是传统模板引擎

Kustomize 的主要思路不是在 YAML 中预留变量，然后用参数替换字符串，而是对 Kubernetes 资源进行结构化修改。

例如：

- 使用 `images` 修改镜像；
- 使用 `replicas` 修改副本数；
- 使用 `namespace` 设置命名空间；
- 使用 `patches` 修改资源限制。

### 3. Kustomize 不是 Release 管理器

Kustomize 负责生成最终 Kubernetes 配置，但它本身不会像 Helm 一样维护 Release、Release 历史和回滚记录。

因此，Kustomize 和 Helm 并不是完全相同的工具，本文不展开二者的详细比较。

## 三、Kustomize 的核心思路：Base 和 Overlay

学习 Kustomize，最重要的是理解 Base 和 Overlay。

### 1. Base：公共配置

Base 保存多个环境共同使用的 Kubernetes 配置。

例如，测试环境和生产环境都需要以下资源：

- Deployment；
- Service；
- 相同的容器端口；
- 相同的健康检查；
- 相同的 Volume 挂载；
- 相同的应用标签和 Selector。

这些真正公共、相对稳定的内容，可以统一放在 Base 中。

一个简单的 Base 目录如下：

```text
base/
├── deployment.yaml
├── service.yaml
└── kustomization.yaml
```

其中：

- `deployment.yaml` ：定义应用工作负载；
- `service.yaml` ：定义集群内部访问方式；
- `kustomization.yaml` ：声明 Base 中包含哪些资源。

### 2. Overlay：环境差异

Overlay 在 Base 的基础上继续定制配置。

例如：

- Test Overlay 设置测试环境的 Namespace；
- Prod Overlay 设置生产环境的 Namespace；
- 测试环境使用 1 个副本；
- 生产环境使用 3 个副本；
- 测试和生产使用不同的镜像版本；
- 生产环境设置更高的 CPU 和内存限制。

一个常见的项目目录如下：

```text
kustomize-demo/
├── base/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── overlays/
    ├── test/
    │   └── kustomization.yaml
    └── prod/
        └── kustomization.yaml
```

它们之间的关系可以理解为：

```text
Base 公共配置
    +
Test Overlay 环境差异
    ↓
测试环境最终 YAML
```

以及：

```text
Base 公共配置
    +
Prod Overlay 环境差异
    ↓
生产环境最终 YAML
```

Base 不需要知道有哪些 Overlay。测试和生产 Overlay 可以分别引用同一个 Base，然后生成各自的最终配置。

需要注意的是，Base 和 Overlay 都不是特殊的 Kubernetes 资源类型。它们本质上都是包含 `kustomization.yaml` 的配置目录，只是承担的职责不同：

- Base：提供公共配置；
- Overlay：引用 Base，并描述环境差异。

还有一个容易混淆的地方：

> Base 是 Kustomize 中的一个概念，但现在不建议在 `kustomization.yaml` 中继续使用旧的 `bases` 字段。

当前推荐使用 `resources` 引用 Base：

```yaml
resources:
  - ../../base
```

Kustomize 官方代码已经将 `bases` 标记为弃用字段，并建议迁移到 `resources` 。

## 四、kustomization.yaml 是干什么的

`kustomization.yaml` 是 Kustomize 的核心配置文件。

它主要用来说明：

- 需要读取哪些 Kubernetes 资源；
- 需要引用哪些 Base；
- 需要生成哪些资源；
- 需要对资源进行哪些修改。

推荐使用下面的完整头部：

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
```

这里的 `apiVersion` 和 `kind` 描述的是 Kustomize 配置格式，而不是要在 Kubernetes 集群中创建一个名为 `Kustomization` 的业务资源。

因此，不应该直接执行：

```bash
kubectl apply -f kustomization.yaml
```

因为 `-f` 会把这个文件当成普通 Kubernetes 资源提交给 API Server。

正确方式是使用 `-k` ，并让它指向包含 `kustomization.yaml` 的目录：

```bash
kubectl apply -k overlays/test
```

此时， `kubectl` 会先使用 Kustomize 构建该目录，再把构建结果提交给 Kubernetes API Server。

## 五、六个最常用的 Kustomize 字段

Kustomize 支持的字段很多，但初学阶段没有必要全部掌握。

对于常见的测试、生产多环境配置，建议先掌握以下六个字段：

| 字段 | 主要用途 |
| --- | --- |
| `resources` | 引入 YAML 文件或其他 Kustomization 目录 |
| `namespace` | 设置资源所属的 Namespace |
| `images` | 修改镜像名称、Tag 或 Digest |
| `replicas` | 修改工作负载副本数 |
| `labels` | 为资源和 Pod 添加标签 |
| `patches` | 修改其他复杂字段 |

下面分别介绍它们的作用。

### 1. resources：引入资源

假设 Base 目录中有两个资源文件：

```text
base/
├── deployment.yaml
├── service.yaml
└── kustomization.yaml
```

那么 `base/kustomization.yaml` 可以写成：

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
```

`resources` 表示当前 Kustomization 需要包含哪些资源。

它既可以引用普通 Kubernetes YAML：

```yaml
resources:
  - deployment.yaml
  - service.yaml
```

也可以引用另一个包含 `kustomization.yaml` 的目录：

```yaml
resources:
  - ../../base
```

当 Overlay 引用 `../../base` 时，Kustomize 会先构建 Base，再对 Base 生成的资源进行环境定制。

需要注意：

> `resources` 中的相对路径，以当前 `kustomization.yaml` 所在目录为基准，而不是以执行命令时所在的 Shell 目录为基准。

例如，当前文件位于：

```text
overlays/test/kustomization.yaml
```

那么：

```yaml
resources:
  - ../../base
```

表示从 `overlays/test` 向上返回两级，然后进入项目根目录下的 `base` 。

### 2. namespace：设置资源所属的命名空间

测试和生产环境通常会使用不同的 Namespace：

```yaml
namespace: kustomize-test
```

Kustomize 构建时，会给 Deployment、Service、ConfigMap 等命名空间作用域资源设置：

```yaml
metadata:
  namespace: kustomize-test
```

例如，Base 中的 Deployment 原来是：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kustomize-demo
```

构建后可能变成：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kustomize-demo
  namespace: kustomize-test
```

但这里必须区分两个概念：

```yaml
namespace: kustomize-test
```

表示把命名空间作用域资源放入 `kustomize-test` ，它不会自动创建这个 Namespace。

如果集群中还不存在该 Namespace，就需要额外提供一个 Namespace 资源：

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kustomize-test
```

然后通过 `resources` 把它加入最终输出。

### 3. images：修改容器镜像

假设 Base 中的 Deployment 使用：

```yaml
containers:
  - name: web
    image: nginx:latest
```

测试环境希望使用固定版本，可以在 Overlay 中写：

```yaml
images:
  - name: nginx
    newTag: "1.27.4-alpine"
```

构建后，镜像会变成：

```yaml
image: nginx:1.27.4-alpine
```

如果还需要修改镜像仓库地址，可以同时使用 `newName` ：

```yaml
images:
  - name: nginx
    newName: registry.example.com/library/nginx
    newTag: "1.27.4-alpine"
```

构建结果为：

```yaml
image: registry.example.com/library/nginx:1.27.4-alpine
```

这里最容易混淆的是 `name` 的匹配对象。

Base 中的配置是：

```yaml
containers:
  - name: web
    image: nginx:latest
```

其中：

- 容器名称是 `web` ；
- 镜像名称是 `nginx` 。

所以 `images.name` 应该写成：

```text
name: nginx
```

它匹配的是 `image: nginx:latest` 中的镜像名称，而不是 `containers[].name` 。

还需要注意：

> Kustomize 只负责修改 YAML 中的镜像字符串，不会连接镜像仓库检查这个 Tag 是否真实存在。

即使写了一个不存在的 Tag， `kubectl kustomize` 也可能正常生成 YAML。真正部署后，Kubelet 拉取不到镜像时，Pod 才会出现 `ErrImagePull` 或 `ImagePullBackOff` 。

### 4. replicas：修改副本数

假设 Base 中的 Deployment 为：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kustomize-demo
spec:
  replicas: 1
```

生产环境需要 3 个副本，可以在 Overlay 中写：

```yaml
replicas:
  - name: kustomize-demo
    count: 3
```

构建后：

```yaml
spec:
  replicas: 3
```

其中：

- `name` ：匹配资源的 `metadata.name` ；
- `count` ：设置最终副本数。

这里的 `name` 不是容器名称，也不是镜像名称，而是 Deployment 等工作负载资源的名称。

`replicas` 适合处理简单的副本数差异。如果需要同时修改滚动更新策略、资源限制等复杂字段，则应该使用 `patches` 。

### 5. labels：添加环境标签

为了区分测试和生产环境，可以给资源添加环境标签：

```yaml
labels:
  - pairs:
      environment: test
    includeTemplates: true
    includeSelectors: false
```

其中：

- `pairs` ：要添加的标签键值；
- `includeTemplates: true` ：把标签加入 Deployment 等工作负载的 Pod Template；
- `includeSelectors: false` ：不把标签加入 Deployment、Service 等资源的 Selector。

构建后，Deployment 自身可能得到：

```yaml
metadata:
  labels:
    environment: test
```

Pod Template 也会得到：

```yaml
spec:
  template:
    metadata:
      labels:
        environment: test
```

这样，Deployment 创建出来的 Pod 也会带有：

```yaml
environment: test
```

可以通过下面的命令查询：

```bash
kubectl get pods -l environment=test
```

为什么示例中将 `includeSelectors` 设置为 `false` ？

因为 Selector 决定资源之间的匹配关系，例如：

- Deployment 通过 Selector 管理 Pod；
- Service 通过 Selector 选择后端 Pod。

环境、版本、发布批次等标签可能会发生变化，不适合随意加入已经存在资源的 Selector。尤其是 Deployment 的 Selector 创建后不能随意修改，否则可能导致资源更新失败。

因此，对于 `environment: test` 这类环境标识，通常可以加入资源和 Pod Template，但不必加入 Selector。

### 6. patches：修改其他复杂字段

`namespace` 、 `images` 、 `replicas` 等字段，适合处理常见且结构比较固定的修改。

如果需要修改以下内容：

- CPU 和内存 Requests、Limits；
- 环境变量；
- 探针；
- 节点选择器；
- 亲和性；
- 容忍度；
- 滚动更新策略；

通常可以使用 `patches` 。

例如，生产环境需要设置资源限制，可以创建：

```text
overlays/prod/deployment-resources-patch.yaml
```

内容如下：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kustomize-demo
spec:
  template:
    spec:
      containers:
        - name: nginx
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

然后在生产环境的 `kustomization.yaml` 中引用：

```yaml
patches:
  - path: deployment-resources-patch.yaml
```

Kustomize 会找到名为 `kustomize-demo` 的 Deployment，并把补丁中的资源配置合并进去。

对于目标较多或者需要精确选择资源的场景，还可以显式指定 `target` ：

```yaml
patches:
  - path: deployment-resources-patch.yaml
    target:
      group: apps
      version: v1
      kind: Deployment
      name: kustomize-demo
```

初学阶段不需要一次掌握所有补丁格式，只需要先记住：

> 常见差异优先使用 `images` 、 `replicas` 等专用字段，其他复杂差异再使用 `patches` 。

Kubernetes 官方文档还建议，一个补丁最好只完成一类修改。例如，副本数和内存限制可以分别使用两个小补丁，这样更容易阅读、审查和复用。

## 六、Kustomize 最终生成了什么

Kustomize 最终输出的不是特殊格式，而是一组普通 Kubernetes YAML。

假设测试环境配置位于：

```text
overlays/test/
```

可以使用下面的命令构建：

```bash
kubectl kustomize overlays/test
```

这个命令会：

1. 找到 `overlays/test/kustomization.yaml` ；
2. 读取其中的 `resources` ；
3. 构建引用的 Base；
4. 应用 `namespace` 、 `images` 、 `replicas` 、 `labels` 和 `patches` ；
5. 把最终 Kubernetes YAML 输出到终端。

它不会在集群中创建任何资源。

如果想查看构建结果与集群当前资源的差异，可以执行：

```bash
kubectl diff -k overlays/test
```

如果确认结果没有问题，再执行：

```bash
kubectl apply -k overlays/test
```

可以把这三个命令记成：

```bash
kubectl kustomize = 生成并查看
kubectl diff -k    = 比较差异
kubectl apply -k   = 构建并部署
```

还需要区分 `-f` 和 `-k` ：

```bash
kubectl apply -f deployment.yaml
```

`-f` 表示直接读取 Kubernetes 资源文件。

```bash
kubectl apply -k overlays/test
```

`-k` 表示先构建包含 `kustomization.yaml` 的目录，再应用生成的资源。

根据 Kubernetes 官方命令参考， `kubectl kustomize` 的参数应该是包含 `kustomization.yaml` 的目录，或者符合要求的远程 Git 地址。

## 七、初学 Kustomize 应该记住的三个原则

### 1. Base 只保存真正公共的配置

Base 中适合保存：

- Deployment、Service 的基本结构；
- 稳定的资源名称；
- 稳定的应用标签和 Selector；
- 容器端口；
- 健康检查；
- 公共的 Volume 配置。

不要把明显属于某个环境的配置强行放进 Base。

### 2. Overlay 只描述环境差异

Overlay 中适合保存：

- Namespace；
- 镜像仓库和镜像版本；
- 副本数；
- 环境标签；
- CPU、内存资源限制；
- 环境变量；
- 节点调度规则。

如果 Test Overlay 和 Prod Overlay 中出现了大量完全相同的内容，通常说明这些内容可能应该上移到 Base。

### 3. 部署前先检查构建结果

推荐按照下面的顺序操作：

```bash
kubectl kustomize overlays/test
kubectl diff -k overlays/test
kubectl apply -k overlays/test
```

先确认 Kustomize 最终生成了什么，再把配置应用到集群。

## 八、版本和字段使用说明

本文使用的是当前推荐写法：

- 使用 `resources` ，不使用已经弃用的 `bases` ；
- 使用 `labels` ，不使用已经弃用的 `commonLabels` ；
- 使用 `patches` ，不使用已经弃用的 `patchesStrategicMerge` ；
- 使用 `patches` ，不使用已经弃用的 `patchesJson6902` 。

这些旧字段可能仍然可以在部分版本中运行，但新项目应优先使用当前推荐字段。

另外， `kubectl` 内置的 Kustomize 与独立安装的 Kustomize 可能不是同一个版本。可以通过下面的命令查看当前客户端信息：

```bash
kubectl version --client
```

遇到某个字段无法识别时，应先确认当前 `kubectl` 内置的 Kustomize 版本是否支持该字段。

## 九、总结

Kustomize 的核心并不是简单地减少 YAML 行数，而是把 Kubernetes 配置拆分成两个部分：

```text
Base    = 多个环境共同使用的公共配置
Overlay = 不同环境之间的配置差异
```

然后通过 `kustomization.yaml` 告诉 Kustomize：

```text
resources  = 读取哪些资源
namespace  = 资源属于哪个命名空间
images     = 使用哪个镜像
replicas   = 运行多少个副本
labels     = 添加哪些标签
patches    = 修改哪些复杂字段
```

最终再通过：

```bash
kubectl kustomize overlays/test
```

生成普通的 Kubernetes YAML。

一句话总结：

> Kustomize 通过 Base 复用公共配置，通过 Overlay 描述环境差异，在不修改原始 YAML 的情况下生成测试、生产等环境的最终 Kubernetes 配置。

## 相关阅读

- [[Docker-Kubernetes/k8s-CICD/Kustomize/k8s配置定制工具-kustomize|K8s 配置定制工具 Kustomize]]：覆盖 Kustomize 基础用法、生成器与更多进阶特性；其中部分旧字段应结合本文的版本说明辨别。
- [[KnowledgeBase/entities/Kustomize|Kustomize 实体页]]
