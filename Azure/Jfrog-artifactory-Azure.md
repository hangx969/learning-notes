---
title: JFrog Artifactory on Azure
tags:
  - azure/container
  - azure/jfrog
  - azure/artifactory
  - azure/aks
aliases:
  - JFrog Artifactory
  - Artifactory AKS
  - Artifactory Deployment
date: 2026-04-16
---

# JFrog Artifactory on Azure

## 相关笔记

- [[Azure/2_AKS-basics]]
- [[Azure/7_ACR-ACI]]
- [[Azure/5_Azure-Storage]]

---

## 1. Artifactory 与目录结构

本文记录在 Azure 上部署 Artifactory 的多种实验路径。ACI、AKS 手工部署与 Rancher 导入 AKS 的尝试均遇到问题；各节保留当时的配置、命令和实际结果，便于复盘。

[JFrog 安装与配置文档](https://jfrog.com/help/r/jfrog-installation-setup-documentation/installation-configuration)给出了 `JFROG_HOME` 的目录布局：

- `app/`：程序、依赖库和脚本等运行文件，通常不需要持久化。
- `var/`：配置、数据、日志等运行时内容，包含用户数据，需要持久化。

```sh
JFROG_HOME
  └── <product>
     ├── app
     │   ├── bin
     │   ├── run
     │   ├── doc
     │   ├── <third-party>
     │   │   ├── java
     │   │   ├── yq
     │   │   └── others
     │   └── <service>
     │   │   ├── bin
     │   │   └── lib
     │   └── misc
     │
     └── var
        ├── backup
        │   └── <service>
        ├── bootstrap
        │   └── <service>
        ├── data
        │   └── <service>
        ├── etc
        │   ├── system.yaml
        │   ├── <service>
        │   └── security
        │       ├── master.key
        │       └── join.key
        ├── log
        │   └── <service logs>
        │   └── archived
        │       └── <archived service logs>
        └── work
            └── <service>
```

---

## 2. 在 ACI 上部署 Artifactory

### 2.1 准备 VNet 与子网

创建地址空间为 `10.225.130.0/24` 的 VNet，并划分两个子网：

- `subnet-aci`：`10.225.130.64/26`
- `subnet-artifactory`：`10.225.130.0/26`

### 2.2 准备镜像

创建 ACR `acrcdstest`，然后将 JFrog 镜像推送到 Azure 中国区 ACR：

```sh
az cloud set --name AzureChinaCloud 
az login -t <tenant-id>
az acr list
az acr login --name acrcdstest
docker pull releases-docker.jfrog.io/jfrog/artifactory-oss:latest
#pulled 7.90.9
docker tag releases-docker.jfrog.io/jfrog/artifactory-oss:latest acrcdstest.azurecr.cn/artifactory:latest
docker push acrcdstest.azurecr.cn/artifactory:latest
```

### 2.3 准备 Azure Files 和配置

参考 [ACI 挂载 Azure Files 文档](https://docs.azure.cn/zh-cn/container-instances/container-instances-volume-azure-files#deploy-container-and-mount-volume---yaml)，创建存储账户和文件共享：

```sh
# Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=rg-artifactory-demo
ACI_PERS_STORAGE_ACCOUNT_NAME=artisa
ACI_PERS_LOCATION=chinanorth3
ACI_PERS_SHARE_NAME=artishare

# Create the storage account with the parameters
az storage account create --resource-group $ACI_PERS_RESOURCE_GROUP --name $ACI_PERS_STORAGE_ACCOUNT_NAME --location $ACI_PERS_LOCATION --sku Standard_LRS
#az storage account create --resource-group rg-artifactory-cds-test --name artifactorysatest --location chinanorth3 --sku Standard_LRS

# Create the file share
az storage share create --name $ACI_PERS_SHARE_NAME --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME
#az storage share create --name artisharetest --account-name artifactorysatest

# Get credentials
STORAGE_KEY=$(az storage account keys list --resource-group $ACI_PERS_RESOURCE_GROUP --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME --query "[0].value" --output tsv)
#STORAGE_KEY=$(az storage account keys list --resource-group rg-artifactory-cds-test --account-name artifactorysatest --query "[0].value" --output tsv)
echo $STORAGE_KEY
```

在文件共享中创建 `etc/`，在本地编写 `system.yaml` 并上传到该目录。JDBC URL 可从 Azure 门户的 PostgreSQL「连接 → 从应用连接 → JDBC」获取。

```yaml
shared:
  database:
    driver: org.postgresql.Driver
    type: postgresql
    url: jdbc:postgresql://pg-artifactory.postgres.database.chinacloudapi.cn:5432/postgres?user=artifactory&password=Passw0rd&sslmode=require
    username: artifactory
    password: Passw0rd
```

### 2.4 准备 PostgreSQL

在 VNet 中创建 PostgreSQL 实例。原实验记录中的管理员密码为 `Passw0rd`；下方配置中的数据库连接信息需与实际实例一致。

### 2.5 创建 ACI 容器组

> [!tip] Best Practices
> - 容器组 IP 地址在创建或删除后可能会发生更改。 建议不要让应用程序代码依赖于容器组的 IP 地址。 如果想维护静态 IP 地址，还建议使用 [NAT 网关](https://docs.azure.cn/zh-cn/container-instances/container-instances-nat-gateway)或[应用程序网关](https://docs.azure.cn/zh-cn/container-instances/container-instances-application-gateway)。
> - ACI 服务保留以下服务功能端口：==22、1025-1027、3389-3399、9999、19000、19080、19390、19100、20000-30000、49152-65534==。 请避免在容器组定义中使用这些端口。
> - 可在 Azure 容器实例上部署的容器映像的最大大小为 ==15 GB==。根据部署时的确切可用性，你也许可以部署更大的映像，但不能保证映像大小更大。

```sh
az container create \
    --resource-group $ACI_PERS_RESOURCE_GROUP \
    --name artifactory \
    --location chinanorth3 \
    --image acrcdstest.azurecr.cn/artifactory:latest \
    --registry-login-server acrcdstest.azurecr.cn \
    --registry-username acrcdstest \
    --registry-password <password> \
    --subnet <snet-id> \
    --ports 8081 8082 \
    --cpu 2 \
    --memory 4 \
    --azure-file-volume-account-name $ACI_PERS_STORAGE_ACCOUNT_NAME \
    --azure-file-volume-account-key $STORAGE_KEY \
    --azure-file-volume-share-name $ACI_PERS_SHARE_NAME \
    --azure-file-volume-mount-path /var/opt/jfrog/artifactory 
```

通过 `http://<container-ip>:8082/ui/` 访问界面。初始账户为 `admin` / `password`，首次登录后修改密码。

> [!warning]
> 本次 ACI 实验中，Artifactory 出现多种启动错误，容器未能正常运行，因此停止该方案。

---

## 3. 在 Azure VM 上使用 Docker 部署

[JFrog Docker 单节点安装文档](https://jfrog.com/help/r/jfrog-installation-setup-documentation/install-artifactory-single-node-with-docker)

实验环境：Ubuntu 22.04、Docker 27.2.1。资源需求参考 [JFrog 安装要求](https://jfrog.com/help/r/jfrog-installation-setup-documentation/install-artifactory-single-node-with-helm-charts?section=UUID-5a5bc1a4-b867-9be2-2902-04b3ce759902_UUID-6560a094-94c2-ca03-359f-ccb55be0e480)。

1. 创建 Azure Database for PostgreSQL Flexible Server。
2. 创建 32 GiB 数据盘，格式化为 ext4，挂载到 `/app/jfrog`，并配置 `/etc/fstab` 使其在重启后自动挂载。
3. 准备 Artifactory 数据目录：

```sh
mkdir -p /app/jfrog
export JFROG_HOME=/app/jfrog
mkdir -p $JFROG_HOME/artifactory/var/etc/
cd $JFROG_HOME/artifactory/var/etc/
touch ./system.yaml
chown -R 1030:1030 $JFROG_HOME/artifactory/var
```

4. 在 `system.yaml` 中配置 PostgreSQL 连接：

```sh
tee $JFROG_HOME/artifactory/var/etc/system.yaml <<'EOF'
shared:
    database:
        driver: org.postgresql.Driver
        type: postgresql
        url: jdbc:postgresql://artipgsql.postgres.database.chinacloudapi.cn:5432/artifactory?user=artifactory&password=Passw0rd&sslmode=require
        username: <username>
        password: <password>
EOF
```

5. 启动容器：

```sh
docker run --name artifactory -v $JFROG_HOME/artifactory/var/:/var/opt/jfrog/artifactory -d -p 8081:8081 -p 80:8082 acrcdstest.azurecr.cn/artifactory:latest 
```

6. 访问 `http://<VM-IP>/ui/`。默认账户为 `admin` / `password`；若已修改密码，请使用修改后的密码。

---

## 4. 在 AKS 上手工部署 Artifactory

### 4.1 准备集群、数据库与命名空间

- 创建私有 AKS 集群。
- 使用外部 PostgreSQL：实例名 `artipgsql`，数据库名 `artifactory-aks`。
- 创建命名空间：

```sh
kubectl create namespace artifactory
```

### 4.2 准备 Azure Files

创建 Azure 文件共享作为数据目录，参考 [AKS Azure Files CSI 文档](https://docs.azure.cn/zh-cn/aks/azure-csi-files-storage-provision#using-azure-tags)。

```sh
# Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=rg-artifactory-demo
ACI_PERS_STORAGE_ACCOUNT_NAME=artifactorysa
ACI_PERS_LOCATION=chinanorth3
ACI_PERS_SHARE_NAME=artishare

# Create the storage account with the parameters
az storage account create --resource-group $ACI_PERS_RESOURCE_GROUP --name $ACI_PERS_STORAGE_ACCOUNT_NAME --location $ACI_PERS_LOCATION --sku Standard_LRS
#az storage account create --resource-group rg-artifactory-cds-test --name artifactorysatest --location chinanorth3 --sku Standard_LRS

# Create the file share
az storage share create --name $ACI_PERS_SHARE_NAME --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME
#az storage share create --name artisharetest --account-name artifactorysatest

# Get credentials
STORAGE_KEY=$(az storage account keys list --resource-group $ACI_PERS_RESOURCE_GROUP --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME --query "[0].value" --output tsv)
#STORAGE_KEY=$(az storage account keys list --resource-group rg-artifactory-cds-test --account-name artifactorysatest --query "[0].value" --output tsv)
echo $STORAGE_KEY

# Create secret
kubectl create secret generic azurefile-secret --namespace artifactory --from-literal=azurestorageaccountname=$ACI_PERS_STORAGE_ACCOUNT_NAME --from-literal=azurestorageaccountkey=$STORAGE_KEY
```

```sh
tee azurefile-pv-pvc.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-azurefile-artishare
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: azurefile-csi
  csi:
    driver: file.csi.azure.com
    volumeHandle: "rg-artifactory-demo#artifactorysa#artishare"  # make sure this volumeid is unique for every identical share in the cluster
    volumeAttributes:
      resourceGroup: rg-artifactory-demo  # optional, only set this when storage account is not in the same resource group as node
      storageAccount: artifactorysa
      shareName: artishare
      server: artifactorysa.privatelink.file.core.chinacloudapi.cn
    nodeStageSecretRef:
      name: azurefile-secret
      namespace: artifactory
  mountOptions:
    - dir_mode=0777
    - file_mode=0777
    - uid=1030 # set for artifactory user
    - gid=1030
    - mfsymlinks
    - cache=strict
    - nosharesock
    - nobrl  # disable sending byte range lock requests to the server and for applications which have challenges with posix locks

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-azurefile-artishare
  namespace: artifactory
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: azurefile-csi
  volumeName: pv-azurefile-artishare #pv name
  resources:
    requests:
      storage: 10Gi
      
EOF
```

### 4.3 配置 Artifactory

编写 `system.yaml`，准备上传到文件共享：

```sh
tee system.yaml <<'EOF'
shared:
    database:
        driver: org.postgresql.Driver
        type: postgresql
        url: <pgsql-connection-url>
        username: <username>
        password: <password>
EOF
```

从已挂载文件共享的 VM 将 `system.yaml` 复制到共享目录：

```sh
mkdir /mnt/artishare/etc/security/ -p
cp ./system.yaml /mnt/artishare/etc/
#尝试提前写入两个key
mkdir /mnt/artishare/etc/security -p
openssl rand -hex 32 > /mnt/artishare/etc/security/master.key
openssl rand -hex 32 > /mnt/artishare/etc/security/join.key
```

### 4.4 创建 Deployment

```sh
tee deploy-artifactory.yaml <<'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deploy-artifactory-demo
  namespace: artifactory
spec:
  replicas: 1
  selector:
    matchLabels:
      app: artifactory
  template:
    metadata:
      labels:
        app: artifactory
    spec:
      containers:
      - name: artifactory
        image: acrcdstest.azurecr.cn/artifactory:latest
        imagePullPolicy: IfNotPresent
        env:
        - name: http_proxy
          value: ""
        - name: HTTP_PROXY
          value: ""
        - name: https_proxy
          value: ""
        - name: HTTPS_PROXY
          value: ""
        ports:
        - containerPort: 8081
        - containerPort: 8082
        volumeMounts:
        - name: fileshare-artifactory
          mountPath: /var/opt/jfrog/artifactory
          readOnly: false
        #- name: cm-system
          #mountPath: /var/opt/jfrog/artifactory/etc/
          #readOnly: false
      volumes:
      - name: fileshare-artifactory
        persistentVolumeClaim:
          claimName: pvc-azurefile-artishare
      #- name: cm-system 
        #configMap:
          #name: artifactory-config
EOF
```

> [!warning]
> 本次实验持续出现以下错误，即使将 key 文件放到指定位置仍未解决，因此停止该方案：
> - `Caught exception in GET /artifactory/api/system/ping`
> - `Missing required services: [jffe]`

---

## 5. 在 AKS 上通过 Helm 部署 Artifactory OSS

### 5.1 添加 Helm 仓库

```sh
helm repo add jfrog https://charts.jfrog.io
helm repo update
```

### 5.2 创建并保存密钥

创建 master key Secret：

```sh
# Create a key
export MASTER_KEY=$(openssl rand -hex 32)
echo ${MASTER_KEY}
 
# Create a secret containing the key. The key in the secret must be named master-key
kubectl create secret generic masterkey-secret -n artifactory --from-literal=master-key=${MASTER_KEY}
```

> [!important] 密钥一致性
> 安装和后续升级必须使用同一组 master key 与 join key。当前 [JFrog Helm 文档](https://docs.jfrog.com/installation/docs/manage-keys)建议通过 `global.masterKeySecretName` 和 `global.joinKeySecretName` 引用 Secret。下方 `artifactory.*` 参数是原实验使用的 chart 配置，运行前应核对所用版本。

创建 join key Secret：

```sh
# Create a key
export JOIN_KEY=$(openssl rand -hex 32)
echo ${JOIN_KEY}
 
# Create a secret containing the key. The key in the secret must be named join-key
kubectl create secret generic joinkey-secret -n artifactory --from-literal=join-key=${JOIN_KEY}
```

### 5.3 配置外部 PostgreSQL

参考 [JFrog PostgreSQL 配置文档](https://jfrog.com/help/r/jfrog-installation-setup-documentation/configure-artifactory-to-use-postgresql-single-node)。原实验直接修改 `artifactory-oss/charts/artifactory/values.yaml` 中约第 1645 行；具体行号依 chart 版本变化。

### 5.4 安装与实验命令

以下是原实验使用的不同安装方式。命令中的镜像地址和 chart values 路径需要与实际 chart 版本核对；标有「无效」的命令保留为排错记录。

```sh
#这个命令无效
helm upgrade --install artifactory --set artifactory.masterKeySecretName=masterkey-secret --set artifactory.joinKeySecretName=joinkey-secret --namespace artifactory --create-namespace jfrog/artifactory

#这个命令没有用到自定义的image
helm install artifactory-oss \
  --set artifactory.masterKeySecretName=masterkey-secret \
  --set artifactory.joinKeySecretName=joinkey-secret \
  --set artifactory.nginx.enabled=false \
  --set artifactory.postgresql.enabled=false \
  --set postgresql.enabled=false \
  --set artifactory.artifactory.service.type=NodePort \
  --set artifactory.artifactory.resources.requests.cpu="500m" \
  --set artifactory.artifactory.resources.limits.cpu="2" \
  --set artifactory.artifactory.resources.requests.memory="1Gi" \
  --set artifactory.artifactory.resources.limits.memory="4Gi" \
  --set artifactory.artifactory.image.registry=acrcdstest.azurecr.cn \
  --set artifactory.artifactory.image.repository=artifactory \
  --set artifactory.artifactory.image.tag=latest \
  jfrog/artifactory-oss -n artifactory

# 手动传入key、指定valus.yaml
export MASTER_KEY=$(openssl rand -hex 32)
export JOIN_KEY=$(openssl rand -hex 32)
helm install artifactory-oss \
  --set artifactory.masterKey=${MASTER_KEY} \
  --set artifactory.joinKey=${JOIN_KEY} \
  --set artifactory.nginx.enabled=false \
  --set artifactory.postgresql.enabled=false \
  --set postgresql.enabled=false \
  --set artifactory.artifactory.service.type=NodePort \
  --set artifactory.artifactory.resources.requests.cpu="500m" \
  --set artifactory.artifactory.resources.limits.cpu="2" \
  --set artifactory.artifactory.resources.requests.memory="1Gi" \
  --set artifactory.artifactory.resources.limits.memory="4Gi" \
  --set artifactory.artifactory.image.registry=acrcdstest.azurecr.cn \
  --set artifactory.artifactory.image.repository=artifactory \
  --set artifactory.artifactory.image.tag=latest \
  jfrog/artifactory-oss -n artifactory -f values.yaml

#dryrun
helm install artifactory-oss \
--set artifactory.masterKey=${MASTER_KEY} \
--set artifactory.joinKey=${JOIN_KEY} \
--set artifactory.nginx.enabled=false \
--set artifactory.postgresql.enabled=false \
--set postgresql.enabled=false \
--set artifactory.artifactory.service.type=NodePort \
--set artifactory.artifactory.resources.requests.cpu="500m" \
--set artifactory.artifactory.resources.limits.cpu="2" \
--set artifactory.artifactory.resources.requests.memory="1Gi" \
--set artifactory.artifactory.resources.limits.memory="4Gi" \
--set artifactory.artifactory.image.registry=acrcdstest.azurecr.cn \
--set artifactory.artifactory.image.repository=artifactory \
--set artifactory.artifactory.image.tag=latest \
--set router.image.registry=acrcdstest.azurecr.cn \
--set router.image.repository=router \
--set router.image.tag=7.118.2 \
--set initContainers.image.registry=acrcdstest.azurecr.cn \
--set initContainers.image.repository=ubi-minimal \
--set initContainers.image.tag=9.4.949.1716471857 \
jfrog/artifactory-oss -n artifactory -f values.yaml --dry-run --debug > result.txt
```

#### 实验结果

原实验中，init container 的镜像始终未能改为 ACR 中的镜像。

### 5.5 卸载

先按 release 名称卸载：

```sh
helm uninstall artifactory-oss -n artifactory
```

如确认要删除持久卷声明，再单独执行（会影响数据）：

```sh
kubectl delete pvc -n artifactory -l app=artifactory
```

如使用了其他 release 名称，先通过 `helm list -n artifactory` 确认后再卸载。

> [!warning]
> 删除 PVC 或其底层数据卷前应先备份数据。`helm uninstall` 的参数是 release 名称，不能使用 `jfrog/artifactory-oss` 这样的 chart 名称。

---

## 6. 在 AKS 上通过 Helm 部署 Artifactory CPP CE

### 6.1 准备配置

1. 创建外部 Azure PostgreSQL。
2. 在 Helm values 中将镜像地址改为 ACR。
3. 在 `system.yaml` 的 `database` 字段中配置外部 PostgreSQL；参数位置需检查对应版本的 `values.yaml`。
4. 在相关 values 中关闭 Nginx 和内置 PostgreSQL。

### 6.2 安装 release

```sh
#key用手动生成的
export MASTER_KEY=$(openssl rand -hex 32)
export JOIN_KEY=$(openssl rand -hex 32)
helm install artifactory-cpp-ce  ./ \
--set artifactory.masterKey=${MASTER_KEY} \
--set artifactory.joinKey=${JOIN_KEY} \
--set artifactory.nginx.enabled=false \
--set artifactory.postgresql.enabled=false \
--set postgresql.enabled=false \
--set artifactory.artifactory.service.type=NodePort \
--set artifactory.artifactory.resources.requests.cpu="500m" \
--set artifactory.artifactory.resources.limits.cpu="2" \
--set artifactory.artifactory.resources.requests.memory="1Gi" \
--set artifactory.artifactory.resources.limits.memory="4Gi" \
-n artifactory -f values.yaml #--dry-run --debug > result.txt

#key用secret
export MASTER_KEY=$(openssl rand -hex 32)
echo ${MASTER_KEY}
kubectl create secret generic masterkey-secret -n artifactory --from-literal=master-key=${MASTER_KEY}

export JOIN_KEY=$(openssl rand -hex 32)
echo ${JOIN_KEY}
kubectl create secret generic joinkey-secret -n artifactory --from-literal=join-key=${JOIN_KEY}

helm install artifactory-cpp-ce  ./ \
--set artifactory.nginx.enabled=false \
--set artifactory.postgresql.enabled=false \
--set postgresql.enabled=false \
--set artifactory.artifactory.service.type=NodePort \
--set artifactory.artifactory.resources.requests.cpu="500m" \
--set artifactory.artifactory.resources.limits.cpu="2" \
--set artifactory.artifactory.resources.requests.memory="1Gi" \
--set artifactory.artifactory.resources.limits.memory="4Gi" \
-n artifactory -f values.yaml
```

### 6.3 配置内部 Load Balancer

内部 Load Balancer Service 的 selector 取自 Helm 创建的 Pod 标签；升级后若 Pod 标签变化，也要同步更新 selector。参考 [AKS 内部负载均衡器文档](https://docs.azure.cn/zh-cn/aks/internal-lb?tabs=set-service-annotations)。

```sh
tee iLB.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: ilb-artifactory-cpp-demo
  namespace: artifactory
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-ipv4: <internal-ip> # fixed internal IP
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8082
  selector:
    app: artifactory
    component: artifactory
    release: artifactory-cpp-ce
EOF
```

### 6.4 管理 release

查看 release：

```sh
helm list -n artifactory
```

升级 release：

> [!important]
> 下方是原实验命令。实际升级时要继续传入安装时使用的 `values.yaml`，并沿用相同的 master key 与 join key（或原有 Secret），否则可能改变现有密钥配置。具体参数以所用 chart 版本为准。

```sh
#cd到helm项目目录
helm upgrade artifactory-cpp-ce -n artifactory .
```

卸载 release：

```sh
helm uninstall artifactory-cpp-ce -n artifactory
```

---

## 7. 通过 Rancher 管理 AKS 的实验

### 7.1 启动 Rancher

单独创建一台 VM，在其中运行 Rancher 容器。

> [!note] 历史环境记录
> 原实验在 Ubuntu 22.04 上遇到容器内 K3s 无法正常启动的问题，相关报告见 [Rancher issue #36238](https://github.com/rancher/rancher/issues/36238)。该 issue 针对旧版 Rancher，不应据此推断所有当前版本都存在同样问题。

```sh
# 原实验在 Ubuntu 20.04 上可启动该 Rancher 镜像
docker run -d --restart=unless-stopped -p 80:80 -p 443:443 --privileged acrcdstest.azurecr.cn/rancher:latest
#按照提示获取登录密码
```

### 7.2 创建 Azure 服务主体

在 Azure 中创建服务主体：

```sh
az ad sp create-for-rbac --scope <rg-resource-id> --role Contributor
```

> [!warning]
> 原实验中，Rancher 导入 AKS 集群时将区域识别为 China East，导致无法获取 API version。未找到可修改该配置的位置，因此停止该方案。
