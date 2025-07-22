# 介绍

- Prometheus Operator 也称为 Kube-Prometheus-Stack。prometheus-community/kube-prometheus-stack Helm Chart 提供了与 kube-prometheus 类似的功能集。该Chart由 Prometheus 社区维护。

- 官网地址：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#kube-prometheus-stack
  - releases page: https://github.com/prometheus-community/helm-charts/releases

  - artifact hub: https://artifacthub.io/packages/helm/prometheus-community/kube-prometheus-stack

- 通过一个prometheus-stack的chart，自动部署prometheus、prometheus rules、Alertmanager以及各种operator；还有kube-state-metrics、grafana、node-exporter。

  - 其中，kube-state-metrics、grafana、node-exporter是通过独立的helm chart安装的：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#dependencies

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
tar xzvf kube-prometheus-stack-52.1.0.tgz
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

~~~yaml
#额外又根据mimer的配置进行了对应调整
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

# Alert-manager发送告警到slack

> - prometheus与slack集成的配置文件说明：https://prometheus.io/docs/alerting/latest/configuration/#slack_config
> - slack web API说明：https://api.slack.com/web
> - slack web API认证：https://api.slack.com/web#authentication
> - chat.postMessage API文档：https://api.slack.com/methods/chat.postMessage
> - bot token: https://api.slack.com/concepts/token-types#bot

## Slack端配置

1. Slack workspace中安装一个App，拿到其Api token（bot token）
2. 创建一个channel用来接收告警信息

## alertmanager端配置

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

# CRD资源使用

## 常见CRD资源

- Prometheus：定义prometheus实例，方便配置管理。（生产环境建议单独找一台机器安装）
- alertmanager：定义alertmanager实例（体量比较小，直接部署即可，副本数设为3即可。）
- ServiceMonitor：定义获取监控数据的service目标，Operator根据ServiceMonitor自动生成Prometheus配置
- PodMonitor：监控一组动态的pod（可能因为这些pod没有前端svc），直接生成prometheus配置来进行监控。
- Probe：定义静态目标，通常和BlackBox Exporter配合使用（比如，在用户角度去探测一个域名/tcp端口是不是可用，访问速度慢不慢等等）
- ScrapeConfig：用于自定义监控目标，抓取K8s集群外部的目标
- AlertmanagerConfig：定义Alertmenegr告警规则
- PrometheusRule：定义告警规则（用promQL去写）

## service/pod monitor

Service Monitor 是 Prometheus Operator 提供的CRD，负责从其他service暴露的接口上抓取数据。可以动态生成prometheus配置，加载到prometheus当中。通过selector找到对应标签的service。

> 注意：
>
> - service在哪个ns，serviceMonitor就创建到哪个ns下面，这是标准的配置。
> - 有可能svc的metrics接口需要证书、认证等。可以配置secret去配置。

- 介绍：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#prometheusioscrape

- 使用说明：https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/user-guides/getting-started.md#include-servicemonitors （app需要用service暴露metrics接口，然后定义serviceMonitor资源去抓取接口数据）


pod monitor绕过了service，直接通过pod的label找到pod，抓取pod暴露的metrics接口：

https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/user-guides/getting-started.md#using-podmonitors

- podMonitor推荐创建在与pod位于同一个ns下面。（与pod同生命周期，防止产生很多垃圾资源）

## PrometheusRule

PrometheusRule是Prometheus Operator中定义的CRD。有一个专门的网站可以查看各种各样的开源CRD的定义：https://operatorhub.io/operator/prometheus

### PrometheusRule的作用

#### Alerting Rule

定义监控数据的条件，当这些条件满足时触发告警。

#### Recording Rule

- 定期将复杂规则的查询结果保存成一个新的时间序列，为了优化查询性能。
- 比如，将一段时间内的平均CPU使用率保存为一个新指标

### helm安装PrometheusRule

#### 自定义helm chart

- ./Chart.yaml文件

  ~~~yaml
  apiVersion: v2
  name: commoninfra-kube-prometheus-config
  description: A Helm chart for kube prometheus configurations
  type: application
  version: 1.0.0
  appVersion: "1.0.0"
  ~~~

- ./templates/PrometheusRule-monitoring.yaml：

~~~yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: loki
  namespace: monitoring
spec:
  groups:
    - name: loki-prometheus #定义规则组的名称
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

- ./templates/PrometheusRule-ArgoCD.yaml

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
      for: 2m #持续时长为2min才会触发告警
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

#### 安装

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

## CRD更新说明

For kube-prometheus-stack: CRDs are firstly extracted from helm charts then installed independently using kubectl apply, which is defined in pipelines.

The reason for installing CRDs separately is that based on [helm document](https://helm.sh/docs/topics/charts/#limitations-on-crds), CRDs will only be installed one time on the fresh install, after which helm will not re-install nor upgrade them during helm chart upgrade. But Mimer considers that not updating CRDs is more breaking than doing it.

Then they suggests that CRDs can be extracted from the helm package and be installed using kubectl apply.
