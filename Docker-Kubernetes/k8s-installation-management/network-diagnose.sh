#!/bin/bash
echo "========== 网络诊断脚本 =========="
echo "时间: $(date)"
echo "主机名: $(hostname)"
echo ""

echo "===== 1. 网卡与IP ====="
ip addr show
echo ""

echo "===== 2. 路由表 ====="
ip route show
echo ""

echo "===== 3. DNS 配置 ====="
cat /etc/resolv.conf
echo ""

echo "===== 4. Ping 网关 ====="
GW=$(ip route show default | awk '{print $3}')
echo "默认网关: $GW"
ping -c 2 -W 3 "$GW" 2>&1
echo ""

echo "===== 5. Ping 外网IP ====="
for ip in 223.5.5.5 8.8.8.8 114.114.114.114; do
    echo "--- ping $ip ---"
    ping -c 2 -W 3 "$ip" 2>&1
    echo ""
done

echo "===== 6. Ping 外网域名 ====="
for host in www.baidu.com www.aliyun.com; do
    echo "--- ping $host ---"
    ping -c 2 -W 3 "$host" 2>&1
    echo ""
done

echo "===== 7. DNS 解析测试 ====="
for dns in "$GW" 223.5.5.5 8.8.8.8; do
    echo "--- nslookup www.baidu.com via $dns ---"
    nslookup www.baidu.com "$dns" 2>&1 || echo "(nslookup 未安装或失败)"
    echo ""
done

echo "===== 8. TCP 端口连通性 ====="
for target in "223.5.5.5 53" "223.5.5.5 80" "8.8.8.8 443" "192.168.164.2 53"; do
    ip_addr=$(echo "$target" | awk '{print $1}')
    port=$(echo "$target" | awk '{print $2}')
    echo -n "TCP $ip_addr:$port -> "
    timeout 3 bash -c "echo >/dev/tcp/$ip_addr/$port" 2>/dev/null && echo "通" || echo "不通"
done
echo ""

echo "===== 9. 防火墙状态 ====="
if command -v firewall-cmd &>/dev/null; then
    firewall-cmd --state 2>&1
    firewall-cmd --list-all 2>&1
else
    echo "firewalld 未安装"
fi
echo ""

echo "===== 10. iptables OUTPUT 链 ====="
iptables -L OUTPUT -n -v --line-numbers 2>&1 | head -20
echo ""

echo "===== 11. SELinux 状态 ====="
getenforce 2>&1
echo ""

echo "===== 12. NAT 类型检查(VMware) ====="
if [ -f /sys/class/dmi/id/product_name ]; then
    echo "虚拟化产品: $(cat /sys/class/dmi/id/product_name)"
fi
hostnamectl 2>&1 | grep -i "virtualization\|chassis"
echo ""

echo "========== 诊断完成 =========="
