# KEDA介绍

文档1：[Getting Started | KEDA](https://keda.sh/docs/2.17/)

## 背景

K8s原生的HPA基于内存和cpu扩缩容，会有一些局限性，比如某些情况下cpu内存的异常升高是因为程序异常或者基础组件异常，这时候盲目扩容反而适得其反。

KEDA被称为下一代弹性扩容：

1. 基于事件扩缩容

   程序可以自定义抛出的消息或者日志，告诉KEDA执行扩容。真实反映了程序内部的问题。

2. 基于消息队列扩缩容

   kafka、rabbitmq等消息队列的指标可以用作做缩容指标

3. 基于流量扩缩容

   流量高并发情况下可以扩缩容。比如基于从HTTP请求数量自动扩缩容相关服务。

4. 基于自定义指标扩缩容

   自己抛出的数据可以被用来扩缩容

5. 基于各种策略扩缩容

   比如设置基于时间的触发器，定时扩缩容。

6. 无服务架构（与Serverless类似）

   KEDA甚至还支持缩容到0，这是HPA做不到的。比如有一些大数据处理pod，在特定数据到来的时候才需要启动，一启动就要占用大量资源，这时候在不需要的时候就缩容到0是非常有用的。

## 概念

KEDA - KubernetesEvent-Driven Autoscaler：是一个基于k8s事件驱动的自动伸缩器。使用KEDA，可以根据需要处理的事件数量、消息队列来驱动k8s中任何服务的伸缩。

KEDA的核心思想是：只有有任务需要处理时，才扩展应用，并且在没有工作时缩减资源，甚至可以缩容到0。这提高资源利用率、还降低了成本。

## 架构和工作流程

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202508241048999.png" alt="image-20250824104832810"  />

1. ScaledObject：
   - KEDA核心CRD资源，用于控制deployment等资源和副本数，可以指定多种事件和消息源，来控制副本数，同时支持scaled to 0
2. Controller：
   - KEDA控制器pod，监听APIServer，通知Scaler调整副本数量，Scaler也是去创建HPA来完成扩缩容
3. Scaler：
   - Scaler与HPA协同工作，以实现自动扩展
4. External Trigger Source：
   - 外部事件或者数据源，应用可以请求这个接口抛过来数据，可以触发KEDA的扩展操作
5. Metrics Adapter：
   - 用于定义自定义指标

## 核心资源

1. ScaledObject：
   - KEDA核心CRD资源，用于控制deployment等资源和副本数，可以指定多种事件和消息源，来控制副本数，同时支持scaled to 0
   - 官网查看支持那些事件源：[Scalers | KEDA](https://keda.sh/docs/2.17/scalers/)

2. ScaledJob：
   - 用于触发一次性job任务，可以根据多种外部事件源出发创建一次性任务。类似Serverless
3. TriggerAuthentication：
   - 用于管理KEDA Scaler与外部事件源（如RabbitMQ、Kafka等）之间的身份验证和授权，支持环境变量、ConfigMap、Secret等。

# 资源定义

## ScaledObject

~~~yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: video-processing-scaledobject
  namespace: default
spec:
  scaleTargetRef:
    name: order-processor # 目标deployment名称
  pollingInterval: 30 # 每30s检查一次队列
  cooldownPeriod: 300 # 扩缩容后等待5分钟。防止扩缩容抖动
  minReplicaCount: 1
  maxReplicaCount: 10
  triggers:
  - type: rabbitmq
    metadata:
      queueName: "video-processing-queue" # rabbitmq队列名称
      mode: QueueLength # 监听类型
      value: "50" # 当队列中每个实例平均消息50条及以上时触发扩容
  authenticationRef: # 不推荐直接把用户名密码写在这里。都是用一个TriggerAuthentication绑定
    name: keda-trigger-auth-rabbitmq-conn # TriggerAuthentication名称
~~~

## ScaledJob

~~~yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledJob
metadata:
  name: video-processing-scaledjob
  namespace: default
spec:
  jobTargetRef:
    parallelism: 1 # 每次只创建一个job实例
    completions: 1 # 每个Job只运行一次
    template:
      spec:
        containers:
        - name: video-processer
          image: busybox:1.28
  pollingInterval: 30 # 每30s检查一次队列
  maxReplicaCount: 10 # 最多同时运行10个job
  successfulJobHistoryLimit: 3 # 保留3个成功job的历史
  failedJobHistoryLimit: 1 # 保留1个失败的job历史
  triggers:
  - type: rabbitmq
    metadata:
      queueName: "video-processing-queue" # rabbitmq队列名称
      mode: QueueLength # 监听类型
      value: "50" # 当队列中每个实例平均消息50条及以上时触发扩容
  authenticationRef: # 不推荐直接把用户名密码写在这里。都是用一个TriggerAuthentication绑定
    name: keda-trigger-auth-rabbitmq-conn # TriggerAuthentication名称
~~~

## TriggerAuthentication

连接基础组件的时候需要认证，KEDA设计了单独的资源来保存认证信息。

TriggerAuthentication直接去k8s secret里面读，他自己并不保存认证信息。

~~~yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secrets
  namespace: default
type: Opaque
dataString:
  mysql_conn_str: user:password@tcp(mysql:3306)/status_db

---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: keda-trigger-auth-mysql-conn
  namespace: default
spec: 
  secretTargetRef:
  - parameter: connectionString # Scaler参数名字。固定值不能改。应该填啥去keda官网查。
    name: mysql-secret # secret名称
    key: mysql_conn_str # secret的key名称
  
  # 也支持基于configMap加载
  # configMapRef:
  # - parameter: connectionString # Scaler参数名字。固定值不能改。应该填啥去keda官网查。
  #   name: keda-cm-name # cm名称
  #   key: azure-storage-connectionstring # cm的key名称
  
  # 也支持基于env加载
  # - parameter: region # Scaler参数名字。固定值不能改。应该填啥去keda官网查。
  #   name: my-env-car # 取哪个环境变量的值 
  #   containerName: my-container # 从哪个容器中取（keda管理的deployment中的pod中的某个container）
~~~

# 基于helm部署KEDA

官网安装说明：[Deploying KEDA | KEDA](https://keda.sh/docs/2.17/deploy/#helm)

artifacthub：[keda 2.17.2 · helm/kedacore](https://artifacthub.io/packages/helm/kedacore/keda)

github release: [Releases · kedacore/keda](https://github.com/kedacore/keda/releases)

## 下载helm chart

~~~sh
helm repo add kedacore https://kedacore.github.io/charts 
helm repo update kedacore
helm pull kedacore/keda --version 2.17.2
~~~

## 安装

~~~sh
helm install keda -n keda --create-namespace -f values.yaml .
~~~

# KEDA实战

## 周期性扩缩容

KEDA支持周期性弹性收缩服务，且支持缩容至0。使用场景：

1. 比如有很多任务，占用大量资源，不能在白天跑，需要在晚上跑。
2. 比如有个服务只有每天早上7-9点属于业务高峰，就可以利用KEDA实现在7-9点扩展服务，除此之外的时间缩减副本，以节省资源。

~~~yaml
apiVersion: keda.sh/v1alpha1 
kind: ScaledObject
metadata:
  name: cron-scaledobject 
  namespace: default 
spec: 
  scaleTargetRef: 
    name: nginx-hpa # 扩容对象是deployment 
  minReplicaCount: 0 # 最低副本数
  cooldownPeriod: 300 # 冷却期：到end时间后，过多久再缩容 
  triggers:
  - type: cron
    metadata:
      timezone: Asia/Shanghai
      # 分钟 小时 日 月 星期
      start: 45 10 * * * # 每天北京时间10:45扩容
      end: 55 10 * * * # 每天北京时间10:55缩容
      desiredReplicas: "3" # 扩容后的副本数
~~~

## 基于RabbitMQ消息队列扩缩容

KEDA支持基于消息队列的弹性伸缩，比如基于RabbitMQ、Kafka、Redis队列进行扩缩容，以便更快的处理处理。

### 创建测试RabbitMQ

~~~yaml
apiVersion: v1 
kind: Service 
metadata: 
  name: rabbitmq
spec: 
  type: NodePort 
  selector: 
    app: rabbitmq 
  ports: 
  - name: web 
    port: 5672 
    protocol: TCP 
    targetPort: 5672 
  - name: http 
    port: 15672 
    protocol: TCP 
    targetPort: 15672 
--- 
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  labels: 
    app: rabbitmq 
  name: rabbitmq 
spec: 
  replicas: 1 
  selector: 
    matchLabels: 
      app: rabbitmq 
  strategy: 
    rollingUpdate: 
      maxSurge: 1 
      maxUnavailable: 0 
    type: RollingUpdate 
  template: 
    metadata: 
      labels: 
        app: rabbitmq 
    spec: 
      containers: 
      - env: 
        - name: TZ 
          value: Asia/Shanghai 
        - name: LANG 
          value: C.UTF-8 
        - name: RABBITMQ_DEFAULT_USER 
          value: user 
        - name: RABBITMQ_DEFAULT_PASS 
          value: password 
        image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq:4.0.5-management-alpine  
        imagePullPolicy: IfNotPresent 
        livenessProbe: 
          failureThreshold: 2 
          initialDelaySeconds: 30 
          periodSeconds: 10 
          successThreshold: 1 
          tcpSocket: 
            port: 5672 
          timeoutSeconds: 2 
        name: rabbitmq 
        ports: 
        - containerPort: 5672 
          name: web 
          protocol: TCP 
        readinessProbe: 
          failureThreshold: 2 
          initialDelaySeconds: 30 
          periodSeconds: 10 
          successThreshold: 1 
          tcpSocket: 
            port: 5672 
          timeoutSeconds: 2
~~~

通过NodePort访问RabbitMQ UI，注意用的是name为http的端口

### 模拟消息写入

~~~yaml
apiVersion: batch/v1 
kind: Job 
metadata: 
  name: rabbitmq-publish 
spec: 
  backoffLimit: 4
  template: 
    spec: 
      restartPolicy: Never
      containers: 
      - name: rabbitmq-client 
        image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq-publish:v1.0  
        imagePullPolicy: IfNotPresent 
        command: 
        - "send"
        - "amqp://user:password@rabbitmq.default.svc.cluster.local:5672"
        - "100"
~~~

### 模拟消费者

~~~yaml
apiVersion: apps/v1 
kind: Deployment 
metadata: 
  name: rabbitmq-consumer 
  namespace: default 
  labels: 
    app: rabbitmq-consumer 
spec: 
  selector: 
    matchLabels: 
      app: rabbitmq-consumer 
  template: 
    metadata: 
      labels: 
        app: rabbitmq-consumer 
    spec: 
      containers: 
        - name: rabbitmq-consumer 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/rabbitmq-consumer:v1.0 
          imagePullPolicy: IfNotPresent
          command:
          - receive 
          args: 
          - "amqp://user:password@rabbitmq.default.svc.cluster.local:5672" 
~~~

### 创建认证TriggerAuth

这里用secret保存连接字符串，也可以直接引用RabbitMQ中的用户名密码env

~~~yaml
apiVersion: v1 
kind: Secret 
metadata: 
  name: keda-rabbitmq-secret 
stringData: # stringData比data更好，不进行base64加密。
  host: amqp://user:password@rabbitmq.default.svc.cluster.local:5672 # amqp地址
--- 
apiVersion: keda.sh/v1alpha1 
kind: TriggerAuthentication 
metadata: 
  name: keda-trigger-auth-rabbitmq-conn 
spec: 
  secretTargetRef: 
    - parameter: host 
      name: keda-rabbitmq-secret 
      key: host
~~~

### 创建scaledObject

配置参数参考：[RabbitMQ Queue | KEDA](https://keda.sh/docs/2.17/scalers/rabbitmq-queue/)

~~~yaml
--- 
apiVersion: keda.sh/v1alpha1 
kind: ScaledObject 
metadata: 
  name: rabbitmq-scaledobject 
spec: 
  scaleTargetRef: 
    name: rabbitmq-consumer 
  pollingInterval: 5 # 检查周期，默认5秒。生产环境建议设长一点，毕竟消费者消费消息也需要一定时间
  cooldownPeriod: 30 # 冷却时间，默认300秒。只有当min设置为0个pod的时候，配置的冷却时间才生效。否则都是用300s
  minReplicaCount: 1 
  maxReplicaCount: 5 # 最大副本数 
  triggers: 
  - type: rabbitmq 
    metadata: 
      protocol: amqp # 这是最常用的连接协议
      queueName: hello
      mode: QueueLength # 监听模式，队列长度(QueueLength)或消息速率(MessageRate)。一般用队列长度来做判断
      value: "50" # 消息数或每秒速率 
    authenticationRef: 
      name: keda-trigger-auth-rabbitmq-conn
~~~

## 基于数据库扩缩容

比如有一个工单系统，处理完成的工单会写到数据库，处理失败的工单就不会写到数据库。可以基于数据库里面的数据进行弹性伸缩，当检测到数据不存在的时候触发扩容。

### 模拟数据库实例

~~~sh
kubectl create deployment mysql --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:8.0.20 
kubectl set env deploy mysql MYSQL_ROOT_PASSWORD=password 
kubectl expose deploy mysql --port 3306

# 进入数据库创建测试的表
kubectl exec -ti mysql-6d8bd866d8-q89nj -- bash
mysql -uroot -hmysql -p 
create database dukuan;
use dukuan;
CREATE TABLE orders ( 
id INT AUTO_INCREMENT PRIMARY KEY, 
customer_name VARCHAR(100), 
order_amount DECIMAL(10, 2), 
status ENUM('pending', 'processed') DEFAULT 'pending', 
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);
~~~

### 模拟数据写入程序

~~~sh
kubectl create job insert-orders-job --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:insert
~~~

再次进入数据库查看数据

~~~sh
kubectl exec -ti mysql-6d8bd866d8-7qjx9 -- bash
use dukuan;
select * from orders;
~~~

结果会出现工单状态，有一些pending状态的即为未处理完的工单。需要创建数据处理程序。

### 创建数据处理程序

~~~sh
kubectl create deploy update-orders --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:process
~~~

再次进入数据库查看数据：

~~~sh
kubectl exec -ti mysql-6d8bd866d8-7qjx9 -- bash
use dukuan;
select * from orders;
~~~

工单状态会变成processed表示处理完成。

后面我们创建scaledObject，用SQL语句查询数据库中对应未处理的工单数量，当未处理的工单数量大于指定的值时，触发工单处理的deployment的扩容。

### 创建TriggerAuthentication

~~~yaml
apiVersion: v1 
kind: Secret 
metadata: 
  name: keda-mysql-secret 
stringData: 
  mysql_conn_str: root:password@tcp(mysql.default.svc.cluster.local:3306)/dukuan 
--- 
apiVersion: keda.sh/v1alpha1 
kind: TriggerAuthentication 
metadata: 
  name: keda-trigger-auth-mysql-conn 
spec: 
  secretTargetRef: 
    - parameter: connectionString  
      name: keda-mysql-secret 
      key: mysql_conn_str 
~~~

### 创建scaledObject

~~~yaml
--- 
apiVersion: keda.sh/v1alpha1 
kind: ScaledObject 
metadata: 
  name: mysql-scaledobject 
spec: 
  scaleTargetRef: 
    name: update-orders 
  pollingInterval: 5 # 检查周期，默认5秒  
  cooldownPeriod: 30 # 冷却时间，默认300秒  
  minReplicaCount: 0 
  maxReplicaCount: 5 # 最大副本数 
  triggers: 
  - type: mysql
    metadata: 
      queryValue: "4.4" # 触发扩缩容的平均值 
      query: "SELECT COUNT(*) FROM orders WHERE status='pending'"                    
    authenticationRef: 
      name: keda-trigger-auth-mysql-conn
~~~

再次触发数据插入：

~~~sh
kubectl delete job insert-orders-job
kubectl create job insert-orders-job --image=registry.cn-beijing.aliyuncs.com/dotbalo/mysql:insert
~~~

可以观察到在insert-order-jobs完成后，立刻触发了updat-orders deployment的扩容，数据处理的很快，迅速就低于设定值了。30s之后就缩容到0了。

## scaledJob任务处理

KEDA可以使用ScaledJob实现单次或者临时的任务处理，用来处理一些数据，比如图片、视频等。

### 基于Redis扩缩容

假设有一个需求，需要从Redis队列获取数据，然后进行处理，就可以使用ScaledJob实现。

首先创建一个Redis实例：

~~~sh
helm repo add bitnami https://charts.bitnami.com/bitnami 
helm repo update bitnami
helm upgrade -i redis bitnami/redis \
--set global.imageRegistry=docker.kubeasy.com \
--set global.redis.password=dukuan \
--set architecture=standalone \
--set master.persistence.enabled=false \
--version 20.1.6 
~~~

#### 创建TriggerAuthentication

~~~yaml
apiVersion: v1 
kind: Secret 
metadata: 
  name: redis-so-secret 
type: Opaque 
stringData: 
  redis_username: "" 
  redis_password: "dukuan"
--- 
apiVersion: keda.sh/v1alpha1 
kind: TriggerAuthentication 
metadata: 
  name: redis-so-ta
spec: 
  secretTargetRef: 
  - parameter: username 
    name: redis-so-secret  
    key: redis_username 
  - parameter: password 
    name: redis-so-secret 
    key: redis_password 
~~~

#### 测试写入数据

~~~sh
kubectl exec -ti redis-master-0 -- bash
redis-cli -h redis-master -a dukuan
# 写入队列数据
LPUSH test_list "t1" "t2" "t3"
LRANGE test_list 0 2 
# 读取数据
RPOP test_list
LPOP test_list
~~~

#### 创建scaledJob监听数据

~~~yaml
apiVersion: keda.sh/v1alpha1 
kind: ScaledJob 
metadata: 
  name: redis-queue-scaledjob 
spec: 
  jobTargetRef: 
    parallelism: 1  # 每次只启动一个 Job 实例 
    completions: 1  # 每个 Job 只需要完成一次 
    backoffLimit: 4  # 最大重试次数 
    template: 
      spec: 
        containers: 
        - name: redis-queue-consumer 
          image: registry.cn-beijing.aliyuncs.com/dotbalo/redis:process 
  pollingInterval: 30  # 每 30 秒检查一次队列中的消息数量 
  successfulJobsHistoryLimit: 3  # 保留最近 3 个成功的 Job 
  failedJobsHistoryLimit: 3  # 保留最近 3 个失败的 Job 
  maxReplicaCount: 5  # 最多同时运行 5 个 Job 
  triggers: 
  - type: redis 
    metadata: 
      address: redis-master.default.svc.cluster.local:6379 
      listName: test_list 
      listLength: "5" 
    authenticationRef: 
      name: redis-so-ta
~~~

#### 写入测试数据

~~~sh
LPUSH test_list "t1" "t2" "t3"
LPUSH test_list "t1" "t2" "t3" 
LPUSH test_list "t1" "t2" "t3"
LRANGE test_list 0 8
~~~

查看redis-queue-scaledjob的日志，就可以看到job扩容出新的pod处理数据。

