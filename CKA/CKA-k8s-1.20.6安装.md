# K8s架构与核心组件

## K8S核心组件介绍

![image-20231017210542411](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310172105530.png)

### master组件

- API server 
  - 集群对外的统一入口，以RESTful API方式做操作。

- scheduler
  - 通过算法算出pod调度到哪个节点

- controller manager
  - 管理一系列的controller（deployment、stateful set、namespace等）

- etcd
  - 存储系统
- Calico：网络插件（给pod提供IP、提供网络policy等）
- kubeproxy 

### Worker Node组件

- kubelet
- kubeproxy
- coredns
- calico
- runtime（docker/containerd）



# kubeadm安装多master集群 

> kubedam和二进制安装k8s
>
> - kubeadm是官方提供的开源工具，是一个开源项目，用于快速搭建kubernetes集群，目前是比较方便和推荐使用的。kubeadm init 以及 kubeadm join 这两个命令可以快速创建 kubernetes 集群。Kubeadm初始化k8s，所有的组件都是以pod形式运行的，具备故障自恢复能力。kubeadm适合需要经常部署k8s，或者对自动化要求比较高的场景下使用。
>
> - 二进制：在官网下载相关组件的二进制包，如果手动安装，对kubernetes理解也会更全面。
>
> - Kubeadm和二进制都适合生产环境，在生产环境运行都很稳定，具体如何选择，可以根据实际项目进行评估。

## 安装准备步骤

- 修改机器IP，变成静态IP （云主机无需配置这个）

```bash
vim /etc/sysconfig/network-scripts/ifcfg-ens33
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static #static表示静态ip地址
IPADDR=192.168.40.180 #ip地址，需要跟自己电脑所在网段一致
NETMASK=255.255.255.0  #子网掩码，需要跟自己电脑所在网段一致
GATEWAY=192.168.40.2 #网关，在自己电脑打开cmd，输入ipconfig /all可看到
DNS1=192.168.40.2 #DNS，在自己电脑打开cmd，输入ipconfig /all可看到 
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=ens33 #网卡名字，跟DEVICE名字保持一致即可
DEVICE=ens33 #网卡设备名，大家ip addr可看到自己的这个网卡设备名，每个人的机器可能这个名字不一样，需要写自己的
ONBOOT=yes #开机自启动网络，必须是yes

#修改配置文件之后需要重启网络服务才能使配置生效，重启网络服务命令如下：
service network restart
```

- 关闭selinux

```bash
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config #修改selinux配置文件之后，重启机器，selinux配置才能永久生效
reboot -f
getenforce #显示Disabled说明selinux已经关闭
```

- 修改hostname

  ```bash
  hostnamectl set-hostname master1 && bash
  ```

- 升级系统，7.6 - 7.9

  ```bash
  yum update -y
  cat /etc/redhat-release
  #CentOS Linux release 7.9.2009 (Core)
  ```

- 关闭交换分区

  ```bash
  #临时关闭
  swapoff -a
  #永久关闭：注释掉fatab的swap挂载
  vim /etc/fstab
  #/dev/mapper/centos-swap swap      swap    defaults        0 0
  ```

  > - Swap是交换分区，如果机器内存不够，会使用swap分区，但是swap分区的性能较低，k8s设计的时候为了能提升性能，默认是不允许使用交换分区的。
  > - Kubeadm初始化的时候会检测swap是否关闭，如果没关闭，那就初始化失败。如果不想要关闭交换分区，安装k8s的时候可以指定--ignore-preflight-errors=Swap来解决。

- 修改内核参数，开路由转发

  ```bash
  modprobe br_netfilter 
  # 加载br_netfilter模块可以使 iptables 规则可以在 Linux Bridges 上面工作，用于将桥接的流量转发至iptables链，k8s如果没有加载br_netfilter模块，会影响同node内的pod之间通过service来通信。
  # 加载这个模块是为了可以正常开启iptables和ip6tables参数
  
  echo "modprobe br_netfilter" >> /etc/profile
  
  cat > /etc/sysctl.d/k8s.conf <<EOF
  net.bridge.bridge-nf-call-ip6tables = 1
  net.bridge.bridge-nf-call-iptables = 1
  net.ipv4.ip_forward = 1 
  EOF
  #net.ipv4.ip_forward = 1做路由转发的
  ##net.ipv4.ip_forward是数据包转发：出于安全考虑，Linux系统默认是禁止数据包转发的。所谓转发即当主机拥有多于一块的网卡时，其中一块收到数据包，根据数据包的目的ip地址将数据包发往本机另一块网卡，该网卡根据路由表继续继续发送数据包。这通常是路由器所要实现的功能。
  ##要让Linux系统具有路由转发功能，需要配置一个Linux的内核参数net.ipv4.ip_forward。这个参数指定了Linux系统当前对路由转发功能的支持情况；其值为0时表示禁止进行IP转发；如果是1,则说明IP转发功能已经打开。
  
  sysctl -p /etc/sysctl.d/k8s.conf 
  #在运行时配置内核参数，-p：从指定的文件加载系统参数，如不指定即从/etc/sysctl.conf中加载
  
  ```

- 禁用firewalld防火墙

  ```bash
  systemctl stop firewalld && systemctl disable firewalld
  ```

- 配置阿里云的repo源

  ```bash
  #安装rzsz命令
  yum install lrzsz -y
  #安装scp：
  yum install -y openssh-clients
  #备份基础repo源
  mkdir /root/repo.bak
  cd /etc/yum.repos.d/
  mv * /root/repo.bak/
  
  #下载阿里云的repo源
  ###注意：用GLobalAzure的VM就不需要这面手动修改源了，用自带的源即可###
  #把CentOS-Base.repo和epel.repo文件上传到master1主机的/etc/yum.repos.d/目录下
  chmod 777 /etc/yum.repos.d/
  #通过vscode拖进来
  ```

- 配置国内阿里云docker的repo源

  ```bash
  yum install yum-utils -y
  yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
  ```

- 配置安装k8s组件需要的阿里云的repo源 

  ```bash
  vim /etc/yum.repos.d/kubernetes.repo
  
  [kubernetes]
  name=Kubernetes
  baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64/
  enabled=1
  gpgcheck=0
  ```

- 配置时间同步

  ```bash
  #安装ntpdate命令
  yum install ntpdate -y
  #跟网络时间做同步
  ntpdate cn.pool.ntp.org
  #把时间同步做成计划任务
  crontab -e
  * */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
  #重启crond服务
  service crond restart
  ```

- 安装基础软件包

  ```bash
  ##这一步如果是国外的VM不需要修改源，用自带的源安装即可成功。
  yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate telnet ipvsadm
  ```

- 安装docker服务并配置docker镜像加速器和驱动

  ```bash
  yum install docker-ce-20.10.6 docker-ce-cli-20.10.6 containerd.io -y
  systemctl start docker --now && systemctl status docker #--now相当于 start+enable
  
  #配置docker镜像加速器和驱动
  vim /etc/docker/daemon.json 
  {
   "registry-mirrors":["https://y8y6vosv.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com"],
    "exec-opts": ["native.cgroupdriver=systemd"]
  } 
  #修改docker文件驱动为systemd，默认为cgroupfs，kubelet默认使用systemd，两者必须一致才可以。
  systemctl daemon-reload && systemctl restart docker && systemctl status docker
  ```

- 安装初始化k8s需要的软件包

  ```bash
  yum install -y kubelet-1.20.6 kubeadm-1.20.6 kubectl-1.20.6
  systemctl enable kubelet 
  ```

- 到这里，复制一下master1 VM的OS盘，再创建两台VM出来。

  ```bash
  # 分别修改hostname
  hostnamectl set-hostname master2 && bash
  hostnamectl set-hostname node1 && bash
  ```

- 配Hosts文件

  ```bash
  #修改每台机器的/etc/hosts文件，增加如下三行：
  192.168.40.4 master1
  192.168.40.5 master2
  192.168.40.6 node1
  ```

- 配主机间无密码登录

  ```bash
  passwd root #设一个root密码
  ssh-keygen #一路回车
  ssh-copy-id master1 #输入root密码
  ssh-copy-id master2
  ssh-copy-id node1
  #在另外两台上也执行同样操作#
  ```

## keepalive+nginx实现k8s master节点高可用

**配置nginx和keepalived**：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310201711229.png" alt="image-20231020171124147"  />

- 安装nginx主备

  ```bash
  #在master1和2上装nginx和keeplived
  yum install nginx keepalived -y
  ```

- 修改nginx配置文件

  ```bash
  vim /etc/nginx/nginx.conf
  user nginx;
  worker_processes auto;
  error_log /var/log/nginx/error.log;
  pid /run/nginx.pid;
  
  include /usr/share/nginx/modules/*.conf;
  
  events {
      worker_connections 1024;
  }
  
  # 四层负载均衡，为两台Master apiserver组件提供负载均衡
  stream {
  
      log_format  main  '$remote_addr $upstream_addr - [$time_local] $status $upstream_bytes_sent';
  
      access_log  /var/log/nginx/k8s-access.log  main;
  
      upstream k8s-apiserver {
         server 192.168.40.4:6443 weight=5 max_fails=3 fail_timeout=30s;   # Master1 APISERVER IP:PORT
         server 192.168.40.5:6443 weight=5 max_fails=3 fail_timeout=30s;   # Master2 APISERVER IP:PORT
      }
      
      server {
         listen 16443; # 由于nginx与master节点复用，这个监听端口不能是6443，否则会冲突
         proxy_pass k8s-apiserver;
      }
  }
  
  http {
      log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
  
      access_log  /var/log/nginx/access.log  main;
  
      sendfile            on;
      tcp_nopush          on;
      tcp_nodelay         on;
      keepalive_timeout   65;
      types_hash_max_size 2048;
  
      include             /etc/nginx/mime.types;
      default_type        application/octet-stream;
  
      server {
          listen       80 default_server;
          server_name  _;
  
          location / {
          }
      }
  }
  ```

- 修改keeplived配置文件

  ```bash
  #########主：master1#################
  vim /etc/keepalived/keepalived.conf
  global_defs { 
     notification_email { 
       acassen@firewall.loc 
       failover@firewall.loc 
       sysadmin@firewall.loc 
     } 
     notification_email_from Alexandre.Cassen@firewall.loc  
     smtp_server 127.0.0.1 
     smtp_connect_timeout 30 
     router_id NGINX_MASTER
  } 
  
  vrrp_script check_nginx {
      script "/etc/keepalived/check_nginx.sh"
  }
  
  vrrp_instance VI_1 { 
      state MASTER 
      interface eth0  # 修改为实际网卡名
      virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的 
      unicast_src_ip 192.168.40.4         ##source ip，当前keepalive机器的ip
      unicast_peer {
            192.168.40.5               ##dest ip，另一台keepalive机器的ip
      }
      #如果不加unicase的参数，识别peer ip，那么BACKUP的机器会自动进入MASTER STATE
      priority 100    # 优先级，备服务器设置 90 
      advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
      authentication { 
          auth_type PASS      
          auth_pass 1111 
      }  
      # 虚拟IP
      virtual_ipaddress { 
          192.168.40.10 #需要和VM的IP处于一个网段
      } 
      track_script {
          check_nginx
      } 
  }
  
  ########备master2############
  global_defs { 
     notification_email { 
       acassen@firewall.loc 
       failover@firewall.loc 
       sysadmin@firewall.loc 
     } 
     notification_email_from Alexandre.Cassen@firewall.loc  
     smtp_server 127.0.0.1 
     smtp_connect_timeout 30 
     router_id NGINX_MASTER
  } 
  
  vrrp_script check_nginx {
      script "/etc/keepalived/check_nginx.sh"
  }
  
  vrrp_instance VI_1 { 
      state BACKUP 
      interface eth0  # 修改为实际网卡名
      virtual_router_id 51 # VRRP 路由 ID实例，每个实例是唯一的
      unicast_src_ip 192.168.40.5         ##source ip，当前keepalive机器的ip
      unicast_peer {
            192.168.40.4               ##dest ip，另一台keepalive机器的ip
      }
      priority 90    # 优先级，备服务器设置 90 
      advert_int 1    # 指定VRRP 心跳包通告间隔时间，默认1秒 
      authentication { 
          auth_type PASS      
          auth_pass 1111 
      }  
      # 虚拟IP
      virtual_ipaddress { 
          192.168.40.10 #需要和VM的IP处于一个网段
      } 
      track_script {
          check_nginx
      } 
  }
  ```

- 写检查nginx工作状态脚本

  ```bash
  vim /etc/keepalived/check_nginx.sh 
  #!/bin/bash
  #1、判断Nginx是否存活
  counter=$(ps -ef |grep nginx | grep sbin | egrep -cv "grep|$$" )
  if [ $counter -eq 0 ]; then
      #2、如果不存活则尝试启动Nginx
      service nginx start
      sleep 2
      #3、等待2秒后再次获取一次Nginx状态
      counter=$(ps -ef |grep nginx | grep sbin | egrep -cv "grep|$$" )
      #4、再次进行判断，如Nginx还不存活则停止Keepalived，让地址进行漂移
      if [ $counter -eq 0 ]; then
          service keepalived stop
      fi
  fi
  #注：keepalived根据脚本返回状态码（0为工作正常，非0不正常）判断是否故障转移。
  ```

- 启动nginx和keepalived

  ```bash
  yum install nginx-mod-stream -y
  chmod +x /etc/keepalived/check_nginx.sh
  chmod 644 /etc/keepalived/keepalived.conf
  systemctl daemon-reload
  systemctl start nginx
  systemctl start keepalived
  systemctl enable nginx keepalived && systemctl status keepalived
  
  #在nginx里面设置了监听端口16443
  #在keeplived里面配了VIP 192.168.40.10
  #==>访问192.168.40.10:16443的流量就会被反向代理到两个master：
  #192.168.40.4:6443
  #192.168.40.5:6443
  ```

- 检查keepalived主备切换情况

  ```bash
  #主机
  systemctl stop keepalived
  ip addr #看到VIP已经没了
  #备机
  ip addr #有了VIP
  systemctl status keepalived #看到提升为Master了
  ```

  - Issue：主备两台的keepalived都会进入到MASTER state。
  - Troubleshooting：
    - 检查两台上面的nginx和keepalived都运行正常，也没有防火墙阻挡，互相可以ping通。
    - keepalived的配置文件正确。
    - KB：[Keepalived两节点出现双VIP的情况 - Netonline - 博客园 (cnblogs.com)](https://www.cnblogs.com/netonline/archive/2017/10/09/7642595.html)：主备两台采用vrrp组播流量发送心跳，有可能是两台的上级交换机禁止了组播流量，所以备用机收不到主机心跳，自动提升为MASTER。
    - 进一步查看了Azure VNET文档：[Azure Virtual Network FAQ | Microsoft Learn](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-faq#do-virtual-networks-support-multicast-or-broadcast)：“No. Multicast and broadcast are not supported.” ==> 说明两台VM的虚拟网络禁止组播流量，这是平台限制。
  - Resolve：
    - [k8s架构师课程CKA和CKS精品班学员学习过程遇到的问题汇总（实时更新）: k8s常见学习问题汇总（实时更新） (gitee.com)](https://gitee.com/hanxianchao66/CKA_CKS#1如果做k8s高可用安装实验出现两台机器搭建keepalived但是两台机器都能看到vip这种情况是有问题的如何排查解决)：主备两台的keepalived配置文件上加上unicast_src_ip，变成vrrp单播就可以了。

## 配置kubeadm

- 创建kubeadm配置文件

  ```bash
  #在master1上配置：
  cd /root/
  vim kubeadm-config.yaml 
  
  apiVersion: kubeadm.k8s.io/v1beta2
  kind: ClusterConfiguration
  kubernetesVersion: v1.20.6
  controlPlaneEndpoint: 192.168.40.4:16443
  imageRepository: registry.aliyuncs.com/google_containers
  apiServer:
   certSANs:
   - 192.168.40.4
   - 192.168.40.5
   - 192.168.40.6
   - 192.168.40.10
  networking:
    podSubnet: 10.244.0.0/16
    serviceSubnet: 10.96.0.0/16
  ---
  apiVersion: kubeproxy.config.k8s.io/v1alpha1
  kind:  KubeProxyConfiguration
  mode: ipvs
  ```

  > 注意：
  >
  > 1. 参数image-repository: registry.aliyuncs.com/google_containers
  >    - 为保证拉取镜像不到国外站点拉取，手动指定仓库地址为registry.aliyuncs.com/google_containers。
  >    - kubeadm默认从k8s.gcr.io拉取镜像。
  >    - 如果本地有导入的离线镜像，会优先使用本地的镜像。
  >
  > 2. kubeproxy模式采用ipvs：如果不指定ipvs，会默认使用iptables，但是iptables效率低，所以我们生产环境建议开启ipvs。
  > 3. controlPlaneEndpoint: 192.168.40.10:16443，16443是把请求代理给nginx的配置。

## 初始化集群

- 加载master组件的镜像

  ```bash
  #在master1、master2、node1上都解压
  docker load -i k8simage-1-20-6.tar.gz
  #没有离线包的话，后面执行kubeadm init也会自动从镜像源下载这些image包
  ```

- kubeadm初始化k8s集群

  ```bash
  #在master1上执行：
  cd /root/
  kubeadm init --config kubeadm-config.yaml --ignore-preflight-errors=SystemVerification
  ```

- 对kubectl授权

  ```bash
  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config
  kubectl get nodes
  #notready是因为还没有安装网络插件
  ```

- kubectl 修改 alias为k并添加补全

  ```bash
  #1. 设置kubectl的alias为k：
  whereis kubectl # kubectl: /usr/bin/kubectl
  echo  "alias k=/usr/bin/kubectl">>/etc/profile
  source /etc/profile
  #2. 设置alias的自动补全：
  source <(kubectl completion bash | sed 's/kubectl/k/g')
  #3. 解决每次启动k都会失效，要重新刷新环境变量（source /etc/profile）的问题：在~/.bashrc文件中添加以下代码：source /etc/profile
  echo "source /etc/profile" >> ~/.bashrc
  ```

  > kubectl机理解释：
  >
  > - kubectl走的是 /root/.kube/config 文件中的配置，如何查看：
  >
  >   - kubectl config view 
  >
  >     ```yaml
  >     apiVersion: v1
  >     clusters:
  >     - cluster:
  >         certificate-authority-data: DATA+OMITTED
  >         server: https://192.168.40.4:16443
  >       name: kubernetes
  >     contexts:
  >     - context:
  >         cluster: kubernetes
  >         user: kubernetes-admin #声明了当前用户，这个是安装k8s的时候自动生成的admin用户
  >       name: kubernetes-admin@kubernetes
  >     current-context: kubernetes-admin@kubernetes
  >     kind: Config
  >     preferences: {}
  >     users:
  >     - name: kubernetes-admin
  >       user:
  >         client-certificate-data: REDACTED
  >         client-key-data: REDACTED
  >     ```
  >
  > - 如果想要在别的机器上运行kubectl，只需要保证这个机器能连通到master，再把/root/.kube/config拷过去就行了。
  >
  >   ```bash
  >   #目标机器
  >   mkdir -p /root/.kube/
  >   #master上
  >   scp /root/.kube/config node1:/root/.kube/
  >   ```

- 扩容集群-添加master节点

  ```bash
  #master2上创建证书目录
  cd /root && mkdir -p /etc/kubernetes/pki/etcd && mkdir -p ~/.kube/
  #把master1的证书拷贝到master2
  scp /etc/kubernetes/pki/ca.crt master2:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/ca.key master2:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/sa.key master2:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/sa.pub master2:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/front-proxy-ca.crt master2:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/front-proxy-ca.key master2:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/etcd/ca.crt master2:/etc/kubernetes/pki/etcd/
  scp /etc/kubernetes/pki/etcd/ca.key master2:/etc/kubernetes/pki/etcd/
  #在master1上查看join节点的命令
  kubeadm token create --print-join-command
  #在master2上执行这个join命令
  #查看节点状况
  kubectl get nodes
  ```

  - Issue: 用VM来做，keepalived的VIP无法接收到流量，无法用做k8s-apiserver暴露的IP。节点扩容会失败。

- 扩容集群-添加node节点

  ```bash
  #在master1上查看join节点的命令
  kubeadm token create --print-join-command
  #在node1上执行这个join命令
  #因为是加master节点，需要加上 --control-plane --ignore-preflight-errors=SystemVerification
  #查看节点状况
  kubectl get nodes
  
  #master1上get node看到node1的role为none
  #可以把node1的ROLES变成worker，按照如下方法：
  kubectl label node node1 node-role.kubernetes.io/worker=worker
  kubectl get pod -n kube-system
  #看到corends pod是pending，因为还没装网络插件
  ```

- 安装网络插件calico

  ```bash
  #上传了Caclio.yaml
  kubectl apply -f calico.yaml
  #在线下载地址为：https://docs.projectcalico.org/manifests/calico.yaml
  ```

  - 测试caclio是否正常工作

    ```bash
    #上传busybox并解压
    docker load -i busybox-1-28.tar.gz
    kubectl run busybox --image busybox:1.28 --restart=Never --rm -it busybox -- sh
    #测试是否能联网
    ping www.baidu.com
    #测试是否能解析dns
    nslookup kubernetes.default.svc.cluster.local #这个域名是默认创建的service的FQDN
    
    Server:    10.96.0.10
    Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local
    
    Name:      kubernetes.default.svc.cluster.local
    Address 1: 10.96.0.1 kubernetes.default.svc.cluster.local
    #k8s内部解析域名用的dns server是coreDNS（coredns的svc ip就是这里的10.96.0.10）
    k get svc -A
    NAMESPACE     NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
    default       kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP                  4h21m
    kube-system   kube-dns     ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   4h21m
    ```

- 延长证书有效期

  ```bash
  #查看ca证书过期时间
  openssl x509 -in /etc/kubernetes/pki/ca.crt -noout -text | grep Not
  # 查看apiserver证书过期时间
  openssl x509 -in /etc/kubernetes/pki/apiserver.crt -noout -text | grep Not
  #可以看到apiserver证书的有效期是1年
  #把延长的脚本上传：update-kubeadm-cert.sh并赋权执行
  chmod +x update-kubeadm-cert.sh
  ./update-kubeadm-cert.sh all
  ```

- 如何卸载kubeadm安装的集群

  ```bash
  #装错了需要重新初始化
  kubeadm reset
  ```

# kubeadm安装单master集群

## 安装装备步骤

- 方法同[前面多master的步骤](#安装准备步骤)

## 安装集群

### 生成并修改配置文件

```yaml
kubeadm config print init-defaults > kubeadm.yaml

apiVersion: kubeadm.k8s.io/v1beta2
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
  advertiseAddress: 192.168.40.4 #控制节点的ip
  bindPort: 6443
nodeRegistration:
  criSocket: /var/run/dockershim.sock
  name: master1 #控制节点主机名
  taints:
  - effect: NoSchedule
    key: node-role.kubernetes.io/master
---
apiServer:
  timeoutForControlPlane: 4m0s
apiVersion: kubeadm.k8s.io/v1beta2
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns:
  type: CoreDNS
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.aliyuncs.com/google_containers #修改默认镜像仓库为阿里云
kind: ClusterConfiguration
kubernetesVersion: v1.20.6
networking:
  dnsDomain: cluster.local
  serviceSubnet: 10.96.0.0/12
  podSubnet: 10.244.0.0/16 #指定pod网段， 需要新增加这个
scheduler: {}
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
```

### 初始化集群

```bash
kubeadm init --config=kubeadm.yaml --ignore-preflight-errors=SystemVerification
```

### 授权kubectl

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 扩容节点

```bash
#master1查看join命令
kubeadm token create --print-join-command
#node1上把命令添加参数：--ignore-preflight-errors=SystemVerification
##master1的kubectl的config文件拷到node1上
scp $HOME/.kube/config node1:/root/.kube/
#node1打标签
kubectl label node node1 node-role.kubernetes.io/worker=worker
##同样方法扩容node2
```

### 安装Caclio

方法同[前面多master的步骤](#初始化集群)

### 延长证书有效期

方法同[前面多master的步骤](#初始化集群)

# kubeadm基础

## 流程

![image-20231023132237932](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310231322150.png)

## 预检查  

kubeadm 在执行安装之前进行了相当细致的环境检测：

​    1) 检查执行 init 命令的用户是否为 root，如果不是 root，直接快速失败（fail fast）；

​    2) 检查待安装的 k8s 版本是否被当前版本的 kubeadm 支持（kubeadm 版本 >= 待安装 k8s 版本）；

​    3) 检查防火墙，如果防火墙未关闭，提示开放端口 10250；

​    4) 检查端口是否已被占用，6443（或你指定的监听端口）、10257、10259；

​    5) 检查文件是否已经存在，/etc/kubernetes/manifests/*.yaml；

​    6) 检查是否存在代理，连接本机网络、服务网络、Pod网络，都会检查，目前不允许代理；

​    7) 检查容器运行时，使用 CRI 还是 Docker，如果是 Docker，进一步检查 Docker 服务是否已启动，是否设置了开机自启动；

​    8) 对于 Linux 系统，会额外检查以下内容：

​      8.1) 检查以下命令是否存在：crictl、ip、iptables、mount、nsenter、ebtables、ethtool、socat、tc、touch；

​      8.2) 检查 /proc/sys/net/bridge/bridge-nf-call-iptables、/proc/sys/net/ipv4/ip-forward 内容是否为 1；

​      8.3) 检查 swap 是否是关闭状态；

​    9) 检查内核是否被支持，Docker 版本及后端存储 GraphDriver 是否被支持；

​       对于 Linux 系统，还需检查 OS 版本和 cgroup 支持程度（支持哪些资源的隔离）；

​    10) 检查主机名访问可达性；

​    11) 检查 kubelet 版本，要高于 kubeadm 需要的最低版本，同时不高于待安装的 k8s 版本；

​    12) 检查 kubelet 服务是否开机自启动；

​    13) 检查 10250 端口是否被占用；

​    14) 如果开启 IPVS 功能，检查系统内核是否加载了 ipvs 模块；

​    15) 对于 etcd，如果使用 Local etcd，则检查 2379 端口是否被占用， /var/lib/etcd/ 是否为空目录；

​       如果使用 External etcd，则检查证书文件是否存在（CA、key、cert），验证 etcd 服务版本是否符合要求；

​    16) 如果使用 IPv6，

​        检查 /proc/sys/net/bridge/bridge-nf-call-iptables、/proc/sys/net/ipv6/conf/default/forwarding 内容是否为 1。

## 完成安装前的配置

​    1) 在 kube-system 命名空间创建 ConfigMap kubeadm-config，同时对其配置 RBAC 权限；

​    2) 在 kube-system 命名空间创建 ConfigMap kubelet-config-<version>，同时对其配置 RBAC 权限；

​    3) 为当前节点（Master）打标记：node-role.kubernetes.io/master=；

​    4) 为当前节点（Master）补充 Annotation；

​    5) 如果启用了 DynamicKubeletConfig 特性，设置本节点 kubelet 的配置数据源为 ConfigMap 形式；

​    6) 创建 BootStrap token Secret，并对其配置 RBAC 权限；

​    7) 在 kube-public 命名空间创建 ConfigMap cluster-info，同时对其配置 RBAC 权限；

​    8) 与 apiserver 通信，部署 DNS 服务；

​    9) 与 apiserver 通信，部署 kube-proxy 服务；

​    10) 如果启用了 self-hosted 特性，将 Control Plane 转为 DaemonSet 形式运行；

​    11) 打印 join 语句；

# Kubeadm生成的k8s证书

## 证书分组

- Kubernetes把证书放在了两个文件夹中

  - /etc/kubernetes/pki

  - /etc/kubernetes/pki/etcd

## 集群根证书

- Kubernetes 集群根证书CA(Kubernetes集群组件的证书签发机构)

  - /etc/kubernetes/pki/ca.crt

  - /etc/kubernetes/pki/ca.key

- 以上这组证书为签发其他Kubernetes组件证书使用的根证书, 可以认为是Kubernetes集群中证书签发机构之一 

- 由此根证书签发的证书有:

  - 1、kube-apiserver apiserver证书

    - /etc/kubernetes/pki/apiserver.crt

    - /etc/kubernetes/pki/apiserver.key

  - 2、kubelet客户端证书, 用作 kube-apiserver 主动向 kubelet 发起请求时的客户端认证
- /etc/kubernetes/pki/apiserver-kubelet-client.crt
  
- /etc/kubernetes/pki/apiserver-kubelet-client.key

## kube-apiserver代理根证书(客户端证书)

- 用在requestheader-client-ca-file配置选项中, kube-apiserver 使用该证书来验证客户端证书是否为自己所签发

  - /etc/kubernetes/pki/front-proxy-ca.crt

  - /etc/kubernetes/pki/front-proxy-ca.key

- 由此根证书签发的证书只有一组:

  - 代理层(如汇聚层aggregator)使用此套代理证书来向 kube-apiserver 请求认证

  - 代理端使用的客户端证书, 用作代用户与 kube-apiserver 认证

    - /etc/kubernetes/pki/front-proxy-client.crt

    - /etc/kubernetes/pki/front-proxy-client.key

## etcd 集群根证书

- etcd集群所用到的证书都保存在/etc/kubernetes/pki/etcd这路径下, 这一套证书是用来专门给etcd集群服务使用的, 设计以下证书文件：

  - etcd 集群根证书CA(etcd 所用到的所有证书的签发机构)

    - /etc/kubernetes/pki/etcd/ca.crt

    - /etc/kubernetes/pki/etcd/ca.key

- 由此根证书签发机构签发的证书有:

  - 1、etcd server 持有的服务端证书

    - /etc/kubernetes/pki/etcd/server.crt

    - /etc/kubernetes/pki/etcd/server.key

  - 2、peer 集群中节点互相通信使用的客户端证书

    - /etc/kubernetes/pki/etcd/peer.crt

    - /etc/kubernetes/pki/etcd/peer.key

  注: Peer：对同一个etcd集群中另外一个Member的称呼

  - 3、pod 中定义 Liveness 探针使用的客户端证书

    - kubeadm 部署的 Kubernetes 集群是以 pod 的方式运行 etcd 服务的, 在该 pod 的定义中, 配置了 Liveness 探活探针

    - /etc/kubernetes/pki/etcd/healthcheck-client.crt

    - /etc/kubernetes/pki/etcd/healthcheck-client.key

    - 当你 describe etcd 的 pod 时, 会看到如下一行配置:

      ```bash
      Liveness: exec [/bin/sh -ec ETCDCTL_API=3 etcdctl --endpoints=https://[127.0.0.1]:2379 --cacert=/etc/kubernetes/pki/etcd/ca.crt --cert=/etc/kubernetes/pki/etcd/healthcheck-client.crt --key=/etc/kubernetes/pki/etcd/healthcheck-client.key get foo] delay=15s timeout=15s period=10s #success=1 #failure=8
      ```

  - 4、配置在 kube-apiserver 中用来与 etcd server 做双向认证的客户端证书

    - /etc/kubernetes/pki/apiserver-etcd-client.crt

    - /etc/kubernetes/pki/apiserver-etcd-client.key

# Calico基础

## 架构图

![image-20231023152017200](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310231520298.png)

## Calico主要工作组件

1. Felix：运行在每一台 Host 的 agent 进程，主要负责网络接口管理和监听、路由、ARP 管理、ACL 管理和同步、状态上报等。保证跨主机容器网络互通。
2. etcd：分布式键值存储，相当于k8s集群中的数据库，存储着Calico网络模型中IP地址等相关信息。主要负责网络元数据一致性，确保 Calico 网络状态的准确性；

3. BGP Client（BIRD）：Calico 为每一台 Host 部署一个 BGP Client，即每台host上部署一个BIRD。 主要负责把 Felix 写入 Kernel 的路由信息分发到当前 Calico 网络，确保 Workload 间的通信的有效性；

4. BGP Route Reflector：在大型网络规模中，如果仅仅使用 BGP client 形成 mesh 全网互联的方案就会导致规模限制，因为所有节点之间俩俩互联，需要 N^2 个连接，为了解决这个规模问题，可以采用 BGP 的 Router Reflector 的方法，通过一个或者多个 BGP Route Reflector 来完成集中式的路由分发。 

## calico配置文件

### Daemonset配置

```
...
containers:
        # Runs calico-node container on each Kubernetes node. This container programs network policy and routes on each host.
        - name: calico-node
          image: docker.io/calico/node:v3.18.0
……
          env:
          # Use Kubernetes API as the backing datastore.
           - name: DATASTORE_TYPE
             value: "kubernetes"
          # Cluster type to identify the deployment type
           - name: CLUSTER_TYPE
             value: "k8s,bgp"
          # Auto-detect the BGP IP address.
           - name: IP
             value: "autodetect"
          #pod网段
           - name: CALICO_IPV4POOL_CIDR 
             value: "10.244.0.0/16"
          # Enable IPIP
           - name: CALICO_IPV4POOL_IPIP
             value: "Always"
```

### calico-node服务的主要参数:

- CALICO_IPV4POOL_IPIP：
  - 是否启用IPIP模式。启用IPIP模式时，Calico将在Node上创建一个名为tunl0的虚拟隧道。IP Pool可以使用两种模式：BGP或IPIP。使用IPIP模式时，设置CALICO_IPV4POOL_IPIP="Always"，不使用IPIP模式时，设置CALICO_IPV4POOL_IPIP="Off"，此时将使用BGP模式。

- IP_AUTODETECTION_METHOD：

  - 获取Node IP地址的方式，默认使用第1个网络接口的IP地址，对于安装了多块网卡的Node，可以使用正则表达式选择正确的网卡，例如"interface=eth.*"表示选择名称以eth开头的网卡的IP地址。

    ```yaml
    -  name: IP_AUTODETECTION_METHOD #位置:在calico.yaml-DaemonSet:Containers:env里面配置
       value: "interface=ens33"
    ```

## IPIP模式和BGP模式对比分析

- IPIP
  - 把一个IP数据包又套在一个IP包里，即把IP层封装到IP层的一个 tunnel，它的作用其实基本上就相当于一个基于IP层的网桥，一般来说，普通的网桥是基于mac层的，根本不需要IP，而这个ipip则是通过两端的路由做一个tunnel，把两个本来不通的网络通过点对点连接起来；
  - calico以ipip模式部署完毕后，node上会有一个tunl0的网卡设备，这是ipip做隧道封装用的,也是一种overlay模式的网络。当我们把节点下线，calico容器都停止后，这个设备依然还在，执行 rmmodipip命令可以将它删除。

- BGP

  - BGP模式直接使用物理机作为虚拟路由路（vRouter），不再创建额外的tunnel

  > - 边界网关协议（BorderGateway Protocol, BGP）是互联网上一个核心的去中心化的自治路由协议。它通过维护IP路由表或‘前缀’表来实现自治系统（AS）之间的可达性，属于矢量路由协议。BGP不使用传统的内部网关协议（IGP）的指标，而是基于路径、网络策略或规则集来决定路由。因此，它更适合被称为矢量性协议，而不是路由协议，通俗的说就是将接入到机房的多条线路（如电信、联通、移动等）融合为一体，实现多线单IP；
  > - BGP 机房的优点：服务器只需要设置一个IP地址，最佳访问路由是由网络上的骨干路由器根据路由跳数与其它技术指标来确定的，不会占用服务器的任何系统；

- 官方提供的calico.yaml模板里，默认打开了ip-ip功能，该功能会在node上创建一个设备tunl0，容器的网络数据会经过该设备被封装一个ip头再转发。
  - 这里，calico.yaml中通过修改calico-node的环境变量：CALICO_IPV4POOL_IPIP来实现ipip功能的开关：默认是Always，表示开启；Off表示关闭ipip。

```yaml
- name:  CLUSTER_TYPE
  value: "k8s,bgp"
  # Auto-detect the BGP IP address.
- name: IP
  value: "autodetect"
  # Enable IPIP
- name: CALICO_IPV4POOL_IPIP
  value: "Always"
```

- 总结：
  - calico BGP通信是基于TCP协议的，所以只要节点间三层互通即可完成，即三层互通的环境bird就能生成与邻居有关的路由。但是这些路由和flannel host-gateway模式一样，需要二层互通才能访问的通，因此如果在实际环境中配置了BGP模式生成了路由但是不同节点间pod访问不通，可能需要再确认下节点间是否二层互通。
  - 为了解决节点间二层不通场景下的跨节点通信问题，calico也有自己的解决方案——IPIP模式.

## 其他常用网络插件

1. flannel：支持vxlan、host-gw，但是效率比较低
2. Calico：支持IPIP、BGP模式，效率较高，可以跨网段、支持网络策略隔离
3. Weave
4. Canal
