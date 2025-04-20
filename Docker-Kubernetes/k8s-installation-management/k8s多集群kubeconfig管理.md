# 多集群管理

- 在实际生产环境中，往往需要维护多个k8s集群，如何实现在一台机器上操作多个集群。通过设置kubeconfig文件来实现。

# 合并多个kubeconfig文件

## 方案1：kubectl config命令

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
kubectl config set-credentials k8smaster2-user --token=xxx

#添加context，集群1上
kubectl config set-context k8smaster2-context --cluster=k8smaster2  --user=k8smaster2-user

#可以在集群1上通过切换context来操作
kubectl config use-context k8smaster2-context
~~~

## 方案2：`KUBECONFIG` 环境变量指向多个文件 

通过在 KUBECONFIG 环境变量中指定多个文件，可以临时将 KUBECONFIG 文件组合在一起，并在 `kubectl `中使用。如下，那么kubeconfig 是在内存中做的合并：

```sh
export KUBECONFIG=~/.kube/config:~/another-config-file-location 
```

## 方案3：`flatten`

```
export KUBECONFIG=~/.kube/config:~/anotherconfig 
kubectl config view --flatten
```

- `--flatten`：将生成的 kubeconfig 文件扁平化为自包含的输出（用于创建可移植的kubeconfig 文件）

- 如果需要，还可以管道输出到另外一个新文件。

## 方案3：kubectl插件kconfig

`kubectl` 有个 `krew` 插件包管理器，可以通过 `krew` 安装 `konfig` 实用插件来管理 kubeconfig。

安装：

~~~sh
kubectl krew install konfig
~~~

`krew `插件 `konfig` 可以帮助你管理 `~/.kube/config`，使用 `konfig` 插件的语法如下:

```
kubectl konfig import -s new.yaml
```
