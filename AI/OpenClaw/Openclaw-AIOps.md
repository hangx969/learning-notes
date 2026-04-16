---
title: OpenClaw AIOps
tags:
  - AI
  - openclaw
  - AIOps
  - kubernetes
aliases:
  - OpenClaw K8s管理
  - OpenClaw巡检
---

# 基于飞书 + OpenClaw 远程智能管理 K8s 集群

## 安装 kubectl skill

- 下载地址：[kubectl skill](https://clawhub.ai/ddevaal/kubectl)
- 解压到 OpenClaw 工作目录的 skills 目录下

> [!important] 前置条件
> 基于 kubectl 来管理的，所以需要在 OpenClaw 机器上安装 kubectl，并且拿到集群的 kubeconfig 文件，放到 `~/.kube/config`，需要直接 `kubectl get nodes` 能运行。

## 使用

完成后即可以自然语言下发命令：

- 获取当前 k8s 集群的版本信息，node 数量和 IP，以及 istio-system 命名空间下的 pod 列表和运行状态。整理成表格发给我。
- 帮我查询一下 default 命名空间下有没有异常状态的 pod，如果有帮我查询异常的原因。注意：仅查询，并不需要修复。

---

# 基于飞书 + OpenClaw 巡检 K8s 集群

## 配置邮箱服务

首先需要自行开通邮箱 SMTP 和 IMAP 服务，并且记录授权码，可以选择 163、QQ 等邮箱。这个邮箱会作为发件人被 OpenClaw 使用。

## 配置邮箱 Skills

1. 下载邮箱 Skills：[imap-smtp-email](https://clawhub.ai/gzlicanyi/imap-smtp-email)

2. 执行 `setup.sh` 脚本，添加邮箱配置：

   ```bash
   bash setup.sh
   ```

3. 把 skill 放到 `openclaw/skills` 目录

4. 把 `Skills.md` 中一些不需要的变量给删掉，否则 WebUI 中的 skills 状态显示为不可用：

   ```markdown
   env:
     - IMAP_HOST
     - IMAP_USER
     - IMAP_PASS
     - SMTP_HOST
     - SMTP_USER
     - SMTP_PASS
   ```

5. `npm install` 安装一下这个 Skill

6. 去 WebUI → 技能，找到 imap-smtp-email，在 API Key 中填入邮箱授权码 → 保存

7. 让 OpenClaw 记住使用这个 skills：

   ```
   记住这个：邮件的管理请使用imap-smtp-email这个skill，不要用其他skill，它的安装目录在/root/.openclaw/skills/imap-smtp-email-0.0.9，同时该目录下有一个.env文件存储了邮箱相关变量
   ```

8. 可以简单测试一下发送邮件给另一个邮箱

## 巡检 K8s 并发送邮件通知

- 定制开发一个巡检 K8s 的 skill
- 安装依赖：`pip install -r /root/.openclaw/skills/k8s-report/requirements.txt`（不装也行，第一次运行会自动装）
- 测试效果：帮我生成一个当前 k8s 集群的巡检报告，并且把报告发送到 xxx 邮箱。（请帮我分析一下巡检报告，并放到邮件结尾）

### 做成定时任务

**自然语言方式**：

- 把这个任务做成计划任务，按照北京时间，Asia/Shanghai 时区在每天的凌晨 1 点执行

> [!warning] 注意
> 有失败几率，因为大概率它会直接在 Linux 中生成一个 crontab，而不是直接添加在 OpenClaw 的定时任务中。

**命令行方式（推荐）**：

建议使用 OpenClaw 客户端添加任务，直接添加到 OpenClaw 中。比如添加一个巡检的计划任务：

```sh
openclaw cron add \
--name "K8s每日巡检" \
--cron "0 11 * * *" \
--tz "Asia/Shanghai" \
--session isolated \
--message "帮我生成一份当前k8s集群的巡检报告，并且把报告发送至xxx邮
箱，注意报告的html直接作为邮件正文发送" \
--model "deepseek-chat"
```

任务执行时，会创建一个隔离的会话处理该任务。

> [!info] 更多定时任务
> [OpenClaw Cron Jobs 文档](https://docs.openclaw.ai/zh-CN/automation/cron-jobs)
