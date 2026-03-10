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
首先需要自行开通邮箱 SMTP 和 IMAP 服务，并且记录授权码，可以选择 163、qq 等邮箱。

## 配置邮箱Skills
- 下载邮箱Skills： https://clawhub.ai/gzlicanyi/imap-smtp-email
- 执行 setup.sh 脚本，添加邮箱配置：
```bash
bash setup.sh
```
- 把skill放到openclaw/skills目录