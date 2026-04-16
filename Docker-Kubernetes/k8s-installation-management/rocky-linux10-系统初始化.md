---
title: Rocky Linux 10 系统初始化
tags:
  - rocky-linux
  - linux
  - initialization
  - k8s-prereq
aliases:
  - Rocky Linux 初始化
  - Linux 系统初始化
date: 2026-04-15
---

本文记录在 Rocky Linux 10 上部署 Kubernetes 之前所需的完整系统初始化步骤，包括：基础源配置、网络设置、内核参数调优、Swap 关闭、IPVS 启用等。完成本文所有步骤后，即可进行容器运行时（containerd）和 K8s 组件的安装。完整安装流程见 [[安装k8s-1.35-基于rockylinux10-最新步骤]]。

# K8s 架构与核心组件

## Master 组件

- **API Server**：集群对外的统一入口，以 RESTful API 方式做操作
- **Scheduler**：通过算法算出 Pod 调度到哪个节点
- **Controller Manager**：管理一系列的 Controller（Deployment、StatefulSet、Namespace 等）
- **etcd**：存储系统

## Worker Node 组件

- **kubelet**：节点代理，负责 Pod 生命周期管理
- **kube-proxy**：负责 Service 的网络代理和负载均衡
- **CoreDNS**：集群 DNS 服务
- **Calico**：网络插件，负责 Pod IP 分配和网络策略
- **containerd**：容器运行时（K8s 1.24+ 已移除 dockershim，不再支持 Docker 作为直接运行时）

> [!info] 本文版本信息
> - 操作系统：Rocky Linux 10（基于 RHEL 10）
> - Kubernetes：1.35.x
> - 容器运行时：containerd 2.x（配置格式 version = 3）
> - kubeadm 配置 API：**v1beta4**（v1beta3 已废弃）
> - 网络插件：Calico（最新版）
> - 包管理器：DNF5（Rocky Linux 10 默认）

# 环境准备

## 实验环境规划

- 操作系统：Rocky Linux 10（下载地址：https://rockylinux.org/download，选择 Minimal ISO）
- 网络：NAT 模式，可以确保机器在任何网络都能 SSH 连接

| K8S 集群角色 | IP              | 主机名 |
| ------------ | --------------- | ------ |
| 控制节点     | 192.168.164.100 | rm1    |
| 工作节点     | 192.168.164.101 | rn1    |
| 工作节点     | 192.168.164.102 | rn2    |

> [!warning] 最低配置要求
> - 控制节点：2 CPU / 2 GB RAM / 20 GB 磁盘
> - 工作节点：2 CPU / 2 GB RAM / 20 GB 磁盘
> - 所有节点需要网络互通，MAC 地址和 product_uuid 必须唯一

## 安装前准备

> [!note] 以下操作若无特殊说明，所有节点均需执行

### 1. 配置基础源

Rocky Linux 10 国内镜像源配置（使用阿里云镜像）：

```sh
# 查看当前 repo 文件
ls /etc/yum.repos.d/

# 替换为阿里云镜像源
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
    -i.bak \
    /etc/yum.repos.d/rocky-*.repo

dnf makecache
```

> [!tip] 换源说明
> 可以去阿里云镜像站（developer.aliyun.com/mirror）搜索 "Rocky Linux" 找到对应系统的换源操作。若阿里云暂未支持 Rocky Linux 10，可尝试 USTC（mirrors.ustc.edu.cn）或网易（mirrors.163.com）镜像源，或暂时使用官方源。

### 2. 安装基础软件包

Rocky Linux 10 使用 **DNF5** 作为默认包管理器，`yum` 作为兼容别名仍可使用：

```sh
dnf update -y
dnf install -y wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake \
  libxml2-devel openssl-devel curl curl-devel unzip sudo libaio-devel \
  vim ncurses-devel autoconf automake epel-release openssh-server \
  telnet coreutils iputils iproute nmap-ncat jq psmisc git bash-completion \
  yum-utils device-mapper-persistent-data lvm2 bind-utils

```

### 3. 配置网络

```sh
# 查看网卡名
ip addr

# 以 ens160 为例，修改为静态 IP（各节点 IP 不同，按实际修改）
nmcli connection modify ens160 ipv4.method manual connection.autoconnect yes
# 各节点 IP 不同，按实际修改
nmcli connection modify ens160 ipv4.addresses 192.168.164.100/24  
nmcli connection modify ens160 ipv4.gateway 192.168.164.2
nmcli con mod "ens160" ipv4.dns "114.114.114.114,8.8.8.8,192.168.164.2"
nmcli connection down ens160 && nmcli connection up ens160

# 验证 DNS 解析正常（能解析外部域名才能拉取镜像）
nslookup registry.cn-hangzhou.aliyuncs.com
```

> [!warning] DNS 配置说明
> 公共 DNS **必须放在 NAT 网关 DNS 前面**。containerd（Go 语言 resolver）只使用第一个 nameserver 解析，
> 如果 `192.168.164.2` 在最前面，它会对外部域名返回 NXDOMAIN（域名不存在），Go resolver 收到明确的否定应答后**不会再尝试后续 DNS**，导致 kubeadm init 时所有镜像拉取失败。
> - `114.114.114.114`：国内公共 DNS，放第一位，解析快
> - `8.8.8.8`：Google DNS，作为备用
> - `192.168.164.2`：NAT 网关，放最后，仅解析内网域名
>
> 如果 `nslookup` 验证失败，说明网络不通，需先排查 NAT 网络配置，不要继续后续步骤。

> [!tip]
> NetworkManager 会把修改写入 `/etc/NetworkManager/system-connections/ens160.nmconnection`；手动编辑该文件也可，但改完需执行 `nmcli connection reload`

### 4. 关闭 SELinux

```sh
# 永久关闭（需要重启）
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

# 立即临时关闭（不需要重启）
setenforce 0

# 验证
getenforce
```

### 5. 配置主机名

```sh
# 控制节点执行
hostnamectl set-hostname rm1 && bash

# 工作节点执行
hostnamectl set-hostname rn1 && bash
```

### 6. 配置 /etc/hosts

所有节点执行：

```sh
tee -a /etc/hosts <<'EOF'
192.168.164.100   rm1
192.168.164.101   rn1
192.168.164.102   rn2
EOF
```

### 7. 配置 SSH 互信

在控制节点执行：

```sh
ssh-keygen -t rsa -b 4096 -N ""
ssh-copy-id rn1
ssh-copy-id rn2
```

### 8. 关闭 Swap

> [!warning] 重要
> 执行删除 swap LV 操作前，请先打虚拟机快照！如删除后无法启动，可从快照恢复。

```sh
# 临时关闭
swapoff -a && sysctl -w vm.swappiness=0

# 永久关闭（注释 fstab 中的 swap 行）
sed -ri '/^[^#]*swap/s@^@#@' /etc/fstab
systemctl daemon-reload
```

可选：释放 swap LV 空间并扩容 root 分区：

```sh
lvs                                 # 查看 swap 占用的 LV
lvdisplay                               # 获取 swap LV Path（如 /dev/rl_rm1/swap）
lvremove /dev/rl_rm1/swap               # 删除 swap LV
vgs                                     # 查看 VG 剩余空间（VFree）
lvextend -L +<SIZE>G /dev/rl_rm1/home  # 扩容 home LV（替换 SIZE 为实际空闲大小）
xfs_growfs /dev/mapper/rl_rm1-home     # 扩容 XFS 文件系统
df -h                               # 验证
```

删除 swap 分区后必须重新配置 grub、BLS 引导条目、dracut 和 initramfs，否则重启会卡住或报 "找不到 swap" 错误：

```sh
# 1. 查看当前 GRUB_CMDLINE_LINUX 的完整内容（确认要删的参数）
grep GRUB_CMDLINE_LINUX /etc/default/grub
# 典型输出（VG 名含主机名，如 rl_rm1）：
# GRUB_CMDLINE_LINUX="crashkernel=... resume=/dev/mapper/rl_rm1-swap rd.lvm.lv=rl_rm1/root rd.lvm.lv=rl_rm1/swap rhgb quiet"

# 2. 修改 /etc/default/grub，删除 swap 相关参数（影响未来新装内核的默认参数）
#    删除 resume= 参数（指向 swap 设备，用于休眠恢复）
sed -i 's/ resume=[^ "]*//' /etc/default/grub
#    删除 rd.lvm.lv=.../swap 参数（告诉 dracut 激活 swap LV）
sed -i 's/ rd\.lvm\.lv=[^ "]*swap//' /etc/default/grub

# 3. 验证 /etc/default/grub 修改结果
grep GRUB_CMDLINE_LINUX /etc/default/grub

# 4.【关键】使用 grubby 更新已有的 BLS 引导条目
#    Rocky Linux 10 使用 BLS（Boot Loader Specification），内核启动参数存储在
#    /boot/loader/entries/*.conf 中。仅修改 /etc/default/grub 不会更新已有的 BLS 条目！
#    必须用 grubby 删除所有已有内核条目中的 swap 相关参数：
grubby --update-kernel=ALL --remove-args="resume rd.lvm.lv=rl_rm1/swap"
# 注意：rd.lvm.lv=rl_rm1/swap 中的 rl_rm1 替换为实际 VG 名（通过 vgs 查看）

# 验证 BLS 条目已更新（确认 resume 和 swap 参数已消失）
grubby --info=ALL | grep -E "resume|swap" || echo "BLS 条目已清理干净"

# 5. 清除 dracut 的 resume 模块配置
#    dracut 有独立的 resume 配置，仅清理引导参数不够！
#    dracut -f 时 resume 模块仍会自动将已删除的 swap 设备写入 initramfs，
#    导致启动时 initramfs 尝试激活不存在的 swap LV 用于休眠恢复，系统卡住。
rm -f /etc/dracut.conf.d/resume.conf
# 显式禁用 resume 模块，防止 dracut 自动探测残留的 swap 引用
echo 'omit_dracutmodules+=" resume "' > /etc/dracut.conf.d/noresume.conf
# 如果存在 systemd-hibernate-resume 服务也一并禁用
systemctl disable systemd-hibernate-resume@*.service 2>/dev/null || true

# 6. 重新生成 initramfs（此步不可跳过，必须在上一步清除 resume 配置之后执行）
dracut -f

# 7. 重新生成 grub 配置
#    Rocky Linux 10 的 UEFI 引导使用 wrapper 机制：
#    /boot/efi/EFI/rocky/grub.cfg 只是一个薄包装，实际配置始终在 /boot/grub2/grub.cfg
#    因此无论 UEFI 还是 Legacy BIOS，统一使用以下命令：
grub2-mkconfig -o /boot/grub2/grub.cfg

# 8. 重启验证
init 6
```

### 9. 修改内核参数

```sh
# 加载必要的内核模块（overlay 用于 containerd，br_netfilter 用于 k8s 网络）
modprobe overlay
modprobe br_netfilter

# 持久化模块加载配置
cat > /etc/modules-load.d/k8s.conf <<'EOF'
overlay
br_netfilter
EOF

# 配置内核网络参数（开启包转发和过滤）
tee /etc/sysctl.d/k8s.conf <<'EOF'
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

sysctl -p /etc/sysctl.d/k8s.conf
```

### 10. 关闭防火墙和 dnsmasq

```sh
systemctl stop firewalld && systemctl disable firewalld
systemctl disable --now dnsmasq 2>/dev/null || true
```

### 11. 配置时间同步

```sh
dnf install -y chrony
systemctl enable chronyd --now

tee -a /etc/chrony.conf <<'EOF'
server ntp1.aliyun.com iburst
server ntp2.aliyun.com iburst
server ntp1.tencent.com iburst
server ntp2.tencent.com iburst
EOF

systemctl restart chronyd

# 验证同步状态
chronyc tracking
```

### 12. 启用 IPVS

```sh
cat > /etc/modules-load.d/ipvs.conf <<'EOF'
br_netfilter
nf_conntrack
ip_vs
ip_vs_lc
ip_vs_wlc
ip_vs_rr
ip_vs_wrr
ip_vs_lblc
ip_vs_lblcr
ip_vs_dh
ip_vs_sh
ip_vs_fo
ip_vs_nq
ip_vs_sed
ip_vs_ftp
ip_tables
ip_set
xt_set
ipt_set
ipt_rpfilter
ipt_REJECT
ipip
EOF

# 安装 IPVS 相关工具
dnf install -y ipvsadm ipset sysstat conntrack-tools libseccomp

# 重启模块加载服务使配置生效
systemctl restart systemd-modules-load.service

# 验证
lsmod | grep -e ip_vs -e nf_conntrack
```

> [!note] Rocky Linux 10 变更
> `ip_conntrack` 模块在新内核中已更名为 `nf_conntrack`，请使用新名称。`conntrack` 软件包也已更名为 `conntrack-tools`。

### 13. 设置文件句柄数上限

```sh
ulimit -SHn 65535

cat >> /etc/security/limits.conf <<'EOF'
* soft nofile 655360
* hard nofile 655360
* soft nproc 655350
* hard nproc 655350
* soft memlock unlimited
* hard memlock unlimited
EOF

# 验证
ulimit -a
```

### 14. 【可选】系统内核优化

针对 8C8G 虚拟机，其余配置可相应调整：

```sh
cat > /etc/sysctl.d/k8s_better.conf <<'EOF'
vm.swappiness=0
vm.overcommit_memory=1
vm.panic_on_oom=0
fs.inotify.max_user_instances=16384
fs.inotify.max_user_watches=2097152
fs.file-max=104857600
fs.nr_open=104857600
net.ipv6.conf.all.disable_ipv6=1
net.netfilter.nf_conntrack_max=4621440
EOF

sysctl -p /etc/sysctl.d/k8s_better.conf
```

> 参数说明：
> - `vm.swappiness=0`：禁用 swap，K8s 要求禁用 swap
> - `vm.overcommit_memory=1`：允许内存过量分配，提高容器密度
> - `vm.panic_on_oom=0`：OOM 时不让系统崩溃，而是杀死进程
> - `fs.inotify.*`：增加文件系统监控限制，防止 "too many open files" 错误
> - `net.netfilter.nf_conntrack_max=4621440`：增加网络连接跟踪表大小

### 15. 配置 Docker CE 阿里云 repo 源

```sh
# 安装 yum-utils（提供 yum-config-manager 命令）
dnf install -y yum-utils

# 添加阿里云 Docker CE 源
# Rocky Linux 10 基于 RHEL 10，使用 rhel 路径（不能用 centos 路径，centos 路径只有 el7/8/9）
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/rhel/docker-ce.repo

dnf clean all && dnf makecache
```

> [!note] 为何从 centos 改为 rhel
> 1.33 文档使用的是 `centos/docker-ce.repo`，其仓库只有 el7/el8/el9 的包。Rocky Linux 10 的 `$releasever=10`，解析后找不到对应包会报错。改为 `rhel/docker-ce.repo` 后，Docker CE 官方为 RHEL 10 提供了 el10 的包，阿里云同步了该镜像源，可以正常安装。
