# kubeadm基础

## 流程

![image-20231024122121237](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310241221337.png)

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

# kubeadm安装的k8s集群升级

参考官网：http://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade