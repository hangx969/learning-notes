# loki日志查询

参考：https://mp.weixin.qq.com/s?__biz=Mzk0NzIyMDA4MA==&mid=2247484579&idx=1&sn=3b2be6ca22c78aae1112601341bb80e9&chksm=c37b7fbcf40cf6aab13c14177d0e0a15d97ee6f3ef1aad00e08ba7e18ff4fae84476dce61434&cur_album_id=3143335204699504647&scene=189#wechat_redirect

# kubernetes events

- 在Kubernetes集群中，事件（Events）是集群内资源对象状态变化的实时反馈，它们提供了丰富的信息来源，包括对象状态变化、配置更改和调度失败等，可以帮助运维人员了解集群内各种对象的活动状态以及变化，响应故障并进行诊断。
- 我们可以简单的使用`kubectl get events`来获取事件，也可以装一个podevents插件`kubectl krew install podevents`，通过`kubectl podevents <pod name>`来查看事件。
- 常见的event类型：
  1. Failed events：由于对象单元级别的错误或从仓库拉取容器镜像失败引起。
  2. Evicted events：资源不足时，Kubelet驱逐节点上的Pods。

  3. Failed scheduling events：没有足够的节点可用或节点不匹配选择器。

  4. Volume events：持久化数据失败，可能由于网络或配置错误。

  5. Node events：节点状态不健康，可能导致5XX错误或无法连接。

  6. OOM events: Pod内存使用率触发limit而OOM。

  7. 还有Image Pull Failed、Liveness Probe Failed、Container Crashed等等。
- 与其他资源对象相比，Events非常活跃，数据量也很大，考虑到Etcd集群的性能问题，不太可能长时间存储在Etcd中。默认情况下Kubernetes Events只保留**一个小时**，这对于长期分析和故障排查是不够的。因此，将Kubernetes Events持久化存储，并通过可视化工具进行分析变得非常重要。
- 收集log的组件很多，EFK比较常用，但是ES太重了。这里推荐Loki，一个高效的日志聚合器，适用于收集和存储日志数据，还非常轻量化，非常适合用于聚合存储Kubernetes Events。

- 采集k8s events的组件也有很多:
  - grafana-agent: https://grafana.com/docs/agent/latest/static/configuration/integrations/integrations-next/eventhandler-config/?pg=blog&plcmt=body-txt
  - k8s-event-logger
  - evetns-operator

# helm部署k8s-event-logger

- 有一个简单的系统`max-rocket-internet/k8s-event-logger`，它监听 Kubernetes API，接收所有事件，并以 JSON 日志形式写入。

- helm部署

  ~~~sh
  helm repo add deliveryhero https://charts.deliveryhero.io/
  helm repo update
  helm upgrade -i k8s-event-logger deliveryhero/k8s-event-logger -n monitoring
  ~~~

- 部署完会创建一个收集event的pod

  ~~~sh
  $ kubectl -n ops-monitoring-ns get pods -l "app.kubernetes.io/name=k8s-event-logger"
  NAME                                READY   STATUS    RESTARTS   AGE
  k8s-event-logger-5b548d6cc4-r8wkl   1/1     Running   0          68s
  ~~~

- pod会将事件写入其输出

  ~~~sh
  $ kubectl -n ops-monitoring-ns logs -l "app.kubernetes.io/name=k8s-event-logger"
  {"metadata":{"name":"backend-api-deployment-7fdfbb755-tjv2j.17daa9e0264e6139","namespace":"prod-backend-api-ns","uid":"1fa06477-62c9-4324-8823-7f2801fc26af","resourceVersion":"110778929","creationTimestamp":"2024-06-20T08:43:07Z","managedFields":[{"manager":"kubelet","operation":"Update","apiVersion":"v1","time":"2024-06-20T08:43:07Z",\
  ...\
  ~~~

- 然后这些日志会进入到promtail实例，再进入到loki，可以从Grafana - Expolre中搜索：

  ~~~sql
  {app="k8s-event-logger"}
  ~~~

# Helm部署Loki+events-exporter

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
  - 也直接在Grafana官网下载相关Dashboard，稍微改改适合我们场景。
  - 查询语句（Explain query）也非常好写。

# helm部署loki-promtail-tempo全家桶

## Loki

- 文档：https://grafana.com/docs/loki/latest/setup/install/helm/install-monolithic/#deploying-the-helm-chart-for-development-and-testing
- github release: https://github.com/grafana/loki/releases
- artifact hub: https://artifacthub.io/packages/helm/grafana/loki

> Grafana生态中日志存储的后端，其单机模式支持直接使用文件存储，而多副本模式依赖对象存储来对数据进行持久化。Grafana内置了Loki数据源类型，在配置相应的数据源后可以通过Grafana Explore页面进行日志查询。

- 下载

~~~sh
helm repo add grafana https://grafana.github.io/helm-chart
helm repo update
helm pull grafana/loki --version "${LOKI_VERSION#helm-loki-}" #5.48.0
~~~

- 配置

  ~~~yaml
  #这里仿照azure_global的values.yaml进行了调整
  ~~~

  > loki的log volume没配置？

- 安装

~~~sh
helm upgrade -i loki -n monitoring . -f values.yaml
~~~

- 添加grafana数据源
  - add data source - loki - URL: http://loki.monitoring.svc.cluster.local:3100

## Promtail

- 文档：https://grafana.com/docs/loki/latest/send-data/promtail/

- github release: https://github.com/grafana/loki/releases

- artifact hub: https://artifacthub.io/packages/helm/grafana/promtail

- 下载

~~~sh
helm repo add grafana https://grafana.github.io/helm-chart
helm repo update
helm pull grafana/promtail --version "${PROMTAIL_VERSION#promtail-}" #6.15.5
~~~

- 配置

~~~sh
#同样采用azure_global的values.yaml进行调整
~~~

- 安装

~~~sh
helm upgrade -i promtail -n monitoring . -f values.yaml
~~~

## tempo

- 文档：
  - https://grafana.org.cn/docs/tempo/latest/introduction/telemetry/
  - https://grafana.com/docs/tempo/latest/getting-started/tempo-in-grafana/
- release page: https://github.com/grafana/tempo/releases
- artifact hub: https://artifacthub.io/packages/helm/grafana/tempo

> 遵循OTel协议的Trace数据存储后端服务，包含若干组件：
>
> - Distributor：接收来自客户端的数据
> - Metrics generator：将Trace数据转化为Metrics存储至Prometheus
> - Ingester：对接存储，将数据写入存储
> - Compactor：将存储的数据进行压缩清理，减少block数量
> - Query Frontend：将前端查询拆分若干搜索空间至Querier进行查询
> - Querier：向存储查询数据，并返回给Query Fronted
>
> Trace的数据流如下图：
>
> ![image-20241112141012964](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202411121410028.png)
>

- 下载

~~~sh
helm repo add grafana https://grafana.github.io/helm-chart
helm repo update
helm pull grafana/tempo --version "${TEMPO_VERSION#tempo-}" #1.8.0
~~~

- 配置

~~~sh
#同样采用azure_global的values.yaml进行调整
~~~

- 安装

~~~sh
helm upgrade -i tempo -n monitoring . -f values.yaml
~~~

> 注：部署完loki和tempo，去prometheus-stack的grafana配置里面加上additionalDataSource：
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

# helm部署grafana agent

## 介绍

- github release: https://github.com/grafana/agent/releases
- artifacthub: https://artifacthub.io/packages/helm/grafana/grafana-agent

Refer：https://mp.weixin.qq.com/s?__biz=Mzk0NzIyMDA4MA==&mid=2247484542&idx=1&sn=02cba4c7dd124a06afa97104c2d50bca&chksm=c37b7f61f40cf677ae5b0aa9dfef3a39a6c945aa6f68379d1f81ccfe54d2cd706aa481efa08b&cur_album_id=3143335204699504647&scene=189#wechat_redirect

- Tempo服务是可以直接通过Tempo-distributor组件或者使用TempoGateWay直接接收Trace数据的，是无需部署Grafana Agent组件的。

- 考虑到生产实践中，Tempo作为基础组件一般与业务服务集群分开部署，部署在单独的集群，为各个业务集群提供Trace存储服务，所以考虑在各集群内部部署Grafana Agent，业务服务产生的Trace数据发送至Grafana Agent，由Grafana Agent根据配置的策略统一发送至Tempo服务端，如图：

  ![image-20241112141359129](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202411121413231.png)

- Grafana Agent集成了监控、日志、链路的处理转发相关客户端功能，可以完成对以上数据的采集。

![image-20241112140930901](/home/s0001969/.config/Typora/typora-user-images/image-20241112140930901.png)

## 下载

~~~sh
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update grafana
helm pull grafana/grafana-agent --version 0.42.0
~~~

## 配置

- 仿照ado的values文件配置

## 安装

~~~sh
helm upgrade -i grafana-agent -n monitoring . -f ./values.yaml
~~~

