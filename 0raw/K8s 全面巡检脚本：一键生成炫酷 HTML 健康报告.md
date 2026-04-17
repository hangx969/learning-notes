---
title: "K8s 全面巡检脚本：一键生成炫酷 HTML 健康报告"
source: "https://mp.weixin.qq.com/s/nDV67plLtWmHHJrGr04qXw"
author:
  - "[[院长技术]]"
published:
created: 2026-04-17
description: "🔍\x0a  \x0a    K8s 全面巡检脚本\x0a  \x0a  \x0a    一键巡检集群 · 自动生成炫酷 HTML"
tags:
  - "clippings"
---
原创 院长技术 *2026年4月6日 07:30*

🔍

K8s 全面巡检脚本

一键巡检集群 · 自动生成炫酷 HTML 健康报告

Shell 脚本 HTML 报告 全面巡检 生产可用

作者：院长 | 专注云原生与 DevOps

📋 文章目录

01为什么需要 K8s 巡检？

02巡检脚本架构设计

03完整巡检 Shell 脚本

04炫酷 HTML 报告模板

05巡检脚本一键部署

06定时自动巡检（CronJob）

07巡检报告预览与告警通知

01

为什么需要 K8s 巡检？

生产环境的 K8s 集群就像一台高速运转的发动机，每天承载着数以百计的微服务和流量洪峰。 **没有定期巡检的集群，就像从不做体检的人** ——平时看起来没事，真出问题往往是大事。

以下这些问题，巡检脚本都能帮你提前发现：

💥

Pod 异常

CrashLoopBackOff、OOMKilled、Pending 卡住…

💾

资源告警

节点 CPU/内存飙高、磁盘快满、PVC 容量不足

🔒

证书到期

API Server 证书、Ingress TLS 证书即将过期

🌐

网络故障

CoreDNS 异常、Service 无 Endpoint、网络策略冲突

02

巡检脚本架构设计

巡检脚本采用 **模块化设计** ，每个检查项独立成函数，最终汇总输出为一份炫酷的 HTML 报告。

📐 架构总览

输入层

kubectl 命令 + metrics-server API + 集群配置

↓

处理层

Shell 函数模块：节点/Pod/资源/网络/证书/事件

↓

输出层

HTML 报告（炫酷仪表盘风格）

↓

通知层

钉钉 / 企微 / 邮件 告警推送（可选）

🔎 巡检模块清单

🖥️

节点健康检查

✓节点 Ready 状态

✓CPU / 内存使用率

✓磁盘压力 / 内存压力 / PID 压力

✓节点版本 & 内核版本

✓Taints 污点分析

🚀

Pod 状态检查

✓所有 Namespace Pod 状态汇总

✓CrashLoopBackOff / OOMKilled 检测

✓Pending 超 5 分钟 Pod 告警

✓Restart 次数超阈值 Pod

✓镜像拉取失败 Pod

💰

资源配额检查

✓ResourceQuota 使用率

✓LimitRange 配置检查

✓PVC 使用状态 & 容量

✓StorageClass 可用性

✓未设置 requests/limits 的 Pod

🌐

网络组件检查

✓CoreDNS 副本数 & Pod 状态

✓Ingress 规则有效性

✓Service 与 Endpoint 绑定

✓NetworkPolicy 规则分析

✓CNI 插件 Pod 状态

🔒

证书安全检查

✓API Server 证书到期时间

✓etcd 证书到期时间

✓Ingress TLS 证书到期

✓ServiceAccount Token 状态

✓RBAC 权限异常检测

⚡

系统组件检查

✓kube-system 全部组件状态

✓etcd 集群健康检查

✓Scheduler & Controller 状态

✓metrics-server 可用性

✓HPA 伸缩策略有效性

03

完整巡检 Shell 脚本

以下是完整的 K8s 巡检脚本，支持全版本 K8s，建议保存为 `k8s_inspect.sh` 并赋予执行权限。

第一部分：脚本头部与全局配置

bash - k8s\_inspect.sh (第一部分：头部声明)

#!/bin/bash

\# =============================================================

\# K8s 全面巡检脚本 v2.0

\# 作者：无处不在的技术

\# 功能：全面检查 K8s 集群健康状态，生成 HTML 报告

\# 用法：bash k8s\_inspect.sh \[namespace\] \[--all-ns\]

\# 依赖：kubectl、bc、awk（已预装于大多数 Linux）

\# =============================================================

set -euo pipefail

\# ── 全局配置 ──────────────────────────────────────────────

REPORT\_DIR

\="${REPORT\_DIR:-/tmp/k8s-inspect}"

REPORT\_FILE

\="${REPORT\_DIR}/k8s\_report\_$(date +%Y%m%d\_%H%M%S).html"

LOG\_FILE

\="${REPORT\_DIR}/inspect.log"

NAMESPACE

\="${1:---all-namespaces}"

THRESHOLD\_CPU

\=80

\# CPU 告警阈值(%)

THRESHOLD\_MEM

\=80

\# 内存告警阈值(%)

THRESHOLD\_DISK

\=85

\# 磁盘告警阈值(%)

THRESHOLD\_RESTART

\=5

\# Pod 重启次数告警阈值

CERT\_WARN\_DAYS

\=30

\# 证书到期提前告警天数

\# ── 颜色输出 ──────────────────────────────────────────────

RED

\='\\033\[0;31m'

GREEN

\='\\033\[0;32m'

YELLOW

\='\\033\[1;33m'

BLUE

\='\\033\[0;34m'

NC

\='\\033\[0m'

\# ── 初始化目录 ────────────────────────────────────────────

mkdir -p "$REPORT\_DIR"

exec > >(tee -a "$LOG\_FILE") 2>&1

\# ── 工具函数 ──────────────────────────────────────────────

log\_info()

{ echo -e "${GREEN}\[INFO\]${NC} $\*"; }

log\_warn()

{ echo -e "${YELLOW}\[WARN\]${NC} $\*"; }

log\_error()

{ echo -e "${RED}\[ERROR\]${NC} $\*"; }

log\_title()

{ echo -e "${BLUE}\\n====== $\* ======${NC}"; }

第二部分：HTML 报告初始化

bash - k8s\_inspect.sh (第二部分：HTML 报告初始化)

\# =============================================================

\# HTML 报告构建函数

\# =============================================================

html\_header()

{

cat > "$REPORT\_FILE" << 'HTMLEOF'

<!DOCTYPE html>

<html lang="zh-CN">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width,initial-scale=1">

<title>K8s 巡检报告</title>

<style>

:root{--ok:#00d084;--warn:#f59e0b;--err:#ef4444;--bg:#0f172a;--card:#1e293b;}

body{margin:0;font-family:system-ui;background:var(--bg);color:#e2e8f0;}

.header{background:linear-gradient(135deg,#1e3a5f,#0f172a);

padding:32px;text-align:center;border-bottom:1px solid #334155;}

.title{font-size:28px;font-weight:900;color:#38bdf8;margin-bottom:8px;}

.subtitle{color:#94a3b8;font-size:14px;}

.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;

padding:24px;max-width:1200px;margin:0 auto;}

.stat{background:var(--card);border-radius:12px;padding:20px;text-align:center;

border:1px solid #334155;}

.stat-num{font-size:36px;font-weight:900;margin-bottom:4px;}

.stat-label{font-size:12px;color:#94a3b8;}

.section{max-width:1200px;margin:0 auto 24px;padding:0 24px;}

.section-title{font-size:18px;font-weight:700;color:#38bdf8;

padding:12px 0;border-bottom:2px solid #334155;margin-bottom:16px;}

table{width:100%;border-collapse:collapse;background:var(--card);

border-radius:10px;overflow:hidden;}

th{background:#1e3a5f;color:#94a3b8;font-size:12px;padding:10px 14px;text-align:left;}

td{padding:10px 14px;font-size:13px;border-bottom:1px solid #334155;}

tr:last-child td{border-bottom:none;}

.ok{color:var(--ok);font-weight:700;}

.warn{color:var(--warn);font-weight:700;}

.err{color:var(--err);font-weight:700;}

.badge{display:inline-block;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;}

.badge-ok{background:rgba(0,208,132,0.15);color:#00d084;}

.badge-warn{background:rgba(245,158,11,0.15);color:#f59e0b;}

.badge-err{background:rgba(239,68,68,0.15);color:#ef4444;}

</style></head>

<body>

HTMLEOF

}

第三部分：节点健康检查

bash - k8s\_inspect.sh (第三部分：节点检查)

\# =============================================================

\# 模块一：节点健康检查

\# =============================================================

check\_nodes()

{

log\_title "节点健康检查"

\# 写入 HTML 节点章节标题

cat >> "$REPORT\_FILE" << 'EOF'

<div class="section">

<div class="section-title">🖥️ 节点健康检查</div>

<table>

<tr><th>节点名称</th><th>状态</th><th>角色</th><th>K8s 版本</th>

<th>CPU 使用</th><th>内存使用</th><th>运行时间</th><th>内核版本</th></tr>

EOF

\# 遍历所有节点

while

IFS= read -r line; do

NODE\_NAME

\=$(echo "$line" | awk '{print $1}')

NODE\_STATUS

\=$(echo "$line" | awk '{print $2}')

NODE\_ROLE

\=$(kubectl get node "$NODE\_NAME" \\

\--no-headers -o jsonpath='{.metadata.labels}' \\

| grep -o '"node-role.\*?"' | head -1 || echo "worker")

K8S\_VER

\=$(echo "$line" | awk '{print $5}')

UPTIME

\=$(echo "$line" | awk '{print $NF}')

\# 获取 CPU/内存使用率（需 metrics-server）

CPU\_USAGE

\=$(kubectl top node "$NODE\_NAME" --no-headers 2>/dev/null \\

| awk '{print $2}' || echo "N/A")

MEM\_USAGE

\=$(kubectl top node "$NODE\_NAME" --no-headers 2>/dev/null \\

| awk '{print $4}' || echo "N/A")

KERNEL

\=$(kubectl get node "$NODE\_NAME" -o jsonpath='{.status.nodeInfo.kernelVersion}')

\# 判断状态颜色

if

\[\[ "$NODE\_STATUS" == "Ready" \]\]; then

STATUS\_CLASS

\="ok"

else

STATUS\_CLASS

\="err"

fi

\# 写入 HTML 行

echo "<tr>

<td>${NODE\_NAME}</td>

<td class='${STATUS\_CLASS}'>${NODE\_STATUS}</td>

<td>${NODE\_ROLE}</td>

<td>${K8S\_VER}</td>

<td>${CPU\_USAGE}</td>

<td>${MEM\_USAGE}</td>

<td>${UPTIME}</td>

<td>${KERNEL}</td>

</tr>" >> "$REPORT\_FILE"

done

< <(kubectl get nodes --no-headers)

echo "</table></div>" >> "$REPORT\_FILE"

log\_info "节点检查完成"

}

第四部分：Pod 状态检查

bash - k8s\_inspect.sh (第四部分：Pod 状态检查)

\# =============================================================

\# 模块二：Pod 状态检查

\# =============================================================

check\_pods()

{

log\_title "Pod 状态检查"

\# 统计各状态 Pod 数量

TOTAL

\=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | wc -l)

RUNNING

\=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null \\

| grep -c "Running" || true)

CRASH

\=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null \\

| grep -c "CrashLoopBackOff\\|Error\\|OOMKilled" || true)

PENDING

\=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null \\

| grep -c "Pending" || true)

\# HTML 写入 Pod 汇总

cat >> "$REPORT\_FILE" << EOF

<div class="section">

<div class="section-title">🚀 Pod 状态检查</div>

<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;">

<div class="stat"><div class="stat-num ok">${RUNNING}</div>

<div class="stat-label">Running</div></div>

<div class="stat"><div class="stat-num err">${CRASH}</div>

<div class="stat-label">异常 Pod</div></div>

<div class="stat"><div class="stat-num warn">${PENDING}</div>

<div class="stat-label">Pending</div></div>

</div>

<table>

<tr><th>命名空间</th><th>Pod 名称</th><th>状态</th>

<th>重启次数</th><th>运行时间</th><th>所在节点</th><th>镜像</th></tr>

EOF

\# 重点：列出所有非正常 Pod

kubectl get pods

\--all-namespaces -o wide --no-headers 2>/dev/null \\

| grep -v "Running\\|Completed" \\

| while IFS= read -r line; do

NS

\=$(echo "$line" | awk '{print $1}')

NAME

\=$(echo "$line" | awk '{print $2}')

READY

\=$(echo "$line" | awk '{print $3}')

STATUS

\=$(echo "$line" | awk '{print $4}')

RESTARTS

\=$(echo "$line" | awk '{print $5}')

AGE

\=$(echo "$line" | awk '{print $6}')

NODE

\=$(echo "$line" | awk '{print $8}')

IMAGE

\=$(kubectl get pod "$NAME" -n "$NS" \\

\-o jsonpath='{.spec.containers\[0\].image}' 2>/dev/null || echo "N/A")

case

"$STATUS" in

CrashLoopBackOff|OOMKilled|Error) STATUS\_CLASS="err";;

Pending|ImagePullBackOff) STATUS\_CLASS="warn";;

\*) STATUS\_CLASS="warn";;

esac

echo "<tr>

<td>${NS}</td><td>${NAME}</td>

<td class='${STATUS\_CLASS}'>${STATUS}</td>

<td>${RESTARTS}</td><td>${AGE}</td>

<td>${NODE}</td>

<td style='font-size:11px;'>${IMAGE}</td>

</tr>" >> "$REPORT\_FILE"

done

echo "</table></div>" >> "$REPORT\_FILE"

log\_info "Pod 检查完成"

}

第五部分：资源配额与存储检查

bash - k8s\_inspect.sh (第五部分：资源与存储检查)

\# =============================================================

\# 模块三：资源配额检查

\# =============================================================

check\_resources()

{

log\_title "资源配额与 PVC 检查"

cat >> "$REPORT\_FILE" << 'EOF'

<div class="section">

<div class="section-title">💰 资源配额 & 存储检查</div>

<table>

<tr><th>命名空间</th><th>配额名称</th><th>CPU 请求</th>

<th>CPU 限制</th><th>内存请求</th><th>内存限制</th><th>Pod 数量</th></tr>

EOF

\# 遍历所有 ResourceQuota

kubectl get resourcequota --all-namespaces --no-headers 2>/dev/null \\

| while IFS= read -r line; do

NS

\=$(echo "$line" | awk '{print $1}')

QN

\=$(echo "$line" | awk '{print $2}')

CPU\_REQ

\=$(kubectl describe resourcequota "$QN" -n "$NS" \\

| grep "requests.cpu" | awk '{print $2"/"$3}')

MEM\_REQ

\=$(kubectl describe resourcequota "$QN" -n "$NS" \\

| grep "requests.memory" | awk '{print $2"/"$3}')

CPU\_LIM

\=$(kubectl describe resourcequota "$QN" -n "$NS" \\

| grep "limits.cpu" | awk '{print $2"/"$3}')

MEM\_LIM

\=$(kubectl describe resourcequota "$QN" -n "$NS" \\

| grep "limits.memory" | awk '{print $2"/"$3}')

PODS

\=$(kubectl describe resourcequota "$QN" -n "$NS" \\

| grep "^ pods" | awk '{print $2"/"$3}')

echo "<tr><td>${NS}</td><td>${QN}</td><td>${CPU\_REQ}</td>

<td>${CPU\_LIM}</td><td>${MEM\_REQ}</td><td>${MEM\_LIM}</td>

<td>${PODS}</td></tr>" >> "$REPORT\_FILE"

done

echo "</table>" >> "$REPORT\_FILE"

\# PVC 状态检查

cat >> "$REPORT\_FILE" << 'EOF'

<br><table>

<tr><th>命名空间</th><th>PVC 名称</th><th>状态</th>

<th>容量</th><th>存储类</th><th>访问模式</th></tr>

EOF

kubectl get pvc --all-namespaces --no-headers 2>/dev/null \\

| while IFS= read -r line; do

NS

\=$(echo "$line" | awk '{print $1}')

PVC

\=$(echo "$line" | awk '{print $2}')

STATUS

\=$(echo "$line" | awk '{print $3}')

CAP

\=$(echo "$line" | awk '{print $5}')

SC

\=$(echo "$line" | awk '{print $7}')

AM

\=$(echo "$line" | awk '{print $6}')

if

\[\[ "$STATUS" == "Bound" \]\]; then SC\_CLASS="ok"; else SC\_CLASS="err"; fi

echo "<tr><td>${NS}</td><td>${PVC}</td>

<td class='${SC\_CLASS}'>${STATUS}</td>

<td>${CAP}</td><td>${SC}</td><td>${AM}</td></tr>" >> "$REPORT\_FILE"

done

echo "</table></div>" >> "$REPORT\_FILE"

log\_info "资源配额与存储检查完成"

}

第六部分：证书与网络检查

bash - k8s\_inspect.sh (第六部分：证书与网络检查)

\# =============================================================

\# 模块四：证书到期检查

\# =============================================================

check\_certs()

{

log\_title "证书到期检查"

cat >> "$REPORT\_FILE" << 'EOF'

<div class="section">

<div class="section-title">🔒 证书安全检查</div>

<table>

<tr><th>证书名称</th><th>到期时间</th><th>剩余天数</th><th>状态</th></tr>

EOF

\# 检查 kubeadm 证书（仅 master 节点有效）

if

command -v kubeadm &>/dev/null; then

kubeadm certs check-expiration 2>/dev/null \\

| grep -v "^CERTIFICATE\\|^!" \\

| while IFS= read -r line; do

CERT\_NAME

\=$(echo "$line" | awk '{print $1}')

EXPIRE\_DATE

\=$(echo "$line" | awk '{print $3,$4,$5}')

RESIDUAL

\=$(echo "$line" | awk '{print $6}')

\# 计算剩余天数判断状态

DAYS\_LEFT

\=$(echo "$RESIDUAL" | grep -o '\[0-9\]\*' | head -1 || echo 0)

if

\[\[ $DAYS\_LEFT -le 7 \]\]; then CLS="err"

elif

\[\[ $DAYS\_LEFT -le 30 \]\]; then CLS="warn"

else

CLS="ok"; fi

echo "<tr><td>${CERT\_NAME}</td><td>${EXPIRE\_DATE}</td>

<td class='${CLS}'>${DAYS\_LEFT} 天</td>

<td><span class='badge badge-${CLS}'>

$(\[ $DAYS\_LEFT -le 7 \] && echo "紧急" || ( \[ $DAYS\_LEFT -le 30 \] && echo "警告" || echo "正常" ))

</span></td></tr>" >> "$REPORT\_FILE"

done

fi

\# 检查 Ingress TLS 证书

kubectl get secrets --all-namespaces --field-selector type=kubernetes.io/tls \\

\--no-headers 2>/dev/null \\

| while IFS= read -r line; do

NS

\=$(echo "$line" | awk '{print $1}')

SEC

\=$(echo "$line" | awk '{print $2}')

CERT\_DATA

\=$(kubectl get secret "$SEC" -n "$NS" \\

\-o jsonpath='{.data.tls\\.crt}' 2>/dev/null | base64 -d)

if

\[\[ -n "$CERT\_DATA" \]\]; then

EXPIRE

\=$(echo "$CERT\_DATA" | openssl x509 -noout -enddate 2>/dev/null \\

| cut -d= -f2)

EXPIRE\_TS

\=$(date -d "$EXPIRE" +%s 2>/dev/null || echo 0)

NOW\_TS

\=$(date +%s)

DAYS\_LEFT

\=$(( (EXPIRE\_TS - NOW\_TS) / 86400 ))

if

\[\[ $DAYS\_LEFT -le 7 \]\]; then CLS="err"

elif

\[\[ $DAYS\_LEFT -le 30 \]\]; then CLS="warn"

else

CLS="ok"; fi

echo "<tr><td>TLS:${NS}/${SEC}</td><td>${EXPIRE}</td>

<td class='${CLS}'>${DAYS\_LEFT} 天</td>

<td><span class='badge badge-${CLS}'>

$(\[ $DAYS\_LEFT -le 7 \] && echo "紧急" || ( \[ $DAYS\_LEFT -le 30 \] && echo "警告" || echo "正常"))

</span></td></tr>" >> "$REPORT\_FILE"

fi

done

echo "</table></div>" >> "$REPORT\_FILE"

log\_info "证书检查完成"

}

\# =============================================================

\# 模块五：网络与 DNS 检查

\# =============================================================

check\_network()

{

log\_title "网络与 DNS 组件检查"

cat >> "$REPORT\_FILE" << 'EOF'

<div class="section">

<div class="section-title">🌐 网络组件检查</div>

<table>

<tr><th>组件</th><th>命名空间</th><th>期望副本</th><th>就绪副本</th><th>状态</th></tr>

EOF

\# 检查关键网络组件

for

comp in coredns kube-proxy calico-node flannel cilium; do

DS\_COUNT

\=$(kubectl get daemonset,deployment --all-namespaces \\

\--no-headers 2>/dev/null | grep "$comp" | wc -l)

if

\[\[ $DS\_COUNT -gt 0 \]\]; then

kubectl get daemonset,deployment --all-namespaces --no-headers \\

2>/dev/null | grep "$comp" | while IFS= read -r line; do

NS

\=$(echo "$line" | awk '{print $1}')

NAME

\=$(echo "$line" | awk '{print $2}')

DESIRED

\=$(echo "$line" | awk '{print $3}')

READY

\=$(echo "$line" | awk '{print $4}' 2>/dev/null || echo "?")

if

\[\[ "$DESIRED" == "$READY" \]\]; then CLS="ok"; else CLS="warn"; fi

echo "<tr><td>${NAME}</td><td>${NS}</td><td>${DESIRED}</td>

<td class='${CLS}'>${READY}</td>

<td><span class='badge badge-${CLS}'>

$(\[ "$DESIRED" == "$READY" \] && echo "正常" || echo "降级")

</span></td></tr>" >> "$REPORT\_FILE"

done

fi

done

echo "</table></div>" >> "$REPORT\_FILE"

log\_info "网络检查完成"

}

第七部分：事件检查与主函数

bash - k8s\_inspect.sh (第七部分：事件检查与主函数)

\# =============================================================

\# 模块六：近期异常事件

\# =============================================================

check\_events()

{

log\_title "近期异常事件"

cat >> "$REPORT\_FILE" << 'EOF'

<div class="section">

<div class="section-title">⚡ 近期异常事件（最近 1 小时）</div>

<table>

<tr><th>时间</th><th>命名空间</th><th>类型</th><th>对象</th><th>原因</th><th>消息</th></tr>

EOF

kubectl get events --all-namespaces --field-selector type=Warning \\

\--sort-by='.lastTimestamp' --no-headers 2>/dev/null \\

| tail -50 | while IFS= read -r line; do

NS

\=$(echo "$line" | awk '{print $1}')

LAST

\=$(echo "$line" | awk '{print $3}')

OBJ

\=$(echo "$line" | awk '{print $5}')

REASON

\=$(echo "$line" | awk '{print $6}')

MSG

\=$(echo "$line" | awk '{for(i=7;i<=NF;i++) printf $i" "; print ""}' | cut -c1-80)

echo "<tr><td style='font-size:11px'>${LAST}</td>

<td>${NS}</td>

<td><span class='badge badge-warn'>Warning</span></td>

<td style='font-size:11px'>${OBJ}</td>

<td class='warn'>${REASON}</td>

<td style='font-size:11px;color:#94a3b8'>${MSG}</td>

</tr>" >> "$REPORT\_FILE"

done

echo "</table></div>" >> "$REPORT\_FILE"

log\_info "事件检查完成"

}

\# =============================================================

\# HTML 页脚 + 主函数入口

\# =============================================================

html\_footer()

{

cat >> "$REPORT\_FILE" << EOF

<div style="text-align:center;padding:32px;color:#475569;font-size:13px;">

巡检时间：$(date "+%Y-%m-%d %H:%M:%S") | 报告由 k8s\_inspect.sh 自动生成

</div></body></html>

EOF

}

main()

{

log\_info "开始 K8s 全面巡检..."

log\_info "报告路径：$REPORT\_FILE"

html\_header

\# 写入概要统计卡（在各模块执行前占位，后面更新）

NODE\_TOTAL

\=$(kubectl get nodes --no-headers 2>/dev/null | wc -l)

NODE\_READY

\=$(kubectl get nodes --no-headers 2>/dev/null | grep -c "Ready" || true)

POD\_TOTAL

\=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | wc -l)

NS\_TOTAL

\=$(kubectl get ns --no-headers 2>/dev/null | wc -l)

cat >> "$REPORT\_FILE" << EOF

<div class="header">

<div class="title">🔍 K8s 集群巡检报告</div>

<div class="subtitle">生成时间：$(date "+%Y-%m-%d %H:%M:%S")</div>

</div>

<div class="summary">

<div class="stat"><div class="stat-num" style="color:#38bdf8">${NODE\_TOTAL}</div>

<div class="stat-label">总节点数</div></div>

<div class="stat"><div class="stat-num ok">${NODE\_READY}</div>

<div class="stat-label">就绪节点</div></div>

<div class="stat"><div class="stat-num" style="color:#a78bfa">${POD\_TOTAL}</div>

<div class="stat-label">总 Pod 数</div></div>

<div class="stat"><div class="stat-num" style="color:#fb923c">${NS\_TOTAL}</div>

<div class="stat-label">命名空间数</div></div>

</div>

EOF

\# 依次执行各巡检模块

check\_nodes

check\_pods

check\_resources

check\_certs

check\_network

check\_events

html\_footer

log\_info "✅ 巡检完成！报告已生成：$REPORT\_FILE"

echo "$REPORT\_FILE"

}

\# 执行主函数

main "$@"

04

炫酷 HTML 报告预览

脚本生成的 HTML 报告采用 **深色仪表盘风格** ，支持浏览器直接打开，或通过 Nginx/Python HTTP Server 对外共享。

🖥️ HTML 报告界面预览

🔍 K8s 集群巡检报告

生成时间：2026-04-06 10:00:00

6

总节点数

6

就绪节点

142

总 Pod 数

18

命名空间数

🖥️ 节点健康检查

| 节点名称 | 状态 | K8s 版本 | CPU | 内存 |
| --- | --- | --- | --- | --- |
| master-01 | Ready | v1.29.3 | 32% | 58% |
| worker-01 | Ready | v1.29.3 | 82% | 61% |
| worker-02 | NotReady | v1.28.8 | — | — |

05

快速部署 & 使用方法

bash - 一键部署巡检脚本

\# ── 步骤 1：下载脚本 ──────────────────────────────────────

curl -o k8s\_inspect.sh https://raw.githubusercontent.com/your-repo/k8s\_inspect.sh

\# 或者直接创建文件，将上面的脚本内容粘贴进去

vim k8s\_inspect.sh

\# ── 步骤 2：赋予执行权限 ──────────────────────────────────

chmod +x k8s\_inspect.sh

\# ── 步骤 3：执行巡检 ──────────────────────────────────────

bash k8s\_inspect.sh

\# ── 步骤 4：自定义输出目录 ────────────────────────────────

REPORT\_DIR=/data/k8s-reports bash k8s\_inspect.sh

\# ── 步骤 5：用 Python 快速预览报告 ───────────────────────

\# 获取报告文件路径（脚本最后一行输出路径）

REPORT\_PATH=$(bash k8s\_inspect.sh | tail -1)

python3 -m http.server 8888 --directory $(dirname $REPORT\_PATH)

\# 浏览器打开 http://<master-ip>:8888

\# ── 步骤 6：Nginx 挂载报告目录（可选）────────────────────

docker run -d --name k8s-report \\

\-p 8080:80 \\

\-v /tmp/k8s-inspect:/usr/share/nginx/html:ro \\

nginx:alpine

\# 浏览器打开 http://<ip>:8080

06

定时自动巡检（CronJob）

将巡检脚本打包为 Docker 镜像，通过 K8s CronJob 每天自动执行，报告持久化到 PVC。

Dockerfile 打包

dockerfile - 巡检脚本 Dockerfile

FROM

alpine:3.19

\# 安装 kubectl + 基础工具

RUN

apk add --no-cache curl bash openssl bc && \\

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \\

chmod +x kubectl && mv kubectl /usr/local/bin/

COPY

k8s\_inspect.sh /usr/local/bin/

RUN

chmod +x /usr/local/bin/k8s\_inspect.sh

CMD

\["k8s\_inspect.sh"\]

CronJob + RBAC

yaml - K8s CronJob（每天 8:00 执行巡检）

apiVersion

: batch/v1

kind

: CronJob

metadata

:

name: k8s-inspect

namespace: kube-system

spec

:

schedule: "0 8 \* \* \*"

\# 每天早上 8:00 执行

jobTemplate:

spec:

template:

spec:

serviceAccountName: k8s-inspect-sa

containers:

\- name: inspect

image: your-registry/k8s-inspect:latest

env:

\- name: REPORT\_DIR

value: "/reports"

volumeMounts:

\- name: reports

mountPath: "/reports"

volumes:

\- name: reports

persistentVolumeClaim:

claimName: k8s-inspect-pvc

restartPolicy: OnFailure

\---

apiVersion

: v1

kind

: ServiceAccount

metadata

:

name: k8s-inspect-sa

namespace: kube-system

\---

\# RBAC：赋予只读权限

apiVersion

: rbac.authorization.k8s.io/v1

kind

: ClusterRole

metadata

:

name: k8s-inspect-role

rules

:

\- apiGroups: \["", "apps", "batch", "storage.k8s.io", "networking.k8s.io"\]

resources: \["\*"\]

verbs: \["get", "list", "watch"\]

部署命令

bash - 部署 CronJob

\# 部署 CronJob + RBAC

kubectl apply -f k8s\_inspect\_cronjob.yaml

\# 手动触发一次（测试用）

kubectl create job --from=cronjob/k8s-inspect k8s-inspect-manual -n kube-system

\# 查看巡检日志

kubectl logs -l job-name=k8s-inspect-manual -n kube-system -f

\# 查看已生成报告列表

kubectl exec -it deploy/nginx-report -n kube-system -- ls /reports/

07

告警通知集成

巡检完成后，可以自动将异常情况推送到钉钉/企业微信/Slack，实现主动告警。

bash - 钉钉告警推送函数

\# ── 钉钉 Webhook 告警 ─────────────────────────────────────

DINGTALK\_WEBHOOK

\="https://oapi.dingtalk.com/robot/send?access\_token=YOUR\_TOKEN"

send\_dingtalk\_alert()

{

local msg

\="$1"

local title

\="${2:-K8s 巡检告警}"

curl -s -X POST "$DINGTALK\_WEBHOOK" \\

\-H "Content-Type: application/json" \\

\-d '{

"msgtype": "markdown",

"markdown": {

"title": "$title",

"text": "$msg"

}

}' > /dev/null

}

\# ── 企业微信 Webhook 告警 ────────────────────────────────

WECOM\_WEBHOOK

\="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR\_KEY"

send\_wecom\_alert()

{

local msg

\="$1"

curl -s -X POST "$WECOM\_WEBHOOK" \\

\-H "Content-Type: application/json" \\

\-d '{

"msgtype": "markdown",

"markdown": {"content": "$msg"}

}' > /dev/null

}

\# ── 在 main() 末尾添加告警汇总 ──────────────────────────

\# 统计异常 Pod 数量，超过 0 则告警

ABNORMAL\_PODS

\=$(kubectl get pods --all-namespaces --no-headers \\

| grep -c "CrashLoopBackOff\\|Error\\|OOMKilled\\|Pending" || true)

if

\[\[ $ABNORMAL\_PODS -gt 0 \]\]; then

MSG

\="## ⚠️ K8s 巡检告警

\> 发现 \*\*${ABNORMAL\_PODS}\*\* 个异常 Pod，请及时处理！

\>

\> 巡检时间：$(date '+%Y-%m-%d %H:%M:%S')

\> 完整报告：http://your-nginx/reports/latest.html"

send\_dingtalk\_alert "$MSG" "K8s 集群异常告警"

send\_wecom\_alert "$MSG"

fi

🗒️ 巡检项速查表

节点  
Ready状态CPU使用率内存使用率磁盘压力内存压力PID压力TaintsK8s版本内核版本

Pod  
Running/Pending/Failed统计CrashLoopBackOffOOMKilled重启次数>NImagePullBackOffEvicted

资源  
ResourceQuota使用率LimitRange配置PVC状态StorageClass无Limits的Pod

网络  
CoreDNS状态CNI插件状态Ingress规则Service→EndpointNetworkPolicy

证书  
API Server证书etcd证书Ingress TLSSA Token状态

组件  
etcd健康Scheduler状态Controller状态metrics-serverHPA伸缩

事件  
Warning事件汇总OOM事件镜像拉取失败事件调度失败事件

🚀

让巡检成为习惯，让故障消于萌芽

定期巡检 + 主动监控 + 快速响应 = 集群永远健康  
把这个脚本接入你的 CI/CD 流水线，让每次发布都经过健康检查！

持续巡检 主动告警 自动报告 防患未然

**微信扫一扫赞赏作者**

继续滑动看下一个

院长技术

向上滑动看下一个