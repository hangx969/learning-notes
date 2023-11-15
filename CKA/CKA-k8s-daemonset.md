# DaemonSet控制器：概念、原理

## 概念

- DaemonSet控制器能够确保k8s集群所有的节点都运行一个相同的pod副本，当向k8s集群中增加node节点时，这个node节点也会自动创建一个pod副本，当node节点从集群移除，这些pod也会自动删除；删除Daemonset也会删除它们创建的pod。

## 原理

- daemonset的控制器会监听kuberntes的daemonset对象、pod对象、node对象，这些被监听的对象之变动，就会触发syncLoop循环让kubernetes集群朝着daemonset对象描述的状态进行演进。

## 场景

- 在集群的每个节点上运行存储，比如：glusterd 或 ceph。
- 在每个节点上运行日志收集组件，比如：flunentd 、 logstash、filebeat等。
- 在每个节点上运行监控组件，比如：Prometheus、 Node Exporter 、collectd等。

## yaml编写