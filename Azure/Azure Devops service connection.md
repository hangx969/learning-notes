# service connection

作用是在pipeline中连接到azure cloud中。是azure devops project级别的资源，在project setting中添加。

https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops

## 连接方式

https://learn.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops#create-an-azure-resource-manager-app-registration-with-workload-identity-federation-automatic

ado中提供了如下几种连接方式：

1. App registration (automatic)：只适用于azure global，因为需要在UI界面直接选择订阅。而Azure China的sub他是识别不了的。
2. managed identity：同上
3. App registration or managed identity (manual): 可以支持自定义Cloud type，可以设成AzureChinaCLoud

## 认证方式

app registration/managed identity方式都支持两种认证方式：

1. workload identity： 是推荐的方式，需要在service principal或者managed identity上创建federated secret，让entraID信任devops颁发的token。在相应的scope上授予权限，devops就能用这个身份创建资源。
2. secret： 不推荐，因为client secret需要手动rotation。

现在我们采用的是service principal+federated secert方式，目前存在一个bug就是service principal - federated secert设置中需要手动把Audience的值从`api://AzureADTokenExchangeChina`（默认值）改成`api://AzureADTokenExchange`。否则devops会找不到service principal

与Azure Support沟通后，他们表示这种修改是非标操作，建议更换为workload identity方式。

测试下来workload identity同样可以实现同样的功能，并且在创建federated secret时默认值就是`api://AzureADTokenExchange`并不需要再改。

### managed identity+workload identity

先在devops UI界面添加service connection中获取到issuer和subject identifier。然后可以用下面terraform代码创建uai+federated secert。

然后去devops UI界面verify and save，完成service connection的创建。

~~~terraform
resource "azurerm_user_assigned_identity" "uai" {
  name                = var.uai_name
  location            = var.location
  resource_group_name = var.test-rg.name

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "azurerm_role_assignment" "test-assign" {
  depends_on           = [azurerm_user_assigned_identity.uai]
  scope                = var.test-rg.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.uai.principal_id
  timeouts {
    create = "20m"
  }
}

resource "azurerm_federated_identity_credential" "example" {
  name                = "ado-service-connection"
  resource_group_name = var.test-rg.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = ""
  parent_id           = azurerm_user_assigned_identity.uai.id
  subject             = ""
}
~~~

