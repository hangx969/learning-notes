# 前提条件

- 准备storage class提供数据持久化，实验环境下事先部署了nfs-client的sc，并设置为default storage class

> 默认存储类：https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#default-storageclass

# helm配置

- 添加仓库

~~~sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm pull prometheus-community/kube-prometheus-stack
tar xzvf kube-prometheus-stack-52.1.0.tgz
cd kube-prometheus-stack
~~~

- 修改配置

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
#将prometheus和alerManager数据持久化
vim values.yaml 
---
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: sc-nfs
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
---
      volumeClaimTemplate:
        spec:
          storageClassName: sc-nfs
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
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

# 安装

~~~sh
helm install kube-prometheus-stack -n monitoring --create-namespace \
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



