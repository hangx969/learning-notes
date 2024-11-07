# kubernetes events

- 在Kubernetes集群中，事件（Events）是集群内资源对象状态变化的实时反馈，它们提供了丰富的信息来源，包括对象状态变化、配置更改和调度失败等，可以帮助运维人员了解集群内各种对象的活动状态以及变化，响应故障并进行诊断。
- 与其他资源对象相比，Events非常活跃，数据量也很大，考虑到Etcd集群的性能问题，因此不太可能长时间存储在Etcd中。默认情况下，Kubernetes Events只保留一个小时，这对于长期分析和故障排查是不够的。因此，将Kubernetes Events持久化存储，并通过可视化工具进行分析变得非常重要。

- 常见的event类型：
  1. Failed events：由于对象单元级别的错误或从仓库拉取容器镜像失败引起。
  2. Evicted events：资源不足时，Kubelet驱逐节点上的Pods。

  3. Failed scheduling events：没有足够的节点可用或节点不匹配选择器。

  4. Volume events：持久化数据失败，可能由于网络或配置错误。

  5. Node events：节点状态不健康，可能导致5XX错误或无法连接。

  6. OOM events: Pod内存使用率触发limit而OOM。

  7. 还有Image Pull Failed、Liveness Probe Failed、Container Crashed等等。

- 收集log的组件很多，EFK比较常用，但是ES太重了。这里推荐Loki，一个高效的日志聚合器，适用于收集和存储日志数据，还非常轻量化，非常适合用于聚合存储**Kubernetes Events**。

# Helm部署Loki

- 使用**Helm**部署**Loki**，部署挺简单，定义一个**value**文件，直接**helm install**就好。因为我们使用的场景相对简单，所以部署方式使用**singleBinary**即可，数据需要持久化。

```yaml
# install-value.yaml
loki:
  commonConfig:
    replication_factor: 1
  storage:
    type: 'filesystem'
  auth_enabled: false
singleBinary:
  replicas: 1

persistence:
 enabled: true
 accessModes:
 - ReadWriteOnce
 size: 50Gi
 annotations: {}
```

- 使用**helm chart**部署：

```sh
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki -n monitoring -f install-values.yaml --debug
```

- 部署Kubernetes Event Exporter

  - 从**Kubernetes Event Exporter**的**GitHub**仓库获取部署清单，部署更加简单，直接**kubectl apply**项目下**deploy**路径里的**3**个**yaml**文件即可

  - 配置**Event Exporter**的**config**，将其指向**Loki**实例。

    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: event-exporter-cfg
      namespace: monitoring
    data:
      config.yaml: |
        logLevel: warn
        logFormat: json
        metricsNamePrefix: event_exporter_
        maxEventAgeSeconds: 60
        route:
          routes:
            - match:
                # - receiver: "es"
                - receiver: "loki"
        receivers:
          # - name: "es"
          #   elasticsearch:
          #     hosts:
          #       - "http://elasticsearch.kube-logging:9200"
          #     indexFormat: "kube-events-{2006-01-02}"
    
          - name: "loki"
            webhook：
              endpoint: "http://loki.monitoring.svc.cluster.local:3100/loki/api/v1/push"
              headers: # optional
                Content-Type: application/json
                User-Agent: "kube-event-exporter"
    ```

  - **apply yaml**文件部署

  ```sh
  kubectl apply -f deploy/
  ```

- 配置grafana仪表板

  - 在Grafana中创建一个新的仪表盘，使用loki作为数据源。
  - 添加Loki查询面板，配置查询语句以筛选和展示Kubernetes事件。
  - 通过Grafana的图表和过滤功能，创建适合的可视化视图。
  - 这里有个更好的建议，直接在Grafana官网下载相关Dashboard，稍微改改适合我们场景就挺好.
  - 查询语句（Explain query非常友好）也非常好写.

# helm部署loki全家桶

~~~sh
helm repo add grafana https://grafana.github.io/helm-charts4
helm repo update
helm pull grafana/loki --version "${LOKI_VERSION#helm-loki-}"
helm pull grafana/promtail --version "${PROMTAIL_VERSION#promtail-}"
helm pull grafana/tempo --version "${TEMPO_VERSION#tempo-}"
~~~

~~~sh
helm upgrade -i loki -n monitoring \
                  oci://crcommoninfra${{parameters.environment}}${{parameters.region}}.azurecr.cn/helm/loki \
                  --version $VERSION \
                  --history-max 3 \
                  -f $VALUES_FILE
~~~

