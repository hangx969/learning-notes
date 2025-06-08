# 介绍

- 官网地址：
  - https://kubernetes.github.io/ingress-nginx/deploy/
  - releases page: https://github.com/kubernetes/ingress-nginx/releases
  - artifactHub: https://artifacthub.io/packages/helm/ingress-nginx/ingress-nginx

- azure文档：
  - https://learn.microsoft.com/en-us/troubleshoot/azure/azure-kubernetes/load-bal-ingress-c/create-unmanaged-ingress-controller?tabs=azure-cli#create-an-ingress-controller-using-an-internal-ip-address
  - https://learn.microsoft.com/en-us/previous-versions/azure/aks/ingress-tls?tabs=azure-cli#install-cert-manager

- 因为K8s中Pod是易变的, Pod IP在更新中会自动修改, 使用Service能使访问入口相对固定, 但是Service IP在集群外不能访问, 要对外提供访问, 只能把Service以NodePort, LoadBalancer这些方式Expose出去, 但是NodePort会与每一个Node主机绑定, 而LoadBalancer要云服务商提供相应的服务 (或自己安装)
- Ingress 启动一个独立的Pod来运行七层代理, 可以是 Nginx, Traefik 或者是 Envoy. Ingress Pod会直接代理后端提供服务的Pod, 为了能监听后端Pod的变化, 需要一个 Headless Service 通过Selector选择指定的Pod, 并收集到Pod对应的IP. 一旦后端Pod产生变化, Headless Service 会自动根据变化更改配置文件并重载。如果使用的是 Nginx 类型的 Ingress Pod, 则每次变化后通过reload修改过的配置文件实现规则更新.
- 集群内节点上运行web七层代理所对应的Pod, 由此Pod代理集群内部的Service, Service再把流量转发给集群内部对应的Pod, 这就叫做 Ingress Controller。


# 下载

~~~sh
# curl -LO https://github.com/kubernetes/ingress-nginx/releases/download/helm-chart-$VERSION/ingress-nginx-$VERSION.tgz #4.10.1
helm repo add --force-update ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update ingress-nginx
helm pull ingress-nginx/ingress-nginx --version "${INGRESS_NGINX_VERSION#helm-chart-}" #4.10.1
~~~

# 配置

- 参照mimer的ado上的配置代码

- 本地集群额外需要修改的地方：

  - `controller.service.type：cloud`上用的是LoadBalancer，本地集群上External IP会创建不出来；所以直接用NodePort

  - `controller.hostNetwork=true，controller.hostPort.enabled=true`，开启工作节点主机80 443端口，否则nginx会报404

  - hosts文件还是配置任意工作节点IP

    172.16.183.101 prometheus.hanxux.local alertmanager.hanxux.local grafana.hanxux.local
    
    > 注意：hosts文件里面写哪个host的IP取决于ingress-controller的pod调度到了哪个host上面，保险起见需要把`controller.sutoscaling`里面设置成3个replica,这样每个host都有pod可以接收80端口的请求。

# 安装

~~~sh
helm upgrade -i ingress-nginx -n ingress-nginx . -f values.yaml --create-namespace
~~~

# 集成oauth2proxy

- 给ingress添加annotations：

~~~yaml
annotations:
  nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
  nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fgrafana.hanxux.local"
~~~

- ingress可以配置的annotations：https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/，可以实现其他流量控制等功能。

# 配置HTTPS访问

## 自签证书

- 以grafana为例。

- 首先部署出certmanager --> 创建clusterissuer --> 创建给grafana ingress https的secret --> helm values.yaml的grafana ingress tls部分配置secret、host

- 创建secret

~~~yaml
tee certificate-grafana.yaml <<'EOF'
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: cert-grafana
  namespace: monitoring
spec:
  secretName: grafana-tls-cert-secret
  privateKey:
    rotationPolicy: Always
  commonName: grafana.hanxux.local
  dnsNames:
    - grafana.hanxux.local
  usages:
    - digital signature
    - key encipherment
    - server auth
  issuerRef:
    name: selfsigned
    kind: ClusterIssuer
EOF
~~~

- kube-prometheus-stack的values配置

~~~yaml
    ## TLS configuration for grafana Ingress
    ## Secret must be manually created in the namespace
    ##
    tls:
      - secretName: cert-grafana
        hosts:
        - grafana.hanxux.local
~~~

- https访问hostname即可，由于lab用的是自签证书，所以浏览器会报连接不安全。

## Letsencrypt证书

- 参考azure文档：https://learn.microsoft.com/en-us/previous-versions/azure/aks/ingress-tls?tabs=azure-cli#install-cert-manager

# 实战--流量复制/流量镜像

流量镜像（Traffic Mirror）功能应用于以下两个场景：

- 在系统进行重大重构或者发布新功能时，可以通过将线上的应用流量镜像到指定的线下环境来对新系统进行仿真测试。

- 线上系统遇到性能瓶颈，要快速地定位出问题时，可以采用流量镜像的方式来将应用的真实流量引导到线下环境来进行问题定位。

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202501192211142.png" alt="image-20250119221126026" style="zoom:50%;" />

## 准备步骤

1. 在prod集群部署应用，在staging集群部署相同应用
2. 获取应用域名信息
   - prod：www.product-nginx.com
   - staging:www.staging-nginx.com

## 流量镜像配置

### 说明

1. 将K8s Product Cluster中应用100%的访问流量镜像到K8s Stage Cluster中应用服务上，即将所有访问域名"www.product-nginx.com"的请求复制一份转发到"www.stage-nginx.com"


2. K8s Stage Cluster Ingress仅作为复制流量的接收方，不做任何配置修改

3. 在将K8s Product Cluster中应用的访问流量镜像到K8s Stage Cluster中对应的应用服务后，客户端只会收到K8s Product Cluster中的请求响应，K8s Stage Cluster中的请求响应会被丢弃。

### 步骤1-配置nging-ingress configMap

在nginx-ingress-controller configmap中增加以下内容，配置多个流量接收目标：

~~~yaml
kubectl get configmap -n kube-system
kubectl edit configmap nginx-ingress-controller -n kube-system

#追加以下配置
data:
  http-snippet: |
    split_clients "$date_gmt" $mirror_servers1 {
       100%    www.stage-nginx1.com;
    }
    split_clients "$date_gmt" $mirror_servers2 {
       100%    www.stage-nginx2.com;
    }
~~~

配置多个接收目标并且每个目标流量都是100%：

1. 流量百分比取值范围：(0, 100]，百分比总和必须不大于100%。
2. 支持同时配置多个不同的复制流量接收目标应用。

> Q：这里是在哪个环境的ingress操作的？？

### 步骤2-配置prod的ingress

通过configuration-snippet和server-snippet修改源Ingress，增加应用的流量镜像配置。

~~~yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ingress
  annotations:
    nginx.ingress.kubernetes.io/configuration-snippet: |
        # 配置多个接收目标
        mirror /mirror1;
        mirror /mirror2;
    nginx.ingress.kubernetes.io/server-snippet: |
        # 配置第1个接收复制的集群
        location = /mirror1 {
            internal;
            # 不打印mirror请求日志
            #access_log off;
            # 设置proxy_upstream_name，格式必须为[Namespace]-[BackendServiceName]-[BackendServicePort]
            set $proxy_upstream_name    "default-nginx-service-80";
            # 自定义字符串，会作为请求头X-Shadow-Service值传给mirror server
            set $shadow_service_name    "nginx-product-service";
            proxy_set_header X-Shadow-Service  $shadow_service_name;
            proxy_set_header Host $mirror_servers1; 
            proxy_pass http://$mirror_servers1$request_uri;
        }
        # 配置第2个接收复制的集群
        location = /mirror2 {
            internal;
            # 不打印mirror请求日志
            #access_log off;
            # 设置proxy_upstream_name，格式必须为[Namespace]-[BackendServiceName]-[BackendServicePort] 
            set $proxy_upstream_name    "default-nginx-service-80";
            # 自定义字符串，会作为请求头X-Shadow-Service值传给mirror server
            set $shadow_service_name    "nginx-product-service";
            proxy_set_header X-Shadow-Service  $shadow_service_name;
            proxy_set_header Host $mirror_servers2;
            proxy_pass http://$mirror_servers2$request_uri;
        }
spec:
  rules:
  - host: www.product-nginx.com
    http:
      paths:
      - path: /
        backend:
          service:
            name: nginx-product
            port:
              number: 80
        pathType: ImplementationSpecific
~~~

### 修改coredns hosts配置

在K8s Product Cluster集群coredns插件中添加需要发送流量镜像的域名解析

~~~yaml
kubectl get configmap -n kube-system
kubectl edit configmap coredns -n kube-system

data:
  Corefile: |-
    .:5353 {
        bind {$POD_IP}
        # 添加服务域名解析
        hosts {
            192.168.4.16 www.stage-nginx1.com
            192.168.4.53 www.stage-nginx2.com
            fallthrough
        }
...
~~~

