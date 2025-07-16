# ReplicaSet - rs

## 示例

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: rs-ft
  namespace: default
  labels:
    app: guestbook
    tier: frontend
spec:
  replicas: 3
  selector: # 在.spec.selector中定义的标签选择器必须能够匹配到spec.template.metadata.labels里定义的Pod标签
    matchLabels:
      tier1: frontend1
  template:
    metadata:
      labels:
        tier1: frontend1
    spec:
      containers:
      - name: samples-gb-frontend
        image: docker.io/yecc/gcr.io-google_samples-gb-frontend:v3
        imagePullPolicy: IfNotPresent
        ports: 
        - containerPort: 80
        startupProbe:
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 10
          httpGet:
            scheme: HTTP
            port: 80
            path: /
        livenessProbe:
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 10
          httpGet:
            scheme: HTTP
            port: 80
            path: /
        readinessProbe:
          initialDelaySeconds: 20
          periodSeconds: 5
          timeoutSeconds: 10
          httpGet:
            scheme: HTTP
            port: 80
            path: /
```

## 缺点

- 更新管理上不如deployment灵活。

# deployment

## 概述

- Deployment是kubernetes中最常用的资源对象，为ReplicaSet和Pod的创建提供了一种声明式的定义方法，在Deployment对象中描述一个期望的状态，Deployment控制器就会按照一定的控制速率把实际状态改成期望状态，通过定义一个Deployment控制器会创建一个新的ReplicaSet控制器。
- 使用Deployment而不直接创建ReplicaSet是因为Deployment对象拥有许多ReplicaSet没有的特性，例如滚动升级、金丝雀发布、蓝绿部署和回滚。

## 工作原理

### RS管理

- Deployment控制器是建立在rs之上的一个控制器，可以管理多个rs，每次更新镜像版本，都会生成一个新的rs，把旧的rs替换掉，多个rs同时存在，但是只有一个rs运行。
- 如下图：rs v1控制三个pod，删除一个pod，在rs v2上重新建立一个，依次类推，直到全部都是由rs v2控制，如果rs v2有问题，还可以回滚，Deployment是建构在rs之上的，多个rs组成一个Deployment，但是只有一个rs处于活跃状态.

![image-20231029220956699](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310292209817.png)

### 更新管理

- 比如说Deployment控制5个pod副本，pod的期望值是5个，但是升级的时候需要额外多几个pod，控制器可以控制在5个pod副本之外还能再增加几个pod副本：
  - 比方说能多一个，但是不能少，那么升级的时候就是先增加一个，再删除一个，始终保持pod副本数是5个
  - 比如最多允许多一个，最少允许少一个；也就是最多6个，最少4个；加一个，删除两个，依次类推。
- 可以自己控制更新方式，这种滚动更新需要加readinessProbe和livenessProbe探测，确保pod中容器里的应用都正常启动了才删除之前的pod。

- 更新策略定义：

  ```bash
  kubectl explain deploy.spec.strategy.rollingUpdate
  
     maxSurge	<string>
  #我们更新的过程当中最多允许超出的指定的目标副本数有几个。
  #它有两种取值方式，第一种直接给定数量；第二种根据百分比，如最多可以超出20%，滚动更新开始时，马上scale up pod数为120%。然后逐渐的kill旧的，创建新的。
  #Absolute number is calculated from percentage by rounding up. ==> 出现小数向上取整
     maxUnavailable	<string>
  #最多允许几个不可用，数字或百分比。如果是30%，滚动更新开始，旧pod马上scale down到70%，然后随着新pod ready，旧pod再进一步scale down。
  #Absolute number is calculated from percentage by rounding down. ==> 出现小数向下取整
  
  replicas： 5
  maxSurge: 25%         5*25%=1.25  ->5+2=7
  maxUnavailable: 25%    5%25%=1.25  -> 5-1=4 #滚动更新时最少4个，最多7个
  ```


## yaml示例

- 用kubectl explain一层一层的查下去慢慢写完yaml文件

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-myapp-blue
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
      version: v1
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      containers:
      - name: myapp
        image: janakiramm/myapp:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        startupProbe:
           periodSeconds: 5
           initialDelaySeconds: 20
           timeoutSeconds: 10
           httpGet:
             scheme: HTTP
             port: 80
             path: /
        livenessProbe:
           periodSeconds: 5
           initialDelaySeconds: 20
           timeoutSeconds: 10
           httpGet:
             scheme: HTTP
             port: 80
             path: /
        readinessProbe:
           periodSeconds: 5
           initialDelaySeconds: 20
           timeoutSeconds: 10
           httpGet:
             scheme: HTTP
             port: 80
             path: /
```

## 重启deployment

`kubectl rollout restart deploy nginx`:会轮替重启deployment里面的pod

## 扩缩容

- 修改yaml文件replicas的值，重新kubectl apply -f即可

## 滚动更新

> 滚动更新是一种自动化程度较高的发布方式，用户体验比较平滑，是目前成熟型技术组织所采用的主流发布方式，一次滚动发布一般由若干个发布批次组成，每批的数量一般是可以配置的（可以通过发布模板定义），例如第一批1台，第二批10%，第三批50%，第四批100%。每个批次之间留观察间隔，通过手工验证或监控反馈确保没有问题再发下一批次，所以总体上滚动式发布过程是比较缓慢的

### yaml定义

```bash
#查看rolling update的参数定义
kubectl explain deploy.spec.strategy
  #type：指定策略类型，支持两种策略
    #Recreate：在创建出新的Pod之前会先杀掉所有已存在的Pod
    #RollingUpdate：滚动更新，就是杀死一部分，就启动一部分，在更新过程中，存在两个版本Pod。（默认值）
  #rollingUpdate：当type为RollingUpdate时生效，用于为RollingUpdate设置参数，支持两个属性：
    #maxUnavailable：用来指定在升级过程中不可用Pod的最大数量，默认为25%。
    #maxSurge： 用来指定在升级过程中可以超过期望的Pod的最大数量，默认为25%。
    
#查看当前deploy的rolling update策略
kubectl describe deploy
```

### 查看滚动更新历史版本

- kubectl rollout： 版本升级相关功能，支持下面的选项：

  -   status 显示当前升级状态

  -   history 显示 升级历史记录

  -   pause 暂停版本升级过程

  -   resume 继续已经暂停的版本升级过程

  -   restart 重启版本升级过程

  -   undo 回滚到上一级版本（可以使用--to-revision回滚到指定版本）
    - --to-version：指的是rollout history里面显示的VERSION版本

```bash
kubectl rollout history deploy dep-myapp-blue 

deployment.apps/dep-myapp-blue 
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

kubectl get rs #能看到两个rs，有一个旧版本的rs都是0.
```

### 回滚到历史版本

```bash
kubectl rollout undo deploy dep-myapp-blue --to-revision=1 
#也是滚动的方式，ready一个新的干掉一个旧的。
```

### 自定义更新策略

maxSurge和maxUnavailable用来控制滚动更新的更新策略:

1. maxUnavailable: [0, 副本数]

2. maxSurge: [0, 副本数]

注意：两者不能同时为0。

比例:

1. maxUnavailable: [0%, 100%] 向下取整，比如10个副本，5%的话==0.5个，但计算按照0个；

2. maxSurge: [0%, 100%] 向上取整，比如10个副本，5%的话==0.5个，但计算按照1个；

注意：两者不能同时为0。

建议配置:

1. maxUnavailable == 0

2. maxSurge == 1

这是我们生产环境提供给用户的默认配置。即“一上一下，先上后下”最平滑原则：1个新版本pod ready（结合readiness）后，才销毁旧版本pod。此配置适用场景是平滑更新、保证服务平稳，但也有缺点，就是“太慢”了。

总结：

- maxUnavailable：和期望的副本数比，不可用副本数最大比例（或最大值），这个值越小，越能保证服务稳定，更新越平滑；


- maxSurge：和期望的副本数比，超过期望副本数最大比例（或最大值），这个值调的越大，副本更新速度越快。

修改deployment的更新策略:

```bash
#通过kubectl patch改
kubectl patch deployment myapp-v1 -p '{"spec":{"strategy":{"rollingUpdate": {"maxSurge":1,"maxUnavailable":0}}}}'
```

```bash
#通过yaml文件改
kubectl explain deploy.spec.strategy
#yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-myapp-blue
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: myapp
      version: v1
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      containers:
      - name: myapp
        image: janakiramm/myapp:v2
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
        ...
```

## 蓝绿部署

### 原理

- 蓝绿部署中，一共有两套系统：一套是正在提供服务系统，标记为“绿色”；另一套是准备发布的系统，标记为“蓝色”。两套系统都是功能完善的、正在运行的系统，只是系统版本和对外服务情况不同。

- 开发新版本，要用新版本替换线上的旧版本，在线上的系统之外，搭建了一个使用新版本代码的全新系统。 这时候，一共有两套系统在运行，正在对外提供服务的老系统是绿色系统，新部署的系统是蓝色系统。

![image-20231111095318581](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311110953730.png)

- 蓝色系统不对外提供服务，用来做发布前测试，测试过程中发现任何问题，可以直接在蓝色系统上修改，不干扰用户正在使用的系统。（注意，两套系统没有耦合的时候才能百分百保证不干扰）蓝色系统经过反复的测试、修改、验证，确定达到上线标准之后，直接将用户切换到蓝色系统：

  ![image-20231111095615746](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311110956844.png)

- 切换后的一段时间内，依旧是蓝绿两套系统并存，但是用户访问的已经是蓝色系统。这段时间内观察蓝色系统（新系统）工作状态，如果出现问题，直接切换回绿色系统。

- 当确信对外提供服务的蓝色系统工作正常，不对外提供服务的绿色系统已经不再需要的时候，蓝色系统正式成为对外提供服务系统，成为新的绿色系统。 原先的绿色系统可以销毁，将资源释放出来，用于部署下一个蓝色系统。

### 优缺点

优点：

1、更新过程无需停机，风险较少

2、回滚方便，只需要更改路由或者切换DNS服务器，效率较高

缺点：

1、成本较高，需要部署两套环境。如果新版本中基础服务出现问题，会瞬间影响全网用户；如果新版本有问题也会影响全网用户。

2、需要部署两套机器，费用开销大

3、在非隔离的机器（Docker、VM）上操作时，可能会导致蓝绿环境被摧毁风险

4、负载均衡器/反向代理/路由/DNS处理不当，将导致流量没有切换过来情况出现

### 实现

K8S本身不支持原生的蓝绿部署，目前最好方法是：部署deployment，更新应用程序的service以指向新的deployment部署的应用

- 部署green应用

```yaml
#部署deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-v1
  namespace: blue-green
spec:
  replicas: 3
  selector:
   matchLabels:
    app: myapp
    version: v2
  template:
   metadata:
    labels:
     app: myapp
     version: v2
   spec:
    containers:
    - name: myapp
      image: janakiramm/myapp:v2
      imagePullPolicy: IfNotPresent
      ports:
      - containerPort: 80
```

```bash
kubectl create ns blue-green
ctr -n=k8s.io images import myapp-blue.tar.gz
ctr -n=k8s.io images import myapp-green.tar.gz
```

```yaml
#创建前端service
apiVersion: v1
kind: Service
metadata:
  name: myapp-lan-lv
  namespace: blue-green
  labels:
    app: myapp
spec:
  type: NodePort
  ports:
  - port: 80
    nodePort: 30062
    name: http
  selector:
    app: myapp
    version: v2
```

- 部署blue应用

  ```yaml
  #创建deployment
  apiVersion: apps/v1
  kind: Deployment
  metadata:
    name: myapp-v2
    namespace: blue-green
  spec:
    replicas: 3
    selector:
     matchLabels:
      app: myapp
      version: v1
    template:
     metadata:
      labels:
       app: myapp
       version: v1
     spec:
      containers:
      - name: myapp
        image: janakiramm/myapp:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
  ```

- 修改svc yaml文件，使其标签选择器指向blue应用

## 金丝雀发布

> - 金丝雀发布的由来：17 世纪，英国矿井工人发现，金丝雀对瓦斯这种气体十分敏感。空气中哪怕有极其微量的瓦斯，金丝雀也会停止歌唱；当瓦斯含量超过一定限度时，虽然人类毫无察觉，金丝雀却早已毒发身亡。当时在采矿设备相对简陋的条件下，工人们每次下井都会带上一只金丝雀作为瓦斯检测指标，以便在危险状况下紧急撤离。
>
> - 金丝雀发布（又称灰度发布、灰度更新）：金丝雀发布一般先发1台，或者一个小比例，例如2%的服务器，主要做流量验证用，也称为金丝雀 (Canary) 测试 （国内常称灰度测试）。
> - 简单的金丝雀测试一般通过手工测试验证，复杂的金丝雀测试需要比较完善的监控基础设施配合，通过监控指标反馈，观察金丝雀的健康状况，作为后续发布或回退的依据。 如果金丝测试通过，则把剩余的V1版本全部升级为V2版本。如果金丝雀测试失败，则直接回退金丝雀，发布失败。

![image-20231111103236653](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202311111032729.png)

### 实现

```yaml
#创建deployment
kubectl apply -f dep-green.yaml
#更新镜像，同时暂停rollout
kubectl set image deployment myapp-v1 myapp=nginx:latest  -n blue-green && kubectl rollout pause deployment myapp-v1 -n blue-green
#注：上面的解释说明把myapp这个容器的镜像更新到nginx:latest版本 更新镜像之后，创建一个新的pod就立即暂停，这就是我们说的金丝雀发布；如果暂停几个小时之后没有问题，那么取消暂停，就会依次执行后面步骤，把所有pod都升级。
#取消暂停，让deployment执行完滚动更新
kubectl rollout resume deployment myapp-v1 -n blue-green
```

> 金丝雀发布功能，用istio实现，更加方便
