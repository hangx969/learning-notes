---
title: Helm部署VPA
tags:
  - kubernetes
  - scaling
  - vpa
aliases:
  - vpa垂直扩缩容
---

# 介绍

VPA可以让用户无需手动设置resource request，VPA会帮助检测并且自动设置合理的request。

VPA helm chart默认包含三个组件：Updater、Admission Controller、Recommender，工作原理如下：

![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202502141049924.png)

VPA有两种安装方式：

1. 手动下载安装脚本安装：[VPA Installation](https://github.com/kubernetes/autoscaler/blob/master/vertical-pod-autoscaler/docs/installation.md)

2. 通过Fairwinds helm chart部署：[Fairwinds VPA Chart](https://github.com/FairwindsOps/charts/tree/master/stable/vpa)

这里通过helm chart方式部署。

helm chart版本发布：

- release page: [Autoscaler Releases](https://github.com/kubernetes/autoscaler/releases)
- artifact hub: [vpa helm chart](https://artifacthub.io/packages/helm/fairwinds-stable/vpa)

# 下载

- 下载helm chart

~~~sh
helm repo add fairwinds-stable https://charts.fairwinds.com/stable
helm repo update fairwinds-stable
helm pull fairwinds-stable/vpa --version 4.7.1
~~~

# 配置

- prerequisites

  注意VPA必须要求metrics server已经安装：[VPA Prerequisites](https://github.com/kubernetes/autoscaler/blob/master/vertical-pod-autoscaler/docs/installation.md#prerequisites)

- values文件

~~~yaml
recommender:
  # recommender.enabled -- If true, the vpa recommender component will be installed.
  enabled: true

admissionController:
  # admissionController.enabled -- If true, will install the admission-controller component of vpa
  enabled: false

# metrics-server -- configuration options for the [metrics server Helm chart](https://github.com/kubernetes-sigs/metrics-server/tree/master/charts/metrics-server). See the projects [README.md](https://github.com/kubernetes-sigs/metrics-server/tree/master/charts/metrics-server#configuration) for all available options
metrics-server:
  # metrics-server.enabled -- Whether or not the metrics server Helm chart should be installed
  enabled: true
  args:
  - --kubelet-insecure-tls
~~~

# 安装

~~~sh
helm upgrade -i vpa fairwinds-stable/vpa \
--namespace vpa \
--history-max 3 \
--set admissionController.enabled=false \   
--set recommender.enabled=true \
~~~

# troubleshooting

对于kubeadm安装的集群，vpa自带的sub-chart安装的metrics-server pod起不来，报错：

> "Failed to scrape node" err="Get \"https://172.16.183.100:10250/metrics/resource\": dial tcp 172.16.183.100:10250: connect: no route to host" node="rm1"

这个问题在github issue上有讨论：[metrics-server#196](https://github.com/kubernetes-sigs/metrics-server/issues/196)

问题原因如[kubernetes官网](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/#kubelet-serving-certs)所述：

> By default the kubelet serving certificate deployed by kubeadm is self-signed. This means a connection from external services like the [metrics-server](https://github.com/kubernetes-sigs/metrics-server) to a kubelet cannot be secured with TLS.

解决方案有两个：

1. 临时方案：给metrics-server pod加参数`--kubelet-insecure-tls`，绕过TLS证书检测。这种方案不安全，不适用于生产环境                                               
   - 如果采用这种方案，helm values中需要配置args传给metrics-server pod，vpa的metrics-server sub-chart配置中也可以实现。（如上配置）
   - 也可以先独立部署一个metrics-server，配置好args参数`--kubelet-insecure-tls`。
2. 终极方案：配置kubelet，将self-signed证书更换为API server CA签发的证书
   - 按照[kubernetes官网](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/#kubelet-serving-certs)教程来做，这种方式默认情况下需要手动运行命令来approve CSR，而且一年过期一次，过期后都要手动去重新approve CSR。（这也是为什么这个选项不是kubeadm安装的默认值）
   - 官网也给了一个三方工具可以自动对CSR做批准

# helm安装metrics-server

- github链接：[kubernetes-sigs/metrics-server](https://github.com/kubernetes-sigs/metrics-server)
- 安装指南：[metrics-server helm chart](https://artifacthub.io/packages/helm/metrics-server/metrics-server)
- 注意metrics-server仅被用作HPA和VPA的CPU/Memory自动监测的用途，不支持用作获取准确监控数据的用途

## 下载

~~~sh
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm pull metrics-server/metrics-server --version 3.12.2
~~~

## 配置

~~~yaml
args:
  - --kubelet-insecure-tls
~~~

## 安装

~~~sh
helm upgrade --install metrics-server . -f values.yaml
~~~

# 使用

[VPA Quick Start](https://github.com/kubernetes/autoscaler/blob/master/vertical-pod-autoscaler/docs/quickstart.md#quick-start)

- VPA helm chart部署好之后，需要手动创建VerticalPodAutoscaler资源来监控指定的container。例如：

  ~~~yaml
  apiVersion: autoscaling.k8s.io/v1beta2
  kind: VerticalPodAutoscaler
  metadata:
    name: nginx-vpa
    namespace: vpa
  spec:
    targetRef:
      apiVersion: "apps/v1"
      kind: Deployment
      name: nginx
    updatePolicy:
      updateMode: "Off" #仅获取推荐值，不更新pod
    resourcePolicy:
      containerPolicies:
      - containerName: "nginx"
        minAllowed: #Specifies the minimal amount of resources that will be recommended for the container. The default is no minimum.
          cpu: "500m"
          memory: "100Mi"
        maxAllowed:
          cpu: "2000m"
          memory: "2600Mi"
  ~~~

- 安装了goldilock之后，goldilock可以自动生成vpa资源，UI dashboard显示推荐值

> [!warning] 注意vpa的update不会去更改deployment的template里面的值，而是去更改pod的request

## demo pod

- [Test Your Installation](https://github.com/kubernetes/autoscaler/blob/master/vertical-pod-autoscaler/docs/quickstart.md#test-your-installation)：vpa github提供了一个示例deployment来测试vpa是否正常工作
- 这个deployment设置了pod request cpu是100m，但是实际pod会用到500m以上，过几分钟之后就会看到pod被删掉重新创建了，request cpu的值被改到600m多

```yaml
# This config creates a deployment with two pods, each requesting 100 millicores
# and trying to utilize slightly above 500 millicores (repeatedly using CPU for
# 0.5s and sleeping 0.5s).
# It also creates a corresponding Vertical Pod Autoscaler that adjusts the
# requests.
# Note that the update mode is left unset, so it defaults to "Auto" mode.
---
apiVersion: "autoscaling.k8s.io/v1"
kind: VerticalPodAutoscaler
metadata:
  name: hamster-vpa
spec:
  # recommenders field can be unset when using the default recommender.
  # When using an alternative recommender, the alternative recommender's name
  # can be specified as the following in a list.
  # recommenders: 
  #   - name: 'alternative'
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: hamster
  resourcePolicy:
    containerPolicies:
      - containerName: '*'
        minAllowed:
          cpu: 100m
          memory: 50Mi
        maxAllowed:
          cpu: 1
          memory: 500Mi
        controlledResources: ["cpu", "memory"]
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hamster
spec:
  selector:
    matchLabels:
      app: hamster
  replicas: 2
  template:
    metadata:
      labels:
        app: hamster
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 65534 # nobody
      containers:
        - name: hamster
          image: registry.k8s.io/ubuntu-slim:0.14
          resources:
            requests:
              cpu: 100m
              memory: 50Mi
          command: ["/bin/sh"]
          args:
            - "-c"
            - "while true; do timeout 0.5s yes >/dev/null; sleep 0.5s; done"
~~~

---

# VPA 深入：四种模式、推荐算法与 HPA 共存

> 来源：[K8s VPA 垂直自动扩缩容：你真的会用吗？](https://mp.weixin.qq.com/s/FfNIwJJrF9XpBSZMNcffag)

## 四种 updateMode 对比

| Mode | 行为 | 适用场景 |
| --- | --- | --- |
| `Off` | 只生成推荐，不做任何修改 | 先观察，收集数据 |
| `Initial` | 只在 Pod 首次创建时注入推荐值 | 稳定服务，减少驱逐 |
| `Auto` | 自动注入 + 驱逐过期 Pod | 接受一定重启的服务 |
| `Recreate` | 强制驱逐并用新推荐值重建 | 需要立即生效（少用） |

**生产建议**：先用 `Off` 模式跑 1-2 周收集推荐值，然后切换到 `Initial` 稳定运行。核心服务不要用 `Auto` 或 `Recreate`，因为会触发 Pod 重启影响可用性。

## VPA 推荐值算法

VPA Recommender 使用**指数衰减直方图**算法对历史 CPU/Memory 使用量建模：

- **CPU 推荐**：基于使用量分布的第 95 百分位（P95），不是平均值
- **Memory 推荐**：基于最近一段时间的内存使用高水位
- **历史窗口**：默认采集过去 8 天的数据（可通过 `--history-length` 调整）
- **衰减因子**：越近的数据权重越高（近期流量特征更重要）

注意：
- 如果服务有周期性业务高峰（每周一峰值），VPA 会把这个峰值纳入推荐
- 如果刚上线没多少历史数据，推荐值可能偏低，需要等 1-2 周

## VPA 与 HPA 共存

**不能同时对同一资源（CPU/Memory）使用 VPA Auto/Recreate + HPA based on CPU/Memory**，会造成控制器互相打架。

正确的共存方案：

```
方案1：VPA Off 模式 + HPA（VPA 只做参考，人工调整 requests）
方案2：VPA 管 Memory + HPA 管 CPU 水平扩容（分离控制维度）
方案3：KEDA 基于自定义指标 HPA + VPA Off 模式推荐
```

配置示例（VPA 只管内存，HPA 只管 CPU 水平扩容）：

~~~yaml
# VPA：只控制 Memory
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: my-app
      controlledResources: ["memory"]   # 只控制内存
      minAllowed:
        memory: 128Mi
      maxAllowed:
        memory: 4Gi
---
# HPA：只基于 CPU 水平扩
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
~~~

## VPA 驱逐风险与缓解

VPA `Auto`/`Recreate` 模式会主动 evict Pod，这是最大风险。缓解措施：

1. **配合 PDB 限制最大驱逐数**：

~~~yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
spec:
  maxUnavailable: 1      # 同时只允许 1 个 Pod 不可用
  selector:
    matchLabels:
      app: my-app
~~~

2. **设置合理的 minAllowed/maxAllowed 缩小触发范围**
3. **生产核心服务建议使用 `Initial` 模式**，只在 Pod 重建（滚动升级/节点迁移）时才注入新推荐值

## VPA 监控

使用 Prometheus + Grafana 监控 VPA：

~~~bash
# VPA 关键指标（vpa-recommender 暴露）
vpa_recommender_memory_usage            # Recommender 自身内存使用
vpa_recommender_cpu_usage               # Recommender CPU 使用
vpa_recommender_recommendations_total   # 总推荐次数

# 定期导出推荐值差异
kubectl get vpa -A -o json | jq '.items[] | {
  name: .metadata.name,
  namespace: .metadata.namespace,
  target: .status.recommendation.containerRecommendations[0].target
}'
~~~

Grafana Dashboard ID: **14588**

> **总结**：1）先用 `Off` 模式收集推荐数据；2）核心服务用 `Initial` 减少驱逐影响；3）与 HPA 共存时分离控制维度（VPA 管内存，HPA 管 CPU）；4）始终配合 PDB 保障可用性。

