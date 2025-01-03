# 介绍

- Prometheus Operator 也称为 Kube-Prometheus-Stack。prometheus-community/kube-prometheus-stack Helm Chart 提供了与 kube-prometheus 类似的功能集。该Chart由 Prometheus 社区维护。

- 官网地址：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#kube-prometheus-stack

- 通过一个prometheus-stack的chart，自动部署prometheus、prometheus rules、Alertmanager以及各种operator；还有kube-state-metrics、grafana、node-exporter。

  - 其中，kube-state-metrics、grafana、node-exporter是通过独立的helm chart安装的：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#dependencies

  - [prometheus-community/kube-state-metrics](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-state-metrics)
  - [prometheus-community/prometheus-node-exporter](https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus-node-exporter)
  - [grafana/grafana](https://github.com/grafana/helm-charts/tree/main/charts/grafana)

## values配置

~~~yaml
# 这些设置表示提到的selector（rule、service monitor、pod monitor 和 scrape config）将有独立的配置，并且不会基于 Helm Chart默认 values。
ruleSelectorNilUsesHelmValues: false
serviceMonitorSelectorNilUsesHelmValues: false
podMonitorSelectorNilUsesHelmValues: false
probeSelectorNilUsesHelmValues: false
scrapeConfigSelectorNilUsesHelmValues: false
~~~

## service/pod monitor

- Service Monitor 是 Prometheus Operator 提供的CRD，负责从其他service暴露的接口上抓取数据。介绍：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#prometheusioscrape

- 使用说明：https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/user-guides/getting-started.md#include-servicemonitors （app需要用service暴露metrics接口，然后定义serviceMonitor资源去抓取接口数据）

- pod monitor绕过了service，直接通过pod的label找到pod，抓取pod暴露的metrics接口：

  https://github.com/prometheus-operator/prometheus-operator/blob/main/Documentation/user-guides/getting-started.md#using-podmonitors

# 前提条件

1. 准备storage class提供数据持久化，实验环境下事先部署了nfs-client的sc，并设置为default storage class
   - 默认存储类：https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#default-storageclass


2. 提前配置ingress controller和ingress class
   - ingress controller yaml: https://github.com/kubernetes/ingress-nginx/tree/main/deploy/static/provider/baremetal
   - ingressController的deployment中配置hostnetwork=true

# helm配置

- 添加仓库

~~~sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm pull prometheus-community/kube-prometheus-stack --version 59.1.0
tar xzvf kube-prometheus-stack-52.1.0.tgz
cd kube-prometheus-stack
~~~

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
>   additionalDataSources:
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

# 安装

~~~sh
helm install kube-prometheus-stack -n monitoring --create-namespace . -f values.yaml
~~~

# 升级

~~~sh
helm upgrade -i kube-prometheus-stack -n monitoring . -f values.yaml
~~~

# 验证安装

~~~sh
#通过port forward转发svc端口来本地访问
kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9000:9090
kubectl port-forward svc/kube-prometheus-stack-grafana -n monitoring 9000:3000
kubectl port-forward svc/kube-prometheus-stack-alertmanager  -n monitoring 9000:9093
~~~

# 卸载

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

# ingress访问

## Http

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

## Https

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

## oauth2proxy

- 给ingress添加annotations：

~~~yaml
annotations:
  nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
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
version: 0.0.1
appVersion: "0.0.1"
~~~

- values.yaml

~~~yaml
dashboards:
  - file_path: "dashboards/aks.json"
    dashboard_name: aks-onepilot-platform
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

- datasource也可以以helm chart的形式部署，例如：

~~~yaml
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
        url: {{ .Values.quantum.db.url }}:{{ .Values.quantum.db.port }}
        database: {{ .Values.quantum.db.database }}
        user: {{ .Values.quantum.db.user }}
        secureJsonData:
          password: {{ .Values.quantum.db.password }}
        sslmode: verify-full
        jsonData:
          postgresVersion: 1400 # 903=9.3, 904=9.4, 905=9.5, 906=9.6, 1000=10
          timescaledb: true
~~~

# helm安装PrometheusRule

- alert可以通过crd PrometheusRule的方式来创建，示例如下：

~~~yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: loki
  namespace: monitoring
spec:
  groups:
    - name: loki-prometheus
      rules:
        - alert: LokiStorageHigh
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"storage-loki.*"} / 1024 / 1024 / 1024 < 5
          labels:
            severity: warning
            namespace: monitoring
          annotations:
            summary: "Loki storage is high"
            description: "Loki storage is high. Please review retention defaults"
            runbook: https://confluence.zenseact.com/pages/viewpage.action?pageId=255570326
        - alert: LokiStorageVeryHigh
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"storage-loki.*"} / 1024 / 1024 / 1024 < 1
          labels:
            severity: warning
            namespace: monitoring
          annotations:
            summary: "Loki storage is very high"
            description: "Loki storage is very high and is about to auto-expand. Please consider changing retention/storage/alert defaults"
            runbook:  https://confluence.zenseact.com/pages/viewpage.action?pageId=255570326
        - alert: PrometheusStorageHigh
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"prometheus-kube-prometheus-stack-prometheus-db.*"} / 1024 / 1024 / 1024 < 5
          labels:
            severity: warning
            namespace: monitoring
          annotations:
            summary: "Prometheus storage is high"
            description: "Prometheus storage is high. Please consider adding more storage"
            runbook: https://confluence.zenseact.com/pages/viewpage.action?pageId=255570326
        - alert: PrometheusStorageVeryHigh
          expr: kubelet_volume_stats_available_bytes{namespace="monitoring", persistentvolumeclaim=~"prometheus-kube-prometheus-stack-prometheus-db.*"} / 1024 / 1024 / 1024 < 1
          labels:
            severity: critical
            namespace: monitoring
          annotations:
            summary: "Prometheus storage is very high"
            description: "Prometheus storage is very high. Please add more storage"
            runbook: https://confluence.zenseact.com/pages/viewpage.action?pageId=255570326
~~~

- 安装

~~~sh
helm upgrade -i commoninfra-kube-prometheus-config -n kube-system . --values ./values/dev.chinanorth3.yaml
~~~

> PrometheusRule是Prometheus Operator中定义的CRD。有一个专门的网站可以查看各种各样的开源CRD的定义：
>
> - https://operatorhub.io/operator/prometheus

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
         userAssignedIdentityID: {{ .Values.commoninfra.secretProviderIdentityId }} # Set the clientID of the user-assigned managed identity to use, e.g. azurekeyvaultsecretsprovider-aks-commoninfra-dev-westeurope
         keyvaultName: {{ .Values.commoninfra.keyvaultName }}
         cloudName: {{ .Values.commoninfra.cloudName }}
         objects:  |
           array:
             - |
               objectName: slack-api-token
               objectType: secret
               objectVersion: ""
     
         tenantId: "{{ .Values.commoninfra.tenantId }}"
       # This creates an actual secret that we can use
       secretObjects:
       - secretName: alertmanager-slack
         data:
         - key: token # add a secret referencable with the same key as was in the keyvault
           objectName: slack-api-token
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
       name: alertmanager-slack-api-token
       namespace: monitoring
     type: Opaque
     data:
       token: xxxxxx
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
             credentials_file: '/mnt/secrets-store/token' #这里的文件名需要和secret的keyname相一致
   ...
       receivers:
       - name: 'null'
       - name: platform-slack
         slack_configs:
           - channel: '#alert-china-onepilot-dev'
             send_resolved: true
             title: '{{ template "slack.onepilot.title" . }}'
             text: '{{ template "slack.onepilot.text" . }}'
       - name: platform-slack-info
         slack_configs:
           - channel: '#alert-china-onepilot-platform-info'
             send_resolved: true
             title: '{{ template "slack.onepilot.title" . }}'
             text: '{{ template "slack.onepilot.text" . }}'
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
         {{ define "slack.onepilot.title" }}
         {{ .CommonLabels.alertname }} - {{ .Alerts.Firing | len }} in {{ .CommonLabels.namespace }}
         {{ end }}
       default_text.tmpl: |-
         {{ define "slack.onepilot.text" }}
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
         - name: alertmanager-secrets
           csi:
             driver: secrets-store.csi.k8s.io
             readOnly: true
             volumeAttributes:
               secretProviderClass: "sp-alertmanager"
   
       # Additional VolumeMounts on the output StatefulSet definition.
       volumeMounts:
         - name: alertmanager-secrets
           mountPath: "/mnt/secrets-store"
           readOnly: true
   ~~~

3. 验证slack端是否可以接收到告警信息
