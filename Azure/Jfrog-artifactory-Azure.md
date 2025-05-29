# Jfrog Artifactory

- 官网：https://jfrog.com/help/r/jfrog-installation-setup-documentation/installation-configuration

- 目录结构
  - app是程序目录，包含Artifactory应用程序的二进制文件和配置文件。它通常包括软件本身、所需的库（libraries）、脚本以及其他与应用程序运行相关的文件，一般不需要持久化
  - var是数据目录，这个目录包含了所有的用户数据，需要持久化

~~~sh
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
        │       └──master.key
        │       └──join.key
        ├── log
        │   └── <service logs>
        │   └── archived
        │       └── <archived service logs>
        └── work
            └── <service>
~~~

# Artifactory部署到ACI

## Prepare Vnet

- Create Vnet with address range 10.225.130.0/24, create 2 subnets
  - subnet-aci: 10.225.130.64/26
  - subnet-artifactory: 10.225.130.0/26

## Prepare Image

- create ACR：acrcdstest

~~~sh
az cloud set --name AzureChinaCloud 
az login -t 8f56d2b8-03ec-4557-b25b-da031f0b234c
az acr list
az acr login --n acrcdstest
docker pull releases-docker.jfrog.io/jfrog/artifactory-oss:latest
#pulled 7.90.9
docker tag releases-docker.jfrog.io/jfrog/artifactory-oss:latest acrcdstest.azurecr.cn/artifactory:latest
docker push acrcdstest.azurecr.cn/artifactory:latest
~~~

## Prepare Storage

- ACI mount azure file：https://docs.azure.cn/zh-cn/container-instances/container-instances-volume-azure-files#deploy-container-and-mount-volume---yaml

- Create sa and file share

~~~sh
# Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=rg-artifactory-cds-demo
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
~~~

- create a folder named “etc” in fileshare.
- create config file locally and upload to azure file share/etc
  - url can be obtained from azure portal - postgresql - connect - connect from your app - JDBC

~~~yaml
shared:
  database:
    driver: org.postgresql.Driver
    type: postgresql
    url: jdbc:postgresql://pg-artifactory.postgres.database.chinacloudapi.cn:5432/postgres?user=artifactory&password=Passw0rd&sslmode=require
    username: artifactory
    password: Passw0rd
~~~

## Prepare postgresql

- Create a postgresql in a VNET
- admin - Passw0rd

## ACI deployment

> Best Practices:
>
> - 容器组 IP 地址在创建或删除后可能会发生更改。 建议不要让应用程序代码依赖于容器组的 IP 地址。 如果想维护静态 IP 地址，还建议使用 [NAT 网关](https://docs.azure.cn/zh-cn/container-instances/container-instances-nat-gateway)或[应用程序网关](https://docs.azure.cn/zh-cn/container-instances/container-instances-application-gateway)。
> - ACI 服务保留以下服务功能端口：22、1025-1027、3389-3399、9999、19000、19080、19390、19100、20000-30000、49152-65534。 请避免在容器组定义中使用这些端口。
> - 可在 Azure 容器实例上部署的容器映像的最大大小为 15 GB。根据部署时的确切可用性，你也许可以部署更大的映像，但不能保证映像大小更大。

~~~sh
az container create \
    --resource-group $ACI_PERS_RESOURCE_GROUP \
    --name artifactory \
    --location chinanorth3 \
    --image acrcdstest.azurecr.cn/artifactory:latest \
    --registry-login-server acrcdstest.azurecr.cn \
    --registry-username acrcdstest \
    --registry-password FEUD1ehvgz1R2P1IkzULd7+z5Bhz/tIZzsB1s1GDbJ+ACRBP1dvE \
    --subnet /subscriptions/4eab3273-e0ec-4165-b6d7-b80ae903b0c7/resourceGroups/rg-artifactory-cds-demo/providers/Microsoft.Network/virtualNetworks/vnet-artifactory/subnets/subnet-aci \
    --ports 8081 8082\
    --cpu 2 \
    --memory 4 \
    --azure-file-volume-account-name $ACI_PERS_STORAGE_ACCOUNT_NAME \
    --azure-file-volume-account-key $STORAGE_KEY \
    --azure-file-volume-share-name $ACI_PERS_SHARE_NAME \
    --azure-file-volume-mount-path /var/opt/jfrog/artifactory 
~~~

- login UI using containerIP:8082/ui (default username: admin, passwd: password)
  - edit admin password after logged in

> ACI部署artifactory会出现各种各样的artifactory报错，导致容器起不来。遂放弃。

# Artifactory-docker部署到azure vm

https://jfrog.com/help/r/jfrog-installation-setup-documentation/install-artifactory-single-node-with-docker

- VM environment

  - Ubuntu 22.04

  - docker version: 27.2.1

- Artifactory requirement: 

  https://jfrog.com/help/r/jfrog-installation-setup-documentation/install-artifactory-single-node-with-helm-charts?section=UUID-5a5bc1a4-b867-9be2-2902-04b3ce759902_UUID-6560a094-94c2-ca03-359f-ccb55be0e480

- Create a postgresql flexible server

- set up data folder
  - create a data disk (32G), format to ext4 and mount it to /app/jfrog as data store path.
  - configure fstab

~~~sh
mkdir /app/jfrog
export JFROG_HOME=/app/jfrog
mkdir -p $JFROG_HOME/artifactory/var/etc/
cd $JFROG_HOME/artifactory/var/etc/
touch ./system.yaml
chown -R 1030:1030 $JFROG_HOME/artifactory/var
~~~

- setup pgsql connection

~~~yaml
tee $JFROG_HOME/artifactory/var/etc/system.yaml <<'EOF'
shared:
    database:
        driver: org.postgresql.Driver
        type: postgresql
        url: jdbc:postgresql://artipgsql.postgres.database.chinacloudapi.cn:5432/artifactory?user=artifactory&password=Passw0rd&sslmode=require
        username: artifactory
        password: Passw0rd
EOF
~~~

- run container

~~~sh
docker run --name artifactory -v $JFROG_HOME/artifactory/var/:/var/opt/jfrog/artifactory -d -p 8081:8081 -p 80:8082 acrcdstest.azurecr.cn/artifactory:latest 
~~~

- visit home page: http://10.225.126.36/ui/ with username admin/passwd Passw0rd

# Artifactory-deppoyment-部署到AKS

- Create private aks cluster

- use external pgsql:

  name: artipgsql

  database: artifactory-aks 

- ns

  ~~~sh
  k create ns artifactory
  ~~~

- Create an azure file share as data path, mount it to aks

  https://docs.azure.cn/zh-cn/aks/azure-csi-files-storage-provision#using-azure-tags

~~~sh
# Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=rg-artifactory-cds-demo
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
~~~

~~~yaml
tee azurefile-pv-pvc.yaml <<'EOF'
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-azurefile-artishare
  namespace: artifactory
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: azurefile-csi
  csi:
    driver: file.csi.azure.com
    volumeHandle: "rg-artifactory-cds-demo#artifactorysa#artishare"  # make sure this volumeid is unique for every identical share in the cluster
    volumeAttributes:
      resourceGroup: rg-artifactory-cds-demo  # optional, only set this when storage account is not in the same resource group as node
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
~~~

- config file upload to file share

~~~yaml
tee system.yaml <<'EOF'
shared:
    database:
        driver: org.postgresql.Driver
        type: postgresql
        url: jdbc:postgresql://artipgsql.postgres.database.chinacloudapi.cn:5432/artifactory-aks?user=artifactory&password=Passw0rd&sslmode=require
        username: artifactory
        password: Passw0rd
EOF
~~~

- copy system.yaml from VM which has mounted the file share

~~~sh
mkdir /mnt/artishare/etc/security/ -p
cp ./system.yaml /mnt/artishare/etc/
#尝试提前写入两个key
mkdir /mnt/artishare/etc/security -p
openssl rand -hex 32 > /mnt/artishare/etc/security/master.key
openssl rand -hex 32 > /mnt/artishare/etc/security/join.key
~~~

- pod

~~~yaml
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
~~~

> 总是报错：
>
> - Caught exception in GET /artifactory/api/system/ping
>
> - Missing required services: [jffe]
> - 即使把key文件放到指定位置了也识别不到，遂放弃。

# Artifactory-helm部署到AKS

- add helm repo

~~~sh
helm repo add jfrog https://charts.jfrog.io
helm repo update
~~~

- create master key as k8s secret

~~~sh
# Create a key
export MASTER_KEY=$(openssl rand -hex 32)
echo ${MASTER_KEY}
 
# Create a secret containing the key. The key in the secret must be named master-key
kubectl create secret generic masterkey-secret -n artifactory --from-literal=master-key=${MASTER_KEY}
~~~

> In either case, make sure to pass the same master key on all future calls to Helm install and Helm upgrade. This means always passing 
> --set artifactory.masterKey=${MASTER_KEY}
>  (for the custom master key) or 
> --set artifactory.masterKeySecretName=my-masterkey-secret
>  (for the manual secret) and verifying that the contents of the secret remain unchanged.

- create join key as k8s secret

~~~sh
# Create a key
export JOIN_KEY=$(openssl rand -hex 32)
echo ${JOIN_KEY}
 
# Create a secret containing the key. The key in the secret must be named join-key
kubectl create secret generic joinkey-secret -n artifactory --from-literal=join-key=${JOIN_KEY}
~~~

- configure pgsql in helm
  - https://jfrog.com/help/r/jfrog-installation-setup-documentation/configure-artifactory-to-use-postgresql-single-node
  - artifactory-oss/charts/artifactory/values.yaml的1645行修改
- install

~~~sh
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
helm install artifactory-oss   --set artifactory.masterKey=${MASTER_KEY}   --set artifactory.joinKey=${JOIN_KEY}   --set artifactory.nginx.enabled=false   --set artifactory.postgresql.enabled=false   --set postgresql.enabled=false   --set artifactory.artifactory.service.type=NodePort   --set artifactory.artifactory.resources.requests.cpu="500m"   --set artifactory.artifactory.resources.limits.cpu="2"   --set artifactory.artifactory.resources.requests.memory="1Gi"   --set artifactory.artifactory.resources.limits.memory="4Gi"   --set artifactory.artifactory.image.registry=acrcdstest.azurecr.cn   --set artifactory.artifactory.image.repository=artifactory   --set artifactory.artifactory.image.tag=latest --set router.image.registry=acrcdstest.azurecr.cn   --set router.image.repository=router   --set router.image.tag=7.118.2 --set initContainers.image.registry=acrcdstest.azurecr.cn   --set initContainers.image.repository=ubi-minimal   --set initContainers.image.tag=9.4.949.1716471857 jfrog/artifactory-oss -n artifactory -f values.yaml --dry-run --debug > result.txt

##！！！initcontainer的image始终没办法修改成ACR里面的。。。
~~~

- uninstall


~~~sh
helm uninstall jfrog/artifactory-oss && sleep 90 && kubectl delete pvc -l app=artifactory
~~~

- delete artifactory


Deleting Artifactory will also delete your data volumes and you will lose all of your data. You must back up all this information before deletion. You do not need to uninstall Artifactory before deleting it.

```sh
helm delete jfrog/artifactory-oss --namespace artifactory
```

# rancher安装artifactory

- 单独开一台虚机，启动rancher容器

> 注意：Ubuntu 2204有bug起导致容器中的K3S起不来：https://github.com/rancher/rancher/issues/36238

~~~sh
#ubuntu 2004上安装latest rancher可以起来
docker run -d --restart=unless-stopped -p 80:80 -p 443:443 --privileged acrcdstest.azurecr.cn/rancher:latest
#按照提示获取登录密码
~~~

- azure 创建 sp

~~~sh
az ad sp create-for-rbac --scope /subscriptions/4eab3273-e0ec-4165-b6d7-b80ae903b0c7/resourcegroups/rg-artifactory-cds-demo --role Contributor
~~~

> rancher无法导入AKS集群，他会默认集群在china east，导致无法获取到api version，但是这个配置无处改变，遂放弃

# Artifactory-cpp-ce-helm部署到AKS

- 外部azure pgsql先创建好

- helm文件配置
  - 先在helm配置文件中修改image地址到ACR
  - 配置system.yaml中的database字段到外部azure pgsql（参数配置要找到对应的values.yaml），
  - 配置关闭nginx、内部pgsql等功能（找到外部和内部两个values.yaml）


~~~sh
#key用手动生成的
export MASTER_KEY=$(openssl rand -hex 32)
export JOIN_KEY=$(openssl rand -hex 32)
helm install artifactory-cpp-ce  ./ --set artifactory.masterKey=${MASTER_KEY}   --set artifactory.joinKey=${JOIN_KEY}   --set artifactory.nginx.enabled=false   --set artifactory.postgresql.enabled=false   --set postgresql.enabled=false   --set artifactory.artifactory.service.type=NodePort   --set artifactory.artifactory.resources.requests.cpu="500m"   --set artifactory.artifactory.resources.limits.cpu="2"   --set artifactory.artifactory.resources.requests.memory="1Gi"   --set artifactory.artifactory.resources.limits.memory="4Gi"  -n artifactory -f values.yaml #--dry-run --debug > result.txt

#key用secret
export MASTER_KEY=$(openssl rand -hex 32)
echo ${MASTER_KEY}
kubectl create secret generic masterkey-secret -n artifactory --from-literal=master-key=${MASTER_KEY}

export JOIN_KEY=$(openssl rand -hex 32)
echo ${JOIN_KEY}
kubectl create secret generic joinkey-secret -n artifactory --from-literal=join-key=${JOIN_KEY}

helm install artifactory-cpp-ce  ./ --set artifactory.nginx.enabled=false   --set artifactory.postgresql.enabled=false   --set postgresql.enabled=false   --set artifactory.artifactory.service.type=NodePort   --set artifactory.artifactory.resources.requests.cpu="500m"   --set artifactory.artifactory.resources.limits.cpu="2"   --set artifactory.artifactory.resources.requests.memory="1Gi"   --set artifactory.artifactory.resources.limits.memory="4Gi"  -n artifactory -f values.yaml
~~~

- internal LB代理pod，selector复制helm里面的tag进来。注意后面tag变化之后也要修改iLB的selector

  doc: https://docs.azure.cn/zh-cn/aks/internal-lb?tabs=set-service-annotations

~~~yaml
tee iLB.yaml <<'EOF'
apiVersion: v1
kind: Service
metadata:
  name: ilb-artifactory-cpp-demo
  namespace: artifactory
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-ipv4: 10.225.126.70 # fixed internal IP
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
~~~

- 查看release

~~~sh
helm list -n artifactory
~~~

- 升级release

~~~sh
#cd到helm项目目录
helm upgrade artifactory-cpp-ce -n artifactory .
~~~

- 卸载release

~~~sh
helm uninstall artifactory-cpp-ce -n artifactory
~~~

- 10/12 admin/cdsPassw0rd
