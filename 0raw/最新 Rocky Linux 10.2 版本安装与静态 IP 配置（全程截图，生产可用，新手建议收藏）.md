---
title: "最新 Rocky Linux 10.2 版本安装与静态 IP 配置（全程截图，生产可用，新手建议收藏）"
source: "https://mp.weixin.qq.com/s/UGV_VeKzduyOfyHkkxs2SQ"
author:
  - "[[真成]]"
published:
created: 2026-06-05
description: "Rocky Linux 是 RHEL（红帽企业 Linux）1:1 二进制兼容的开源免费发行版，由 CentOS 项目创始人 Gregory Kurtzer 在 2020 年创立；起因：红帽宣布停止 CentOS 稳定版（CentOS8/9 转为滚动流 CentOS Stream），社区为替代传统稳定 CentOS 诞生 Rocky Linux，"
tags:
  - "clippings"
---
真成 *2026年6月3日 08:00*

**[关注领取运维自学路线资料](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247488479&idx=1&sn=b09902d7bdc17ed4de667075840e3504&scene=21#wechat_redirect) | [进百人交流群](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247484443&idx=1&sn=39c66a908163621ff255280d837f9e97&scene=21#wechat_redirect) | [学企业级运维项目](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247490328&idx=1&sn=672e5579e954d7d8ef9dd6edd6670de0&scene=21#wechat_redirect)**

Rocky Linux 是 **RHEL（红帽企业 Linux）1:1 二进制兼容的开源免费发行版** ，由 CentOS 项目创始人 **Gregory Kurtzer** 在 2020 年创立；

起因：红帽宣布停止 CentOS 稳定版（CentOS8/9 转为滚动流 CentOS Stream），社区为替代传统稳定 CentOS 诞生 Rocky Linux， **完全免费、无订阅费、兼容 RHEL 官方软件** 。

## Rocky Linux 10.2 系统安装

Rocky Linux 10.2 ISO 镜像文件下载：https://rockylinux.org/zh-CN/download

Rocky Linux 三种 ISO 镜像区别（DVD / Minimal / Boot）

1）Minimal ISO（最小化镜像｜生产服务器首选） 体积小，仅几百 MB；系统基础最小安装包内置在镜像里。

**安装特点** ： **断网也能完成最小化系统安装，只有内核 + 基础命令 + 系统组件，无桌面、无多余软件**

✅ 适用：生产服务器

2）DVD ISO（完整版 DVD 镜像） 体积最大（8G 左右），内置 BaseOS+AppStream 全套 rpm 软件源

**安装特点** ： **完全离线安装，安装时可以自选桌面环境 (GNOME)、开发包、数据库、工具集，不需要联网下载包** 。装好系统后，本机光盘可当本地 yum 源。

✅ 适用：离线机房不能联网、需要装桌面 / 大量预装软件、本地自建源

3）Boot ISO（网络引导镜像｜网装专用）

体积最小（几十-几百 MB），只有引导程序，镜像里没有任何系统安装包。

**安装特点** ：开机引导后，必须配置网络 + 填写在线源地址（官方 / 国内阿里 / 清华源），全程从网络下载系统包

✅ 适用：批量 PXE 装机、网络自动化部署、服务器机房统一批量装系统

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

### 虚拟机配置

CPU：安装 K8s 最少 2 vCPUs

内存：推荐 4G - 8G

硬盘：推荐 50G - 100G

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

### 安装过程

1）选择第一项安装

四个选项说明，按需选择：

1. **Install Rocky Linux 10.2（首选正常安装）** 日常装机直接选这个，回车启动安装向导，绝大多数场景用该项。
2. **Test this media & install Rocky Linux 10.2** 先校验安装镜像完整性（检测 U 盘 / ISO 文件是否损坏），校验通过后再安装；U 盘刻录不稳、怀疑镜像损坏时用。
3. **Install Rocky Linux 10.2 in FIPS mode** 联邦安全加密规范模式， **政企合规场景专用** ，普通个人 / 服务器装机不用。
4. **Troubleshooting** 故障排查菜单（救援模式、内存测试等），系统出问题修复才进，新装系统不用。
![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

2）这里我们选择英文

为啥中文排在了第一？原因说明：

1. **安装介质自动识别本地硬件时区 / 键盘区域** 你的虚拟机 / 宿主机系统是中文环境、BIOS 时区中国，Rocky 安装程序自动探测系统区域， **默认优选中文** ，所以简体中文置顶。
2. **Rocky Linux 10.2 本地化优化** 新版本 RHEL 系安装器 anaconda 会根据硬件所在地区、主板时区自动匹配首选语言，国内环境默认中文优先。
![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

3）自定义分区

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

`/` 根分区，空间给大一些

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

4）开启 root 用户登录

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

5）开始安装

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

6）安装完成重启

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

### 配置网卡静态 IP

安装时，我们默认采用的 DHCP 获取 IP。原因是为了避免 IP 冲突，我需要他自动获取一个未被使用的 IP，之后再将其修改为静态 IP。

你如果没有这种担心，完全可以在安装页面配置静态 IP。

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

1） 方式一（生产推荐，一条命令）

通过 `nmcli` 命令行，配置网卡静态 IP

```
# 替换【网卡名、IP、网关、DNS】
nmcli connection modify "ens34" \
  ipv4.method manual \
  ipv4.addresses 192.168.101.107/24 \
  ipv4.gateway 192.168.101.1 \
  ipv4.dns "223.5.5.5,8.8.8.8"
# 重载网卡生效
nmcli con down ens34 && nmcli con up ens34
```

2）方式二

修改网卡配置文件

```
$ vi /etc/NetworkManager/system-connections/ens34.nmconnection
...
...
[ipv4]s
address1=192.168.101.107/24
dns=223.5.5.5;8.8.8.8;
gateway=192.168.101.1
method=manual
...
...
```
![修改前](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

修改前

![修改后](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

修改后

重启网卡生效

```
# 1. 让 NM 重新读取所有配置文件（必须执行，否则不生效）
nmcli connection reload

# 2. 关掉 ens34 连接，再重新激活
nmcli connection down ens34
nmcli connection up ens34

# 3. 查看结果
ip a
nmcli connection show ens34
```

**[关注领取运维自学路线资料](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247488479&idx=1&sn=b09902d7bdc17ed4de667075840e3504&scene=21#wechat_redirect)** **| [进百人交流群](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247484443&idx=1&sn=39c66a908163621ff255280d837f9e97&scene=21#wechat_redirect) | [学企业级运维项目](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247490328&idx=1&sn=672e5579e954d7d8ef9dd6edd6670de0&scene=21#wechat_redirect)**

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

**|获取更多免费资料 | 进千人交流圈子**

**学企业级运维项目到： [真成运维导航](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247490328&idx=1&sn=672e5579e954d7d8ef9dd6edd6670de0&scene=21#wechat_redirect)**

**进百人交流群（推荐vx群聊）：** [运维交流/商务合作，集合](http://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247484443&idx=1&sn=39c66a908163621ff255280d837f9e97&chksm=cf7e2722f809ae349603d3f0aafd17da03b4cb2798ee2a2c37ec3ee67aab4b0702525477026e&scene=21#wechat_redirect)

[第一期 运维必知扫盲之阿里云中云防火墙和WAF防火墙区别？](https://mp.weixin.qq.com/s?__biz=Mzg3OTc2OTE3NA==&mid=2247487997&idx=1&sn=30252b22e47ff83e90c72b6e6b8b5c88&scene=21#wechat_redirect)

![图片](data:image/svg+xml,%3C%3Fxml version='1.0' encoding='UTF-8'%3F%3E%3Csvg width='1px' height='1px' viewBox='0 0 1 1' version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'%3E%3Ctitle%3E%3C/title%3E%3Cg stroke='none' stroke-width='1' fill='none' fill-rule='evenodd' fill-opacity='0'%3E%3Cg transform='translate(-249.000000, -126.000000)' fill='%23FFFFFF'%3E%3Crect x='249' y='126' width='1' height='1'%3E%3C/rect%3E%3C/g%3E%3C/g%3E%3C/svg%3E)

一指禅 戳戳戳!

作者提示: 个人观点，仅供参考

阅读原文

继续滑动看下一个

真成运维

向上滑动看下一个