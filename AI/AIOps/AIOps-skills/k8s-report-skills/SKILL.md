---
name: k8s-report
description: Inspect Kubernetes clusters and generate HTML health reports. Query cluster status, node health, pod metrics, deployment replicas, and recent warning events. Use when you need a comprehensive overview of a Kubernetes cluster's health or need to generate status reports for email notifications.
license: MIT
metadata:
  author: User
  version: "1.0.0"
  keywords: "kubernetes,k8s,inspect,report,health-check,html,nodes,pods"
compatibility: Requires python kubernetes client (v28.1.0+) and an active kubeconfig connection. Works anywhere Python can run and connect to the K8s API server.
---

# K8s Inspector Skill

Execute a comprehensive Kubernetes cluster inspection using Python and the `kubernetes` Python client, generating a beautifully formatted HTML report.

## Overview

This skill enables agents to autonomously:
- **Query Cluster Status** — Get Kubernetes version, base platform, and total namespace counts.
- **Inspect Nodes** — Check node readiness, roles, CPU/Memory usage (if metrics-server is available), and kubelet versions.   
- **Analyze Pods** — Categorize pods into normal and abnormal (e.g., CrashLoopBackOff, Pending), identifying restarts and specific failure reasons.
- **Validate Deployments** — Identify deployments where the available replicas are fewer than the desired replicas (capacity issues).
- **Extract Events** — Fetch all Warning events generated within the last 1 hour across all namespaces.
- **Generate Reports** — Compile all parsed data into a polished HTML template designed for email sharing.

## Prerequisites

1. **Python 3.8+** installed. 
2. **Required Packages**: `kubernetes` and `jinja2`.
3. **kubeconfig** file configured with cluster credentials (default: `~/.kube/config`) or running inside a Pod with ServiceAccount permissions.

## Quick Setup

### Install Dependencies

```bash
pip install -r requirements.txt
```
*(Ensure `kubernetes>=28.1.0` and `Jinja2>=3.1.2` are included in your requirements)*

**Verify Connection (Manual Test):**
```bash
python k8s_inspector.py
```
*This will execute the script locally and output a `test_report.html` if the connection is successful.*

## Essential Operations

### Run Full Inspection

In Python, instantiate the skill and generate the HTML report:

```python
from k8s_inspector import run_k8s_inspection_skill

# Uses default ~/.kube/config or InCluster config
html_report = run_k8s_inspection_skill()

# Or specify a custom kubeconfig path
html_report = run_k8s_inspection_skill(kubeconfig_path="/path/to/custom/kubeconfig")
```

### Process the Output

The skill returns a raw HTML string. Agents should handle this string by:
1. Saving it to a `.html` file for the user to open.
2. Passing the string as the HTML body to an Email or Notification Skill.

```python
# Example: Saving the report to a file
with open("cluster_health_report.html", "w", encoding="utf-8") as f:
    f.write(html_report)
```

## Internal Methods (For Advanced Agents)

If an agent needs to access the raw data instead of the HTML, the `K8sReportSkill` class methods can be called directly:

```python
from k8s_inspector import K8sReportSkill

inspector = K8sReportSkill()

# Get pure JSON/Dict data
nodes_data = inspector.get_nodes_status()
pods_data = inspector.get_pods_status()
warnings = inspector.get_recent_warnings()
```

## Common Workflows

### 1. Daily Health Check Email
Combine this skill with an SMTP script to send an automated daily status report of the entire cluster to the DevOps team.

### 2. Incident Triage
When an alert fires, an agent can immediately trigger this skill to capture the *exact state* of the cluster (including the 1-hour warning events) at the time of the incident, attaching the HTML report to the ticketing system (e.g., Jira).

## Security and RBAC

If running this skill inside the Kubernetes cluster (In-Cluster mode), the associated ServiceAccount requires strictly read-only permissions (`get`, `list`) for the following resources across all namespaces:
- `nodes`
- `namespaces`
- `pods`
- `events`
- `deployments` (apps API group)
- `custom-objects` (metrics.k8s.io API group - optional, for node metrics)

## Environment Variables

- `KUBECONFIG` — Path to kubeconfig file. The `kubernetes` Python client automatically reads this if set, eliminating the need to pass the `kubeconfig_path` parameter.

## Getting Help

If the report generation fails:
1. Ensure the `templates/report.html` file is in the same directory structure as `k8s_inspector.py`.
2. Check if the cluster API Server is reachable from the environment running the skill.
3. Verify that the provided kubeconfig has sufficient RBAC permissions.

---

**Version:** 1.0.0  
**License:** MIT  
**Compatible with:** Python 3.8+, Kubernetes clusters v1.20+