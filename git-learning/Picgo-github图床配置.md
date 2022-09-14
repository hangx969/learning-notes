# Picogo-github图床配置

## 背景

- 用typora编辑的Markdown文件中的图片通常是保存在本地路径下，更换电脑或者文件移动后，图片容易挂掉。
- 利用Picgo将typora中的图片自动上传至github，实现图片持久化。

## 配置方法

github、picgo、typora都需要配置。

### github配置

- 创建一个公有仓库，用于存放图片

  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111314538.png" alt="image-20220911131456460" style="zoom:50%;" />

- 获取access token

  - settings - developer settings - Personal access tokens
  - 用于让picgo自动上传至仓库。

  - 生成之后需要手动复制到本地，因为之后该token就不可见了。

  ![image-20220911131547101](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111315144.png)

### Picgo配置

- 下载：[PicGo (molunerfinn.com)](https://molunerfinn.com/PicGo/)

- 注意：Picgo的插件需要Node.js，[Node.js (nodejs.org)](https://nodejs.org/en/)

- 安装github-plus插件

  ![image-20220911132003628](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111320685.png)

- 配置图床设置

  - 注意repo的路径中不能有空格！

  - branch要填main而非master

  - token填github复制出来的的access token

  ![image-20220911132056970](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111320007.png)

- 配置Picgo：

  - Picgo相当于一个http server让typora将图片文件上传，Server的监听端口需要与typora中的配置一致。

  ![image-20220911132334774](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111323821.png)

  - 设置中打开时间戳重命名

  ![image-20220911132544225](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111325254.png)

  ### Typora配置

  偏好设置 - 图像：

  ![image-20220911132923566](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111329625.png)

  可点击验证图片选项，测试上传是否能成功。

### Troubleshooting

根据我配置中遇到的报错经验：

- Picgo设置中的repo路径有空格，会导致404报错。
- Picgo设置中的时间戳命名如果没开的话，会导致文件名重复，typora上传失败，picgo日志中会有detect second instance信息。

- typora中图片上传成功，但是typora中不显示。可能是github图片被屏蔽；解决办法是修改host文件(C:\Windows\System32\drivers\etc\hosts)，加上：

  ```shell
  185.199.108.133 raw.githubusercontent.com
  185.199.109.133 raw.githubusercontent.com
  185.199.110.133 raw.githubusercontent.com
  185.199.111.133 raw.githubusercontent.com
  ```

  