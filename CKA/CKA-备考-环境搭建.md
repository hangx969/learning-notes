# Ubuntu模拟环境准备

## 虚拟机创建

- VMWare中打开master1和node1两个虚拟机，删除快照。
- 登录虚拟机，user：linux，passwd：linux；user：root，passwd：linux。
- ip addr查看本机IP：
  - ckamaster1：10.17.0.247
  - ckanode1：10.17.1.27

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
> ![img](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401081935367.jpg)
>
> 解决方案：
>
> ```sh
> apt-key adv --recv-keys --keyserver keyserver.ubuntu.com FEEA9169307EA071
> apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 8B57C5C2836F4BEB
> apt-get update && apt-get install -y apt-transport-https curl
> ```

### 安装k8s组件

~~~sh
apt-get install -y kubelet=1.23.1-00 kubeadm=1.23.1-00 kubectl=1.23.1-00
#标记指定软件包为保留（held back），阻止软件自动更新
apt-mark hold kubelet kubeadm kubectl 
~~~

