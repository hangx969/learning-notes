# az devops cli

## 登录devops

https://learn.microsoft.com/en-us/azure/devops/cli/log-in-via-pat?view=azure-devops&tabs=windows

~~~sh
echo "xxx" | az devops login --organization https://dev.azure.com/xxx
cat PAT.txt | az devops login --organization https://dev.azure.com/xxx
~~~

## 操作agent pool

https://learn.microsoft.com/en-us/cli/azure/pipelines/pool?view=azure-cli-latest

- 获取pool id

~~~sh
az pipelines pool list  > pools.json
~~~

- 显示pool具体信息

  ~~~sh
  az pipelines pool show	--id 56
  ~~~

## 操作agents

https://learn.microsoft.com/en-us/cli/azure/pipelines/agent?view=azure-cli-latest

- list

  ~~~sh
  az pipelines agent show --id 77315 --pool-id 56 --include-assigned-request true --include-last-completed-request true --output jsonc
  ~~~

- detect status

- delete: azcli没有提供删除agent的命令，只能通过REST API来操作

## 检测agent current status

~~~sh
az pipelines agent show \
--id 77398 \
--pool-id 56 \
--include-assigned-request true \ #关键在于这个参数可以获取agent现在是否正有job在跑。这个参数也是通过REST API发送的。
--include-last-completed-request true \
--output jsonc
# --debug 可以看到azcli发送REST API的具体过程和参数
~~~

- 有job在跑的agent，返回值带有一大段“assignedRequest”字段：

  ~~~json
  {
      "accessPoint": "CodexAccessMapping",
      "assignedAgentCloudRequest": null,
      "assignedRequest": {
        "agentDelays": null,
        "agentSpecification": null,
        "assignTime": "2025-02-19T07:27:43.060000+00:00",
        "data": {
          "IsScheduledKey": "False",
          "ParallelismTag": "Private"
        },
  ......
    }
  ~~~

- idle的agent，返回值里面assigned request是null。（注意：如果这个agent上面有job已经跑完了，则assigned request仍然是null）

  ~~~json
  {
      "accessPoint": "CodexAccessMapping",
      "assignedAgentCloudRequest": null,
      "assignedRequest": null,
  ......
  }
  ~~~

# Azure devops REST API

## 删除offline的agent

shell脚本实现

参考：

1. https://thanhtunguet.info/posts/delete-offline-agents-from-azure-devops-pools/
2. REST API文档：https://learn.microsoft.com/en-us/rest/api/azure/devops/distributedtask/agents/delete?view=azure-devops-rest-7.1
3. REST API可以附加的参数：https://learn.microsoft.com/en-us/rest/api/azure/devops/distributedtask/agents/get-agent?view=azure-devops-rest-7.1#uri-parameters
4. PAT document：https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Linux#q-why-did-my-pat-stop-working

==一定注意：curl传递的authorization header是在原有token前面加了个:==

~~~sh
#!/usr/bin/env bash

# Set your Azure DevOps organization URL and PAT token (Note that PAT should be encoded with base64)
ORG_URL="https://dev.azure.com/xxxx"
PAT_TOKEN=""

# Encode the PAT token as base64 for use in the Authorization header, pay atttention to the : prefix and -w0 to avoid line break
PAT_TOKEN_B64=$(printf "%s"":$PAT_TOKEN" | base64 -w0)

# Set the agent pool ID and API version
POOL_ID="$1"
API_VERSION="7.1"

# Get a list of all agents in the pool
AGENTS=$(curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents?api-version=${API_VERSION}")

# Loop through each agent and delete the offline agents
for AGENT in $(echo $AGENTS | jq -r '.value[].id')
do
  STATUS=$(echo $AGENTS | jq -r --arg AGENTID "$AGENT" '.value[] | select(.id == ($AGENTID | tonumber)) | .status')

  if [ "$STATUS" == "offline" ]
  then
    echo "Deleting agent with ID $AGENT"
    curl -s -X DELETE -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents/${AGENT}?api-version=${API_VERSION}"
  fi
done
~~~

~~~sh
chmod +x azure-devops-delete-offline-agents.sh
# To run the script, pass the agent pool ID as an argument.
./azure-devops-delete-offline-agents.sh <pool_id>
~~~

## 检测agent current status

用Get Agent API检查每个具体agent信息：

~~~sh
# Set your Azure DevOps organization URL and PAT token
ORG_URL="https://dev.azure.com/xxx"
PAT_TOKEN_B64=""

# Set the agent pool ID and API version
POOL_ID="56"
API_VERSION="7.1"

curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents/${AGENT_ID}?includeAssignedRequest=true&includeCapabilities=true&api-version=${API_VERSION}" > agent-info.json
~~~

## 脚本逻辑

> 注意：
>
> - azcli pod中需要先安装gawk：`yum install gawk -y`

1. 根据pool name获取pool id
2. 获取这个pool中的所有agent id和agent count
3. 删掉offline的agent，检测对应的vm instance如果有就删掉（防止后面scale out出新的时候，与已经offline的冲突）
5. 过滤出：

   - 状态为online

   - assignedRequest字段不存在

   - created-on时间距今已超过5天


   提取出这些agent的computerName。

6. scale-in: 用azcli删掉这些agent对应的VM instance
7. scale-out：判断剩余agent数量是否小于4个，如果是，就scale out到4个。

~~~sh
#!/bin/bash

yum install -y gawk
ORG_URL="https://dev.azure.com/xxx"
PAT_TOKEN=${AZURE_DEVOPS_PAT}
# Encode PAT for use in the Authorization header, pay atttention that : prefix is required
PAT_TOKEN_B64=$(printf "%s"":$PAT_TOKEN" | base64 -w0)
API_VERSION="7.1"

# Resrouce group and VMSS name
RG_NAME=${VMSS_RG_NAME}
VMSS_NAME=${VMSS_NAME}

# Get devops pool id by pool name
POOL_NAME=${POOL_NAME}

POOL_ID=$(curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools?api-version=${API_VERSION}" | jq -r '.value[] | select(.name == "'$POOL_NAME'") | .id')

if [ -z "$POOL_ID" ]; then
    echo "Pool $POOL_NAME not found, please check the pool name and PAT token"
    exit 1
fi
echo "Agent pool $POOL_NAME found, Pool ID: $POOL_ID"

# Login AzureChina and set RG and VMSS name
az account clear && az cloud set --name AzureChinaCloud && az login --service-principal --username "${AZURE_CLIENT_ID}" --tenant "${AZURE_TENANT_ID}" --federated-token "$(cat $AZURE_FEDERATED_TOKEN_FILE)"


# Get VM instance id by agent computer name
function getInstanceID() {
    local RG_NAME=$1
    local VMSS_NAME=$2
    local TARGET_COMPUTER_NAME=$3

    # Get the map of instance ids to computer names for all instances in the VMSS
    local INSTANCES=$(az vmss list-instances --resource-group $RG_NAME --name $VMSS_NAME --query "[].{name:name, computerName:osProfile.computerName}" -o json)

    for INSTANCE in $(echo $INSTANCES | jq -c '.[]'); do
        local INSTANCE_NAME=$(echo $INSTANCE | jq -r '.name')
        local COMPUTER_NAME=$(echo $INSTANCE | jq -r '.computerName')

        if [ "$COMPUTER_NAME" == "$TARGET_COMPUTER_NAME" ]; then
            local INSTANCE_ID=$(echo $INSTANCE_NAME | awk -F'_' '{print $NF}')
            echo $INSTANCE_ID
            return
        fi
    done

    # If the agent is not found, return empty string
    echo ""
}


# Get a list of all agent ids in the pool
AGENT_IDS=$(curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents?api-version=${API_VERSION}" | jq -r '.value[].id')

# Loop through the agent ids and get the details for each agent
for AGENT_ID in $AGENT_IDS; do

    # Get info of each agent, including assignedRequest and capabilities
    AGENT_INFO=$(curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents/${AGENT_ID}?includeAssignedRequest=true&includeCapabilities=true&api-version=${API_VERSION}")

    # filter offline agents, delete them firstly to avoid conflict with newly created instances later
    if [ "$(echo "$AGENT_INFO" | jq -r '.status')" = "offline" ]; then
        # get compuster name of the agent
        COMPUTER_NAME=$(echo "$AGENT_INFO" | jq -r '.systemCapabilities."Agent.ComputerName"')
        echo "Deleting offline agent $AGENT_ID, computer name: $COMPUTER_NAME"
        # delete agent from devops pool
        curl -s -X DELETE -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents/${AGENT_ID}?api-version=${API_VERSION}"

        # delete azure vm instance
        VM_INSTANCE_ID=$(getInstanceID "$RG_NAME" "$VMSS_NAME" "$COMPUTER_NAME")

        if [ -n "$VM_INSTANCE_ID" ]; then
            echo "Deleting VM instance in Azure, computer name: $COMPUTER_NAME, instance id: $VM_INSTANCE_ID"
            az vmss delete-instances --resource-group $RG_NAME --name $VMSS_NAME --instance-ids $VM_INSTANCE_ID
        else
            echo "VM instance not found for agent $AGENT_ID (computer name: $COMPUTER_NAME, instance id: $VM_INSTANCE_ID), skipping"
        fi

    # filter the agents whose status is online and has been created more than 5 days
    elif [ "$(echo "$AGENT_INFO" | jq -r '.status')" = "online" ] && [ "$(echo "$AGENT_INFO" | jq -r '.createdOn | sub("\\..*"; "Z") | fromdateiso8601')" -lt "$(date -d "5 days ago" +%s)" ]; then

        if jq -e '.assignedRequest | not' <<< "$AGENT_INFO" > /dev/null; then
            echo "Agent $AGENT_ID is older than 5 days, currently online and idle, can be removed"
            # delete agent from devops pool
            echo "Deleting agent $AGENT_ID from pool $POOL_ID"
            curl -s -X DELETE -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents/${AGENT_ID}?api-version=${API_VERSION}"

            # Get its computer name
            COMPUTER_NAME=$(echo "$AGENT_INFO" | jq -r '.systemCapabilities."Agent.ComputerName"')
            # delete azure vm instance
            VM_INSTANCE_ID=$(getInstanceID "$RG_NAME" "$VMSS_NAME" "$COMPUTER_NAME")

            if [ -n "$VM_INSTANCE_ID" ]; then
                echo "Deleting VM instance in Azure, computer name: $COMPUTER_NAME, instance id: $VM_INSTANCE_ID"
                az vmss delete-instances --resource-group $RG_NAME --name $VMSS_NAME --instance-ids $VM_INSTANCE_ID
            else
                echo "VM instance not found for agent $AGENT_ID (computer name: $COMPUTER_NAME, instance id: $VM_INSTANCE_ID)"
            fi

        else
            # the online agent is currently running a job, skip it.
            echo "Agent $AGENT_ID is idle but has been assigned a request, keep it"
        fi

    else
        # the agent younger than 5 days, skip it.
        echo "Agent $AGENT_ID is created less than 5 days, keep it"
    fi
done

# Get the number of remaining agents in the pool
AGENT_COUNTS=$(curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents?api-version=${API_VERSION}" | jq -r '.count')
echo "There are $AGENT_COUNTS agents remaining in pool $POOL_NAME"

# If current number of agents is less than expected, scale out the VMSS to the expected number
if [ $AGENT_COUNTS -lt ${EXPECTED_COUNT} ]; then
    echo "Scaling out VMSS $VMSS_NAME to ${EXPECTED_COUNT} instances"
    az vmss scale --resource-group $RG_NAME --name $VMSS_NAME --new-capacity ${EXPECTED_COUNT}
fi
~~~

> - 需要检测offline的agent同时，也检测对应VM instance也删掉
> - 遇到被disable的agent，即使是offline的也删不掉。后面可以测试一下disabled的agent怎么

# Azure VMSS Cli

## scale

~~~sh
az vmss scale \
    --resource-group myResourceGroup \
    --name myScaleSet \
    --new-capacity 5
~~~

注意：有个问题就是如果定期用azcli直接scale VMSS，那么无法识别这个VMSS是否有CICD任务在运行，容易误伤。还是需要想办法通过azure devops RESI API来检测agent是否是idle。

## extension

https://docs.azure.cn/zh-cn/virtual-machines/extensions/custom-script-linux

https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-linux

## 替换image

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/scale-set-agents?view=azure-devops#update-an-existing-scale-set-with-a-new-custom-image

# helm chart部署

~~~sh
# 部署到dev环境
kubectl config use-context aks-commoninfra-dev-chinanorth3
cd ~/Cloud/devops-management/devops-agent-management
helm upgrade -i devops-agent-management -n devops-agent-management --create-namespace . -f ./values.yaml
~~~

## 测试pod里运行az devops

- 用预装了azcli的pod，导入到ACR
  - 截止2025/04/09，最新版本2.71.0：https://learn.microsoft.com/zh-cn/cli/azure/release-notes-azure-cli#april-01-2025

```sh
az acr import --name <ACR> --source mcr.microsoft.com/azure-cli:2.71.0-cbl-mariner2.0
```

- 创建测试pod，exec进去看看能不能登录azure devops

  ~~~yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-test-azcli
    namespace: devops-agent-management
  spec:
    containers:
      - name: standby
        image: mcr.microsoft.com/azure-cli:2.71.0-cbl-mariner2.0
        command: ["/bin/sh"]
        args: ["-c", "while true; do echo hello; sleep 10;done"]
        volumeMounts:
        - name: azure-devops-pat
          mountPath: /etc/secret-vol
          readOnly: true
        resources:
          requests:
            cpu: 500m
            memory: 200Mi
          limits:
            cpu: 800m
            memory: 500Mi
    volumes:
    - name: azure-devops-pat
      secret:
        secretName: azure-devops-pat
  ~~~

  ~~~sh
  #测试登录
  base64 -d /etc/secret-vol/token > pat.txt
  cat pat.txt | az devops login --organization <ORG>
  
  # 或者在容器内执行
  kubectl exec -n devops-agent-management pod-test-azcli -- bash -c "base64 -d /etc/secret-vol/token > pat.txt"
  ~~~

  > az devops extension装不上： network issue
  >
  
- 预先build一个带有az devops extension的镜像：

  ~~~dockerfile
  FROM mcr.microsoft.com/azure-cli:2.71.0-cbl-mariner2.0
  
  RUN az extension add --upgrade --name azure-devops --yes \
      && az --version
  ~~~

  进pod里面登录az devops，报错：

  ~~~sh
  cli.azext_devops.dev.common.credential_store: Failed to store PAT using keyring; falling back to file storage.
  ~~~

  这个报错看起来是az devops cli的bug，还没修复：

  https://github.com/Azure/azure-cli/issues/26731

  > 到此基本判断pod中运行az devops cli不可行。还是需要用REST API实现

## 测试pod中请求REST API

### 测试pod

~~~yaml
---
apiVersion: v1
kind: Pod
metadata:
  name: pod-test-alpine
  namespace: devops-agent-management
spec:
  containers:
    - name: test-container
      image: docker.io/library/alpine:3.21.3
      command: ["/bin/sh"]
      args: ["-c", "while true; do echo hello; sleep 10;done"]
      volumeMounts:
      - name: azure-devops-pat
        mountPath: /etc/secret-vol
        readOnly: true
      resources:
        requests:
          cpu: 100m
          memory: 200Mi
        limits:
          cpu: 200m
          memory: 400Mi
  volumes:
  - name: azure-devops-pat
    secret:
      secretName: azure-devops-pat
~~~

alpine镜像默认不带curl，可以进容器安装一下：

~~~sh
apk add --no-cache curl
~~~

测试成功，可以获取到json格式agent信息。

~~~sh
ORG_URL="https://dev.azure.com/xxxx"
PAT_TOKEN=$(cat /etc/secret-vol/token)
PAT_TOKEN_B64=$(printf "%s"":$PAT_TOKEN" | base64 -w0)
POOL_ID="56"
API_VERSION="7.1"

curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents?api-version=${API_VERSION}"

AGENT_ID=77399
curl -s -H "Authorization: Basic $PAT_TOKEN_B64" "${ORG_URL}/_apis/distributedtask/pools/${POOL_ID}/agents/${AGENT_ID}?includeAssignedRequest=true&includeCapabilities=true&api-version=${API_VERSION}"
~~~

> 注意：如果一个agent处于idle状态，REST API返回值中不存在“assignedRequest”字段。如果有任务在运行，那么会返回“assignedRequest”字段及其详细信息。

## pod中登录azcli-sp

参考： https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli-service-principal

- client位于AKS中，VMSS位于另一个tenant中。看起来managed identity用不了，试试用VMSS的tenant中的sp，在AKS中用sp登录

  ~~~yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-test-azcli
    namespace: devops-agent-management
  spec:
    containers:
      - name: standby
        image: mcr.microsoft.com/azure-cli:2.71.0-cbl-mariner2.0
        command: ["/bin/sh"]
        args: ["-c", "while true; do echo hello; sleep 10;done"]
        resources:
          requests:
            cpu: 500m
            memory: 200Mi
          limits:
            cpu: 800m
            memory: 500Mi
  ~~~

  ~~~sh
  az cloud set --name AzureChinaCloud
  
  TENANT_ID="xxx"
  CLIENT_ID="xxx"
  CLIENT_SECRET="xxx"
  
  echo "Logging in with service principal"
  az login --service-principal --username $CLIENT_ID --tenant $TENANT_ID --password $CLIENT_SECRET
  ~~~

  登录是成功的

## pod登录azcli-workload identity

参考：https://learn.microsoft.com/zh-cn/entra/workload-id/workload-identity-federation-config-app-trust-managed-identity?tabs=microsoft-entra-admin-center

- 在ns中创建service account

  ~~~yaml
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    annotations:
      azure.workload.identity/client-id: "xxx"
      azure.workload.identity/tenant-id: "xxx"
    labels:
      azure.workload.identity/use: "true"
    name: "sa-devops-agent-management"
    namespace: "devops-agent-management"
  ~~~

- 获取clusterIssuer

  ~~~sh
  AKS_RG_NAME="myResourceGroup"
  CLUSTER_NAME="myCluster"
  az aks show -g $AKS_RG_NAME -n $CLUSTER_NAME --query "oidcIssuerProfile.issuerUrl" -otsv
  ~~~

- 前往sp的federated secrets界面，基于已经创建的sa、AKS的OIDC issuer URL，创建一个新的federated credential

  ==注意在Audience字段中不能带China，要改成 api://AzureADTokenExchange。否则在后面pod中登录的时候会报错：AADSTS700212: No matching federated identity record found for presented assertion audience 'api://AzureADTokenExchange'.==

- 创建pod挂载workload identity和sa

  ~~~yaml
  apiVersion: v1
  kind: Pod
  metadata:
    name: pod-test-azcli
    namespace: devops-agent-management
    labels:
      azure.workload.identity/use: true	
  spec:
    serviceAccountName: sa-devops-agent-management
    containers:
      - name: standby
        image: mcr.microsoft.com/azure-cli:2.71.0-cbl-mariner2.0
        command: ["/bin/sh"]
        args: ["-c", "while true; do echo hello; sleep 10;done"]
        resources:
          requests:
            cpu: 500m
            memory: 200Mi
          limits:
            cpu: 800m
            memory: 500Mi
  ~~~

- describe pod检查这几个环境变量：

  ~~~sh
  AZURE_CLIENT_ID:             
  AZURE_TENANT_ID:             
  AZURE_FEDERATED_TOKEN_FILE:  /var/run/secrets/azure/tokens/azure-identity-token
  AZURE_AUTHORITY_HOST:        https://login.chinacloudapi.cn/
  
  cat /var/run/secrets/azure/tokens/azure-identity-token
  ~~~

- 利用workload identity登录

  ~~~sh
  az cloud set --name AzureChinaCloud && az login --service-principal --username "${AZURE_CLIENT_ID}" --tenant "${AZURE_TENANT_ID}" --federated-token "$(cat $AZURE_FEDERATED_TOKEN_FILE)"
  ~~~

- 尝试scale VMSS -- 成功

  ~~~sh
  rgname=""
  vmssname=""
  az vmss scale --resource-group $rgname --name $vmssname --new-capacity 4
  ~~~

  

