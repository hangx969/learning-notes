# 介绍

- github地址：https://github.com/kubernetes-sigs/external-dns
- release pages: https://github.com/kubernetes-sigs/external-dns/releases
- artifact hub: https://artifacthub.io/packages/helm/external-dns/external-dns

> - external-dns配置azure dns教程：https://kubernetes-sigs.github.io/external-dns/v0.13.6/tutorials/azure/
> - 视频教程：https://www.youtube.com/watch?v=VSn6DPKIhM8&list=PLpbcUe4chE79sB7Jg7B4z3HytqUUEwcNE，https://github.com/HoussemDellai/aks-course/tree/main/61_external_dns
> - github示例：https://github.com/HoussemDellai/aks-course/tree/main/61_external_dns
> 

- AKS中的app，通过ingress暴露了一个IP以供访问，需要配置一个域名绑定IP方便访问，往往公司已经有了一个注册域名，这个app一般会用公司域名下的custom sub-domain name，例如app1.mycompany.com。公司域名的解析可能已经用了一个外部DNS提供商比如AzureDNS，我们就需要把app1.mycompany.com这个域名解析记录添加到外部DNS提供商。

- ExternalDNS 将公开的Kubernetes Service和Ingress与DNS提供商同步。与KubeDNS不同的是，它本身并不是一个DNS服务器，而只是用于对接其他DNS提供商。

# 下载

~~~sh
helm repo add --force-update external-dns https://kubernetes-sigs.github.io/external-dns
helm repo update external-dns
helm pull external-dns/external-dns --version 1.14.4
~~~

# 配置

> 以Azure作为外部DNS为例：https://kubernetes-sigs.github.io/external-dns/v0.13.6/tutorials/azure/#managed-identity-using-workload-identity

- Azure DNS托管域名的大致过程：

  - 首先从域名注册机构注册一个父域名比如xyz


  - 让Azure DNS托管子域app1.xyz


  - 再去域名注册机构，配置使用azure dns nameserver
  - 配置文件中的source字段指定了监控哪些服务（例如ingress、service）；provider字段指定了外部dns服务商，我们用的是azure-private-dns-zone
  - 创建ingress和service时可以通过annotations字段指定hostname，external dns就会同步到外部dns
- 与Azure的身份验证：

  - SP or MI？
    - SPN的方式，通过azure.json里面写入appID，secret等信息绑定到SPN，azure层面做一下RBAC授权（RG的reader，DNS Zone的DNS Zone Contributor）
    - MI是用的kubelet Identity，因为是所有pod共用的，会存在安全问题。

  - workload identity？可以限制仅某些pod可以使用，external-dns已经支持workloadIdentityExtension。配置方式见官网。

# 安装

~~~sh
helm upgrade -i external-dns -n external-dns . -f values.yaml --create-namespace
~~~

