# 背景

- 在Linux操作系统中，我们经常通过修改网卡的配置文件来修改IP地址，这个方法确实非常的方便。但在高版本Linux中，特别是在CentOS8、RHEL8等系统中，已经完全采用NetworkManager服务来管理网络，network服务已经被废弃了，所以最好的方式就是采用nmcli命令来配置IP地址信息。
- 以下配置方法不仅适用于CentOS7、8，RHEL7、8、9，也适用于Ubuntu20.x、Ubuntu22.x，Rocky Linux 9.x等，使用NetworkManager服务管理网络的Linux发行版本基本通用。

# nmcli使用

- 通过nmcli命令修改IP地址，需要启动NetworkManager服务来管理系统网络

~~~sh
#查看网卡名称（与ip a/ip add show/ip addr效果一样）
nmcli device
#查看配置文件
nmcli connection show
#删除网卡配置信息
nmcli connection delete <网卡名称>
#增加网卡配置文件
nmcli connection add con-name <配置文件名称> ifname <指定网卡名称，将此配置与网卡绑定> type <指定网卡类型>
nmcli connection add con-name ens33 ifname ens33 type ethernet
#默认情况下，在Ubuntu中增加网卡配置文件后，会启动DHCP功能获取IP地址。
~~~

假设想把网卡配置改为如下：

- IP地址：192.168.211.201
- 掩  码：255.255.255.0
- 网  关：192.168.211.2
- DNS地址：8.8.8.8和114.114.114.114

~~~sh
nmcli connection modify ens33 ipv4.method manual connection.autoconnect yes #修改IP地址为手动配置，并且设置开机启动
nmcli connection modify ens33 ipv4.addresses 192.168.211.201/24 #修改IP地址和掩码
nmcli connection modify ens33 ipv4.gateway 192.168.211.2 #修改网关
nmcli connection modify ens33 ipv4.dns 8.8.8.8,114.114.114.114 #修改DNS，多个DNS以逗号分隔
nmcli connection down ens33 #关闭网卡
nmcli connection up ens33 #启用网卡
~~~

~~~sh
#y也可以一条命令来修改
nmcli connection modify ens33 ipv4.addresses 192.168.211.201/24 ipv4.gateway 192.168.211.2 ipv4.dns 8.8.8.8,114.114.114.114 ipv4.method manual connection.autoconnect yes
~~~

