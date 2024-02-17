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

