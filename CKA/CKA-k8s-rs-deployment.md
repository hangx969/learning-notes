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
apiversion: apps/v1
kind: deployment
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
      label:
        app: myapp
        version: v1
    spec:
      containers:
      - name: myapp
        images: janakiramm/myapp:v1
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

## 扩缩容

- 修改yaml文件replicas的值，重新kubectl apply -f即可

## 滚动更新

> 滚动更新是一种自动化程度较高的发布方式，用户体验比较平滑，是目前成熟型技术组织所采用的主流发布方式，一次滚动发布一般由若干个发布批次组成，每批的数量一般是可以配置的（可以通过发布模板定义），例如第一批1台，第二批10%，第三批50%，第四批100%。每个批次之间留观察间隔，通过手工验证或监控反馈确保没有问题再发下一批次，所以总体上滚动式发布过程是比较缓慢的

### yaml定义

```bash
#查看rolling update的参数定义
kubectl explain deploy.spec.strategy
kubectl explain deploy.spec.strategy.rollingUpdate
#查看当前deploy的rolling update
kubectl describe deploy
```

### 查看滚动更新历史版本

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

