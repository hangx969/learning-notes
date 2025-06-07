# Self-hosted agents

> https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agents?view=azure-devops&tabs=yaml%2Cbrowser#self-hosted-agents

- azure devops在azure china不支持MS managed agents，只能是用self-hosted agents，可能会存在一些cache warm-up和拉取commit到local repo的准备时间。
- self-hosted agents提供capability，意思是上面装了什么软件。pipeline的demand会定义需要哪些软件。
  - 如果pipeline定义的demands，没有agent具备capability能满足，那么job就会失败。
  - 如果是没有空闲的agent能满足demands，job就会等待。

- azure devops - pipelines - edit - triggers - YAML - Default agent pool for YAML：可以选择默认用Azure-hosted还是private（self hosted）。yaml文件里面没定义agent pool的话，就用这个默认的。

## Agent与pipeline通信

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/agents?view=azure-devops&tabs=yaml%2Cbrowser#communication

- agent向pipeline注册的时候会拿到一个listener OAuth Token。

- agent监听pipeline service是否有job要执行，有job的话，会下载一个per-job的OAuth Token，用来访问pipeline的资源，用完即弃。
- agent和pipeline之间走的是非对称加密，agent的公钥在注册的时候提供给了devops service。

## Agent版本

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/v3-agent?view=azure-devops

- agent版本每隔几周会更新，major version.minor version的格式。
- 对于self-hosted agent，小版本可以自动升级，大版本需要手动升级。
- 检查现有agent的version：在agent页面的system capabilities里面。检查最新发布的版本：https://github.com/Microsoft/azure-pipelines-agent/releases

## Agent手动注册

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent?view=azure-devops

## Agent认证

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/personal-access-token-agent-registration?view=azure-devops

- 对于self-hosted agent，当agent向pipeline注册的时候，需要agent做认证。有三种认证方式：PAT、device code、Service Principal

- PAT：在自己account的setting里面创建PAT，复制下来，agent注册时会用
- 注意这个PAT仅用于agent首次向pipeline注册时使用。后续的agent-pipeline通信用的是OAuth Token。

# Agent Custom Image

对于self-hosted agent，我们往往需要创建custom image，安装各种pipeline中需要用到的工具。

## Packer

Packer是一个自动化构建OS image的工具，可以与Azure集成，将image自动化创建到Azure shared image gallery中。

- Packer官网：https://developer.hashicorp.com/packer/install?product_intent=packer#linux
- Azure文档-如何用Packer制作Azure VM Image：https://learn.microsoft.com/en-us/azure/virtual-machines/linux/build-image-with-packer

  - azure还推出了azure image builder但是目前在china属于preview状态：https://learn.microsoft.com/en-us/azure/virtual-machines/linux/image-builder-json?tabs=json%2Cazure-powershell
- HashiCorp文档-packer的azure-arm builder，可以找到hcl template中的各种参数的定义：https://developer.hashicorp.com/packer/integrations/hashicorp/azure/latest/components/builder/arm

### Packer@1

是Packer提供的Azure devops pipeline task。在实际使用中，遇到认证问题：

一开始打算用service connection做认证，但是一直报错：`##[error]Error: Endpoint auth data not present: <id>`。这个id就是service connection的id。这表明service connection在这里没起到认证作用。经过调查原因如下：

1. 首先，Packer@1 task的参数，传递的值是azure devops service connection的name。

~~~sh
connectedServiceAzure: ${{ parameters.serviceConnection }}
connectedServiceType: 'azure'
~~~

2. 去翻了Packer的源码：https://github.com/riezebosch/vsts-tasks-packer/blob/9611850a1b2571bde9c7c7e9459eb5d00cd42039/Packer/PackerV1/src/packer.ts#L69，他是要去找这个service connection对应的service principal的client id和client secert。

3. 也就是说，service connection需要是通过secret的方式注册的，Packer@1才能顺利拿到client secret完成认证。workload identity的方式注册的他拿不到federated secret。Packer@1版本根本不支持Azure devops service connection和EntraID service principal的workload identity的认证方式。
4. 去service connection界面尝试创建一个secret类型的service connection，结果发现根本选不了subscription，他默认会去global endpoint去找，不会识别到china，因为azure devops service连不到Azure China的tenant。也就是说我们用的global azure devops，根本无法创建secret类型的service connection。也就是说我们无法在china使用Packer@1这个task了。

### PackerBuild@1

- Azure devops Pipeline的PackerBuild模块：https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/packer-build-v1?view=azure-pipelines

- PackerBuild task 通过一个模板文件定义一堆参数，告诉Packer：在azure上创建什么样的虚机，用这个虚机制作什么种类的系统镜像，在其中运行哪些自定义脚本安装依赖，最后把镜像保存到什么位置。template有hcl和json两种格式可以选择。
- PackerBuild@1 到2025年依然不支持hcl格式的config文件：https://github.com/microsoft/azure-pipelines-tasks/issues/16753，所以hcl的template用不了。改成json template可用。

### Packer template注意事项

- `build_resource_group_name` - 要求这个rg必须已经提前存在。要去image_gallery.tf文件里面预先创建出来
- `shared_image_gallery_destination.image_name` - 这个变量是指VM Image Definition，也需要提前创建好。Packer会在里面创建image version
- `virtual_network_name` 和 `virtual_network_subnet_name` - 要求虚拟网络和子网也要提前存在。要去terraform中预先创建出来

- Packer Build过程中也需要Azure Cli task，新版@2版本：https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/azure-cli-v2?view=azure-pipelines

## Azure image builder

是azure推荐的，azure托管Packer来做镜像：

- https://learn.microsoft.com/en-us/azure/virtual-machines/linux/image-builder
- https://docs.azure.cn/zh-cn/virtual-machines/image-builder-overview?tabs=azure-cli

根据文档示例尝试建一个image：

~~~sh
az cloud set --name AzureChinaCloud
az login -t <tenant ID>
az account set --subscription <Sub ID>

# Resource group name
sigResourceGroup=""
# Datacenter location
location=chinanorth3
# Additional region to replicate the image to
additionalregion=chinanorth2
# Name of the Azure Compute Gallery
sigName=""
# Name of the image definition to be created
imageDefName=AIB_Image_test
# Reference name in the image distribution metadata
runOutputName=aibImageTest

# 
subscriptionID=<Sub ID>
# Create user-assigned identity for VM Image Builder to access the storage account where the script is stored
identityName=""
# Get the identity ID
imgBuilderCliId=""
# Get the user identity URI that's needed for the template
imgBuilderId=""

# Create VM Definition
az sig image-definition create \
    -g $sigResourceGroup \
    --gallery-name $sigName \
    --gallery-image-definition $imageDefName \
    --publisher myIbPublisher \
    --offer myOffer \
    --sku 20_04-lts-gen2 \
    --os-type Linux \
    --hyper-v-generation V2

curl https://raw.githubusercontent.com/Azure/azvmimagebuilder/master/quickquickstarts/1_Creating_a_Custom_Linux_Shared_Image_Gallery_Image/helloImageTemplateforSIG.json -o helloImageTemplateforSIG.json

sed -i -e "s/<subscriptionID>/$subscriptionID/g" helloImageTemplateforSIG.json
sed -i -e "s/<rgName>/$sigResourceGroup/g" helloImageTemplateforSIG.json
sed -i -e "s/<imageDefName>/$imageDefName/g" helloImageTemplateforSIG.json
sed -i -e "s/<sharedImageGalName>/$sigName/g" helloImageTemplateforSIG.json
sed -i -e "s/<region1>/$location/g" helloImageTemplateforSIG.json
sed -i -e "s/<region2>/$additionalregion/g" helloImageTemplateforSIG.json
sed -i -e "s/<runOutputName>/$runOutputName/g" helloImageTemplateforSIG.json
sed -i -e "s%<imgBuilderId>%$imgBuilderId%g" helloImageTemplateforSIG.json

az resource create \
    --resource-group $sigResourceGroup \
    --properties @helloImageTemplateforSIG.json \
    --is-full-object \
    --resource-type Microsoft.VirtualMachineImages/imageTemplates \
    -n AIBImageTemplateforSIG01

az resource invoke-action \
    --resource-group $sigResourceGroup \
    --resource-type  Microsoft.VirtualMachineImages/imageTemplates \
    -n AIBImageTemplateforSIG01 \
    --action Run
~~~

# vmss agent

- 特点：每个job结束后会reimage job，而且支持base image的更新。无需手动安装注册agent，pipeline自动安装agent
- 创建VMSS需要关闭Overprovisioning和auto-scaling功能。由Pipelines根据要运行的job数量决定scale的数量？（https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/scale-set-agents?view=azure-devops#how-azure-pipelines-manages-the-scale-set）

- custom image：https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/scale-set-agents?view=azure-devops#create-a-scale-set-with-custom-image-software-or-disk-size

- 创建vmss agent pool可以在**Project settings** or **Organization settings**，但是删除agentpool需要去**Organization settings**，而且要先删pipeline上的agent pool，再去portal删vmss。
- 添加vmss agent pool需要一个认证过程，登录的账户要对vmss的sub具有Owner或者User Access Admin角色。
- 如果有现成的service connection，可以不用认证。

## 手动创建agent pool

1. 去image gallery definition里面用custom imageCreate VM，模仿VMSS的配置创建新的VM

2. 进入VM，手动执行一下repo中的cloud init中的脚本、注册脚本：

   ~~~sh
   # cloud init 脚本
   sudo groupadd docker
   sudo usermod -aG docker lxadmin
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo chmod 666 /var/run/docker.sock
   ~~~

   ~~~sh
   #给lxadmin添加无密码sudo
   sudo usermod -aG sudo lxadmin
   visudo
   # User privilege specification 下面添加一行：
   lxadmin ALL=(ALL) NOPASSWD: ALL
   
   # ctrl+O保存，ctrl+X退出
   ~~~

   ~~~sh
   # 执行注册脚本install.sh，注意要在root下执行
   sudo su
   # keyvault{1} secret{2} pool{3} agent_name{4} username{5}
   ./install.sh "kv name" "pat secret name" "agent pool name" "agent name" "linux user name"
   ~~~

3. 等待注册脚本执行完成，去azure devops agent pool中查看是否有新agent加进来，状态是否为online。

## 手动管理agent进程

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent?view=azure-devops&tabs=IP-V4#run-interactively

1. 一次性启动agent进程

~~~sh
cd /devopsagent
./run.sh
~~~

2. 注册成为systemd进程

这就是安装脚本install.sh里面用的方法。

https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/linux-agent?view=azure-devops&tabs=IP-V4#run-as-a-systemd-service

~~~sh
su ${5} -c "$DEVOPS_AGENT/config.sh --unattended  --url https://dev.azure.com/<org name> --auth pat --token ${pat} --pool ${3} --agent ${random} --acceptTeeEula"
./svc.sh install ${5}
./svc.sh start
./svc.sh status
~~~

## Agent pool Authentication

### PAT

我们现在用的就是PAT模式，PAT存到keyvault里面，VMSS用uai从kayvault读取，读取出来用agent的注册脚本传进去完成认证和注册。

微软正在考虑逐步减少PAT的使用：https://devblogs.microsoft.com/devops/reducing-pat-usage-across-azure-devops/

### service principal

想法是把Azure China的service principal或者managed identity注册到Azure devops service，然后用它进行注册。

但是仅支持从azure devops org连接到的EntraID tenant里面加载sp或mi。从Azure China加载不支持。

https://learn.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/service-principal-managed-identity?view=azure-devops

> You can only add a managed identity or service principal for the tenant your organization is connected to. 

可以看下这里的开发指南：https://learn.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/service-principal-managed-identity?view=azure-devops

从sp或mi直接拿access token也不行，还是要求必须是连接到AAD的tenant：

> Make sure the subscription is associated with the tenant connected to the Azure DevOps organization you're trying to access.