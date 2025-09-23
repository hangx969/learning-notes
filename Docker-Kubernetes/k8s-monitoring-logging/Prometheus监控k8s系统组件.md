# 监控etcd-手动创建yaml

## etcd的metrics接口

Etcd原生提供了Metrics接口，所以无需任何服务就可以直接监控Etcd。但是访问Etcd的Metrics接口需要使用证书，如下所示：

~~~sh
curl -s --cert /etc/kubernetes/pki/etcd/server.crt --key /etc/kubernetes/pki/etcd/server.key https://192.168.40.180:2379/metrics -k | tail -1
~~~

etcd的证书路径在哪里看？

~~~sh
cat /etc/kubernetes/manifests/etcd.yaml
# command下面
#     - --cert-file=/etc/kubernetes/pki/etcd/server.crt
#     - --key-file=/etc/kubernetes/pki/etcd/server.key
# 	  - --trusted-ca-file=/etc/kubernetes/pki/etcd/ca.crt
~~~

## etcd的svc

默认没有创建etcd的svc，给他创建一个。将endpoint的IP换成etcd的pod IP

~~~yaml
apiVersion: v1 
kind: Endpoints 
metadata:
  name: etcd-prom 
  namespace: kube-system 
  labels: 
    app: etcd-prom 
subsets: 
- addresses: 
  - ip: 192.168.40.180
  ports: 
  - name: https-metrics 
    port: 2379 # etcd端口 
    protocol: TCP 
--- 
apiVersion: v1 
kind: Service 
metadata: 
  name: etcd-prom 
  namespace: kube-system
  labels: 
    app: etcd-prom 
spec: 
  type: ClusterIP
  ports: 
  - name: https-metrics 
    port: 2379 
    protocol: TCP 
    targetPort: 2379 
~~~

访问svc clusterIP测试：

~~~sh
curl -s --cert /etc/kubernetes/pki/etcd/server.crt --key /etc/kubernetes/pki/etcd/server.key https://10.104.93.132:2379/metrics -k
~~~

## 创建secret并挂载

创建Etcd证书的Secret（证书路径根据实际环境进行更改）：

~~~sh
kubectl create secret generic etcd-ssl -n monitoring --from-file=/etc/kubernetes/pki/etcd/ca.crt --from-file=/etc/kubernetes/pki/etcd/server.key --from-file=/etc/kubernetes/pki/etcd/server.crt
~~~

接下来将证书挂载至Prometheus容器（如果Prometheus是Operator部署的，所以只需要修改Prometheus资源即可；helm chart部署的，就去values里面改prometheus的挂载）：

~~~yaml
prometheus:
...
  prometheusSpec:
  ...
    ## Secrets is a list of Secrets in the same namespace as the Prometheus object, which shall be mounted into the Prometheus Pods.
    ## The Secrets are mounted into /etc/prometheus/secrets/. Secrets changes after initial creation of a Prometheus object are not
    ## reflected in the running Pods. To change the secrets mounted into the Prometheus Pods, the object must be deleted and recreated
    ## with the new list of secrets.
    ##
    secrets:
    - etcd-ssl # 挂载etcd的证书，用于获取etcd metrics数据
~~~

## 创建serviceMonitor

~~~yaml
apiVersion: monitoring.coreos.com/v1 
kind: ServiceMonitor 
metadata: 
  name: etcd 
  namespace: monitoring 
  labels: 
    app: etcd 
spec: 
  jobLabel: k8s-app 
  endpoints: 
  - interval: 30s 
    port: https-metrics # 这个port对应 Service.spec.ports.name 
    scheme: https 
    tlsConfig: 
      caFile: /etc/prometheus/secrets/etcd-ssl/ca.crt #证书路径 
      certFile: /etc/prometheus/secrets/etcd-ssl/server.crt 
      keyFile: /etc/prometheus/secrets/etcd-ssl/server.key 
      insecureSkipVerify: true # 关闭证书校验 
  selector: 
    matchLabels: 
      app: etcd-prom # 跟svc的labels保持一致 
  namespaceSelector: 
    matchNames: 
    - kube-system
~~~

## 验证

1. 登录prometheus UI去查看target中的etcd是否是up状态。
2. 可以去grafana官网搜索etcd下载对应的dashboard，比如：[Etcd by Prometheus | Grafana Labs](https://grafana.com/grafana/dashboards/3070-etcd/)

## 重点指标

在这个dashboard中有一个指标叫“Disk Sync Duration”：

- WAL fsync: 通常应该 < 10ms （测量将WAL条目从内存刷新到磁盘所需的时间）
- Backend commit: 通常应该 < 25ms （测量将数据库事务提交到磁盘所需的时间）

# 监控etcd-修改vaules

kube-prometheus-stack的values文件里面会自动处理https的metrics接口认证。并且在开启etcd监控之后，会自动安装etcd dashboard。

kube-prometheus-stack的配置如下：

~~~yaml
kubeEtcd:
  enabled: true
  endpoints:
  - 192.168.40.180
  service:
    enabled: true
    port: 2381
    targetPort: 2381
    selector:
      component: etcd
  serviceMonitor:
    enabled: true
    https: true
    insecureSkipVerify: true
    serverName: localhost
    interval: 30s
    metricRelabelings: []
    relabelings: []
~~~

# 监控ControllerManager

## 修改配置

对于kubeadm安装的集群，controller manager默认是绑定--bind-address=127.0.0.1，这样无法通过节点IP访问到，所以要改成0.0.0.0：

~~~sh
vim /etc/kubernetes/manifests/kube-scheduler.yaml
spec:
  containers:
  - command:
    - kube-controller-manager
    - --allocate-node-cidrs=true
    - --authentication-kubeconfig=/etc/kubernetes/controller-manager.conf
    - --authorization-kubeconfig=/etc/kubernetes/controller-manager.conf
    - --bind-address=0.0.0.0
~~~

由于manifests目录下是以静态Pod运行在集群中的，所以只要修改静态Pod目录下对应的yaml文件即可。等待一会后，对应服务会自动重启，所以不需要我们手动重启。

## metrics接口测试

kube-controller-manager通常需要具有适当权限的客户端证书。应该使用admin证书去访问：

~~~sh
curl --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt \
     --key /etc/kubernetes/pki/apiserver-kubelet-client.key \
     --cacert /etc/kubernetes/pki/ca.crt \
     https://192.168.40.180:10257/metrics -k | 
~~~

## 【可选】创建secret

如果是用类似etcd一样，手动创建yaml文件的方式，那么需要把admin证书创建secret并挂载进prometheus

~~~sh
kubectl create secret generic controller-manager-ssl -n monitoring --from-file=/etc/kubernetes/pki/apiserver-kubelet-client.crt --from-file=/etc/kubernetes/pki/apiserver-kubelet-client.key --from-file=/etc/kubernetes/pki/ca.crt
~~~

~~~yaml
prometheus:
  prometheusSpec:
    secrets:
    - etcd-ssl # 挂载etcd的证书，用于获取etcd metrics数据
    - controller-manager-ssl # 挂载controller-manager的证书，用于获取metrics数据
~~~

## 配置prometheus-stack yaml

用helm部署的kube-prometheus-stack，就能自动处理 TLS 配置：通过 https: true 和 insecureSkipVerify: true。不用再

使用内置的证书处理机制：Prometheus operator 会自动使用 ServiceAccount 的证书进行认证

~~~yaml
kubeControllerManager:
  enabled: true
  endpoints:
  - 192.168.40.180
  service:
    enabled: true
    port: 10257
    targetPort: 10257
    selector:
      component: kube-controller-manager
  serviceMonitor:
    enabled: true
    https: true
    insecureSkipVerify: true
    serverName: localhost
    interval: 30s
    metricRelabelings: []
    relabelings: []
~~~

## 查看dashboard

在kube-prometheus-stack中有自带的dashboard：Kubernetes / Controller Manager，需要在开启kubeControllerManager.enabled=true之后才会被创建。

# 监控Scheduler

## 修改监听配置

对于kubeadm安装的集群，scheduler默认是绑定127.0.0.1，这样无法通过节点IP访问到，所以要改成0.0.0.0：

~~~sh
vim /etc/kubernetes/manifests/kube-scheduler.yaml
spec:
  containers:
  - command:
    - kube-scheduler
    - --bind-address=0.0.0.0  # 改为0.0.0.0
    - --kubeconfig=/etc/kubernetes/scheduler.conf
    - --leader-elect=true
~~~

由于manifests目录下是以静态Pod运行在集群中的，所以只要修改静态Pod目录下对应的yaml文件即可。等待一会后，对应服务会自动重启，所以不需要我们手动重启。

## 开启监控

kube-prometheus-stack的配置如下：

~~~yaml
kubeScheduler:
  enabled: true
  endpoints:
  - 192.168.40.180
  service:
    enabled: true
    port: 10259
    targetPort: 10259
    selector:
      component: kube-scheduler
  serviceMonitor:
    enabled: true
    https: true
    insecureSkipVerify: true
    serverName: localhost
    interval: 30s
    metricRelabelings: []
    relabelings: []
~~~

开启之后就会自动创建dashboard：Kubernetes / Scheduler

# 监控kubeProxy

## 修改configMap

kubeProxy的配置卸载configMap中，默认没有开启metrics端口，给他开启：

~~~sh
k edit cm -n kube-system kube-proxy
# 找到这个字段，打开。
metricsBindAddress: 0.0.0.0:10249
~~~

可以删掉节点的kuibe-proxy pod重启。

## 开启监控

~~~yaml
kubeProxy:
  enabled: true
  service:
    enabled: true
    port: 10249
    targetPort: 10249
    selector:
      k8s-app: kube-proxy
  serviceMonitor:
    enabled: true
    https: false
    interval: 30s
    metricRelabelings: []
    relabelings: []
~~~

不用写endpoint列表，会自动发现。

开启之后就会自动创建dashboard：Kubernetes / Proxy
