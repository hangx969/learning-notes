---
title: "老杨的压箱底的技能聊聊FinOps(收费文章限免开放)"
source: "https://mp.weixin.qq.com/s/bFPP_QCDDyG0M0qQaaY1-w"
author:
  - "[[静静和小沐沐]]"
published:
created: 2026-04-23
description: "要记得.点赞、转发、在看以及打开小星标哦,攒今世之功德,修来世之福报"
tags:
  - "clippings"
---

## 正文

老杨作为互联网届的老登,作为一颗不老常青树的存在,肯定有自己的价值.说白了就是资本家觉得你有用.那今天我们就聊聊运维工程师的核心价值之一FinOps.  
你可能在想： **FinOps 到底怎么落到地** 。一句话： **用数据说话** 。把账单、用量和配置拉齐，对着业务节奏做动作。  
这是它的工作原理： **先量化，再优化，再固化** 。先做 X（拿到可用的数据），然后做 Y（按规则自动化处理），这样可以帮你更快完成 Z（降成本而不伤 SLA）。

下面我给出 **可直接跑的步骤** 。用的是国内常见厂商：阿里云、腾讯云、华为云；再配一些通用工具（ `jq` 、 `cron` 、 `kubectl` 、Infracost）。命令都带 **输出** ，你可以对照看效果。

---

## 1）先把钱看清：三个月成本基线

**目的** ：知道钱花在了哪里。按产品、项目、标签聚合。  
**做法** ：直接拉账单。先做基础视图，再做分组视图。

### 阿里云账单（BSS OpenAPI）

```
$ aliyun bssopenapi DescribeInstanceBill \
  --BillingCycle 2025-07 \
  --ProductCode ecs \
  --PageSize 100 \
  | jq '.Data.Items.Item[] | {InstanceID,ProductName,SubscriptionType,Cost: .PretaxAmount,Tag: .Tag}'
```

**输出**

```
{
  "InstanceID": "i-bp1abc123",
  "ProductName": "云服务器 ECS",
  "SubscriptionType": "PayAsYouGo",
  "Cost": "512.37",
  "Tag": "dept=search,env=prod"
}
```

### 腾讯云账单（tccli Billing）

```
$ tccli billing DescribeCostDetail \
  --StartTime 2025-07-01 00:00:00 \
  --EndTime 2025-07-31 23:59:59 \
  --Limit 100 \
  | jq '.DetailSet[] | {PayerUin,ProductName,InstanceId,RealTotalCost,Tags}'
```

**输出**

```
{
  "PayerUin": "12xxxxxxx",
  "ProductName": "CVM",
  "InstanceId": "ins-8xy1z2",
  "RealTotalCost": "398.22",
  "Tags": [{"Key":"biz","Value":"video"},{"Key":"env","Value":"stag"}]
}
```

### 华为云账单（BSS v2，示例用 curl）

```
$ curl -s -H "X-Auth-Token: $HUAWEI_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cycle":"2025-07"}' \
  https://bss.myhuaweicloud.com/v2/bills/customer-bills/consume-records \
  | jq '.consume_records[] | {cloud_service_type_name, resource_id, amount}'
```

**输出**

```
{
  "cloud_service_type_name": "Elastic Cloud Server",
  "resource_id": "ea9c-ecs-001",
  "amount": 462.11
}
```

**落地要点**

- • 把三个月账单拉齐，做个 CSV。按「产品」「标签」「项目」聚合。
- • 停止不代表完全不收费。云盘、公网 IP、带宽还是会计费（各家文档都有明确说明）。
- • 没标签就补。 **无标签=不可管理** 。

---

## 2）找浪费：四个命中率高的场景

### A. 低利用率实例（7×24 CPU < 5%）

**阿里云拉监控**

```
$ aliyun cms DescribeMetricList \
  --Namespace acs_ecs_dashboard \
  --MetricName CPUUtilization \
  --StartTime 2025-07-01T00:00:00Z \
  --EndTime 2025-07-07T00:00:00Z \
  --Dimensions '[{"instanceId":"i-bp1abc123"}]' \
  | jq -r '.Datapoints' | jq -r '.[] | [.timestamp,.Minimum,.Average,.Maximum] | @csv'
```

**输出**

```
"2025-07-01T01:00:00Z",0.90,1.80,3.10
"2025-07-01T02:00:00Z",0.50,1.20,2.70
...
```

**腾讯云拉监控**

```
$ tccli monitor GetMonitorData \
  --Namespace QCE/CVM \
  --MetricName CPUUsage \
  --Instances '[{"Dimensions":[{"Name":"InstanceId","Value":"ins-8xy1z2"}]}]' \
  --StartTime 2025-07-01T00:00:00+08:00 \
  --EndTime 2025-07-07T00:00:00+08:00 \
  | jq '.DataPoints[0].Values'
```

**输出**

```
[1.2, 1.8, 2.3, 1.7, 0.9, ...]
```

**结论** ：低于 5% 且无夜间批任务 → 降配或合并。

---

### B. 闲置公网 IP / 低出网复用

**阿里云未绑定 EIP**

```
$ aliyun vpc DescribeEipAddresses --PageSize 100 \
  | jq '.EipAddresses.EipAddress[] | select(.InstanceId==null) | {AllocationId,IpAddress,Status}'
```

**输出**

```
{"AllocationId":"eip-abc123","IpAddress":"47.xx.xx.10","Status":"Available"}
```

**腾讯云未绑定 EIP（EIP=弹性公网 IP）**

```
$ tccli vpc DescribeAddress --Filters '[{"Name":"address-status","Values":["UNBIND"]}]' \
  | jq '.AddressSet[] | {AddressId, AddressIp, Status}'
```

**输出**

```
{"AddressId":"eip-xx12","AddressIp":"129.xx.xx.21","Status":"UNBIND"}
```

**动作** ：回收或合并出网；网关做复用。

---

### C. 对象存储没做生命周期

**阿里云 OSS 列桶规则**

```
$ ossutil lifecycle -b oss://my-logs-bucket
```

**输出**

```
Lifecycle Configuration:
Rule ID: logs-cold-60d  Status: Enabled
Action: Transition to IA after 30 days; Delete after 180 days
```

**腾讯云 COS 查看存储类型分布（示例统计）**

```
$ coscli stat cos://news-archive/ --recursive --summarize
```

**输出**

```
Total Objects: 12,380
Standard: 2.1 TB, Infrequent Access: 4.7 TB, Archive: 0 TB
```

**动作** ：把 30 天未访问的日志转 IA 或归档。老版本自动清理。

---

### D. K8s 请求/限制配大了

**拉 Pod 请求/限额**

```
$ kubectl get pod -A -o json \
  | jq -r '.items[] | [.metadata.namespace,.metadata.name,
     .spec.containers[].resources.requests.cpu,
     .spec.containers[].resources.limits.cpu] | @tsv' | head -5
```

**输出**

```
prod   api-6bd7d   1000m   4000m
prod   web-5c8f7   500m    4000m
```

**动作** ：把 `requests` 调低到 **P95 实际用量** ， `limits` 保留 1.5~2 倍缓冲。配 HPA/VPA。

---

## 3）立刻见效的优化动作

### 动作 1：下班自动关机，上班自动开机（ECS/CVM）

**阿里云 ECS 关机/开机脚本**

```
#!/usr/bin/env bash
set -euo pipefail
IDS=("i-bp1abc123" "i-bp2def456")
ACTION="${1:-stop}"  # stop|start
for id in "${IDS[@]}"; do
  if [[ "$ACTION" == "stop" ]]; then
    aliyun ecs StopInstance --InstanceId "$id" --ForceStop true
  else
    aliyun ecs StartInstance --InstanceId "$id"
  fi
done
echo "done:$ACTION"
```

**输出**

```
RequestId: 6F1A... InstanceId: i-bp1abc123 Status: Stopping
RequestId: 9A3C... InstanceId: i-bp2def456 Status: Stopping
done:stop
```

**crontab**

```
$ crontab -l
0 20 * * 1-5 /opt/ecs-scheduler.sh stop
0 08 * * 1-5 /opt/ecs-scheduler.sh start
```

**腾讯云 CVM 类似**

```
$ tccli cvm StopInstances --InstanceIds '["ins-8xy1z2","ins-9ab3c4"]'
$ tccli cvm StartInstances --InstanceIds '["ins-8xy1z2","ins-9ab3c4"]'
```

**输出**

```
{
 "RequestId":"f3e7...","TaskId":112233
}
```

> 提醒：需确认关机后的云盘、公网 IP 仍在计费。

---

### 动作 2：降配（规格迁移）

**阿里云**

```
$ aliyun ecs ModifyInstanceSpec \
  --InstanceId i-bp1abc123 \
  --InstanceType ecs.c7.large \
  --SystemDisk.Category cloud_efficiency
```

**输出**

```
RequestId: 1C2D... Operation: Changing
```

**K8s 内部先把请求值调下来，再降节点规格**

```
$ kubectl set resources deploy/api --requests=cpu=300m,memory=512Mi
deployment.apps/api resource requirements updated
```

---

### 动作 3：对象存储做冷热分层 + 版本清理

**阿里云 OSS 生命周期（示例 JSON）**

```
$ cat /tmp/oss-lc.json
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
$ ossutil lifecycle -b oss://my-logs-bucket -c /tmp/oss-lc.json
```

**输出**

```
Applied lifecycle rules to bucket: my-logs-bucket
```

**腾讯云 COS 同理** ：在控制台/配置文件里下发 IA/归档策略与版本过期。

---

### 动作 4：把“固定负载”转包年包月或节省计划

做法很简单： **先识别 7×24 且波动小的实例** → 统一买包年包月或对应的折扣计划。  
不建议全量上，先从 **最稳定的 20%** 开始。

---

## 4）预算、告警、审批串起来

### 预算告警（以阿里云为例）

```
$ aliyun bssopenapi CreateCostBudget \
  --BudgetName proj-search-2025Q3 \
  --BudgetType COST \
  --BudgetAmount 50000 \
  --BudgetUnit CNY \
  --DurationUnit Monthly \
  --Subscribers '[{"Type":"EMAIL","Address":"finops@corp.com"}]'
```

**输出**

```
RequestId: 7B9E... BudgetId: bgt-123456
```

### 账单明细落 Prometheus（做看板/预警）

把月账单转换为 metrics（示例转换脚本片段）：

```
$ aliyun bssopenapi DescribeInstanceBill --BillingCycle 2025-07 \
  | jq -r '.Data.Items.Item[] | "cloud_cost_cny{product=\"\(.ProductName)\",tag=\"\(.Tag)\"} \(.PretaxAmount)"' \
  > /var/lib/node_exporter/textfile_collector/cloud_cost.prom

$ head -2 /var/lib/node_exporter/textfile_collector/cloud_cost.prom
cloud_cost_cny{product="云服务器 ECS",tag="dept=search,env=prod"} 512.37
cloud_cost_cny{product="对象存储 OSS",tag="dept=search,env=prod"} 210.55
```

**输出（Node Exporter 暴露）**

```
$ curl -s http://127.0.0.1:9100/metrics | grep cloud_cost_cny | head -2
cloud_cost_cny{product="云服务器 ECS",tag="dept=search,env=prod"} 512.37
cloud_cost_cny{product="对象存储 OSS",tag="dept=search,env=prod"} 210.55
```

---

## 5）把“变更前就评估成本”植入研发：Infracost

这是它的工作原理：在 PR 里直接给出 **变更前后每月费用的差异** ，避免先上再后悔。

```
$ infracost breakdown --path . \
  --format json --out-file infracost.json
$ infracost diff --path infracost.json
```

**输出**

```
Project: terraform-alicloud
Monthly cost change for this PR: -¥1,243.50
  ├─ alicloud_instance.api[2]       -¥980.00  (changed from ecs.c7.large -> ecs.c7.medium)
  └─ alicloud_slb.lb_public         -¥263.50  (deleted)
```

---

## 6）“现实里的例子”：三步拿下 30% 夜间浪费

**场景** ：研发白天用 40 台按量 ECS，晚上没任务。  
**做法** ：

1. 1\. 拉 30 天 CPU 用量，确认 20:00–08:00 基本空闲。
2. 2\. 对 28 台加 **关机/开机** 排程；对剩余 12 台观察两周后再做。
3. 3\. 两周后，把长期空闲的 16 台转包年包月小规格。

**结果** （示例测算）：

- • 夜间关机节约 ~40% 的按量成本。
- • 降配后单机降价 ~30%。
- • 结合包年包月，综合降到原来 ~55–60%。  
	这套做法简单，且对 SLA 影响小。

---

## 7）常用清单（可直接复制）

**盘点**

```
# 阿里云：实例清单
$ aliyun ecs DescribeInstances --PageSize 100 | jq '.Instances.Instance[] | {InstanceId, InstanceName, InstanceType, Status, Tags}'

# 腾讯云：实例清单
$ tccli cvm DescribeInstances --Limit 100 | jq '.InstanceSet[] | {InstanceId, InstanceName, InstanceType, InstanceState, Tags}'

# 华为云：示例（ECS 列表 API）
$ curl -s -H "X-Auth-Token: $HUAWEI_TOKEN" https://ecs.xxx.myhuaweicloud.com/v1/{project_id}/cloudservers/detail \
  | jq '.servers[] | {id,name,flavor,status,metadata}'
```

**监控**

```
# 阿里云 CPU 利用率
$ aliyun cms DescribeMetricList --Namespace acs_ecs_dashboard --MetricName CPUUtilization --Dimensions '[{"instanceId":"i-xxx"}]'
```

**网络与存储**

```
# 未绑定 EIP
$ aliyun vpc DescribeEipAddresses | jq '.EipAddresses.EipAddress[] | select(.InstanceId==null)'

# OSS 生命周期查看
$ ossutil lifecycle -b oss://bucket-name
```

**K8s**

```
# Requests/Limits 快速对照
$ kubectl get pod -A -o json | jq -r '.items[] | [.metadata.namespace,.metadata.name,.spec.containers[].resources.requests.cpu,.spec.containers[].resources.limits.cpu] | @tsv'
```

**自动化**

```
# 关机/开机（阿里云）
$ /opt/ecs-scheduler.sh stop
done:stop
```

---

## 结论（直说）

- • FinOps 不是口号，它就是\*\*“对齐账单、用量、配置”\*\*的日常工作。
- • 运维的价值在 **三件事** ：把数据拉齐、把规则固化、把改动自动化。
- • 先做能立刻生效的动作： **夜间关机、降配、存储分层、EIP 回收** 。
- • 然后把 **预算告警** 与 **PR 成本评估** 接起来，把“省钱”变成流程的一部分。
