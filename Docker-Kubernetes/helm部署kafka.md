# 介绍

## Kafka

- Kafka 是一种高吞吐量的分布式发布订阅消息系统。主要用于实时数据流的处理和分析。它可以处理大量的实时数据，并提供高吞吐量、可扩展性和容错性。即使是非常普通的硬件Kafka也可以支持每秒数百万的消息。采用生产者消费者模型。

2、相关术语：

- Broker： Kafka集群包含一个或多个服务器，服务器被称为broker。Kafka的数据是分布式存储在各个Broker上的。每个Broker都会存储一部分Topic的Partition。Kafka的Broker主要用于存储和处理实时数据流。
- Topic： 每条发布到Kafka集群的消息都有一个类别，这个类别被称为Topic。（物理上不同Topic的消息分开存储，逻辑上一个Topic的消息虽然保存于一个或多个broker上，但用户只需指定消息的Topic，即可生产或消费数据，而不必关心数据存于何处）
- Partition： Partition是物理上的概念，每个Topic包含一个或多个Partition。
- Producer： 负责发布消息到Kafka broker
- Consumer： 消息消费者，向Kafka broker读取消息的客户端。

> 消费者的偏移量：
>
> 在Kafka中，消费者的偏移量（Consumer Offset）是一个非常重要的概念。它表示消费者在特定的主题和分区中已经消费到的位置。
>
> Kafka的主题（Topic）被划分为一个或多个分区（Partition），每个分区中的消息都是有序的，并且每条消息在分区中都有一个唯一的序号，这个序号就是偏移量（Offset）。当消费者从分区中读取消息时，它会维护一个指针，这个指针指向下一条需要读取的消息的位置，这个位置就是消费者的偏移量。
>
> 消费者的偏移量是消费者消费消息的基础，通过维护每个消费者的偏移量，Kafka可以支持消息的重复消费，也就是说，消费者可以随时将偏移量回退到之前的位置，重新消费已经消费过的消息。同时，通过正确地管理消费者的偏移量，Kafka还可以实现消费者的故障恢复和负载均衡。

## strimzi-kafka-operator

- 生产环境推荐的kafka部署方式为operator方式部署，Strimzi是目前最主流的operator方案。集群数据量较小的话，可以采用NFS共享存储，数据量较大的话可使用local pv存储。
- github地址：https://github.com/strimzi/strimzi-kafka-operator/releases
- 官网地址：https://strimzi.io/docs/operators/latest/deploying.html#deploying-cluster-operator-helm-chart-str
- cluster operator部署出来之后，再去手动创建kafka cluster、topic operator、user operator等CRD资源。

## kafka-ui

- 官网地址：https://docs.kafka-ui.provectus.io/

## kafka-mirror-maker

- 官网地址：https://strimzi.io/docs/operators/latest/deploying.html#kafka-mirror-maker-str

- 解决 Kafka 集群之间数据复制和数据同步的问题而诞生的 Kafka 官方的数据复制工具。在实际生产中，经常被用来实现 Kafka 数据的备份，迁移和灾备等目的。其实现原理是通过从Source Cluster消费消息，然后将消息生产到Target Cluster，即普通的消息生产和消费。用户只要通过简单的consumer配置和producer配置，启动Mirror，就可以实现准实时的数据同步。

# 部署srtimzi-kafka-operator

## 下载

~~~sh
helm repo add strimzi https://strimzi.io/charts/
helm repo update strimzi
helm pull strimzi/strimzi-kafka-operator --version 0.42.0
~~~

## 配置

- 开启了dashboard、watchAnyNamespace

## 安装

~~~sh
helm upgrade -i strimzi-kafka-operator -n kafka --create-namespace . --values values.yaml  #--skip-crds --values $VALUES_FILE
~~~

# 部署kafka cluster

- cluster operator部署完之后，去部署下面几个CRD资源，这些资源也是以helm chart形式部署，chart name：name: commoninfra-kafka-config

## kafka-broker-nodepool

~~~yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: kafka
  namespace: kafka
  labels:
    strimzi.io/cluster: {{ .Values.commoninfra.kafka.name }}
spec:
  replicas: {{ .Values.commoninfra.kafka.replicas }}
  roles:
    - broker
  storage:
    type: {{ .Values.commoninfra.kafka.storage.type }}
    size: {{ .Values.commoninfra.kafka.storage.size }}
    class: {{ .Values.commoninfra.kafka.storage.class }}
~~~

## kafka-cluster

~~~yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: {{ .Values.commoninfra.kafka.name }}
  namespace: kafka
  annotations:
    strimzi.io/kraft: "enabled"
    strimzi.io/node-pools: "enabled"
spec:
  kafka:
    version: {{ .Values.commoninfra.kafka.version }}
    listeners:
      - name: tls
        port: 9093
        type: internal
        tls: true
        authentication:
          type: tls
      - name: external
        port: 9094
        type: loadbalancer
        tls: true
        authentication:
          type: tls
        configuration:
          bootstrap:
            annotations:
              #service.beta.kubernetes.io/azure-load-balancer-internal: "true"
              #external-dns.alpha.kubernetes.io/hostname: kafka.{{ .Values.environment }}.{{ .Values.product }}#.{{ .Values.dns.domain }}
              #external-dns.alpha.kubernetes.io/ttl: "600"
            alternativeNames:
              - kafka.{{ .Values.environment }}.{{ .Values.product }} #.{{ .Values.dns.domain }}
          brokers:
            {{- $root := . -}}
            {{- range $i, $e := until (int .Values.commoninfra.kafka.replicas) }}
            - broker: {{ $i }}
              annotations:
                #service.beta.kubernetes.io/azure-load-balancer-internal: "true"
                #external-dns.alpha.kubernetes.io/hostname: kafka-broker-{{ $i }}.{{ $root.Values.environment }}.{{ $root.Values.product }}.{{ $root.Values.dns.domain }}
                #external-dns.alpha.kubernetes.io/ttl: "600"
              advertisedHost: kafka-broker-{{ $i }}.{{ $root.Values.environment }}.{{ $root.Values.product }} #.{{ $root.Values.dns.domain }}
            {{- end }}
    authorization:
      type: simple
    resources: {{- .Values.commoninfra.kafka.kafka_resources | toYaml | trim | nindent 6 }}
    jvmOptions:
      -Xms: 2500m
      -Xmx: 2500m
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      log.retention.ms: 604800000
      delete.topic.enable: true
      num.partitions: 6
      log.segment.bytes: 104857600
      log.roll.ms: 86400000
      auto.create.topics.enable: false
      socket.send.buffer.bytes: 102400
      socket.receive.buffer.bytes: 102400
      socket.request.max.bytes: 104857600
      replica.fetch.max.bytes: 104857600
      message.max.bytes: 104857600
    metricsConfig:
      type: jmxPrometheusExporter
      valueFrom:
        configMapKeyRef:
          name: kafka-metrics
          key: kafka-metrics-config.yml
    template:
      clusterCaCert:
        metadata:
          annotations:
            kubed.appscode.com/sync: "config-sync-kafka"
  entityOperator:
    topicOperator:
      resources:
        requests:
          memory: 128Mi
          cpu: "100m"
        limits:
          memory: 128Mi
          cpu: "750m"
      jvmOptions:
        -Xms: 256m
        -Xmx: 256m
    userOperator:
      resources:
        requests:
          memory: 128Mi
          cpu: "100m"
        limits:
          memory: 128Mi
          cpu: "750m"
      jvmOptions:
        -Xms: 256m
        -Xmx: 256m
  kafkaExporter: {}
~~~

## kafka-controller-nodepool

~~~yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: controller
  namespace: kafka
  labels:
    strimzi.io/cluster: {{ .Values.commoninfra.kafka.name }}
spec:
  replicas: {{ .Values.commoninfra.kafka.replicas }}
  roles:
    - controller
  resources: {{- .Values.commoninfra.kafka.kafka_controller_resources | toYaml | trim | nindent 4 }}
  storage:
    type: {{ .Values.commoninfra.kafka.storage.type }}
    size: {{ .Values.commoninfra.kafka.storage.size }}
    class: {{ .Values.commoninfra.kafka.storage.class }}
~~~

## kafka-metrics-config

~~~yaml
# This file is copy from
# https://github.com/strimzi/strimzi-kafka-operator/blob/<strimzi_version>/examples/metrics/kafka-metrics.yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: kafka-metrics
  namespace: kafka
  labels:
    app: strimzi
data:
  kafka-metrics-config.yml: |
    # See https://github.com/prometheus/jmx_exporter for more info about JMX Prometheus Exporter metrics
    lowercaseOutputName: true
    rules:
    # Special cases and very specific rules
    - pattern: kafka.server<type=(.+), name=(.+), clientId=(.+), topic=(.+), partition=(.*)><>Value
      name: kafka_server_$1_$2
      type: GAUGE
      labels:
        clientId: "$3"
        topic: "$4"
        partition: "$5"
    - pattern: kafka.server<type=(.+), name=(.+), clientId=(.+), brokerHost=(.+), brokerPort=(.+)><>Value
      name: kafka_server_$1_$2
      type: GAUGE
      labels:
        clientId: "$3"
        broker: "$4:$5"
    - pattern: kafka.server<type=(.+), cipher=(.+), protocol=(.+), listener=(.+), networkProcessor=(.+)><>connections
      name: kafka_server_$1_connections_tls_info
      type: GAUGE
      labels:
        cipher: "$2"
        protocol: "$3"
        listener: "$4"
        networkProcessor: "$5"
    - pattern: kafka.server<type=(.+), clientSoftwareName=(.+), clientSoftwareVersion=(.+), listener=(.+), networkProcessor=(.+)><>connections
      name: kafka_server_$1_connections_software
      type: GAUGE
      labels:
        clientSoftwareName: "$2"
        clientSoftwareVersion: "$3"
        listener: "$4"
        networkProcessor: "$5"
    - pattern: "kafka.server<type=(.+), listener=(.+), networkProcessor=(.+)><>(.+-total):"
      name: kafka_server_$1_$4
      type: COUNTER
      labels:
        listener: "$2"
        networkProcessor: "$3"
    - pattern: "kafka.server<type=(.+), listener=(.+), networkProcessor=(.+)><>(.+):"
      name: kafka_server_$1_$4
      type: GAUGE
      labels:
        listener: "$2"
        networkProcessor: "$3"
    - pattern: kafka.server<type=(.+), listener=(.+), networkProcessor=(.+)><>(.+-total)
      name: kafka_server_$1_$4
      type: COUNTER
      labels:
        listener: "$2"
        networkProcessor: "$3"
    - pattern: kafka.server<type=(.+), listener=(.+), networkProcessor=(.+)><>(.+)
      name: kafka_server_$1_$4
      type: GAUGE
      labels:
        listener: "$2"
        networkProcessor: "$3"
    # Some percent metrics use MeanRate attribute
    # Ex) kafka.server<type=(KafkaRequestHandlerPool), name=(RequestHandlerAvgIdlePercent)><>MeanRate
    - pattern: kafka.(\w+)<type=(.+), name=(.+)Percent\w*><>MeanRate
      name: kafka_$1_$2_$3_percent
      type: GAUGE
    # Generic gauges for percents
    - pattern: kafka.(\w+)<type=(.+), name=(.+)Percent\w*><>Value
      name: kafka_$1_$2_$3_percent
      type: GAUGE
    - pattern: kafka.(\w+)<type=(.+), name=(.+)Percent\w*, (.+)=(.+)><>Value
      name: kafka_$1_$2_$3_percent
      type: GAUGE
      labels:
        "$4": "$5"
    # Generic per-second counters with 0-2 key/value pairs
    - pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*, (.+)=(.+), (.+)=(.+)><>Count
      name: kafka_$1_$2_$3_total
      type: COUNTER
      labels:
        "$4": "$5"
        "$6": "$7"
    - pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*, (.+)=(.+)><>Count
      name: kafka_$1_$2_$3_total
      type: COUNTER
      labels:
        "$4": "$5"
    - pattern: kafka.(\w+)<type=(.+), name=(.+)PerSec\w*><>Count
      name: kafka_$1_$2_$3_total
      type: COUNTER
    # Generic gauges with 0-2 key/value pairs
    - pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+), (.+)=(.+)><>Value
      name: kafka_$1_$2_$3
      type: GAUGE
      labels:
        "$4": "$5"
        "$6": "$7"
    - pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+)><>Value
      name: kafka_$1_$2_$3
      type: GAUGE
      labels:
        "$4": "$5"
    - pattern: kafka.(\w+)<type=(.+), name=(.+)><>Value
      name: kafka_$1_$2_$3
      type: GAUGE
    # Emulate Prometheus 'Summary' metrics for the exported 'Histogram's.
    # Note that these are missing the '_sum' metric!
    - pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+), (.+)=(.+)><>Count
      name: kafka_$1_$2_$3_count
      type: COUNTER
      labels:
        "$4": "$5"
        "$6": "$7"
    - pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.*), (.+)=(.+)><>(\d+)thPercentile
      name: kafka_$1_$2_$3
      type: GAUGE
      labels:
        "$4": "$5"
        "$6": "$7"
        quantile: "0.$8"
    - pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.+)><>Count
      name: kafka_$1_$2_$3_count
      type: COUNTER
      labels:
        "$4": "$5"
    - pattern: kafka.(\w+)<type=(.+), name=(.+), (.+)=(.*)><>(\d+)thPercentile
      name: kafka_$1_$2_$3
      type: GAUGE
      labels:
        "$4": "$5"
        quantile: "0.$6"
    - pattern: kafka.(\w+)<type=(.+), name=(.+)><>Count
      name: kafka_$1_$2_$3_count
      type: COUNTER
    - pattern: kafka.(\w+)<type=(.+), name=(.+)><>(\d+)thPercentile
      name: kafka_$1_$2_$3
      type: GAUGE
      labels:
        quantile: "0.$4"
    # KRaft overall related metrics
    # distinguish between always increasing COUNTER (total and max) and variable GAUGE (all others) metrics
    - pattern: "kafka.server<type=raft-metrics><>(.+-total|.+-max):"
      name: kafka_server_raftmetrics_$1
      type: COUNTER
    - pattern: "kafka.server<type=raft-metrics><>(.+):"
      name: kafka_server_raftmetrics_$1
      type: GAUGE
    # KRaft "low level" channels related metrics
    # distinguish between always increasing COUNTER (total and max) and variable GAUGE (all others) metrics
    - pattern: "kafka.server<type=raft-channel-metrics><>(.+-total|.+-max):"
      name: kafka_server_raftchannelmetrics_$1
      type: COUNTER
    - pattern: "kafka.server<type=raft-channel-metrics><>(.+):"
      name: kafka_server_raftchannelmetrics_$1
      type: GAUGE
    # Broker metrics related to fetching metadata topic records in KRaft mode
    - pattern: "kafka.server<type=broker-metadata-metrics><>(.+):"
      name: kafka_server_brokermetadatametrics_$1
      type: GAUGE
~~~

## strimzi-pod-monitor

~~~yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: cluster-operator-metrics
  namespace: monitoring
  labels:
    app: strimzi
spec:
  selector:
    matchLabels:
      strimzi.io/kind: cluster-operator
  namespaceSelector:
    any: true
  podMetricsEndpoints:
  - path: /metrics
    port: http
---
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: entity-operator-metrics
  namespace: monitoring
  labels:
    app: strimzi
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: entity-operator
  namespaceSelector:
    any: true
  podMetricsEndpoints:
  - path: /metrics
    port: healthcheck
---
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: bridge-metrics
  namespace: monitoring
  labels:
    app: strimzi
spec:
  selector:
    matchLabels:
      strimzi.io/kind: KafkaBridge
  namespaceSelector:
    any: true
  podMetricsEndpoints:
  - path: /metrics
    port: rest-api
---
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: kafka-resources-metrics
  namespace: monitoring
  labels:
    app: strimzi
spec:
  selector:
    matchExpressions:
      - key: "strimzi.io/kind"
        operator: In
        values: ["Kafka", "KafkaConnect", "KafkaMirrorMaker", "KafkaMirrorMaker2"]
  namespaceSelector:
    any: true
  podMetricsEndpoints:
  - path: /metrics
    port: tcp-prometheus
    relabelings:
    - separator: ;
      regex: __meta_kubernetes_pod_label_(strimzi_io_.+)
      replacement: $1
      action: labelmap
    - sourceLabels: [__meta_kubernetes_namespace]
      separator: ;
      regex: (.*)
      targetLabel: namespace
      replacement: $1
      action: replace
    - sourceLabels: [__meta_kubernetes_pod_name]
      separator: ;
      regex: (.*)
      targetLabel: kubernetes_pod_name
      replacement: $1
      action: replace
    - sourceLabels: [__meta_kubernetes_pod_node_name]
      separator: ;
      regex: (.*)
      targetLabel: node_name
      replacement: $1
      action: replace
    - sourceLabels: [__meta_kubernetes_pod_host_ip]
      separator: ;
      regex: (.*)
      targetLabel: node_ip
      replacement: $1
      action: replace
~~~

## values.yaml

~~~yaml
environment: "hanxux"
cloud: "" #azurecloudchina
product: "local"
commoninfra:
  kafka:
    name: kafka
    zoneredundant: "true"
    version: 3.7.1
    replicas: 3
    storage:
      type: persistent-claim
      size: "1Gi"
      class: sc-nfs
~~~

## 安装

~~~sh
helm upgrade -i commoninfra-kafka-config -n kube-system . --values ./values/values.yaml #--set oauth.secretProviderIdentityId=$secretProviderIdentityId
~~~

# 部署kafka-ui

