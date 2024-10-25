# Prometheus v2.33.5部署

## 部署node-exporter

- node-exporter可以采集机器（物理机、虚拟机、云主机等）的监控指标数据，能够采集到的指标包括CPU, 内存，磁盘，网络，文件数等信息。

### 安装node-exporter

~~~sh
kubectl create ns monitor-sa
~~~

~~~yaml
apiVersion: apps/v1
kind: DaemonSet  #可以保证k8s集群的每个节点都运行完全一样的pod
metadata:
  name: node-exporter
  namespace: monitor-sa
  labels:
    name: node-exporter
spec:
  selector:
    matchLabels:
     name: node-exporter
  template:
    metadata:
      labels:
        name: node-exporter
    spec:
      hostPID: true
      hostIPC: true
      hostNetwork: true #表示这个pod不用网络插件划分Ip，共享宿主机IP，调度到哪个node上，就用哪个node的IP。
      # hostNetwork、hostIPC、hostPID都为True时，表示这个Pod里的所有容器，会直接使用宿主机的网络，直接与宿主机进行IPC（进程间通信）通信，可以看到宿主机里正在运行的所有进程。加入了hostNetwork:true会直接将我们的宿主机的9100端口映射出来，从而不需要创建service在宿主机上就会有一个9100的端口
      containers:
      - name: node-exporter
        image: prom/node-exporter:v0.16.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9100
        resources:
          requests:
            cpu: 0.15  #这个容器运行至少需要0.15核cpu
        securityContext:
          privileged: true  #开启特权模式，任何在容器内运行的进程都将拥有几乎与主机上运行的进程相同的权限。这意味着这些进程可以访问主机的所有资源，包括操作系统和硬件设备。
        args:
        - --path.procfs  #配置挂载宿主机（node节点）的路径
        - /host/proc
        - --path.sysfs  #配置挂载宿主机（node节点）的路径
        - /host/sys
        - --collector.filesystem.ignored-mount-points
        - '"^/(sys|proc|dev|host|etc)($|/)"' #node-exporter在收集文件系统指标时，将忽略挂载点路径以/sys、/proc、/dev、/host或/etc开头的文件系统。这些路径通常包含的是操作系统和运行环境的数据，而不是用户数据，因此通常不需要监控它们的文件系统使用情况。忽略这些路径可以减少node-exporter的输出，使得输出的指标更加关注于对用户更有价值的数据。
        volumeMounts:
        #将主机/dev、/proc、/sys这些目录挂到容器中，这是因为我们采集的很多节点数据都是通过这些文件来获取系统信息的。
        - name: dev
          mountPath: /host/dev
        - name: proc
          mountPath: /host/proc
        - name: sys
          mountPath: /host/sys
        - name: rootfs
          mountPath: /rootfs
      tolerations:
      - key: "node-role.kubernetes.io/control-plane"
        operator: "Exists"
        effect: "NoSchedule"
      volumes:
        - name: proc
          hostPath:
            path: /proc
        - name: dev
          hostPath:
            path: /dev
        - name: sys
          hostPath:
            path: /sys
        - name: rootfs
          hostPath:
            path: /
~~~

### 验证exporter数据采集

~~~sh
#查看宿主机的9100端口占用
ss -antulp | grep :9100
#查看exporter采集到的数据
curl http://192.168.40.5:9100/metrics
~~~

## 部署prometheus

### 创建sa并授权

~~~sh
kubectl create serviceaccount monitor -n monitor-sa
#给sa和sa用户都授权，防止prometheus报错--user=system:serviceaccount:monitor:monitor-sa没有权限。
kubectl create clusterrolebinding monitor-clusterrolebinding -n monitor-sa --clusterrole=cluster-admin  --serviceaccount=monitor-sa:monitor

kubectl create clusterrolebinding monitor-clusterrolebinding-1 -n monitor-sa --clusterrole=cluster-admin --user=system:serviceaccount:monitor:monitor-sa
#将cluster-admin这个ClusterRole绑定到了一个特定的用户，这个用户是monitor命名空间下的monitor-sa这个ServiceAccount。这里的--user参数的值system:serviceaccount:monitor:monitor-sa是Kubernetes内部用来表示ServiceAccount的一种格式。
~~~

> 这两条命令的主要区别在于它们绑定的对象不同，第一条命令是直接绑定到一个`ServiceAccount`，而第二条命令是绑定到一个表示`ServiceAccount`的用户。在实际使用中，这两种方式的效果是相同的，都是将`cluster-admin`这个`ClusterRole`的权限赋予了`monitor`命名空间下的`monitor-sa`这个`ServiceAccount`。

> yaml格式的：
>
> ~~~yaml
> apiVersion: v1
> kind: ServiceAccount
> metadata:
>   name: monitor
>   namespace: monitor-sa
>   
> ---
> apiVersion: rbac.authorization.k8s.io/v1
> kind: ClusterRoleBinding
> metadata:
>   name: monitor-clusterrolebinding
> roleRef:
>   apiGroup: rbac.authorization.k8s.io
>   kind: ClusterRole
>   name: cluster-admin
> subjects:
> - kind: ServiceAccount
>   name: monitor
>   namespace: monitor-sa
> ---
> apiVersion: rbac.authorization.k8s.io/v1
> kind: ClusterRoleBinding
> metadata:
>   name: monitor-clusterrolebinding-1
> roleRef:
>   apiGroup: rbac.authorization.k8s.io
>   kind: ClusterRole
>   name: cluster-admin
> subjects:
> - apiGroup: rbac.authorization.k8s.io
>   kind: User
>   name: system:serviceaccount:monitor:monitor-sa
> ~~~

### 创建数据存储目录

~~~sh
#在node-1上创建数据目录并给满权限（否则prometheus写不进去数据）
mkdir /data
chmod 777 /data/
~~~

### 安装prometheus server服务

#### 创建configmap存储配置

~~~yaml
---
kind: ConfigMap
apiVersion: v1
metadata:
  labels:
    app: prometheus
  name: prometheus-config
  namespace: monitor-sa
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      scrape_timeout: 10s
      evaluation_interval: 1m
    scrape_configs:
    - job_name: 'kubernetes-node'
      kubernetes_sd_configs:
      - role: node
      relabel_configs:
      - source_labels: [__address__]
        regex: '(.*):10250'
        replacement: '${1}:9100'
        target_label: __address__
        action: replace
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
    - job_name: 'kubernetes-node-cadvisor'
      kubernetes_sd_configs:
      - role:  node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics/cadvisor
    - job_name: 'kubernetes-apiserver'
      kubernetes_sd_configs:
      - role: endpoints
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
    - job_name: 'kubernetes-service-endpoints'
      kubernetes_sd_configs:
      - role: endpoints
      relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_label: __scheme__
        regex: (https?)
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
      - action: labelmap
        regex: __meta_kubernetes_service_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: kubernetes_name 
~~~

> summary：
>
> job_name: 'kubernetes-node' ：访问node exporter，获取物理机监控数据
>
> job_name: 'kubernetes-node-cadvisor'：可以请求到node上的kubelet的cAdvisior里面的监控数据
>
> job_name: 'kubernetes-apiserver' ：采集apiserver 6443端口获取到的监控数据
>
> job_name: 'kubernetes-service-endpoints' ：创建svc的时候加一个annotation，svc就能被这个job监控到

#### 创建prometheus pod

- 通过deployment把prometheus server调度到有数据目录的node-1上面

  ~~~yaml
  ---
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: prometheus-server
    namespace: monitor-sa
    labels:
      app: prometheus
  spec:
    replicas: 1
    selector:
      matchLabels:
        app: prometheus
        component: server
      #matchExpressions:
      #- {key: app, operator: In, values: [prometheus]}
      #- {key: component, operator: In, values: [server]}
    template:
      metadata:
        labels:
          app: prometheus
          component: server
        annotations:
          prometheus.io/scrape: 'false'
      spec:
        nodeName: node1
        serviceAccountName: monitor
        containers:
        - name: prometheus
          image: docker.io/prom/prometheus:latest
          imagePullPolicy: IfNotPresent
          command:
            - prometheus
            - --config.file=/etc/prometheus/prometheus.yml
            - --storage.tsdb.path=/prometheus
            - --storage.tsdb.retention=720h
            - --web.enable-lifecycle
          ports:
          - containerPort: 9090
            protocol: TCP
          volumeMounts:
          - mountPath: /etc/prometheus
            name: prometheus-config
          - mountPath: /prometheus/
            name: prometheus-storage-volume
        volumes:
          - name: prometheus-config
            configMap:
              name: prometheus-config
          - name: prometheus-storage-volume
            hostPath:
             path: /data
             type: Directory
  ~~~
  
  > 如果集群搭建了nfs供应商，可以用nfs存储
  >
  > ~~~yaml
  > #......
  >      volumes:
  >         - name: prometheus-config
  >           configMap:
  >             name: prometheus-config
  >         - name: prometheus-storage-volume
  >           persistentVolumeClaim:
  >             claimName: pvc-prometheus
  > 
  > ---
  > kind: PersistentVolumeClaim
  > apiVersion: v1
  > metadata:
  >   name: pvc-prometheus
  >   namespace: monitor-sa
  > spec:
  >   accessModes:
  >   - ReadWriteMany
  >   resources:
  >     requests:
  >       storage: 1Gi
  >   storageClassName:  sc-nfs
  > ~~~

#### 创建svc代理prometheus server

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitor-sa
  labels:
    app: prometheus
spec:
  type: NodePort
  selector:
    app: prometheus
    component: server
  ports:
  - port: 9090
    targetPort: 9090
    protocol: TCP
~~~

# Grafana v8.4.5部署

## 部署Grafana服务

~~~sh
#grafana用到的镜像为k8s.gcr.io/heapster-grafana-amd64:v5.0.4
#可以创建pod的时候拉取，也可以先上传到node上
docker load -i grafana_8.4.5.tar.gz
#上传grafana的yaml文件
kubectl apply -f dep-grafana.yaml
~~~

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: monitoring-grafana
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      task: monitoring
      k8s-app: grafana
  template:
    metadata:
      labels:
        task: monitoring
        k8s-app: grafana
    spec:
      #nodeName: node-01
      containers:
      - name: grafana
        image: grafana/grafana:8.4.5
        ports:
        - containerPort: 3000
          protocol: TCP
        volumeMounts:
        - mountPath: /etc/ssl/certs
          name: ca-certificates
          readOnly: true
        - mountPath: /var
          name: grafana-storage
        - mountPath: /var/lib/grafana/
          name: lib
        env:
        - name: INFLUXDB_HOST
          value: monitoring-influxdb
        - name: GF_SERVER_HTTP_PORT
          value: "3000"
          # The following env variables are required to make Grafana accessible via
          # the kubernetes api-server proxy. On production clusters, we recommend
          # removing these env variables, setup auth for grafana, and expose the grafana
          # service using a LoadBalancer or a public IP.
        - name: GF_AUTH_BASIC_ENABLED
          value: "false"
        - name: GF_AUTH_ANONYMOUS_ENABLED
          value: "true"
        - name: GF_AUTH_ANONYMOUS_ORG_ROLE
          value: Admin
        - name: GF_SERVER_ROOT_URL
          # If you're only using the API Server proxy, set this value instead:
          # value: /api/v1/namespaces/kube-system/services/monitoring-grafana/proxy
          value: /
      volumes:
      - name: ca-certificates
        hostPath:
          path: /etc/ssl/certs
      - name: grafana-storage
        emptyDir: {}
      - name: lib
        hostPath:
         path: /var/lib/grafana/
         type: DirectoryOrCreate
---
apiVersion: v1
kind: Service
metadata:
  labels:
    # For use as a Cluster add-on (https://github.com/kubernetes/kubernetes/tree/master/cluster/addons)
    # If you are NOT using this as an addon, you should comment out this line.
    kubernetes.io/cluster-service: 'true'
    kubernetes.io/name: monitoring-grafana
  name: monitoring-grafana
  namespace: kube-system
spec:
  # In a production setup, we recommend accessing Grafana through an external Loadbalancer
  # or through a public IP.
  # type: LoadBalancer
  # You could also use NodePort to expose the service at a randomly-generated port
  # type: NodePort
  ports:
  - port: 80
    targetPort: 3000
  selector:
    k8s-app: grafana
  type: NodePort
~~~

> 部署了nfs供应商的集群里面可以直接用：
>
> ~~~yaml
>      volumes:
>       - name: ca-certificates
>         hostPath:
>           path: /etc/ssl/certs
>       - name: grafana-storage
>         persistentVolumeClaim:
>           claimName: pvc-grafana-storage
>       - name: lib
>         persistentVolumeClaim:
>           claimName: pvc-grafana-storage-lib
> ---
> kind: PersistentVolumeClaim
> apiVersion: v1
> metadata:
>   name: pvc-grafana-storage
>   namespace: monitor-sa
> spec:
>   accessModes:
>   - ReadWriteMany
>   resources:
>     requests:
>       storage: 200Mi 
>   storageClassName:  sc-nfs
> ---
> kind: PersistentVolumeClaim
> apiVersion: v1
> metadata:
>   name: pvc-grafana-storage-lib
>   namespace: monitor-sa
> spec:
>   accessModes:
>   - ReadWriteMany
>   resources:
>     requests:
>       storage: 200Mi 
>   storageClassName:  sc-nfs
> ~~~

## 接入prometheus服务

- 通过nodeIP:nodeport登陆grafana，在浏览器访问UI

- 默认admin/admin

- add data source - prometheus - 地址填`http://<prometheus svc name>.<namespace>.svc:9090`

  ![image-20240105161500835](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051615043.png)

![image-20240105161508508](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051615563.png)

![image-20240105161528980](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051615029.png)

![image-20240105161537658](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051615728.png)

![image-20240105161545724](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401051615776.png)

## 导入监控模板

- import **node_exporter.json**、**docker_rev1.json** (ID为：8919，9276，11074)

