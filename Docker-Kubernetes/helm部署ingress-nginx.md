# 介绍

- 官网地址：https://kubernetes.github.io/ingress-nginx/deploy/


# 下载

~~~sh
curl -LO https://github.com/kubernetes/ingress-nginx/releases/download/helm-chart-$VERSION/ingress-nginx-$VERSION.tgz #helm-chart-4.10.1
~~~

# 配置

- 参照mimer的ado上的配置代码

- 本地集群额外需要修改的地方：

  - controller.service.type，cloud上用的是LoadBalancer，本地集群上External IP会创建不出来；所以直接用NodePort

  - controller.hostNetwork=true，controller.hostPort.enabled=true，开启工作节点主机80 443端口，否则nginx会报404

  - hosts文件还是配置任意工作节点IP

    172.16.183.101 prometheus.hanxux.local alertmanager.hanxux.local grafana.hanxux.local

# 安装

~~~sh
helm upgrade -i ingress-nginx -n ingress-nginx . -f values.yaml --create-namespace
~~~



# 疑问待解决

- 默认的LoadBalancer的配置是否可以在本地集群生成ExternalIP？ -- 在另一个集群上测试看看。
