# 介绍

- 官网地址：https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack#kube-prometheus-stack

- 通过一个prometheus-stack的chart，自动部署prometheus、kube-state-metrics、grafana、node-exporter、Alertmanager。

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
helm pull prometheus-community/kube-prometheus-stack
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

# slack alert配置

https://prometheus.wang/alertmanager/slack.html

我们的workspace里面没有“Incoming Webhooks”的app？需要admin安装，之前的alert是怎么发进来的？

# helm安装dashboard

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

# helm安装prometheus config

# helm安装grafana datasources
