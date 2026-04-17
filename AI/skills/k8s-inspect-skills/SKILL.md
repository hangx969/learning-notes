---
name: k8s-inspect
description: Run a comprehensive Kubernetes cluster health inspection using kubectl and generate a dark-themed HTML dashboard report. Checks nodes, pods, resources, certificates, network components, and warning events. Use when you need to audit cluster health, troubleshoot issues, or generate visual status reports.
license: MIT
metadata:
  author: User
  version: "1.0.0"
  keywords: "kubernetes,k8s,inspect,health-check,html,nodes,pods,shell,kubectl"
compatibility: Requires kubectl (v1.20+), bash, bc, awk, and an active kubeconfig connection to a Kubernetes cluster. Works on macOS and Linux.
---

# K8s Inspect Skill (Shell)

Execute a comprehensive Kubernetes cluster health inspection using shell scripting and kubectl, generating a dark-themed HTML dashboard report.

## Overview

This skill enables agents to autonomously:
- **Check Node Health** — Readiness, CPU/Memory usage (via metrics-server), kubelet version, kernel version, uptime
- **Analyze Pod Status** — Running/Pending/CrashLoopBackOff/OOMKilled counts, abnormal pod listing with images and restart counts
- **Audit Resource Quotas** — ResourceQuota usage, PVC status and capacity, StorageClass binding
- **Verify Certificates** — kubeadm certificates expiration, Ingress TLS secrets expiration with countdown
- **Inspect Network** — CoreDNS, kube-proxy, Calico/Flannel/Cilium replica health
- **Extract Warning Events** — Recent Warning events across all namespaces
- **Generate Reports** — Compile all data into a polished dark-themed HTML dashboard

## Prerequisites

1. **kubectl** installed and on PATH (v1.20+)
2. **bash**, **bc**, **awk** (pre-installed on most systems)
3. **kubeconfig** file with cluster credentials
4. **metrics-server** (optional, for CPU/Memory usage stats)

## Quick Start

```bash
# Basic usage (uses default ~/.kube/config)
bash k8s_inspect.sh

# Specify a custom kubeconfig
bash k8s_inspect.sh --kubeconfig /path/to/kubeconfig

# Custom output directory
bash k8s_inspect.sh --kubeconfig /path/to/kubeconfig --output-dir /tmp/my-reports
```

## Essential Operations

### Run Full Inspection

```bash
# The script outputs the report file path as the last line of stdout
REPORT_PATH=$(bash k8s_inspect.sh --kubeconfig /path/to/kubeconfig 2>/dev/null | tail -1)
echo "Report generated at: $REPORT_PATH"
```

### Process the Output

The script generates an HTML file and prints its path. Agents should:
1. Run the script and capture the output path
2. Read the HTML file or serve it for the user to view
3. Optionally parse the structured summary printed to stdout

### Output Format

The script prints a structured summary before the file path:

```
===== INSPECTION SUMMARY =====
Nodes: 3 total, 3 ready
Pods: 45 total, 42 running, 2 abnormal, 1 pending
Warning Events: 3
Report: /tmp/k8s-inspect/k8s_report_20260417_120000.html
===============================
```

## Inspection Modules

| Module | Checks |
|--------|--------|
| **Nodes** | Ready status, CPU/Memory usage, roles, K8s version, kernel, uptime |
| **Pods** | Status distribution, abnormal pods with details, restart counts |
| **Resources** | ResourceQuota usage, PVC status/capacity/StorageClass |
| **Certificates** | kubeadm certs expiry, Ingress TLS secrets expiry (days remaining) |
| **Network** | CoreDNS, kube-proxy, CNI plugin (Calico/Flannel/Cilium) replica health |
| **Events** | Last 50 Warning events across all namespaces |

## Common Workflows

### 1. Daily Health Check
Schedule via cron or K8s CronJob to generate daily reports.

### 2. Incident Triage
When an alert fires, run immediately to capture the cluster state snapshot.

### 3. Pre-deployment Audit
Run before major deployments to ensure cluster is healthy.

## Security Notes

The script only performs **read-only** operations (`kubectl get`, `kubectl top`, `kubectl describe`). No cluster state is modified.

## Environment Variables

- `KUBECONFIG` — Path to kubeconfig file (alternative to `--kubeconfig` flag)
- `REPORT_DIR` — Output directory for reports (alternative to `--output-dir` flag)

## Differences from k8s-report-skills (Python)

| Aspect | k8s-inspect (Shell) | k8s-report (Python) |
|--------|---------------------|---------------------|
| Language | Bash + kubectl | Python kubernetes client |
| Dependencies | kubectl only | kubernetes + Jinja2 packages |
| Report Style | Dark dashboard theme | Light professional theme |
| Cert Checks | Yes (kubeadm + TLS) | No |
| Network Checks | Yes (CNI/CoreDNS) | No |
| PV/PVC Checks | Yes | Yes |
| Best For | Ops engineers, CronJob | Agent API integration |

---

**Version:** 1.0.0
**License:** MIT
**Compatible with:** kubectl v1.20+, Kubernetes v1.20+, Bash 4+
