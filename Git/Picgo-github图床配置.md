---
title: PicGo-GitHub 图床配置
tags:
  - git
  - github
  - picgo
  - typora
aliases:
  - PicGo图床配置
  - GitHub图床
---

# PicGo-GitHub 图床配置

## 背景

Typora 中使用本地路径引用图片时，换电脑或移动文件后，图片可能无法显示。可以通过 PicGo 将图片上传到 GitHub 图床，再在 Markdown 中引用远程图片地址。

## 配置流程

依次配置 GitHub 图片仓库、PicGo 和编辑器。

### 1. 配置 GitHub 图片仓库

1. 创建用于存放图片的公开仓库。

   <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111314538.png" alt="image-20220911131456460" style="zoom:50%;" />

2. 在 GitHub 的 **Settings → Developer settings → Personal access tokens** 中创建访问令牌，供 PicGo 上传图片。令牌应仅授予目标仓库所需的权限，并妥善保存；创建后无法再次查看完整令牌。

   ![image-20220911131547101](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111315144.png)

### 2. 配置 PicGo

1. [下载 PicGo](https://molunerfinn.com/PicGo/)。安装插件前，先安装 [Node.js](https://nodejs.org/en/)。
2. 安装 `github-plus` 插件。

   ![image-20220911132003628](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111320685.png)

3. 配置图床：

   - `repo`：填写仓库路径，避免加入空格。
   - `branch`：填写图片仓库实际使用的分支名；图示仓库使用 `main`。
   - `token`：填写上一步创建的 GitHub 访问令牌。

   ![image-20220911132056970](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111320007.png)

4. 在 PicGo 中配置上传服务，并记下监听端口。Typora 中填写的端口必须与这里一致。

   ![image-20220911132334774](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111323821.png)

5. 开启时间戳重命名，以减少图片文件名重复。

   ![image-20220911132544225](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111325254.png)

### 3. 配置 Typora

打开 **偏好设置 → 图像**，按图配置 PicGo 上传，并使用图片验证功能测试上传。

![image-20220911132923566](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111329625.png)

### 4. 配置 Obsidian

安装 Image auto upload 插件，按插件设置填写 GitHub 仓库、令牌和 PicGo 监听端口。配置完成后，可在粘贴图片时自动上传。

## 排查问题

> [!warning] 上传失败
> - `repo` 路径中有空格时，可能出现 404 错误。
> - 图片文件名重复可能导致上传失败；可以检查 PicGo 日志，并开启时间戳重命名。
> - 如果日志提示 `detect second instance`，应先检查是否同时运行了多个 PicGo 实例；此提示本身不能证明是文件名重复。

> [!tip] 上传成功但 Typora 不显示图片
> 先在浏览器中直接打开图片 URL，确认地址可访问，再检查本机网络和 DNS。不要将固定的 GitHub IP 地址长期写入 `hosts` 文件；这些地址可能变化。
