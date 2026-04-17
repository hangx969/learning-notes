#!/bin/bash
# =============================================================
# K8s 全面巡检脚本 v2.1 (AI Skill Edition)
# 功能：全面检查 K8s 集群健康状态，生成深色仪表盘风格 HTML 报告
# 用法：bash k8s_inspect.sh [--kubeconfig PATH] [--output-dir DIR]
# 依赖：kubectl、bc、awk（已预装于大多数 Linux/macOS）
# =============================================================

# ── 参数解析 ──────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --kubeconfig)   export KUBECONFIG="$2"; shift 2 ;;
        --output-dir)   REPORT_DIR="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: bash k8s_inspect.sh [--kubeconfig PATH] [--output-dir DIR]"
            exit 0 ;;
        *)  shift ;;
    esac
done

# ── 全局配置 ──────────────────────────────────────────────
REPORT_DIR="${REPORT_DIR:-/tmp/k8s-inspect}"
REPORT_FILE="${REPORT_DIR}/k8s_report_$(date +%Y%m%d_%H%M%S).html"
LOG_FILE="${REPORT_DIR}/inspect.log"
THRESHOLD_CPU=80
THRESHOLD_MEM=80
THRESHOLD_DISK=85
THRESHOLD_RESTART=5
CERT_WARN_DAYS=30

# ── 颜色输出 ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ── 初始化目录 ────────────────────────────────────────────
mkdir -p "$REPORT_DIR"

# ── 工具函数 ──────────────────────────────────────────────
log_info()  { echo -e "${GREEN}[INFO]${NC} $*" >&2; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
log_title() { echo -e "${BLUE}\n====== $* ======${NC}" >&2; }

# ── 连接检查 ──────────────────────────────────────────────
check_connection() {
    if ! kubectl cluster-info &>/dev/null; then
        log_error "无法连接到 Kubernetes 集群！"
        log_error "请检查 kubeconfig 配置或使用 --kubeconfig 指定路径"
        [[ -n "${KUBECONFIG:-}" ]] && log_error "当前 KUBECONFIG: $KUBECONFIG"
        exit 1
    fi
    log_info "集群连接成功"
}

# =============================================================
# HTML 报告构建函数
# =============================================================
html_header() {
cat > "$REPORT_FILE" << 'HTMLEOF'
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

# =============================================================
# 模块一：节点健康检查
# =============================================================
check_nodes() {
    log_title "节点健康检查"

    cat >> "$REPORT_FILE" << 'EOF'
<div class="section">
<div class="section-title">🖥️ 节点健康检查</div>
<table>
<tr><th>节点名称</th><th>状态</th><th>角色</th><th>K8s 版本</th>
<th>CPU 使用</th><th>内存使用</th><th>运行时间</th><th>内核版本</th></tr>
EOF

    local ALL_NODE_TOP
    ALL_NODE_TOP=$(kubectl top nodes --no-headers 2>/dev/null || true)
    local ALL_NODE_KERNELS
    ALL_NODE_KERNELS=$(kubectl get nodes -o custom-columns='NAME:.metadata.name,KERNEL:.status.nodeInfo.kernelVersion' --no-headers 2>/dev/null)

    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        NODE_NAME=$(echo "$line" | awk '{print $1}')
        NODE_STATUS=$(echo "$line" | awk '{print $2}')
        NODE_ROLE=$(echo "$line" | awk '{print $3}')
        [[ "$NODE_ROLE" == "<none>" ]] && NODE_ROLE="worker"
        K8S_VER=$(echo "$line" | awk '{print $5}')
        UPTIME=$(echo "$line" | awk '{print $4}')

        CPU_USAGE=$(echo "$ALL_NODE_TOP" | awk -v n="$NODE_NAME" '$1==n{print $2}')
        MEM_USAGE=$(echo "$ALL_NODE_TOP" | awk -v n="$NODE_NAME" '$1==n{print $4}')
        [[ -z "$CPU_USAGE" ]] && CPU_USAGE="N/A"
        [[ -z "$MEM_USAGE" ]] && MEM_USAGE="N/A"
        KERNEL=$(echo "$ALL_NODE_KERNELS" | awk -v n="$NODE_NAME" '$1==n{print $2}')

        if [[ "$NODE_STATUS" == "Ready" ]]; then
            STATUS_CLASS="ok"
        else
            STATUS_CLASS="err"
        fi

        cat >> "$REPORT_FILE" << NODEEOF
<tr>
    <td>${NODE_NAME}</td>
    <td class='${STATUS_CLASS}'>${NODE_STATUS}</td>
    <td>${NODE_ROLE}</td>
    <td>${K8S_VER}</td>
    <td>${CPU_USAGE}</td>
    <td>${MEM_USAGE}</td>
    <td>${UPTIME}</td>
    <td>${KERNEL}</td>
</tr>
NODEEOF
    done < <(kubectl get nodes --no-headers 2>/dev/null)

    echo "</table></div>" >> "$REPORT_FILE"
    log_info "节点检查完成"
}

# =============================================================
# 模块二：Pod 状态检查
# =============================================================
check_pods() {
    log_title "Pod 状态检查"

    local ALL_PODS_DATA
    ALL_PODS_DATA=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null)
    TOTAL=$(echo "$ALL_PODS_DATA" | wc -l | tr -d ' ')
    RUNNING=$(echo "$ALL_PODS_DATA" | grep -c "Running" || true)
    CRASH=$(echo "$ALL_PODS_DATA" | grep -c "CrashLoopBackOff\|Error\|OOMKilled" || true)
    PENDING=$(echo "$ALL_PODS_DATA" | grep -c "Pending" || true)

    # 保存到全局变量供摘要使用
    G_POD_TOTAL=$TOTAL
    G_POD_RUNNING=$RUNNING
    G_POD_CRASH=$CRASH
    G_POD_PENDING=$PENDING

    cat >> "$REPORT_FILE" << EOF
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

    kubectl get pods --all-namespaces -o wide --no-headers 2>/dev/null \
        | grep -v "Running\|Completed" \
        | while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        NS=$(echo "$line" | awk '{print $1}')
        NAME=$(echo "$line" | awk '{print $2}')
        STATUS=$(echo "$line" | awk '{print $4}')
        RESTARTS=$(echo "$line" | awk '{print $5}')
        AGE=$(echo "$line" | awk '{print $6}')
        NODE=$(echo "$line" | awk '{print $8}')
        IMAGE=$(kubectl get pod "$NAME" -n "$NS" \
            -o jsonpath='{.spec.containers[0].image}' 2>/dev/null || echo "N/A")

        case "$STATUS" in
            CrashLoopBackOff|OOMKilled|Error) STATUS_CLASS="err";;
            *) STATUS_CLASS="warn";;
        esac

        cat >> "$REPORT_FILE" << PODEOF
<tr>
    <td>${NS}</td><td>${NAME}</td>
    <td class='${STATUS_CLASS}'>${STATUS}</td>
    <td>${RESTARTS}</td><td>${AGE}</td>
    <td>${NODE}</td>
    <td style='font-size:11px;'>${IMAGE}</td>
</tr>
PODEOF
    done

    echo "</table></div>" >> "$REPORT_FILE"
    log_info "Pod 检查完成"
}

# =============================================================
# 模块三：资源配额检查
# =============================================================
check_resources() {
    log_title "资源配额与 PVC 检查"

    cat >> "$REPORT_FILE" << 'EOF'
<div class="section">
<div class="section-title">💰 资源配额 & 存储检查</div>
<table>
<tr><th>命名空间</th><th>配额名称</th><th>CPU 请求</th>
<th>CPU 限制</th><th>内存请求</th><th>内存限制</th><th>Pod 数量</th></tr>
EOF

    kubectl get resourcequota --all-namespaces --no-headers 2>/dev/null \
        | while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        NS=$(echo "$line" | awk '{print $1}')
        QN=$(echo "$line" | awk '{print $2}')
        CPU_REQ=$(kubectl describe resourcequota "$QN" -n "$NS" 2>/dev/null \
            | grep "requests.cpu" | awk '{print $2"/"$3}')
        MEM_REQ=$(kubectl describe resourcequota "$QN" -n "$NS" 2>/dev/null \
            | grep "requests.memory" | awk '{print $2"/"$3}')
        CPU_LIM=$(kubectl describe resourcequota "$QN" -n "$NS" 2>/dev/null \
            | grep "limits.cpu" | awk '{print $2"/"$3}')
        MEM_LIM=$(kubectl describe resourcequota "$QN" -n "$NS" 2>/dev/null \
            | grep "limits.memory" | awk '{print $2"/"$3}')
        PODS=$(kubectl describe resourcequota "$QN" -n "$NS" 2>/dev/null \
            | grep "^ pods" | awk '{print $2"/"$3}')

        cat >> "$REPORT_FILE" << RQEOF
<tr><td>${NS}</td><td>${QN}</td><td>${CPU_REQ:-N/A}</td>
    <td>${CPU_LIM:-N/A}</td><td>${MEM_REQ:-N/A}</td><td>${MEM_LIM:-N/A}</td>
    <td>${PODS:-N/A}</td></tr>
RQEOF
    done

    echo "</table>" >> "$REPORT_FILE"

    # PVC 状态检查
    cat >> "$REPORT_FILE" << 'EOF'
<br><table>
<tr><th>命名空间</th><th>PVC 名称</th><th>状态</th>
<th>容量</th><th>存储类</th><th>访问模式</th></tr>
EOF

    kubectl get pvc --all-namespaces --no-headers 2>/dev/null \
        | while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        NS=$(echo "$line" | awk '{print $1}')
        PVC=$(echo "$line" | awk '{print $2}')
        STATUS=$(echo "$line" | awk '{print $3}')
        CAP=$(echo "$line" | awk '{print $5}')
        SC=$(echo "$line" | awk '{print $7}')
        AM=$(echo "$line" | awk '{print $6}')

        if [[ "$STATUS" == "Bound" ]]; then SC_CLASS="ok"; else SC_CLASS="err"; fi

        cat >> "$REPORT_FILE" << PVCEOF
<tr><td>${NS}</td><td>${PVC}</td>
    <td class='${SC_CLASS}'>${STATUS}</td>
    <td>${CAP}</td><td>${SC}</td><td>${AM}</td></tr>
PVCEOF
    done

    echo "</table></div>" >> "$REPORT_FILE"
    log_info "资源配额与存储检查完成"
}

# =============================================================
# 模块四：证书到期检查
# =============================================================
check_certs() {
    log_title "证书到期检查"

    cat >> "$REPORT_FILE" << 'EOF'
<div class="section">
<div class="section-title">🔒 证书安全检查</div>
<table>
<tr><th>证书名称</th><th>到期时间</th><th>剩余天数</th><th>状态</th></tr>
EOF

    # 检查 kubeadm 证书（仅 master 节点有效）
    if command -v kubeadm &>/dev/null; then
        kubeadm certs check-expiration 2>/dev/null \
            | grep -v "^CERTIFICATE\|^!" \
            | while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            CERT_NAME=$(echo "$line" | awk '{print $1}')
            EXPIRE_DATE=$(echo "$line" | awk '{print $3,$4,$5}')
            RESIDUAL=$(echo "$line" | awk '{print $6}')
            DAYS_LEFT=$(echo "$RESIDUAL" | grep -o '[0-9]*' | head -1 || echo 0)

            if [[ ${DAYS_LEFT:-0} -le 7 ]]; then CLS="err"
            elif [[ ${DAYS_LEFT:-0} -le 30 ]]; then CLS="warn"
            else CLS="ok"; fi

            local STATUS_TEXT="正常"
            [[ ${DAYS_LEFT:-0} -le 30 ]] && STATUS_TEXT="警告"
            [[ ${DAYS_LEFT:-0} -le 7 ]] && STATUS_TEXT="紧急"

            cat >> "$REPORT_FILE" << CERTEOF
<tr><td>${CERT_NAME}</td><td>${EXPIRE_DATE}</td>
    <td class='${CLS}'>${DAYS_LEFT} 天</td>
    <td><span class='badge badge-${CLS}'>${STATUS_TEXT}</span></td></tr>
CERTEOF
        done
    fi

    # 检查 Ingress TLS 证书
    kubectl get secrets --all-namespaces --field-selector type=kubernetes.io/tls \
        --no-headers 2>/dev/null \
        | while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        NS=$(echo "$line" | awk '{print $1}')
        SEC=$(echo "$line" | awk '{print $2}')
        CERT_DATA=$(kubectl get secret "$SEC" -n "$NS" \
            -o jsonpath='{.data.tls\.crt}' 2>/dev/null | base64 -d 2>/dev/null)

        if [[ -n "$CERT_DATA" ]]; then
            EXPIRE=$(echo "$CERT_DATA" | openssl x509 -noout -enddate 2>/dev/null \
                | cut -d= -f2)
            if [[ -n "$EXPIRE" ]]; then
                # macOS 和 Linux 的 date 命令兼容
                if date --version &>/dev/null; then
                    # GNU date (Linux)
                    EXPIRE_TS=$(date -d "$EXPIRE" +%s 2>/dev/null || echo 0)
                else
                    # BSD date (macOS)
                    EXPIRE_TS=$(date -jf "%b %d %H:%M:%S %Y %Z" "$EXPIRE" +%s 2>/dev/null || echo 0)
                fi
                NOW_TS=$(date +%s)
                DAYS_LEFT=$(( (EXPIRE_TS - NOW_TS) / 86400 ))

                if [[ $DAYS_LEFT -le 7 ]]; then CLS="err"
                elif [[ $DAYS_LEFT -le 30 ]]; then CLS="warn"
                else CLS="ok"; fi

                local STATUS_TEXT="正常"
                [[ $DAYS_LEFT -le 30 ]] && STATUS_TEXT="警告"
                [[ $DAYS_LEFT -le 7 ]] && STATUS_TEXT="紧急"

                cat >> "$REPORT_FILE" << TLSEOF
<tr><td>TLS:${NS}/${SEC}</td><td>${EXPIRE}</td>
    <td class='${CLS}'>${DAYS_LEFT} 天</td>
    <td><span class='badge badge-${CLS}'>${STATUS_TEXT}</span></td></tr>
TLSEOF
            fi
        fi
    done

    echo "</table></div>" >> "$REPORT_FILE"
    log_info "证书检查完成"
}

# =============================================================
# 模块五：网络与 DNS 检查
# =============================================================
check_network() {
    log_title "网络与 DNS 组件检查"

    cat >> "$REPORT_FILE" << 'EOF'
<div class="section">
<div class="section-title">🌐 网络组件检查</div>
<table>
<tr><th>组件</th><th>命名空间</th><th>期望副本</th><th>就绪副本</th><th>状态</th></tr>
EOF

    for comp in coredns kube-proxy calico-node flannel cilium; do
        # DaemonSet 检查
        kubectl get daemonset --all-namespaces --no-headers 2>/dev/null \
            | grep "$comp" | while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            NS=$(echo "$line" | awk '{print $1}')
            NAME=$(echo "$line" | awk '{print $2}')
            DESIRED=$(echo "$line" | awk '{print $3}')
            READY=$(echo "$line" | awk '{print $5}')

            if [[ "$DESIRED" == "$READY" ]]; then
                CLS="ok"; STATUS_TEXT="正常"
            else
                CLS="warn"; STATUS_TEXT="降级"
            fi

            cat >> "$REPORT_FILE" << NETEOF
<tr><td>ds/${NAME}</td><td>${NS}</td><td>${DESIRED}</td>
    <td class='${CLS}'>${READY}</td>
    <td><span class='badge badge-${CLS}'>${STATUS_TEXT}</span></td></tr>
NETEOF
        done

        # Deployment 检查
        kubectl get deployment --all-namespaces --no-headers 2>/dev/null \
            | grep "$comp" | while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            NS=$(echo "$line" | awk '{print $1}')
            NAME=$(echo "$line" | awk '{print $2}')
            READY_STR=$(echo "$line" | awk '{print $3}')  # format: "2/2"
            DESIRED=$(echo "$READY_STR" | cut -d'/' -f2)
            READY=$(echo "$READY_STR" | cut -d'/' -f1)

            if [[ "$DESIRED" == "$READY" ]]; then
                CLS="ok"; STATUS_TEXT="正常"
            else
                CLS="warn"; STATUS_TEXT="降级"
            fi

            cat >> "$REPORT_FILE" << NETEOF
<tr><td>deploy/${NAME}</td><td>${NS}</td><td>${DESIRED}</td>
    <td class='${CLS}'>${READY}</td>
    <td><span class='badge badge-${CLS}'>${STATUS_TEXT}</span></td></tr>
NETEOF
        done
    done

    echo "</table></div>" >> "$REPORT_FILE"
    log_info "网络检查完成"
}

# =============================================================
# 模块六：近期异常事件
# =============================================================
check_events() {
    log_title "近期异常事件"

    cat >> "$REPORT_FILE" << 'EOF'
<div class="section">
<div class="section-title">⚡ 近期异常事件（Warning Events）</div>
<table>
<tr><th>时间</th><th>命名空间</th><th>类型</th><th>对象</th><th>原因</th><th>消息</th></tr>
EOF

    G_WARNING_COUNT=0
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        NS=$(echo "$line" | awk '{print $1}')
        LAST=$(echo "$line" | awk '{print $2}')
        OBJ=$(echo "$line" | awk '{print $5}')
        REASON=$(echo "$line" | awk '{print $4}')
        MSG=$(echo "$line" | awk '{for(i=6;i<=NF;i++) printf $i" "; print ""}' | cut -c1-80)
        G_WARNING_COUNT=$((G_WARNING_COUNT + 1))

        cat >> "$REPORT_FILE" << EVTEOF
<tr><td style='font-size:11px'>${LAST}</td>
    <td>${NS}</td>
    <td><span class='badge badge-warn'>Warning</span></td>
    <td style='font-size:11px'>${OBJ}</td>
    <td class='warn'>${REASON}</td>
    <td style='font-size:11px;color:#94a3b8'>${MSG}</td>
</tr>
EVTEOF
    done < <(kubectl get events --all-namespaces --field-selector type=Warning \
        --sort-by='.lastTimestamp' --no-headers 2>/dev/null | tail -50)

    echo "</table></div>" >> "$REPORT_FILE"
    log_info "事件检查完成 (${G_WARNING_COUNT} 条警告)"
}

# =============================================================
# HTML 页脚
# =============================================================
html_footer() {
    cat >> "$REPORT_FILE" << EOF
<div style="text-align:center;padding:32px;color:#475569;font-size:13px;">
巡检时间：$(date "+%Y-%m-%d %H:%M:%S") | 报告由 k8s_inspect.sh (AI Skill Edition) 自动生成
</div></body></html>
EOF
}

# =============================================================
# 主函数入口
# =============================================================
main() {
    log_info "开始 K8s 全面巡检..."
    [[ -n "${KUBECONFIG:-}" ]] && log_info "使用 KUBECONFIG: $KUBECONFIG"

    # 连接检查
    check_connection

    log_info "报告路径：$REPORT_FILE"

    html_header

    # 获取概要统计数据
    NODE_TOTAL=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d ' ')
    NODE_READY=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready" || echo "0")
    POD_TOTAL=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null | wc -l | tr -d ' ')
    NS_TOTAL=$(kubectl get ns --no-headers 2>/dev/null | wc -l | tr -d ' ')

    # 写入概要统计卡
    cat >> "$REPORT_FILE" << EOF
<div class="header">
    <div class="title">🔍 K8s 集群巡检报告</div>
    <div class="subtitle">生成时间：$(date "+%Y-%m-%d %H:%M:%S") | KUBECONFIG: ${KUBECONFIG:-default}</div>
</div>
<div class="summary">
    <div class="stat"><div class="stat-num" style="color:#38bdf8">${NODE_TOTAL}</div>
        <div class="stat-label">总节点数</div></div>
    <div class="stat"><div class="stat-num ok">${NODE_READY}</div>
        <div class="stat-label">就绪节点</div></div>
    <div class="stat"><div class="stat-num" style="color:#a78bfa">${POD_TOTAL}</div>
        <div class="stat-label">总 Pod 数</div></div>
    <div class="stat"><div class="stat-num" style="color:#fb923c">${NS_TOTAL}</div>
        <div class="stat-label">命名空间数</div></div>
</div>
EOF

    # 依次执行各巡检模块
    check_nodes
    check_pods
    check_resources
    check_certs
    check_network
    check_events

    html_footer

    log_info "✅ 巡检完成！"

    # ── 结构化摘要输出（供 AI Agent 解析）──────────────────
    ALL_PODS=$(kubectl get pods --all-namespaces --no-headers 2>/dev/null)
    ABNORMAL_PODS=$(echo "$ALL_PODS" | grep -c "CrashLoopBackOff\|Error\|OOMKilled" || true)
    PENDING_PODS=$(echo "$ALL_PODS" | grep -c "Pending" || true)
    WARNING_EVENTS=$(kubectl get events --all-namespaces --field-selector type=Warning \
        --no-headers 2>/dev/null | wc -l | tr -d ' ')

    echo ""
    echo "===== INSPECTION SUMMARY ====="
    echo "Nodes: ${NODE_TOTAL} total, ${NODE_READY} ready"
    echo "Pods: ${POD_TOTAL} total, ${ABNORMAL_PODS} abnormal, ${PENDING_PODS} pending"
    echo "Warning Events: ${WARNING_EVENTS}"
    echo "Report: ${REPORT_FILE}"
    echo "==============================="
}

# 执行主函数
main "$@"
