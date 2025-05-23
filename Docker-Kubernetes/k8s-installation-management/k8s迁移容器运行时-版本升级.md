# 将容器运行时从docker迁移到containerd

## 实验环境

- master1、node1
- k8s版本为1.23.1
- OS版本为centos7.9

## 封锁排空节点

- cordon、drain master节点

~~~sh
kubectl cordon master1
kubectl drain master1  --delete-emptydir-data  --force --ignore-daemonsets
#当一些pod不是经 ReplicationController, ReplicaSet, Job, DaemonSet 或者 StatefulSet 管理的时候，就需要用--force来强制执行 (例如:kube-proxy)
#--ignore-daemonsets：如果有mount local volume的pod，会强制驱逐pod
~~~

## 停止并卸载docker

~~~sh
systemctl disable docker  --now
yum remove docker-ce docker-ce-cli -y
~~~

## 安装配置containerd

- 安装containerd

~~~sh
yum install containerd.io cri-tools  -y
crictl config runtime-endpoint unix:///var/run/containerd/containerd.sock
~~~

- 生成containerd配置文件

~~~sh
containerd config default > /etc/containerd/config.toml
vim /etc/containerd/config.toml

#在[plugins."io.containerd.grpc.v1.cri".registry.mirrors]这一行下面配置endpoint
[plugins."io.containerd.grpc.v1.cri".registry.mirrors]
  [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
    endpoint = ["https://rsbud4vc.mirror.aliyuncs.com"]

#修改：
sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.7"
#修改：
[plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
   SystemdCgroup = true
~~~

- 重启containerd

~~~sh
systemctl enable containerd; systemctl restart containerd
~~~

## 配置kubelet

- 修改kubelet参数

~~~sh
vim /etc/sysconfig/kubelet
KUBELET_EXTRA_ARGS="--container-runtime=remote --runtime-request-timeout=15m --container-runtime-endpoint=unix:///run/containerd/containerd.sock"
systemctl restart kubelet
~~~

- 修改node annotation

~~~yaml
kubectl edit nodes master1

apiVersion: v1
kind: Node
metadata:
  annotations:
    kubeadm.alpha.kubernetes.io/cri-socket: /var/run/containerd/containerd.sock
~~~

## 解锁节点调度

~~~sh
kubectl uncordon master1
~~~

## 验证

~~~sh
kubectl get nodes -owide
~~~

## 迁移worker节点

- 遵循上面与master相同的步骤

# k8s版本升级-1.23-1.24

## 实验环境

- 由1.23升级到1.24，包括了容器运行时由docker升级为containerd，升级kubernetes组件。这里接着上面升级到containerd继续进行。
- 参考官网文档：http://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade

## 封锁排空控制节点

~~~sh
kubectl cordon master1
kubectl drain master1 --delete-emptydir-data --force --ignore-daemonsets
~~~

## 升级控制节点

- 升级kubeadm

~~~sh
# 升级到对应版本
yum install -y kubeadm-1.24.1-0 --disableexcludes=kubernetes
#--disableexcludes=kubernetes表示临时禁用对kubernetes分类的排除，确保即使 yum 配置中设置了对 Kubernetes 相关软件包的排除，这个命令也能够强制安装指定的 kubelet 和 kubectl 版本。这样可以帮助用户安装特定版本的软件，即使这些版本可能与系统中其他部分软件的兼容性有冲突或者其他原因导致它们被默认排除。
kubeadm upgrade plan
kubeadm upgrade apply v1.24.1
~~~

- 升级kubectl和kubelet

~~~sh
yum install -y kubelet-1.24.1-0 kubectl-1.24.1-0 --disableexcludes=kubernetes
~~~

- 修改kubelet参数

~~~sh
vim /var/lib/kubelet/kubeadm-flags.env
#由
KUBELET_KUBEADM_ARGS="--network-plugin=cni --pod-infra-container-image=registry.aliyuncs.com/google_containers/pause:3.6"
#修改成：
KUBELET_KUBEADM_ARGS="--pod-infra-container-image=registry.aliyuncs.com/google_containers/pause:3.6"
#删除了参数--network-plugin=cni，如果不删除此参数则kubelet启动不了

systemctl daemon-reload && systemctl restart kubelet
~~~

## 升级工作节点

- 步骤参考前面升级控制节点的步骤
- 注意在升级kubeadm这一步命令为：

~~~sh
kubeadm upgrade node
~~~

# k8s patch版本升级-1.30.0-1.30.12

## 控制节点

1. 封锁排空控制节点

   ~~~sh
   kubectl cordon rm1
   kubectl drain rm1 --delete-emptydir-data --force --ignore-daemonsets
   ~~~

2. 升级kubeadm

   ~~~sh
   yum install -y kubeadm-'1.31.12-0' --disableexcludes=kubernetes
   kubeadm upgrade plan
   kubeadm upgrade apply v1.31.12
   ~~~

3. 升级kubelet和kubectl

   ~~~sh
   yum install -y kubelet-1.30.12-150500.1.1 kubectl-1.30.12-150500.1.1 --disableexcludes=kubernetes
   systemctl daemon-reload
   systemctl restart kubelet
   # 重启kubelet之后，node才会显示新版本
   kubectl get nodes
   ~~~

4. 恢复节点

   ~~~sh
   kubectl uncordon rm1
   ~~~

## 工作节点

1. 封锁排空

   ~~~sh
   # 控制节点上
   kubectl cordon rn1
   kubectl drain rn1 --delete-emptydir-data --force --ignore-daemonsets
   ~~~

2. 升级kubeadm

   ~~~sh
   # 登录到工作节点上
   yum list --showduplicates kubeadm --disableexcludes=kubernetes
   yum install -y kubeadm-'1.30.12-150500.1.1' --disableexcludes=kubernetes
   kubeadm upgrade node
   ~~~

3. 升级kubelet和kubectl

   ~~~sh
   # 工作节点上
   yum install -y kubelet-1.30.12-150500.1.1 kubectl-1.30.12-150500.1.1 --disableexcludes=kubernetes
   systemctl daemon-reload
   systemctl restart kubelet
   ~~~

4. 恢复节点

   ~~~sh
   # 控制节点上
   kubectl uncordon rn1
   ~~~

# k8s minor版本升级-1.30-1.31

## 控制节点

1. 封锁排空控制节点

   ~~~sh
   kubectl cordon rm1
   kubectl drain rm1 --delete-emptydir-data --force --ignore-daemonsets
   ~~~

2. 升级kubeadm

   ~~~sh
   yum list --showduplicates kubeadm --disableexcludes=kubernetes
   yum install -y kubeadm-'1.31.8-150500.1.1' --disableexcludes=kubernetes
   kubeadm upgrade plan
   kubeadm upgrade apply v1.31.8
   ~~~

   > 如果yum install报错找不到包，两种方式解决：
   >
   > **方法1：**
   >
   > - 可以直接去repo下载rpm文件：https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.31/rpm/x86_64/
   > - 安装命令：`rpm -ivh xxx.rpm`
   >
   > **方法2：**
   >
   > - 添加k8s repo
   >
   >   ~~~sh
   >   cat > /etc/yum.repos.d/kubernetes.repo <<EOF
   >   [kubernetes]
   >   name=Kubernetes
   >   baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.31/rpm/
   >   enabled=1
   >   gpgcheck=1
   >   gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.31/rpm/repodata/repomd.xml.key
   >   EOF
   >   ~~~
   >
   > - 重新build
   >
   >   ~~~sh
   >   yum clean all && yum makecache
   >   ~~~
   >
   > - 查找新版本的包
   >
   >   ~~~sh
   >   yum list --showduplicates kubeadm --disableexcludes=kubernetes
   >   ~~~

3. 升级kubelet和kubectl

   ~~~sh
   yum install -y kubelet-1.31.8-150500.1.1 kubectl-1.31.8-150500.1.1 --disableexcludes=kubernetes
   systemctl daemon-reload
   systemctl restart kubelet
   # 重启kubelet之后，node才会显示新版本
   kubectl get nodes
   ~~~

4. 恢复节点

   ~~~sh
   kubectl uncordon rm1
   ~~~

## 工作节点

1. 封锁排空

   ~~~sh
   # 控制节点上
   kubectl cordon rn1
   kubectl drain rn1 --delete-emptydir-data --force --ignore-daemonsets
   ~~~

2. 升级kubeadm

   ~~~sh
   # 登录到工作节点上
   yum list --showduplicates kubeadm --disableexcludes=kubernetes
   yum install -y kubeadm-'1.31.8-150500.1.1' --disableexcludes=kubernetes
   kubeadm upgrade node
   ~~~

   > 如果yum install报错找不到包，两种方式解决：
   >
   > **方法1：**
   >
   > - 可以直接去repo下载rpm文件：https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.31/rpm/x86_64/
   > - 安装命令：`rpm -ivh xxx.rpm`
   >
   > **方法2：**
   >
   > - 添加k8s repo
   >
   >   ~~~sh
   >   cat > /etc/yum.repos.d/kubernetes.repo <<EOF
   >   [kubernetes]
   >   name=Kubernetes
   >   baseurl=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.31/rpm/
   >   enabled=1
   >   gpgcheck=1
   >   gpgkey=https://mirrors.aliyun.com/kubernetes-new/core/stable/v1.31/rpm/repodata/repomd.xml.key
   >   EOF
   >   ~~~
   >
   > - 重新build
   >
   >   ~~~sh
   >   yum clean all && yum makecache
   >   ~~~
   >
   > - 查找新版本的包
   >
   >   ~~~sh
   >   yum list --showduplicates kubeadm --disableexcludes=kubernetes
   >   ~~~

3. 升级kubelet和kubectl

   ~~~sh
   # 工作节点上
   yum install -y kubelet-1.31.8-150500.1.1 kubectl-1.31.8-150500.1.1 --disableexcludes=kubernetes
   systemctl daemon-reload
   systemctl restart kubelet
   ~~~

4. 恢复节点

   ~~~sh
   # 控制节点上
   kubectl uncordon rn1
   ~~~
