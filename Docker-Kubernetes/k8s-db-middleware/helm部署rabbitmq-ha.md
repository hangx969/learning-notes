---
title: Helm部署RabbitMQ高可用集群
tags:
  - kubernetes
  - middleware
  - rabbitmq
aliases:
  - rabbitmq-ha
---

# Helm 部署 RabbitMQ 高可用集群（HA）

## 搜索并下载 RabbitMQ HA Helm Chart

~~~sh
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable http://mirror.azure.cn/kubernetes/charts
helm repo add aliyun https://kubernetes.oss-cn-hangzhou.aliyuncs.com/charts
helm repo add incubator https://charts.helm.sh/incubator
helm repo update

helm search repo rabbitmq
~~~

下载 Chart 包并解压：

~~~sh
helm pull aliyun/rabbitmq-ha
tar -xf rabbitmq-ha-1.0.0.tgz
cd rabbitmq-ha
~~~

## 修改配置文件

~~~sh
vim rabbitmq-ha/values.yaml
~~~

关键配置项：

~~~yaml
rabbitmqUsername: rabbitmq
rabbitmqPassword: rabbitmq

image:
  repository: docker-0.unsee.tech/rabbitmq
  tag: 3.7-alpine
  pullPolicy: IfNotPresent

service:
  type: NodePort

persistentVolume:
  enabled: false  # 如果需要开启持久化存储，将此项改为 true
  accessModes:
    - ReadWriteMany
  size: 8Gi
~~~

### 修改 API 版本（兼容新版 K8s）

找到 `templates/` 目录下的以下文件，修改 API 版本：

- `role.yaml` 和 `rolebinding.yaml`：`apiVersion: rbac.authorization.k8s.io/v1beta1` → `apiVersion: rbac.authorization.k8s.io/v1`
- `statefulset.yaml`：`apiVersion: apps/v1beta1` → `apiVersion: apps/v1`

同时需在 StatefulSet 的 spec 中添加 selector：

~~~yaml
spec:
  selector:
    matchLabels:
      app: rabbitmq-ha
~~~

## 安装 RabbitMQ HA

~~~sh
helm install rabbitmq-ha ./rabbitmq-ha
~~~

查看服务和 Pod 状态：

~~~sh
kubectl get svc
kubectl get pod
~~~

## 访问 RabbitMQ 管理界面

通过 NodePort 访问管理界面：

~~~
http://<节点IP>:<NodePort>
~~~

默认登录凭证：

- 用户名：`rabbitmq`
- 密码：`rabbitmq`

## 注意事项

- 部署过程中需确保 Helm Chart 与 Kubernetes API 版本兼容（旧版 Chart 需手动修改 apiVersion）
- 生产环境建议开启 `persistentVolume.enabled: true` 以保证数据持久化
- 生产环境应修改默认账号密码
