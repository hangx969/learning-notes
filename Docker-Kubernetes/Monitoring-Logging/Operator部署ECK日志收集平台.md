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

## ECK operator、CRD安装

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

