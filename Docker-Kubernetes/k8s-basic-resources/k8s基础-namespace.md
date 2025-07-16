# namespace介绍

- Namespace提供了一种将集群资源逻辑上隔离的方式，允许在同一个集群中划分多个虚拟的、逻辑上独立的集群环境，相当于集群的“虚拟化”。

- 命名空间namespace是k8s集群级别的资源，可以给不同的用户、租户、环境或项目创建对应的命名空间，例如，可以为test、devlopment、production环境分别创建各自的命名空间。

# namespace应用场景

命名空间适用于存在很多跨多个团队或项目的用户的场景。对于只有几到几十个用户的集群，根本不需要创建或考虑命名空间。

# 创建

```bash
kubectl create ns test
```

# 资源限额

```yaml
#给某个namespace下的资源做限制
vim namespace-quota.yaml

apiVersion: v1
kind: ResourceQuota
metadata:
  name: mem-cpu-quota
  namespace: test
spec:
  hard:
    requests.cpu: 2
    requests.memory: 2Gi # k8s会根据请求的资源量来决定调度到哪个node上。
    limits.cpu: 4
    limits.memory: 4Gi
```

> CPU的单位解释：[为 Pod 和容器管理资源 | Kubernetes](https://kubernetes.io/zh-cn/docs/concepts/configuration/manage-resources-containers/)
>
> CPU 资源的限制和请求以 “cpu” 为单位。 在 Kubernetes 中，一个 CPU 等于 **1 个物理 CPU 核** 或者 **1 个虚拟核**， 取决于节点是一台物理主机还是运行在某物理主机上的虚拟机。
>
> - 如果是request.cpu: 0.5 --> 那就是请求0.5个核
> - 如果是request.cpu: 500m --> 那是500毫核 --> 也就是0.5核

# ns删除后卡在terminating状态

- 需要手动结束finalizer

~~~sh
# 开启代理
kubectl proxy
# Starting to serve on 127.0.0.1:8001
# 新开终端
kubectl get namespace $NAMESPACE -o json > temp.json
# 编辑状态文件
vim temp.json
# 删掉以下三行：
"finalizers": [
   "controller.cattle.io/namespace-auth"
],
# 发送状态文件
curl -k -H "Content-Type: application/json" -X PUT --data-binary @temp.json 127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize
~~~

不推荐，还是建议先回收其中的资源再删除ns。

# 特殊namespace

## kube-node-lease

- 节点的心跳信息会存放在其中，api server去里面查看心跳信息，获取node状态。
