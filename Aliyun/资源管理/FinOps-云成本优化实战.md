---
title: FinOps - 云成本优化实战
tags:
  - Aliyun
  - FinOps
  - cost-optimization
  - cloud
aliases:
  - FinOps
  - 云成本优化
---

# FinOps — 云成本优化实战

> 来源：[老杨的压箱底的技能聊聊FinOps](https://mp.weixin.qq.com/s/bFPP_QCDDyG0M0qQaaY1-w)

FinOps 核心方法论：**先量化，再优化，再固化**。用数据说话——把账单、用量和配置拉齐，对着业务节奏做动作，降成本而不伤 SLA。

---

## 1. 成本基线：把钱看清

按产品、项目、标签聚合三个月账单，建立基线。

### 阿里云（BSS OpenAPI）

```bash
aliyun bssopenapi DescribeInstanceBill \
  --BillingCycle 2025-07 \
  --ProductCode ecs \
  --PageSize 100 \
  | jq '.Data.Items.Item[] | {InstanceID,ProductName,SubscriptionType,Cost: .PretaxAmount,Tag: .Tag}'
```

### 腾讯云（tccli Billing）

```bash
tccli billing DescribeCostDetail \
  --StartTime "2025-07-01 00:00:00" \
  --EndTime "2025-07-31 23:59:59" \
  --Limit 100 \
  | jq '.DetailSet[] | {PayerUin,ProductName,InstanceId,RealTotalCost,Tags}'
```

### 华为云（BSS v2）

```bash
curl -s -H "X-Auth-Token: $HUAWEI_TOKEN" \
  -d '{"cycle":"2025-07"}' \
  https://bss.myhuaweicloud.com/v2/bills/customer-bills/consume-records \
  | jq '.consume_records[] | {cloud_service_type_name, resource_id, amount}'
```

> [!tip] 落地要点
> - 三个月账单拉齐，按产品/标签/项目做 CSV 聚合
> - 停机不代表不收费——云盘、公网 IP、带宽仍计费
> - **无标签 = 不可管理**，务必补全

---

## 2. 找浪费：四个高命中场景

### A. 低利用率实例（7×24 CPU < 5%）

```bash
# 阿里云拉 CPU 监控
aliyun cms DescribeMetricList \
  --Namespace acs_ecs_dashboard \
  --MetricName CPUUtilization \
  --Dimensions '[{"instanceId":"i-bp1abc123"}]' \
  --StartTime 2025-07-01T00:00:00Z \
  --EndTime 2025-07-07T00:00:00Z \
  | jq -r '.Datapoints' | jq -r '.[] | [.timestamp,.Average,.Maximum] | @csv'

# 腾讯云拉 CPU 监控
tccli monitor GetMonitorData \
  --Namespace QCE/CVM \
  --MetricName CPUUsage \
  --Instances '[{"Dimensions":[{"Name":"InstanceId","Value":"ins-8xy1z2"}]}]' \
  --StartTime 2025-07-01T00:00:00+08:00 \
  --EndTime 2025-07-07T00:00:00+08:00 \
  | jq '.DataPoints[0].Values'
```

**判定**：低于 5% 且无夜间批任务 → 降配或合并。

### B. 闲置公网 IP

```bash
# 阿里云：未绑定 EIP
aliyun vpc DescribeEipAddresses --PageSize 100 \
  | jq '.EipAddresses.EipAddress[] | select(.InstanceId==null) | {AllocationId,IpAddress}'

# 腾讯云：未绑定 EIP
tccli vpc DescribeAddress --Filters '[{"Name":"address-status","Values":["UNBIND"]}]' \
  | jq '.AddressSet[] | {AddressId, AddressIp}'
```

**动作**：回收或合并出网，网关做复用。

### C. 对象存储没做生命周期

```bash
# 阿里云 OSS 查看桶生命周期规则
ossutil lifecycle -b oss://my-logs-bucket

# 腾讯云 COS 查看存储类型分布
coscli stat cos://news-archive/ --recursive --summarize
```

**动作**：30 天未访问 → 转 IA/归档，老版本自动清理。

### D. K8s 请求/限制配大了

```bash
kubectl get pod -A -o json \
  | jq -r '.items[] | [.metadata.namespace,.metadata.name,
     .spec.containers[].resources.requests.cpu,
     .spec.containers[].resources.limits.cpu] | @tsv' | head -5
```

**动作**：`requests` 调低到 P95 实际用量，`limits` 保留 1.5~2 倍缓冲，配 HPA/VPA。

---

## 3. 立刻见效的优化动作

### 动作 1：下班自动关机 / 上班自动开机

```bash
#!/usr/bin/env bash
set -euo pipefail
IDS=("i-bp1abc123" "i-bp2def456")
ACTION="${1:-stop}"
for id in "${IDS[@]}"; do
  if [[ "$ACTION" == "stop" ]]; then
    aliyun ecs StopInstance --InstanceId "$id" --ForceStop true
  else
    aliyun ecs StartInstance --InstanceId "$id"
  fi
done
echo "done:$ACTION"
```

```bash
# crontab 定时
0 20 * * 1-5 /opt/ecs-scheduler.sh stop
0 08 * * 1-5 /opt/ecs-scheduler.sh start
```

> [!warning] 关机后云盘、公网 IP 仍在计费，需确认。

### 动作 2：降配（规格迁移）

```bash
# 阿里云 ECS 变配
aliyun ecs ModifyInstanceSpec \
  --InstanceId i-bp1abc123 \
  --InstanceType ecs.c7.large

# K8s 内部先降 requests
kubectl set resources deploy/api --requests=cpu=300m,memory=512Mi
```

### 动作 3：对象存储冷热分层 + 版本清理

```json
{
  "Rule": [{
    "ID": "logs-ia-30d",
    "Prefix": "logs/",
    "Status": "Enabled",
    "Transition": {"Days": 30, "StorageClass": "IA"},
    "Expiration": {"Days": 180}
  },{
    "ID": "versioned-clean",
    "Status": "Enabled",
    "NoncurrentVersionExpiration": {"NoncurrentDays": 30}
  }]
}
```

```bash
ossutil lifecycle -b oss://my-logs-bucket -c /tmp/oss-lc.json
```

### 动作 4：固定负载转包年包月

先识别 7×24 且波动小的实例 → 从最稳定的 20% 开始买包年包月或节省计划，不建议全量上。

---

## 4. 预算告警 + 可观测

### 预算告警（阿里云）

```bash
aliyun bssopenapi CreateCostBudget \
  --BudgetName proj-search-2025Q3 \
  --BudgetType COST \
  --BudgetAmount 50000 \
  --BudgetUnit CNY \
  --DurationUnit Monthly \
  --Subscribers '[{"Type":"EMAIL","Address":"finops@corp.com"}]'
```

### 账单落 Prometheus（做看板/预警）

```bash
# 账单转 metrics，node_exporter textfile 采集
aliyun bssopenapi DescribeInstanceBill --BillingCycle 2025-07 \
  | jq -r '.Data.Items.Item[] | "cloud_cost_cny{product=\"\(.ProductName)\",tag=\"\(.Tag)\"} \(.PretaxAmount)"' \
  > /var/lib/node_exporter/textfile_collector/cloud_cost.prom
```

---

## 5. PR 级成本评估：Infracost

在 PR 里直接给出变更前后每月费用差异，避免先上再后悔：

```bash
infracost breakdown --path . --format json --out-file infracost.json
infracost diff --path infracost.json
```

输出示例：

```
Monthly cost change for this PR: -¥1,243.50
  ├─ alicloud_instance.api[2]   -¥980.00  (c7.large -> c7.medium)
  └─ alicloud_slb.lb_public     -¥263.50  (deleted)
```

---

## 6. 实战案例：三步拿下 30% 夜间浪费

**场景**：研发白天用 40 台按量 ECS，晚上无任务。

| 步骤 | 动作 | 效果 |
|------|------|------|
| 1 | 拉 30 天 CPU，确认 20:00–08:00 空闲 | 数据验证 |
| 2 | 28 台加关机/开机排程，12 台观察两周 | 夜间成本 ~40%↓ |
| 3 | 长期空闲 16 台转包年包月小规格 | 单机 ~30%↓ |

**综合结果**：降到原来 55~60%，对 SLA 影响小。

---

## 总结

FinOps 不是口号，是**对齐账单、用量、配置**的日常工作。运维的价值在三件事：

1. **把数据拉齐** — 账单 + 监控 + 标签
2. **把规则固化** — 预算告警 + Infracost PR 卡点
3. **把改动自动化** — 夜间关机、降配、存储分层、EIP 回收
