# 介绍

- 官网地址：https://external-secrets.io/latest/
- release pages: https://github.com/external-secrets/external-secrets/releases
- artifact hub: https://artifacthub.io/packages/helm/external-secrets-operator/external-secrets
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

参考文档：https://external-secrets.io/latest/provider/azure-key-vault/

## 前提条件

1. 配置user-assigned managed identity （或者workload identity）
2. 对Azure Keyvault赋予identity读取secret的权限
3. 复制identity的client id

## 部署ClusterSectretStore对象

ClusterSecretStore/SecretStore负责指定Azure Keyvault、identity认证信息

~~~yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: <name-of-Cluster-SecretStore>
  namespace: <your-namespace>
spec:
  provider:
    azurekv:
      authType: ManagedIdentity
      tenantId: <your-tenant-id>  # Set tenant id where the managed identity resides
      identityId: <MI-clientId>        # Optionally set the Id of the Managed Identity, if multiple identities are assigned to external-secrets operator
      vaultUrl: <your-keyvault-FQDN>   # URL of your vault instance, see: https://docs.microsoft.com/en-us/azure/key-vault/general/about-keys-secrets-certificates
      environmentType: ChinaCloud
~~~

## 部署ExternalSecret对象

ExternalSecret对象负责把Azure Keyvault secret转换为Kubernetes Secrets。

~~~yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: <name-of-ExternalSecret>
  namespace: <your-namespace>
spec:
  refreshInterval: 1h  # rate ESO pulls Azure Key Vault
  secretStoreRef:
    name: <name-of-SecretStore>
    kind: ClusterSecretStore  # Kind of the SecretStore
  target:
    name: <name-of-k8s-Secret-to-be-created>
    creationPolicy: Owner #
  data:
    # name of the SECRET in the Azure KV (no prefix is by default a SECRET)
    - secretKey: ca.crt
      remoteRef:
        key: ca-crt
~~~

# 集成HashiCorp Valut

HashiCorp Vault 是一个开源工具，提供对密钥（如 API 密钥、密码、证书和其他敏感数据）的安全访问。Vault 提供强大的功能，如动态密钥、密钥租用和续订、撤销和详细的审计日志。

## helm部署hashiCorp Valut

~~~sh
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
helm install vault hashicorp/vault --set "server.ha.enabled=true"
~~~

## 初始化和解封vault

1. 端口转发到Vault Pod

   ~~~sh
   kubectl port-forward vault-0 8200:8200
   export VAULT_ADDR='http://127.0.0.1:8200
   ~~~

2. 初始化vault

   ~~~sh
   vault operator init
   ~~~

3. 解封vault

   ~~~sh
   vault operator unseal <Unseal Key 1>
   vault operator unseal <Unseal Key 2>
   vault operator unseal <Unseal Key 3>
   ~~~

## 配置vault以进行k8s身份验证

~~~sh
vault auth enable kubernetes
vault write auth/kubernetes/config \
    token_reviewer_jwt="$(kubectl get secret $(kubectl get serviceaccount vault -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode)" \
    kubernetes_host=https://$KUBERNETES_PORT_443_TCP_ADDR:443 \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
~~~

## 保存vault token

创建一个secret保存vault token

~~~sh
kubectl create secret generic vault-credentials \
    --from-literal=token=<VAULT_TOKEN>
~~~

## 创建SecretStore

~~~yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "http://vault.default.svc.cluster.local:8200"
      path: "secret"
      version: "v2"
      auth:
        tokenSecretRef: #这里用vault token认证
          name: vault-credentials
          key: token
~~~

## 创建externalSecret从vault获取密钥

~~~yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-secret
spec:
  refreshInterval: "1h"
  secretStoreRef: #引用secretStore名称
    name: vault-backend
    kind: SecretStore
  target: # 需要在k8s中生成的secret名称
    name: my-secret
    creationPolicy: Owner
  data: 
  - secretKey: my-secret-key # 定义生成的k8s secret中的key名称
    remoteRef: # vault中的secret名称
      key: secret/data/my-secret-path
      property: my-secret-property
~~~

## 在pod中引用secret

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app-image
        env:
        - name: MY_SECRET
          valueFrom:
            secretKeyRef:
              name: my-secret
              key: my-secret-key
~~~

