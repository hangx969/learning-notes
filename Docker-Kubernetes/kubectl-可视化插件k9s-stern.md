# k9s

- kubectl可视化插件：https://github.com/derailed/k9s
- 安装指南：https://k9scli.io/topics/install/

## 使用

- vim风格，：来输入资源类型；/来输入filter

# stern

- 查看pod log的插件：https://github.com/stern/stern#installation

## 使用

~~~sh
实时查看当前 Namespace 中所有 Pod 中所有容器的日志
$ stern  .

实时查看 Pod 中指定容器的日志
$ stern envvars --container gateway

实时查看指定命名空间中除指定容器外的所有容器的日志
$ stern -n staging --exclude-container istio-proxy .

实时查看指定时间范围内容器的日志，下面的例子表示是 15 分钟内
$ stern auth -t --since 15m

实时查看指定命名空间中容器的日志
$ stern kubernetes-dashboard --namespace kube-system

实时查看所有命名空间中符合指定标签容器的日志
$ stern --all-namespaces -l run=nginx
~~~

