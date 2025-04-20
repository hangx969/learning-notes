# kuboard

- 官网地址：https://www.kuboard.cn/
- 安装kuboard参考：https://www.kuboard.cn/v4/install/

# 部署kuboard

~~~sh
#先安装docker，再下载kuboard_v3安装包。为测试用，直接在master1上部署
docker load -i kuboard_v3.tar.gz
mkdir -p /root/kuboard-data
docker run -d --restart=unless-stopped --name=kuboard -p 10080:80/tcp -p 10081:10081/tcp -e KUBOARD_ENDPOINT="http://172.16.183.100:80" -e KUBOARD_AGENT_SERVER_TCP_PORT="10081" -v /root/kuboard-data:/data  swr.cn-east-2.myhuaweicloud.com/kuboard/kuboard:v3
#eipwork/kuboard:v3
~~~

- 登录

  ![image-20240515210353507](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405152103585.png)

- 添加集群

  ![image-20240515210411323](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405152104374.png)

  ![image-20240515210446282](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405152104336.png)

  ![image-20240515210504187](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405152105248.png)

- 选择认证方式 - service account：kuboard-admin

  ![image-20240515210600968](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202405152106027.png)

# 创建资源

- 创建deploy：[https://kuboard.cn/learning/k8s-basics/deploy-app.html#%E5%AE%9E%E6%88%98-%E9%83%A8%E7%BD%B2-nginx-deployment](https://kuboard.cn/learning/k8s-basics/deploy-app.html#实战-部署-nginx-deployment)

- 创建svc：https://kuboard.cn/learning/k8s-basics/expose.html

