---
title: AKS SecretProviderClass with KeyVault
tags:
  - azure/aks
  - azure/keyvault
  - azure/secrets
aliases:
  - SecretProviderClass
  - AKS KeyVault Integration
date: 2026-04-16
---

# AKS SecretProviderClass with KeyVault

## Related Notes

- [[Azure/2_AKS-basics]]
- [[Azure/3_AKS-workload-identity]]

---

## Introduction

- ==SecretProviderClass== is an AKS plugin responsible for converting Azure Key Vault secrets into Kubernetes Secrets
- Reference docs:
  - Azure docs: https://docs.azure.cn/en-us/aks/csi-secrets-store-configuration-options
  - SecretProviderClass supported parameters: https://github.com/Azure/secrets-store-csi-driver-provider-azure/blob/master/website/content/en/getting-started/usage/_index.md

---

## Deployment

### Prerequisites

> [!important] Required Steps Before Deployment
> 1. Create a ==user-assigned managed identity== (or configure workload identity)
> 2. Grant the identity permission to read Secrets on Azure Key Vault (Access Policy or RBAC)
> 3. Copy the identity's client ID

### Create SecretProviderClass

```yaml
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
```

> [!note] Namespace
> The namespace of the newly created Kubernetes secret will be the same as the SecretProviderClass.
