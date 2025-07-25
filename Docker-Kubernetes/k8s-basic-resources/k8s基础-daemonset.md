# DaemonSet控制器：概念、原理

## 概念

- DaemonSet控制器能够确保k8s集群所有的节点都运行一个相同的pod副本，当向k8s集群中增加node节点时，这个node节点也会自动创建一个pod副本，当node节点从集群移除，这些pod也会自动删除；删除Daemonset也会删除它们创建的pod。

## 原理

- daemonset的控制器会监听kuberntes的daemonset对象、pod对象、node对象，这些被监听的对象之变动，就会触发syncLoop循环让kubernetes集群朝着daemonset对象描述的状态进行演进。

## 场景

- 在集群的每个节点上运行存储，比如：glusterd 或 ceph。
- 在每个节点上运行日志收集组件，比如：flunentd、logstash、filebeat等。
- 在每个节点上运行监控组件，比如：Prometheus、Node Exporter、collectd等。

# 示例：ds部署fluentd

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: ds-test
  namespace: default
  labels:
    app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane # 容忍master的污点
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: fluentd:v2.5.1
        imagePullPolicy: IfNotPresent
        resources: 
          requests: 
            cpu: 100m
            memory: 200Mi
          limits: 
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
      volumes:
      - name: varlog # 挂载系统日志
        hostPath:
          path: /var/log
      - name: varlibdockercontainers # 挂载容器日志
        hostPath:
          path: /var/lib/docker/containers
```

> ds和deployment yaml文件的区别：
>
> 1. kind变成daemonSet
> 2. replicaCount删除了

# 指定节点部署

~~~yaml
# 如果指定了.spec.template.spec.nodeSelector，DaemonSet Controller 将在与 Node Selector 匹配的节点上创建 Pod
# 比如部署在磁盘类型为 ssd 的节点上（需要提前给节点定义标签 Label）：
nodeSelector:
  disktype: ssd
# 比如调度到GPU节点上
nodeSelector:
  gpu: "true" # 注意布尔值需要设成字符串
~~~

> 如果添加了新节点或修改了节点标签（Label），DaemonSet 将立刻向新匹配上的节点添加Pod，同时删除不能匹配的节点上的 Pod。

# ds滚动更新

```bash
kubectl explain ds.spec.updateStrategy.rollingUpdate
```

1. **maxUnavailable（最大不可用）：**定义了在滚动更新期间可以同时不可用的 Pods 的最大数量。例如，如果 `maxUnavailable` 设置为 1，那么在任何给定时间内，最多只能有一个 Pod 不可用。这有助于确保在更新期间保持一定的可用性。

2. **maxSurge（最大增长）：** 它定义了在滚动更新期间可以同时创建的新 Pods 的最大数量。这个参数允许你一次性引入一定数量的新 Pods，以加速更新过程，同时仍然受到 `maxUnavailable` 的限制，确保不会一次性影响太多的旧 Pods。

   > 注意：只有maxUnavailable为0的时候，才允许设置maxSurge的值

3. **逐步替换：** DaemonSet 滚动更新通过逐步替换的方式进行，首先在节点上启动新的 Pod，然后停止旧的 Pod。这样可以确保在更新的过程中，每个节点都保持有一个 Pod 在运行。

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: ds-test
  namespace: default
  labels:
    app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd-elasticsearch
  updateStrategy:
    type: RollingUpdate
    rollingUpdate: 
      maxSurge: 1 # maxSurge是1代表更新过程中最多同时有1个node上的ds pod在更新
      maxUnavailable: 0 # 代表最多同时停掉几个node上的ds，起新的ds。设成0就代表最多
  template:
    metadata:
      labels:
        name: fluentd-elasticsearch
    spec:
      tolerations:
      - key: node-role.kubernetes.io/control-plane #容忍控制节点的污点
        effect: NoSchedule
      containers:
      - name: fluentd-elasticsearch
        image: centos #xianchao/fluentd:v2.5.1
        imagePullPolicy: IfNotPresent
        resources: 
          requests: 
            cpu: 100m
            memory: 200Mi
          limits: 
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
      volumes:
      - name: varlog # 挂载系统日志
        hostPath:
          path: /var/log
      - name: varlibdockercontainers # 挂载容器日志
        hostPath:
          path: /var/lib/docker/containers
```

# ds回滚

```bash
# 查看更新状态
kubectl rollout status ds/ds-test
# 查看更新历史版本
kubectl rollout history ds ds-test
# 回滚到历史版本
kubectl rollout undo ds ds-test --to-revision=1 
```

