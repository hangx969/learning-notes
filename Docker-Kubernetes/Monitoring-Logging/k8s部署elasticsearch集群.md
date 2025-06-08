# ES

- Elasticsearch是一个分布式可扩展的实时搜索和分析引擎，有restful接口，设计用于云计算中，能够达到实时搜索，稳定，可靠，快速，安装使用方便。

# 创建nfs存储类

- 安装nfs见CKA-storage-nfs章节

~~~sh
mkdir es
cd es/
tee es-storageclass.yaml <<'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs
provisioner: example.com/nfs
EOF
~~~

# 部署ES

- 准备镜像

~~~sh
docker load -i busybox.tar.gz 
docker load -i elasticsearch.tar.gz
kubectl create ns es
~~~

- 创建cm

~~~sh
apiVersion: v1
kind: ConfigMap
metadata:
  name: sirc-elasticsearch-config
  namespace: es
  labels:
    app: elasticsearch
data:             #具体挂载的配置文件
  elasticsearch.yml: |+     
cluster.name: es-test
#配置的集群名称，默认是elasticsearch，es服务会通过广播方式自动连接在同一网段下的es服务，通过多播方式进行通信，同一网段下可以有多个集群，通过集群名称这个属性来区分不同的集群。
node.name: ${MY_POD_NAME}    
#环境变量，通过kubectl explain pod.spec.containers.env.valueFrom.fieldRef获取，当前配置所在机器的节点名，你不设置就默认随机指定一个name列表中名字，该name列表在es的jar包中config文件夹里name.txt文件中。当创建ES集群时，保证同一集群中的cluster.name名称是相同的，node.name节点名称是不同的。
path.data: /usr/share/elasticsearch/data 
#设置索引数据的存储路径，默认是es根目录下的data文件夹，可以设置多个存储路径，用逗号隔开，例：path.data: /path/to/data1,/path/to/data2
path.logs: /usr/share/elasticsearch/logs 
#设置日志文件的存储路径，默认是es根目录下的logs文件夹
network.host: 0.0.0.0 #全网地址
http.port: 9200 #设置对外服务的http端口，默认为9200。
transport.tcp.port: 9300 #设置节点之间交互的tcp端口，默认是9300。 如我搭建多节点，我的配置分别是9300、9302、9304
discovery.zen.ping.unicast.hosts: ["elasticsearch-0.elasticsearch-cluster.es:9300","elasticsearch-1.elasticsearch-cluster.es:9300","elasticsearch-2.elasticsearch-cluster.es:9300"]
#设置集群中master节点的初始列表，可以通过这些节点来自动发现新加入集群的节点。
node.master: true
#指定该节点是否有资格被选举成为node（注意这里只是设置成有资格， 不代表该node一定就是master），默认是true，es是默认集群中的第一台机器为master，如果这台机挂了就会重新选举master。
node.data: true #指定该节点是否存储索引数据，默认为true。
http.cors.enabled: true #支持跨域
http.cors.allow-origin: "*" 
#当设置允许跨域，默认为*,表示支持所有域名，如果我们只是允许某些网站能访问，那么可以使用正则表达式。比如只允许本地地址。 /https?:\ /\ /localhost(:[0-9]+)?/
bootstrap.system_call_filter: false #启动进行系统检测
xpack.security.enabled: false #不用密码登录
indices.fielddata.cache.size: 60%
indices.queries.cache.size: 40%
~~~

- 创建StatefulSet，ES属于数据库类型的应用，此类应用适合StatefulSet类型

~~~yaml
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: elasticsearch
  namespace: es
spec:
  serviceName: "elasticsearch-cluster"   #填写没有IP的service
  replicas: 3
  selector: 
    matchLabels: 
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      initContainers:
      - name: fix-permissions
        image: busybox
        imagePullPolicy: IfNotPresent
        command: ["sh", "-c", "chown -R 1000:1000 /usr/share/elasticsearch/data"]
        securityContext:
          privileged: true
        volumeMounts:
        - name: es-data
          mountPath: /usr/share/elasticsearch/data
      - name: increase-vm-max-map
        image: busybox
        imagePullPolicy: IfNotPresent
        command: ["sysctl", "-w", "vm.max_map_count=262144"]
        securityContext:
          privileged: true
      - name: increase-fd-ulimit
        image: busybox
        imagePullPolicy: IfNotPresent
        command: ["sh", "-c", "ulimit -n 65536"]
        securityContext:
          privileged: true
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:6.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 9200
          name: elasticsearch
        env:
        - name: MY_POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name  #metadata.name获取自己pod名称添加到变量MY_POD_NAME，status.hostIP获取自己ip等等可以自己去百度
        - name: ES_JAVA_OPTS
          value: "-Xms1g -Xmx1g"
        volumeMounts:                           
          - name: elasticsearch-config            #挂载配置
            mountPath: /usr/share/elasticsearch/config/elasticsearch.yml
            subPath: elasticsearch.yml
          - name: es-data                  #挂载数据
            mountPath: /usr/share/elasticsearch/data 
      volumes:
      - name: elasticsearch-config
        configMap:                                #configMap挂载
          name: sirc-elasticsearch-config
  volumeClaimTemplates:                     #这步自动创建pvc，并挂载动态pv
    - metadata:
        name: es-data
      spec:
        accessModes: ["ReadWriteMany"]
        storageClassName: nfs
        resources:
          requests:
            storage: 1Gi
#创建Service
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch-cluster  #无头服务的名称，需要通过这个获取ip，与主机的对应关系
  namespace: es
  labels:
    app: elasticsearch
spec:
  ports:
    - port: 9200
      name: elasticsearch
  clusterIP: None
  selector:
    app: elasticsearch  
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch   #service服务的名称，向外暴露端口
  namespace: es
  labels:
    app: elasticsearch
spec:
  type: NodePort
  selector:
    app: elasticsearch
  ports:
    - port: 9200
      name: elasticsearch
~~~

- 访问ES集群：任意node IP加NodePort
