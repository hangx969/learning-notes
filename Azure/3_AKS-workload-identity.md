# AKS中开启workload identity

- AKS开启Workload Identity的依赖项

[在 Azure Kubernetes 服务 (AKS) 上使用 Azure AD 工作负载标识（预览版） - Azure Kubernetes Service | Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Furldefense.com%2Fv3%2F__https%3A%2Fnam06.safelinks.protection.outlook.com%2F%3Furl%3Dhttps*3A*2F*2Furldefense.com*2Fv3*2F__https*3A*2Fdocs.azure.cn*2Fzh-cn*2Faks*2Fworkload-identity-overview*dependencies__*3BIw!!BBM_p3AAtQ!NxzuIBoFPildEvnwnfh55GoLZkGnbcJAQdPlwJEwpvD2I9K1r99RJX96GW7zgNkFvTZoiilY51qzaQAWpQ*24%26data%3D05*7C01*7Changx*40microsoft.com*7Cf505418627d3425733ca08daeef0e160*7C72f988bf86f141af91ab2d7cd011db47*7C1*7C0*7C638085015645861271*7CUnknown*7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0*3D*7C3000*7C*7C*7C%26sdata%3D*2FsUw2MMtYdsdxYj9PQNpxg2ev2jXlif1l5RwpX81ZV4*3D%26reserved%3D0__%3BJSUlJSUlJSUlJSolJSUlJSUlJSUlJSUlJSUlJSUl!!BBM_p3AAtQ!M9iewh_14uLGYpxt93mW8SG-fkyTvOkfj2X_Y-B86-CjFxO7QPipcIJmzRT2SnLK_GSg__odw_eAp8Mxog%24&data=05|01|hangx@microsoft.com|60cfa8df43df4f270e4c08daeeffa413|72f988bf86f141af91ab2d7cd011db47|1|0|638085079067176601|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=k0JxgkojpWQ%2BoXE8Rs%2BV8ut2y2oTg82MJdzcl3SPZYo%3D&reserved=0)

- 安装Az Cli 2.40.0或更高版本

[如何安装 Azure CLI | Microsoft Learn](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Furldefense.com%2Fv3%2F__https%3A%2Fnam06.safelinks.protection.outlook.com%2F%3Furl%3Dhttps*3A*2F*2Furldefense.com*2Fv3*2F__https*3A*2Flearn.microsoft.com*2Fzh-cn*2Fcli*2Fazure*2Finstall-azure-cli__*3B!!BBM_p3AAtQ!NxzuIBoFPildEvnwnfh55GoLZkGnbcJAQdPlwJEwpvD2I9K1r99RJX96GW7zgNkFvTZoiilY51qcCZ0IBw*24%26data%3D05*7C01*7Changx*40microsoft.com*7Cf505418627d3425733ca08daeef0e160*7C72f988bf86f141af91ab2d7cd011db47*7C1*7C0*7C638085015645861271*7CUnknown*7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0*3D*7C3000*7C*7C*7C%26sdata%3D*2F4UsOHbatRfkZYVTqGJeEvFh681RX*2FY*2BRtc*2BOhrC6Uo*3D%26reserved%3D0__%3BJSUlJSUlJSUlJSUlJSUlJSUlJSUlJSUlJSUlJSUlJSUl!!BBM_p3AAtQ!M9iewh_14uLGYpxt93mW8SG-fkyTvOkfj2X_Y-B86-CjFxO7QPipcIJmzRT2SnLK_GSg__odw_fs5rqqnQ%24&data=05|01|hangx@microsoft.com|60cfa8df43df4f270e4c08daeeffa413|72f988bf86f141af91ab2d7cd011db47|1|0|638085079067176601|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=EX8gQIlf8lTqL0c3nqMjeqndcpEO4yOI5r5UI%2BfPcYY%3D&reserved=0)

- 安装 aks-preview Extension

```sh
az extension add --name aks-preview
az extension update --name aks-preview 
```

- 登录az cli

```sh
az cloud set -n AzureChinaCloud
az account set --subscription <name or id>
az login
```

- 注册“EnableWorkloadIdentityPreview”功能标志

```sh
#注册
az feature register --namespace "Microsoft.ContainerService" --name "EnableWorkloadIdentityPreview"

#查看注册状态
az feature list -o table --query "[?contains(name, 'Microsoft.ContainerService/EnableWorkloadIdentityPreview')].{Name:name,State:properties.state}"

#等待几分钟，当状态变为registered后，刷新资源提供程序的注册状态
az provider register --namespace Microsoft.ContainerService
```

- 更新集群，启用oidc-issuer和workload-identity

```sh
az aks update -g <resource group name> -n <cluster name> --enable-oidc-issuer --enable-workload-identity
```

- 获取 OIDC 颁发者 URL 并将其保存到环境变量

```sh
az aks show -g <resource group name> -n <cluster name> --query "oidcIssuerProfile.issuerUrl"
export AKS_OIDC_ISSUER="$(az aks show -g <resource group name> -n <cluster name> --query "oidcIssuerProfile.issuerUrl" -otsv)"
```

- 创建managed identity（测试以managed identity为例，也可以使用AAD application） 

```sh
export SUBSCRIPTION_ID="$(az account show --query id --output tsv)" 
export USER_ASSIGNED_IDENTITY_NAME="myIdentity" 
export RG_NAME="myResourceGroup" 
export LOCATION="chinanorth" 
az identity create --name "${USER_ASSIGNED_IDENTITY_NAME}" --resource-group "${RG_NAME}" --location "${LOCATION}" --subscription "${SUBSCRIPTION_ID}"
```

- 创建Kubernetes service account

```sh
az aks get-credentials -g <resource group name> -n <cluster name>
export SERVICE_ACCOUNT_NAME="workload-identity-sa"
export SERVICE_ACCOUNT_NAMESPACE="my-namespace"
```

```yaml
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: "${USER_ASSIGNED_CLIENT_ID}"
  labels:
    azure.workload.identity/use: "true"
  name: "${SERVICE_ACCOUNT_NAME}"
  namespace: "${SERVICE_ACCOUNT_NAMESPACE}"
EOF
```

- 建立联合标识凭据

```sh
az identity federated-credential create --name <federated Identity name> --identity-name "${USER_ASSIGNED_IDENTITY_NAME}"--resource-group "${RG_NAME}" --issuer "${AKS_OIDC_ISSUER}" --subject system:serviceaccount:"${SERVICE_ACCOUNT_NAMESPACE}":"${SERVICE_ACCOUNT_NAME}"
```

# Lab-pod挂载workload identity访问keyvault

- Set Environment

```sh
# environment variables for the Azure Key Vault resource
export KEYVAULT_NAME="hangwikv1"
export KEYVAULT_SECRET_NAME="hangsecret1"
export RESOURCE_GROUP="aksWI"
export LOCATION="chinanorth2"

# environment variables for the user-assigned managed identity
# [OPTIONAL] Only set this if you're using a user-assigned managed identity as part of this tutorial
export USER_ASSIGNED_IDENTITY_NAME="hangWI1"

# environment variables for the Kubernetes service account & federated identity credential
export SERVICE_ACCOUNT_NAMESPACE="default"
export SERVICE_ACCOUNT_NAME="hangwi1"
export SERVICE_ACCOUNT_ISSUER="https://chinanorth2.oic.prod-aks.azure.cn/xxxxxx/" 
```

- Create key vault

```sh
az keyvault create --resource-group "${RESOURCE_GROUP}" --location "${LOCATION}" --name "${KEYVAULT_NAME}"
export USER_ASSIGNED_IDENTITY_CLIENT_ID="$(az identity show --name "${USER_ASSIGNED_IDENTITY_NAME}" --resource-group "${RESOURCE_GROUP}" --query 'clientId' -otsv)"
export KEYVAULT_URL="$(az keyvault show -g ${RESOURCE_GROUP} -n ${KEYVAULT_NAME} --query properties.vaultUri -o tsv)"
```

- Set policy

```sh
az keyvault set-policy --name "${KEYVAULT_NAME}" \ --secret-permissions get \ --spn "${USER_ASSIGNED_IDENTITY_CLIENT_ID}" 
```

- Create workload (a pod)

~~~yaml
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: quick-start
  namespace: ${SERVICE_ACCOUNT_NAMESPACE}
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: ${SERVICE_ACCOUNT_NAME}
  containers:
    - image: ghcr.io/azure/azure-workload-identity/msal-go
      name: oidc
      env:
      - name: KEYVAULT_URL
        value: ${KEYVAULT_URL}
      - name: SECRET_NAME
        value: ${KEYVAULT_SECRET_NAME}
  nodeSelector:
    kubernetes.io/os: linux
EOF
~~~

# Lab-pod挂载WI获取AccessToken

- [sample-dotnet-worker-servicebus-queue/deploy-app-with-workload-identity.yaml at main · kedacore/sample-dotnet-worker-servicebus-queue · GitHub](https://github.com/kedacore/sample-dotnet-worker-servicebus-queue/blob/main/deploy/workload-identity/deploy-app-with-workload-identity.yaml)

~~~yaml
cat order-processor.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-processor
  labels:
    app: order-processor
    azure.workload.identity/use: "true"
spec:
  selector:
    matchLabels:
      app: order-processor
  template:
    metadata:
      labels:
        app: order-processor
    spec:
      serviceAccountName: hangwi1
      containers:
      - name: order-processor
        image: ghcr.io/kedacore/sample-dotnet-worker-servicebus-queue:latest
        env:
        - name: KEDA_SERVICEBUS_AUTH_MODE
          value: WorkloadIdentity
        - name: KEDA_SERVICEBUS_HOST_NAME
          value: elksvcBus.servicebus.chinacloudapi.cn
        - name: KEDA_SERVICEBUS_QUEUE_NAME
          value: orders
EOF
~~~

- 获取pod中挂进去的azure identity token，可以在[jwt.ms: Welcome!](https://jwt.ms/)中decode：

~~~sh
k exec -it order-processor-8649d8cbb8-mn6mg /bin/sh
cat /run/secrets/azure/tokens/azure-identity-token
~~~

- 可以拿identity token，通过postman去兑换access token

![image-20241010100053457](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202410101000598.png)

POST的endpoint可以在AAD - App registration - endpoints里面找

client_id 使用的下划线而不是短杠

# Lab-pod挂载WI直接拿到access token

- 挂载service account进去，在cat /run/secrets/azure/tokens/azure-identity-token里面就能看到azure access token：

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: centos
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: hangwi1
  containers:
    - name: centos
      image: dockerhub.azk8s.cn/library/centos:latest
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]
~~~

```sh
k exec -it centos-workload-identity -- /bin/bash
#查看token
cat /run/secrets/azure/tokens/azure-identity-token
```

