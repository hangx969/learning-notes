# 介绍

- github地址：https://github.com/bitnami/charts/blob/main/bitnami/tomcat/README.md

- artifactHub地址：https://artifacthub.io/packages/helm/bitnami/tomcat


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
>
> - 注意需要把charts/bitnami/common目录放到tomcat/charts/目录里面才能组成完整的helm chart，因为common是子chart需要安装。

# 配置

service用NodePort，暴露端口30080。

~~~yaml
global:
  defaultStorageClass: "sc-nfs"
  storageClass: "sc-nfs"

tomcatUsername: user
tomcatPassword: "111111"
replicaCount: 1
deployment:
  type: deployment
containerPorts:
  http: 8080
pdb:
  create: false
persistence:
  enabled: true
  storageClass: "sc-nfs"
  size: 200Mi

service:
  type: NodePort
  ports:
    http: 80
  nodePorts:
    http: "30080"
~~~

# 安装

~~~sh
kubectl create ns tomcat
helm upgrade -i tomcat -n tomcat -f values.dev.yaml .
~~~

# 使用

```sh
# 1. Get the Tomcat URL by running:
export NODE_PORT=$(kubectl get --namespace tomcat -o jsonpath="{.spec.ports[0].nodePort}" services tomcat)
export NODE_IP=$(kubectl get nodes --namespace tomcat -o jsonpath="{.items[0].status.addresses[0].address}")
echo "Tomcat URL: http://$NODE_IP:$NODE_PORT"
echo "Tomcat Management URL: http://$NODE_IP:$NODE_PORT/manager"

# 2. Login with the following credentials
echo Username: user
echo Password: $(kubectl get secret --namespace tomcat tomcat -o jsonpath="{.data.tomcat-password}" | base64 -d)
```

