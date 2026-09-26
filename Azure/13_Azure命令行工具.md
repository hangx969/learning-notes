---
title: Command Line Tools
tags:
  - azure/tools
  - azure/CLI
  - azure/PowerShell
  - azure/azcopy
aliases:
  - Azure CLI Tools
  - Az PowerShell
  - AzCopy
date: 2026-09-26
---

# Azure 命令行工具

Azure PowerShell、Azure CLI 和 AzCopy 分别用于脚本化管理 Azure 资源，以及在本地与 [[Azure/5_Azure-Storage|Azure Storage]] 之间或不同存储账户之间传输数据。

| 工具 | 主要用途 |
| --- | --- |
| Azure PowerShell | 在 PowerShell 中使用 Az 模块的 cmdlet 管理 Azure 资源 |
| Azure CLI（`az`） | 在命令行或脚本中管理 Azure 资源 |
| AzCopy（`azcopy`） | 复制和同步 Azure Storage 数据 |

## Azure PowerShell

### 简介

PowerShell 是跨平台的自动化和脚本环境，可用于系统管理、部署和测试；其管道传递 .NET 对象。Azure PowerShell 的 Az 模块提供一组 cmdlet，用于在 PowerShell 中管理 Azure 资源。

### 安装

参考：[Az 模块介绍](https://docs.microsoft.com/en-us/powershell/azure/new-azureps-module-az?view=azps-7.3.2)、[Azure PowerShell 安装指南](https://learn.microsoft.com/en-us/powershell/azure/install-az-ps?view=azps-9.4.0)。

- **推荐环境**：受支持的 PowerShell 7 或更高版本。
- **Windows PowerShell 5.1**：需安装 .NET Framework 4.7.2 或更高版本，并更新 PowerShellGet。

在 Windows PowerShell 5.1 中，先更新 PowerShellGet，再安装 Az 模块：

```powershell
Install-Module -Name PowerShellGet -Force
Install-Module -Name Az -Scope AllUsers -Repository PSGallery -Force
```

### 登录 Azure 中国云

```powershell
Connect-AzAccount -Environment AzureChinaCloud
```

> [!tip] 使用应用身份自动登录
> 可在 Microsoft Entra ID（原 Azure AD）中创建应用及客户端机密，再在 PowerShell 脚本中使用该应用身份登录。下图是原文保留的操作示例；机密应妥善保管。
>
> ![应用身份登录示例](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301646534.png)

### 清除登录上下文

登录异常时，可先使用 Az 模块提供的命令清除当前用户保存的上下文与凭据，然后重新登录：

```powershell
Clear-AzContext -Scope CurrentUser
Connect-AzAccount -Environment AzureChinaCloud
```

原笔记还记录了 Windows 上可能涉及的缓存或上下文文件，供排查旧环境时参考；不要不加区分地批量删除：

- `C:\Users\<yourname>\.azure\AzureRmContext.json`
- `C:\Users\<yourname>\.azure\AzureRmContextSettings.json`
- `C:\Users\<yourname>\.azure\AzureRmSurvey.json`
- `C:\Users\<yourname>\.azure\keystore.cache`
- `C:\Users\<yourname>\AppData\Local\.IdentityService\msal.cache`

参考：[Azure PowerShell 上下文与凭据](https://learn.microsoft.com/en-us/powershell/azure/context-persistence)。

## Azure CLI

Azure CLI 是基于 Python 的跨平台命令行工具，用于管理 Azure 资源。

### 安装

- Windows：[安装 Azure CLI](https://docs.azure.cn/zh-cn/cli/install-azure-cli-windows?view=azure-cli-latest&tabs=azure-cli)。
- Linux：[按发行版选择安装方式](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=dnf)。RHEL/CentOS Stream 应按版本使用官方文档对应的软件源；原笔记中的 `yumrepos/azure-cli` 配置属于 RHEL 7 路径，RHEL/CentOS 7 已不再获得 Azure CLI 更新。

### 登录 Azure 中国云

先选择云环境，再交互式登录：

```bash
az cloud set -n AzureChinaCloud
az login
```

> [!warning] 登录失败时
> 如果怀疑本地账户或订阅缓存异常，可参考 [Azure CLI 问题记录](https://github.com/Azure/azure-cli/issues/20231#issuecomment-1007176901)，执行 `az account clear` 清除缓存，然后重新运行 `az login`。清除后必须重新登录，才能继续使用账户相关命令。
>
> <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301652604.png" alt="Azure CLI 登录报错示例" style="zoom:50%;" />

### 选择订阅

先完成交互式登录，查看可用订阅，再切换到目标订阅：

```bash
az account list --output table
az account set --subscription "<订阅 ID 或名称>"
```

原笔记以用户账户和具体订阅 ID 演示切换。现在不建议在命令行中使用用户密码登录：这种方式不适用于启用多重身份验证（MFA）的账户；自动化应使用服务主体或托管身份。

参考：[管理 Azure CLI 订阅](https://learn.microsoft.com/en-us/cli/azure/manage-azure-subscriptions-azure-cli#change-the-active-tenant)、[Azure CLI 登录方式](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli)。

## AzCopy

AzCopy v10 用于在本地和 Azure Storage 之间，或在不同存储账户之间复制、同步 Blob 和文件。

> [!info] 数据传输路径
> **存储账户之间**的复制可使用服务端到服务端 API，数据不必经过运行 AzCopy 的本地机器。**本地与存储账户之间**的上传和下载仍会使用本地网络。AzCopy 客户端还负责发起和监控传输。

### 安装与登录

1. 参考 [AzCopy v10 安装与入门](https://docs.azure.cn/zh-cn/storage/common/storage-use-azcopy-v10?toc=%2Fstorage%2Fblobs%2Ftoc.json) 下载工具；在 Windows 上将 `azcopy.exe` 所在目录加入 `PATH`。
2. 面向 Azure 中国云登录，并按提示在浏览器中输入设备代码：

   ```bash
   azcopy login --aad-endpoint https://login.partner.microsoftonline.cn
   ```

### 在存储账户之间复制

参考：[使用 AzCopy 在存储账户之间复制 Blob](https://docs.azure.cn/zh-cn/storage/common/storage-use-azcopy-blobs-copy?toc=/storage/blobs/toc.json)。

```bash
azcopy copy "<源 URL>" "<目标 URL>"
```

实际 URL 和授权方式取决于源、目标账户的设置；使用 Microsoft Entra ID 时，应确认身份在两侧具有所需权限。

### 性能与内存

参考：[优化 AzCopy 性能](https://docs.azure.cn/zh-cn/storage/common/storage-use-azcopy-optimize)。

#### 调整并发请求数

可通过环境变量 `AZCOPY_CONCURRENCY_VALUE` 设置并发请求数；具体值应结合基准测试和环境资源调整。原笔记还保留了通过命令查看设置的截图：

![AzCopy 并发设置示例](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301658301.png)

PowerShell 示例：

```powershell
$env:AZCOPY_CONCURRENCY_VALUE = 3
```

#### 减少同步时的资源开销

`azcopy sync` 会先扫描并比较源、目标。如果只需复制新增或更新的文件、无需删除目标中多余的文件，可使用 `copy --overwrite=ifSourceNewer`，减少预扫描开销：

```bash
azcopy copy "<源 URL>" "<目标 URL>" --overwrite=ifSourceNewer --recursive
```

如果需要删除目标中源端已不存在的文件，使用 `azcopy sync` 并按需要设置 `--delete-destination`。上传或下载时还可通过 `AZCOPY_BUFFER_GB` 调整缓冲区内存；该变量不严格限制 AzCopy 的总内存用量。

参考：[AzCopy sync 命令](https://learn.microsoft.com/en-us/azure/storage/common/storage-ref-azcopy-sync)、[优化 AzCopy 性能](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-optimize)。
