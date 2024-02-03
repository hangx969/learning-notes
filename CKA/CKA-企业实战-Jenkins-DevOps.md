# DevOps

## 持续集成-CI

- 持续集成强调开发人员提交了新代码之后，立刻自动的进行构建、（单元）测试。根据测试结果，我们可以确定新代码和原有代码能否正确地集成在一起。持续集成过程中很重视自动化测试验证结果，对可能出现的一些问题进行预警，以保障最终合并的代码没有问题。
- 常见的持续集成工具：Jenkins、Gitlab CI

## 持续交付

- 持续交付在持续集成的基础上，将集成后的代码部署到更贴近真实运行环境的「类生产环境」（production-like environments）中。交付给质量团队或者用户，以供评审。如果评审通过，代码就进入生产阶段。
- 如果所有的代码完成之后一起交付，会导致很多问题爆发出来，解决起来很麻烦，所以持续集成，也就是没更新一次代码，都向下交付一次，这样可以及时发现问题，及时解决，防止问题大量堆积。

## 持续部署

- 持续部署是指当交付的代码通过评审之后，自动部署到生产环境中。持续部署是持续交付的最高阶段。

- Puppet，SaltStack和Ansible是这个阶段使用的流行工具。

  ![image-20240203174605239](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402031746374.png)

# 基于Jenkins+k8s+Git+DockerHub构建DevOps平台

## 环境准备

- K8S环境：

  - VMware虚拟机，centos7.9
  - root密码为root

  | K8S集群角色 | IP             | 主机名  |
  | ----------- | -------------- | ------- |
  | 控制节点    | 192.168.40.180 | master1 |
  | 工作节点    | 192.168.40.181 | node1   |

## 部署jenkins

### 安装nfs

~~~sh
#两台节点上都安装nfs
yum install nfs-utils -y
systemctl start nfs
systemctl enable nfs
#master1上创建共享目录
mkdir /data/v1 -p
mkdir /data/v2 -p

vim /etc/exports
/data/v1 *(rw,no_root_squash)
/data/v2 *(rw,no_root_squash)

#使配置文件生效
exportfs -arv
~~~

### 安装jenkins

- 创建ns

  ~~~sh
  ~~~

- 安装jenkins（示例就用2.421版本）

