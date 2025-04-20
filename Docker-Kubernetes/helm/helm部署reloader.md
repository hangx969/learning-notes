# 介绍

- 官网地址：https://github.com/stakater/Reloader

- 教程：https://zhuanlan.zhihu.com/p/669681298

- github release： https://github.com/stakater/Reloader/releases

- artifact hub： https://artifacthub.io/packages/helm/stakater/reloader

- configMap和secret有两种方式赋值：

  - env系统变量赋值：不支持热更新，要更新就得删除旧pod滚动更新。
  - volume挂载赋值：k8s原生就支持热更新，不用重启pod，由kubelet来实现。

- 开源工具Reloader，通过 watch ConfigMap 和 Secret，一旦发现对象更新，就自动触发对 Deployment 或 StatefulSet 等工作负载对象进行滚动升级。

- Reloader 默认是监控所有命名空间中的资源，如果只是需要监控单一命名空间，那么需要在使用 Helm 安装的时候覆盖配置，命令如下：

  ~~~sh
  #--set reloader.watchGlobally=false --namespace test
  #这样就只会监控test名称空间下面
  ~~~

- 也可以配置ConfigMap和Secret的某一个来监控，但是不能两个**都不监控**，reloader pod会出异常。如果暂时都不想监控，可以将副本数设置为0。


# 下载

~~~sh
helm repo add stakater https://stakater.github.io/stakater-charts
helm repo update stakater
helm pull stakater/reloader --version 1.0.115
~~~

# 配置

- watchGlobally: true --> 配置为全部监测即可


# 安装

~~~sh
helm upgrade -i reloader -n reloader --create-namespace . -f values.yaml
~~~

# 使用

- 监控所有configMap和secret并自动更新

  ~~~yaml
  #在deployment的configMap中添加annotation
  kind: Deployment
  metadata:
    name: foo
    annotations:
      reloader.stakater.com/auto: "true"
  spec:
  ...
  #这样 Reloader 就会发现这个 Pod 中引用的所有 ConfigMap 或者 Secret，并且在这两个资源更新的时候滚动更新这个 Pod。
  #没有添加此项注释的就不会被自动滚动更新
  ~~~

- 监控部分configMap/Secret并自动更新

  ~~~yaml
  #如果不需要一个pod下所有的configMap/Secret更新都触发自动重启，仅需要指定的configMap/Secret，给deployment加annotation：
  kind: Deployment
  metadata:
    annotations:
      reloader.stakater.com/search: "true"
  spec:
  ...
  
  #同时configMap也加上annotation
  kind: ConfigMap
  metadata:
    annotations:
      reloader.stakater.com/match: "true"
  data:
    key: value
  ...
  #注：对volume和env两种方式的configMap都生效
  ~~~

- 监控指定的configMap并自动更新

  ~~~yaml
  #deployment的annotation配置;
  kind: Deployment
  metadata:
    annotations:
      configmap.reloader.stakater.com/reload: "foo-configmap,bar-configmap,baz-configmap"
  spec:
  ...
  ~~~


> 注：
>
> - 需要注意的一点是，`reloader.stakater.com/search` 和 `reloader.stakater.com/auto` 不能同时生效。如果已经指定了 `reloader.stakater.com/auto: "true"` 这个注释，那么这个 Pod 就会在任何一个 ConfigMap 或 Secret 改变时开始滚动更新，不论是否还有其他的相关注释
