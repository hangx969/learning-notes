# 背景

- 1987年，微软公司和英特尔公司共同制定了SMB（server Messages Block）协议用来解决局域网内的文件或打印机等的资源共享问题。但是这时后还是解决不了跨系统之间的文件共享。直到1991年，在读大学的Tridgwell基于SMB协议开发能够解决Linux系统和windows系统之间的文件的问题——也就是SMB Server服务。后来被命名为samba（根据一个拉丁舞名字）。如今，samba服务测序成为了在Linux和windows系统之间共享文件的最佳选择。

  # samba

介绍:

1. samba是一组软件包，是Linux支持SMB/CIFS协议（也称S/C）
2. samba可以在几乎所有的类UNIX平台上运行。

功能：

1. 使Linux主机成为Windows网络的一份子，与Windows网络相互分享资源
2. 使Linux主机可以使用Windows共享的文件和打印机
3. 使Linux主机成为文件服务器或打印服务器，为Linux 、Windows客户端提供文件共享服务和远程打印服务

需要启动的服务：

1. smb服务：管理SAMBA服务器共享什么目录、文件、打印机
2. nmb服务：管理群组和netbios name解析

# 搭建samba环境

## server端-Linux

- 创建两个nologin用户

~~~sh
useradd -s /bin/nologin user01
useradd -s /bin/nologin user02
~~~

- 我们做这个服务是为了能够实现文件共享，为此，我们还要准备一个共享的文件 /share，并且设置其文件权限为777

~~~sh
mkdir /share
chmod -R 777 /share/
~~~

- 在server上通过yum来安装samba服务

~~~sh
yum -y install samba
~~~

- 创建samba账号，用我们最开始创建的user01和user02用户，密码设置为123456

~~~sh
smbpasswd -a user01
pdbedit -a -u user02
#两个命令都是samba自带的工具，功能差不多
~~~

- 配置文件

~~~sh
vim /etc/samba/smb.conf
#写入以下
[myshare]
        comment = public document
        path = /share
        public = no
        browseable = Yes
        writable = Yes
#重启samba
systemctl restart smb
~~~

- 配置防火墙

~~~sh
#测试环境直接关闭
systemctl stop firewalld
#正式环境配置允许samba服务
firewall-cmd --add-service=samba --permanent 
firewall-cmd --reload
~~~

- 配置selinux

~~~sh
chcon -R -t samba_share_t /share
~~~

- 如果需要samba服务程序访问普通用户家目录或者是共享用户的家目录，我们需要打开sebool设置

~~~sh
#可以通过getsebool 命令筛选出有关samba相关的SELinux域策略，但是还是需要策略的名称选择出正确的策略开启就行了
getsebool -a | grep samba
samba_create_home_dirs --> off
samba_domain_controller --> off
samba_enable_home_dirs --> on    ####我们本次实操开启这个就行了，基本上也就只要要开启这个
samba_export_all_ro --> off
samba_export_all_rw --> off
samba_load_libgfapi --> off
samba_portmapper --> off
samba_run_unconfined --> off
samba_share_fusefs --> off
samba_share_nfs --> off
sanlock_use_samba --> off
tmpreaper_use_samba --> off
use_samba_home_dirs --> off
virt_use_samba --> off
#打开配置
setsebool -P samba_enable_home_dirs on
~~~

## client端-Windows

~~~sh
#访问server地址
\\192.168.147.11
#输入网络凭据，也就是我们一开始设置的samba用户和密码
#注：可以使用 net use * /del 命令清除网络连接缓存，用来排除上次连接的影响
~~~

## client端-Linux

- 直接用smbclient访问

~~~sh
yum -y install samba-client cifs-utils
smbclient -L 192.168.147.11 -U user01
#可以看到myshare被列出了
smbclient //192.168.147.11/myshare -U user01
#测试创建目录（根据我们之前在server上samba配置文件所给的权限）
smb: \> mkdir test_share
~~~

- 将samba共享的目录挂在到客户端的本地目录下（临时挂载）

~~~sh
mkdir /usershare
mount -t cifs //192.168.147.11/myshare /usershare/ -o username=user01
ls -l /usershare/
~~~

