# 介绍

Prometheus Operator 也称为 Kube-Prometheus-Stack。prometheus-community/kube-prometheus-stack Helm Chart 提供了与 kube-prometheus 类似的功能集。该Chart由 Prometheus 社区维护。

官网地址：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#kube-prometheus-stack

releases page: https://github.com/prometheus-community/helm-charts/releases

artifact hub: https://artifacthub.io/packages/helm/prometheus-community/kube-prometheus-stack

通过一个prometheus-stack的chart，自动部署prometheus、prometheus rules、Alertmanager以及各种operator；还有kube-state-metrics、grafana、node-exporter。

- 其中，kube-state-metrics(采集容器指标)、node-exporter（采集宿主机指标）、grafana是通过独立的sub helm chart安装的：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#dependencies

- [prometheus-community/kube-state-metrics](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-state-metrics)
- [prometheus-community/prometheus-node-exporter](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-node-exporter)
- [grafana/grafana](https://github.com/grafana/helm-charts/tree/main/charts/grafana)

# 部署

## 前提条件

1. 准备storage class提供数据持久化，实验环境下事先部署了nfs-client的sc，并设置为default storage class
   - 默认存储类：https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#default-storageclass


2. 提前配置ingress controller和ingress class
   - ingress controller yaml: https://github.com/kubernetes/ingress-nginx/tree/main/deploy/static/provider/baremetal
   - ingressController的deployment中配置hostnetwork=true

## 下载

- 添加仓库

~~~sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm pull prometheus-community/kube-prometheus-stack --version 59.1.0
tar xzvf kube-prometheus-stack-59.1.0.tgz
cd kube-prometheus-stack
~~~

## helm配置

- 修改配置文件

~~~yaml
#修改两个镜像源
vim values.yaml
##将
---
      image:
        registry: registry.k8s.io
        repository: ingress-nginx/kube-webhook-certgen
        tag: v20221220-controller-v1.5.1-58-g787ea74b6
##改成
---
      image:
        registry: registry.cn-hangzhou.aliyuncs.com/google_containers
        repository: kube-webhook-certgen
        tag: v20221220-controller-v1.5.1-58-g787ea74b6

vim charts/kube-state-metrics/values.yaml
#将
---
image:
  registry: registry.k8s.io
  repository: kube-state-metrics/kube-state-metrics
  # If unset use v + .Charts.appVersion
  tag: ""
#改成
---
image:
  registry: docker.io
  repository: bitnami/kube-state-metrics
  # If unset use v + .Charts.appVersion
  tag: "2.10.0"
~~~

~~~yaml
#将prometheus和alertManager数据持久化
#需要提前部署nfs-provisioner和默认存储类
vim values.yaml
---
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: sc-nfs
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 1Gi
---
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: sc-nfs
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 1Gi
---
~~~

~~~yaml
#grafana数据持久化
vim charts/grafana/values.yaml
persistence:
  type: pvc
  enabled: true
  storageClassName: sc-nfs
  accessModes:
    - ReadWriteOnce
  size: 1Gi
~~~

~~~yaml
#配置ingress
#需要修改的values.yaml地方如下：
  --set prometheus.ingress.enabled=true \
  --set prometheus.prometheusSpec.retention=7d \
  --set prometheus.ingress.hosts='{prometheus.hanxux.local}' \
  --set prometheus.ingress.paths='{/}' \
  --set prometheus.ingress.pathType=Prefix \
  --set alertmanager.ingress.enabled=true \
  --set alertmanager.ingress.hosts='{alertmanager.hanxux.local}' \
  --set alertmanager.ingress.paths='{/}' \
  --set alertmanager.ingress.pathType=Prefix \
  --set grafana.ingress.enabled=true \
  --set grafana.adminPassword=admin \
  --set grafana.ingress.hosts='{grafana.hanxux.local}' \
  --set grafana.ingress.paths='{/}' \
  --set grafana.ingress.pathType=Prefix . -f values.yaml
~~~

> 注意：
>
> 后面单独部署了loki和tempo之后，要去prometheus-stack的values里面加上grafana.additaionalDataSources字段：
>
> ~~~yaml
> additionalDataSources:
>     - name: Tempo
>       type: tempo
>       uid: tempo
>       url: http://tempo.monitoring.svc:3100
>       access: proxy
>       version: 1
>       jsonData:
>         httpMethod: GET
>         serviceMap:
>           datasourceUid: 'prometheus'
>         tracesToLogsV2: # https://grafana.com/docs/grafana/next/datasources/tempo/#trace-to-logs
>           datasourceUid: 'Loki'
>           spanStartTimeShift: '-5m'
>           spanEndTimeShift: '5m'
>           tags: [{ key: 'service.name', value: 'app' }, { key: 'host.name', value: 'pod' }]
>     - name: Loki
>       type: loki
>       url: http://loki.monitoring.svc:3100
>       access: proxy
> ~~~

~~~yaml
# 这些设置表示提到的selector（rule、service monitor、pod monitor 和 scrape config）将有独立的配置，并且不会基于 Helm Chart默认 values。
ruleSelectorNilUsesHelmValues: false
serviceMonitorSelectorNilUsesHelmValues: false
podMonitorSelectorNilUsesHelmValues: false
probeSelectorNilUsesHelmValues: false
scrapeConfigSelectorNilUsesHelmValues: false
~~~

## 安装

~~~sh
helm install kube-prometheus-stack -n monitoring --create-namespace . -f values.yaml
~~~

## 升级

~~~sh
helm upgrade -i kube-prometheus-stack -n monitoring . -f values.yaml
~~~

## 验证安装

~~~sh
#通过port forward转发svc端口来本地访问
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9000:9090
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 9000:3000
kubectl port-forward svc/kube-prometheus-stack-alertmanager  -n monitoring 9000:9093
~~~

## 卸载

~~~sh
helm uninstall kube-prometheus-stack -n monitoring #--dry-run

#CRDs created by this chart are not removed by default and should be manually cleaned up:
kubectl delete crd alertmanagerconfigs.monitoring.coreos.com
kubectl delete crd alertmanagers.monitoring.coreos.com
kubectl delete crd podmonitors.monitoring.coreos.com
kubectl delete crd probes.monitoring.coreos.com
kubectl delete crd prometheusagents.monitoring.coreos.com
kubectl delete crd prometheuses.monitoring.coreos.com
kubectl delete crd prometheusrules.monitoring.coreos.com
kubectl delete crd scrapeconfigs.monitoring.coreos.com
kubectl delete crd servicemonitors.monitoring.coreos.com
kubectl delete crd thanosrulers.monitoring.coreos.com
~~~

## ingress访问

### Http

- 查看ingress的ip

~~~sh
k get ing -n monitoring

NAME                                 CLASS   HOSTS                       ADDRESS          PORTS   AGE
kube-prometheus-stack-alertmanager   nginx   alertmanager.hanxux.local   172.16.183.101   80      10m
kube-prometheus-stack-grafana        nginx   grafana.hanxux.local        172.16.183.101   80      10m
kube-prometheus-stack-prometheus     nginx   prometheus.hanxux.local     172.16.183.101   80      10m
~~~

- 本地加解析

~~~sh
172.16.183.101 prometheus.hanxux.local alertmanager.hanxux.local grafana.hanxux.local
~~~

- 浏览器登录grafana：grafana.hanxux.local admin/admin

> ~~~sh
> #查看grafana密码
> kubectl get secrets  -n monitoring kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
> ~~~

### Https

- 首先部署出certmanager --> 创建clusterissuer --> 创建给grafana ingress https的secret --> helm values.yaml的grafana ingress tls部分配置secret、host

- secret

~~~yaml
tee certificate-grafana.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-grafana
  namespace: monitoring
spec:
  secretName: grafana-tls-cert-secret
  privateKey:
    rotationPolicy: Always
  commonName: grafana.hanxux.local
  dnsNames:
    - grafana.hanxux.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: selfsigned
    kind: ClusterIssuer
EOF
~~~

- kube-prometheus-stack的values配置

~~~yaml
    ## TLS configuration for grafana Ingress
    ## Secret must be manually created in the namespace
    ##
    tls:
      - secretName: cert-grafana
        hosts:
        - grafana.hanxux.local
~~~

- https访问hostname即可，由于lab用的是自签证书，所以浏览器会报连接不安全。

## 集成oauth2proxy认证

给ingress添加annotations：

~~~yaml
annotations:
  nginx.ingress.kubernetes.io/auth-url: "http://oauth2-proxy.oauth2-proxy.svc.cluster.local/oauth2/auth"
  nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fgrafana.hanxux.local"
~~~

# helm管理grafana dashboard

- dashboard可以单独打成一个helm包

~~~yaml
./
├── Chart.yaml
├── dashboards #放各种dashboard的json文件
│   ├── aks.json
├── templates
│   └── grafana_dashboard.yaml
├── values
└── values.yaml #主要定义dashboard的名字和json模板路径
~~~

- Chart.yaml

~~~yaml
apiVersion: v2
name: grafana-dashboards-config
description: A Helm chart for Grafana Dashborads configuration
type: application
version: 1.0.0
appVersion: "1.0.0"
~~~

- values.yaml

~~~yaml
dashboards:
  - file_path: "dashboards/aks.json"
    dashboard_name: aks-platform
~~~

- templates/grafana_dashboard.yaml

~~~yaml
{{- range .Values.dashboards }}
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: "grafana-dashboard-{{ .dashboard_name -}}"
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  grafana_dashboard_{{- .file_path | replace "dashboards/" "" }}: |-
{{ $.Files.Get .file_path | indent 4 }}
{{- end }}
~~~

- 安装命令

~~~sh
helm upgrade -i grafana-dashboards-config -n monitoring . --values values.yaml
~~~

# helm管理grafana datasources

- datasource也可以以helm chart的形式部署，例如templates目录下放datasources的yaml文件：

~~~yaml
tee pg1-fatasource.yaml <<'EOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-event-datasource
  namespace: monitoring
  labels:
    grafana_datasource: "1"
data:
  postgres_event_datasource.yaml: |-
    apiVersion: 1
    datasources:
      - name: PostgresDB
        type: postgres
        access: proxy
        url: {{ .Values.pg1.db.url }}:{{ .Values.pg1.db.port }}
        database: {{ .Values.pg1.db.database }}
        user: {{ .Values.pg1.db.user }}
        secureJsonData:
          password: {{ .Values.pg1.db.password }}
        sslmode: verify-full
        jsonData:
          postgresVersion: 1400 # 903=9.3, 904=9.4, 905=9.5, 906=9.6, 1000=10
          timescaledb: true
EOF
~~~

# prometheus CRD资源

## 常见CRD资源

- Prometheus：定义prometheus实例，方便配置管理。（生产环境建议单独找一台机器安装）
- alertmanager：定义alertmanager实例（体量比较小，直接部署即可，副本数设为3即可。）
- ServiceMonitor：定义获取监控数据的service目标，Operator根据ServiceMonitor自动生成Prometheus配置
- PodMonitor：监控一组动态的pod（可能因为这些pod没有前端svc），直接生成prometheus配置来进行监控。
- Probe：定义静态目标，通常和BlackBox Exporter配合使用（比如，在用户角度去探测一个域名/tcp端口是不是可用，访问速度慢不慢等等）
- ScrapeConfig：用于自定义监控目标，抓取K8s集群外部的目标
- AlertmanagerConfig：定义Alertmenegr告警规则
- PrometheusRule：定义告警规则（用promQL去写）

## CRD更新说明

For kube-prometheus-stack: CRDs are firstly extracted from helm charts then installed independently using kubectl apply, which is defined in pipelines.

The reason for installing CRDs separately is that based on [helm document](https://helm.sh/docs/topics/charts/#limitations-on-crds), CRDs will only be installed one time on the fresh install, after which helm will not re-install nor upgrade them during helm chart upgrade. But azure_global considers that not updating CRDs is more breaking than doing it.

Then they suggests that CRDs can be extracted from the helm package and be installed using kubectl apply.

## service/pod monitor

### serviceMonitor

Service Monitor 是 Prometheus Operator 提供的CRD，负责从其他service暴露的接口上抓取数据。可以动态生成prometheus配置，加载到prometheus当中。通过selector找到对应标签的service。

> 注意：
>
> - service在哪个ns，serviceMonitor就创建到哪个ns下面，这是标准的配置。
> - 有可能svc的metrics接口需要证书、认证等。可以配置secret去配置。

- 介绍：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#prometheusioscrape

- 使用说明：https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/user-guides/getting-started.md#include-servicemonitors （app需要用service暴露metrics接口，然后定义serviceMonitor资源去抓取接口数据）

### podMonitor


pod monitor绕过了service，直接通过pod的label找到pod，抓取pod暴露的metrics接口：

https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/user-guides/getting-started.md#using-podmonitors

podMonitor推荐创建在与pod位于同一个ns下面。（与pod同生命周期，防止产生很多垃圾资源）

~~~yaml
apiVersion: monitoring.coreos.com/v1 
kind: PodMonitor 
metadata: 
  name: example-app 
  labels: 
    team: frontend 
spec: 
  selector: 
    matchLabels: 
      app: example-app 
  podMetricsEndpoints: 
  - targetPort: 8080 
~~~

### 监控流程设计

1. 云原生应用：`/metrics`（serviceMonitor用的比较多）
2. 非云原生应用：部署`exporter`，exporter本身会暴露metrics接口

## Probe

serviceMonitor和PodMonitor属于白盒监控，监控svc和pod自己暴露出来的metrics接口。

Probe属于黑盒监控。通常和BlackBox Exporter配合使用（比如，在用户角度去探测一个域名/tcp端口是不是可用，访问速度慢不慢等等。不关心内部逻辑，只关心表面状态）

~~~yaml
apiVersion: monitoring.coreos.com/v1
kind: Probe
metadata:
  name: probe-test
  namespace: monitoring
spec:
  jobName: probe-test
  interval: 30s
  module: http_2xx
  prober:
    url: http://blackbox-exporter.monitoring:9115/probe # 专门监控域名的exporter
    scheme: http
    path: /probe
    params:
      module: [http_2xx]
  targets:
    staticConfig:
      static:
      - https://www.kubeasy.com
~~~

## ScrapeConfig

有一些服务是安装在集群外部的，无法直接用podMonitor监控，serviceMonitor也得先创建一个指向外部的service，比较麻烦。Prometheus提供了ScrapeConfig可以采集外部服务的指标。

~~~yaml
apiVersion: monitoring.coreos.con/v1alpha1
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
    - redis://redis.default:6379 # 写exporter的地址
    labels:
      env: test
    relabelings: # 替换掉prometheus中默认的标签
      - sourceLabels: [__address__]
        targetLabel: __param_target
      - sourceLabels: [__param_target]
        targetLabel: instance
      - targetLabel: __address__
        replacement: redis-exporter.monitoring:9121
~~~

## PrometheusRule

PrometheusRule是Prometheus Operator中定义的CRD。有一个专门的网站可以查看各种各样的开源CRD的定义：https://operatorhub.io/operator/prometheus

- Alerting Rule：定义监控数据的条件，当这些条件满足时触发告警。
- Recording Rule：定期将复杂规则的查询结果保存成一个新的时间序列，为了优化查询性能。比如，将一段时间内的平均CPU使用率保存为一个新指标。

### 自带PrometheusRule

kube-prometheus-stack的helm chart自带一些PrometheusRUle，模板文件保存在：kube-prometheus-stack/templates/prometheus/rules-1.14目录下，如果有想去掉的rule就在里面删掉。

这些告警的激活情况可以在prometheus UI界面的Alerts里面查看。 

### helm安装自定义PrometheusRule

./Chart.yaml文件

~~~yaml
apiVersion: v2
name: commoninfra-kube-prometheus-config
description: A Helm chart for kube prometheus configurations
type: application
version: 1.0.0
appVersion: "1.0.0"
~~~

./templates/PrometheusRule-monitoring.yaml：

~~~yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: loki
  namespace: monitoring
spec:
  groups: # 对不同类型的告警规则进行监控。建议对不同种类监控，直接创建新的prometheusRule yaml。
    - name: loki-prometheus # 定义规则组的名称，建议同一个yaml里面就写一个group就行了
      rules: # 规则列表，定义具体的告警规则
        - alert: LokiStorageHigh #告警名称
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"storage-loki.*"} / 1024 / 1024 / 1024 < 5 #PromQL表达式，描述触发告警的条件
          labels:
            severity: warning
            namespace: monitoring
          annotations:
            summary: "Loki storage is high"
            description: "Loki storage is high. Please review retention defaults"
            runbook: https://xxx
        - alert: LokiStorageVeryHigh
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"storage-loki.*"} / 1024 / 1024 / 1024 < 1
          labels:
            severity: warning
            namespace: monitoring
          annotations:
            summary: "Loki storage is very high"
            description: "Loki storage is very high and is about to auto-expand. Please consider changing retention/storage/alert defaults"
            runbook:  https://xxxx
        - alert: PrometheusStorageHigh
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"prometheus-kube-prometheus-stack-prometheus-db.*"} / 1024 / 1024 / 1024 < 5
          labels:
            severity: warning
            namespace: monitoring
          annotations:
            summary: "Prometheus storage is high"
            description: "Prometheus storage is high. Please consider adding more storage"
            runbook: https://xxxxx
        - alert: PrometheusStorageVeryHigh
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"prometheus-kube-prometheus-stack-prometheus-db.*"} / 1024 / 1024 / 1024 < 1
          labels:
            severity: critical
            namespace: monitoring
          annotations:
            summary: "Prometheus storage is very high"
            description: "Prometheus storage is very high. Please add more storage"
            runbook: https://xxxxx
~~~

./templates/PrometheusRule-ArgoCD.yaml

~~~yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: argocd-rules
  namespace: monitoring
  labels:
    prometheus: k8s
    role: alert-rules
    app.kubernetes.io/name: argocd
    app.kubernetes.io/part-of: argocd
spec:
  groups:
  - name: argocd.rules
    rules:
    # ArgoCD Application Controller 高延迟告警
    - alert: ArgoCDApplicationControllerHighLatency
      expr: histogram_quantile(0.95, rate(argocd_app_controller_reconciliation_duration_seconds_bucket[5m])) > 1
      for: 2m # 持续时长为2min才会触发告警
      labels:
        severity: warning
      annotations:
        summary: "ArgoCD Application Controller Reconciliation Latency High ({{ $labels.namespace }})"
        description: "The reconciliation latency for ArgoCD application controller in namespace {{ $labels.namespace }} is over 1 second for more than 2 minutes."

    # ArgoCD Server 高请求错误率告警
    - alert: ArgoCDServerHighRequestErrorRate
      expr: rate(argocd_server_http_requests_total{status=~"5.*"}[5m]) > 0.05
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "ArgoCD Server High Error Rate ({{ $labels.namespace }})"
        description: "The ArgoCD server in namespace {{ $labels.namespace }} has an HTTP error rate over 5% for the past 5 minutes."

    # ArgoCD Repo Server 同步失败告警
    - alert: ArgoCDRepoServerSyncFailed
      expr: increase(argocd_repo_server_git_request_failures_total[5m]) > 5
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "ArgoCD Repo Server Sync Failures ({{ $labels.namespace }})"
        description: "ArgoCD Repo Server in namespace {{ $labels.namespace }} has more than 5 sync failures in the last 5 minutes."

    # ArgoCD Dex Server 不可用告警
    - alert: ArgoCDDexServerDown
      expr: up{job="argocd-dex-server"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "ArgoCD Dex Server Down ({{ $labels.namespace }})"
        description: "The ArgoCD Dex Server in namespace {{ $labels.namespace }} is not running for more than 1 minute."

    # ArgoCD Application 运行失败告警
    - alert: ArgoCDApplicationOutOfSync
      expr: argocd_app_info{health_status!="Healthy"} > 0
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "ArgoCD Applications Out of Sync ({{ $labels.namespace }})"
        description: "There are applications in ArgoCD that are not in a healthy state for more than 5 minutes."
~~~

~~~sh
helm upgrade -i commoninfra-kube-prometheus-config -n kube-system . --values ./values/dev.chinanorth3.yaml
~~~

### ruleSelector

- 创建完PrometheusRule之后，rules文件会被自动加载到`prometheus-kube-prometheus-stack-prometheus-0`这个pod的如下目录中：

  ~~~sh
  cd /etc/prometheus/rules/prometheus-kube-prometheus-stack-prometheus-rulefiles-0
  ~~~

- 怎么判断加载哪些prometheusRule呢？

  - prometheus-stack的values文件中有一个`ruleSelector`的选项，通过标签选择器来匹配PrometheusRule资源。
  - 默认情况下不做配置：匹配所有PrometheusRule资源

## AlertmanagerConfig

~~~yaml
apiVersion: monitoring.coreos.con/v1alpha1
kind: AlertmanagerConfig
metadata:
  name: example-alertmanagerconfig
  namespace: monitoring
spec:
  route:
    receiver: team-email # 根路由，默认receiver。如果没有被下面的routes匹配到，就往这里发
    groupBy: [type] # 告警有不同的种类，比如cpu、内存等，他们都是属于某个节点的，就可以打包同一节点的告警（type=node），避免告警轰炸。
    routes:
    - matchers:
      - matchType: =
        name: serverity
        value: critical
      receiver: critical-email
    - continue: true
      matchers:
      - name: slack
        regex: true
        value: ^[@#a-z0-9][a-z0-9._-]*$
      receiver: slack-team-receiver
  receivers: # 上面的receiver都需要在这里有定义
  - name: team-email
    emailConfigs:
    - to: team@example.com
      from: alertmanager@example.com
      smarthost: smtp.example.com:587
      authUsername: user
      authPassword:
        secretKeyRef:
          name: email-secret
          key: password
~~~

# target down排查流程

一般是从prometheus中看到target是down的状态。

1. 首先看对应的pod是不是正常Running
2. 看serviceMonitor，找到namespaceSelector、selector，去对应的ns里面找对应标签的svc
3. 确认能通过svc访问到metrics接口
4. 确认svc的端口和scheme、serviceMonitor的一致

# 告警规则实战

## 使用技巧

有很多监控语法可能比较复杂，此时可以借助现有的Dashboard编写PrometheusRule。比如想要实现主机内存的监控，可以先从面板点击edit获取PromQL语法，复制出来稍加改动就能获取到PromQL的计算公式。再去放到PrometheusRule里面就行。

## 常用监控告警文件

~~~yaml
    groups:
    - name: example
      rules:
      - alert: HighNginxServerRequests
        expr: sum(irate(nginx_server_requests{instance=~"192.168.40.180:9913", code="2xx"}[5m])) by (code)>1000
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "High Nginx Server Requests"
          description: "在最近2s钟时间,nginx服务请求数达到了1000次"
    - name: 物理节点状态-监控告警
      rules:
      - alert: 物理节点cpu使用率
        expr: 100-avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) by(instance)*100 > 20
        for: 2s
        labels:
          severity: ccritical
        annotations:
          summary: "{{ $labels.instance }}cpu使用率过高"
          description: "{{ $labels.instance }}的cpu使用率超过20%,当前使用率[{{ $value }}],需要排查处理" 
      - alert: 物理节点内存使用率
        expr: (node_memory_MemTotal_bytes - (node_memory_MemFree_bytes + node_memory_Buffers_bytes + node_memory_Cached_bytes)) / node_memory_MemTotal_bytes * 100 > 50
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }}内存使用率过高"
          description: "{{ $labels.instance }}的内存使用率超过60%,当前使用率[{{ $value }}],需要排查处理"
      - alert: InstanceDown
        expr: up == 0
        for: 2s
        labels:
          severity: critical
        annotations:   
          summary: "{{ $labels.instance }}: 服务器宕机"
          description: "{{ $labels.instance }}: 服务器延时超过2分钟"
      - alert: 物理节点磁盘的IO性能
        expr: 100-(avg(irate(node_disk_io_time_seconds_total[1m])) by(instance)* 100) < 60
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流入磁盘IO使用率过高！"
          description: "{{$labels.mountpoint }} 流入磁盘IO大于60%(目前使用:{{$value}})"
      - alert: 入网流量带宽
        expr: ((sum(rate (node_network_receive_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr*|lo*'}[5m])) by (instance)) / 100) > 102400
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流入网络带宽过高！"
          description: "{{$labels.mountpoint }}流入网络带宽持续5分钟高于100M. RX带宽使用率{{$value}}"
      - alert: 出网流量带宽
        expr: ((sum(rate (node_network_transmit_bytes_total{device!~'tap.*|veth.*|br.*|docker.*|virbr*|lo*'}[5m])) by (instance)) / 100) > 102400
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 流出网络带宽过高！"
          description: "{{$labels.mountpoint }}流出网络带宽持续5分钟高于100M. RX带宽使用率{{$value}}"
      - alert: TCP会话
        expr: node_netstat_Tcp_CurrEstab > 1000
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} TCP_ESTABLISHED过高！"
          description: "{{$labels.mountpoint }} TCP_ESTABLISHED大于1000%(目前使用:{{$value}}%)"
      - alert: 磁盘容量
        expr: 100-(node_filesystem_free_bytes{fstype=~"ext4|xfs"}/node_filesystem_size_bytes {fstype=~"ext4|xfs"}*100) > 80
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "{{$labels.mountpoint}} 磁盘分区使用率过高！"
          description: "{{$labels.mountpoint }} 磁盘分区使用大于80%(目前使用:{{$value}}%)"
      - alert: apiserver的cpu使用率大于90%
        expr: rate(process_cpu_seconds_total{job=~"kubernetes-apiserver"}[1m]) * 100 > 0
        for: 2s
        labels:
          severity: warnning
        annotations:
          description: "{{$labels.instance}}的{{$labels.job}}组件的cpu使用率超过80%"
      - alert: 容器内存使用率
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100 > 0
        for: 2s
        labels:
          severity: critical
        annotations:
          summary: "High Container Memory Usage"
          description: "Container memory usage is above 90%."
~~~

> - https://github.com/samber/awesome-prometheus-alerts
>
>   这个项目中包含了常见组件的prometheus alerts

## 域名访问延迟及故障告警

~~~yaml
apiVersion: monitoring.coreos.com/v1 
kind: PrometheusRule 
metadata: 
  name: blackbox  
  namespace: monitoring 
  labels: 
    app.kubernetes.io/component: exporter 
    app.kubernetes.io/name: blackbox-exporter 
    prometheus: k8s 
    role: alert-rules 
spec: 
  groups: 
  - name: blackbox-exporter 
    rules: 
    - alert: DomainCannotAccess 
      annotations: 
        description:  域名：{{ $labels.instance }} 不可达 # 从指标的label中取值
        summary: 域名探测失败
      expr: probe_success == 0 
      for: 1m 
      labels: 
        severity: critical 
        type: blackbox 
    - alert: DomainAccessDelayExceeds1s 
      annotations: 
        description:  域名：{{ $labels.instance }} 探测延迟大于1秒，当前延迟为：{{ $value }} 
        summary: 域名探测，访问延迟超过1秒  
      expr: sum(probe_http_duration_seconds{job=~"blackbox"}) by (instance) > 1  
      for: 1m 
      labels: 
        severity: warning 
        type: blackbox 
~~~

## 应用活性探测

针对基础组件也可以实现活性探测，用exporter采集数据的组件，比如MySQL和Redis监控，可以通过up指标进行监控：

~~~yaml
apiVersion: monitoring.coreos.com/v1 
kind: PrometheusRule 
metadata: 
  labels: 
    prometheus: k8s 
    role: alert-rules 
  name: basic 
  namespace: monitoring 
spec: 
  groups: 
  - name: mysql # 按照组件类型去分组
    rules: 
    - alert: MySQLStatus 
      annotations: 
        description:  实例：{{ $labels.instance }} 故障 
        summary: MySQL 服务宕机 
      expr: mysql_up == 0 
      for: 1m 
      labels: 
        severity: critical 
        type: basic 
        component: mysql 
  - name: redis 
    rules: 
    - alert: RedisStatus 
      annotations: 
        description:  实例：{{ $labels.instance }} 故障 
        summary: Redis 服务宕机 
      expr: redis_up == 0 
      for: 1m 
      labels: 
        severity: critical 
        type: basic 
        component: redis 
~~~

# Alertmanager配置与实战

示例文件：[alertmanager/doc/examples/simple.yml at main · prometheus/alertmanager](https://github.com/prometheus/alertmanager/blob/main/doc/examples/simple.yml)

官网说明：[Alerting Routes - Prometheus Operator](https://prometheus-operator.dev/docs/developer/alerting/)

## 模板字段

~~~yaml
# Global：全局配置，主要用来配置一些通用的配置，比如邮件通知的账号、密码、SMTP服务器、微信告警等。Global 块配置下的配置选项在本配置文件内的所有配置项下可见，但是文件内其它位置的子配置可以覆盖Global配置
global: 
  resolve_timeout: 5m 
  ... 
# Route：告警路由配置，用于告警信息的分组路由，可以将不同分组的告警发送给不同的收件人。比如将数据库告警发送给DBA，服务器告警发送给OPS
route: 
  receiver: Default 
  group_by: 
  - namespace 
  - job 
  - alertname 
  group_wait: 30s 
  group_interval: 5m 
  repeat_interval: 10m 
  routes: 
    - matchers: 
        - service=~"foo1|foo2|baz" 
      receiver: team-X-mails 
      routes: 
        - matchers: 
            - severity="critical" 
          receiver: team-X-pager 
# Inhibit_rules：告警抑制，主要用于减少告警的次数，防止“告警轰炸”。比如某个宿主机宕机，可能会引起容器重建、漂移、服务不可用等一系列问题，如果每个异常均有告警，会一次性发送很多告警，造成告警轰炸，并且也会干扰定位问题的思路，所以可以使用告警抑制，屏蔽由宿主机宕机引来的其他问题，只发送宿主机宕机的消息即可
inhibit_rules: 
  - source_matchers: [severity="critical"] 
    target_matchers: [severity="warning"] 
    equal: [alertname, cluster, service] 
#eceivers：告警收件人配置，每个receiver都有一个名字，经过route分组并且路由后需要指定一个receiver，就是在此位置配置的
receivers: 
- name: Default 
  email_configs: 
  - send_resolved: true 
    to: kubernetes_guide@163.com 
    from: kubernetes_guide@163.com 
    hello: 163.com 
    smarthost: smtp.163.com:465 
    auth_username: kubernetes_guide@163.com 
    auth_password: <secret> 
    headers: 
      From: kubernetes_guide@163.com 
      Subject: '{{ template "email.default.subject" . }}' 
      To: kubernetes_guide@163.com 
    html: '{{ template "email.default.html" . }}' 
    require_tls: false 
  - name: Watchdog 
  - name: Critical 
# Templates：用于放置自定义模板的位置
 templates: [] 
~~~

## Route路由规则

~~~yaml
route: 
  # 告警的通知目标，需要和 receivers 配置中 name 进行匹配。、
  # 需要注意的是route.routes下也可以有receiver配置，优先级高于route.receiver配置的默认接收人。当告警没有匹配到子路由时，会使用route.receiver进行通知
  receiver: Default 
  # 分组配置，值类型为列表。比如配置成['job', 'severity']，代表告警信息包含job和severity标签的会进行分组，且标签的key和value都相同才会被分到一组
  group_by: 
  - namespace 
  - job 
  - alertname 
  routes: # 子路由树，用于详细的告警路由
  - matchers: # matchers：匹配规则
    - owner="team-X" 
    receiver: team-X-pager # 局部收件人 
    continue: false # 决定匹配到该路由后，是否继续后续匹配。默认为false，即匹配到后停止继续匹配
  - matchers: 
    - owner="team-Y" 
    receiver: team-Y-pager  
  group_wait: 30s # 告警通知等待。若一组新的告警产生，则会等group_wait后再发送通知，该功能主要用于当告警在很短时间内接连产生时，在group_wait内合并为单一的告警后再发送，防止告警过多，默认值30s
  group_interval: 5m # 同一组告警通知后，如果有新的告警添加到该组中，不会立即发送。而是等一段时间再发送。默认值为5m 
  repeat_interval: 10m # 如果一条告警通知已成功发送，且在间隔 repeat_interval 后，该告警仍然未被设置为resolved，则会再次发送该告警通知，默认值4h
~~~

## Slience

比如晚上一段时间进行例行维护，肯定会引发一些告警，但是我们希望在这段维护窗口不发送告警，可以在alertmanager UI界面的Silence里面，配置matcher匹配哪些标签的告警不发送，配置多长的时间段。

## 发送告警到邮件

邮件通知需要先开启邮箱服务的IMAP/SMTP服务。

### 基于yaml文件配置邮件告警

找到Alertmanager的配置文件，添加邮箱服务配置：

~~~yaml
# cat alertmanager-secret.yaml 
 alertmanager.yaml: |- 
    "global": 
      "resolve_timeout": "5m" 
      smtp_from: "xxx@163.com" 
      smtp_smarthost: "smtp.163.com:465" 
      smtp_hello: "163.com" 
      smtp_auth_username: "xxx@163.com" 
      smtp_auth_password: "xxx" 
      smtp_require_tls: false
~~~

之后将名称为Default的receiver配置更改为邮件通知，修改alertmanager-secret.yaml文件 的receivers配置如下：

~~~yaml
"receivers": 
- "name": "Default" 
   "email_configs": # 代表使用邮件通知
   - to: "xxx@163.com" # 收件人，可以配置多个，逗号隔开
     send_resolved: true # 告警如果被解决是否发送解决通知
~~~

加载配置：

~~~sh
kubectl replace -f alertmanager-secret.yaml
~~~

稍等几分钟即可在Alertmanager的Web界面看到更改的配置（Status）

### AlertmanagerConfig实现邮件告警

前面的配置都是在添加邮件告警的服务配置，路由规则等。没有涉及具体的告警指标。如果需要将西定义的告警发送至邮件，可以使用AlertmanagerConfig进行单独配置，比如将Blackbox的告警发送至邮箱。

首先更改Alertmanager的配置。要配置成写了alertmanagerConfig=example的告警规则才会被alertmanager加载。 

~~~yaml
vim kube-prometheus/manifests/alertmanager-alertmanager.yaml 
replicas: 1 
alertmanagerConfigSelector: 
  matchLabels: 
    alertmanagerConfig: example 
~~~

接下来添加AlertmanagerConfig：

~~~yaml
apiVersion: monitoring.coreos.com/v1alpha1 
kind: AlertmanagerConfig 
metadata: 
  name: blackbox 
  namespace: monitoring
  labels: 
    alertmanagerConfig: example
spec: 
  route: 
    groupBy: ['type'] # 因为产生的告警是有type标签的，用他来进行分组
    groupWait: 30s 
    groupInterval: 5m 
    repeatInterval: 12h 
    routes: 
    - matchers: 
      - matchType: = 
        name: type 
        value: blackbox 
      receiver: Default # 只有type=blackbox的告警，才会被Default这个receiver进行通知
  receivers: 
  - name: Default 
    emailConfigs: 
    - to: xxx@163.com 
      sendResolved: true
~~~



## 发送告警到slack

> - prometheus与slack集成的配置文件说明：https://prometheus.io/docs/alerting/latest/configuration/#slack_config
> - slack web API说明：https://api.slack.com/web
> - slack web API认证：https://api.slack.com/web#authentication
> - chat.postMessage API文档：https://api.slack.com/methods/chat.postMessage
> - bot token: https://api.slack.com/concepts/token-types#bot

### Slack端配置

1. Slack workspace中安装一个App，拿到其Api token（bot token）
2. 创建一个channel用来接收告警信息

### alertmanager端配置

1. 将bot token放到k8s里面：

   - 如果是azure环境下，token被写入到azure keyvault中，k8s用SecretProviderClass将keyvault secret转换成k8s secret，示例如下：

     ~~~yaml
     apiVersion: secrets-store.csi.x-k8s.io/v1
     kind: SecretProviderClass
     metadata:
       name: sp-alertmanager
       namespace: monitoring
     spec:
       provider: azure
       parameters:
         usePodIdentity: "false"
         useVMManagedIdentity: "true" #采用MI的认证方式，secretProviderClass在azure中有默认创建的MI以供使用
         userAssignedIdentityID: <secretProviderIdentityId> # Set the clientID of the user-assigned managed identity to use, e.g. azurekeyvaultsecretsprovider-aks-commoninfra-dev-westeurope
         keyvaultName: <keyvaultName>
         cloudName: <cloudName>
         objects:  |
           array:
             - |
               objectName: <the object name of keyvault>
               objectType: secret
               objectVersion: ""
     
         tenantId: "<tenant-id>"
       # This creates an actual secret that we can use
       secretObjects:
       - secretName: <actual-secret-name>
         data:
         - key: <key-name-of-the-secret> # add a secret referencable with the same key as was in the keyvault
           objectName: <same-object-name-with-above-objectName>
         type: Opaque
     ~~~

   - 本地环境下，直接把token做成secret

     ~~~sh
     #Opaque类型的secret只接受base64类型的string，先转一下token到base64
     echo -n 'xxxxx' | base64
     ~~~

     ~~~yaml
     apiVersion: v1
     kind: Secret
     metadata:
       name: <secret-name>
       namespace: monitoring
     type: Opaque
     data:
       token:
     ~~~

2. kube-prometheus-stack的values.yaml中alertmanager部分配置slack

   ~~~yaml
   alertmanager:
   ...
     ## Alertmanager configuration directives
     ## ref: https://prometheus.io/docs/alerting/configuration/#configuration-file
     ##      https://prometheus.io/webtools/alerting/routing-tree-editor/
     ##
     config:
       global:
         resolve_timeout: 5m
         slack_api_url: https://slack.com/api/chat.postMessage
         http_config:
           authorization:
             credentials_file: '/mnt/secrets-store/<key-name-of-secret>' #这里的文件名需要和secret的keyname相一致
       inhibit_rules:
         - source_matchers:
             - 'severity = critical'
           target_matchers:
             - 'severity =~ warning|info'
           equal:
             - 'namespace'
             - 'alertname'
         - source_matchers:
             - 'severity = warning'
           target_matchers:
             - 'severity = info'
           equal:
             - 'namespace'
             - 'alertname'
         - source_matchers:
         # alertmanager自带一条alert: InfoInhibitor，作用是压制Info level的alert。
         # 背景：info的alert正常情况下会noisy，但是每当有warning/critical的alert出现时，info又会提供有价值的信息。
         # 在同一个namespace下，InfoInhibitor会在Info alert触发之后触发，压制Info alert；但又会在有warning/critical出现后停止触发，不压制那时的Info alert。
         # Refer to: https://runbooks.prometheus-operator.dev/runbooks/general/infoinhibitor/
             - 'alertname = InfoInhibitor'
           target_matchers:
             - 'severity = info'
           equal:
             - 'namespace'
       route:
         receiver: 'null'
   ...
       receivers:
       - name: 'null'
       - name: platform-slack
         slack_configs:
           - channel: '#<channel-name>'
             send_resolved: true
             title: '{{ template "slack.xxx.title" . }}'
             text: '{{ template "slack.xxx.text" . }}'
       - name: platform-slack-info
         slack_configs:
           - channel: '#<channel-name>'
             send_resolved: true
             title: '{{ template "slack.xxx.title" . }}'
             text: '{{ template "slack.xxx.text" . }}'
       templates:
       - '/etc/alertmanager/config/*.tmpl'
   ...
     ## Alertmanager template files to format alerts
     ## By default, templateFiles are placed in /etc/alertmanager/config/ and if
     ## they have a .tmpl file suffix will be loaded. See config.templates above
     ## to change, add other suffixes. If adding other suffixes, be sure to update
     ## config.templates above to include those suffixes.
     ## ref: https://prometheus.io/docs/alerting/notifications/
     ##      https://prometheus.io/docs/alerting/notification_examples/
     ##
     templateFiles:
       default_title.tmpl: |-
         {{ define "slack.xxx.title" }}
         {{ .CommonLabels.alertname }} - {{ .Alerts.Firing | len }} in {{ .CommonLabels.namespace }}
         {{ end }}
       default_text.tmpl: |-
         {{ define "slack.xxx.text" }}
         {{ range .Alerts }}
         `{{ .Labels.severity }}` - {{ .Annotations.summary }}
         *Description:* {{ .Annotations.description }}
         {{ if match `^http.+` .GeneratorURL }}*Graph:* <{{ .GeneratorURL }}|:chart_with_upwards_trend:> {{ end }}{{ if .Annotations.runbook }}*Runbook:* <{{ .Annotations.runbook }}|:spiral_note_pad:>{{ end }}
         *Details:*
           {{ range .Labels.SortedPairs }} • *{{ .Name }}:* `{{ .Value }}`
           {{ end }}
         {{ end }}
         {{ end }}
   
       # Additional volumes on the output StatefulSet definition.
       volumes:
         - name: <volume-name>
           csi:
             driver: secrets-store.csi.k8s.io
             readOnly: true
             volumeAttributes:
               secretProviderClass: "sp-alertmanager"
   
       # Additional VolumeMounts on the output StatefulSet definition.
       volumeMounts:
         - name: <volume-name>
           mountPath: "/mnt/secrets-store"
           readOnly: true
   ~~~

3. 验证slack端是否可以接收到告警信息

### 发送告警到企业微信

#### 企业微信配置

1. 首先需要在企业微信官网注册企业微信账号：https://work.weixin.qq.com/。
2. 注册完成后进行登录，登录后点击我的企业。
3. 在页面的最下面找到企业ID（corp_id）并记录，稍后会用到。
4. 之后创建一个部门，用于接收告警通知。
5. 查看该部门ID（to_party）并记录。
6. 之后创建机器人应用，首先点击应用管理→应用创建，选择一个logo，输入应用名称和选择可见范围。
7. 创建完成后，查看AgentId和Secret（api_secret）并记录。点击查看Secret，企业微信会将Secret发送至企业微信。

接下来需要在企业微信添加可信域名，并且需要完成网页授权。网页授权的条件如下：

1. 必须要有一个公网可以访问的域名（需要是已经备案的域名）：开发者接口 - 设置可信域名
1. 将授权文件放在域名的根目录下，也就是通过http(s)://你的域名/xxx.txt可以直接访问到该文件 。

最后还需要添加信任IP（是alertmanager所在的主机的出口公网IP地址），首先在所有的K8s节点上获取公网IP：`curl ifconfig.me`，在开发者接口 - 企业可信IP添加进去。

#### Alertmanager配置

企业微信配置完成后，修改Alertmanager配置文件，添加企业微信告警。

首先修改Global，添加一些通用配置，wechat_api_url是固定配置，corp_id为企业ID：

~~~yaml
   "global": 
      "resolve_timeout": "5m" 
     ... 
      wechat_api_url: "https://qyapi.weixin.qq.com/cgi-bin/"  
      wechat_api_corp_id: "wwef86a30130f04f2b"

# kubectl replace -f kube-prometheus/manifests/alertmanager-secret.yaml 
~~~

#### AlertmanagerConfig配置告警通知

首先需要创建的微信密钥的Secret：

~~~sh
kubectl create secret generic webchat-secret --from-literal=secret=xxx -n monitoring
~~~

示例，将mysql和redis的告警发送至企业微信：

~~~yaml
apiVersion: monitoring.coreos.com/v1alpha1 
kind: AlertmanagerConfig 
metadata: 
  name: basic
  namespace: monitoring
  labels: 
    alertmanagerConfig: example 
spec: 
  route: 
    groupBy: ['type'] 
    groupWait: 30s 
    groupInterval: 5m 
    repeatInterval: 12h 
    routes: 
    - matchers: 
      - matchType: =  
        name: type 
        value: "basic" 
      receiver: Wechat 
  receivers: 
  - name: Wechat 
    wechatConfigs: 
      - sendResolved: true 
        toParty: "4" 
        toUser: '@all' 
        agentID: "1000008" 
        apiSecret:  
          key: "secret" 
          name: "webchat-secret" 
~~~

此处配置的receiver名字为wechat，toUser为@all，代表发送给所有人，也可以只发送给 部门的某一个人，只需要将此处改为USER_ID即可。

#### 自定义微信告警信息

首先修改alertmanager的全局配置文件alertmanager-secret.yaml，在stringData下面新添加一个自定义模板： 

~~~yaml
app.kubernetes.io/part-of: kube-prometheus 
app.kubernetes.io/version: 0.21.0 
name: alertmanager-main 
namespace: monitoring 
stringData: 
  wechat.tmpl: |- 
    {{ define "wechat.default.message" }} 
    {{- if gt (len .Alerts.Firing) 0 -}} 
    {{- range $index, $alert := .Alerts -}} 
    {{- if eq $index 0 }} 
    ==========异常告警========== 
    告警类型: {{ $alert.Labels.alertname }} 
    告警级别: {{ $alert.Labels.severity }} 
    告警详情: {{ $alert.Annotations.message }}{{ $alert.Annotations.description}};{{$alert .Annotations.summary}} 
    故障时间: {{ ($alert.StartsAt.Add 28800e9).Format "2006-01-02 15:04:05" }} 
{{- if gt (len $alert.Labels.instance) 0 }} 
    实例信息: {{ $alert.Labels.instance }} 
    {{- end }} 
    {{- if gt (len $alert.Labels.namespace) 0 }} 
    命名空间: {{ $alert.Labels.namespace }} 
    {{- end }} 
    {{- if gt (len $alert.Labels.node) 0 }} 
    节点信息: {{ $alert.Labels.node }} 
    {{- end }} 
    {{- if gt (len $alert.Labels.pod) 0 }} 
    实例名称: {{ $alert.Labels.pod }} 
    {{- end }} 
    ============END============ 
    {{- end }} 
    {{- end }} 
    {{- end }} 
    {{- if gt (len .Alerts.Resolved) 0 -}} 
    {{- range $index, $alert := .Alerts -}} 
    {{- if eq $index 0 }} 
    ==========异常恢复========== 
    告警类型: {{ $alert.Labels.alertname }} 
    告警级别: {{ $alert.Labels.severity }} 
    告警详情: {{ $alert.Annotations.message }}{{ $alert.Annotations.description}};{{$alert .Annotations.summary}} 
    故障时间: {{ ($alert.StartsAt.Add 28800e9).Format "2006-01-02 15:04:05" }} 
    恢复时间: {{ ($alert.EndsAt.Add 28800e9).Format "2006-01-02 15:04:05" }} 
    {{- if gt (len $alert.Labels.instance) 0 }} 
    实例信息: {{ $alert.Labels.instance }} 
    {{- end }} 
    {{- if gt (len $alert.Labels.namespace) 0 }} 
    命名空间: {{ $alert.Labels.namespace }} 
    {{- end }} 
    {{- if gt (len $alert.Labels.node) 0 }} 
    节点信息: {{ $alert.Labels.node }} 
    {{- end }} 
    {{- if gt (len $alert.Labels.pod) 0 }} 
    实例名称: {{ $alert.Labels.pod }} 
    {{- end }} 
    ============END============ 
    {{- end }} 
    {{- end }} 
    {{- end }} 
    {{- end }} 
  alertmanager.yaml: |- 
    "global": 
      "resolve_timeout": "5m" 
      ......
~~~

在template字段添加模板位置：

~~~yaml
    templates: 
    - '/etc/alertmanager/config/*.tmpl' 
    "inhibit_rules": 
    ......
~~~

加载配置文件：

~~~sh
kubectl replace -f alertmanager-secret.yaml -n monitoring 
~~~

接下来在AlertmanagerConfig配置中指定这个自定义模板：

~~~yaml
  receivers: 
  - name: Wechat 
    wechatConfigs: 
      - sendResolved: true 
        toParty: "4" 
        toUser: '@all' 
        agentID: "1000008" 
        apiSecret:  
          key: "secret" 
          name: "webchat-secret" 
        message: '{{ template "wechat.default.message" . }}'
~~~

~~~sh
kubectl replace -f basic-alertmanagerconfig.yaml  -n monitoring
~~~

> 注意：{{ template "wechat.default.message" . }} 配置的 wechat.default.message，是模板文件里面通过 define 定义的名称：{{ define "wechat.default.message" }}，并非文件名称。 

## 发送告警到钉钉

alertmanager原生不支持钉钉，所以用webhook去发送告警

使用钉钉告警，需要先创建一个群聊，然后添加一个自定义机器人： 

1. 安全设置 - 加签的值复制出来
2. 添加完成后，webhook地址复制出来

下载钉钉Webhook服务部署文件：

~~~sh
git clone https://github.com/timonwong/prometheus-webhook-dingtalk.git
cd prometheus-webhook-dingtalk/contrib/k8s/ 
# 修改配置
vim config/config.yaml
# targets.webhook1.url写上webhook的url
# targets.webhook1.secret写上加签的值 （webhook1就写这俩字段）
# 如果有很多个钉钉群，就写上webhook2、3、4以此类推
~~~

安装：

~~~sh
kubectl kustomize | kubectl apply -f - -n monitoring
~~~

pod创建完成之后就可以创建alertmanagerConfig：

~~~yaml
apiVersion: monitoring.coreos.com/v1alpha1 
kind: AlertmanagerConfig 
metadata: 
  name: dingding
  namespace: monitoring
  labels: 
    alertmanagerConfig: example 
spec: 
  route: 
    groupBy: ['alertname'] 
    groupWait: 1m 
    groupInterval: 1m 
    repeatInterval: 1m 
    routes: 
    - matchers: 
      - matchType: "=" 
        name: alertname 
        value: "Watchdog" 
      receiver: dingding-webhook1 
  receivers: 
  - name: dingding-webhook1 
    webhookConfigs: 
      - sendResolved: true 
        # 给webhook的pod的svc发请求即可
        url: http://alertmanager-webhook-dingtalk.monitoring.svc.cluster.local/dingtalk/webhook1/send
~~~

