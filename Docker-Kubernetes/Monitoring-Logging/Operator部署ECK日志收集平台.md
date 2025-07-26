# 云原生日志收集

## 哪些日志需要收集

1. 操作系统日志
   - `/var/log/messages` or `/var/log/syslog`
2. k8s组件日志
   - k8s旧版，可指定日志路径，默认`/var/log/kube.*`
   - k8s新版，不能手动指定日志文件了，这不符合云原生设计要素。已经默认是收集到控制台，从而被`/var/log/message`收集了。
3. 业务应用程序日志:
   - 云原生应用：输出至控制台（在`/var/log/containers`下是能看到的）
   - 非云原生：输出到本地文件，就抓这个文件；有些容器内的日志，宿主机上是不好找的，那就直接sidecar去拿容器日志。

## 怎么收集

### 传统架构

1. **ELK（ElasticSearch + Logstash + Kibana）**：Logstash收集分析日志，发给ElasticSearch存储，Kibana从ES拿到数据可视化展示。
2. 在K8s中进行了专门设计，变成**EFK（ElasticSearch + Fluentd + Kibana）**: Fluentd提供了一些配置可以把宿主机日志，k8s组件日志一锅端了全部发送到ES集群。
3. 但是Fluentd对于亿级流量，支持性不好；而且配置复杂，很重。所以Fluentd又被替换成了**FileBeat/Fluent-bit**。但是不管怎么换，都是基于ES和Kibana的框架。

### Loki轻量架构

**Loki + Grafana + Promtail + Tempo**的架构，是grafana公司开发的轻量级日志框架，对于业务较少，日志流量不大的情况是比较新的框架。

但是为业务扩张、日志量大做打算，还是要依赖于传统EFK框架。

## 日志技术栈对比

### Logstash

- 成熟、功能齐全，可以收集、转换日志、对日志二次加工。
- 可以从文件、消息队列中读取日志。
- 可以保存日志到ES、mysql、opensearch、kafka

- 配置复杂，资源占用非常高。一般现在不用他收集日志，用他转换日志。

### Fluentd

- 大部分情况是用在k8s环境中。原生的配置可以直接收集宿主机日志、k8s组件日志、容器日志一锅端。
- 各种功能依赖于安装插件去实现，想要更改收集的源、发送的后端，就会配置起来很麻烦。
- 资源占用还是很高。

### Fluent-bit

- 轻量级Fluentd替代品，非常轻量大概只占4M内存，专门为IOT或者边缘场景设计的。
- 新工具，功能待完善。不适合亿级流量。

### Filebeat

- 也是属于ES stack厂家的一个轻量级日志收集器。
- Auto-discovery可以自动发现k8s日志。

- 也可以作为sidecar注入容器，在容器里采集日志文件。对于某些非云原生设计的应用，他们把日志输出到容器内某个日志文件，就很适合去收集。
- 侧重于日志收集，不适合复杂数据转换。如果用Logstash作为日志转换器的话，就用Filebeat作为日志收集 --> `ES + Filebeat + Logstash + Kibana`

综合来看Filebeat是k8s上收集日志的最推荐的组件。

# 生产环境日志收集架构

## EFK+kafka集群搭建

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202507192212133.png" alt="image-20250719221238971" style="zoom:50%;" />

日志量可能非常大，filebeat实例有很多，但是ES和Logstash集群只有一个。如果日志全部直接写入到ES和Logstash，压力很大，可能会有数据丢失等风险。所以一般会加一个kafka中间件作为缓冲。Logstash从kafka读取日志。

如果外部已经有了一套Kafka-Logstash-ES平台了，那么filebeat直接把日志抛到外部的Kafka的某一个topic当中就可以了。不用重复造轮子。

## Filebeat日志收集方案

### 容器日志

一般默认情况下容器日志在宿主机的/var/log/containers目录里面，filebeat可以直接获取到容器信息、pod信息、ns信息等。

filebeat也是pod形式部署的，怎么获取到宿主机的/var/log/containers？

- filebeat用daemonset部署，用hostpath把/var/log/containers挂到filebeat的/var/log/containers。就能采集了。

### 非云原生的文件日志

比如有些app pod的日志是写到/tmp/xxx.log，可以注入一个filebeat sidecar容器：

- 在app容器挂一个emptyDir的volume，共享日志路径；
- filebeat也挂这个emptyDir Volume，把日志存到自己容器里（filebeat容器里面都映射到固定位置比如/app/xxx.log，这样配置起来比较统一），就能抓走日志了。

### 操作系统和k8s组件日志

一般都在宿主机的/var/log路径下面，用hostPath挂到filebeat里面/var/log下，直接抓走。

# 云原生ECK日志平台部署

前面提到的ELK和EFK都是日志平台技术栈，而ECK（Elastic Cloud on k8s）是K8s的Operator，提供的是一个对ELK和EFK全生命周期管理的CRD资源。可以简化在K8s中部署、管理、扩展Elastic Stack的组件。

ECK的核心资源：

- ElasticSearch：用于管理和部署ES集群
- Kibana：管理部署Kibana
- Beat：管理和部署Filebeat服务
- Logstash：管理和部署Logstash服务

## ECK operator/CRD安装

1. 需要K8s版本>1.28。
2. operator最好单独放到一个namespace里面，不要把operator和资源都放一个namespace里面

### 方法1：yaml安装

参考：[Install ECK using the YAML manifests | Elastic Docs](https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/install-using-yaml-manifest-quickstart)

两条命令分别安装operator和CRD

~~~sh
kubectl create -f https://download.elastic.co/downloads/eck/3.0.0/crds.yaml
kubectl apply -f https://download.elastic.co/downloads/eck/3.0.0/operator.yaml
kubectl get -n elastic-system pods
~~~

### 方法2：helm安装

~~~sh
helm repo add elastic https://helm.elastic.co
helm repo update
helm pull elastic/eck-operator --version 3.0.0
~~~

## 基于CRD部署ES集群

ES的高级配置在这里：[Elasticsearch configuration | Elastic Docs](https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/elasticsearch-configuration)

### yaml文件部署

~~~yaml
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: es-cluster
  namespace: logging
spec:
  version: 8.16.1
  nodeSets: # 支持多种类型的节点，这里先用1个节点作为测试用
  - name: default
    count: 1
    # 用initContainer设置了虚拟内存空间，这里就保持unset
    # https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/virtual-memory
    # config:
    #node.store.allow_mmap: true # 开启内存映射，提高查询速度
    volumeClaimTemplates:
    - metadata:
        name: elasticsearch-data
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 1Gi
        storageClassName: sc-nfs
    podTemplate:
      spec:
        initContainers:
        - name: sysctl
          securityContext:
            privileged: true
            runAsUser: 0
          command: ['sh', '-c', 'sysctl -w vm.max_map_count=262144'] # #  提升虚拟地址空间的默认值
~~~

检查状态：

~~~sh
kubectl get es -n logging
# HEALTH变成green说明起来了
~~~

获取ES密码（用户名是elastic）：

~~~sh
PASSWORD=$(kubectl -n logging get secret es-cluster-es-elastic-user -o go-template='{{.data.elastic | base64decode}}') 
echo $PASSWORD

# 获取集群状态，得扩成3个的集群才有结果。单个是没有结果的
curl -u "elastic:$PASSWORD" https://<es-http-svc-IP>:9200/_cluster/health?pretty -k
~~~

## 基于CRD部署Kibana

注意Kibana一定要和ES版本一致。按照集群名称找到对应的ES集群。

Kibana的高级配置在这里：[Kibana configuration | Elastic Docs](https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/kibana-configuration)

### yaml文件部署

~~~yaml
apiVersion: kibana.k8s.elastic.co/v1
kind: Kibana
metadata:
  name: kibana
  namespace: logging
spec:
  version: 8.16.1
  count: 1
  elasticsearchRef:
    name: es-cluster
  http:
    service:
      spec:
        type: NodePort # default is ClusterIP
    tls:
      selfSignedCertificate:
        disabled: true

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kibana
  namespace: logging
spec:
  ingressClassName: nginx-default
  rules:
  - host: kibana.hanxux.local
    http:
      paths:
      - backend:
          service:
            name: kibana-kb-http
            port:
              number: 5601
        path: /
        pathType: ImplementationSpecific
~~~

~~~sh
# 检查状态，变成green说明起来了
kubectl get kibana -n logging
~~~

用户名密码和ES的一样

## 部署Zookeeper+Kafka集群

用helm分别部署zookeeper和kafka集群，用的是bitnami的chart：

~~~sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update bitnami
helm search repo bitnami/zookeeper
helm search repo bitnami/kafka
helm pull bitnami/zookeeper --version 13.8.5
helm pull bitnami/kafka --version 32.3.6
~~~

注意：

- 对于8.16的logstash，支持的是3.8.1的kakfa：https://www.elastic.co/guide/en/logstash/8.16/plugins-inputs-kafka.html#_description_35
- 所以要去查一下哪个helm chart版本是3.8.1的kafka：[kafka 30.1.8 · bitnami/bitnami](https://artifacthub.io/packages/helm/bitnami/kafka/30.1.8)。（30.1.8）



不需要单独部署zk，可以用bitname/kafka helm chart里面自带的zookeeper，kafka的values这样写：

~~~yaml
# 明确禁用 KRaft 模式
kraft:
  enabled: false

# 配置控制器副本数为 0（使用 Zookeeper 模式时）
controller:
  replicaCount: 0

# 配置 Broker（重要：Zookeeper 模式必需）
broker:
  replicaCount: 3
  persistence:
    enabled: true
    storageClass: "sc-nfs"
    accessModes:
      - ReadWriteOnce
    size: 3Gi

# 禁用所有认证机制，使用 PLAINTEXT
sasl:
  enabled: false

auth:
  enabled: false

listeners:
  client:
    containerPort: 9092
    protocol: PLAINTEXT
    name: CLIENT

  controller:
    name: CONTROLLER
    containerPort: 9093
    protocol: PLAINTEXT

  interbroker:
    containerPort: 9094
    protocol: PLAINTEXT
    name: INTERNAL

  external:
    containerPort: 9095
    protocol: PLAINTEXT
    name: EXTERNAL

# 启用 Zookeeper 模式
zookeeper:
  enabled: true
  replicaCount: 1
  persistence:
    enabled: true
    storageClass: "sc-nfs"
    accessModes:
      - ReadWriteOnce
    size: 300Mi
~~~

kafka安装完会有一个专门用于客户端连接的svc：kafka.logging.svc.cluster.local:9092，logstash和filebeat里面配置一下。

## 基于CRD部署Logstash

Logstash的高级配置在这里：[Configuration | Elastic Docs](https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/configuration-logstash)

注意：

1. 8.16的logstash，用的kafka版本为3.8.1:https://www.elastic.co/guide/en/logstash/8.16/plugins-inputs-kafka.html
2. 3.8.1 kafka对应的bitnami/kafka helm chart版本为：

~~~yaml
apiVersion: logstash.k8s.elastic.co/v1alpha1
kind: Logstash
metadata:
  name: logstash
  namespace: logging
spec:
  version: 8.16.1
  count: 1
  elasticsearchRefs:
  - name: es-cluster
    clusterName: es-cluster
  podTemplate:
    spec:
      volumes:
      - name: logstash-data
        emptyDir: {}
  pipelines:
    - pipeline.id: main
      config.string: |
        input {
          kafka {
            enable_auto_commit => true
            auto_commit_interval_ms => "1000"
            bootstrap_servers => "kafka:9092"
            topics => ["k8spodlogs"]
            codec => json
            group_id => "logstash"
          }
        }
        output {
          elasticsearch {
            hosts => [ "https://es-cluster-es-http:9200" ]
            index => "k8spodlogs-%{+YYYY.MM.dd}"
            ssl_enabled => true
            user => "elastic"
            password => "7JxHfm0659LLMPF6519aO5nu"
            ssl_certificate_authorities => "${ES_CLUSTER_ES_SSL_CERTIFICATE_AUTHORITY}"
          }
        }
~~~

注：

- 注意Logstash一定要和ES版本一致。Logstash可以指定连接到多个ES集群，集群名称设置好对应的ES。
- Logstash的数据不需要持久化，因为是从kafka读取数据，把kafka的数据持久化了就行。
- config可以配置多个，针对不同环境的发送到不同的kafka topic都可以加。

- 官网上直接用的环境变量注入ES的信息，也可以；如果ES是外部的，那就用这里的手动配的形式。
- ssl_certificate_authorities => "${`ES_CLUSTER`_ES_SSL_CERTIFICATE_AUTHORITY}" 注意配置正确的集群名称

## 基于CRD部署Filebeat

注意filebeat一定要和ES版本一致。可以配置自动发现、基于inputs的发现。

Filebeat的高级配置在这里：

- [Configuration | Elastic Docs](https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/configuration-beats)
- 自动发现：[Configuration | Elastic Docs](https://www.elastic.co/docs/deploy-manage/deploy/cloud-on-k8s/configuration-beats#k8s-beat-role-based-access-control-for-beats)

~~~yaml
apiVersion: beat.k8s.elastic.co/v1beta1
kind: Beat
metadata:
  name: filebeat
  namespace: logging
spec:
  type: filebeat
  version: 8.16.1
  # image:
  config:
    output.kafka:
      hosts: ["kafka:9092"]
      topic: '%{[fields.log_topic]}'
      #topic: 'k8spodlogs'
    # 配置自动发现
    filebeat.autodiscover.providers:
    - node: ${NODE_NAME}
      type: kubernetes
      templates:
      - config:
        - paths:
          - /var/log/messages
          tail_files: true
          type: log
          fields:
            log_topic: k8spodlogs
            log_type: system
      - config:
        - paths:
          - /var/log/containers/*${data.kubernetes.container.id}.log
          tail_files: true
          type: container
          fields:
            log_topic: k8spodlogs
          processors:
          - add_cloud_metadata: {}
          - add_host_metadata: {}
          - drop_event:
              when:
                or: # and
                - not:
                    equals:
                      kubernetes.namespace_labels.filebeat: "true"
    # 全局设置，忽略filebeat容器自身的日志
    processors:
    - add_cloud_metadata: {}
    - add_host_metadata: {}
    - drop_event:
        when:
          or:
          - equals:
              kubernetes.container.name: "filebeat"
  daemonSet:
    podTemplate:
      spec:
        serviceAccountName: filebeat
        automountServiceAccountToken: true
        terminationGracePeriodSeconds: 30
        dnsPolicy: ClusterFirstWithHostNet
        hostNetwork: true # Allows to provide richer host metadata
        containers:
        - name: filebeat
          securityContext:
            runAsUser: 0
            # If using Red Hat OpenShift uncomment this:
            #privileged: true
          volumeMounts:
          - name: varlogcontainers
            mountPath: /var/log/containers
          - name: varlogpods
            mountPath: /var/log/pods
          - name: varlibdockercontainers
            mountPath: /var/lib/docker/containers
          - name: messages
            mountPath: /var/log/messages
          env:
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
        volumes:
        - name: varlogcontainers
          hostPath:
            path: /var/log/containers
        - name: varlogpods
          hostPath:
            path: /var/log/pods
        - name: varlibdockercontainers
          hostPath:
            path: /var/lib/docker/containers
        - name: messages
          hostPath:
            path: /var/log/messages
        tolerations:
          - key: "node-role.kubernetes.io/control-plane"
            operator: "Equal"
            effect: "NoSchedule"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: filebeat
  namespace: logging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: elastic-beat-autodiscover-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: elastic-beat-autodiscover
subjects:
- kind: ServiceAccount
  name: filebeat
  namespace: logging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: elastic-beat-autodiscover
rules:
- apiGroups:
  - ""
  resources:
  - nodes
  - namespaces
  - events
  - pods
  verbs:
  - get
  - list
  - watch
- apiGroups: ["apps"]
  resources:
  - replicasets
  verbs:
  - get
  - list
  - watch
- apiGroups: ["batch"]
  resources:
  - jobs
  verbs:
  - get
  - list
  - watch
~~~

注意：

1. /var/log/containers软链到了/var/log/pods，两个都要挂进去。软链接的文件名可能会被解析一些字段。
2. 这种配置把所有输出到控制台的容器日志一锅端全部收集走了。但是不能收集容器内的文件日志。

### ns打标签

由于filebeat配置了自动发现基于namespace，所以要给想收集日志的ns打标签

~~~yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    filebeat: "true"
~~~

~~~sh
kubectl label namespace kube-system filebeat=true
~~~

## 用Kibana UI查看日志

1. 待所有的 Pod 启动完成后，即可使用 Kibana 查询日志。
2. 用户名密码是在logstash的配置文件里面指定的（elastic/7JxHfm0659LLMPF6519aO5nu）登录 Kibana 后，搜索框搜索 Index Management，即可查看索引
3. 之后点击 Dashboards --> data views 创建一个 data view
4. 然后就可以查看日志了

## Filebeat收集指定namespace的日志

