# Artifactory-ACI

## Prepare Image

- create ACR：acrcdstest

~~~sh
az cloud set --name AzureChinaCloud 
az login -t 8f56d2b8-03ec-4557-b25b-da031f0b234c
az acr list
az acr login --n acrcdstest
docker pull releases-docker.jfrog.io/jfrog/artifactory-oss:latest
docker tag releases-docker.jfrog.io/jfrog/artifactory-oss:latest acrcdstest.azurecr.cn/artifactory:latest
docker push acrcdstest.azurecr.cn/artifactory:latest
~~~

## Prepare Storage

https://docs.azure.cn/zh-cn/container-instances/container-instances-volume-azure-files#deploy-container-and-mount-volume---yaml

- Create sa and file share

~~~sh
# Change these four parameters as needed
ACI_PERS_RESOURCE_GROUP=rg-artifactory-cds-test
ACI_PERS_STORAGE_ACCOUNT_NAME=artsa
ACI_PERS_LOCATION=chinanorth3
ACI_PERS_SHARE_NAME=acishare

# Create the storage account with the parameters
az storage account create --resource-group $ACI_PERS_RESOURCE_GROUP --name $ACI_PERS_STORAGE_ACCOUNT_NAME --location $ACI_PERS_LOCATION --sku Standard_LRS

# Create the file share
az storage share create --name $ACI_PERS_SHARE_NAME --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME

# Get credentials
STORAGE_KEY=$(az storage account keys list --resource-group $ACI_PERS_RESOURCE_GROUP --account-name $ACI_PERS_STORAGE_ACCOUNT_NAME --query "[0].value" --output tsv)
echo $STORAGE_KEY
~~~

## Prepare postgresql

## ACI deployment

> Best Practices:
>
> - 容器组 IP 地址在创建或删除后可能会发生更改。 建议不要让应用程序代码依赖于容器组的 IP 地址。 如果想维护静态 IP 地址，还建议使用 [NAT 网关](https://docs.azure.cn/zh-cn/container-instances/container-instances-nat-gateway)或[应用程序网关](https://docs.azure.cn/zh-cn/container-instances/container-instances-application-gateway)。
> - ACI 服务保留以下服务功能端口：22、1025-1027、3389-3399、9999、19000、19080、19390、19100、20000-30000、49152-65534。 请避免在容器组定义中使用这些端口。
> - 可在 Azure 容器实例上部署的容器映像的最大大小为 15 GB。 根据部署时的确切可用性，你也许可以部署更大的映像，但不能保证映像大小更大。

~~~sh
az container create \
    --resource-group $ACI_PERS_RESOURCE_GROUP \
    --name artifactory \
    --image acrcdstest.azurecr.cn/artifactory:latest \
    --ports  \
    --azure-file-volume-account-name $ACI_PERS_STORAGE_ACCOUNT_NAME \
    --azure-file-volume-account-key $STORAGE_KEY \
    --azure-file-volume-share-name $ACI_PERS_SHARE_NAME \
    --azure-file-volume-mount-path /aci/logs/
~~~



# Artifactory-docker

https://jfrog.com/help/r/jfrog-installation-setup-documentation/install-artifactory-single-node-with-docker

## external database

- For Non-Production environment, you can start an PostgreSQL container on the same machine as Artifactory Container:

```sh
docker run --name postgres -itd -e POSTGRES_USER=artifactory -e POSTGRES_PASSWORD=Passw0rd -e POSTGRES_DB=artifactorydb -p 5432:5432 library/postgres
```

- Configure the system.yaml file with the database configuration details:

```yaml
shared:
  database:
    driver: org.postgresql.Driver
    type: postgresql
    url: jdbc:postgresql://host.docker.internal:5432/artifactorydb
    username: artifactory
    password: Passw0rd
```

## start up container

~~~sh
mkdir /app/jfrog
export JFROG_HOME=/app/jfrog
mkdir -p $JFROG_HOME/artifactory/var/etc/
cd $JFROG_HOME/artifactory/var/etc/
touch ./system.yaml
chown -R 1030:1030 $JFROG_HOME/artifactory/var
docker run --name artifactory -v $JFROG_HOME/artifactory/var/:/var/opt/jfrog/artifactory -d -p 8081:8081 -p 8082:8082 releases-docker.jfrog.io/jfrog/artifactory-oss:latest
~~~

> 管理页面:http://localhost:8082/ui/,默认管理用户名admin,口令password
>

