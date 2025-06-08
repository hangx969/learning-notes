# 介绍

- secretProviderClass是AKS提供的一个插件，负责将Azure Keyvault secret转换为Kubernetes Secret
- 参考文档：
  - Azure文档：https://docs.azure.cn/en-us/aks/csi-secrets-store-configuration-options
  - SecretProviderClass支持的参数：https://github.com/Azure/secrets-store-csi-driver-provider-azure/blob/master/website/content/en/getting-started/usage/_index.md

# 部署

## 前提条件

1. 创建一个user-assigned managed identity （或者配置workload identity）
2. 对Azure Keyvault赋予identity读取Secret的权限（Access Policy或者RBAC）
3. 复制identity的client id

## 创建SecretProviderClass

~~~yaml
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: <Name-of-SecretProviderClass>
  namespace: <your-namepace>
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    tenantId: <tenant-id>
    # Set the clientID of the user-assigned managed identity to use, e.g. azurekeyvaultsecretsprovider-aks-commoninfra-dev-chinanorth3
    userAssignedIdentityID: <secretProviderIdentityId>
    keyvaultName: <keyvaultName>
    cloudName: AzureChinaCloud
    objects:  |
      array:
        - |
          objectName: <Azure-Key-vault-secret-name>
          objectType: secret
          objectVersion: ""
# This creates an actual kubernetes secret that we can mount to pods
  secretObjects:
  - secretName: <kubernetes-secret-name-to-be-generated> # Note that the namespace of newly created secret will be the same as this SecretProviderClass
    data:
    - key: <key-name> # add a secret referencable with the same key as was in the keyvault
      objectName: <keep-the-same-of-"spec.parameters.objects.objectName">
    type: Opaque
~~~

