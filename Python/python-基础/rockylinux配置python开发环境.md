---
title: RockyLinux 配置 Python 开发环境
tags:
  - python/setup
  - python/linux
  - linux/rockylinux
aliases:
  - RockyLinux Python 环境配置
  - Linux 安装 Python
date: 2026-04-16
---

# RockyLinux 配置 Python 开发环境

## 安装python

1. 安装前置包

```sh
yum install openssl-devel bzip2-devel expat-devel gdbm-devel readline-devel sqlite-devel libffi-devel gcc gcc-c++ make cmake lrzsz -y
```

2. python官网下载python源码包:https://www.python.org/downloads ,选择Gzipped source tarball版本

```sh
wget https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tgz
```

3. 编译安装

```sh
tar zxvf Python-3.12.5.tgz
mv Python-3.12.5 /usr/local/
cd /usr/local/Python-3.12.5/
./configure
make && make install
```

4. 配置环境变量

```sh
echo 'export PATH=/usr/local/bin:$PATH' >> ~/.bashrc
# 把export PATH=/usr/local/bin:$PATH 命令写入到当前用户的~/.bashrc,使得每次开启新session时,/usr/local/bin 目录会被自动添加到 PATH 中
source ~/.bashrc
ln -s /usr/local/bin/python3.12 /usr/bin/python
```

5. 验证安装版本

```sh
python -V
```

> [!tip] 升级版本
> 升级版本时,直接下载新版安装包,编译安装,软链接到新版路径即可。

相关内容参见 [[windows配置python开发环境|Windows 配置 Python 开发环境]] 和 [[python包管理工具-uv|Python 包管理工具 uv]]
