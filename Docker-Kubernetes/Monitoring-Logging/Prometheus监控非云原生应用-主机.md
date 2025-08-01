# 使用exporter监控服务

如果想要监控一些未提供Metrics接口的服务，比如MySQL、Redis等，需要安装对应的Exporter才能进行监控。

exporter一般支持监控多个实例，但是一般建议还是一个exporter监控一个实例，以免故障之后影响多个服务。

下面将使用MySQL作为一个测试用例，演示如何使用Exporter监控非云原生应用。

## 部署测试用例

~~~sh
# 部署mysql
kubectl create deploy mysql --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:8.0.20
kubectl set env deploy/mysql MYSQL_ROOT_PASSWORD=mysql
kubectl expose deploy mysql --port 3306
# 检查svc可用性
telnet 192.168.140.81 3306
# 登录MySQL，创建Exporter所需的用户和权限
kubectl exec -ti mysql-pod -- bash
mysql -uroot -pmysql
CREATE USER 'exporter'@'%' IDENTIFIED BY 'exporter' WITH MAX_USER_CONNECTIONS 3;
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'exporter'@'%';
quit
~~~

## 部署mysql exporter

创建MySQL Exporter的配置文件：

~~~sh
cat <<'EOF' >> .my.cnf 
[client] 
user=exporter 
password=exporter 
EOF
~~~

创建ConfigMap：

~~~sh
kubectl create cm mysql-exporter-cm --from-file=.my.cnf -n monitoring
~~~

部署mysql exporter及其svc：

~~~yaml
# cat mysql-exporter.yaml
apiVersion: apps/v1 
kind: Deployment 
metadata:
  labels:
    app: mysql-exporter 
  name: mysql-exporter 
  namespace: monitoring
spec:
  replicas: 1 
  selector:
    matchLabels:
      app: mysql-exporter 
  template:
    metadata:
      annotations:
        app: mysql-exporter 
      labels:
        app: mysql-exporter 
    spec:
      containers:
      - args:
        - --config.my-cnf
        - /mnt/.my.cnf
        - --mysqld.address
        - mysql.default:3306
        image: registry.cn-beijing.aliyuncs.com/dotbalo/mysqld- exporter:latest
        imagePullPolicy: IfNotPresent 
        name: mysql-exporter
        ports:
        - containerPort: 9104 
          name: http-web 
          protocol: TCP
        resources: 
          limits:
            cpu: "1" 
            memory: 1Gi
          requests: 
            cpu: 100m
            memory: 128Mi 
        volumeMounts:
        - mountPath: /mnt 
          name: config
      volumes:
      - name: config
        configMap: 
          defaultMode: 420
          name: mysql-exporter-cm
          optional: true 
--- 
apiVersion: v1 
kind: Service 
metadata: 
  name: mysql-exporter 
  namespace: monitoring 
  labels: 
    k8s-app: mysql-exporter 
spec: 
  type: ClusterIP 
  selector: 
    app: mysql-exporter 
  ports: 
  - name: http-web 
    port: 9104 
    protocol: TCP
~~~

通过svc地址获取监控数据：

~~~sh
curl -s 10.103.67.39:9104/metrics | tail -1
~~~

## 部署serviceMonitor

需要注意matchLabels和endpoints的配置，要和MySQL的Service一致

~~~yaml
apiVersion: monitoring.coreos.com/v1 
kind: ServiceMonitor 
metadata: 
  name: mysql-exporter 
  namespace: monitoring 
  labels: 
    k8s-app: mysql-exporter 
    namespace: monitoring 
spec: 
  jobLabel: k8s-app 
  endpoints: 
  - port: http-web 
    interval: 30s 
    scheme: http 
  selector: 
    matchLabels: 
      k8s-app: mysql-exporter 
  namespaceSelector: 
    matchNames: 
    - monitoring
~~~

# 使用ScrapeConfig监控多实例

演示使用ScrapeConfig监控Redis多实例

## 部署测试用例

~~~sh
kubectl create deploy redis --image=registry.cn-beijing.aliyuncs.com/dotbalo/redis:7.2.5 
kubectl expose deploy redis --port 6379
~~~

## 部署exporter

~~~sh
kubectl create deploy redis-exporter -n monitoring --image=registry.cn-beijing.aliyuncs.com/dotbalo/redis_exporter 
kubectl expose deployment redis-exporter -n monitoring --port 9121 
~~~

## 部署ScrapeConfig

接下来创建ScrapeConfig即可监控不同的实例： 

~~~yaml
apiVersion: monitoring.coreos.com/v1alpha1 
kind: ScrapeConfig 
metadata: 
  name: redis-exporter  
  namespace: monitoring 
spec: 
  scrapeInterval: 30s 
  jobName: redis-exporter 
  metricsPath: /scrape 
  scheme: HTTP 
  staticConfigs: 
  - targets: 
    # 多个实例写多次即可 
    # redis://<username>:<password>@address:port 
    - redis://redis.default:6379 
    labels: 
      env: test 
  relabelings: 
      - sourceLabels: [__address__] 
        targetLabel: __param_target 
      - sourceLabels: [__param_target] 
        targetLabel: instance 
  - targetLabel: __address__ 
    replacement: redis-exporter.monitoring:9121 
~~~

部署完成后可以去prometheus-target中查看状态，可以安装dashboard展示指标

# 使用Probe黑盒监控

参考文档：https://github.com/prometheus/blackbox_exporter

CRD 文档：https://github.com/prometheus-operator/kube-prometheus/blob/main/docs/blackbox-exporter.md  

Probe 类型的监控通常都会和Blackbox配合使用，用于监控域名的可用性。

比如需要使用HTTP请求监控某个域名，可以使用如下配置：

~~~yaml
apiVersion: monitoring.coreos.com/v1 
kind: Probe 
metadata: 
  name: blackbox 
  namespace: monitoring 
spec: 
  interval: 30s 
  jobName: blackbox 
  module: http_2xx 
  prober: 
    url: blackbox-exporter.monitoring.svc:19115 
    scheme: http 
    path: /probe 
  targets: 
  staticConfig: 
    static: 
    # 多个实例写多次即可 
    - https://www.kubeasy.com 
    - https://www.baidu.com
~~~

资源创建后即可在Prometheus-targets搜blackbox，查看到监控目标，同样可以安装dashboard，Dashboard ID为：13659

# 监控外部主机

监控Linux 的Exporter 是：https://github.com/prometheus/node_exporter

监控 Windows 主机的Exporter 是：https://github.com/prometheus-community/windows_exporter。  

1. 首先下载对应的 Exporter 至 Windows 主机（ MSI 文 件 下 载 地 址 ： https://github.com/prometheus-community/windows_exporter/releases）

2. 下载完成后，双击打开即可完成安装，之后可以在任务管理器上看到对应的进程

3. Windows Exporter 会暴露一个9182端口，可以通过该端口访问到Windows的监控数据。 

4. 创建一个Scrape即可监控外部的Windows机器：

   ~~~yaml
   apiVersion: monitoring.coreos.com/v1alpha1 
   kind: ScrapeConfig 
   metadata: 
     name: windows-exporter  
     namespace: monitoring 
   spec: 
     scrapeInterval: 30s 
     jobName: windows-exporter 
     metricsPath: /metrics 
     scheme: HTTP 
   staticConfigs: 
   - targets: 
     # 多个实例写多次即可 
     - 192.168.1.104:9182  
     labels: 
       env: test
   ~~~

5. 最后在Grafana中导入模板（ID：20763）即可
