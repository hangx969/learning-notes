# docker pull配置代理

## 背景

关于 docker 配置代理服务器的 [官方文档](https://docs.docker.com/network/proxy/#configure-the-docker-client) ：

> If your container needs to use an HTTP, HTTPS, or FTP proxy server, you can configure it in different ways: Configure the Docker client On the Docker client, create or edit the file ~/.docker/config.json in the home directory of the user that starts containers. 
>
> ...
>
> When you create or start new containers, the environment variables are set automatically within the container.

文档意思是：如果你的 **容器** 需要使用代理服务器，那么可以以如下方式配置： 在运行容器的用户 home 目录下，配置 `~/.docker/config.json` 文件。重新启动容器后，这些环境变量将自动设置进容器，从而容器内的进程可以使用代理服务。

所以这篇文章是讲如何配置运行 容器 的环境，与如何拉取镜像无关。如果按照这篇文档的指导，如同南辕北辙。

## 环境变量

常规的命令行程序如果要使用代理，需要设置两个环境变量：`HTTP_PROXY` 和 `HTTPS_PROXY` 。但是仅仅这样设置环境变量，也不能让 docker 成功拉取镜像。

因为镜像的拉取和管理都是 docker daemon 的职责，所以我们要让 docker daemon 知道代理服务器的存在。而 docker daemon 是由 systemd 管理的，所以我们要从 systemd 配置入手。

## 配置方法

> The Docker daemon uses the HTTP_PROXY, HTTPS_PROXY, and NO_PROXY environmental variables in its start-up environment to configure HTTP or HTTPS proxy behavior. You cannot configure these environment variables using the daemon.json file.
>
> This example overrides the default docker.service file.
>
> If you are behind an HTTP or HTTPS proxy server, for example in corporate settings, you need to add this configuration in the Docker systemd service file.

这段话的意思是，docker daemon 使用 `HTTP_PROXY`, `HTTPS_PROXY`, 和 `NO_PROXY` 三个环境变量配置代理服务器，但是你需要在 systemd 的文件里配置环境变量，而不能配置在 `daemon.json` 里。参考：[官方文档](https://docs.docker.com/config/daemon/systemd/#httphttps-proxy)。

1. 查找docker.service文件位置

   ~~~sh
   systemctl status docker.service
   #Loaded行会显示docker.service的路径
   ~~~

2. 编辑docker.service文件，在[Service]部分添加代理环境变量

   ~~~sh
   sudo vim /lib/systemd/system/docker.service
   [Service]
   Environment="HTTP_PROXY=http://127.0.0.1:7890/"
   Environment="HTTPS_PROXY=http://127.0.0.1:7890/"
   ~~~

3. 重启docker

   ~~~sh
   sudo systemctl daemon-reload
   sudo systemctl restart docker.service
   ~~~

4. 检查环境变量

   ~~~sh
   sudo systemctl show --property=Environment docker
   ~~~

   

