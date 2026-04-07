# 介绍

- Jaeger是一个开源的分布式追踪系统，最初由Uber开发并开源，现在是CNCF的项目之一。主要用于监控和体哦按是分布式系统中的事务。
- 官网：https://www.jaegertracing.io/
- helm chart github地址：https://github.com/jaegertracing/helm-charts/tree/v2
- ArtifactHub地址：https://artifacthub.io/packages/helm/jaegertracing/jaeger

# 下载

- 下载helm chart

~~~sh
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update jaegertracing
helm pull jaegertracing/jaeger --version 3.4.1
~~~

# 配置

~~~yaml
provisionDataStore:
  cassandra: false
  elasticsearch: false
  kafka: false

allInOne:
  enabled: true
  replicas: 1
  image:
    registry: "quay.io"
    repository: jaegertracing/all-in-one
    tag: "1.65.0"
  extraEnv:
    - name: BADGER_SPAN_STORE_TTL
      value: "72h0m0s"
  service:
    headless: true
    collector:
      otlp:
        grpc:
          name: otlp-grpc
        http:
          name: otlp-http
  
  resources:
    requests:
      cpu: 22m
      memory: 128M
    limits:
      cpu: 1000m
      memory: 1024M

storage:
  type: badger  
  badger:
    ephemeral: false
    persistence:
      mountPath: /mnt/data
      useExistingPvcName: badger-data

agent:
  enabled: false

collector:
  enabled: false

query:
  enabled: false
~~~

> 注：
>
> - Badger是jaeger自带的k-v数据库：https://www.jaegertracing.io/docs/2.5/badger/

# 安装

- 准备PVC

~~~yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: badger-data
  namespace: monitoring
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: sc-nfs
  volumeMode: Filesystem
~~~

- 部署

~~~sh
# Create Badger PVC
kubectl apply -f $DIRECTORY/external/jaeger/storage/pvc.yaml -n monitoring

helm upgrade -i jaeger -n monitoring \
  jaegertracing/jaeger \
  --version $VERSION \
  -f $DIRECTORY/external/jaeger/values.yaml

# allow slow badger startup
kubectl patch deployment/jaeger -n monitoring --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/readinessProbe/failureThreshold", "value": 100},
  {"op": "replace", "path": "/spec/template/spec/containers/0/livenessProbe/failureThreshold", "value": 100}
]'
~~~

# 使用

