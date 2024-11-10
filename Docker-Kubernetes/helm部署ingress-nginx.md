# 介绍

- 官网地址：https://kubernetes.github.io/ingress-nginx/deploy/
- 因为K8s中Pod是易变的, Pod IP在更新中会自动修改, 使用Service能使访问入口相对固定, 但是Service IP在集群外不能访问, 要对外提供访问, 只能把Service以NodePort, LoadBalancer这些方式Expose出去, 但是NodePort会与每一个Node主机绑定, 而LoadBalancer要云服务商提供相应的服务(或自己安装)
- Ingress 启动一个独立的Pod来运行七层代理, 可以是 Nginx, Traefik 或者是 Envoy. Ingress Pod会直接代理后端提供服务的Pod, 为了能监听后端Pod的变化, 需要一个 Headless Service 通过Selector选择指定的Pod, 并收集到Pod对应的IP. 一旦后端Pod产生变化, Headless Service 会自动根据变化更改配置文件并重载。如果使用的是 Nginx 类型的 Ingress Pod, 则每次变化后通过reload修改过的配置文件实现规则更新.
- 集群内节点上运行web七层代理所对应的Pod, 由此Pod代理集群内部的Service, Service再把流量转发给集群内部对应的Pod, 这就叫做 Ingress Controller。


# 下载

~~~sh
curl -LO https://github.com/kubernetes/ingress-nginx/releases/download/helm-chart-$VERSION/ingress-nginx-$VERSION.tgz #4.10.1
~~~

# 配置

- 参照mimer的ado上的配置代码

- 本地集群额外需要修改的地方：

  - controller.service.type：cloud上用的是LoadBalancer，本地集群上External IP会创建不出来；所以直接用NodePort

  - controller.hostNetwork=true，controller.hostPort.enabled=true，开启工作节点主机80 443端口，否则nginx会报404

  - hosts文件还是配置任意工作节点IP

    172.16.183.101 prometheus.hanxux.local alertmanager.hanxux.local grafana.hanxux.local

# 安装

~~~sh
helm upgrade -i ingress-nginx -n ingress-nginx . -f values.yaml --create-namespace
~~~
