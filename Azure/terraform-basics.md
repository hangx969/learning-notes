# 介绍

- ARM template和Bicep都是仅用于Azure的

- Terraform是 Hashicorp发明，基于Go语言

- 脚本采用HCL语言：

  - 声明式脚本语言，Infrastructure as Code，通过目标状态和现在状态的对比，来实现资源的变更。

  - 脚本即文档
  
  - 比ARM template少30%

# Terraform 三个阶段

- terraform init
  - 检查脚本使用了哪些provider，会下载下来。

- terraform plan
  - 提示登录到azure
  - 会计算出来通过哪几步达到目标状态

- terraform apply
  - 执行变更，会提示是否变更。如果需要跳过提示的话，加参数 --auto-approve。


# 基本文件

- main.tf
  - 部署的骨头架子，存放主要的代码

- variable.tf
  - 集中存储变量

- terraform.tfvars
  - 覆盖一些变量，作为变量的临时定义处
- terraform.tfstate文件
  - 以json文件的格式描述了所有被terraform管理的资源状态，会拿这个文件和main.tf文件作比对，找到差异。

# 配置文件main.tf组成

- Provider部分：用哪家的provider	

- resource部分：创建什么资源

- variable部分：集中存储变量、参数

- output文件
  - 某些值需要在等资源创建出来之后才有。比如资源ID等。
  - 如果这些值需要在其他地方被使用，可以把这些值放到output文件里面。

# 示例

## 创建azure资源组

- main.tf文件

~~~sh
terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.100.0"
    }
  }
}

provider "azurerm" {
    features {} #This is required for v2+ of the provider even if empty or plan will fail
    # Configuration options
    environment = "china"
}

resource "azurerm_resource_group" "ExampleRG" {
  name     = "HangXu-ExampleRG"
  location = "chinanorth3"
}
~~~

~~~sh
#使用azcli的方式登录
az cloud set --name AzureChinaCloud
az login -t 5748bdcc-52eb-4a8e-be69-29d0645fadbf 
az account set --name "onepilot-dev"
#执行部署
terraform plan -out=./tf-plan
terraform apply "./tf-plan"
~~~

# variable存储变量

- main.tf

~~~sh
# 3 Files
# main.tf – The main configuration file for resource deployment.
# variables.tf – The file for variables used for the deployment.
# terraform.tfvars – The variable definition file used to set the variables for the deployment.

terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.100.0"
    }
  }
}

provider "azurerm" {
  features{}
  environment = "china"
}

# Local is a also a varibale, it's for repetitive use.
locals {
  tags = {
    owner = "hangxu"
    usage = "LearnTerraform"
  }
}

#Create a Resource Group, note "resourcegroup" is a local name for Terraform only
resource "azurerm_resource_group" "resourcegroup" {
  name     = var.rsgname #call Variable
  location = var.location #call Variable
  tags = local.tags # #call Local
}

#Create a Storage Account
resource "azurerm_storage_account" "storageaccount" {
  name                     = var.stgactname
  resource_group_name      = azurerm_resource_group.resourcegroup.name
  location                 = azurerm_resource_group.resourcegroup.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags = local.tags
  }
~~~

- variable.tf

~~~sh
# Variables can be in main.tf, but it's a mess, so we seperated it

variable "location" {
  type = string
  description = "Location for deployment"
  default = "chinanorth3"
}

variable "rsgname" {
  type = string
  description = "Resource Group Name"
  default = "Hangxu-TerraformRG"
}

variable "stgactname" {
  type = string
  description = "Storage Account Name" #Storage Account should be globally unique
}
~~~

- terraform.tfvars

~~~sh
# 虽然我们可以通过这种方式指定variable，terraform plan -var="stgactname=cirtest332244423"
# 但很不方便，所以我们创建terraform.tfvars文件

location = "chinanorth3"
rsgname = "Hangxu-TerraformRG"
stgactname = "hangxutestsa"
~~~

- variable.tf和terraform.tfvars的区别
  - 主要用于声明在Terraform配置中使用的变量。你可以在这个文件中定义变量的类型、默认值和描述等信息。
  - 主要用于设置在Terraform配置中声明的变量的值。在执行`terraform apply`或`terraform plan`命令时，Terraform会自动加载这个文件，并使用其中的值来填充变量。
  - `variables.tf`用于声明变量，而`terraform.tfvars`用于为这些变量设置值。这种分离的方式使得你可以在不同的环境中使用不同的`terraform.tfvars`文件，而不需要修改Terraform的主配置。

# module可复用的基础架构代码

- 在Terraform中，模块（Module）是一种可重用的、自包含的包，它封装了一组相关的资源。模块可以被视为一种函数或者微服务，它接收一组输入变量，然后输出一组资源。

- 模块的主要作用有：

  1. **代码重用**：你可以将常用的配置封装成模块，然后在多个地方重用，避免了代码的重复。

  2. **组织代码**：你可以使用模块来组织你的Terraform代码，将复杂的配置分解成一组可管理的模块。

  3. **共享代码**：你可以将模块发布到Terraform Registry，让其他人可以使用你的模块。

  例如，你的`main.tf`文件中的存储账户资源可以被封装成一个模块，然后在其他地方重用。模块的定义可能如下：

  ```terraform
  module "storage_account" {
    source  = "Azure/storage/azurerm"
    version = "1.5.0"
  
    name                     = var.stgactname
    resource_group_name      = azurerm_resource_group.resourcegroup.name
    location                 = azurerm_resource_group.resourcegroup.location
    account_tier             = "Standard"
    account_replication_type = "LRS"
    tags = local.tags
  }
  ```

  然后在其他地方使用这个模块，只需要提供输入变量：

  ```terraform
  module "storage_account" {
    source = "../modules/storage_account"
    
    stgactname = "my_storage_account"
    # other variables...
  }
  ```

  这样，你就可以在多个地方重用这个存储账户的配置，而不需要每次都写一遍相同的代码。

- 在基础架构的目录中，root根目录下面会有main.tf/variables.tf/terraform.tfvar，可以创建一个modules目录，里面同样定义main.tf等，在其他地方可以引用这个modules文件中的资源定义。

# outputs获取模块的输出

- 示例 - 创建outputs.tf

~~~terraform
# output "Resource Group" name, to be used as an input variable for "Storage Account"

output "rg_name_out" {
  value = azurerm_resource_group.example.name # 资源类型.资源名.name
}
~~~

- 示例 - 引用outputs.tf中的值

~~~terraform
# call "StorageAccount" module which has 3 variables
module "StorageAccount" {
  source ="./StorageAccount"
  basename = "learntfmodule"
  resource_group_name = module.ResourceGroup.rg_name_out #引用来自Resource Group module的outputs
  location = "chinanorth3"
}
~~~

- modules子目录中定义的outputs可以作为主模块或者其他子模块的输入，来引用。
- 根目录中定义的outputs.tf可以作为terraform apply的输出，显示到terminal上。

# backend状态文件存储

> Terraform的状态文件（通常命名为`terraform.tfstate`）是Terraform管理和跟踪资源的关键组件。Terraform使用这个文件来记录它所管理的各种资源的信息，以及这些资源的配置和属性。
>
> 以下是Terraform状态文件的主要用途：
>
> 1. **映射资源到实际资源**：Terraform使用状态文件来映射你的配置文件中定义的资源到实际的云资源。例如，你可能在配置文件中定义了一个AWS EC2实例，Terraform会在状态文件中记录这个实例的ID，以便在将来的操作中找到它。
> 2. **存储元数据**：状态文件还包含了关于你的Terraform环境的元数据，例如Terraform的版本号，以及你的提供者的版本号。
> 3. **跟踪更改**：每次你运行`terraform apply`时，Terraform都会更新状态文件，以反映你的环境的最新状态。这使得Terraform能够知道哪些资源已经被创建，哪些资源已经被修改，哪些资源已经被删除。
> 4. **支持团队协作**：通过共享状态文件，团队成员可以共享对Terraform环境的视图，这对于团队协作非常重要。
>
> 需要注意的是，由于状态文件可能包含敏感信息，因此需要妥善保管。在生产环境中，通常会使用远程状态存储（如Terraform Cloud或AWS S3）来安全地存储和共享状态文件。

- 我们都知道在执行部署计划之后，当前目录中就产生了名叫 “terraform.states” 的 Terraform 的状态文件，该文件中记录了已部署资源的状态。默认情况下，在执行部署计划后，Terraform 的状态文件会存储在本地，但是这样往往就造成一些弊端：

  （1）不适用团队之间协助，就好比在数据库中对同一条数据进行操作时，就会引起异常

  （2）状态文件中包含一些机密信息，会造成一定的机密泄露

  （3）如果不慎将本地的状态文件删除掉的话，已执行部署计划的资源的管理将很难在通过 Terraform 进行管理

  所以，Terraform 是支持在远端存储状态文件，也就是在 Azure Storage Account 中存储远端状态文件，Terraform 状态的存储是由一个称之为Backend的组件决定的，local state使用的是local backend。并且其他所有的Backend在使用之前都需要在模板中显式定义并通过 **terraform init** 来实现加载和配置。

- 可以把terraform状态文件保存到存储账户中: https://www.cnblogs.com/AllenMaster/p/14274731.html

- 当你运行`terraform init`命令时，Terraform会初始化后端，并将本地状态文件迁移到远程状态存储。在后续的`terraform apply`或`terraform destroy`操作中，Terraform会直接从远程状态存储读取和写入状态。
- 如果你想从远程状态存储拉取最新的状态，你可以运行`terraform refresh`命令。如果你想将远程状态下载到本地，你可以运行`terraform state pull`命令。如果你想将本地状态推送到远程存储，你可以运行`terraform state push`命令。
- 需要注意的是，使用远程状态存储需要考虑安全性和访问控制。例如，你可能需要配置适当的IAM策略来限制对S3 bucket的访问，或者使用服务器端加密来保护存储在bucket中的状态文件。

# import导入已有资源

- 项目根目录创建一个imports.tf文件

  ~~~json
  tee imports.tf <<'EOF'
  import {
      to = azurerm_storage_account.infrasa
      id = "/subscriptions/9365cbc6-1cc4-4ab2-bd5f-2cb518cc2a51/resourceGroups/rg-mapapps-dev-mmatransfer/providers/Microsoft.Storage/storageAccounts/samapappsdevmmatransfer"
  }
  EOF
  ~~~

- terraform导入

  ~~~sh
  terraform plan -generate-config-out=generated_resources.tf
  ~~~

- 在generated_resources.tf中即可看到资源定义

# Terraform源参数

Terraform 为所有资源类型提供了一组通用的元参数,包括:

- count - 控制资源实例的数量
- for_each - 基于集合创建多个实例
- depends_on - 显式声明依赖关系
- provider - 指定使用的 provider
- lifecycle - 控制资源生命周期行为

示例：`count` 的工作原理，条件创建逻辑:

- **当 `count = 1`** (vpc_cen_grant 不为 null)
  - 创建 **1个** 资源实例
  - 资源引用: `alicloud_cen_transit_router_grant_attachment.vpc_cen_grant[0]`
- **当 `count = 0`** (vpc_cen_grant 为 null)
  - 创建 **0个** 资源实例
  - 相当于此资源**不存在**,Terraform 跳过此资源

~~~sh
resource "alicloud_cen_transit_router_grant_attachment" "vpc_cen_grant" {
  count = var.vpc.vpc_cen_grant != null ? 1 : 0
  # ... 其他属性
}
~~~

count 是 Terraform 核心功能,与具体的云资源类型无关。任何 Terraform 资源(AWS、Azure、阿里云等)都可以使用 count 来控制创建数量, 包括 0 个(即不创建)。



# terraform questions

Basic：

1. What is Terraform, and why is it used in the context of infrastructure automation? 

Terraform is an open-source infrastructure as code (IaC) tool developed by HashiCorp. It allows you to define and manage your infrastructure declaratively using a simple and human- readable configuration language. 

Terraform is used for infrastructure automation to provision and manage resources across various cloud providers and on-premises environments in a consistent and reproducible manner. 

2. What is the Terraform state file, and why is it important? 

The Terraform state file is a JSON or binary file that stores the current state of the managed infrastructure. It records resource metadata, dependencies, and other relevant information. The state file is critical for Terraform's operation as it allows the tool to understand the existing infrastructure and track changes over time. 

It helps Terraform determine the delta between the desired state and the actual state during subsequent runs, enabling it to apply the necessary updates accurately. 

3. What is the purpose of the Terraform plan command? 

The Terraform plan command is used to create an execution plan that shows the changes Terraform will apply to the infrastructure. It compares the desired state defined in the configuration with the current state recorded in the state file. 

The plan command provides a summary of the actions Terraform will take, such as creating, modifying, or deleting resources. It allows you to review and verify the changes before applying them to the infrastructure. 

4. What is the purpose of the "Terraform init" command? 

The "Terraform init" command initializes a Terraform working directory. It downloads and installs the necessary provider plugins, sets up the backend configuration, and prepares the directory for Terraform operations. 

5. What are Terraform variables, and how can you use them in your infrastructure code? 

Terraform variables allow you to parameterize your infrastructure code and make it more reusable and configurable. Variables can be defined in Terraform configuration files or separate variable files. You can use variables to customize resource configurations, such as specifying the number of instances or setting environment-specific values. 

By leveraging variables, you can avoid hardcoding values and easily reuse and share your infrastructure code across different environments. 

6. How does Terraform handle variable interpolation in strings? 

Terraform allows variable interpolation in strings using the "${var.NAME}" syntax. When the configuration is processed, Terraform replaces the variable references with their corresponding values. 

Intermediate：

7. How can you organize your Terraform codebase for better maintainability?

To organize a Terraform codebase for better maintainability, you can adopt various practices:

***\*Modularization\****: Break down the codebase into reusable modules, encapsulating related resources and configurations.

***\*Folder Structure\****: Organize files into logical folders based on resource types, environments, or modules.

***\*Naming Conventions\****: Use consistent and descriptive naming conventions for resources, variables, and modules.

***\*Documentation\****: Include comments, README files, or documentation to provide guidance and context for the codebase.

***\*Version Control\****: Utilize a version control system like Git to track changes, collaborate, and roll back if needed.

By following these practices, you can enhance code readability, reusability, and collaboration, making the codebase easier to maintain and evolve.

8. Explain the concept of Terraform providers and their role in resource provisioning. 

Terraform providers are plugins that enable Terraform to interact with specific infrastructure platforms, such as AWS, Azure, or GCP. They provide a way for Terraform to manage and provision resources on these platforms. Each provider implements resource types and APIs to create, update, and delete resources. 

By configuring a provider in Terraform, you can leverage its resource types to define infrastructure as code and manage the lifecycle of resources on the target platform 

9. What is the purpose of Terraform modules, and how do they promote reusability? 

Terraform modules are self-contained packages of Terraform configurations that encapsulate a specific set of resources and their associated dependencies. Modules promote reusability by allowing you to define and share infrastructure components across projects and teams. 

With modules, you can abstract complex configurations into reusable building blocks, reducing duplication, and improving maintainability. Modules can be published and consumed internally or through public module registries, enabling code sharing and collaboration. 

10. How does Terraform handle drift detection and reconciliation? 

Terraform handles drift detection by comparing the state stored in the state file with the current state of the infrastructure. During a Terraform application, it detects any differences between the two states and identifies resources that have drifted. 

To reconcile the drift, Terraform determines the necessary actions (create, update, or delete) to bring the infrastructure back to the desired state defined in the configuration. By applying the changes, Terraform ensures that the infrastructure aligns with the intended configuration and resolves any discrepancies. 

11. Describe how Terraform applies changes to your infrastructure and what happens during a Terraform application. 

During a Terraform application, Terraform examines the configuration and state to determine the changes needed to reach the desired state. It creates an execution plan that outlines the actions required for resource creation, modification, or deletion. After confirming the execution plan, Terraform applies the changes by invoking the respective provider APIs. 

It provisions or updates resources according to the plan and updates the state file with the new infrastructure state. Terraform captures the output values of the resources, which can be used for further configuration or reference in subsequent Terraform runs. 

12. How can you manage secrets and sensitive data in Terraform?

Managing secrets and sensitive data in Terraform require careful consideration to ensure security. Best practices include:

· Storing secrets outside of version-controlled files, using tools like HashiCorp Vault or cloud-specific secret management services.

· Utilizing Terraform input variables or environment variables to pass sensitive values securely during runtime.

· Encrypting sensitive data using tools like Terraform Vault provider or native encryption mechanisms provided by the infrastructure platform.

· Avoid writing secrets in plain text within Terraform configurations or logs.

By following these practices, you can protect sensitive information and minimize the risk of exposing secrets unintentionally.

Advanced：

13. Explain the role of Terraform data sources and how you can use them.

Terraform data sources allow you to fetch and reference information from external systems or existing resources. They provide a way to query and import data into your Terraform configurations.

You can use data sources to retrieve attributes or metadata from various sources such as cloud providers, databases, or APIs. This data can then be used to make decisions, configure resources, or establish dependencies within your infrastructure.

14. How can you perform blue-green deployments using Terraform?

Blue-green deployments involve creating two identical environments (blue and green) and switching traffic from one to the other. In Terraform, you can achieve this by creating two sets of infrastructure resources with slight differences, such as different AWS Auto Scaling Groups or Azure Virtual Machine Scale Sets.

Once the new environment (green) is provisioned and tested, you can update the load balancer or DNS records to direct traffic to the green environment. Terraform enables you to manage the infrastructure changes required for blue-green deployments in a declarative and automated manner.

15. How can you integrate Terraform with CI/CD pipelines?

Terraform can be integrated with [CI/CD pipelines](https://www.turing.com/kb/ci-cd-pipeline) to automate the deployment and management of infrastructure. Here's the typical process:

· Commit the Terraform configurations to a version control system (e.g., Git).

· Set up a CI/CD pipeline that monitors changes to the Terraform code repository.

· In the pipeline, execute Terraform commands such as init, validate, and plan to ensure the configurations are valid and generate an execution plan.

· Use Terraform's apply command to create or modify infrastructure based on the approved changes.

· Optionally, leverage infrastructure testing and verification tools to validate the deployed infrastructure.

· Finally, trigger additional pipeline stages for application deployment, testing, and release.

16. How can you manage Terraform state locking for team collaboration?

Terraform state locking is crucial for preventing concurrent modifications to the same infrastructure. To manage state locking for team collaboration, you can use a remote backend with built-in state locking support.

Terraform supports various remote backends like Amazon S3, Azure Storage, or HashiCorp Consul. By configuring a remote backend, Terraform automatically handles the state locking, ensuring that only one user or process can modify the state at a time.

This prevents conflicts and data corruption when multiple team members are working on the same infrastructure concurrently.

17. How can you perform rolling updates or zero-downtime deployments with Terraform?

Rolling updates or zero-downtime deployments involve updating infrastructure components without causing service disruptions. With Terraform, you can achieve this by utilizing features such as rolling deployment strategies and lifecycle hooks.

For example, you can define an AWS Auto Scaling Group with a rolling update policy to gradually replace instances while ensuring the overall availability of the application. Terraform allows you to specify update policies, health checks, and other parameters to control the pace and behavior of updates, minimizing downtime and ensuring smooth transitions.

 

 

 