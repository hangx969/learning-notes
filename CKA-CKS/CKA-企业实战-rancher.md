# Rancher介绍

- Rancher是一个开源的企业级多集群Kubernetes管理平台，实现了Kubernetes集群在混合云+本地数据中心的集中部署与管理，以确保集群的安全性，加速企业数字化转型。

- Rancher官方文档：https://docs.rancher.cn/

- Rancher和k8s的区别
  - Rancher和k8s都是用来作为容器的调度与编排系统。但是rancher不仅能够管理应用容器，更重要的一点是能够管理k8s集群。Rancher2.x底层基于k8s调度引擎，通过Rancher的封装，用户可以在不熟悉k8s概念的情况下轻松的通过Rancher来部署容器到k8s集群当中。

# Rancher部署

## 实验机器准备

- Rancher VM
  - 192.168.40.138；hostname：rancher；memory：6G；cpu：6vCPU

- K8S VM
  - version：1.23.1
  - master1：192.168.40.180
  - node1：192.168.40.181

## 安装前准备

### 配置主机名

~~~sh
#配置主机名
hostnamectl set-hostname rancher
#rancher、master1、node1添加host
vim /etc/hosts
192.168.40.180   master1
192.168.40.181   node1
192.168.40.138   rancher
~~~

### 配置ssh互信

~~~sh
ssh-keygen
ssh-copy-id master1 #node1 rancher
~~~

