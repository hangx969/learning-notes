---
title: Helm部署External-Secrets
tags:
  - kubernetes
  - security
  - auth
aliases:
  - external-secrets部署
---

# 介绍

- 官网地址：[External Secrets Operator](https://external-secrets.io/latest/)
- release pages: [External Secrets Releases](https://github.com/external-secrets/external-secrets/releases)
- artifact hub: [external-secrets helm chart](https://artifacthub.io/packages/helm/external-secrets-operator/external-secrets)
- 作用是从外部secrets提供商读取secrets，写入到k8s secrets

## 为什么需要 ESO

> 来源：[K8S实战教程: 如何使用 External Secrets Operator 管理 Kubernetes密钥](https://mp.weixin.qq.com/s/uXjo4bNQ-_s-9acP2KroLg)

| 痛点 | 传统 K8s Secret | External Secrets Operator |
|------|------------------|---------------------------|
| 版本控制风险 | 容易误入 Git / 明文 YAML | 不在仓库中存敏感值 |
| 轮换复杂度 | 需人工更新 + 重启 | 外部变更 → 自动同步 |
| 中心化治理 | 分散在各环境 | 外部 Secret Manager 为单一真源 |
| 权限与审计 | 依赖集群权限 | 结合云厂商 IAM / 审计日志 |
| 多环境一致性 | 手动复制 | 同模板 + 不同后端 Key |

## 工作原理

ESO 通过自定义资源（CRD）与控制器 Reconcile Loop 实现同步：

1. 定义 **SecretStore / ClusterSecretStore** → 指向外部密钥系统
2. 创建 **ExternalSecret** → 声明需要获取哪些外部密钥、映射策略、刷新间隔
3. **ESO 控制器**使用凭证或云原生身份（如 IRSA / Managed Identity）调用外部 API
4. 拉取密钥内容，生成或更新目标 **Kubernetes Secret**
5. Pod 以普通方式（env / volume）消费该 Secret
6. 外部值变化 → 下一次 `refreshInterval` 周期内自动同步

核心 CRD：

| CRD | 作用 |
|-----|------|
| SecretStore | 命名空间级密钥存储引用 |
| ClusterSecretStore | 集群级复用（多命名空间共享） |
| ExternalSecret | 声明"要什么 + 取哪里 + 怎么映射" |

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

参考文档：[Azure Key Vault Provider](https://external-secrets.io/latest/provider/azure-key-vault/)

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

# 集成AWS Secrets Manager

## 创建访问凭证

生产环境首选 IRSA（无需静态 AK/SK）。示例使用静态凭证：

~~~sh
kubectl create secret generic aws-credentials \
  --from-literal=access_key=AKIAxxxxxxxx \
  --from-literal=secret_access_key=xxxxxxxxxxxxxxxx
~~~

最小权限 IAM Policy：

~~~json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:secretsmanager:us-east-1:111122223333:secret:my-secret-*"
    }
  ]
}
~~~

## 创建SecretStore

~~~yaml
apiVersion: external-secrets.io/v1
kind: SecretStore
metadata:
  name: aws-secret-store
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        secretRef:
          accessKeyIDSecretRef:
            name: aws-credentials
            key: access_key
          secretAccessKeySecretRef:
            name: aws-credentials
            key: secret_access_key
~~~

## 创建ExternalSecret

~~~yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: app-external-secret
spec:
  refreshInterval: 1m
  secretStoreRef:
    name: aws-secret-store
    kind: SecretStore
  target:
    name: app-secret
    creationPolicy: Owner
  dataFrom:
    - extract:
        key: app_credentials    # AWS Secrets Manager 中的密钥名
~~~

# 进阶用法

## 精细字段映射

只取外部 JSON 的部分字段并重命名：

~~~yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: partial-external-secret
spec:
  secretStoreRef:
    name: demo-secret-store
  target:
    name: db-secret
  data:
    - secretKey: db.user       # K8s Secret 中的 key 名
      remoteRef:
        key: app_db_creds      # 外部密钥名
        property: username     # JSON 中的字段
    - secretKey: db.password
      remoteRef:
        key: app_db_creds
        property: password
~~~

## 模板渲染

用 Go template 语法对拉取的值进行组合或变换：

~~~yaml
target:
  name: rendered-secret
  template:
    type: Opaque
    data:
      FULL_NAME: "{{ .FIRST_NAME }} {{ .MIDDLE_NAME }} {{ .LAST_NAME }}"
      CONNECTION_STRING: "postgresql://{{ .DB_USER }}:{{ .DB_PASS }}@{{ .DB_HOST }}:5432/mydb"
~~~

## creationPolicy 策略

| 策略 | 行为 |
|------|------|
| Owner | 删除 ExternalSecret 时同步删除目标 K8s Secret（默认） |
| Merge | 合并到已有 Secret，不覆盖其他 key |
| Orphan | 删除 ExternalSecret 时保留目标 Secret |

## 结合 GitOps

- Git 中仅保存 ExternalSecret / SecretStore 声明（无明文值）
- 外部密钥平台负责生命周期
- Argo CD / Flux + ESO → "配置即代码 + 动态密钥"

# 监控与可观测

| 指标 | 说明 |
|------|------|
| Reconcile 成功/失败次数 | 识别后端权限/网络问题 |
| 同步延迟 | 外部变更到内部生效的耗时 |
| 错误类型 | 鉴权/速率限制/字段缺失 |

- 通过 Prometheus 抓取 ESO 暴露的 Metrics（Chart 自带 ServiceMonitor）
- 失败次数连续 N 次 → 触发告警
- `kubectl describe externalsecret` 查看事件和同步状态

> [!warning] refreshInterval 设置
> 过短会导致后端 API 速率限制（rate limiting），建议生产环境 ≥ 1h，非敏感场景 ≥ 5m。

# 与其他密钥管理方案对比

| 方案 | 特点 | 适用场景 |
|------|------|----------|
| K8s Secret（原生） | 简单；需自行加密管理 | 小规模/非敏感环境 |
| Sealed Secrets | GitOps 友好；静态加密 | 发布前加密、变化不频繁 |
| Mozilla SOPS | 支持多种 KMS；开发灵活 | 复杂 KMS 组合需求 |
| CSI Secret Store Driver | 以 Volume 动态挂载 | 文件型/短时读取、不入 env |
| **External Secrets Operator** | 云密钥源同步、自动轮换 | 中大型生产、集中治理 |

> [!tip] 可组合使用
> ESO 负责"拉取 + 生成 Secret"，应用以 env 或文件消费。若需要文件形式 + 不进入 etcd，可结合 CSI Secret Store Driver。

# 生产落地路线

1. **PoC 阶段**：单命名空间 + SecretStore + 静态 AK/SK
2. **生产化**：迁移到 ClusterSecretStore + 云原生身份（IRSA / Managed Identity / Workload Identity）
3. **GitOps**：纳入 Argo CD，禁止直接 kubectl 手工改
4. **可观测**：打通 Metrics / Alert / 日志追踪
5. **安全收口**：策略、轮换、审计、密钥分类分级
6. **自动化**：轮换事件 → 应用热更新（信号 / sidecar）

