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
date: 2026-04-16
---

# Command Line Tools

> [!summary] Azure command-line tools for managing resources and data
> Covers ==Azure PowerShell==, ==Az CLI==, and ==AzCopy== for managing [[Azure/5_Azure-Storage|Azure Storage]] and other Azure resources.

---

## Azure PowerShell

### 介绍

- PowerShell 是跨平台自动化任务解决方案，作为脚本语言，用于自动化系统管理；还用于自动化部署、测试解决方案；输入输出均为 ==.NET 对象==
- Azure PowerShell 是一组 ==cmdlet==（轻量级命令），用于直接从 PowerShell 管理 Azure 资源

### 安装

- [Introducing the Azure Az PowerShell module | Microsoft Docs](https://docs.microsoft.com/en-us/powershell/azure/new-azureps-module-az?view=azps-7.3.2)
- [Install the Azure Az PowerShell module | Microsoft Learn](https://learn.microsoft.com/en-us/powershell/azure/install-az-ps?view=azps-9.4.0)

> [!info] 通过 PowerShellGet 安装 Azure PowerShell
> 要求：
> - Windows PowerShell ==5.1== or more
> - .NET Framework ==4.7.2== or more
> - 要先安装最新版本的 PowerShellGet

- 安装 PowerShellGet：

  ```powershell
  Install-Module -Name PowerShellGet -Force
  ```

- 从 Windows PowerShell 上安装：

  ```powershell
  Install-Module -Name Az -Scope AllUsers -Repository PSGallery -Force
  ```

### 登录

- 对于 ==Azure China Cloud==，使用：

  ```powershell
  Connect-AzAccount -Environment AzureChinaCloud
  ```

#### 便捷登录 Tips

> [!tip] 使用 AAD App 自动登录
> - 建一个 AAD 的 app，new 一个 ==client secret==
> - 在 PowerShell 里面写一个登录脚本，做一个 credential，用这个 app 的 client secret 来登录

![image-20231030164620380](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301646534.png)

### AzPowerShell 清除缓存

> [!warning] 清除缓存
> `msal.cache` 里面存了 token，清缓存可以手动删除以下文件：

Remove all of these files:

- `C:\Users\<yourname>\.azure\AzureRmContext.json`
- `C:\Users\<yourname>\.azure\AzureRmContextSettings.json`
- `C:\Users\<yourname>\.azure\AzureRmSurvey.json`
- `C:\Users\<yourname>\.azure\keystore.cache`
- `C:\Users\<yourname>\AppData\Local\.IdentityService\msal.cache`

---

## Az CLI

- Tool for managing Azure resources, text-based, designed for efficiency.
- CLI 是基于 ==Python== 的。

### 安装

- Install in Windows: [安装适用于 Windows 的 Azure CLI | Azure Docs](https://docs.azure.cn/zh-cn/cli/install-azure-cli-windows?view=azure-cli-latest&tabs=azure-cli)

- Install in Linux: [Install the Azure CLI on Linux | Microsoft Docs](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-linux?pivots=dnf)

  ```bash
  sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
  echo -e "[azure-cli]
  name=Azure CLI
  baseurl=https://packages.microsoft.com/yumrepos/azure-cli
  enabled=1
  gpgcheck=1
  gpgkey=https://packages.microsoft.com/keys/microsoft.asc" | sudo tee /etc/yum.repos.d/azure-cli.repo
  yum install -y dnf
  sudo dnf install azure-cli
  ```

### 登录

```bash
az cloud set -n AzureChinaCloud
az login
```

> [!warning] 登录报错排查
> <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301652604.png" alt="image-20231030165207511" style="zoom:50%;" />
>
> - 有可能是 ==account credential cache== 的问题：[`az login` fails: OSError: \[WinError -2146893813\] · Issue #20231 · Azure/azure-cli · GitHub](https://github.com/Azure/azure-cli/issues/20231#issuecomment-1007176901)
> - 尝试：`az account clear`

### 订阅管理

[How to manage Azure subscriptions – Azure CLI | Microsoft Learn](https://learn.microsoft.com/en-us/cli/azure/manage-azure-subscriptions-azure-cli#change-the-active-tenant)

```bash
#先用user登录：
az login --user hangx@mcpod.partner.onmschina.cn --password
#再切换sub：
az account set --subscription 9ef8a15c-15a2-4ef1-a19b-e31876ab177
```

---

## AzCopy

> [!info] AzCopy 概述
> Perform copy and sync operations with AzCopy between local and Azure or different storage accounts.
> ==注意：azcopy 使用的是服务器到服务器 Azure backbone 的 API，不占用本地网络带宽。==

### 安装与登录

- 安装：
  - [使用 AzCopy v10 将数据复制或移到 Azure 存储 | Azure Docs](https://docs.azure.cn/zh-cn/storage/common/storage-use-azcopy-v10?toc=%2Fstorage%2Fblobs%2Ftoc.json)
  - 下载 AzCopy 安装包，把 `azcopy.exe` 路径添加到系统路径。

- 登录：

  ```bash
  azcopy login --aad-endpoint https://login.partner.microsoftonline.cn
  #打开给定的web，输入给定的device code
  ```

### 用法

#### 从不同的存储账户之间 Copy

- [使用 AzCopy v10 在 Azure 存储帐户之间复制 Blob | Azure Docs](https://docs.azure.cn/zh-cn/storage/common/storage-use-azcopy-blobs-copy?toc=/storage/blobs/toc.json)
- `azcopy copy "源URL" "目的URL"`

### 性能优化

[通过 Azure 存储优化 AzCopy v10 的性能 | Azure Docs](https://docs.azure.cn/zh-cn/storage/common/storage-use-azcopy-optimize)

#### 设置并发数

- 通过 azcopy 命令设置：

  ![image-20231030165855197](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202310301658301.png)

- 通过 PowerShell 设置：

  ```powershell
  $env:AZCOPY_CONCURRENCY_VALUE=3
  ```

#### AzCopy Sync 降低内存使用

[azcopy sync | Microsoft Learn](https://nam06.safelinks.protection.outlook.com/?url=https%3A%2F%2Flearn.microsoft.com%2Fen-us%2Fazure%2Fstorage%2Fcommon%2Fstorage-ref-azcopy-sync%23guidelines&data=05|01|hangx@microsoft.com|b4d7a41178ef42d4a42108db5c3742c4|72f988bf86f141af91ab2d7cd011db47|1|0|638205164739901027|Unknown|TWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D|3000|||&sdata=bKeG0cy5j3QZgRETHDMHwDZkaHpqZKFyrUoxSRLdzmc%3D&reserved=0)

```bash
azcopy copy –overwrite=ifSourceNewer
```
