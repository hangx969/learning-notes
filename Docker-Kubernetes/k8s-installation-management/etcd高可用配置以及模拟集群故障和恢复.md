# etcd高可用配置

- kubeadm安装的多master集群中，可以将etcd做成高可用集群

- 在所有master节点上：

  ```sh
  vim /etc/kubernetes/manifests/etcd.yaml
  ```

  ```sh
  - --initial-cluster=master1=https://192.168.40.180:2380
  变成如下：
  - --initial-cluster=master1=https://192.168.40.180:2380,master2=https://192.168.40.181:2380,master3=https://192.168.40.183:2380
  ```

- 修改成功之后重启kubelet：

  ```sh
  systemctl restart kubelet
  ```

- 测试etcd集群是否配置成功：

  ```sh
  docker run --rm -it --net host -v /etc/kubernetes:/etc/kubernetes  registry.cn-hangzhou.aliyuncs.com/google_containers/etcd:3.5.4-0 etcdctl --cert /etc/kubernetes/pki/etcd/peer.crt --key /etc/kubernetes/pki/etcd/peer.key --cacert /etc/kubernetes/pki/etcd/ca.crt member list
  ```

  ```sh
  docker run --rm -it --net host -v /etc/kubernetes:/etc/kubernetes  registry.cn-hangzhou.aliyuncs.com/google_containers/etcd:3.5.4-0 etcdctl --cert /etc/kubernetes/pki/etcd/peer.crt --key /etc/kubernetes/pki/etcd/peer.key --cacert /etc/kubernetes/pki/etcd/ca.crt --endpoints=https://192.168.40.180:2379,https://192.168.40.181:2379,https://192.168.40.182:2379 endpoint health  --cluster
  ```

# 模拟剔除故障节点重新加入

- K8s集群，公司里有3个控制节点和1个工作节点，有一个控制节点master1出问题关机了，修复不成功，然后我们kubectl delete nodes master1把master1移除，移除之后，我把机器恢复了，上架了，我打算还这个机器加到k8s集群，还是做控制节点，如何做？

  1. 把master1这个机器的etcd从etcd集群删除（可以在master2上执行）

  ```sh
  docker run --rm -it --net host -v /etc/kubernetes:/etc/kubernetes  registry.cn-hangzhou.aliyuncs.com/google_containers/etcd:3.5.4-0 etcdctl --cert /etc/kubernetes/pki/etcd/peer.crt --key /etc/kubernetes/pki/etcd/peer.key --cacert /etc/kubernetes/pki/etcd/ca.crt --endpoints=https://192.168.40.181:2379,https://192.168.40.182:2379 member list
  #拿到故障节点上的etcd的id。
  ```

  2. 通过如下命令：删除master1上的etcd

  ```sh
  docker run --rm -it --net host -v /etc/kubernetes:/etc/kubernetes  registry.cn-hangzhou.aliyuncs.com/google_containers/etcd:3.5.4-0 etcdctl --cert /etc/kubernetes/pki/etcd/peer.crt --key /etc/kubernetes/pki/etcd/peer.key --cacert /etc/kubernetes/pki/etcd/ca.crt --endpoints=https://192.168.40.181:2379,https://192.168.40.182:2379 member remove 75e64910a4405073
  ```

  3. 在master1上，创建存放证书目录

  ```sh
  cd /root && mkdir -p /etc/kubernetes/pki/etcd &&mkdir -p ~/.kube/
  ```

  4. 把其他控制节点的证书拷贝到master1上

  ```sh
  scp /etc/kubernetes/pki/ca.crt master1:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/ca.key master1:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/sa.key master1:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/sa.pub master1:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/front-proxy-ca.crt master1:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/front-proxy-ca.key master1:/etc/kubernetes/pki/
  scp /etc/kubernetes/pki/etcd/ca.crt master1:/etc/kubernetes/pki/etcd/
  scp /etc/kubernetes/pki/etcd/ca.key master1:/etc/kubernetes/pki/etcd/
  ```

  5. 把master1加入到集群

  ```sh
  #其他节点上查看加入集群的命令
  kubeadm token create --print-join-command
  #在master1上执行，使其加入集群。
  ```

# etcd性能分析

- 首先安装etcdctl

~~~sh
#下载etcd-v3.4.13-linux-amd64.tar.gz
wget https://github.com/etcd-io/etcd/releases/download/v3.4.13/etcd-v3.4.13-linux-amd64.tar.gz
tar zxvf etcd-v3.4.13-linux-amd64.tar.gz
cp etcd-v3.4.13-linux-amd64/etcdctl /usr/bin/
~~~

- 当etcd指标显示高延迟时，查看原因：

~~~sh
# 检查 etcd 指标
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint status --write-out=table
~~~

