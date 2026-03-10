# 基于飞书+OpenClaw远程智能管理K8s集群
- 安装kubectl skill
	- 下载地址： https://clawhub.ai/ddevaal/kubectl
	- 解压到openclaw工作目录的skills目录下
- 是基于kubectl来管理的，所以需要在openclaw机器上安装kubectl，并且拿到集群的kubeconfig文件，放到`~/.kube/config` ，需要直接kubectl get nodes运行。



