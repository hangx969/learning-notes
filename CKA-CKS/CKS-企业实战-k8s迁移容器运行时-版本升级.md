# 将容器运行时从docker迁移到containerd

## 实验环境

- master1、node1
- k8s版本为1.23.1
- OS版本为centos7.9

## 迁移master节点

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

~~~sh
vim /etc/sysconfig/kubelet
KUBELET_EXTRA_ARGS="--container-runtime=remote --runtime-request-timeout=15m --container-runtime-endpoint=unix:///run/containerd/containerd.sock"

systemctl restart kubelet
~~~

## 解锁master

~~~sh
kubectl uncordon master1
~~~

## 验证

~~~sh
kubectl get nodes -owide
~~~

## 迁移worker节点

- 遵循与master相同的步骤