- 参考：https://mp.weixin.qq.com/s/ls2Tv9_X9M_iWphTUUIjpQ

# 实验环境搭建

- 虚机

  - OS: rocky Linux 8


  | 主机名  | IP            | 角色       |
  | ------- | ------------- | ---------- |
  | rocky-1 | 172.16.183.80 | controller |
  | rocky-2 | 172.16.183.81 | node       |

- 配置网络(虚机安装时可以预配，没有的话就装好再配)

~~~sh
nmcli connection modify ens160 ipv4.method manual connection.autoconnect yes #修改IP地址为手动配置，并且设置开机启动
nmcli connection modify ens160 ipv4.addresses 172.16.183.81/24 #修改IP地址和掩码
nmcli connection modify ens160 ipv4.gateway 172.16.183.2 #修改网关
nmcli connection modify ens160 ipv4.dns 172.16.183.2 #修改DNS，多个DNS以逗号分隔
nmcli connection down ens160 #关闭网卡
nmcli connection up ens160 #启用网卡
~~~

- 配置hosts

~~~sh
#两台虚机上
tee -a /etc/hosts <<'EOF'
172.16.183.80 rocky-1
172.16.183.81 rocky-2
EOF
~~~

- 配置ssh互信

~~~sh
ssh-keygen
ssh-copy-id root@rocky-1
ssh-copy-id root@rocky-2
~~~

- 配置防火墙和selinux

~~~sh
systemctl stop firewalld && systemctl disable firewalld
#安装iptables防火墙
yum install iptables-services -y
#禁用iptables
service iptables stop && systemctl disable iptables
#清空防火墙规则
iptables -F 
#关闭selinux
setenforce 0
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
~~~

- 安装软件包

~~~sh
yum update -y
yum install -y wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo libaio-devel wget vim ncurses-devel autoconf automake zlib-devel epel-release openssh-server socat ipvsadm conntrack yum-utils chrony
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
~~~

# 主控节点安装ansible

~~~sh
yum install -y ansible
ansible --version
##############
ansible [core 2.16.3]
  config file = /etc/ansible/ansible.cfg
  configured module search path = ['/root/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python3.12/site-packages/ansible
  ansible collection location = /root/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/bin/ansible
  python version = 3.12.3 (main, Jul  2 2024, 20:57:30) [GCC 8.5.0 20210514 (Red Hat 8.5.0-22)] (/usr/bin/python3.12)
  jinja version = 3.1.2
  libyaml = True
#####################
~~~

# ansible环境配置

- 用户配置

> 生产中会配置特定的用户，不使用root用户来做

~~~sh
#所有节点上加用户
adduser --uid 2001 hangx
passwd hangx #hangx
#所有节点上，用户提权
visudo
## Allow root to run any commands anywhere
root    ALL=(ALL)       ALL
#加这一行
hangx  ALL=(ALL)       ALL

#配置sudo免密
tee /etc/sudoers.d/hangx <<'EOF'
hangx  ALL=(ALL) NOPASSWD:ALL
EOF
~~~

- 配置hangx普通用户ssh互信

~~~sh
su hangx
ssh-keygen
ssh-copy-id hangx@rocky-1
ssh-copy-id hangx@rocky-2
~~~

- 主配置文件`ansible.cfg`编写

~~~sh
#主控节点上
su hangx
cd
mkdir ansible
cd ansible
tee ansible.cfg <<'EOF' 
[defaults]
# 主机清单文件，就是要控制的主机列表
inventory=inventory
# 连接受管机器的远程的用户名
remote_user=hangx
# 角色目录
roles_path=roles
# 设置用户的su 提权
[privilege_escalation]
become=True
become_method=sudo
become_user=root
become_ask_pass=False
EOF
~~~

- 主机清单文件

~~~sh
#主控节点上。主机清单填被控节点
tee /home/hangx/ansible/inventory <<'EOF'
[nodes]
rocky-2
EOF

ansible all --list-hosts
ansible nodes --list-hosts
~~~

# 测试临时命令

`ansible 清单主机地址列表 -m 模块名 [-a '任务参数']`

```sh
ansible all -m ping
ansible nodes -m command -a 'ip a list ens160'
```
