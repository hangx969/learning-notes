# Prometheus简介

## 介绍

- Prometheus是一个开源的系统监控和报警系统，现在已经加入到CNCF基金会，成为继k8s之后第二个在CNCF托管的项目。

- 在kubernetes容器管理系统中，通常会搭配prometheus进行监控，同时也支持多种exporter采集数据，还支持pushgateway进行数据上报，Prometheus性能足够支撑上万台规模的集群。
- 其他监控服务比如：Zabbix、nagios、cattio、夜莺等，在k8s中，prometheus会更原生，配置起来更简便，修改配置文件即可部署监控。

## 配置文档

- Prometheus配置：https://prometheus.io/docs/prometheus/latest/configuration/configuration/

- Prometheus监控组件对应的exporter部署地址: https://prometheus.io/docs/instrumenting/exporters/
  - 可以通过官网给出的不同的exporter来采集不同的指标（比如采集mysql、redis等软件的指标，采集GPU等硬件指标，采集node的OS指标，官网都给出了不同的exporter）

- Prometheus基于k8s服务发现参考: https://github.com/prometheus/prometheus/blob/release-2.31/documentation/examples/prometheus-kubernetes.yml

## 特点

1. 多维度数据模型

   - 每一个时间序列数据都由metric度量指标名称和它的标签labels键值对集合唯一确定：

   - 比如：http_requests_total 接收http请求的总计数，度量名称为/api/tracks的http请求，可以打上不同的标签，获取不同的操作：method=POST的标签，method=GET的标签，查看不同的操作
   - 这个查询语言在这些度量和标签列表的基础上进行过滤和聚合。改变任何度量上的任何标签值，则会形成新的时间序列图。

2. 灵活的查询语言（PromQL）
   - 可以对采集的metrics指标进行加法，乘法，连接等操作；

3. 可以直接在本地部署，不依赖其他分布式存储；

4. 通过基于HTTP的pull方式采集时序数据；

5. 可以通过中间网关pushgateway的方式把时间序列数据推送到prometheus server端；

6. 可通过服务发现或者静态配置来发现目标服务对象（targets）。

7. 有多种可视化图像界面，如Grafana等。

8. **高效的存储：每个采样数据占3.5 bytes左右。比如：300万的时间序列，30s间隔，保留60天，消耗磁盘大概200G。**

9. 做高可用，可以对数据做异地备份，联邦集群，部署多套prometheus，pushgateway上报数据：
   - 比如，自己开发的应用，官网肯定没有exporter，就可以写脚本采集相应数据，用pushgateway推送到prometheus。

## schema

- 在时间序列中的每一个点称为一个样本（sample），样本由以下三部分组成：

  - 指标（metric）：指标名称和描述当前样本特征的 labelsets；

  - 时间戳（timestamp）：一个精确到毫秒的时间戳；

  - 样本值（value）： 一个 float64 的浮点型数据表示当前样本的值。

- 表示方式：

  - 通过如下表达方式表示指定指标名称和指定标签集合的时间序列：

    `<metric name>{<label name>=<label value>, ...}`

  - 例如，指标名称为 api_http_requests_total，标签为 method="POST" 和 handler="/messages" 的时间序列可以表示为：

    `api_http_requests_total{method="POST", handler="/messages"}`

## 数据类型

### Counter

- Counter是计数器类型：
  - Counter 用于累计值，例如记录请求次数、任务完成数、错误发生次数。
  - 一直增加，不会减少。
  - 重启进程后，会被重置。

- 例如：
  - http_response_total{method="GET",endpoint="/api/tracks"} 100
  - http_response_total{method="GET",endpoint="/api/tracks"} 160

- Counter可以方便的了解事件产生的速率的变化，在PromQL内置的相关操作函数可以提供相应的分析，比如以HTTP应用请求量来进行说明：

  - 通过rate()函数获取HTTP请求量的增长率

    `rate(http_requests_total[5m])`

  - 查询当前系统中，访问量前10的HTTP地址

    `topk(10, http_requests_total)`

### Gauge

- Gauge是测量器类型：
  - Gauge是常规数值，例如温度变化、内存使用变化。
  - 可变大，可变小。
  - 重启进程后，会被重置

- 例如：
  - memory_usage_bytes{host="master-01"}  100
  - memory_usage_bytes{host="master-01"}  30
  - memory_usage_bytes{host="master-01"}  50

- 对于 Gauge 类型的监控指标，通过 PromQL 内置函数`delta()`可以获取样本在一段时间内的变化情况，例如，计算 CPU 温度在两小时内的差异：

  `dalta(cpu_temp_celsius{host="zeus"}[2h])`

- 还可以通过PromQL内置函数`predict_linear()`基于简单线性回归的方式，对样本数据的变化趋势做出预测。例如，基于 2 小时的样本数据，来预测主机可用磁盘空间在 4 个小时之后的剩余情况：`predict_linear(node_filesystem_free{job="node"}[2h], 4 \* 3600) < 0`

### histogram

- histogram是柱状图，在Prometheus系统的查询语言中，有三种作用：
  - 在一段时间范围内对数据进行采样（通常是请求持续时间或响应大小等），并将其计入可配置的存储桶（bucket）中. 后续可通过指定区间筛选样本，也可以统计样本总数，最后一般将数据展示为直方图。
  - 对每个采样点值累计和(sum)
  - 对采样点的次数累计和(count)

- 度量指标名称: `basename_`上面三类的作用度量指标名称
  - `basename_bucket{le="上边界"}`, 这个值为小于等于上边界的所有采样点数量
  - `basename_sum`
  - `basename_count`

- 为什需要用histogram柱状图？

  - 在大多数情况下人们都倾向于使用某些量化指标的平均值，例如 CPU 的平均使用率、页面的平均响应时间。这种方式的问题很明显，以系统 API 调用的平均响应时间为例：如果大多数 API 请求都维持在 100ms 的响应时间范围内，而个别请求的响应时间需要 5s，那么就会导致某些 WEB 页面的响应时间落到中位数的情况，而这种现象被称为长尾问题。

  - 为了区分是平均的慢还是长尾的慢，最简单的方式就是按照请求延迟的范围进行分组。例如，统计延迟在 0~10ms 之间的请求数有多少，而 10~20ms 之间的请求数又有多少。通过这种方式可以快速分析系统慢的原因。Histogram 和 Summary 都是为了能够解决这样问题的存在，通过 Histogram 和 Summary 类型的监控指标，我们可以快速了解监控样本的分布情况。

- 例如：

  样本的值分布在 bucket 中的数量，命名为 `basename_bucket{le="上边界"}`。这个值表示指标值小于等于上边界的所有样本数量。

  1、http 请求响应时间 <=0.005 秒 的请求次数为0

  `io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200",le="0.005",} 0.0`

  2、http 请求响应时间 <=0.01 秒 的请求次数为0

  `io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200",le="0.01",} 0.0`

   3、http 请求响应时间 <=0.025 秒 的请求次数为0

  `io_namespace_http_requests_latency_seconds_histogram_bucket{path="/",method="GET",code="200",le="0.025",} 0.0`

### summary

- 与 Histogram 类型类似，用于表示一段时间内的数据采样结果（通常是请求持续时间或响应大小等），但它直接存储了分位数（通过客户端计算，然后展示出来），而不是通过区间来计算。它也有三种作用：

  1、观察时间的quantiles (0~1), 显示为`basename{分位数="quantitles"}`

  2、`[basename]_sum`， 是指所有观察值的总和

  3、`[basename]_count`, 是指已观察到的事件计数值

- 例如：

  - quantiles

    - http 请求中有 50% 的请求响应时间在 3.052404983s以内 `io_namespace_http_requests_latency_seconds_summary{path="/",method="GET",code="200",quantile="0.5",} 3.052404983`

    - http 请求中有 90% 的请求响应时间是在8.003261666s以内

      `io_namespace_http_requests_latency_seconds_summary{path="/",method="GET",code="200",quantile="0.9",} 8.003261666`

  - basename_sum

    http 请求的总响应时间为 51.029495508s

    `io_namespace_http_requests_latency_seconds_summary_sum{path="/",method="GET",code="200",} 51.029495508`

  - basename_count

    当前一共发生了 12 次 http 请求

    `io_namespace_http_requests_latency_seconds_summary_count{path="/",method="GET",code="200",} 12.0`

## 组件

1. Prometheus Server: 用于收集和存储时间序列数据。
   - Retrieval负责在活跃的target主机上抓取监控指标数据
   - TSDB把采集到的数据存储到磁盘中
   - http server会将告警信息传递到alertmanager，推送到接收方

2. Client Library: 客户端库，检测应用程序代码，当Prometheus抓取实例的HTTP端点时，客户端库会将所有跟踪的metrics指标的当前状态发送到prometheus server端。

3. Exporters: prometheus支持多种exporter，通过exporter可以采集metrics数据，然后发送到prometheus server端，所有向promtheus server提供监控数据的程序都可以被称为exporter

4. Alertmanager: 从 Prometheus server 端接收到 alerts 后，会进行去重，分组，并路由到相应的接收方，发出报警，常见的接收方式有：电子邮件，微信，钉钉, slack等。

5. Grafana：监控仪表盘，可视化监控数据

6. pushgateway: 各个目标主机可上报数据到pushgateway，然后prometheus server统一从pushgateway拉取数据。

![image-20240103104154211](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031041340.png)



## 工作流程

1. Prometheus server可定期从活跃的（up）目标主机上（target）拉取监控指标数据，目标主机的监控数据可通过配置静态job或者服务发现的方式被prometheus server采集到，这种方式默认的pull方式拉取指标；也可通过pushgateway把采集的数据上报到prometheus server中；还可通过一些组件自带的exporter采集相应组件的数据；

2. Prometheus server把采集到的监控指标数据保存到本地磁盘或者数据库；

3. Prometheus采集的监控指标数据按时间序列存储，通过配置报警规则，把触发的报警发送到alertmanager

4. Alertmanager通过配置报警接收方，发送报警到邮件，微信或者钉钉等

5. Prometheus 自带的web ui界面提供PromQL查询语言，可查询监控数据

6. Grafana可接入prometheus数据源，把监控数据以图形化形式展示出

## 与Zabbix对比

![image-20240103111904910](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031119014.png)

# Prometheus高可用部署方案

## 基本HA模式

![image-20240103130932595](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031309673.png)

- 只能确保prometheus服务的高可用，但是不解决Prometheus Server之间的数据一致性问题以及持久化问题(数据丢失后无法恢复)，也无法进行动态的扩展。因此这种部署方式适合监控规模不大，Promthues Server也不会频繁发生迁移的情况，并且只需要保存短周期监控数据的场景。

## 基本HA+远程存储

![image-20240103131028372](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031310434.png)

- 在解决了Promthues服务可用性的基础上，同时确保了数据的持久化，当Promthues Server发生宕机或者数据丢失的情况下，可以快速的恢复。 同时Promthues Server可能很好的进行迁移。因此，该方案适用于用户监控规模不大（几百台服务器的规模），但是希望能够将监控数据持久化，同时能够确保Promthues Server的可迁移性的场景。

## 基本HA+远程存储+联邦集群

![image-20240103131314094](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401031313162.png)

- Promthues的性能瓶颈主要在于大量的采集任务，因此用户需要利用Prometheus联邦集群的特性，将不同类型的采集任务划分到不同的Promthues子服务中，从而实现功能分区。
- 例如一个Promthues Server负责采集基础设施相关的监控指标，另外一个Prometheus Server负责采集应用监控指标。再有上层Prometheus Server实现对数据的汇聚。
- 这种方案比较耗费资源，规模较小的环境（几百台服务器）就没必要部署这种方案了。

## prometheus监控k8s集群

- 对于Kubernetes而言，我们可以把当中所有的资源分为几类：

  - 基础设施层（Node）：集群节点，为整个集群和应用提供运行时资源
  - 容器基础设施（Container）：为应用提供运行时环境
  - 用户应用（Pod）：Pod中会包含一组容器，它们一起工作，并且对外提供一个（或者一组）功能
  - 内部服务负载均衡（Service）：在集群内，通过Service在集群暴露应用功能，集群内应用和应用之间访问时提供内部的负载均衡
  - 外部访问入口（Ingress）：通过Ingress提供集群外的访问入口，从而可以使外部客户端能够访问到部署在Kubernetes集群内的服务

- 因此，如果要构建一个完整的监控体系，我们应该考虑，以下5个方面：

  1. 集群节点状态监控：从集群中各节点的kubelet服务获取节点的基本运行状态；

  2. 集群节点资源用量监控：通过Daemonset的形式在集群中各个节点部署Node Exporter采集节点的资源使用情况；

  3. 节点中运行的容器监控：通过各个节点中kubelet内置的cAdvisor中获取个节点中所有容器的运行状态和资源使用情况；

  4. 如果在集群中部署的应用程序本身内置了对Prometheus的监控支持，那么我们还应该找到相应的Pod实例，并从该Pod实例中获取其内部运行状态的监控指标。

  5. 对k8s本身的组件做监控：apiserver、scheduler、controller-manager、kubelet、kube-proxy

# 部署node-exporter

- node-exporter可以采集机器（物理机、虚拟机、云主机等）的监控指标数据，能够采集到的指标包括CPU, 内存，磁盘，网络，文件数等信息。

## 安装node-exporter

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
      - key: "node-role.kubernetes.io/master"
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

## 验证exporter数据采集

~~~sh
#查看宿主机的9100端口占用
ss -antulp | grep :9100
#查看exporter采集到的数据
curl http://192.168.40.180:9100/metrics
~~~

# 部署prometheus

## 创建sa并授权

~~~sh
kubectl create serviceaccount monitor -n monitor-sa
#给sa和sa用户都授权，防止prometheus报错--user=system:serviceaccount:monitor:monitor-sa没有权限。
kubectl create clusterrolebinding monitor-clusterrolebinding -n monitor-sa --clusterrole=cluster-admin  --serviceaccount=monitor-sa:monitor

kubectl create clusterrolebinding monitor-clusterrolebinding-1 -n monitor-sa --clusterrole=cluster-admin --user=system:serviceaccount:monitor:monitor-sa
#将cluster-admin这个ClusterRole绑定到了一个特定的用户，这个用户是monitor命名空间下的monitor-sa这个ServiceAccount。这里的--user参数的值system:serviceaccount:monitor:monitor-sa是Kubernetes内部用来表示ServiceAccount的一种格式。
~~~

> 这两条命令的主要区别在于它们绑定的对象不同，第一条命令是直接绑定到一个`ServiceAccount`，而第二条命令是绑定到一个表示`ServiceAccount`的用户。在实际使用中，这两种方式的效果是相同的，都是将`cluster-admin`这个`ClusterRole`的权限赋予了`monitor`命名空间下的`monitor-sa`这个`ServiceAccount`。

## 创建数据存储目录

~~~sh
#在node-1上创建数据目录并给满权限（否则prometheus写不进去数据）
mkdir /data
chmod 777 /data/
~~~

## 安装prometheus server服务

### 创建configmap存储配置

~~~yaml
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
      scrape_interval: 20s #采集目标主机监控据的时间间隔
      scrape_timeout: 10s #数据采集超时时间，默认10s
      evaluation_interval: 1m #触发告警检测的时间，默认是1m。这个时间间隔要大于采集数据的间隔，否则会产生多次重复告警。假如我们的指标是5m被拉取一次。检测根据evaluation_interval 1m一次，所以在值被更新前，我们一直用的旧值来进行多次判断，造成了1m一次，同一个指标被告警了4次。
    scrape_configs: #定义了Prometheus从哪些源收集指标数据。每个scrape_config块指定一组目标和参数，描述了如何从这些目标收集指标。
    - job_name: 'kubernetes-node' 
      kubernetes_sd_configs: #使用的是k8s的服务发现
      - role: node #使用node模式，意味着Prometheus将从Kubernetes的节点收集指标。可能包括CPU使用率、内存使用量、磁盘空间等。
      relabel_configs: #定义标签重写规则
      - source_labels: [__address__] #更改__address__标签
        regex: '(.*):10250' #10250是kubelet的监听端口，为的是找到每个node，默认走kubelet10250来服务发现
        replacement: '${1}:9100' #把匹配到的ip:10250的ip保留，端口替换成exporter的9100端口
        target_label: __address__ #表示找这个node上面的exporter拿数据
        action: replace
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+) #匹配所有以__meta_kubernetes_node_label_开头的标签。这些标签是由Prometheus的Kubernetes服务发现生成的，包含了k8s节点的元数据。所以，这个labelmap动作将所有K8s节点的标签复制到Prometheus指标的标签中。这样，你就可以在Prometheus查询中使用这些标签
    - job_name: 'kubernetes-node-cadvisor' #抓取cAdvisor数据，是获取kubelet上/metrics/cadvisor接口数据来获取容器的资源使用情况
      kubernetes_sd_configs:
      - role:  node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__ ##获取到的地址：__address__="192.168.40.180:10250"
        replacement: kubernetes.default.svc:443 ##把获取到的地址替换成新的地址kubernetes.default.svc:443,这个svc后端关联到的pod是apiserver
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics/cadvisor #将指标路径设置为每个节点的cAdvisor指标路径。cAdvisor是一个开源的容器监控工具，它内置在Kubernetes的节点中，提供了关于容器的详细指标。
    - job_name: 'kubernetes-apiserver' 
      kubernetes_sd_configs:
      - role: endpoints #基于k8s的服务发现，走的是endpoint模式，采集apiserver 6443端口获取到的监控数据
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
    - job_name: 'kubernetes-service-endpoints' #创建svc的时候加一个annotation，svc就能被这个job监控到
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

### 创建prometheus pod

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
        nodeName: node-1 #直接指定要调度到的node
        serviceAccountName: monitor
        containers:
        - name: prometheus
          image: prom/prometheus:v2.2.1
          imagePullPolicy: IfNotPresent
          command:
            - prometheus
            - --config.file=/etc/prometheus/prometheus.yml
            - --storage.tsdb.path=/prometheus
            - --storage.tsdb.retention=240h
            - --web.enable-lifecycle
            #web.enable-lifecycle：修改配置之后不需要重新创建pod，会热加载
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

### 创建svc代理prometheus server

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

### 查看prometheus UI

- 直接访问node IP:31408

- 在Status - Targets - kubernetes-service-endpoints里面能看到两个svc后端pod。这两个pod是coredns，svc是kube-dns。

  ![image-20240104132718578](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401041327748.png)

  - 为啥这个svc会被监控到？因为这个svc自带了annotation：

    ~~~yaml
    Name:              kube-dns
    Namespace:         kube-system
    Labels:            k8s-app=kube-dns
                       kubernetes.io/cluster-service=true
                       kubernetes.io/name=CoreDNS
    Annotations:       prometheus.io/port: 9153
                       prometheus.io/scrape: true
    ~~~

# prometheus监控常见服务

## tomcat

- tomcat_exporter地址：https://github.com/nlighten/tomcat_exporter

- 下载相关包

  metrics.war 

  simpleclient-0.8.0.jar

  simpleclient_common-0.8.0.jar

  simpleclient_hotspot-0.8.0.jar

  simpleclient_servlet-0.8.0.jar

  tomcat_exporter_client-0.0.12.jar

- 打包镜像

  ~~~dockerfile
  cat Dockerfile
  FROM tomcat:8.5-jdk8-corretto
  ADD metrics.war /usr/local/tomcat/webapps/
  ADD simpleclient-0.8.0.jar  /usr/local/tomcat/lib/
  ADD simpleclient_common-0.8.0.jar /usr/local/tomcat/lib/
  ADD simpleclient_hotspot-0.8.0.jar /usr/local/tomcat/lib/
  ADD simpleclient_servlet-0.8.0.jar /usr/local/tomcat/lib/
  ADD tomcat_exporter_client-0.0.12.jar /usr/local/tomcat/lib/
  ~~~

  ~~~sh
  docker build -t='tomcat_prometheus:v1' .
  docker save -o 
  ~~~

- 创建tomcat实例

  ~~~yaml
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: dep-tomcat
    namespace: default
  spec:
    selector: 
      matchLabels: 
       app: tomcat
    replicas: 2 # tells deployment to run 2 pods matching the template
    template: # create pods using pod definition in this template
      metadata:
        labels:
          app: tomcat
        annotations:
          prometheus.io/scrape: 'true'
      spec:
        containers:
        - name: tomcat
          image: tomcat_prometheus:v1
          ports:
          - containerPort: 8080
          securityContext: 
            privileged: true
  ---
  kind: Service
  apiVersion: v1
  metadata:
    name: svc-tomcat
    annotations:
      prometheus.io/scrape: 'true'
  spec:
    selector:
      app: tomcat
    ports:
    - nodePort: 31360
      port: 80
      protocol: TCP
      targetPort: 8080
    type: NodePort
  ~~~

- prometheus中通过kubernetes-pods的job查看监控到的pod情况

## redis





# prometheus热加载

- 为了每次修改配置文件可以热加载prometheus，也就是不停止prometheus就可以使配置生效，想要使配置生效可用如下热加载命令：

  ~~~sh
  #查看prometheus server的pod IP
  kubectl get pods -n monitor-sa -o wide -l app=prometheus
  #推送更新
  curl -X POST http://<pod ip>:9090/-/reload
  #前提是在prometheus server的deployment yaml中配置了参数：--web.enable-lifecycle
  ~~~

- 另一种方式是暴力重启prometheus:kubectl delete 删掉configmap和deploy，再重新apply。这样会造成监控数据中断甚至丢失。推荐热加载。

# PromQL查询语言

- PromQL（Prometheus Query Language）是 Prometheus 自己开发的表达式语言，语言表现力很丰富，内置函数也很多。使用它可以对时序数据进行筛选和聚合。

## 数据类型

PromQL 表达式计算出来的值有以下几种类型：

- 瞬时向量 (Instant vector): 一组时序，每个时序只有一个采样值

- 区间向量 (Range vector): 一组时序，每个时序包含一段时间内的多个采样值

- 标量数据 (Scalar): 一个浮点数

- 字符串 (String): 一个字符串，暂时未用 

### 瞬时向量选择器

- 瞬时向量选择器用来选择一组时序在某个采样点的采样值。最简单的情况就是指定一个度量指标，选择出所有属于该度量指标的时序的当前采样值。
- 比如下面的表达式：`apiserver_request_total`，可以通过在后面添加用大括号包围起来的一组标签键值对来对时序进行过滤。比如下面的表达式筛选出了 job 为 kubernetes-apiservers，并且 resource为 pod的时序：`apiserver_request_total{job="kubernetes-apiserver",resource="pods"}`

- 匹配标签值时可以是等于，也可以使用正则表达式。总共有下面几种匹配操作符：

  - =：完全相等

  - !=： 不相等

  - =~： 正则表达式匹配

  - !~： 正则表达式不匹配

- 下面的表达式筛选出了container是kube-scheduler或kube-proxy或kube-apiserver的时序数据:`container_processes{container=~"kube-scheduler|kube-proxy|kube-apiserver"}`

### 区间向量选择器

- 区间向量选择器类似于瞬时向量选择器，不同的是它选择的是过去一段时间的采样值。可以通过在瞬时向量选择器后面添加包含在 [] 里的时长来得到区间向量选择器。
- 比如下面的表达式选出了所有度量指标为apiserver_request_total且resource是pod的时序在过去1分钟的采样值：`apiserver_request_total{job="kubernetes-apiserver",resource="pods"}[1m]`

### 偏移向量选择器

- 偏移修饰器用来调整基准时间，使其往前偏移一段时间。偏移修饰器紧跟在选择器后面，使用 offset 来指定要偏移的量。
- 比如下面的表达式选择度量名称为apiserver_request_total的所有时序在 5 分钟前的采样值:`apiserver_request_total{job="kubernetes-apiserver",resource="pods"} offset 5m`

- 下面的表达式选择apiserver_request_total 度量指标在 1 周前的这个时间点过去 5 分钟的采样值:`apiserver_request_total{job="kubernetes-apiserver",resource="pods"} [5m] offset 1w`

## 聚合操作符

- PromQL 的聚合操作符用来将向量里的元素聚合得更少。总共有下面这些聚合操作符：

  - sum：求和

  - min：最小值

  - max：最大值

  - avg：平均值

  - stddev：标准差

  - stdvar：方差

  - count：元素个数

  - count_values：等于某值的元素个数

  - bottomk：最小的 k 个元素

  - topk：最大的 k 个元素

  - quantile：分位数

- 如：

  - 计算xianchaomaster1节点所有容器总计内存

    `sum(container_memory_usage_bytes{instance=~"xianchaomaster1"})/1024/1024/1024` 

  - 计算xianchaomaster1节点最近1m所有容器cpu使用率

    `sum (rate (container_cpu_usage_seconds_total{instance=~"xianchaomaster1"}[1m])) / sum (machine_cpu_cores{ instance =~"xianchaomaster1"}) * 100`

  - 计算最近1m所有容器cpu使用率的总和

    `sum (rate (container_cpu_usage_seconds_total{id!="/"}[1m])) by (id)`\#把id会打印出来

  > `rate()`函数用于计算时间序列数据的平均速率。这个函数通常用于处理计数器类型的指标

## 函数

- Prometheus 内置了一些函数来辅助计算，下面介绍一些典型的。

  - abs()：绝对值

  - sqrt()：平方根

  - exp()：指数计算

  - ln()：自然对数

  - ceil()：向上取整

  - floor()：向下取整

  - round()：四舍五入取整

  - delta()：计算区间向量里每一个时序第一个和最后一个的差值

  - sort()：排序
