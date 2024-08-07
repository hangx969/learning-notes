# 环境准备

## 实验环境规划

- 操作系统：rockylinux8.9

- 配置：4Gib/内存/4vCPU/60G硬盘

- 网络：NAT模式，可以确保机器在任何网络都能ssh连接 

| K8S集群角色 | IP            | 主机名   |
| ----------- | ------------- | -------- |
| 控制节点    | 172.16.183.60 | rmaster1 |
| 工作节点    | 172.16.183.61 | rnode1   |

## 安装前准备

- 软件包安装

~~~sh
yum install -y device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat ipvsadm conntrack telnet ipvsadm vim
~~~

- 配置网络

~~~sh
#查看网卡名
ip addr
~~~

~~~sh
#编辑网卡配置文件
vim /etc/sysconfig/network-scripts/ifcfg-ens160
#修改成如下内容：
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
IPADDR=172.16.183.60
NETMASK=255.255.255.0
GATEWAY=172.16.183.2
DNS1=172.16.183.2
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=ens160
DEVICE=ens160
ONBOOT=yes
~~~

~~~sh
nmcli connection reload 
nmcli c up ens160
~~~

- 关闭selinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot
~~~

- 配置主机名

~~~sh
hostnamectl set-hostname rmaster1 && bash #rnode1 
~~~

- 配置hosts

~~~sh
tee -a /etc/hosts <<'EOF'
172.16.183.60   rmaster1  
172.16.183.61   rnode1
EOF
~~~

- 配置ssh互信

~~~sh
ssh-keygen
ssh-copy-id rnode1
~~~

- 关闭交换分区

~~~sh
swapoff -a
vim /etc/fstab   
#/dev/mapper/centos-swap swap      swap    defaults        0 0
~~~

- 修改内核参数

~~~sh
#将br_netfilter模块添加到 Linux 内核中。这是Linux网桥的核心模块，提供网络包转发和过滤。Kubernetes需要网络插件（如 Flannel、Calico）实现容器间通信，而这些网络插件通常会用Linux网桥来进行数据包转发和过滤。
modprobe br_netfilter

#开启包过滤
tee /etc/sysctl.d/k8s.conf <<'EOF'
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

sysctl -p /etc/sysctl.d/k8s.conf
~~~

- 关闭防火墙

~~~sh
systemctl stop firewalld && systemctl disable firewalld
~~~

- 配置时间同步

~~~sh
yum -y install chrony
systemctl enable chronyd --now 

tee -a /etc/chrony.conf <<'EOF'  
server ntp1.aliyun.com iburst
server ntp2.aliyun.com iburst
server ntp1.tencent.com iburst
server ntp2.tencent.com iburst
EOF
#Iburst: 如果设置该选项，前四轮询之间的间隔将是2秒，而不是minpoll。 这对于在chronyd启动后快速获得时钟的第一次更新非常有用。即：重启chronyd后，2秒后，直接同步一次时间。
crontab -e
* * * * * /usr/bin/systemctl restart chronyd

systemctl restart crond
~~~

- 配置aliyun docker repo源

~~~sh
#配置国内安装docker和containerd的阿里云在线源
yum install yum-utils -y
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
~~~

# 组件安装

## containerd

~~~sh
yum install containerd.io-1.6.22*  -y
cd /etc/containerd
#rm -rf *
~~~

- 如果有harbor环境，修改config.toml为以下。（将\<harbor IP>替换为安装harbor机器的IP）

~~~toml
disabled_plugins = []
imports = []
oom_score = 0
plugin_dir = ""
required_plugins = []
root = "/var/lib/containerd"
state = "/run/containerd"
temp = ""
version = 2

[cgroup]
  path = ""

[debug]
  address = ""
  format = ""
  gid = 0
  level = ""
  uid = 0

[grpc]
  address = "/run/containerd/containerd.sock"
  gid = 0
  max_recv_message_size = 16777216
  max_send_message_size = 16777216
  tcp_address = ""
  tcp_tls_ca = ""
  tcp_tls_cert = ""
  tcp_tls_key = ""
  uid = 0

[metrics]
  address = ""
  grpc_histogram = false

[plugins]

  [plugins."io.containerd.gc.v1.scheduler"]
    deletion_threshold = 0
    mutation_threshold = 100
    pause_threshold = 0.02
    schedule_delay = "0s"
    startup_delay = "100ms"

  [plugins."io.containerd.grpc.v1.cri"]
    device_ownership_from_security_context = false
    disable_apparmor = false
    disable_cgroup = false
    disable_hugetlb_controller = true
    disable_proc_mount = false
    disable_tcp_service = true
    enable_selinux = false
    enable_tls_streaming = false
    enable_unprivileged_icmp = false
    enable_unprivileged_ports = false
    ignore_image_defined_volumes = false
    max_concurrent_downloads = 3
    max_container_log_line_size = 16384
    netns_mounts_under_state_dir = false
    restrict_oom_score_adj = false
    sandbox_image = "registry.cn-hangzhou.aliyuncs.com/google_containers/pause:3.7"
    selinux_category_range = 1024
    stats_collect_period = 10
    stream_idle_timeout = "4h0m0s"
    stream_server_address = "127.0.0.1"
    stream_server_port = "0"
    systemd_cgroup = false
    tolerate_missing_hugetlb_controller = true
    unset_seccomp_profile = ""

    [plugins."io.containerd.grpc.v1.cri".cni]
      bin_dir = "/opt/cni/bin"
      conf_dir = "/etc/cni/net.d"
      conf_template = ""
      ip_pref = ""
      max_conf_num = 1

    [plugins."io.containerd.grpc.v1.cri".containerd]
      default_runtime_name = "runc"
      disable_snapshot_annotations = true
      discard_unpacked_layers = false
      ignore_rdt_not_enabled_errors = false
      no_pivot = false
      snapshotter = "overlayfs"

      [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.default_runtime.options]

      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]

        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
          base_runtime_spec = ""
          cni_conf_dir = ""
          cni_max_conf_num = 0
          container_annotations = []
          pod_annotations = []
          privileged_without_host_devices = false
          runtime_engine = ""
          runtime_path = ""
          runtime_root = ""
          runtime_type = "io.containerd.runc.v2"

          [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
            BinaryName = ""
            CriuImagePath = ""
            CriuPath = ""
            CriuWorkPath = ""
            IoGid = 0
            IoUid = 0
            NoNewKeyring = false
            NoPivotRoot = false
            Root = ""
            ShimCgroup = ""
            SystemdCgroup = true

      [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime]
        base_runtime_spec = ""
        cni_conf_dir = ""
        cni_max_conf_num = 0
        container_annotations = []
        pod_annotations = []
        privileged_without_host_devices = false
        runtime_engine = ""
        runtime_path = ""
        runtime_root = ""
        runtime_type = ""

        [plugins."io.containerd.grpc.v1.cri".containerd.untrusted_workload_runtime.options]

    [plugins."io.containerd.grpc.v1.cri".image_decryption]
      key_model = "node"

    [plugins."io.containerd.grpc.v1.cri".registry]
      config_path = ""

      [plugins."io.containerd.grpc.v1.cri".registry.auths]

      [plugins."io.containerd.grpc.v1.cri".registry.configs]
        [plugins."io.containerd.grpc.v1.cri".registry.configs."<harbor IP>".tls]
            insecure_skip_verify = true
        [plugins."io.containerd.grpc.v1.cri".registry.configs."<harbor IP>".auth]
            username = "admin"
            password = "Harbor12345"

      [plugins."io.containerd.grpc.v1.cri".registry.headers]

      [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
         [plugins."io.containerd.grpc.v1.cri".registry.mirrors."<harbor IP>"]
            endpoint = ["https://<harbor IP>:443"]
          [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
             endpoint = ["https://vh3bm52y.mirror.aliyuncs.com","https://registry.docker-cn.com"]

    [plugins."io.containerd.grpc.v1.cri".x509_key_pair_streaming]
      tls_cert_file = ""
      tls_key_file = ""

  [plugins."io.containerd.internal.v1.opt"]
    path = "/opt/containerd"

  [plugins."io.containerd.internal.v1.restart"]
    interval = "10s"

  [plugins."io.containerd.internal.v1.tracing"]
    sampling_ratio = 1.0
    service_name = "containerd"

  [plugins."io.containerd.metadata.v1.bolt"]
    content_sharing_policy = "shared"

  [plugins."io.containerd.monitor.v1.cgroups"]
    no_prometheus = false

  [plugins."io.containerd.runtime.v1.linux"]
    no_shim = false
    runtime = "runc"
    runtime_root = ""
    shim = "containerd-shim"
    shim_debug = false

  [plugins."io.containerd.runtime.v2.task"]
    platforms = ["linux/amd64"]
    sched_core = false

  [plugins."io.containerd.service.v1.diff-service"]
    default = ["walking"]

  [plugins."io.containerd.service.v1.tasks-service"]
    rdt_config_file = ""

  [plugins."io.containerd.snapshotter.v1.aufs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.btrfs"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.devmapper"]
    async_remove = false
    base_image_size = ""
    discard_blocks = false
    fs_options = ""
    fs_type = ""
    pool_name = ""
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.native"]
    root_path = ""

  [plugins."io.containerd.snapshotter.v1.overlayfs"]
    root_path = ""
    upperdir_label = false

  [plugins."io.containerd.snapshotter.v1.zfs"]
    root_path = ""

  [plugins."io.containerd.tracing.processor.v1.otlp"]
    endpoint = ""
    insecure = false
    protocol = ""

[proxy_plugins]

[stream_processors]

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar"

  [stream_processors."io.containerd.ocicrypt.decoder.v1.tar.gzip"]
    accepts = ["application/vnd.oci.image.layer.v1.tar+gzip+encrypted"]
    args = ["--decryption-keys-path", "/etc/containerd/ocicrypt/keys"]
    env = ["OCICRYPT_KEYPROVIDER_CONFIG=/etc/containerd/ocicrypt/ocicrypt_keyprovider.conf"]
    path = "ctd-decoder"
    returns = "application/vnd.oci.image.layer.v1.tar+gzip"

[timeouts]
  "io.containerd.timeout.bolt.open" = "0s"
  "io.containerd.timeout.shim.cleanup" = "5s"
  "io.containerd.timeout.shim.load" = "5s"
  "io.containerd.timeout.shim.shutdown" = "3s"
  "io.containerd.timeout.task.state" = "2s"

[ttrpc]
  address = ""
  gid = 0
  uid = 0
~~~

~~~sh
systemctl start containerd && systemctl enable containerd
~~~

## k8s

~~~sh
#配置安装k8s组件需要的阿里云的repo源 
cat > /etc/yum.repos.d/kubernetes.repo <<EOF
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/
enabled=1
gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.30/rpm/repodata/repomd.xml.key
EOF
#其中baseurl是指定仓库的URL地址。这个仓库是Kubernetes针对CentOS 7 x86_64架构的yum仓库，yum会从这个指定的URL地址获取Kubernetes的安装包和依赖包，从而进行安装。使用阿里云镜像站可以提高安装速度和稳定性。
yum clean all && yum makecache
yum install -y kubelet-1.30.0 kubeadm-1.30.0 kubectl-1.30.0
systemctl enable kubelet
~~~

# kubeadm初始化k8s集群

## 初始化集群

~~~sh
kubeadm config print init-defaults > kubeadm.yaml
~~~

~~~yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 172.16.183.60 #控制节点的ip
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///run/containerd/containerd.sock  #指定containerd容器运行时
  imagePullPolicy: IfNotPresent
  name:  rmaster1 #控制节点主机名
  taints: null
---
apiVersion: kubeadm.k8s.io/v1beta3
certificatesDir: /etc/kubernetes/pki
clusterName: kubernetes
controllerManager: {}
dns: {}
etcd:
  local:
    dataDir: /var/lib/etcd
imageRepository: registry.cn-hangzhou.aliyuncs.com/google_containers
kind: ClusterConfiguration
kubernetesVersion: 1.30.0 
networking:
  dnsDomain: cluster.local
  podSubnet: 10.244.0.0/16 
  serviceSubnet: 10.96.0.0/12 
scheduler: {}
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
~~~

~~~sh
kubeadm init --config=kubeadm.yaml --ignore-preflight-errors=SystemVerification
~~~

## 配置kubeconfig

~~~sh
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

#1. 设置kubectl的alias为k：
whereis kubectl ## kubectl: /usr/bin/kubectl
echo "alias k=/usr/bin/kubectl">>/etc/profile
source /etc/profile
#2. 设置alias的自动补全：
source <(kubectl completion bash | sed 's/kubectl/k/g')
#3. 解决每次启动k都会失效，要重新刷新环境变量（source /etc/profile）的问题：在~/.bashrc文件中添加以下代码：source /etc/profile
echo "source /etc/profile" >> ~/.bashrc
#4. 给alias k也配置补全
vim ~/.bashrc
##加入以下
alias k='kubectl'
complete -o default -F __start_kubectl k
source <(kubectl completion bash)
##使命令生效
source ~/.bashrc
~~~

## 扩容工作节点

~~~sh
#master上
kubeadm token create --print-join-command
#把rnode1加入k8s集群，加上参数：--ignore-preflight-errors=SystemVerification
#打工作节点label
kubectl label nodes rnode1 node-role.kubernetes.io/work=worker
~~~

## 安装calico

~~~sh
#上传calico镜像包和yaml文件，解压
ctr -n=k8s.io images import calico.tar.gz
#修改calico.yaml中网卡名称
- name: IP_AUTODETECTION_METHOD
  value: "interface=ens33"
  
kubectl apply -f calico.yaml
~~~

~~~sh
#测试网络访问
kubectl run busybox --image busybox:1.28  --image-pull-policy=IfNotPresent --restart=Never --rm -it busybox -- sh
# ping www.baidu.com
# nslookup kubernetes.default.svc.cluster.local
~~~
