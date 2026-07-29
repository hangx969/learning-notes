#!/usr/bin/env bash
set -euo pipefail

: "${NIC_NAME:?NIC_NAME is required}"
: "${STATIC_IP_CIDR:?STATIC_IP_CIDR is required}"
: "${GATEWAY_IPV4:?GATEWAY_IPV4 is required}"
: "${DNS_SERVERS:?DNS_SERVERS is required}"
: "${HOSTNAME_VALUE:?HOSTNAME_VALUE is required}"
: "${HOSTS_BLOCK_B64:?HOSTS_BLOCK_B64 is required}"

HOSTS_BLOCK="$(printf '%s' "$HOSTS_BLOCK_B64" | base64 -d)"

# 1. 配置基础源
ls /etc/yum.repos.d/
sed -e 's|^mirrorlist=|#mirrorlist=|g' \
    -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
    -i.bak \
    /etc/yum.repos.d/rocky-*.repo

dnf makecache

# 2. 安装基础软件包
dnf update -y
dnf install -y wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake \
  libxml2-devel openssl-devel curl curl-devel unzip sudo libaio-devel \
  vim ncurses-devel autoconf automake epel-release openssh-server \
  telnet coreutils iputils iproute nmap-ncat jq psmisc git bash-completion \
  yum-utils device-mapper-persistent-data lvm2 bind-utils

# 3. 配置网络
ip addr
nmcli connection modify "$NIC_NAME" ipv4.method manual connection.autoconnect yes
nmcli connection modify "$NIC_NAME" ipv4.addresses "$STATIC_IP_CIDR"
nmcli connection modify "$NIC_NAME" ipv4.gateway "$GATEWAY_IPV4"
nmcli con mod "$NIC_NAME" ipv4.dns "$DNS_SERVERS"
nmcli connection down "$NIC_NAME" && nmcli connection up "$NIC_NAME"
nslookup registry.cn-hangzhou.aliyuncs.com

# 4. 关闭 SELinux
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
setenforce 0
getenforce

# 5. 配置主机名
hostnamectl set-hostname "$HOSTNAME_VALUE" && bash

# 6. 配置 /etc/hosts
tee -a /etc/hosts >/dev/null <<EOF
$HOSTS_BLOCK
EOF

# 8. 关闭 Swap
swapoff -a && sysctl -w vm.swappiness=0
sed -ri '/^[^#]*swap/s@^@#@' /etc/fstab
systemctl daemon-reload

# 9. 修改内核参数
modprobe overlay
modprobe br_netfilter
cat > /etc/modules-load.d/k8s.conf <<'EOF'
overlay
br_netfilter
EOF
tee /etc/sysctl.d/k8s.conf <<'EOF'
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl -p /etc/sysctl.d/k8s.conf

# 10. 关闭防火墙和 dnsmasq
systemctl stop firewalld && systemctl disable firewalld
systemctl disable --now dnsmasq 2>/dev/null || true

# 11. 配置时间同步
dnf install -y chrony
systemctl enable chronyd --now
tee -a /etc/chrony.conf <<'EOF'
server ntp1.aliyun.com iburst
server ntp2.aliyun.com iburst
server ntp1.tencent.com iburst
server ntp2.tencent.com iburst
EOF
systemctl restart chronyd
chronyc tracking

# 12. 启用 IPVS
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
dnf install -y ipvsadm ipset sysstat conntrack-tools libseccomp
systemctl restart systemd-modules-load.service
lsmod | grep -e ip_vs -e nf_conntrack

# 13. 设置文件句柄数上限
ulimit -SHn 65535
cat >> /etc/security/limits.conf <<'EOF'
* soft nofile 655360
* hard nofile 655360
* soft nproc 655350
* hard nproc 655350
* soft memlock unlimited
* hard memlock unlimited
EOF
ulimit -a

# 15. 配置 Docker CE 阿里云 repo 源
dnf install -y yum-utils
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/rhel/docker-ce.repo
dnf clean all && dnf makecache
