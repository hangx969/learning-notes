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
- 集群内节点上运行web七层代理nginx所对应的Pod, 由nginx Pod代理到集群内部的Service, Service再把流量转发给集群内部对应的Pod, 这就叫做 Ingress Controller。


# 下载

~~~sh
# curl -LO https://github.com/kubernetes/ingress-nginx/releases/download/helm-chart-$VERSION/ingress-nginx-$VERSION.tgz #4.10.1
helm repo add --force-update ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update ingress-nginx
helm pull ingress-nginx/ingress-nginx --version "${INGRESS_NGINX_VERSION#helm-chart-}" #4.10.1
~~~

# 配置hostnetwork模式

- [Bare-metal considerations - Ingress-Nginx Controller](https://kubernetes.github.io/ingress-nginx/deploy/baremetal/#via-the-host-network)

## hostnetwork

- `controller.service.type：cloud`上用的是LoadBalancer，本地虚拟机集群上External IP会创建不出来；所以disable掉暂时不需要service。
- `controller.hostNetwork=true，controller.hostPort.enabled=true`，ingress-nginx pod用宿主机网络栈，并且开启节点宿主机80、443端口，否则nginx会报404

## DNS policy

[DNS for Services and Pods | Kubernetes](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/#pod-s-dns-policy)

- `controller.dnsPolicy: ClusterFirstWithHostNet`，让ingress-nginx pod可以用kube-dns解析集群内的svc
- 虚拟机和虚拟机外面的hosts文件还是配置任意工作节点IP

> 注意：
>
> 1. hosts文件里面写哪个节点的IP取决于ingress-controller的pod调度到了哪个节点上面，保险起见可以这样做：
>
> - `controller.sutoscaling`里面设置至少3个replica，
>
> - 或者replicaCount设置为3。
>
> - 或者干脆直接把controller type设为daemonset
>
>   这样每个host都有pod可以接收80端口的请求。
>
> 2. 当 Pod 设置 hostNetwork: true 时：
>
>    - Pod 会使用宿主机的网络命名空间
>
>    - 默认情况下，Pod 会使用宿主机的 DNS 配置（/etc/resolv.conf）
>
>      这意味着 Pod 无法解析 Kubernetes 集群内部的服务名称，如：
>
>      kubernetes.default.svc.cluster.local
>
>      oauth2-proxy.oauth2-proxy.svc.cluster.local
>
>    - ClusterFirstWithHostNet 的解决方案：设置 dnsPolicy: ClusterFirstWithHostNet 后：
>
>      - 优先使用 CoreDNS（集群内部 DNS）来解析域名
>      - 能够解析 Kubernetes 集群内部服务
>      - 如果集群 DNS 解析失败，则回退到宿主机的 DNS

# 安装

~~~sh
helm upgrade -i ingress-nginx -n ingress-nginx . -f values.yaml --create-namespace
~~~

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

# hostnetwork的流量代理过程

基于当前的 ingress-nginx 配置，从 Windows 电脑访问 `grafana.hanxux.local` 到达 K8s 后端 Pod 的完整请求流程：

1. **DNS 解析阶段**

```sh
Windows 电脑 → DNS 查询 grafana.hanxux.local
```
- Windows 电脑上的浏览器发起对 `grafana.hanxux.local` 的 DNS 查询
- 需要在 Windows 的 `hosts` 文件或 DNS 服务器中配置该域名指向 VMware 虚拟机的 IP 地址
- 例如：`192.168.x.x grafana.hanxux.local`（虚拟机的 IP）

2. **网络路由阶段**

```sh
Windows 电脑 → VMware 虚拟网络 → K8s 节点
```
- 请求通过 VMware 的虚拟网络接口发送到虚拟机
- 由于您配置了 `hostNetwork: true`，ingress-nginx Pod 直接使用宿主机的网络栈

3. **Ingress Controller 接收阶段**

**请求处理流程：**

```sh
Windows:浏览器 → VMware虚拟网络 → K8s节点:80端口 → ingress-nginx Pod
```

4. **Ingress 规则匹配阶段**

- ingress-nginx Controller 接收到请求后，检查 HTTP Host 头部（`grafana.hanxux.local`）
- 根据 Ingress 资源中定义的规则进行匹配
- 找到对应的后端服务配置

5. **DNS 解析后端服务阶段**

由于配置了：
```yaml
dnsPolicy: ClusterFirstWithHostNet
```

- ingress-nginx Pod 使用 K8s 集群的 DNS（CoreDNS）来解析后端服务名
- 例如解析 `grafana-service.monitoring.svc.cluster.local` 到对应的 Cluster IP

6. **负载均衡转发阶段**

```sh
ingress-nginx → Grafana Service → Grafana Pod
```

- ingress-nginx 根据 Ingress 规则将请求转发给对应的 Service
- Service 通过 iptables/ipvs 规则进行负载均衡
- 最终请求到达 Grafana Pod

**完整的数据流路径**

```sh
[Windows 电脑:浏览器]
        ↓ HTTP请求 grafana.hanxux.local
[VMware 虚拟网络层]
        ↓ 网络包转发
[K8s节点:80端口] (hostNetwork模式)
        ↓ 端口绑定
[ingress-nginx Pod] (DaemonSet)
        ↓ Host头匹配 + 路由规则
[Grafana Service] (ClusterIP)
        ↓ 负载均衡
[Grafana Pod] (目标容器)
```

**关键配置的作用**

1. **`hostNetwork: true`** - 让 ingress-nginx 直接使用宿主机网络，避免额外的网络层转发
2. **`hostPort.enabled: true`** - 直接绑定宿主机的 80/443 端口
3. **`kind: DaemonSet`** - 确保每个节点都有 ingress controller
4. **`service.enabled: false`** - 不需要 Service，因为使用了 hostNetwork 模式
5. **`dnsPolicy: ClusterFirstWithHostNet`** - 确保能正确解析集群内服务名

这种配置特别适合单节点或裸机部署，能够提供最直接的网络路径和最佳性能。

# Nodeport模式的流量代理过程

上面是采用hostNetwork模式，请求直接到达宿主机80/443端口，被ingress-controller pod接收。还可以给ingress controller开一个NodePort service，请求先到NodePort Service再给ingress-controller。

需要将 `values.yaml` 修改为：

````yaml
controller:
  # ...existing code...
  
  # 禁用 hostNetwork 模式
  hostNetwork: false
  # 移除 hostPort 配置
  # hostPort:
  #   enabled: true
  #   ports:
  #     http: 80
  #     https: 443
  
  # 启用 Service 并配置为 NodePort
  service:
    enabled: true
    type: NodePort
    ports:
      http: 80
      https: 443
    nodePorts:
      http: 30080    # 指定 NodePort 端口
      https: 30443   # 指定 NodePort 端口
  
  # DNS 策略可以改回默认值
  dnsPolicy: ClusterFirst
  
  # ...existing code...
````

原有 hostNetwork 模式流程：

```
Windows电脑 → VMware虚拟网络 → K8s节点:80 → ingress-nginx Pod
```

NodePort 模式流程：

```
Windows电脑 → VMware虚拟网络 → K8s节点:30080 → NodePort Service → ingress-nginx Pod:80
```

**详细实现步骤**：

1. **DNS 配置调整**

在 Windows 的 `hosts` 文件中，需要指定端口：
```sh
# 方式1：在 hosts 文件中仍然指向虚拟机IP（需要端口转发）
192.168.x.x grafana.hanxux.local

# 方式2：直接在浏览器中访问带端口的URL
http://grafana.hanxux.local:30080
```

2. **端口转发解决方案**

由于域名访问默认使用 80/443 端口，有几种方案：

**方案A：使用端口转发（推荐）**
在 VMware 虚拟机或宿主机上配置端口转发：

```bash
# 在 Linux 虚拟机上使用 iptables
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 30080
sudo iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 30443
```

**方案B：在 Windows 上使用 netsh**

```powershell
# 在 Windows 上配置端口转发
netsh interface portproxy add v4tov4 listenport=80 listenaddress=0.0.0.0 connectport=30080 connectaddress=192.168.x.x
netsh interface portproxy add v4tov4 listenport=443 listenaddress=0.0.0.0 connectport=30443 connectaddress=192.168.x.x
```

3. **网络流量路径**

```
[Windows 电脑:浏览器] 
        ↓ HTTP请求 grafana.hanxux.local:80
[端口转发规则] 
        ↓ 80 → 30080 转发
[VMware 虚拟网络层]
        ↓ 网络包转发到 30080
[K8s节点:30080] (NodePort)
        ↓ iptables/kube-proxy 规则
[ingress-nginx Service] (ClusterIP)
        ↓ 负载均衡
[ingress-nginx Pod:80] (容器端口)
        ↓ Host头匹配 + 路由规则
[Grafana Service] (ClusterIP)
        ↓ 负载均衡
[Grafana Pod] (目标容器)
```

**NodePort 模式的优缺点**

优点：

1. **标准 K8s 模式** - 更符合 Kubernetes 最佳实践
2. **端口隔离** - 避免与宿主机其他服务的端口冲突
3. **更好的可移植性** - 可以轻松迁移到云环境
4. **支持多副本** - 不受 hostNetwork 的单节点限制

缺点：

1. **额外的网络跳转** - 性能略有损失
2. **端口映射复杂性** - 需要配置端口转发
3. **端口范围限制** - NodePort 默认范围 30000-32767

特点：

1. **保持现有的 hostNetwork 模式** - 对于单节点开发环境，性能和简洁性更佳
2. **如果需要 NodePort 模式** - 使用方案A的 iptables 端口转发，配置简单且稳定

# 集成oauth2proxy

- 给ingress添加annotations：

~~~yaml
annotations:
  nginx.ingress.kubernetes.io/auth-url: "https://oauth2proxy.hanxux.local/oauth2/auth"
  nginx.ingress.kubernetes.io/auth-signin: "https://oauth2proxy.hanxux.local/oauth2/start?rd=https%3A%2F%2Fgrafana.hanxux.local"
~~~

- ingress可以配置的annotations：https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/，可以实现其他流量控制等功能。

# 

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

