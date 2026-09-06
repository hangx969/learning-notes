---
title: KServe + KEDA 实战：基于请求指标实现服务自动扩缩容
tags:
  - kubernetes
  - kubernetes/autoscaling
  - kserve
  - keda
  - vllm
aliases:
  - KServe 集成 KEDA
  - vLLM 请求指标扩缩容
date: 2026-09-06
sources:
  - "[[0raw/KServe + KEDA 实战：基于请求指标实现服务自动扩缩容]]"
---

# KServe + KEDA 实战：基于请求指标实现服务自动扩缩容

模型服务运行后，固定副本数很难同时兼顾突发请求和资源利用率。本文通过一个 Demo，为 KServe 模型服务接入 KEDA，根据 vLLM 的请求指标自动调整副本数，并验证服务从 `1 -> 2 -> 1` 的扩缩容过程。

![KServe 集成 KEDA 的自动扩缩容链路](https://mmbiz.qpic.cn/sz_mmbiz_jpg/TKUQcaFRv0FvqP1P3HoaO2hjaaNSLepQoFzr8MeicVIncdg1uic7Svdu1xBcjfIyDLCsSScNftk59sOLAIiccewGfkOtTyAzibhOB9l2XxerHzI/640?wx_fmt=jpeg&from=appmsg&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

## 环境准备

### 实现思路

需要额外安装 KEDA 和 Prometheus，工作流程如下：

1. KServe 创建 Predictor Deployment 启动模型服务，底层推理引擎 vLLM 通过 `/metrics` 暴露运行指标。
2. Prometheus 采集 `vllm:num_requests_running` 和 `vllm:num_requests_waiting` 等指标。
3. KEDA 查询 Prometheus，并通过 External Metrics API 将查询结果暴露为 HPA 可以使用的外部指标。
4. HPA 比较当前指标值与目标值，计算期望副本数并调整 Predictor Deployment。

### 安装 KEDA

本文实测 KEDA 2.17.2：

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo update

helm upgrade --install keda kedacore/keda \
  -n keda --create-namespace \
  --version 2.17.2 \
  --wait
```

安装后确认 Operator、Admission Webhook 和 Metrics API Server 都已启动：

```bash
kubectl get pod -n keda
kubectl get apiservice v1beta1.external.metrics.k8s.io
```

预期可以看到：

```text
keda-admission-webhooks-...          1/1   Running
keda-operator-...                    1/1   Running
keda-operator-metrics-apiserver-...  1/1   Running

NAME                                     SERVICE                              AVAILABLE
v1beta1.external.metrics.k8s.io          keda/keda-metrics-apiserver          True
```

只有 CRD 不够。`external.metrics.k8s.io` 不可用时，ScaledObject 可以创建，但 HPA 读不到 KEDA 提供的指标。

### 部署 Prometheus

使用 `kube-prometheus-stack` 部署 Prometheus 和 Prometheus Operator，关闭 Grafana、Alertmanager、Exporter 和默认告警规则，仅保留指标采集所需组件：

```bash
helm upgrade --install prometheus \
  oci://ghcr.io/prometheus-community/charts/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --version 88.2.0 \
  --set grafana.enabled=false \
  --set alertmanager.enabled=false \
  --set kubeStateMetrics.enabled=false \
  --set nodeExporter.enabled=false \
  --set defaultRules.create=false \
  --set kubeApiServer.enabled=false \
  --set kubelet.enabled=false \
  --set kubeControllerManager.enabled=false \
  --set coreDns.enabled=false \
  --set kubeDns.enabled=false \
  --set kubeEtcd.enabled=false \
  --set kubeScheduler.enabled=false \
  --set kubeProxy.enabled=false \
  --set prometheusOperator.admissionWebhooks.enabled=false \
  --set prometheusOperator.tls.enabled=false \
  --wait
```

先确认 Prometheus Service 已创建。后续 InferenceService 和查询都使用这个 Service；如果没有输出，应先检查 Helm Release 和 Prometheus Pod，不要继续创建 InferenceService：

```bash
kubectl get svc prometheus-kube-prometheus-prometheus -n monitoring
kubectl get pod -n monitoring
kubectl get pod,svc -n monitoring
```

当前配置不创建 PrometheusRule，因此一并关闭了只用于校验规则的 Admission Webhook。安装完成后，集群中应保留 Prometheus Operator 和 Prometheus 两个 Pod。

## 配置自动扩缩容

### 创建 InferenceService

测试节点只有一张 GPU，而 Demo 需要把服务扩到两个副本，因此使用 HAMi DRA 共享 GPU。创建 ResourceClaimTemplate 和完整的 InferenceService，同时配置每个副本的 GPU 配额、模型和 KEDA 自动扩缩容：

```bash
cat <<'EOF' > qwen-llm.yaml
apiVersion: resource.k8s.io/v1
kind: ResourceClaimTemplate
metadata:
  name: qwen-hami-gpu
  namespace: kserve-test
spec:
  spec:
    devices:
      requests:
        - name: gpu
          exactly:
            deviceClassName: hami-core-gpu.project-hami.io
            allocationMode: ExactCount
            count: 1
            capacity:
              requests:
                memory: 3Gi
                cores: "20"
---
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: qwen-llm
  namespace: kserve-test
  annotations:
    serving.kserve.io/deploymentMode: Standard
    serving.kserve.io/autoscalerClass: keda
spec:
  predictor:
    minReplicas: 1
    maxReplicas: 2
    resourceClaims:
      - name: gpu
        resourceClaimTemplateName: qwen-hami-gpu
    autoScaling:
      metrics:
        - type: External
          external:
            metric:
              backend: prometheus
              serverAddress: http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090
              query: >-
                sum(vllm:num_requests_running{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
                +
                sum(vllm:num_requests_waiting{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
            target:
              type: Value
              value: "1"
    model:
      modelFormat:
        name: huggingface
      image: docker.m.daocloud.io/kserve/huggingfaceserver:v0.18.0-gpu
      storageUri: pvc://qwen-model
      args:
        - --model_name=qwen
        - --max_model_len=4096
        - --max-num-seqs=32
        - --gpu-memory-utilization=0.8
      resources:
        requests:
          cpu: "1"
          memory: 4Gi
        limits:
          cpu: "2"
          memory: 6Gi
        claims:
          - name: gpu
EOF

kubectl apply -f qwen-llm.yaml

kubectl wait --for=condition=Ready \
  inferenceservice/qwen-llm -n kserve-test --timeout=10m
```

每个 Predictor 副本通过 `qwen-hami-gpu` 申请 3Gi 显存和 20% GPU 核心，因此单 GPU 节点可以同时运行两个副本。KServe 创建 Predictor Deployment 和 ScaledObject，KEDA 再创建 HPA 管理副本数。

### 扩缩容配置解析

这份 YAML 中的扩缩容配置如下：

```yaml
metadata:
  annotations:
    serving.kserve.io/autoscalerClass: keda
spec:
  predictor:
    minReplicas: 1
    maxReplicas: 2
    autoScaling:
      metrics:
        - type: External
          external:
            metric:
              backend: prometheus
              serverAddress: http://prometheus-kube-prometheus-prometheus.monitoring.svc:9090
              query: >-
                sum(vllm:num_requests_running{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
                +
                sum(vllm:num_requests_waiting{namespace="kserve-test",pod=~"qwen-llm-predictor-.*"})
            target:
              type: Value
              value: "1"
```

各参数含义：

- `autoscalerClass: keda`：使用 KEDA 进行扩缩容。
- `minReplicas`、`maxReplicas`：限制最小和最大副本数。
- `serverAddress`：Prometheus 地址。
- `query`：使用 `running + waiting`，同时统计正在执行和已经进入 vLLM 队列的请求。
- `target.value`：每个副本期望承载的目标值。

Prometheus 查询得到的是所有 Predictor Pod 的请求总数：

```text
Query = running 请求数 + waiting 请求数
```

`target.value: 1` 表示希望每个副本平均处理 1 个请求。当前副本范围是 1～2：

- 当前只有 1 个副本时，如果 `Query = 0` 或 `1`，保持 1 个副本。
- 当前只有 1 个副本时，如果 `Query >= 2`，说明请求超过单个副本的目标值，扩到 2 个副本。
- 扩容后即使请求继续增加，也不会超过 `maxReplicas: 2`。
- 负载停止后，`Query` 回到 `0` 或 `1`，等待 300 秒缩容稳定窗口结束，再缩回 1 个副本。

### 配置 ServiceMonitor

Prometheus Stack 不会自动采集 `qwen-llm`。创建 ServiceMonitor，通过 InferenceService Label 选择 KServe 生成的 Predictor Service：

```bash
cat <<'EOF' > qwen-llm-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: qwen-llm
  namespace: monitoring
  labels:
    release: prometheus
spec:
  namespaceSelector:
    matchNames:
      - kserve-test
  selector:
    matchLabels:
      serving.kserve.io/inferenceservice: qwen-llm
  endpoints:
    - port: qwen-llm-predictor
      path: /metrics
      interval: 5s
EOF

kubectl apply -f qwen-llm-monitor.yaml
```

ServiceMonitor 不会通过 Service 的 ClusterIP 随机抓取一个后端。Prometheus Operator 会读取 Service 对应的 EndpointSlice，并把每个 Predictor Pod 都作为独立 Target。

### 检查指标和扩缩容资源

通过 Kubernetes Service Proxy 检查 Target。当前只有一个 Predictor，应看到一行 `qwen-llm-predictor-*`，状态为 `up`：

```bash
kubectl get --raw \
  '/api/v1/namespaces/monitoring/services/http:prometheus-kube-prometheus-prometheus:http-web/proxy/api/v1/targets?state=active' | \
  jq -r '.data.activeTargets[] | select(.labels.namespace == "kserve-test") | [.labels.pod, .health, .scrapeUrl] | @tsv'
```

检查空闲时的指标：

```bash
kubectl get --raw \
  '/api/v1/namespaces/monitoring/services/http:prometheus-kube-prometheus-prometheus:http-web/proxy/api/v1/query?query=sum(vllm:num_requests_running%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)%2Bsum(vllm:num_requests_waiting%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)' | \
  jq -r '[.status, .data.resultType, (.data.result | length), .data.result[0].value[1]] | @tsv'
```

实测输出：

```text
success vector 1 0
```

KServe 创建 Deployment 和 ScaledObject，KEDA 再创建并管理 HPA：

```bash
kubectl get inferenceservice qwen-llm -n kserve-test
kubectl get scaledobject qwen-llm-predictor -n kserve-test
kubectl get hpa keda-hpa-qwen-llm-predictor -n kserve-test
kubectl get deployment qwen-llm-predictor -n kserve-test
kubectl get pod -n kserve-test \
  -l serving.kserve.io/inferenceservice=qwen-llm
```

空闲状态下，各条命令输出中的关键字段如下：

```text
qwen-llm-predictor                  READY=True   ACTIVE=False   MIN=1   MAX=2
keda-hpa-qwen-llm-predictor         TARGETS=0/1                 REPLICAS=1
qwen-llm-predictor                  READY=1/1
```

直接读取 HPA，确认缩容稳定窗口：

```bash
kubectl get hpa keda-hpa-qwen-llm-predictor -n kserve-test \
  -o jsonpath='{.spec.behavior.scaleDown.stabilizationWindowSeconds}{"\n"}'
```

当前结果为 `300`。

## 验证自动扩缩容

### 验证扩容

先查询 Envoy Gateway 的地址，发送一次推理请求确认服务正常：

```bash
ENVOY_SERVICE=$(kubectl get service -n envoy-gateway-system \
  -l gateway.envoyproxy.io/owning-gateway-name=kserve-ingress-gateway \
  -o jsonpath='{.items[0].metadata.name}')

NODE_PORT=$(kubectl get service -n envoy-gateway-system "$ENVOY_SERVICE" \
  -o jsonpath='{.spec.ports[?(@.port==80)].nodePort}')

NODE_IP=$(kubectl get node \
  -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')

GATEWAY_ADDR="${NODE_IP}:${NODE_PORT}"

curl -H 'Host: qwen-llm-kserve-test.example.com' \
  -H 'Content-Type: application/json' \
  "http://${GATEWAY_ADDR}/openai/v1/chat/completions" \
  -d '{
    "model": "qwen",
    "messages": [{"role": "user", "content": "Answer only with the number: 2+3"}],
    "max_tokens": 8,
    "temperature": 0
  }'
```

#### 产生持续负载

```bash
BODY='{"model":"qwen","messages":[{"role":"user","content":"Write a detailed numbered list from 1 to 300, with a complete sentence for every item."}],"max_tokens":768,"temperature":0.7}'
export BODY GATEWAY_ADDR

seq 12 | xargs -n 1 -P 12 bash -c '
  while true; do
    curl -sS --max-time 180 \
      -H "Host: qwen-llm-kserve-test.example.com" \
      -H "Content-Type: application/json" \
      "http://${GATEWAY_ADDR}/openai/v1/chat/completions" \
      -d "$BODY" >/dev/null
  done
'
```

这条命令会一直占用当前终端，并将并发数保持为 12 持续发送请求。

#### 观察扩容结果

另开两个终端，同时观察 Prometheus 指标以及扩缩容资源：

```bash
watch -n 5 'kubectl get --raw "/api/v1/namespaces/monitoring/services/http:prometheus-kube-prometheus-prometheus:http-web/proxy/api/v1/query?query=sum(vllm:num_requests_running%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)%2Bsum(vllm:num_requests_waiting%7Bnamespace=%22kserve-test%22,pod=~%22qwen-llm-predictor-.*%22%7D)" | jq -r ".data.result[0].value[1]"'
```

```bash
watch -n 5 'kubectl get scaledobject,hpa,deployment,pod -n kserve-test'
```

本次实测时间线：

```text
启动负载后  Prometheus 查询值升到 12
              ScaledObject ACTIVE=True
              HPA TARGETS=6/1，Deployment REPLICAS=2
约 250 秒后   第二个 vLLM 完成模型加载，两个 Pod 均为 1/1 Running
```

![KServe 模型服务自动扩缩容时间线](https://mmbiz.qpic.cn/sz_mmbiz_jpg/TKUQcaFRv0ENbjbGGO7fvr9gxOhJYeBLb53lJ4kLT0F8YmO1ggO8KRns50Z4Uw0WUGIbn4IrMXyGB1xpsYhXMfd50rHqRb857ibkNg6cnITE/640?wx_fmt=jpeg&from=appmsg&watermark=1)

指标值是整个 Deployment 的 `running + waiting` 总数。两个副本、总值 12 时，平均每个副本为 6，因此 HPA 的目标列显示约 `6/1`。

扩容期间再次调用 Chat Completions 仍返回正确结果，说明 KEDA 已根据 vLLM 指标把服务从 1 个副本扩到 2 个。

### 验证缩容

回到运行压测的终端，按 `Ctrl+C` 停止全部请求。

先重复 Prometheus 查询，确认结果回到 0，再检查 ScaledObject 变成 `ACTIVE=False`。Deployment 不会立即缩容，因为当前生成的 HPA 带有 300 秒缩容稳定窗口：

```yaml
behavior:
  scaleDown:
    stabilizationWindowSeconds: 300
```

实际缩容时间还会受到 KEDA 轮询、HPA 同步周期和 Pod 终止时间影响。使用以下命令等待 Deployment 回到一个 Ready 副本：

```bash
kubectl wait deployment/qwen-llm-predictor -n kserve-test \
  --for=jsonpath='{.status.replicas}'=1 --timeout=8m
kubectl wait deployment/qwen-llm-predictor -n kserve-test \
  --for=jsonpath='{.spec.replicas}'=1 --timeout=2m
kubectl wait deployment/qwen-llm-predictor -n kserve-test \
  --for=jsonpath='{.status.readyReplicas}'=1 --timeout=2m

kubectl get hpa keda-hpa-qwen-llm-predictor -n kserve-test
kubectl get deployment qwen-llm-predictor -n kserve-test \
  -o custom-columns=NAME:.metadata.name,SPEC:.spec.replicas,STATUS:.status.replicas,READY:.status.readyReplicas
kubectl get pod -n kserve-test \
  -l serving.kserve.io/inferenceservice=qwen-llm
```

本次停止负载后，Prometheus 查询值回到 `0`，ScaledObject 变成 `ACTIVE=False`；约 299 秒后，HPA 将 Deployment 从 2 缩回 1。最后再次执行 Chat Completions 请求，仍然返回 `5`。

## 总结

1. KServe 创建 Predictor Deployment 启动模型服务，vLLM 通过 `/metrics` 暴露运行指标。
2. Prometheus 采集 `vllm:num_requests_running` 和 `vllm:num_requests_waiting`。
3. KEDA 查询 Prometheus，并通过 External Metrics API 将结果暴露为 HPA 可用的外部指标。
4. HPA 根据指标与目标值计算期望副本数，调整 Predictor Deployment。

这套方案将模型服务的扩缩容信号从 CPU/内存利用率转为请求压力，更接近推理服务的实际容量瓶颈。生产落地前还应根据模型加载时间、GPU 可用性、指标延迟和缩容稳定窗口进行压测与参数校准。
