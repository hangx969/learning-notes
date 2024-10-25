# EFK+logstash+kafka高吞吐量日志收集

- fluentd采集日志数据 --> kafka缓冲 --> logstash消费数据-格式转换 --> elasticsearch --> kibana
- 这套方案加了缓冲，适合大量日志（TB每日）的环境

## 部署fluentd

- https://github.com/kubernetes/kubernetes/blob/master/cluster/addons/fluentd-elasticsearch/fluentd-es-ds.yaml

- 给想要收日志的节点打标签，给ds的标签选择器来调度

  ~~~sh
  kubectl label nodes master-1 beta.kubernetes.io/fluentd-ds-ready=true
  kubectl label nodes node-1 beta.kubernetes.io/fluentd-ds-ready=true
  kubectl label nodes node-2 beta.kubernetes.io/fluentd-ds-ready=true
  ~~~

- 创建configmap（原始没接入kafka的配置）

~~~yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: fluentd-config
  namespace: logging
  labels:
    addonmanager.kubernetes.io/mode: Reconcile
data:
  system.conf: |-
    <system>
      root_dir /tmp/fluentd-buffers/
    </system>
  containers.input.conf: |-
    <source>
      @id fluentd-containers.log
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/es-containers.log.pos
      time_format %Y-%m-%dT%H:%M:%S.%NZ
      localtime
      tag raw.kubernetes.*
      format json
      read_from_head true
    </source>
    # Detect exceptions in the log output and forward them as one log entry.
    <match raw.kubernetes.**>
      @id raw.kubernetes
      @type detect_exceptions
      remove_tag_prefix raw
      message log
      stream stream
      multiline_flush_interval 5
      max_bytes 500000
      max_lines 1000
    </match>
  system.input.conf: |-
    # Logs from systemd-journal for interesting services.
    <source>
      @id journald-docker
      @type systemd
      filters [{ "_SYSTEMD_UNIT": "docker.service" }]
      <storage>
        @type local
        persistent true
      </storage>
      read_from_head true
      tag docker
    </source>
    <source>
      @id journald-kubelet
      @type systemd
      filters [{ "_SYSTEMD_UNIT": "kubelet.service" }]
      <storage>
        @type local
        persistent true
      </storage>
      read_from_head true
      tag kubelet
    </source>
  forward.input.conf: |-
    # Takes the messages sent over TCP
    <source>
      @type forward
    </source>
  output.conf: |-
    # Enriches records with Kubernetes metadata
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    <match **>
      @id elasticsearch
      @type elasticsearch
      @log_level info
      include_tag_key true
      host 192.168.40.180
      port 9200
      logstash_format true
      request_timeout    30s
      <buffer>
        @type file
        path /var/log/fluentd-buffers/kubernetes.system.buffer
        flush_mode interval
        retry_type exponential_backoff
        flush_thread_count 2
        flush_interval 5s
        retry_forever
        retry_max_interval 30
        chunk_limit_size 2M
        queue_limit_length 8
        overflow_action block
      </buffer>
    </match>
~~~

- 创建ds

  ~~~yaml
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: fluentd-es
    namespace: logging
    labels:
      k8s-app: fluentd-es
      kubernetes.io/cluster-service: "true"
      addonmanager.kubernetes.io/mode: Reconcile
  ---
  kind: ClusterRole
  apiVersion: rbac.authorization.k8s.io/v1
  metadata:
    name: fluentd-es
    labels:
      k8s-app: fluentd-es
      kubernetes.io/cluster-service: "true"
      addonmanager.kubernetes.io/mode: Reconcile
  rules:
  - apiGroups:
    - ""
    resources:
    - "namespaces"
    - "pods"
    verbs:
    - "get"
    - "watch"
    - "list"
  ---
  kind: ClusterRoleBinding
  apiVersion: rbac.authorization.k8s.io/v1
  metadata:
    name: fluentd-es
    labels:
      k8s-app: fluentd-es
      kubernetes.io/cluster-service: "true"
      addonmanager.kubernetes.io/mode: Reconcile
  subjects:
  - kind: ServiceAccount
    name: fluentd-es
    namespace: logging
    apiGroup: ""
  roleRef:
    kind: ClusterRole
    name: fluentd-es
    apiGroup: ""
  ---
  apiVersion: apps/v1
  kind: DaemonSet
  metadata:
    name: fluentd-es
    namespace: logging
    labels:
      k8s-app: fluentd-es
      version: v2.0.4
      kubernetes.io/cluster-service: "true"
      addonmanager.kubernetes.io/mode: Reconcile
  spec:
    selector:
      matchLabels:
        k8s-app: fluentd-es
        version: v2.0.4
    template:
      metadata:
        labels:
          k8s-app: fluentd-es
          kubernetes.io/cluster-service: "true"
          version: v2.0.4
        # This annotation ensures that fluentd does not get evicted if the node
        # supports critical pod annotation based priority scheme.
        # Note that this does not guarantee admission on the nodes (#40573).
        annotations:
          scheduler.alpha.kubernetes.io/critical-pod: ''
      spec:
        serviceAccountName: fluentd-es
        containers:
        - name: fluentd-es
          image: cnych/fluentd-elasticsearch:v2.0.4
          env:
          - name: FLUENTD_ARGS
            value: --no-supervisor -q
          resources:
            limits:
              memory: 500Mi
            requests:
              cpu: 100m
              memory: 200Mi
          volumeMounts:
          - name: varlog
            mountPath: /var/log
          - name: varlibdockercontainers
            mountPath: /var/lib/docker/containers
            readOnly: true
          - name: config-volume
            mountPath: /etc/fluent/config.d
        nodeSelector:
          beta.kubernetes.io/fluentd-ds-ready: "true"
        tolerations:
        - key: node-role.kubernetes.io/master
          operator: Exists
          effect: NoSchedule
        terminationGracePeriodSeconds: 30
        volumes:
        - name: varlog
          hostPath:
            path: /var/log
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
        - name: config-volume
          configMap:
            name: fluentd-config
  ~~~


## fluentd接入kafka

~~~yaml
kind: ConfigMap
apiVersion: v1
metadata:
  name: fluentd-config
  namespace: logging
  labels:
    addonmanager.kubernetes.io/mode: Reconcile
data:
  system.conf: |-
    <system>
      root_dir /tmp/fluentd-buffers/
    </system>
  containers.input.conf: |-
    <source>
      @id fluentd-containers.log
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/es-containers.log.pos
      time_format %Y-%m-%dT%H:%M:%S.%NZ
      localtime
      tag raw.kubernetes.*
      format json
      read_from_head true
    </source>
    # Detect exceptions in the log output and forward them as one log entry.
    <match raw.kubernetes.**>
      @id raw.kubernetes
      @type detect_exceptions
      remove_tag_prefix raw
      message log
      stream stream
      multiline_flush_interval 5
      max_bytes 500000
      max_lines 1000
    </match>
  system.input.conf: |-
    # Logs from systemd-journal for interesting services.
    <source>
      @id journald-docker
      @type systemd
      filters [{ "_SYSTEMD_UNIT": "docker.service" }]
      <storage>
        @type local
        persistent true
      </storage>
      read_from_head true
      tag docker
    </source>
    <source>
      @id journald-kubelet
      @type systemd
      filters [{ "_SYSTEMD_UNIT": "kubelet.service" }]
      <storage>
        @type local
        persistent true
      </storage>
      read_from_head true
      tag kubelet
    </source>
  forward.input.conf: |-
    # Takes the messages sent over TCP
    <source>
      @type forward
    </source>
  output.conf: |-
    # Enriches records with Kubernetes metadata
    <filter kubernetes.**>
      @type kubernetes_metadata
    </filter>
    <match **>
      @id kafka
      @type kafka2
      @log_level info
      include_tag_key true
      # list of seed brokers
      brokers kafka ip:9092 #这里填入kafka ip
      use_event_time true
      # buffer settings
      <buffer>
        @type file
        path /var/log/fluentd-buffers/kubernetes.system.buffer
        flush_mode interval
        retry_type exponential_backoff
        flush_thread_count 2
        flush_interval 5s
        retry_forever
        retry_max_interval 30
        chunk_limit_size 2M
        queue_limit_length 8
        overflow_action block
      </buffer>
      # data type settings
      <format>
        @type json
      </format>
      # topic settings
      topic_key topic
      default_topic messages #交给kafka的topic
      # producer settings
      required_acks -1
      compression_codec gzip
    </match>
~~~

## 配置logstash

- 配置logstash消费messages日志写入elasticsearch

~~~yaml
cat config/kafkaInput_fluentd.conf 

input {
    kafka {
        bootstrap_servers => ["kafka ip:9092"]
        client_id => "fluentd"
        group_id => "fluentd"
        consumer_threads => 1
        auto_offset_reset => "latest"
        topics => ["messages"]
    }
}
 
filter {
        json{
                source => "message"
        }
        
       ruby {
       code => "event.set('timestamp', event.get('@timestamp').time.localtime + 8*60*60)"
       }
      ruby {
        code => "event.set('@timestamp',event.get('timestamp'))"
       }
      ruby {
        code => "event.set('find_time',event.get('@timestamp').time.localtime - 8*60*60)"
       }
     mutate {
    remove_field => ["timestamp"]
    remove_field => ["message"]
    }
     
} 
output {
          elasticsearch{
               hosts => ["es ip地址: 9200"]
               index => "kubernetes_%{+YYYY_MM_dd}"
 
          }
#    stdout {
#           codec => rubydebug
#           }
}
~~~

- 启动logstash

  ~~~sh
  nohup ./bin/logstash -f config/kafkaInput_fluentd.conf --config.reload.automatic --path.data=/opt/logstash/data_fluentd 2>&1 > fluentd.log &
  ~~~


# EFK+logstash+kafka具体案例分享

## fluentd配置文件

- 在 Kubernetes 集群中，Fluentd 配置文件定义了日志从哪里获取、如何处理和将其发送到哪里。可以将 Fluentd 配置文件存储为 ConfigMap。下面是一个简单的 Fluentd 配置文件，它从节点上的 Docker 容器中收集日志，并将其发送到 Kafka。

~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: kube-system
  labels:
    k8s-app: fluentd-logging
data:
  fluent.conf: |-
    <source>
      @type tail
      path /var/log/containers/*.log
      pos_file /var/log/es-containers.log.pos
      tag kubernetes.*
      read_from_head true
      <parse>
        @type json
        time_key time
        time_format %Y-%m-%dT%H:%M:%S.%N%z
      </parse>
    </source>

    <match kubernetes.**>
      @type kafka_buffered
      brokers kafka:9092
      topic logs
      buffer_type memory
      buffer_chunk_records 1000
      buffer_queue_limit 1000
      flush_interval 5s
      output_data_type json
      output_include_time true
    </match>
~~~

> 1. @type tail: 指定输入插件的类型为 tail，表示该插件将读取文件末尾的日志数据。
> 2. path /var/log/containers/*.log: 指定要监控的日志文件路径，这里是通配符 *.log 表示匹配所有以 .log 结尾的文件，位于 /var/log/containers/ 目录下。
> 3. pos_file /var/log/es-containers.log.pos: 指定用于保存已读取日志文件位置的文件路径，以确保 Fluentd 在重启后可以继续从上次停止的位置读取日志，避免重复读取。
> 4. tag kubernetes.*: 分配一个标签给这些日志事件，以便在后续的 Fluentd 配置中可以根据标签进行过滤或者应用不同的处理规则。这里的标签是 kubernetes.*，表示匹配以 "kubernetes." 开头的标签。
> 5. read_from_head true: 表示在启动 Fluentd 时，从文件头开始读取日志。如果设置为 false，则从文件末尾开始读取。
> 6. <parse> 和 </parse> 之间的部分是用于解析日志内容的配置块。
>    @type json: 指定解析器的类型为 JSON，表明日志是以 JSON 格式存储的。
>    time_key time: 指定用于提取时间戳的键，这里是 time。
>    time_format %Y-%m-%dT%H:%M:%S.%N%z: 指定时间戳的格式，这里使用了 ISO 8601 格式，包括日期和时间，并带有纳秒和时区信息。

## fluentd部署

~~~yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-system
  labels:
    k8s-app: fluentd-logging
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluent/fluentd:v1.12.4-1.0
        env:
        - name: FLUENT_UID
          value: "0"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: fluentdconf
          mountPath: /fluentd/etc/
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: fluentdconf
        configMap:
          name: fluentd-config
~~~

## 安装配置kafka和logstash

- Kafka 是一个分布式流平台，用于收集和处理大量的日志数据。Logstash是一个开源数据处理工具，可以将数据从不同来源采集、转换和发送到指定的目的地。在本例中，Kafka 用于收集 Fluentd 发送的日志数据，而 Logstash 用于将这些数据转换为 Elasticsearch 可以索引的格式。
- 首先，需要创建一个 Kafka 集群，可以使用 Docker Compose 快速搭建一个本地 Kafka 环境。下面是一个简单的 Docker Compose 文件，它定义了一个包含一个 Kafka broker 和一个 ZooKeeper 实例的 Kafka 集群。

~~~yaml
version: '3'
services:
  zookeeper:
    image: 'confluentinc/cp-zookeeper:5.3.1'
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - '2181:2181'
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: 'confluentinc/cp-kafka:5.3.1'
    hostname: kafka
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - '9092:9092'
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
~~~

- 然后，需要安装和配置 Logstash。可以使用 Docker 安装 Logstash，并将其配置为从 Kafka 中读取数据，并将其发送到 Elasticsearch。下面是一个简单的 Logstash 配置文件，它从 Kafka 主题中读取数据，并将其发送到 Elasticsearch。

~~~yaml
input {
  kafka {
    bootstrap_servers => "kafka:9092"
    topics => ["logs"]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "kubernetes-%{+YYYY.MM.dd}"
  }
}
~~~

## 安装配置Elasticsearch和Kibana

- Elasticsearch 是一个分布式搜索和分析引擎，可以将大量的结构化和非结构化数据存储到一个地方，并支持实时搜索和分析。Kibana 是一个用于 Elasticsearch 的开源分析和可视化平台，可以帮助您快速理解和探索 Elasticsearch 中的数据。
- 首先，需要创建一个 Elasticsearch 集群。可以使用 Docker Compose 快速搭建一个本地 Elasticsearch 环境。下面是一个简单的 Docker Compose 文件，它定义了一个包含三个 Elasticsearch 节点的 Elasticsearch 集群。

~~~sh
version: '3'
services:
  elasticsearch1:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.12.0
    container_name: elasticsearch1
    environment:
      - node.name=elasticsearch1
      - discovery.seed_hosts=elasticsearch2,elasticsearch3
      - cluster.initial_master_nodes=elasticsearch1
      - discovery.type=single-node
environment:
      - "ES_JAVA_OPTS=-Xmx256m -Xms256m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    ports:
      - 9200:9200
  elasticsearch2:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.12.0
    container_name: elasticsearch2
    environment:
      - node.name=elasticsearch2
      - discovery.seed_hosts=elasticsearch1,elasticsearch3
      - cluster.initial_master_nodes=elasticsearch1
      - "ES_JAVA_OPTS=-Xmx256m -Xms256m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
  elasticsearch3:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.12.0
    container_name: elasticsearch3
    environment:
      - node.name=elasticsearch3
      - discovery.seed_hosts=elasticsearch1,elasticsearch2
      - cluster.initial_master_nodes=elasticsearch1
      - "ES_JAVA_OPTS=-Xmx256m -Xms256m"
    ulimits:
      memlock:
        soft: -1
        hard: -1
~~~

- 然后，需要安装和配置 Kibana。可以使用 Docker 安装 Kibana，并将其配置为连接到 Elasticsearch。下面是一个简单的 Kibana 配置文件，它指定了 Elasticsearch 的地址和端口号。

~~~yaml
server.name: kibana
server.host: "0"
elasticsearch.hosts: ["http://elasticsearch1:9200"]
~~~

## 测试EFK系统

~~~sh
$ kubectl run --rm -it --image=alpine:3.12 test-pod -- /bin/sh
/ # echo "test log message" >> /var/log/test.log
/ # exit
$ kubectl logs test-pod
test log message
$ curl -s http://elasticsearch1:9200/_search?q=test
{"took":2,"timed_out":false,"_shards":{"total":1,"successful":1,"skipped":0,"failed":0},"hits":{"total":{"value":1,"relation":"eq"},"max_score":0.2876821,"hits":[{"_index":"logstash-2021.05.01-000001","_type":"_doc","_id":"2zL-QnoBE-kYj-SbJZ4x","_score":0.2876821,"_source":{"@timestamp":"2021-05-01T06:26:44.586Z","@version":"1","message":"test log message","host":"test-pod","container_name":"test-pod","kubernetes":{"pod_name":"test-pod","namespace_name":"default","pod_id":"4e4de90e-9a9b-46b8-b1c6-b1fd6ce97b6c","labels":{"run":"test-pod"}}}}]}}
~~~

