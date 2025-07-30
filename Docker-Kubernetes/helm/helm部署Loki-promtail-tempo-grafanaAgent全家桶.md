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

# python集成tempo

对于 Python 应用对接 Tempo 收集 Trace 数据，主要有两种方式：**OpenTelemetry** (推荐) 和 **Jaeger Python SDK**。我推荐使用 OpenTelemetry，因为它是现代标准且与 Tempo 集成最好。

## 方案 1: OpenTelemetry (推荐)

**1. 安装依赖**

```bash
pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-exporter-otlp \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-flask \
            opentelemetry-instrumentation-django \
            opentelemetry-instrumentation-psycopg2
```

**2. 基础配置代码**

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import os

def init_tracing():
    # 配置资源信息
    resource = Resource.create({
        "service.name": "my-python-app",
        "service.version": "1.0.0",
        "deployment.environment": "production"
    })
    
    # 创建 TracerProvider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    
    # 配置 OTLP 导出器 - 连接到 Tempo
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://tempo.monitoring.svc.cluster.local:4317",  # Tempo gRPC 端点
        insecure=True  # 在生产环境中应该使用 TLS
    )
    
    # 添加批量处理器
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # 自动装载常用库
    RequestsInstrumentor().instrument()
    FlaskInstrumentor().instrument()  # 如果使用 Flask
    
    return trace.get_tracer(__name__)

# 初始化追踪
tracer = init_tracing()
```

**3. Flask 应用示例**

```python
# app.py
from flask import Flask, request, jsonify
from tracing import tracer
import requests
import time

app = Flask(__name__)

@app.route('/api/users/<user_id>')
def get_user(user_id):
    # 手动创建 span
    with tracer.start_as_current_span("get_user") as span:
        # 添加属性到 span
        span.set_attribute("user.id", user_id)
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", request.url)
        
        try:
            # 模拟数据库查询
            user_data = fetch_user_from_db(user_id)
            
            # 调用外部服务
            profile_data = fetch_user_profile(user_id)
            
            span.set_attribute("user.found", True)
            return jsonify({
                "user": user_data,
                "profile": profile_data
            })
            
        except Exception as e:
            # 记录错误
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            return jsonify({"error": str(e)}), 500

def fetch_user_from_db(user_id):
    """模拟数据库查询"""
    with tracer.start_as_current_span("db.query.users") as span:
        span.set_attribute("db.operation", "SELECT")
        span.set_attribute("db.table", "users")
        span.set_attribute("db.user.id", user_id)
        
        # 模拟数据库延迟
        time.sleep(0.1)
        
        return {"id": user_id, "name": f"User {user_id}"}

def fetch_user_profile(user_id):
    """调用外部服务"""
    with tracer.start_as_current_span("http.client.user_profile") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.url", f"http://profile-service/users/{user_id}")
        
        # requests 会自动被装载，创建子 span
        response = requests.get(f"http://profile-service/users/{user_id}")
        
        span.set_attribute("http.status_code", response.status_code)
        return response.json()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**4. 环境变量配置方式**

更简单的方式是使用环境变量：

```yaml
# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: my-python-app:latest
        env:
        # OpenTelemetry 环境变量
        - name: OTEL_SERVICE_NAME
          value: "my-python-app"
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://tempo.monitoring.svc.cluster.local:4317"
        - name: OTEL_EXPORTER_OTLP_INSECURE
          value: "true"
        - name: OTEL_RESOURCE_ATTRIBUTES
          value: "service.version=1.0.0,deployment.environment=production"
        # 自动装载
        - name: OTEL_PYTHON_DISABLED_INSTRUMENTATIONS
          value: ""  # 留空表示启用所有自动装载
```

```python
# 简化的应用代码
from opentelemetry.instrumentation.auto_instrumentation import sitecustomize

# 只需要这一行，其他都自动配置！
```

**5. 使用自动装载启动**

```bash
# 使用 opentelemetry-instrument 启动应用
opentelemetry-instrument python app.py

# 或者在 Dockerfile 中
CMD ["opentelemetry-instrument", "python", "app.py"]
```

## 方案 2: Jaeger Python SDK

如果您更喜欢 Jaeger SDK：

```python
import opentracing
from jaeger_client import Config

def init_jaeger_tracer(service_name='my-python-app'):
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'local_agent': {
                'reporting_host': 'tempo.monitoring.svc.cluster.local',
                'reporting_port': 6831,  # Jaeger UDP 端口
            },
            'logging': True,
        },
        service_name=service_name,
    )
    return config.initialize_tracer()

tracer = init_jaeger_tracer()

@app.route('/api/test')
def test_endpoint():
    with tracer.start_span('test_operation') as span:
        span.set_tag('user.id', '12345')
        span.log_kv({'event': 'processing request'})
        
        # 业务逻辑
        result = do_something()
        
        span.set_tag('result.count', len(result))
        return jsonify(result)
```

## 更新 Tempo 配置

确保您的 Tempo 配置支持接收 OTLP 数据：

```yaml
# 添加到您的 tempo values.yaml
tempo:
  config: |
    server:
      http_listen_port: 3100
      grpc_listen_port: 9095
    
    distributor:
      receivers:
        otlp:
          protocols:
            grpc:
              endpoint: 0.0.0.0:4317
            http:
              endpoint: 0.0.0.0:4318
        jaeger:
          protocols:
            grpc:
              endpoint: 0.0.0.0:14250
            thrift_http:
              endpoint: 0.0.0.0:14268
```

## 验证追踪数据

**1. 检查应用日志**

```bash
# 查看应用是否成功发送 spans
kubectl logs -f deployment/python-app
```

**2. 在 Grafana 中查看**

1. 打开 Grafana
2. 切换到 Explore
3. 选择 Tempo 数据源
4. 输入 Trace ID 或使用查询语句

**3. 查看生成的指标**

由于您启用了 `metricsGenerator`，Tempo 会自动生成指标：
```promql
# 在 Prometheus 中查询
tempo_traces_total{service_name="my-python-app"}
tempo_traces_duration_seconds{service_name="my-python-app"}
```

## 最佳实践

**1. Span 命名规范**

```python
# 好的命名
with tracer.start_as_current_span("db.query.users"):
with tracer.start_as_current_span("http.client.user_service"):
with tracer.start_as_current_span("cache.get.user_profile"):

# 避免的命名
with tracer.start_as_current_span("function1"):
with tracer.start_as_current_span("processing"):
```

**2. 关键属性设置**

```python
span.set_attribute("http.method", "GET")
span.set_attribute("http.status_code", 200)
span.set_attribute("db.statement", "SELECT * FROM users WHERE id = ?")
span.set_attribute("user.id", user_id)
span.set_attribute("error", True)  # 发生错误时
```

**3. 采样策略**

```python
# 在生产环境中设置采样率
config = {
    'sampler': {
        'type': 'probabilistic',
        'param': 0.1  # 10% 采样率
    }
}
```

这样配置后，您的 Python 应用就能够向 Tempo 发送详细的追踪数据，在 Grafana 中实现完整的分布式追踪可视化了。
