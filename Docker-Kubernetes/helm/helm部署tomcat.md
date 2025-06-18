# 介绍

github地址：https://github.com/bitnami/charts/blob/main/bitnami/tomcat/README.md

artifactHub地址：https://artifacthub.io/packages/helm/bitnami/tomcat

# 下载

~~~python
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update bitnami
helm pull bitnami/tomcat --version 11.7.12
~~~

> 注：
>
> - bitnami/tomcat如果网络问题pull不下来就直接从bitnami github上clone下来源码，里面就有tomcat的helm chart。
>
>   ~~~sh
>   git clone https://github.com/bitnami/charts.git
>   ~~~

# 配置

service用NodePort，暴露端口30006。

~~~yaml

~~~

# 安装

~~~sh
kubectl create ns tomcat
helm upgrade -i tomcat -n tomcat -f values.dev.yaml .
~~~

# 使用
