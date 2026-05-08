---
title: "Helm部署RabbitMQ 高可用集群(HA)"
source: "https://mp.weixin.qq.com/s/6s95cOLmsYis084uefbuBQ"
author:
  - "[[爱踢人生sre]]"
published:
created: 2026-05-08
description:
tags:
  - "clippings"
---
爱踢人生sre *2026年5月7日 23:27*

## 1、搜索并下载 RabbitMQ HA Helm Chart

helm repo add bitnami https://charts.bitnami.com/bitnami

helm repo add stable http://mirror.azure.cn/kubernetes/charts

helm repo add aliyun https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts

helm repo add incubator https://charts.helm.sh/incubator

helm repo update

helm search repo rabbitmq

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/dticnLjiacG4YbfjCgDFznRJhYGoJ9DeZZxKeTb6BtIsZeppWbNTredtjx1pLyzk81fBS9O8d7giatxI5FT6dlibxtibcoAUETdTzLShoW2nhvDk/640?wx_fmt=png&watermark=1&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

下载Chart包:

helm pull aliyun/rabbitmq-ha

解压下载的Chart包：

tar -xf rabbitmq-ha-1.0.0.tgz

cd rabbitmq-ha

## 2、修改配置文件

vim rabbitmq-ha/values.yaml

rabbitmqUsername: rabbitmq

rabbitmqPassword: rabbitmq

image:

repository: docker-0.unsee.tech/rabbitmq

tag: 3.7-alpine

pullPolicy: IfNotPresent

service:

type: NodePort

persistentVolume:

enabled: false # 如果需要开启持久化存储，将此项改为 true

accessModes:

\- ReadWriteMany

size: 8Gi

修改API版本：

找到templates/目录下的以下文件：

role.yaml和rolebinding.yaml：将apiVersion: rbac.authorization.k8s.io/v1beta1替换为apiVersion: rbac.authorization.k8s.io/v1。

statefulset.yaml：将apiVersion: apps/v1beta1 替换为apiVersion: apps/v1

需添加配置：

spec:

selector:

matchLabels:

app: rabbitmq-ha

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

## 3、安装RabbitMQHA

helm install rabbitmq-ha./rabbitmq-ha

查看服务状态：

kubectl get svc

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

查看Pod状态：

kubectl get pod

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

## 4、浏览器访问RabbitMQ管理界面

http://192.168.52.16:30108

登录账号密码为：

用户名：rabbitmq

密码：rabbitmq

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

## 5、结论

通过以上步骤，你成功地在Kubernetes集群上使用Helm部署了RabbitMQ高可用集群。你可以使用浏览器访问管理界面，并根据需要调整配置，处理常见的安装错误。在部署过程中，确保Helm Chart与Kubernetes API版本兼容，才能顺利完成安装。

**微信扫一扫赞赏作者**

k8s · 目录

继续滑动看下一个

爱踢人生sre

向上滑动看下一个