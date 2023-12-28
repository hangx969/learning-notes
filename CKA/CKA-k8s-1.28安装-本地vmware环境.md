# 本地VMWare环境搭建1.28版本K8S

## 配置VMware虚拟机

- 安装VMware
- 下载CentOS7镜像
- 配置VMWare虚拟机，使用NAT模式。
- 安装CentOS系统

## 配置CentOS虚拟机网络

- 新搭建出来的虚拟机默认没有IP，需要先修改配置文件加一个IP

- vmware-编辑-虚拟机网络编辑器，先把网段和子网掩码设置好：

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312281954166.png" alt="image-20231228195437108" style="zoom:50%;" />

- 修改网卡配置文件

  ~~~bash
  vi /etc/sysconfig/network-scripts/ifcfg-ens33
  
  TYPE=Ethernet
  PROXY_METHOD=none
  BROWSER_ONLY=no
  BOOTPROTO=static #static表示静态ip地址
  IPADDR=192.168.40.180 #ip地址，需要跟自己电脑所在网段一致
  NETMASK=255.255.255.0
  GATEWAY=192.168.40.2
  DNS1=192.168.40.2
  DEFROUTE=yes
  IPV4_FAILURE_FATAL=no
  IPV6INIT=yes
  IPV6_AUTOCONF=yes
  IPV6_DEFROUTE=yes
  IPV6_FAILURE_FATAL=no
  IPV6_ADDR_GEN_MODE=stable-privacy
  NAME=ens33 #网卡名字，跟DEVICE名字保持一致即可
  DEVICE=ens33 #网卡设备名，ip addr可看到自己的这个网卡设备名
  ONBOOT=yes #开机自启动网络，必须是yes
  ~~~

## 关闭Selinux

~~~bash
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
~~~

## SSH连接

- VSCod直接配置ssh host文件用内网IP登录。

### 免密登录

- 客户端ssh-keygen生成公钥

- 把公钥复制到服务器端

  ```bash
  mkdir -p ~/.ssh/
  touch ~/.ssh/authorized_keys
  vi ~/.ssh/authorized_keys
  #将公钥值复制进去
  ```

- 编辑ssh配置文件

  ~~~bash
  sudo vim /etc/ssh/sshd_config
  #PubkeyAuthentication yes注释去掉，才可以使用公钥验证
  ~~~

- 重启ssh服务

  ~~~bash
  systemctl restart sshd.service 
  ~~~

- VsCode的ssh配置文件中加入公钥位置

  ~~~bash
  Host 192.168.40.180
    HostName 192.168.40.180
    User root
    IdentityFile /C:/Users/hangx/.ssh/id_rsa
  ~~~

## 克隆两台工作节点

- 虚拟机关机-右键克隆出两台新机器

- 修改两台机器网卡配置文件，配置静态IP

  ~~~bash
  vi /etc/sysconfig/network-scripts/ifcfg-ens33
  #IP修改成192.168.40.181,192.168.40.182
  ~~~

  