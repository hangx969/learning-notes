# 前提条件

- 准备storage class提供数据持久化，实验环境下事先部署了nfs-client的sc，并设置为default storage class

> 默认存储类：https://kubernetes.io/zh-cn/docs/concepts/storage/storage-classes/#default-storageclass

# helm配置

- 添加仓库

~~~sh
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm pull prometheus-community/kube-prometheus-stack
tar xzvf kube-prometheus-stack-52.1.0.tgz
cd kube-prometheus-stack
~~~

- 修改配置
