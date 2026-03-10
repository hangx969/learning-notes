# 基于飞书+OpenClaw远程智能管理K8s集群
- 安装kubectl skill
	- 下载地址： https://clawhub.ai/ddevaal/kubectl
	- 解压到openclaw工作目录的skills目录下
- 是基于kubectl来管理的，所以需要在openclaw机器上安装kubectl，并且拿到集群的kubeconfig文件，放到`~/.kube/config` ，需要直接kubectl get nodes运行。

完成后即可以自然语言下发命令：
- 获取当前k8s集群的版本信息，node数量和IP，以及istio-system命名空间下的pod列表和运行状态。整理成表格发给我。
- 帮我查询一下default命名空间下有没有异常状态的pod，如果有帮我查询异常的原因。注意：仅查询，并不需要修复

# 基于飞书+OpenClaw巡检K8s集群
## 配置邮箱服务
首先需要自行开通邮箱 SMTP 和 IMAP 服务，并且记录授权码，可以选择 163、qq 等邮箱。这个邮箱会作为发件人被openclaw使用。

## 配置邮箱Skills
- 下载邮箱Skills： https://clawhub.ai/gzlicanyi/imap-smtp-email
- 执行 setup.sh 脚本，添加邮箱配置：
```bash
bash setup.sh
```
- 把skill放到openclaw/skills目录
- 把Skills.md中一些不需要的变量给删掉，否则WebUI中的skills状态显示为不可用：
```markdown
      env:
        - IMAP_HOST
        - IMAP_USER
        - IMAP_PASS
        - SMTP_HOST
        - SMTP_USER
        - SMTP_PASS
```
- `npm install` 安装一下这个Skill
- 去WebUI - 技能找到imap-smtp-email，在API Key中填入邮箱授权码-保存。
- 让openclaw记住使用这个skills：
```
记住这个：邮件的管理请使用imap-smtp-email这个skill，不要用其他skill，它的安装目录在/root/.openclaw/skills/imap-smtp-email-0.0.9，同时该目录下有一个.env文件存储了邮箱相关变量
```
- 可以简单测试一下发送邮件给另一个邮箱。

## 巡检k8s并发送邮件通知
- 定制开发一个巡检k8s的skill： 
- 安装依赖：`pip install -r /root/.openclaw/skills/k8s-report/requirements.txt` （不装也行，第一次运行会自动装）
- 测试效果： 帮我生成一个当前k8s集群的巡检报告，并且把报告发送到xxx邮箱。

### 做成定时任务
自然语言：
- 把这个任务做成计划任务，按照北京时间，Asia/Shanghai时区在每天的凌晨1点执行

命令行执行：
注意，添加的任务可能是宿主机的 Crontab，建议使用 openclaw 客户端添加任务。比如添加一个巡检的计划任务：

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

更多定时任务： https://docs.openclaw.ai/zh-CN/automation/cron-jobs
