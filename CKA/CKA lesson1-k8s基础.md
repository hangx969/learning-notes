# 第二章 实验环境搭建

## 虚拟机搭建

- VM OS 版本：CentOS 7.6 - 7.9

- 2G内存、2vcpu

## docker安装

https://docs.docker.com/engine/install/centos/

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
```

