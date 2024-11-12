# 介绍

- external-dns配置azure dns教程：https://kubernetes-sigs.github.io/external-dns/v0.13.6/tutorials/azure/
- github地址：https://github.com/kubernetes-sigs/external-dns
- 视频教程：https://www.youtube.com/watch?v=VSn6DPKIhM8&list=PLpbcUe4chE79sB7Jg7B4z3HytqUUEwcNE

- ExternalDNS 将公开的 Kubernetes Service 和 Ingress 与 DNS 提供商同步。与 KubeDNS 不同的是，它本身并不是一个 DNS 服务器，而只是用于对接其他 DNS 提供商。

# 下载

~~~sh
helm repo add --force-update external-dns https://kubernetes-sigs.github.io/external-dns
helm repo update external-dns
helm pull external-dns/external-dns --version 1.14.4
~~~

# 安装

~~~sh
helm upgrade -i external-dns -n external-dns --version 1.14.4 -f values.yaml --create-namespace
~~~

