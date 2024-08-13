# Ubuntu模拟环境准备

## 虚拟机创建

- VMWare中打开master1和node1两个虚拟机，删除快照。
- 登录虚拟机，user：linux，passwd：linux；user：root，passwd：linux。
- ip addr查看本机IP：
  - ckamaster1：10.17.0.62
  - ckanode1：10.17.2.182

## 配置OS

### 修改hostname

~~~sh
hostnamectl set-hostname ckamaster1 && bash
hostnamectl set-hostname ckanode1 && bash
#bash是为了刷新环境变量
~~~

### 修改host文件

~~~sh
vim /etc/hosts
10.17.0.247 ckamaster1
10.17.1.27 ckanode1
~~~

### 更新apt源和安装基础软件包

~~~sh
apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg2
apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg2
~~~

> 如果报错如下：
>
> ![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401081901198.jpg)
>
> 解决方法如下：
>
> ```bash
> sudo rm /var/lib/apt/lists/lock
> sudo rm /var/cache/apt/archives/lock
> sudo rm /var/lib/dpkg/lock*
> sudo dpkg --configure -a
> sudo apt update
> ```
>
> 解决 Ubuntu 或其他基于 Debian 的系统中的 APT 包管理器锁定问题。当你试图同时运行多个包管理器实例（如 apt、apt-get、dpkg）时，可能会出现锁定问题。这些命令的具体含义如下：
>
> - `rm /var/lib/apt/lists/lock`：删除 APT 包列表的锁定文件。这个文件防止多个进程同时更改包列表。
> - `rm /var/cache/apt/archives/lock`：删除 APT 包缓存的锁定文件。这个文件防止多个进程同时更改包缓存。
> - `rm /var/lib/dpkg/lock*`：删除 dpkg 的锁定文件。这个文件防止多个进程同时更改 dpkg 的状态。
> - `dpkg --configure -a`：配置所有未配置的包。如果 dpkg 在配置包时被中断，可以使用此命令完成配置。

### 把下载的key添加到本地trusted数据库

~~~sh
curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
~~~

> 1. `curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg`：这是一个用于下载 Docker 的 GPG 密钥的命令。`curl` 是一个命令行工具，用于从或向服务器传输数据。`-fsSL` 参数的含义是：
>    - `-f` 或 `--fail`：如果 HTTP 状态码大于等于 400，就不显示错误消息。
>    - `-s` 或 `--silent`：静默模式。不输出所有的错误和进度信息。
>    - `-S` 或 `--show-error`：当 `-s` 选项启用，且发生错误时，使 curl 显示错误。
>    - `-L` 或 `--location`：如果服务器报告了一个新的位置，那么这个选项将使 curl 重新定向到新的位置。
> 2. `sudo apt-key add -`：将前一个命令的输出（即 Docker 的 GPG 密钥）添加到 APT 的密钥库中。`-` 表示从标准输入读取 GPG 密钥。

### 设置稳定版仓库

~~~sh
add-apt-repository \
   "deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/ \
  $(lsb_release -cs) \
  stable"
~~~

### 关闭交换分区

~~~sh
#临时关闭
swapoff -a
#永久关闭
vim /etc/fstab
#注释掉swapfile这一行
~~~

### 卸载原来就有的k8s

~~~sh
kubeadm reset
~~~

## 安装docker

~~~sh
apt-get install docker-ce docker-ce-cli containerd.io -y
~~~

### 配置docker驱动

~~~sh
cat <<EOF | tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF
~~~

~~~sh
mkdir -p /etc/systemd/system/docker.service.d
systemctl daemon-reload && systemctl restart docker && systemctl enable --now docker
~~~

## 安装k8s

### 配置k8s源

~~~sh
apt-get update && apt-get install -y apt-transport-https curl

cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb http://mirrors.ustc.edu.cn/kubernetes/apt kubernetes-xenial main
EOF

apt-get update
~~~

> 报错如下：
>
> ![image-20240109072509367](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401090725553.png)
>
> 解决方案：
>
> ```sh
> apt-key adv --recv-keys --keyserver keyserver.ubuntu.com FEEA9169307EA071
> apt-key adv --recv-keys --keyserver keyserver.ubuntu.com B53DC80D13EDEF05
> apt-get update && apt-get install -y apt-transport-https curl
> ```
>
> - 这个命令的作用是从 Ubuntu 的密钥服务器下载并添加 ID 为 `B53DC80D13EDEF05` 的公钥。
> - `apt-key adv`：这是一个用于管理 APT 的密钥的命令，`adv` 是 `--advanced` 的缩写，表示使用 gpg 命令的高级选项。
> - `--recv-keys`：这是一个 gpg 命令的选项，用于从密钥服务器接收密钥。
> - `--keyserver keyserver.ubuntu.com`：这个选项指定了密钥服务器的地址，这里是 Ubuntu 的密钥服务器。

### 安装k8s组件

~~~sh
apt-get install -y kubelet=1.23.1-00 kubeadm=1.23.1-00 kubectl=1.23.1-00
#标记指定软件包为保留（held back），阻止软件自动更新
apt-mark hold kubelet kubeadm kubectl 
~~~

# 初始化集群

## kubeadm初始化k8s集群

~~~bash
kubeadm config print init-defaults > kubeadm.yaml
~~~

~~~yaml
apiVersion: kubeadm.k8s.io/v1beta3
bootstrapTokens:
- groups:
  - system:bootstrappers:kubeadm:default-node-token
  token: abcdef.0123456789abcdef
  ttl: 24h0m0s
  usages:
  - signing
  - authentication
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 10.17.0.247 #控制节点的ip
  bindPort: 6443
nodeRegistration:
  criSocket: /var/run/dockershim.sock
  imagePullPolicy: IfNotPresent
  name: ckamaster1 #控制节点的hostname
  taints: null
---
apiServer:
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta3
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.aliyuncs.com/google_containers #修改默认镜像仓库为阿里云
kind: ClusterConfiguration
kubernetesVersion: 1.23.1 #安装的版本
networking:
  dnsDomain: cluster.local
  serviceSubnet: 10.96.0.0/12 #指定service网段
  podSubnet: 10.244.0.0/16 #增加这一行，指定pod网段， 需要新增加这个
scheduler: {}
---
#新增配置，指定kubeproxy模式为ipvs
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
#新增配置，指定kubelet配置为systemd
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
~~~

~~~sh
kubeadm init --config=kubeadm.yaml --ignore-preflight-errors=SystemVerification
~~~

## 授权kubectl

~~~sh
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

#1. 设置kubectl的alias为k：
whereis kubectl # kubectl: /usr/bin/kubectl
echo "alias k=/usr/bin/kubectl">>/etc/profile
source /etc/profile
#2. 设置alias的自动补全：
source <(kubectl completion bash | sed 's/kubectl/k/g')
#3. 解决每次启动k都会失效，要重新刷新环境变量（source /etc/profile）的问题：在~/.bashrc文件中添加以下代码：source /etc/profile
echo "source /etc/profile" >> ~/.bashrc
#安装了zsh的环境，把上面放到~/.zshrc中
echo "source /etc/profile" >> ~/.zshrc 

#config文件拷贝到两台node上
#node上
mkdir -p $HOME/.kube
#master上
scp $HOME/.kube/config ckanode1:/root/.kube/
~~~

## 扩容节点

~~~sh
kubeadm token create --print-join-command
kubeadm join 10.17.0.247:6443 --token abcdef.0123456789abcdef --discovery-token-ca-cert-hash sha256:08fa4a7ee9316b14db26197e7dafd0e9afdd1668da4d27e290f79b0d185dcaa6 --ignore-preflight-errors=SystemVerification
kubectl label node ckanode1 node-role.kubernetes.io/worker=worker
~~~

# 安装calico

~~~bash
#注：在线下载配置文件地址是： https://docs.projectcalico.org/manifests/calico.yaml
k apply -f calico.yaml    
~~~

~~~sh
#测试网络插件
kubectl run busybox --image busybox:1.28 --restart=Never --rm -it busybox -- sh
ping www.baidu.com
nslookup kubernetes.default.svc.cluster.local
~~~

# 1 RBAC

## 题目

Context：
为部署流水线创建一个新的ClusterRole 并将其绑定到范围为特定的 namespace 的特定ServiceAccount 。

Task

创建一个名为deployment-clusterrole 的clusterrole，该clusterrole 只允许对Deployment 、Daemonset 、Statefulset 具有create 权限。

在现有的 namespace app-team1中创建一个名为cicd-token的新 ServiceAccount。

限于 namespace app-team1中，将新的ClusterRole deployment-clusterrole绑定到新的 ServiceAccount cicd-token。

## 解答

- kubernetes.io文档中搜rbac

~~~sh
#切换集群
kubectl config use-context k8s
#创建ns（考试时ns已经有了不用创建）
kubectl create ns app-team1
#创建clusterrole，文档中搜create clusterrole
kubectl create clusterrole deployment-clusterrole --verb=create --resource=deployments,daemonsets,statefulsets
#创建sa
kubectl create sa cicd-token -n app-team1
#创建rolebinding，文档搜create rolebinding
kubectl create rolebinding -n app-team1 --clusterrole=deployment-clusterrole --serviceaccount=app-team1:cicd-token
#检查
kubectl describe rolebinding cicd-token-binding -n app-team1
~~~

> - 注意资源要变复数
> - sa要带着ns，--serviceaccount=`app-team1`:cicd-token

# 2 node节点不可用

## 题目

将ek8s-node-1节点设置为不可用，然后重新调度该节点上的所有Pod

## 解答

- kubectl drain --help 来看参数

~~~sh
kubectl config use-context ek8s
kubectl get nodes
kubectl cordon ckanode1
kubectl drain ckanode1 --delete-emptydir-data --ignore-daemonsets --force
~~~

# 3 k8s版本升级

## 题目

- 现有的Kubernetes 集群正在运行版本1.23.1。仅将master节点上的所有 Kubernetes控制平面和节点组件升级到版本1.23.2。确保在升级之前 drain master节点，并在升级后 uncordon master节点。
- 可以使用以下命令，通过ssh连接到master节点：ssh master01
- 可以使用以下命令，在该master节点上获取更高权限：sudo -i
- 另外，在主节点上升级kubelet和kubectl。
- 请不要升级工作节点，etcd，container 管理器，CNI插件， DNS服务或任何其他插件。

## 解答

- kubernetes.io搜upgrade

~~~sh
kubectl get nodes
#在node节点上，cordon and drain nodes
kubectl cordon master01
kubectl drain master01 --delete-emptydir-data --ignore-daemonsets --force

#ssh到master01节点
ssh master01
sudo -i
#Determine which version to upgrade to 
apt update
apt-cache madison kubeadm | grep 1.23.2
#Upgrading control plane nodes 
#Call "kubeadm upgrade" 
apt-mark unhold kubeadm && \
apt-get update && apt-get install -y kubeadm='1.23.2-00' && \
apt-mark hold kubeadm
kubeadm version
#Verify the upgrade plan
kubeadm upgrade plan
kubeadm upgrade apply v1.23.2 --etcd-upgrade=false #这里一定记得不需要升级etcd
#upgrade kubelet and kubectl
apt-mark unhold kubelet kubectl && \
apt-get update && apt-get install -y kubelet='1.23.2-00' kubectl='1.23.2-00' && \
apt-mark hold kubelet kubectl
#restart the kubelet
systemctl daemon-reload
systemctl restart kubelet
#退出root
exit
#退出master01
exit
#uncordon master01
kubectl uncordon master01
kubectl get nodes 
~~~

# 4 etcd备份还原

## 题目

> （真实考试时，第3题是“升级集群”那道题。建议真正考试时，前4道题按照顺序做，特别是第4题，且做完后不要再修改，做完第3道题，如果没有exit退出到student@node-1，则无法执行etcdctl命令，另外这道题没有切换集群，用的是第3道题的集群，所以，这道题做完就不要在回来检查或者操作了，etcd不建议放到最后做，如果最后做，etcd备份还原可能把所有pod都清空了，有可能会出现，所以前4道题按照顺序做）

- 首先，为运行在https://27.0.0.1:2379 上的现有 etcd 实例创建快照并将快照保存到 /srv/data/etcd-snapshot.db 文件。为给定实例创建快照预计能在几秒钟内完成。 如果该操作似乎挂起，则命令可能有问题。用 CTRL + C 来取消操作，然后重试。
- 然后还原位于/var/lib/backup/etcd-snapshot-previous.db的现有先前快照。提供了以下TLS证书和密钥，以通过etcdctl连接到服务器。
- CA 证书: /opt/KUIN00601/ca.crt
  客户端证书: /opt/KUIN00601/etcd-client.crt
  客户端密钥: /opt/KUIN00601/etcd-client.key

## 解答

> 自己的环境先安装etcdctl：上传etcd-v3.4.13-linux-amd64.tar.gz
>
> ~~~sh
> tar zxvf etcd-v3.4.13-linux-amd64.tar.gz
> cp etcd-v3.4.13-linux-amd64/etcdctl /usr/bin/
> ~~~

- kubernetes.io搜etcd restore, ctrl+F搜snapshot

~~~sh
#首先确保退回到了student@node-1的终端，才能继续用etcdctl，官网命令如下：
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=<trusted-ca-file> --cert=<cert-file> --key=<key-file> \
  snapshot save <backup-file-location>

#自己环境命令：
mkdir -p /srv/data/
##备份
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379  --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /srv/data/etcd-snapshot.db
##还原
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
--cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot restore /srv/data/etcd-snapshot.db

#考试环境命令
##备份
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379  --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/server.crt --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /srv/data/etcd-snapshot.db
##还原
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
--cacert=/opt/KUIN00601/ca.crt --cert=/opt/KUIN00601/etcd-client.crt --key=/opt/KUIN00601/etcd-client.key \
  snapshot restore /var/lib/backup/etcd-snapshot-previous.db
~~~

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

重新配置一个已经存在的front-end的deployment，在名字为nginx 的容器里面添加一个端口配置，名字为http，暴露端口号为80，然后创建一个service，名字为front-end-svc，暴露该deployment
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
    - port: 80
      targetPort: http #targetPort可以写containerport的名字
~~~

# 7 Ingress七层代理

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
#官网搜ingress，在文档内搜default ingressClass，拿到示例ingressclass的yaml文件
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  labels:
    app.kubernetes.io/component: controller
  name: nginx-example
  namespace: ing-internal #补一个ns
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
  ingressClassName: nginx-example
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
  nodeSelector:
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
kubectl get nodes | grep -w "Ready" | wc -l
#再把出来的node名称放到下面去describe
kubectl describe nodes ckanode1 | grep -i Taint | grep -v NoSchedule | wc -l
#记录总数为x
echo x > /opt/KUSC00402/kusc00402.txt
~~~

> `-i` 参数使搜索变为不区分大小写。这个命令的目的是从 kubectl 的输出中找出包含 "Taint" 的行。
>
> `-v` 参数让 grep 只输出不匹配的行，`-c` 参数让 grep 输出匹配的行数。这个命令的目的是计数不包含 "NoSchedule" 的行

# 11 pod封装多个容器

## 题目

创建一个Pod，名字为kucc1，这个Pod 包含4容器，为nginx 、redis 、memcached 、consul

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
kubectl logs foobar | grep unable-access-website > /opt/KUTR00101/foobar
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

