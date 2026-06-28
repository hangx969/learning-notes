---
title: "企业级监控告警落地：Prometheus 规则分层与 Alertmanager 通知编排"
source: "https://mp.weixin.qq.com/s/uVH_OTvFznkk1WnbGMnvDw"
author:
published:
created: 2026-06-28
description: "关注「Raymond运维」公众号，并设为「星标」，也可以扫描底部二维码加入群聊，第一时间获取最新内容，不再错过"
tags:
  - "clippings"
---
Raymond运维 *2026年6月17日 20:00![图片](https://mmbiz.qpic.cn/sz_mmbiz_gif/b5PbQq93ic09N2RfN7gYF9IOF5giaofTOPoR8Y9szIF5eLelR8lIXgGMn1Lh700B0dPxeeibC2VX1mAzhWvcHz0cg/640?wx_fmt=gif&from=appmsg&wxfrom=5&tp=webp&wx_lazy=1#imgIndex=0)

关注 **「Raymond运维」** 公众号，并设为 **「星标」** ，也可以扫描底部二维码加入群聊，第一时间获取最新内容，不再错过精彩内容。

## 一、概述

### 1.1 背景介绍

监控系统搭完了，指标也采集上来了，但如果没有告警，等于白搭。我见过不少团队Prometheus跑得好好的，Grafana大屏也挂在墙上，结果凌晨3点数据库磁盘写满了，第二天早上用户投诉才发现。监控不闭环，就是摆设。

Prometheus的告警分两部分：Prometheus Server负责根据PromQL表达式评估告警规则，触发后把告警推给Alertmanager；Alertmanager负责去重、分组、路由、静默，最终通过邮件、钉钉、企业微信、Webhook等渠道发出通知。这个分工设计得很合理——Prometheus专注数据采集和规则评估，Alertmanager专注通知管理，各司其职。

我们团队从2020年开始用这套告警体系，目前管理着600多条告警规则，覆盖主机、容器、中间件、业务四个层面，日均触发告警200-300条，通过分级策略和收敛机制，实际推送到人的不超过30条。

### 1.2 技术特点

- **PromQL驱动的告警规则** ：告警条件用PromQL表达式定义，能写出非常灵活的判断逻辑。比如"CPU使用率连续5分钟超过85%"、"磁盘空间按当前速率24小时内会写满"、"HTTP错误率突然飙升到正常值的3倍"，这些用PromQL都能精确表达。
- **路由树+分组去重** ：Alertmanager的路由配置是树状结构，根据label匹配把告警分发到不同的接收器。同一组的告警会合并成一条通知发送，避免告警风暴。我们线上一次网络故障触发了80多条告警，经过分组后只发了3条通知。
- **抑制和静默机制** ：抑制（Inhibition）可以设置告警之间的依赖关系，比如节点宕机时自动抑制该节点上所有服务的告警。静默（Silence）可以在维护窗口临时屏蔽特定告警，避免计划内变更触发误报。

### 1.3 适用场景

- 基础设施告警：主机CPU、内存、磁盘、网络异常检测，服务进程存活监控，硬件故障预警。这是最基础的告警需求，覆盖面广，规则相对固定。
- 应用服务告警：HTTP接口的QPS、延迟、错误率监控，JVM内存和GC监控，数据库连接池和慢查询监控。需要和开发团队配合定义合理的阈值。
- 业务指标告警：订单量异常波动、支付成功率下降、用户注册量骤降。这类告警直接关联业务，阈值需要根据业务特征动态调整。

### 1.4 环境要求

| 组件 | 版本要求 | 说明 |
| --- | --- | --- |
| Prometheus | 2.45+ | 告警规则评估引擎，需要和Alertmanager版本匹配 |
| Alertmanager | 0.27+ | 0.27版本修复了集群模式下的几个关键bug |
| 操作系统 | CentOS 7+ / Ubuntu 20.04+ | Alertmanager资源消耗很低，1C1G就够 |
| 网络 | 内网互通 | Prometheus到Alertmanager需要9093端口，Alertmanager集群间需要9094端口 |
| 通知渠道 | 邮件服务器/钉钉机器人/企微机器人 | 至少配一个通知渠道，建议配两个做冗余 |

---

## 二、详细步骤

### 2.1 准备工作

#### 2.1.1 Alertmanager安装

```
# 创建用户
sudo useradd --no-create-home --shell /bin/false alertmanager

# 下载Alertmanager
cd /tmp
wget https://github.com/prometheus/alertmanager/releases/download/v0.27.0/alertmanager-0.27.0.linux-amd64.tar.gz
tar xzf alertmanager-0.27.0.linux-amd64.tar.gz
cd alertmanager-0.27.0.linux-amd64

# 安装
sudo cp alertmanager /usr/local/bin/
sudo cp amtool /usr/local/bin/
sudo chown alertmanager:alertmanager /usr/local/bin/alertmanager
sudo chown alertmanager:alertmanager /usr/local/bin/amtool

# 创建配置和数据目录
sudo mkdir -p /etc/alertmanager
sudo mkdir -p /var/lib/alertmanager
sudo chown -R alertmanager:alertmanager /etc/alertmanager
sudo chown -R alertmanager:alertmanager /var/lib/alertmanager

# 验证
alertmanager --version
```

#### 2.1.2 Systemd服务配置

```
sudo tee /etc/systemd/system/alertmanager.service > /dev/null << 'EOF'
[Unit]
Description=Alertmanager
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=alertmanager
Group=alertmanager
ExecStart=/usr/local/bin/alertmanager \
  --config.file=/etc/alertmanager/alertmanager.yml \
  --storage.path=/var/lib/alertmanager \
  --web.listen-address=0.0.0.0:9093 \
  --web.external-url=http://alertmanager.example.com:9093 \
  --cluster.listen-address=0.0.0.0:9094 \
  --log.level=info \
  --data.retention=120h

Restart=always
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
```

**参数说明** ：

- `--data.retention=120h` ：告警数据保留5天，默认也是120h。这个数据是Alertmanager自己的状态数据（静默规则、通知记录等），不是Prometheus的监控数据。
- `--cluster.listen-address` ：集群通信端口，多实例部署时用。单机可以设成空字符串禁用。
- `--web.external-url` ：外部访问地址，告警通知里的链接会用这个地址。设错了点告警链接会404。

#### 2.1.3 防火墙配置

```
# Alertmanager Web UI和API
sudo ufw allow 9093/tcp
# Alertmanager集群通信
sudo ufw allow 9094/tcp
sudo ufw allow 9094/udp
sudo ufw reload
```

### 2.2 核心配置

#### 2.2.1 Alertmanager主配置文件

```
# 文件路径：/etc/alertmanager/alertmanager.yml
global:
resolve_timeout:5m
smtp_from:'alertmanager@example.com'
smtp_smarthost:'smtp.example.com:465'
smtp_auth_username:'alertmanager@example.com'
smtp_auth_password:'your_smtp_password'
smtp_require_tls:false

# 通知模板
templates:
-'/etc/alertmanager/templates/*.tmpl'

# 路由树配置
route:
# 分组依据，同一组的告警合并发送
group_by:['alertname','cluster','service']
# 新告警等待时间，等这么久再发送，让同组告警有机会合并
group_wait:30s
# 同一组告警的发送间隔
group_interval:5m
# 已发送告警的重复发送间隔
repeat_interval:4h
# 默认接收器
receiver:'default-webhook'

routes:
    # P0级别 - 核心服务宕机，立刻通知
    -match:
        severity:critical
      receiver:'critical-pager'
      group_wait:10s
      repeat_interval:1h
      continue:false

    # P1级别 - 性能告警，5分钟内通知
    -match:
        severity:warning
      receiver:'warning-dingtalk'
      group_wait:30s
      repeat_interval:4h
      continue:false

    # 数据库相关告警单独路由给DBA
    -match_re:
        job:'(mysql|redis|mongodb).*'
      receiver:'dba-dingtalk'
      group_wait:30s
      repeat_interval:2h
      continue:false

    # 业务告警路由给对应团队
    -match:
        team:'order'
      receiver:'order-team-webhook'
      continue:false

    -match:
        team:'payment'
      receiver:'payment-team-webhook'
      continue:false

# 抑制规则
inhibit_rules:
# 节点宕机时，抑制该节点上所有服务的告警
-source_match:
      alertname:'NodeDown'
    target_match_re:
      alertname:'.+'
    equal:['instance']

# critical级别告警触发时，抑制同指标的warning告警
-source_match:
      severity:'critical'
    target_match:
      severity:'warning'
    equal:['alertname','instance']

# 接收器配置
receivers:
# 默认接收器 - 企业微信
-name:'default-webhook'
    webhook_configs:
      -url:'http://localhost:8060/dingtalk/ops/send'
        send_resolved:true

# P0告警 - 电话+短信+钉钉
-name:'critical-pager'
    webhook_configs:
      -url:'http://localhost:8060/dingtalk/critical/send'
        send_resolved:true
      -url:'http://oncall-api.internal:8080/api/v1/alert'
        send_resolved:true
    email_configs:
      -to:'oncall@example.com'
        send_resolved:true
        headers:
          Subject:'[P0-CRITICAL] {{ .GroupLabels.alertname }}'

# Warning告警 - 钉钉群
-name:'warning-dingtalk'
    webhook_configs:
      -url:'http://localhost:8060/dingtalk/warning/send'
        send_resolved:true

# DBA告警
-name:'dba-dingtalk'
    webhook_configs:
      -url:'http://localhost:8060/dingtalk/dba/send'
        send_resolved:true

# 订单团队
-name:'order-team-webhook'
    webhook_configs:
      -url:'http://localhost:8060/dingtalk/order/send'
        send_resolved:true

# 支付团队
-name:'payment-team-webhook'
    webhook_configs:
      -url:'http://localhost:8060/dingtalk/payment/send'
        send_resolved:true
```

**说明** ： `group_wait` 设成30秒是经过权衡的。太短了同一批告警来不及合并，太长了延迟通知。P0级别的critical告警我们设成10秒，因为这类告警宁可多发也不能晚发。 `repeat_interval` 设4小时，避免同一个告警反复骚扰值班人员，但critical级别设1小时，确保持续关注。

#### 2.2.2 告警规则文件 - 主机监控

```
# 文件路径：/etc/prometheus/rules/node_alerts.yml
groups:
-name:node_alerts
    rules:
      -alert:NodeDown
        expr:up{job="node-exporter"}==0
        for:2m
        labels:
          severity:critical
          team:ops
        annotations:
          summary:"节点 {{ $labels.instance }} 宕机"
          description:"节点已超过2分钟无响应，请立即排查"
          runbook:"https://wiki.internal/runbook/node-down"

      -alert:NodeCPUHigh
        expr:|
          1 - avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) > 0.85
        for:5m
        labels:
          severity:warning
          team:ops
        annotations:
          summary:"{{ $labels.instance }} CPU使用率 {{ $value | humanizePercentage }}"
          description:"CPU持续5分钟超过85%，检查是否有异常进程"

      -alert:NodeMemoryHigh
        expr:|
          1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes > 0.90
        for:5m
        labels:
          severity:warning
          team:ops
        annotations:
          summary:"{{ $labels.instance }} 内存使用率 {{ $value | humanizePercentage }}"

      -alert:NodeDiskAlmostFull
        expr:|
          1 - node_filesystem_avail_bytes{mountpoint="/",fstype!="tmpfs"}
          / node_filesystem_size_bytes{mountpoint="/",fstype!="tmpfs"} > 0.85
        for:5m
        labels:
          severity:warning
          team:ops
        annotations:
          summary:"{{ $labels.instance }} 磁盘使用率 {{ $value | humanizePercentage }}"

      -alert:NodeDiskWillFull
        expr:|
          predict_linear(
            node_filesystem_avail_bytes{mountpoint="/",fstype!="tmpfs"}[6h], 24*3600
          ) < 0
        for:10m
        labels:
          severity:warning
          team:ops
        annotations:
          summary:"{{ $labels.instance }} 磁盘预计24小时内写满"
          description:"按当前写入速率推算，根分区将在24小时内耗尽"

      -alert:NodeNetworkErrors
        expr:|
          rate(node_network_receive_errs_total[5m]) > 10
          or rate(node_network_transmit_errs_total[5m]) > 10
        for:5m
        labels:
          severity:warning
          team:ops
        annotations:
          summary:"{{ $labels.instance }} 网卡 {{ $labels.device }} 出现错误包"

      -alert:NodeLoadHigh
        expr:node_load15/countby(instance)(node_cpu_seconds_total{mode="idle"})>2
        for:10m
        labels:
          severity:warning
          team:ops
        annotations:
          summary:"{{ $labels.instance }} 15分钟负载过高"
          description:"负载/CPU核数比值 {{ $value }}，超过2说明系统严重过载"
```

**说明** ： `for` 参数很关键，设太短容易误报，设太长又延迟告警。CPU和内存设5分钟是因为短暂的毛刺很常见，持续5分钟才说明真有问题。NodeDown设2分钟，因为网络抖动可能导致一两次采集失败，2分钟（约8次采集）能过滤掉大部分误报。

#### 2.2.3 告警规则文件 - 应用服务监控

```
# 文件路径：/etc/prometheus/rules/app_alerts.yml
groups:
-name:app_alerts
    rules:
      -alert:ServiceDown
        expr:up{job=~"app-.*"}==0
        for:1m
        labels:
          severity:critical
        annotations:
          summary:"服务 {{ $labels.job }} 实例 {{ $labels.instance }} 不可达"

      -alert:HighErrorRate
        expr:|
          sum by(job) (rate(http_requests_total{status=~"5.."}[5m]))
          / sum by(job) (rate(http_requests_total[5m])) > 0.05
        for:3m
        labels:
          severity:critical
        annotations:
          summary:"{{ $labels.job }} HTTP 5xx错误率 {{ $value | humanizePercentage }}"
          description:"错误率超过5%持续3分钟，检查应用日志"

      -alert:HighLatencyP99
        expr:|
          histogram_quantile(0.99,
            sum by(job, le) (rate(http_request_duration_seconds_bucket[5m]))
          ) > 2
        for:5m
        labels:
          severity:warning
        annotations:
          summary:"{{ $labels.job }} P99延迟 {{ $value | humanizeDuration }}"

      -alert:QPSDropSudden
        expr:|
          sum by(job) (rate(http_requests_total[5m]))
          < sum by(job) (rate(http_requests_total[1h] offset 1d)) * 0.5
        for:10m
        labels:
          severity:warning
        annotations:
          summary:"{{ $labels.job }} QPS较昨日同期下降超过50%"
          description:"当前QPS {{ $value }}，可能存在流量异常"

      -alert:JVMHeapHigh
        expr:|
          jvm_memory_used_bytes{area="heap"}
          / jvm_memory_max_bytes{area="heap"} > 0.85
        for:5m
        labels:
          severity:warning
        annotations:
          summary:"{{ $labels.instance }} JVM堆内存使用率 {{ $value | humanizePercentage }}"

      -alert:JVMGCTimeHigh
        expr:|
          rate(jvm_gc_pause_seconds_sum[5m])
          / rate(jvm_gc_pause_seconds_count[5m]) > 0.5
        for:5m
        labels:
          severity:warning
        annotations:
          summary:"{{ $labels.instance }} GC平均耗时超过500ms"
```

#### 2.2.4 钉钉通知模板配置

```
# 安装prometheus-webhook-dingtalk
cd /tmp
wget https://github.com/timonwong/prometheus-webhook-dingtalk/releases/download/v2.1.0/prometheus-webhook-dingtalk-2.1.0.linux-amd64.tar.gz
tar xzf prometheus-webhook-dingtalk-2.1.0.linux-amd64.tar.gz
sudo cp prometheus-webhook-dingtalk-2.1.0.linux-amd64/prometheus-webhook-dingtalk /usr/local/bin/
```
```
# 文件路径：/etc/prometheus-webhook-dingtalk/config.yml
targets:
ops:
    url:https://oapi.dingtalk.com/robot/send?access_token=YOUR_OPS_TOKEN
    secret:SEC_YOUR_OPS_SECRET
    message:
      title:'{{ template "ding.link.title" . }}'
      text:'{{ template "ding.link.content" . }}'
critical:
    url:https://oapi.dingtalk.com/robot/send?access_token=YOUR_CRITICAL_TOKEN
    secret:SEC_YOUR_CRITICAL_SECRET
warning:
    url:https://oapi.dingtalk.com/robot/send?access_token=YOUR_WARNING_TOKEN
    secret:SEC_YOUR_WARNING_SECRET
dba:
    url:https://oapi.dingtalk.com/robot/send?access_token=YOUR_DBA_TOKEN
    secret:SEC_YOUR_DBA_SECRET
```
```
# Systemd服务
sudo tee /etc/systemd/system/dingtalk-webhook.service > /dev/null << 'EOF'
[Unit]
Description=Prometheus Webhook DingTalk
After=network-online.target

[Service]
Type=simple
ExecStart=/usr/local/bin/prometheus-webhook-dingtalk \
  --config.file=/etc/prometheus-webhook-dingtalk/config.yml \
  --web.listen-address=0.0.0.0:8060
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start dingtalk-webhook
sudo systemctl enable dingtalk-webhook
```

### 2.3 启动和验证

#### 2.3.1 启动服务

```
# 检查Alertmanager配置语法
amtool check-config /etc/alertmanager/alertmanager.yml
# 输出：Checking '/etc/alertmanager/alertmanager.yml'  SUCCESS

# 检查告警规则语法
promtool check rules /etc/prometheus/rules/node_alerts.yml
promtool check rules /etc/prometheus/rules/app_alerts.yml

# 启动Alertmanager
sudo systemctl start alertmanager
sudo systemctl enable alertmanager
sudo systemctl status alertmanager

# 重载Prometheus配置使告警规则生效
curl -X POST http://localhost:9090/-/reload
```

#### 2.3.2 功能验证

```
# 验证Alertmanager健康状态
curl -s http://localhost:9093/-/healthy
# 输出：OK

# 查看当前告警规则
curl -s http://localhost:9090/api/v1/rules | python3 -m json.tool | head -40

# 查看活跃告警
curl -s http://localhost:9090/api/v1/alerts | python3 -m json.tool

# 用amtool查看Alertmanager状态
amtool --alertmanager.url=http://localhost:9093 config show

# 发送测试告警验证通知链路
curl -X POST http://localhost:9093/api/v2/alerts \
  -H 'Content-Type: application/json' \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "instance": "test-node:9100"
    },
    "annotations": {
      "summary": "这是一条测试告警，验证通知链路"
    },
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }]'

# 等30秒后检查钉钉群是否收到通知
# 然后发送resolve清除测试告警
curl -X POST http://localhost:9093/api/v2/alerts \
  -H 'Content-Type: application/json' \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "instance": "test-node:9100"
    },
    "endsAt": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }]'
```

**说明** ：每次改完告警规则或Alertmanager配置，一定要先用amtool和promtool做语法检查。我们有一次直接reload了一个有语法错误的规则文件，Prometheus没报错但那条规则静默失效了，直到出了故障才发现告警没触发。

---

## 三、示例代码和配置

### 3.1 完整配置示例

#### 3.1.1 K8s集群告警规则集

```
# 文件路径：/etc/prometheus/rules/k8s_alerts.yml
groups:
-name:kubernetes_alerts
    rules:
      -alert:KubePodCrashLooping
        expr:|
          rate(kube_pod_container_status_restarts_total[15m]) * 60 * 5 > 0
        for:5m
        labels:
          severity:warning
        annotations:
          summary:"Pod {{ $labels.namespace }}/{{ $labels.pod }} 频繁重启"
          description:"过去15分钟重启次数: {{ $value | humanize }}"

      -alert:KubePodNotReady
        expr:|
          sum by(namespace, pod) (
            max by(namespace, pod) (kube_pod_status_phase{phase=~"Pending|Unknown"}) * on(namespace, pod)
            group_left(owner_kind, owner_name) max by(namespace, pod, owner_kind, owner_name) (kube_pod_owner)
          ) > 0
        for:10m
        labels:
          severity:warning
        annotations:
          summary:"Pod {{ $labels.namespace }}/{{ $labels.pod }} 超过10分钟未就绪"

      -alert:KubeDeploymentReplicasMismatch
        expr:|
          kube_deployment_spec_replicas != kube_deployment_status_ready_replicas
        for:10m
        labels:
          severity:warning
        annotations:
          summary:"Deployment {{ $labels.namespace }}/{{ $labels.deployment }} 副本数不匹配"
          description:"期望 {{ $labels.spec_replicas }}，实际就绪 {{ $labels.ready_replicas }}"

      -alert:KubeNodeNotReady
        expr:kube_node_status_condition{condition="Ready",status="true"}==0
        for:5m
        labels:
          severity:critical
        annotations:
          summary:"K8s节点 {{ $labels.node }} NotReady"

      -alert:KubeContainerOOMKilled
        expr:|
          kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} == 1
        for:0m
        labels:
          severity:warning
        annotations:
          summary:"容器 {{ $labels.namespace }}/{{ $labels.pod }}/{{ $labels.container }} 被OOM Kill"

      -alert:KubePVCAlmostFull
        expr:|
          kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes > 0.85
        for:5m
        labels:
          severity:warning
        annotations:
          summary:"PVC {{ $labels.namespace }}/{{ $labels.persistentvolumeclaim }} 使用率超过85%"
```

#### 3.1.2 中间件告警规则集

```
# 文件路径：/etc/prometheus/rules/middleware_alerts.yml
groups:
-name:mysql_alerts
    rules:
      -alert:MySQLDown
        expr:mysql_up==0
        for:1m
        labels:
          severity:critical
          team:dba
        annotations:
          summary:"MySQL {{ $labels.instance }} 宕机"

      -alert:MySQLSlowQueries
        expr:rate(mysql_global_status_slow_queries[5m])>0.1
        for:5m
        labels:
          severity:warning
          team:dba
        annotations:
          summary:"MySQL {{ $labels.instance }} 慢查询增多"
          description:"每秒慢查询数 {{ $value }}"

      -alert:MySQLConnectionsHigh
        expr:|
          mysql_global_status_threads_connected
          / mysql_global_variables_max_connections > 0.8
        for:5m
        labels:
          severity:warning
          team:dba
        annotations:
          summary:"MySQL {{ $labels.instance }} 连接数使用率 {{ $value | humanizePercentage }}"

-name:redis_alerts
    rules:
      -alert:RedisDown
        expr:redis_up==0
        for:1m
        labels:
          severity:critical
          team:dba
        annotations:
          summary:"Redis {{ $labels.instance }} 宕机"

      -alert:RedisMemoryHigh
        expr:|
          redis_memory_used_bytes / redis_memory_max_bytes > 0.85
        for:5m
        labels:
          severity:warning
          team:dba
        annotations:
          summary:"Redis {{ $labels.instance }} 内存使用率 {{ $value | humanizePercentage }}"

      -alert:RedisRejectedConnections
        expr:increase(redis_rejected_connections_total[5m])>0
        for:1m
        labels:
          severity:warning
          team:dba
        annotations:
          summary:"Redis {{ $labels.instance }} 出现连接拒绝"
```

#### 3.1.3 自定义钉钉通知模板

```
{{/* 文件路径：/etc/alertmanager/templates/dingtalk.tmpl */}}
{{ define "ding.link.title" }}
{{ if eq (index .Alerts 0).Labels.severity "critical" }}[P0-严重]{{ else }}[P1-警告]{{ end }} {{ .GroupLabels.alertname }} ({{ .Alerts | len }}条)
{{ end }}

{{ define "ding.link.content" }}
{{ if eq .Status "firing" }}**🔴 告警触发**{{ else }}**🟢 告警恢复**{{ end }}

**告警名称**: {{ .GroupLabels.alertname }}
**告警级别**: {{ (index .Alerts 0).Labels.severity }}
**告警数量**: {{ .Alerts | len }}条
**触发时间**: {{ (.Alerts.Firing | first).StartsAt.Local.Format "2006-01-02 15:04:05" }}

{{ range .Alerts }}
---
**实例**: {{ .Labels.instance }}
**摘要**: {{ .Annotations.summary }}
**详情**: {{ .Annotations.description }}
{{ end }}

[查看详情]({{ .ExternalURL }}/#/alerts?receiver={{ .Receiver | urlquery }})
{{ end }}
```

### 3.2 实际应用案例

#### 案例一：告警分级策略落地

**场景描述** ：我们团队把告警分成P0-P3四个级别，不同级别走不同通知渠道和响应时效。这套分级策略跑了两年多，告警疲劳问题基本解决了。

**分级标准** ：

| 级别 | 定义 | 通知方式 | 响应时效 | 示例 |
| --- | --- | --- | --- | --- |
| P0 | 核心服务不可用 | 电话+短信+钉钉 | 5分钟内响应 | 数据库宕机、支付服务挂了 |
| P1 | 服务降级但可用 | 钉钉+邮件 | 15分钟内响应 | 错误率超5%、延迟超2秒 |
| P2 | 资源预警 | 钉钉群 | 1小时内处理 | 磁盘85%、内存90% |
| P3 | 信息通知 | 邮件 | 下个工作日处理 | 证书30天后过期 |

**实现方式** ：在告警规则的labels里加severity字段，Alertmanager路由树根据severity分发。

```
# Alertmanager路由配置片段
route:
group_by:['alertname','cluster']
receiver:'default'
routes:
    -match:
        severity:critical
      receiver:'p0-pager'
      group_wait:10s
      repeat_interval:30m
    -match:
        severity:warning
      receiver:'p1-dingtalk'
      group_wait:30s
      repeat_interval:4h
    -match:
        severity:info
      receiver:'p2-dingtalk'
      group_wait:1m
      repeat_interval:12h
    -match:
        severity:none
      receiver:'p3-email'
      repeat_interval:24h
```

#### 案例二：企业微信Webhook告警脚本

**场景描述** ：部分团队用企业微信而不是钉钉，Alertmanager原生不支持企微，需要通过Webhook中转。我们写了个轻量的Python脚本做格式转换。

**实现代码** ：

```
#!/usr/bin/env python3
# 文件名：/opt/scripts/wecom_webhook.py
# 功能：接收Alertmanager Webhook，转发到企业微信机器人
# 启动：python3 /opt/scripts/wecom_webhook.py

import json
import requests
from flask import Flask, request

app = Flask(__name__)

WECOM_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WECOM_KEY"

@app.route('/webhook', methods=['POST'])
defwebhook():
    data = request.json
    status = data.get('status', 'unknown')
    alerts = data.get('alerts', [])

    if status == 'firing':
        color = "warning"
        title = f"告警触发 ({len(alerts)}条)"
    else:
        color = "info"
        title = f"告警恢复 ({len(alerts)}条)"

    content_lines = [f"## {title}\n"]
    for alert in alerts[:10]:  # 最多显示10条
        labels = alert.get('labels', {})
        annotations = alert.get('annotations', {})
        content_lines.append(f"**{labels.get('alertname', 'N/A')}**")
        content_lines.append(f"> 实例: {labels.get('instance', 'N/A')}")
        content_lines.append(f"> 级别: {labels.get('severity', 'N/A')}")
        content_lines.append(f"> 摘要: {annotations.get('summary', 'N/A')}\n")

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": "\n".join(content_lines)
        }
    }

    resp = requests.post(WECOM_WEBHOOK_URL, json=payload, timeout=10)
    return json.dumps({"status": "ok", "wecom_response": resp.status_code})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8065)
```

**运行结果** ：

```
告警触发 (2条)

NodeCPUHigh
> 实例: 10.0.1.12:9100
> 级别: warning
> 摘要: 10.0.1.12:9100 CPU使用率 92.3%

NodeMemoryHigh
> 实例: 10.0.1.12:9100
> 级别: warning
> 摘要: 10.0.1.12:9100 内存使用率 94.1%
```

---

## 四、最佳实践和注意事项

### 4.1 最佳实践

#### 4.1.1 性能优化

- **告警规则分组评估** ：把相关的告警规则放在同一个group里，Prometheus会并行评估不同group。我们把600多条规则分成了12个group，评估耗时从3.2秒降到了0.8秒。
	```
	# 查看规则评估耗时
	curl -s 'http://localhost:9090/api/v1/query?query=prometheus_rule_group_duration_seconds{quantile="0.99"}' | jq .
	```
- **避免在告警规则中使用高开销PromQL** ： `count()` 、 `group_left` 、 `label_replace` 这些操作在大数据量下很耗CPU。能用Recording Rules预聚合的先聚合，告警规则里直接查预聚合后的指标。
- **合理设置evaluation\_interval** ：默认15秒评估一次，600条规则每次评估都要跑一遍PromQL。如果规则不需要那么高的时效性，可以在group级别设置更长的interval。比如磁盘空间告警，60秒评估一次完全够用。
- **Alertmanager通知去重** ： `group_by` 的选择直接影响告警合并效果。按 `['alertname', 'cluster']` 分组，同一个集群同一类告警会合并成一条通知。别把instance放进group\_by，不然每台机器单独发一条，网络故障时钉钉群直接被刷屏。

#### 4.1.2 安全加固

- **Alertmanager开启Basic Auth** ：和Prometheus一样，Alertmanager也支持web.yml配置认证。裸奔的Alertmanager任何人都能创建静默规则，等于能让告警失效。
	```
	# /etc/alertmanager/web.yml
	basic_auth_users:
	  admin:$2a$12$KmR3iR5eJx5Oj5Yl5FpNOuJGQwMOsKOqJ7Mcp7hVQ8sKqGzLkjS6
	```
- **Webhook地址用内网** ：钉钉/企微的Webhook转发服务只监听内网地址，不要暴露到公网。Webhook URL里包含access\_token，泄露了别人就能往你的群里发消息。
- **告警通知脱敏** ：告警内容里不要包含敏感信息，比如数据库连接串、密码、内网IP段。通过模板控制输出内容，只展示必要的诊断信息。
- **静默规则审计** ：定期检查Alertmanager的静默规则，防止有人创建了永久静默忘记删除。我们写了个脚本每天扫描一次，超过7天的静默规则自动告警通知。

#### 4.1.3 高可用配置

- **Alertmanager集群模式** ：生产环境至少部署3个Alertmanager实例，通过gossip协议同步状态。Prometheus配置里写上所有实例地址，任何一个挂了不影响告警通知。
	```
	# 实例1
	alertmanager --cluster.listen-address=0.0.0.0:9094 \
	  --cluster.peer=10.0.1.51:9094 --cluster.peer=10.0.1.52:9094
	# 实例2
	alertmanager --cluster.listen-address=0.0.0.0:9094 \
	  --cluster.peer=10.0.1.50:9094 --cluster.peer=10.0.1.52:9094
	# 实例3
	alertmanager --cluster.listen-address=0.0.0.0:9094 \
	  --cluster.peer=10.0.1.50:9094 --cluster.peer=10.0.1.51:9094
	```
- **通知渠道冗余** ：critical级别的告警至少配两个通知渠道。我们的做法是钉钉+电话，钉钉挂了电话还能打通。曾经钉钉API故障了2小时，全靠电话通知兜底。
- **备份策略** ：Alertmanager的静默规则和通知状态存在 `--storage.path` 目录下，定期备份这个目录。

### 4.2 注意事项

#### 4.2.1 配置注意事项

**WARNING** ：告警配置改错了可能导致关键告警丢失，后果比监控挂了还严重。

- `for` 参数不要设成0m，除非你确定这个告警不会有瞬时抖动。我们有个同事把CPU告警的for设成0，结果每天收到上百条CPU毛刺告警，一周后整个团队都对告警通知免疫了。
- `continue: true` 要谨慎使用。设了continue后告警会继续匹配下一条路由，可能导致同一条告警发到多个渠道。除非你确实需要多渠道通知，否则别加。
- 抑制规则的 `equal` 字段必须精确匹配。如果source和target的label名称不一致，抑制不会生效，而且不会报错。

#### 4.2.2 常见错误

| 错误现象 | 原因分析 | 解决方案 |
| --- | --- | --- |
| 告警规则配了但从不触发 | PromQL表达式有误或for时间太长 | 在Prometheus UI手动执行表达式验证 |
| 同一条告警重复收到通知 | group\_by配置不当导致分组过细 | 检查group\_by字段，减少分组维度 |
| 告警恢复通知没收到 | receiver没配send\_resolved: true | 在webhook\_configs里加上send\_resolved |
| Alertmanager集群状态不同步 | gossip端口不通或网络分区 | 检查9094端口连通性和防火墙规则 |
| 钉钉通知发送失败 | access\_token过期或IP白名单限制 | 检查钉钉机器人配置和安全设置 |

#### 4.2.3 兼容性问题

- **版本兼容** ：Alertmanager 0.27对配置文件格式做了一些调整， `match` 和 `match_re` 在未来版本会被 `matchers` 替代。建议新项目直接用matchers语法。
- **平台兼容** ：钉钉机器人2023年后强制要求加签或IP白名单，老的Webhook URL直接用会返回310000错误码。企业微信机器人对消息格式有长度限制，markdown内容超过4096字节会被截断。
- **组件依赖** ：prometheus-webhook-dingtalk 2.x版本要求Go 1.19+编译，低版本系统可能需要手动编译。

---

## 五、故障排查和监控

### 5.1 故障排查

#### 5.1.1 日志查看

```
# 查看Alertmanager日志
sudo journalctl -u alertmanager -f --no-pager

# 查看最近的错误
sudo journalctl -u alertmanager --since "1 hour ago" | grep -i "error\|warn"

# 查看钉钉Webhook转发服务日志
sudo journalctl -u dingtalk-webhook -f --no-pager
```

#### 5.1.2 常见问题排查

**问题一：告警规则配了但不触发**

```
# 检查规则是否被Prometheus加载
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.name=="NodeCPUHigh")'

# 手动执行告警表达式，看是否有返回值
curl -s 'http://localhost:9090/api/v1/query?query=1-avg+by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m]))>0.85' | jq .

# 检查for条件是否满足（pending状态说明条件满足但还没到for时间）
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | select(.labels.alertname=="NodeCPUHigh")'
```

**解决方案** ：

1. 先在Prometheus UI的Graph页面手动执行PromQL，确认有数据返回
2. 检查for时间是否太长，临时改短测试
3. 检查label是否匹配，job名、instance格式是否和实际一致

**问题二：告警触发了但通知没收到**

```
# 检查Alertmanager是否收到了告警
curl -s http://localhost:9093/api/v2/alerts | jq '.[0:5]'

# 检查路由匹配结果
amtool --alertmanager.url=http://localhost:9093 config routes test \
  severity=warning alertname=NodeCPUHigh

# 检查是否被静默规则屏蔽
amtool --alertmanager.url=http://localhost:9093 silence query

# 检查是否被抑制
curl -s http://localhost:9093/api/v2/alerts | jq '.[] | select(.status.state=="suppressed")'
```

**解决方案** ：

1. 确认Prometheus配置了正确的Alertmanager地址
2. 用amtool测试路由匹配，确认告警能匹配到正确的receiver
3. 检查静默规则和抑制规则是否误伤

**问题三：Alertmanager集群脑裂**

```
# 查看集群成员状态
curl -s http://localhost:9093/api/v2/status | jq '.cluster'

# 检查gossip端口连通性
nc -zv 10.0.1.51 9094
nc -zv 10.0.1.52 9094

# 查看集群日志中的gossip相关信息
journalctl -u alertmanager | grep -i "gossip\|cluster\|peer"
```

**解决方案** ：

1. 确认9094端口TCP和UDP都放通了，gossip协议两个都用
2. 检查各实例的 `--cluster.peer` 参数是否正确
3. 如果网络分区导致脑裂，恢复网络后集群会自动合并

#### 5.1.3 调试模式

```
# Alertmanager开启debug日志
# 修改systemd服务，添加 --log.level=debug
sudo systemctl edit alertmanager
# 添加 ExecStart 覆盖

# 查看告警路由匹配过程
amtool --alertmanager.url=http://localhost:9093 config routes show

# 测试特定告警的路由匹配
amtool --alertmanager.url=http://localhost:9093 config routes test \
  alertname=NodeDown severity=critical instance=10.0.1.10:9100
```

### 5.2 性能监控

#### 5.2.1 关键指标监控

```
# Alertmanager通知发送成功率
curl -s 'http://localhost:9093/metrics' | grep alertmanager_notifications_total

# 通知发送延迟
curl -s 'http://localhost:9093/metrics' | grep alertmanager_notification_latency

# 当前活跃告警数
curl -s 'http://localhost:9093/api/v2/alerts?active=true' | jq 'length'

# Prometheus规则评估耗时
curl -s 'http://localhost:9090/metrics' | grep prometheus_rule_group_duration
```

#### 5.2.2 监控指标说明

| 指标名称 | 正常范围 | 告警阈值 | 说明 |
| --- | --- | --- | --- |
| alertmanager\_notifications\_failed\_total | 0 | \>0 | 通知发送失败计数 |
| alertmanager\_notification\_latency\_seconds | <5s | \>30s | 通知发送延迟 |
| prometheus\_rule\_group\_duration\_seconds | <1s | \>5s | 规则组评估耗时 |
| prometheus\_rule\_evaluation\_failures\_total | 0 | \>0 | 规则评估失败数 |
| alertmanager\_alerts | 根据规模定 | \>500 | 活跃告警数量 |

#### 5.2.3 Alertmanager自监控告警规则

```
# 文件路径：/etc/prometheus/rules/alertmanager_self_rules.yml
groups:
-name:alertmanager_self
    rules:
      -alert:AlertmanagerDown
        expr:up{job="alertmanager"}==0
        for:1m
        labels:
          severity:critical
        annotations:
          summary:"Alertmanager {{ $labels.instance }} 宕机"

      -alert:AlertmanagerNotificationFailed
        expr:increase(alertmanager_notifications_failed_total[5m])>0
        for:1m
        labels:
          severity:critical
        annotations:
          summary:"Alertmanager通知发送失败"
          description:"集成 {{ $labels.integration }} 发送失败"

      -alert:AlertmanagerClusterMemberDown
        expr:alertmanager_cluster_members<3
        for:5m
        labels:
          severity:warning
        annotations:
          summary:"Alertmanager集群成员数不足3"
```

### 5.3 备份与恢复

#### 5.3.1 备份策略

```
#!/bin/bash
# 文件名：/opt/scripts/alertmanager_backup.sh
# 备份Alertmanager配置和状态数据

BACKUP_DIR="/data/backup/alertmanager"
DATE=$(date +%Y%m%d)

mkdir -p "${BACKUP_DIR}"

# 备份配置文件
tar czf "${BACKUP_DIR}/alertmanager_config_${DATE}.tar.gz" \
    /etc/alertmanager/ \
    /etc/prometheus/rules/

# 备份状态数据（静默规则等）
tar czf "${BACKUP_DIR}/alertmanager_data_${DATE}.tar.gz" \
    /var/lib/alertmanager/

# 清理30天前的备份
find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +30 -delete
```

#### 5.3.2 恢复流程

1. **停止服务** ： `sudo systemctl stop alertmanager`
2. **恢复配置** ： `tar xzf /data/backup/alertmanager/alertmanager_config_20241215.tar.gz -C /`
3. **恢复数据** ： `tar xzf /data/backup/alertmanager/alertmanager_data_20241215.tar.gz -C /`
4. **重启服务** ： `sudo systemctl start alertmanager`

---

## 六、总结

### 6.1 技术要点回顾

- 告警规则的 `for` 参数是过滤误报的关键手段。CPU/内存类告警设5分钟，服务宕机类设1-2分钟，磁盘预测类设10分钟，这是我们反复调优后的经验值。
- Alertmanager的路由树设计决定了告警通知的效率。按severity分级路由，配合group\_by做告警合并，能把日均300条告警收敛到30条有效通知。
- 抑制规则能大幅减少告警风暴。节点宕机时自动抑制该节点上所有服务告警，一次网络故障从80条告警收敛到3条通知。
- 告警分级策略（P0-P3）是告警治理的基础。不同级别走不同通知渠道和响应时效，避免所有告警一视同仁导致的告警疲劳。
- 通知渠道要做冗余，critical级别至少配两个渠道。钉钉API故障时电话通知兜底，这个设计救过我们好几次。

### 6.2 进阶学习方向

1. **告警自愈（Auto-Remediation）** ：告警触发后自动执行修复脚本，比如磁盘满了自动清理日志、服务挂了自动重启。可以通过Webhook对接自动化平台实现。
- 实践建议：从简单的场景开始，比如自动重启崩溃的服务，逐步扩展到更复杂的自愈场景
3. **AIOps智能告警** ：基于历史告警数据做异常检测，替代固定阈值。Prometheus的predict\_linear是最简单的预测函数，更复杂的可以对接外部ML模型。
- 实践建议：先用predict\_linear做磁盘和流量预测，积累经验后再考虑引入ML模型
5. **OnCall轮值管理** ：配合PagerDuty或自建OnCall系统，实现告警自动分派和升级。值班人员15分钟没响应自动升级给主管。

### 6.3 参考资料

- Alertmanager官方文档 - 配置参数和路由规则详解
- Awesome Prometheus Alerts - 社区告警规则集合
- prometheus-webhook-dingtalk - 钉钉通知转发工具
- PromQL备忘单 - 告警表达式编写参考

---

## 附录

### A. 命令速查表

```
# Alertmanager操作
amtool check-config /etc/alertmanager/alertmanager.yml   # 检查配置语法
amtool --alertmanager.url=http://localhost:9093 alert query  # 查看活跃告警
amtool --alertmanager.url=http://localhost:9093 silence add \
  alertname=NodeCPUHigh -d 2h -c "计划维护"              # 创建2小时静默
amtool --alertmanager.url=http://localhost:9093 silence query  # 查看静默规则
amtool --alertmanager.url=http://localhost:9093 silence expire <id>  # 删除静默

# 告警规则操作
promtool check rules /etc/prometheus/rules/*.yml          # 检查规则语法
promtool test rules test_rules.yml                        # 单元测试告警规则
curl -X POST http://localhost:9090/-/reload               # 热重载规则
```

### B. 配置参数详解

**Alertmanager路由参数** ：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| group\_by | \[\] | 告警分组依据的label列表 |
| group\_wait | 30s | 新告警组等待合并的时间 |
| group\_interval | 5m | 同组告警发送间隔 |
| repeat\_interval | 4h | 已发送告警重复通知间隔 |
| continue | false | 匹配后是否继续匹配下一条路由 |
| match | \- | 精确匹配label |
| match\_re | \- | 正则匹配label |
| receiver | \- | 接收器名称 |

### C. 术语表

| 术语 | 英文 | 解释 |
| --- | --- | --- |
| 告警规则 | Alert Rule | 基于PromQL表达式定义的告警条件，由Prometheus评估 |
| 路由树 | Route Tree | Alertmanager中告警分发的树状匹配结构 |
| 分组 | Grouping | 将相同label的告警合并为一条通知发送 |
| 抑制 | Inhibition | 当某条告警触发时自动屏蔽相关的其他告警 |
| 静默 | Silence | 在指定时间窗口内屏蔽匹配条件的告警通知 |
| 接收器 | Receiver | 告警通知的目标渠道配置（邮件、Webhook等） |
| 去重 | Deduplication | Alertmanager集群中避免同一告警被多次通知的机制 |
| for持续时间 | For Duration | 告警条件需要持续满足的时间，用于过滤瞬时抖动 |

**微**

**信**

**群**

WeChat group

为了方便大家更好的交流运维等相关技术问题，创建了微信交流群，需要加群的小伙伴们可以扫一扫下面的二维码加我为好友拉您进群（备注：加群）。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/FfXfjX4xJDeUZzZPLPUQzYkKa8np5mWo94xQpRevDOIMKkz0EQlSnt7V4IzJtRmxxRibgwfMa4iao0ZjhPTIscrg/640?wx_fmt=jpeg&from=appmsg&watermark=1#imgIndex=1)

**代**

**码**

仓

库

| **代码仓库** | **网址** |
| --- | --- |
| Github | https://github.com/raymond999999 |
| Gitee | https://gitee.com/raymond9 |

**博**

**客**

Blog

| **博客** | **网址** |
| --- | --- |
| CSDN | https://blog.csdn.net/qq\_25599925 |
| 稀土掘金 | https://juejin.cn/user/4262187909781751 |
| 知识星球 | https://wx.zsxq.com/group/15555885545422 |
| 阿里云社区 | https://developer.aliyun.com/profile/snzh3xpxaf6sg |
| 腾讯云社区 | https://cloud.tencent.com/developer/user/11823619 |
| 华为云社区 | https://developer.huaweicloud.com/usercenter/mycommunity/dynamics |

访问博客网站，查看更多优质原创内容。

云原生 · 目录