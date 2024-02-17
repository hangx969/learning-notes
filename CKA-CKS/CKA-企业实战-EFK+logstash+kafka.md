# EFK+logstash+kafka高吞吐量日志收集

- fluentd-->kafka-->logstash-->elasticsearch-->kibana
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

  