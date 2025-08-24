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
helm pull kedacore/keda --version 2.17.
~~~

## 安装

~~~sh
helm install keda -n keda --create-namespace -f values.yaml .
~~~

