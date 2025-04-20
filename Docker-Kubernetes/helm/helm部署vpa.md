# 介绍

VPA可以让用户无需手动设置resource request，VPA会帮助检测并且自动设置合理的request。

VPA helm chart默认包含三个组件：Updater、Admission Controller、Recommender，工作原理如下：

![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202502141049924.png)

VPA有两种安装方式：

1. 手动下载安装脚本安装：https://github.com/kubernetes/autoscaler/blob/master/vertical-pod-autoscaler/docs/installation.md

2. 通过Fairwinds helm chart部署：https://github.com/FairwindsOps/charts/tree/master/stable/vpa

这里通过helm chart方式部署。

- release page: https://github.com/kubernetes/autoscaler/releases
- artifact hub: https://artifacthub.io/packages/helm/fairwinds-stable/vpa

# 下载

- 下载helm chart

~~~sh
helm repo add fairwinds-stable https://charts.fairwinds.com/stable
helm repo update fairwinds-stable
helm pull fairwinds-stable/vpa --version 4.7.1
~~~

# 配置

- prerequisites

  注意VPA必须要求metrics server已经安装：https://github.com/kubernetes/autoscaler/blob/master/vertical-pod-autoscaler/docs/installation.md#prerequisites

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

这个问题在github issue上有讨论：https://github.com/kubernetes-sigs/metrics-server/issues/196

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

- github链接：https://github.com/kubernetes-sigs/metrics-server
- 安装指南：https://artifacthub.io/packages/helm/metrics-server/metrics-server
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
