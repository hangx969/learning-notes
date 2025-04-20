# ACR

[托管容器注册表 - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-intro)

## 层级概念

[关于注册表、存储库、映像和项目 - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-concepts)

![image-20231031170357549](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311703613.png)

- 容器注册表

  [支持的内容格式 - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-image-formats)

- 存储库

  名称相同但是标记不同的镜像；标记不同的含义有两种：

  1. tag不同

  2. namespace不同

- 容器镜像

  层：注册表中的项目共享公用的层，因而提高了存储效率。

## 清单

- 推送到ACR的每个image都与一个清单关联，推送的时候由注册表生成清单唯一标识image。

- 列出存储库的清单：

```bash
az acr manifest list-metadata --name azure-vote-front --registry xhacrtest
```

### 清单摘要 digest

- 清单由唯一的 SHA-256 哈希（即清单摘要）进行标识 。 每个映像或项目（无论是否标记）均由其摘要标识。 即便项目的层数据与其他项目的层数据相同，摘要值也是唯一的。 此机制使你能够反复向注册表推送标记相同的映像。 例如，你可反复向注册表推送 myimage:latest 而不出任何错误，因为每个映像均由其唯一摘要标识。

## 项目寻址

[关于注册表、存储库、映像和项目 - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-concepts#addressing-an-artifact)

- ACR要用完全限定URL：\<registry name>. azurecr. cn

## ACR的SKU

[注册表服务层级和功能 - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-skus)

## 推送image到ACR

[快速入门 - 创建注册表 - Azure CLI - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-get-started-azure-cli#push-image-to-registry)

- 将映像推送到注册表之前，必须使用 ACR 登录服务器的完全限定的名称进行标记。 登录服务器名称采用 \<registry-name>.azurecr.cn（全小写）格式，例如 *mycontainerregistry007.azurecr.cn*。

- 使用 [docker tag](https://docs.docker.com/engine/reference/commandline/tag/) 命令标记映像。 使用 ACR 实例的登录服务器名称替换 \<acrLoginServer>

## image异地复制、区域冗余

[教程 - 创建异地复制注册表 - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-tutorial-prepare-registry)

- 需要Premium的SKU

## ACR 任务

在Azure中生成docker镜像，推送至Registry

- 快速任务：az acr build使用docker build；发送到ACR任务。

- 自动触发的任务

- - 提交代码时生成
  - 更新base image时生成
  - 定时运行

- 多步骤任务

日志查看：az acr task logs

## ACR MI

在 ACR 任务中启用 Azure 资源的托管标识，使**该任务无需提供或管理凭据**即可访问其他 Azure 资源。 例如，使用托管标识可让某个任务步骤将容器映像提取或推送到其他注册表。

## ACR登录

To authenticate with an Azure Container Registry, you can use the az acr login command with the name of the registry:

```bash
#This command will authenticate your Docker CLI with the Azure Container Registry and allow you to push and pull images
az acr login --name <registry_name>
#Alternatively, you can use the docker login command with the fully qualified name of the registry, This command will prompt you for your Azure Container Registry username and password, which you can find in the Azure portal under "Access keys" in the container registry's settings.
docker login <registry_name>.azurecr.io
#After authenticating, you can use the Docker CLI to push and pull images to and from the Azure Container Registry.
```

## ACR清理image

[清除标记和清单- Azure Container Registry | Azure Docs](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fdocs.azure.cn%2Fzh-cn%2Fcontainer-registry%2Fcontainer-registry-auto-purge%23run-in-an-on-demand-task&data=05|01|hangx%40microsoft.com|868fb1a8d7154d8ab7d008db60d8ba91|72f988bf86f141af91ab2d7cd011db47|1|0|638210256247290568|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=%2F5gQ7fDh3nDcu7%2FMwoCKDM1wxhKeM72DhpwxQ7RkXZo%3D&reserved=0)

![image-20231031172557527](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311725569.png)

- --filter是必需的选项，如果您需要对所有repository进行清理，请使用类似如下方式。

  ```bash
  PURGE_CMD="acr purge --filter '*:.*'--untagged --ago 180d --dry-run" 
  ```

  重要：由于删除的image无法恢复，请在删除前使用--dry-run参数来查看可能被删除的数据。

## Troubleshooting

[注册表登录故障排除 - Azure Container Registry | Azure Docs](https://docs.azure.cn/zh-cn/container-registry/container-registry-troubleshoot-login)

[Can't pull images from Azure Container Registry to Kubernetes - Azure | Microsoft Learn](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-kubernetes/cannot-pull-image-from-acr-to-aks-cluster)

```bash
az acr check-health #测试ACR健康情况
az aks check-acr --name <aks name> --resource-group <aks rg> --acr <acr name> #查看AKS与ACR连接性
```

## AzureChina注册表endpoint

- 不过由于docker.io的镜像仓库，其IP所在的地理位置位于海外，在整个网络链路上涉及到的节点比较多，确实会存在网络拥塞导致的拉取镜像慢或是失败的情况。

- 您可以考虑使用Azure China的container registry proxy，其部署在Azure中国数据中心内部，可以实现镜像的缓存，进而实现更加稳定快速的镜像拉取，详情请见: [container-service-for-azure-china/README.md at master · Azure/container-service-for-azure-china · GitHub](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Fgithub.com%2FAzure%2Fcontainer-service-for-azure-china%2Fblob%2Fmaster%2Faks%2FREADME.md%2322-container-registry-proxy&data=05|01|hangx%40microsoft.com|4f732694e9b14b1adcba08dabe01f3f0|72f988bf86f141af91ab2d7cd011db47|1|0|638031213178529331|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=qyk78YI4b7Ses1bt%2F%2FiZbnyHYNeFCuU5SIM9QU709fw%3D&reserved=0)

  ![image-20231031172012735](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311720820.png)

# ACI

- 不管什么方案（包括简单应用程序、任务自动化、生成作业），只要能够在隔离容器中操作，就可以使用 Azure 容器实例这种解决方案。
- [Azure 中的无服务器容器 - Azure Container Instances | Azure Docs](https://docs.azure.cn/zh-cn/container-instances/container-instances-overview)

- 底层也是跑在VM上，创建的时候可以选择CPU、内存的大小。

![image-20231031172127637](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310311721707.png)

## 持久存储

- 默认情况，容器是无状态的，崩溃重启等，会造成数据丢失。

- 可以将file share挂载到instance上：[将 Azure 文件卷装载到容器组 - Azure Container Instances | Azure Docs](https://docs.azure.cn/zh-cn/container-instances/container-instances-volume-azure-files#deploy-container-and-mount-volume---yaml)

- 可以用azcli或者yaml文件来部署容器并挂载

## 容器组

- 容器组中的容器共享生命周期、资源、本地网络和存储卷；与POD概念类似。

  [教程 - 部署多容器组 - YAML - Azure Container Instances | Azure Docs](https://docs.azure.cn/zh-cn/container-instances/container-instances-multi-container-yaml)

- 用yaml文件+azcli部署

## 查看容器日志

[教程 - 部署多容器组 - YAML - Azure Container Instances | Azure Docs](https://docs.azure.cn/zh-cn/container-instances/container-instances-multi-container-yaml#view-container-logs)

[获取容器实例日志和事件 - Azure Container Instances | Azure Docs](https://docs.azure.cn/zh-cn/container-instances/container-instances-get-logs)