# 临时容器

在Kubernetes中，Ephemeral容器（临时容器）是一种特殊类型的容器，它是为了在正在运行的Pod中临时执行诊断和调试操作而设计的。临时容器可以在Pod的生命周期中的任何时刻被添加，而无需重新启动Pod或改变现有容器的定义。

## 特点

1. **动态添加**：Ephemeral容器可以动态添加到已经运行的Pod中，这可以让运维人员或开发人员在不干扰Pod正常运行的情况下，进行故障排查或性能分析。
2. **不包含在Pod规范中**：临时容器不像Pod中的其他常规容器，不会在Pod的初始规范中定义。它们是临时添加的，通常在需要时通过kubectl工具注入。临时容器没有端口配置，因此像 ports，livenessProbe，readinessProbe 这样的字段是不允许的。Pod 资源分配是不可变的，因此 resources 配置是不允许的。临时容器是使用 API 中的一种特殊的 ephemeralcontainers 处理器进行创建的， 而不是直接添加到 pod.spec 段，因此无法使用 kubectl edit 来添加一个临时容器，也无法通过yaml文件创建临时容器。
3. **隔离与安全**：尽管临时容器可以访问Pod的所有资源和网络，但它们的运行和存在不会对Pod的安全性配置或其它运行容器产生影响。

## 使用场景

- **调试**：如果一个Pod出现问题，可以kubectl动态添加一个临时容器来执行调试工具，而不必修改原有容器的设置。当由于容器崩溃，或主容器镜像中不包含调试程序（比如shell）而导致 kubectl exec进不去主容器时，临时容器对于交互式故障排查很有用。
- **监控和诊断**：加入一个临时容器来收集运行信息，进行性能监控或日志收集。
- **安全审查**：动态注入临时容器来执行安全扫描或审计任务。

## 示例

假设你想为一个正在运行的Pod添加一个临时容器进行网络诊断。可以使用以下kubectl命令来实现：

```bash
kubectl debug [POD_NAME] -it --image=busybox --target=[POD_NAME]
```

这条命令会向指定的Pod添加一个以busybox镜像运行的临时容器，并提供交互式终端。

> - 官方文档：[Ephemeral Containers | Kubernetes](https://kubernetes.io/docs/concepts/workloads/pods/ephemeral-containers/)
> - 教程示例：https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/#ephemeral-container
> - 临时容器在1.25版本开始变成stable

# 开启临时容器功能

- 修改kube-apiserver配置

~~~sh
vim /etc/kubernetes/manifests/kube-apiserver.yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    kubeadm.kubernetes.io/kube-apiserver.advertise-address.endpoint: 192.168.40.180:6443
  creationTimestamp: null
  labels:
    component: kube-apiserver
    tier: control-plane
  name: kube-apiserver
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-apiserver
    - --advertise-address=192.168.40.180
    #......
    - --feature-gates=RemoveSelfLink=false
    - --feature-gates=EphemeralContainers=true
#新增加--feature-gates=EphemeralContainers=true字段
~~~

- 修改kube-scheduler配置

~~~sh
vim /etc/kubernetes/manifests/kube-scheduler.yaml
apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
  labels:
    component: kube-scheduler
    tier: control-plane
  name: kube-scheduler
  namespace: kube-system
spec:
  containers:
  - command:
    - kube-scheduler
    - --authentication-kubeconfig=/etc/kubernetes/scheduler.conf
    - --authorization-kubeconfig=/etc/kubernetes/scheduler.conf
    - --bind-address=192.168.40.180
    - --kubeconfig=/etc/kubernetes/scheduler.conf
    - --leader-elect=true
    - --feature-gates=EphemeralContainers=true
#新增加--feature-gates=EphemeralContainers=true字段
~~~

- 修改kubelet配置

~~~sh
#master和node上都要改
vim /etc/sysconfig/kubelet 
KUBELET_EXTRA_ARGS="--feature-gates=EphemeralContainers=true"
~~~

- 重启控制节点和工作节点的kubelet

~~~sh
systemctl restart kubelet
kubectl get pods -n kube-system #检查pod正常工作
~~~

> 重启apiserver会影响业务，最好集群创建完就配置上；或者配置高可用master节点

# 使用临时容器

- 创建主pod

~~~yaml
tee pod-tomcat.yaml <<'EOF' 
apiVersion: v1
kind: Pod
metadata:
  name: tomcat-test
  namespace: default
  labels:
    app:  tomcat
spec:
  containers:
  - name:  tomcat-java
    image: tomcat-8.5-jre8:v1
    imagePullPolicy: IfNotPresent
    ports:
    - containerPort: 8080
EOF
kubectl apply -f pod-tomcat.yaml
~~~

- kubectl debug注入临时容器

~~~sh
kubectl debug -it tomcat-test --image=busybox --target=tomcat-java
#通过临时容器查看tomcat主容器信息
ps -ef | grep tomcat
#查看pod yaml中是否注入了临时容器
kubectl describe pods tomcat-test 
Ephemeral Containers:
  debugger-lhdc8:
    Container ID:   docker://e005a0bbd9020107585e8742fb8442c21d32a5365df6fa49bdf2ef48bab6b009
    Image:          busybox
    Image ID:       docker-pullable://busybox@sha256:5acba83a746c7608ed544dc1533b87c737a0b0fb730301639a0179f9344b1678
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Sun, 19 May 2024 09:23:39 -0400
    Ready:          False
    Restart Count:  0
    Environment:    <none>
    Mounts:         <none>
~~~

- 通过kubectl raw注入临时容器

~~~sh
kubectl delete -f pod-tomcat.yaml
kubectl apply -f pod-tomcat.yaml
tee a.json <<'EOF' 
{
    "apiVersion": "v1",
    "kind": "EphemeralContainers",
    "metadata": {
            "name": "tomcat-test"
    },
    "ephemeralContainers": [{
        "command": [
            "sh"
        ],
        "image": "busybox",
        "imagePullPolicy": "IfNotPresent",
        "name": "debugger",
        "stdin": true,
        "tty": true,
        "targetContainerName": "tomcat-java",
        "terminationMessagePolicy": "File"
    }]
}

EOF

kubectl replace --raw /api/v1/namespaces/default/pods/tomcat-test/ephemeralcontainers -f a.json
#通过attach连接到临时容器
kubectl attach -it -c debugger tomcat-test
#调试完成退出临时容器之后，这个容器会被销毁，无法再次attach
~~~

> - kubectl replace --raw /api/v1/namespaces/default/pods/tomcat-test/ephemeralcontainers -f a.json
> - 报错：Error from server (BadRequest): EphemeralContainers in version "v1" cannot be handled as a Pod: no kind "EphemeralContainers" is registered for version "v1" in scheme "k8s.io/kubernetes/pkg/api/legacyscheme/scheme.go:30" 
>
> ~~~sh
> kubectl get api-versions #查看支持的所有api
> #里面有v1版本
> #查看v1版本里面具体有哪些资源
> kubectl api-resources --api-group=""
> #查看apps/v1版本里面具体有哪些资源
> kubectl api-resources --api-group=apps
> #都没有看到ephemeralcontainers资源
> ~~~
>
> - k8s官网上都没有给出这种上传json的方法，暂时不搞这种方法了。

## 示例-AKS pod添加azcli debug容器

- 有时AKS中的pod与azure交互出现问题需要排查，我们可以在pod上attach一个azcli的debug容器

- 获取azure官方azcli容器：https://learn.microsoft.com/zh-cn/cli/azure/run-azure-cli-docker#run-the-docker-container-with-a-specific-version-of-the-azure-cli

~~~sh
#镜像上传到ACR
z acr import --name "<acr name>.azurecr.cn" --source mcr.microsoft.com/azure-cli:2.65.0-cbl-mariner2.0 --image azure-cli:2.65.0-cbl-mariner2.0

#attach debug容器
kubectl debug -it <pod name> -n <ns name> --image=<acr name>/azure-cli:2.66.0-cbl-mariner2.0 --target=<container name>
~~~

# 问题

- 目前临时容器存在一个bug：

  在pod中添加临时容器之后，目前还无法删除，同时如果这时候临时容器已经退出，会导致无法再次attach，也不会被重启（临时容器不支持probe什么的），相关的issue：https://github.com/kubernetes/kubernetes/issues/84764

- 此时，如果要重复上述步骤再次进行调试，需要用新name创建一个新的临时容器，保留原有的配置，否则k8s会拒绝新的配置。

  ~~~sh
  tee a.json <<'EOF'
  {
      "apiVersion": "v1",
      "kind": "EphemeralContainers",
      "metadata": {
              "name": "tomcat-test"
      },
      "ephemeralContainers": [
     {
          "command": [
              "sh"
          ],
          "image": "busybox",
          "imagePullPolicy": "IfNotPresent",
          "name": "debugger",
          "stdin": true,
          "tty": true,
          "targetContainerName": "tomcat-java",
          "terminationMessagePolicy": "File"
      },
        {"command": [
              "sh"
          ],
          "image": "busybox",
          "imagePullPolicy": "IfNotPresent",
          "name": "debugger1",
          "stdin": true,
          "tty": true,
          "targetContainerName": "tomcat-java",
          "terminationMessagePolicy": "File"
      }
  ]
  }
  EOF
  
  kubectl replace --raw /api/v1/namespaces/default/pods/tomcat-test/ephemeralcontainers -f a.json
  ~~~

  
