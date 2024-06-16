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
