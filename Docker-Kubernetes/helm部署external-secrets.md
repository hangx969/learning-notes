# 介绍

- 官网地址：https://external-secrets.io/latest/
- 作用是从外部secrets提供商读取secrets，写入到k8s secrets

# 下载

~~~sh
helm repo add --force-update external-secrets https://charts.external-secrets.io
helm repo update external-secrets
helm pull external-secrets/external-secrets --version 0.10.5
~~~

# 配置

- 根据ado的配置添加了一些resource limits

# 安装

~~~sh
helm upgrade -i external-secrets -n external-secrets . -f values.yaml --create-namespace
~~~

# 集成Azure Key Vault

- https://external-secrets.io/latest/provider/azure-key-vault/
