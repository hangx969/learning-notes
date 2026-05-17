---
title: "K8s审计日志深度实践——从运维利器到合规基石"
source: "https://mp.weixin.qq.com/s/kvIaTMck_V1LpP848x4v7g?scene=1&click_id=225"
author:
  - "[[WAKEUP技术]]"
published:
created: 2026-05-17
description: "个人主页：https://lweiqiang.xyz"
tags:
  - "clippings"
---
WAKEUP技术 *2026年5月17日 19:09*

作者：WAKE UP技术  
公众号：WAKE UP技术  
个人主页：https://lweiqiang.xyz  
技术博客：https://blog.lweiqiang.xyz

---

## 一次"谁删了我的Pod"的追踪

周一早上，开发组长冲进SRE办公室："生产环境的订单服务Pod被删了！谁干的？"

我们打开Kubernetes Dashboard——没有操作记录。打开kubelet日志——只有调度事件，没有"谁删的"信息。

这是我们第一次意识到： **Kubernetes默认不记录"谁在什么时候对什么资源做了什么操作"** 。

而这个问题的答案，藏在 **K8s审计日志（Audit Log）** 里。

---

## 审计日志是什么？

K8s审计日志是API Server的 **访客登记簿** 。每一个对API Server的请求（kubectl、Controller、Scheduler、外部调用），都会被记录下来。

一条审计日志记录了一个API请求的完整生命周期：

```
{
  "kind": "Event",
  "apiVersion": "audit.k8s.io/v1",
  "level": "RequestResponse",
  "auditID": "aBcDeFgHi",
  "stage": "ResponseComplete",
  "requestURI": "/api/v1/namespaces/prod/pods/order-service-6d8f9",
  "verb": "delete",
  "user": {
    "username": "zhangsan",
    "groups": ["system:authenticated"]
  },
  "sourceIPs": ["10.0.1.15"],
  "objectRef": {
    "resource": "pods",
    "namespace": "prod",
    "name": "order-service-6d8f9"
  },
  "responseStatus": {
    "code": 200
  },
  "requestObject": {...},
  "responseObject": {...},
  "timestamp": "2026-05-12T03:15:22Z"
}
```

**这条记录回答的问题** ：

- • 谁？（username: zhangsan）
- • 从哪来？（sourceIPs: 10.0.1.15）
- • 做了什么？（verb: delete）
- • 对什么资源？（objectRef: pods/prod/order-service-6d8f9）
- • 结果如何？（responseStatus: 200）
- • 什么时候？（timestamp）

---

## 审计策略配置实战

K8s审计需要通过 **审计策略文件（Audit Policy）** 来配置——定义哪些事件需要记录、记录到什么详细程度。

```
# /etc/kubernetes/audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
# 默认规则：不记录
omitStages:
  - "RequestReceived"

rules:
  # 1. 在命名空间 default 中，不记录对 Pod 的请求
  - level: None
    namespaces: ["default"]
    resources:
      - group: ""
        resources: ["pods"]

  # 2. 记录对 Secret 和 ConfigMap 的所有请求（安全敏感）
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["secrets", "configmaps"]

  # 3. 记录对 RBAC 相关资源的修改操作
  - level: RequestResponse
    verbs: ["create", "update", "patch", "delete"]
    resources:
      - group: "rbac.authorization.k8s.io"
        resources: ["*"]

  # 4. 记录生产命名空间的所有写操作
  - level: RequestResponse
    verbs: ["create", "update", "patch", "delete"]
    namespaces: ["prod", "prod-chn", "prodfeu-chn"]

  # 5. 健康检查等只读请求，只记录元数据
  - level: Metadata
    verbs: ["get", "list", "watch"]

  # 6. 节点（Node）相关操作，记录请求体
  - level: Request
    resources:
      - group: ""
        resources: ["nodes"]

  # 7. 默认规则：只读操记录元数据，写操作记录完整信息
  - level: Metadata
    verbs: ["get", "list", "watch"]
  - level: RequestResponse
```

**审计级别（Level）说明** ：

| Level | 记录内容 | 适用场景 |
| --- | --- | --- |
| `None` | 不记录 | 高频只读操作（如健康检查） |
| `Metadata` | 只记录请求元数据（谁、什么资源、什么操作） | 只读查询 |
| `Request` | 记录元数据 + 请求体 | 敏感资源查询 |
| `RequestResponse` | 记录元数据 + 请求体 + 响应体 | 写操作、安全审计 |

---

## 在API Server中启用审计

修改kube-apiserver的启动参数（静态Pod方式）：

```
# /etc/kubernetes/manifests/kube-apiserver.yaml
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: kube-apiserver
      command:
        - kube-apiserver
        # 审计策略文件
        - --audit-policy-file=/etc/kubernetes/audit-policy.yaml
        # 审计日志输出文件
        - --audit-log-path=/var/log/kubernetes/audit/audit.log
        # 日志文件最大大小（MB）
        - --audit-log-maxsize=100
        # 保留的旧日志文件数量
        - --audit-log-maxbackup=10
        # 保留的天数
        - --audit-log-maxage=30
        # （可选）输出到webhook
        - --audit-webhook-config-file=/etc/kubernetes/audit-webhook.yaml
```

**重要提醒** ：audit.log文件会快速增长，必须配置日志轮转！

```
# /etc/logrotate.d/k8s-audit
/var/log/kubernetes/audit/audit.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 root root
    postrotate
        systemctl reload kubelet
    endscript
}
```

---

## 审计日志采集与存储架构

生产环境不会直接读取audit.log文件——需要集中式采集和分析。

```
K8s API Server
    │
    ├── 输出到文件（audit.log）
    │       └── Fluent Bit / Filebeat采集
    │               └── Elasticsearch / Loki
    │                       └── Kibana / Grafana（可视化查询）
    │
    └── 输出到Webhook（实时）
            └── 审计专用后端（如Falco、自研系统）
```

**使用Fluent Bit采集审计日志** ：

```
# /etc/fluent-bit/conf.d/k8s-audit.conf
[INPUT]
    Name tail
    Path /var/log/kubernetes/audit/audit.log
    Parser k8s-audit
    Tag k8s.audit
    Refresh_Interval 5
    Mem_Buf_Limit 50MB

[OUTPUT]
    Name es
    Match k8s.audit
    Host elasticsearch.logging.svc
    Port 9200
    Index k8s-audit-logs
```

**审计日志的JSON解析器** ：

```
# /etc/fluent-bit/parsers.conf
[PARSER]
    Name k8s-audit
    Format json
    Time_Key timestamp
    Time_Format %Y-%m-%dT%H:%M:%SZ
```

---

## 典型排查场景

**场景1：追踪"谁删了我的资源"**

```
# 在audit.log中搜索删除操作
grep '"verb":"delete"' /var/log/kubernetes/audit/audit.log | \
  jq 'select(.objectRef.name=="order-service-6d8f9") | 
       {time: .timestamp, user: .user.username, ip: .sourceIPs[0], verb: .verb, resource: .objectRef}'
```

**场景2：发现异常高频API调用（可能是攻击或Bug）**

```
# 统计每个用户的API调用次数
cat /var/log/kubernetes/audit/audit.log | \
  jq -r '.user.username + " " + .verb + " " + .requestURI' | \
  sort | uniq -c | sort -rn | head -20
```

**场景3：检测匿名访问**

```
# 查找system:anonymous用户的操作
grep '"username":"system:anonymous"' /var/log/kubernetes/audit/audit.log
```

**场景4：Grafana可视化——监控异常操作**

```
# Prometheus + Grafana告警规则
groups:
  - name: k8s_audit_alerts
    rules:
      - alert: AnonymousAccessDetected
        expr: |
          sum(rate(k8s_audit_events_total{user="system:anonymous"}[5m])) > 0
        labels:
          severity: critical
        annotations:
          summary: "检测到匿名用户访问K8s API"
```

---

## 合规视角：等保2.0与SOC2的要求

**等保2.0（中国网络安全等级保护）** 对云计算平台的要求：

- • 必须记录用户操作日志，保留至少6个月
- • 日志必须不可篡改
- • 必须能追踪到具体操作人

**SOC2 Type II** 对审计的要求：

- • 所有对生产环境的变更必须有审计记录
- • 审计日志必须定期审查
- • 异常操作必须能触发告警

**K8s审计日志直接满足上述要求** ，但需要配合：

1. 1\. **不可篡改存储** ：将审计日志发送至WORM（一次写入多次读取）存储，如S3 Object Lock
2. 2\. **定期审计** ：每月导出敏感操作（RBAC变更、Secret访问、生产资源删除）并人工审查
3. 3\. **实时告警** ：对接SIEM系统（如Splunk、ELK Watcher）
```
# Elasticsearch Watcher示例：告警敏感操作
{
  "trigger": {
    "schedule": { "interval": "1m" }
  },
  "input": {
    "search": {
      "request": {
        "indices": ["k8s-audit-logs"],
        "body": {
          "query": {
            "bool": {
              "must": [
                { "terms": { "verb": ["create", "update", "patch", "delete"] } },
                { "terms": { "objectRef.resource": ["secrets", "configmaps", "roles", "rolebindings"] } },
                { "range": { "@timestamp": { "gte": "now-1m" } } }
              ]
            }
          }
        }
      }
    }
  },
  "condition": { "compare": { "ctx.payload.hits.total": { "gt": 0 } } },
  "actions": { "send_email": { "email": { "to": ["sre@company.com"] } } }
}
```

---

## 性能优化：审计日志不是免费午餐

全量记录 `RequestResponse` 级别会产生显著的性能开销（序列化、磁盘IO、网络传输）。

**优化策略1：分级记录**

```
# 对核心命名空间使用RequestResponse，其余使用Metadata
rules:
  - level: RequestResponse
    namespaces: ["prod", "prod-chn"]
  - level: Metadata
    namespaces: ["staging", "dev"]
  - level: None
    namespaces: ["kube-system"]  # kube-system内部通信量大，酌情过滤
```

**优化策略2：采样**

```
# 对只读操作采样10%
rules:
  - level: Metadata
    verbs: ["get", "list", "watch"]
    omitStages:
      - "ResponseComplete"
    # 注意：原生K8s审计策略不支持采样
    # 如需采样，可通过webhook后端实现
```

**优化策略3：使用Webhook异步处理**

```
# kube-apiserver配置：输出到webhook（非阻塞）
- --audit-webhook-config-file=/etc/kubernetes/audit-webhook.yaml
- --audit-webhook-mode=batch  # 批量发送，减少API Server阻塞
```

---

## 与Open Policy Agent（OPA）联动

审计日志是"事后追溯"，OPA是"事前拦截"。两者结合，形成完整的K8s安全闭环。

```
# OPA Gatekeeper策略示例：禁止在prod命名空间创建LoadBalancer类型Service
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sNoLoadBalancerInProd
metadata:
  name: no-lb-in-prod
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Service"]
    namespaces: ["prod", "prod-chn"]
  parameters:
    prohibitedType: "LoadBalancer"
```

当OPA拦截请求时，K8s仍会记录审计日志（verb: create，status: 403），形成完整的"拦截+记录"链条。

---

## 结语

K8s审计日志是集群可观测性的重要组成部分，却常常被忽视。

它不仅是 **排查问题的利器** （谁删了我的Pod），更是 **企业合规的基石** （等保2.0、SOC2审计要求）。

配置审计日志只需30分钟，但它给你的，是面对生产事故时"有据可查"的从容。

**不要把这30分钟省掉。**

---

> **快速启用K8s审计日志**
> 
> ```
> # 1. 创建审计策略文件
> cat > /etc/kubernetes/audit-policy.yaml <<EOF
> apiVersion: audit.k8s.io/v1
> kind: Policy
> rules:
>   - level: Metadata
> EOF
> 
> # 2. 修改kube-apiserver配置
> # 添加 --audit-policy-file 和 --audit-log-path 参数
> 
> # 3. 重启kubelet使配置生效
> systemctl restart kubelet
> 
> # 4. 验证审计日志
> tail -f /var/log/kubernetes/audit/audit.log | jq .
> ```

**微信扫一扫赞赏作者**

继续滑动看下一个

WAKE UP技术

向上滑动看下一个