# 介绍

- 使用certmanager，对cloudfare申请的域名签发证书：https://todoit.tech/k8s/cert/
- certmanager官网：https://cert-manager.io/docs/installation/helm/

- 使用 HTTPS 需要向权威机构申请证书，并且需要付出一定的成本，如果需求数量多，则开支也相对增加。[cert-manager](https://cert-manager.io/docs/) 是 Kubernetes 上的全能证书管理工具，支持利用 cert-manager 基于 [ACMEopen](https://tools.ietf.org/html/rfc8555) 协议与[Let's Encryptopen](https://letsencrypt.org/) 签发免费证书并为证书自动续期，实现永久免费使用证书。

# 拉取

~~~sh
helm repo add jetstack https://charts.jetstack.io 
helm repo update jetstack
helm pull jetstack/cert-manager --version v1.16.1
~~~

# 配置

~~~yaml

~~~

# 安装

~~~sh
helm upgrade -i cert-manager -n cert-manager . --values values.yaml
~~~

