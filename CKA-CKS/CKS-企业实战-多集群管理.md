# 多集群管理

- 在实际生产环境中，往往需要维护多个k8s集群，如何实现在一台机器上操作多个集群。通过设置kubeconfig文件来实现。

# 配置kubeconfig

- 假设存在两套集群，集群1：master1/node1、集群2：master2/node2。现在在master1上配置访问master2的集群

- 查看两个集群

~~~sh
kubectl config view
#或者直接查看config文件
cat /root/.kube/config
~~~

- 在集群1上添加集群2的信息

~~~sh
#添加cluster，在集群1上
kubectl config set-cluster k8smaster2 --server=https://192.168.40.185:6443 --insecure-skip-tls-verify=true

#添加user
##集群2上获取token
kubeadm token create --print-join-command
##集群1上设置token
kubectl config set-credentials k8smaster2-user --token=clknqa.km25oi82urcuja9u

#添加context，集群1上
kubectl config set-context k8smaster2-context --cluster=k8smaster2  --user=k8smaster2-user

#可以在集群1上通过切换context来操作
kubectl config use-context k8smaster2-context
~~~

