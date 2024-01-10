# 1 RBAC

## 题目

Context：
为部署流水线创建一个新的ClusterRole 并将其绑定到范围为特定的 namespace 的特定ServiceAccount 。

Task

创建一个名为deployment-clusterrole 的clusterrole，该clusterrole 只允许对Deployment 、Daemonset 、Statefulset 具有create 权限。

在现有的 namespace app-team1中创建一个名为cicd-token的新 ServiceAccount。

限于 namespace app-team1中，将新的ClusterRole deployment-clusterrole绑定到新的 ServiceAccount cicd-token。

## 解答



# 2 node节点不可用

## 题目

将ek8s-node-1 节点设置为不可用，然后重新调度该节点上的所有Pod

## 解答



# 3 k8s版本升级

## 题目

- 现有的Kubernetes 集群正在运行版本1.23.1。仅将master节点上的所有 Kubernetes控制平面和节点组件升级到版本1.23.2。确保在升级之前 drain master节点，并在升级后 uncordon master节点。
- 可以使用以下命令，通过ssh连接到master节点：ssh master01
- 可以使用以下命令，在该master节点上获取更高权限：sudo -i
- 另外，在主节点上升级kubelet和kubectl。
- 请不要升级工作节点，etcd，container 管理器，CNI插件， DNS服务或任何其他插件。

## 解答

# 4 etcd备份还原

## 题目

- 首先，为运行在https://27.0.0.1:2379 上的现有 etcd 实例创建快照并将快照保存到 /srv/data/etcd-snapshot.db 文件。为给定实例创建快照预计能在几秒钟内完成。 如果该操作似乎挂起，则命令可能有问题。用 CTRL + C 来取消操作，然后重试。
- 然后还原位于/var/lib/backup/etcd-snapshot-previous.db的现有先前快照。提供了以下TLS证书和密钥，以通过etcdctl连接到服务器。
- CA 证书: /opt/KUIN00601/ca.crt
  客户端证书: /opt/KUIN00601/etcd-client.crt
  客户端密钥: /opt/KUIN00601/etcd-client.key

## 解答

# 5 networkpolicy

## 题目

- 在现有的namespace my-app中创建一个名为allow-port-from-namespace的新NetworkPolicy。

- 确保新的NetworkPolicy允许namespace echo中的Pods连接到namespace my-app中的Pods的9000端口。

- 进一步确保新的NetworkPolicy：
  - 不允许对没有在监听端口9000的Pods的访问
  - 不允许非来自 namespace echo中的Pods的访问

## 答案

- kubernetes.io中搜network policies

> #注意vim中 :set paste，防止yaml文件空格错序。

~~~sh
#自己环境
kubectl create ns my-app
kubectl create ns echo
#查看ns的标签
kubectl get ns --show-labels
#如果ns没有独特的标签，自己打一个，方便yaml文件里面标识这个源ns echo
kubectl label ns echo project=echo
#官网上复制示例yaml，vim一下做修改:set paste
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-port-from-namespace
  namespace: my-app
spec:
  podSelector:
    matchLabels: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              project: echo
      ports:
        - protocol: TCP
          port: 9000
~~~

~~~sh
kubectl apply -f np.yaml
~~~

# 6 四层负载均衡svc

## 题目

重新配置一个已经存在的front-end的deployment，在名字为nginx 的容器里面添加一个端口配置，名字为http，暴露端口号为80，然后创建一个serviceservice，名字为front-end-svc，暴露该deployment
的http 端口，并且service 的类型为Node Port 。

## 解答

- 官网搜service

~~~sh
kubectl edit deploy front-end
~~~

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: front-end
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      Label:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        imagePullPolicy: IfNotPresent
        #加入下面的端口配置
        ports:
        - name: http
          containerPort: 80
~~~

- 官网搜service，搜nodePort，把示例yaml拿过来改一下

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: front-end-svc
spec:
  type: NodePort
  selector:
    app: nginx
  ports:
    - port: 80 #题目没规定svc的端口是多少，就还用跟containerport一样的80就行
      targetPort: http #targetPort可以写containerport的名字
~~~

# 7 Ingress七层代理

> 规定了ns的题目，创建资源的时候记得yaml文件里面加上ns

## 题目

如下创建一个新的nginx Ingress资源：

- 名称: pong

- Namespace: ing-internal

- 使用服务端口 5678在路径 /hello 上公开服务 hello

- 可以使用以下命令检查服务 hello的可用性，该命令应返回 hello：

  curl -kL <INTERNAL_IP>/hello

## 解答

- 官网搜ingress，拿到示例ingress的yaml

~~~sh
kubectl create ns ing-internal
~~~

- #先创建一个ingressClass

~~~yaml
#官网搜ingress，在文档内搜default ingressClass吗，拿到示例ingressclass的yaml文件
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  labels:
    app.kubernetes.io/component: controller
  name: nginx-example
  namespace: ing-internal #补一个ns，这里容易忘记
  annotations:
    ingressclass.kubernetes.io/is-default-class: "true"
spec:
  controller: k8s.io/ingress-nginx
~~~

- 创建ingress

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pong
  namespace: ing-internal
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx #ingressClassName一般写nginx就行
  rules:
  - http:
      paths:
      - path: /hello
        pathType: Prefix
        backend:
          service:
            name: hello
            port:
              number: 5678
~~~

# 8 deployment实现pod扩缩容

## 题目

将loadbalancer 的deployment 管理的Pod 的副本数扩容成6 个

## 解答

~~~yaml
kubectl edit deployment loadbalancer
#把replica改成6
~~~

# 9 pod指定节点部署

## 题目

创建一个Pod，名字为nginx-kusc00401，镜像地址是nginx，调度到具有disk=spinning 标签的节点上

## 解答

- 官网搜pod，拿示例yaml，镜像改成nginx，加一个nodeSelector指定标签

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-kusc00401
spec:
  nodeSelector: #注意nodeselector这里不需要写matchlabels
    disk: spinning #注意labels的写法，yaml文件里面是map[string][string]，是冒号空格的形式
  containers:
  - name: nginx
    image: nginx
~~~

# 10 检查Ready节点数量

## 题目

检查集群中有多少节点为Ready 状态（不包括被打上 `Taint：NoSchedule` 的节点），之后将数量写到 /opt/KUSC00402/kusc00402.txt

## 解答

~~~sh
#先找Ready的nodes
kubectl get nodes | grep -w "Ready"
#再把出来的node名称放到下面去describe
kubectl describe nodes ckanode1 | grep -i Taint | grep -vc NoSchedule
#记录总数为x
echo x > /opt/KUSC00402/kusc00402.txt
~~~

> `-i` 参数使搜索变为不区分大小写。这个命令的目的是从 kubectl 的输出中找出包含 "Taint" 的行。
>
> `-v` 参数让 grep 只输出不匹配的行，`-c` 参数让 grep 输出匹配的行数。这个命令的目的是计数不包含 "NoSchedule" 的行

# 11 pod封装多个容器

## 题目

创建一个PodPod，名字为kucc1，这个Pod 包含4容器，为nginx 、redis 、memcached 、consul

## 解答

- 官网拿pod示例yaml

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: kucc1
spec:
  containers:
  - name: nginx
    image: nginx
  - name: redis
    image: redis
  - name: memcached
    image: memcached
  - name: consul
    image: consul
~~~

~~~sh
kubectl apply -f pod.yaml
~~~

# 12 创建pv

## 题目

创建一个pv，名字为app-config，大小为2Gi，访问权限为ReadWriteMany。Volume 的类型为hostPath，路径为 /srv/app-config

## 解答

- 官网搜PersistentVolume，文档中搜hostPath，找到链接See an example of `hostPath` typed volume，拿到示例yaml

~~~yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: app-config #这里改一下
spec:
  capacity:
    storage: 2Gi #这里改一下
  accessModes:
    - ReadWriteMany #这里改一下
  hostPath:
    path: "/srv/app-config" #加上目录
~~~

# 13 创建pvc

## 题目

创建一个名字为pv-volume 的pvc，指定storage Class 为csi-hostpath-sc，大小为10Mi

然后创建一个Pod，名字为web-server，镜像为nginx，并且挂载该PVC 至/usr/share/nginx/html，挂载的权限为ReadWriteOnce。之后通过kubectl edit或者kubectl patch将pvc改成70Mi，并且`记录修改记录`。

## 解答

- 官网搜pvc，进到PV的文档里面，搜kind: PersistentVolumeClaim，拿到示例yaml

~~~yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pv-volume
spec:
  resources:
    requests:
      storage: 10Mi
  storageClassName: csi-hostpath-sc
  accessModes: #在这里指定挂载权限
    - ReadWriteOnce
~~~

- 还是在pv的页面，搜king: pod，拿到pod的示例yaml

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server
spec:
  containers:
    - name: nginx
      image: nginx
      volumeMounts:
      - mountPath: "/usr/share/nginx/html"
        name: pv-volume
  volumes:
    - name: pv-volume
      persistentVolumeClaim:
        claimName: pv-volume
~~~

- 修改并记录

  ~~~sh
  kubectl edit pvc pv-volume --record
  ~~~

  # 14 查看pod日志

## 题目

监控名为foobar 的Pod 的日志，并过滤出具有unable-access-website 信息的行，然后将写入到 /opt/KUTR00101/foobar

## 解答

~~~sh
kubectl logs foobar | grep unable-access-website > /opt/KUTR00101/foobar #写入的命令可以直接在grep后面加>
~~~

# 15 side-car代理

## 题目

- 将一个现有的 Pod 集成到 Kubernetes 的内置日志记录体系结构中（例如 kubectl logs）。
  添加 streaming sidecar 容器是实现此要求的一种好方法。
- 使用busybox Image 来将名为sidecar 的sidecar 容器添加到现有的Pod legacy-app 上，新的sidecar 容器必须运行以下命令：
  /bin/sh -c tail -n+1 -f /var/log/legacy-app.log
  使用volume 挂载 /var/log/ 目录，确保sidecar 能访问/var/log/legacy-app.log 文件

## 解答

- 官网搜logging，拿一个sidecar的示例pod来参考，直接修改给定的pod yaml

~~~sh
kubectl get po count -o yaml > sidecar.yaml
~~~

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: counter
spec:
  containers:
  - name: legacy-app
    image: busybox:1.28
    args:
    - /bin/sh
    - -c
    - >
      i=0;
      while true;
      do
        echo "$i: $(date)" >> /var/log/legacy-app.log;
        echo "$(date) INFO $i" >> /var/log/legacy-app.log;
        i=$((i+1));
        sleep 1;
      done      
    volumeMounts: #考试的时候原来容器的挂载信息是没有的，自己加上
    - name: varlog
      mountPath: /var/log
  - name: sidecar #从这里修改sidecar的容器信息
    image: busybox #改image
    args: ['/bin/sh', '-c', 'tail -n+1 -F /var/log/legacy-app.log'] #加命令。命令去看的log文件要和原容器的log文件一样
    volumeMounts: #加一个卷挂载
    - name: varlog
      mountPath: /var/log
  volumes: #考试时如果这里没有的话，自己加一下
  - name: varlog
    emptyDir: {}
~~~

~~~sh
#改好之后，强制删除现有pod，重新创建新pod
kubectl delete po legacy-app --force --grace-period=0
kubectl apply -f sidecar.yaml
kubectl logs counter -c sidecar
~~~

# 16 查看pod的CPU使用

> 这里 -A 指定所有pod 容易被忽略

## 题目

找出标签是name=cpu-user 的Pod，并过滤出使用CPU最高的Pod，然后把它的名字写在已经存在的/opt/KUTR00401/KUTR00401.txt 文件里（注意他没有说指定namespace。所以需要使用 -A）

## 解答

~~~sh
kubectl top pod -A -l name=cpu-user --sort-by=cpu
echo "pod name" > /opt/KUTR00401/KUTR00401.txt
~~~

> 用kubectl top前提是有metrics-server这个组件，可以部署一下：
>
> 上传课件两个文件：
>
> - addon.tar.gz
>
> - metrics-server-amd64-0-3-6.tar.gz
> - metrics.yaml
>
> ~~~sh
> #ckanode1上
> docker load -i metrics-server-amd64-0-3-6.tar.gz
> docker load -i addon.tar.gz
> kubectl apply -f metrics.yaml
> ~~~

# 17 节点故障排查

## 题目

Task
一个名为wk8s-node-0 的节点状态为NotReady，让其他恢复至正常状态，并确认所有的更改开机自动完成。
可以使用以下命令，通过ssh连接到wk8s-node-0 节点：
ssh wk8s-node-0
可以使用以下命令，在该节点上获取更高权限：
sudo -i

## 解答

~~~sh
ssh wk8s-node-0
sudo -i
systemctl status kubelet
systemctl restart kubelet
systemctl enable kubelet
~~~

