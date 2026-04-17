---
name: k8s-inspect
description: Run a comprehensive Kubernetes cluster health inspection using kubectl and generate a dark-themed HTML dashboard report. Checks nodes, pods, resources, certificates, network components, and warning events. Use this skill whenever the user mentions cluster inspection, k8s health check, cluster audit, node status, pod troubleshooting, certificate expiry, resource usage review, or wants any kind of cluster status report — even if they don't explicitly say "inspect" or "health check". Also trigger for pre-deployment checks, incident triage, or cluster readiness questions.
---

# K8s Inspect

Execute a comprehensive Kubernetes cluster health inspection via `k8s_inspect.sh`, generating a dark-themed HTML dashboard report.

## What it does

The bundled script performs **read-only** inspection across six modules:

| Module | Checks |
|--------|--------|
| **Nodes** | Ready status, CPU/Memory usage (metrics-server), roles, K8s version, kernel, uptime |
| **Pods** | Status distribution, abnormal pods with images, restart counts |
| **Resources** | ResourceQuota usage, PVC status/capacity/StorageClass |
| **Certificates** | kubeadm certs expiry, Ingress TLS secrets expiry (days remaining) |
| **Network** | CoreDNS, kube-proxy, CNI plugin (Calico/Flannel/Cilium) replica health |
| **Events** | Last 50 Warning events across all namespaces |

## Prerequisites

- `kubectl` (v1.20+) on PATH with valid kubeconfig
- `bash`, `bc`, `awk` (pre-installed on macOS/Linux)
- `metrics-server` (optional — CPU/Memory stats show N/A without it)

## Usage

```bash
# Default kubeconfig (~/.kube/config)
bash k8s_inspect.sh

# Custom kubeconfig
bash k8s_inspect.sh --kubeconfig /path/to/kubeconfig

# Custom output directory
bash k8s_inspect.sh --kubeconfig /path/to/kubeconfig --output-dir /tmp/reports
```

## Processing output

The script prints a structured summary to stdout and the HTML report path:

```
===== INSPECTION SUMMARY =====
Nodes: 3 total, 3 ready
Pods: 45 total, 2 abnormal, 1 pending
Warning Events: 3
Report: /tmp/k8s-inspect/k8s_report_20260417_120000.html
===============================
```

Capture the report path:
```bash
REPORT=$(bash k8s_inspect.sh 2>/dev/null | grep "^Report:" | awk '{print $2}')
```

## Workflows

- **Daily health check** — schedule via cron or K8s CronJob
- **Incident triage** — run immediately when alerts fire to snapshot cluster state
- **Pre-deployment audit** — verify cluster health before major rollouts

## Security

Only read-only operations (`kubectl get`, `kubectl top`, `kubectl describe`). No cluster state is modified.
