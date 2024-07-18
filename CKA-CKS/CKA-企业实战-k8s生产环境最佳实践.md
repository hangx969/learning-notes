# 如何使用k8s管理应用

## 1 dockerfile制作镜像

- 镜像分为：
  - 基础镜像：centos、rocklinux、ubuntu、debian等
  - 服务镜像：openjdk、nginx、mysql、tomcat等
  - 项目镜像
- java或者go代码需要编译
  - java：mvn编译，生成一个jar包或者war包，放到镜像里
  - go: go build编译，生成一个二进制文件
- php和python可以不用编译
  - py文件直接放到镜像里运行即可

## 2 创建pod

- deployment
- statefulset
- daemonset
- job、cronjob

## 3 数据持久化

- 容器部署过程中一般有三种数据：
  - 容器启动需要的数据，可以是配置文件
  - 启动过程产生的临时数据，需要多个容器共享
  - 运行过程中产生的业务数据
- 采用hostPath、emptyDir、NFS等方式存储或共享

## 4 创建四层代理

- 使用svc的ClusterIP暴露集群内访问，四层代理pod
- svc的名称和IP是由coredns来解析的

## 5 创建七层代理

- 一般是网站类的服务，通过ingress对外暴露应用，通过svc关联pod。
- 通过ingressController实现pod负载均衡
- 支持基于请求头、权重、域名等切分流量，支持TCP/UDP四层和HTTP七层的代理

## 6 日志与监控

- prometheus监控资源状态
- 使用EFK+logstash+kafka收集应用日志

# apiserver优化

kube-apiserver是整个集群的所有请求的入口，apiserver不可用会导致集群失效。可以从以下几个方面优化：

1. apiserver部署多个实例，前端用SLB做负载均衡，提供可用性。
2. 参数优化（/etc/kubernetes/manifests/kube-apiserver.yaml）：--max-mutating-requests-inflight
   - 给定时间内最大的并发请求数，可以调整至3000。默认为200
3. 参数优化：--watch-cache-sizes
   - 某些资源（Pod、Node 等）的监视缓存大小设置，以逗号分隔。 每个资源对应的设置格式：resources#size
   - 集群中node和pod数量较大时可以调大一些，例如：--watch-cache-size=nodes#1000,pods#5000
4. etcd多实例支持：对于不同的object进行分库存储，数据和状态分离，即将event放在单独的etcd实例中。
   - 参数加上--etcd-servers-overrides=/events#https://xxx:3379;https://xxx:3379
   - 也可以将pods, nodes等object也分离在单独的etcd实例中
