# Jenkins部署使用

Jenkins主节点可以采用Docker、K8s或者war包进行部署。如果K8s中没有安装分布式可靠存储，建议直接采用Docker安装，slave从节点可以在k8s中部署。

## Docker安装jenkins

1. 首先需要一个Linux服务器，配置不低于2C4G和40G硬盘。

2. 装Docker：

~~~sh
# 在rockylinux上：
yum install -y yum-utils device-mapper-persistent-data lvm2 
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo 
yum install docker-ce docker-ce-cli -y 
systemctl daemon-reload && systemctl enable --now docker
~~~

3. 创建Jenkins 的数据目录，防止容器重启后数据丢失：

~~~sh
mkdir /data/jenkins_data -p
chmod -R 777 /data/jenkins_data
~~~

4. **【可选】**如果后面有需求要用到docker slave的话，需要修改宿主机docker.sock权限

~~~sh
chown 1000:1000  /var/run/docker.sock
chmod 777  /var/run/docker.sock
chmod 777 /usr/bin/docker
chown -R 1000.1000  /usr/bin/docker
~~~

5. 启动Jenkins，并配置管理员账号密码为admin/admin123：

- 其中8080端口为Jenkins Web界面的端口，50000是jnlp使用的端口，后期Jenkins Slave需要使用50000端口和Jenkins主节点通信。 
- 把宿主机的docker挂进主节点了，后面如果有需求要用docker slave，将会调用宿主机的docker。

~~~sh
# 用的镜像是：docker.io/bitnami/jenkins:2.504.3-debian-12-r1
docker run -d \
--name=jenkins \
--restart=always \
-e JENKINS_PASSWORD=admin123 \
-e JENKINS_USERNAME=admin \
-e JENKINS_HTTP_PORT_NUMBER=8080 \
-p 8080:8080 \
-p 50000:50000 \
-v /usr/bin/docker:/usr/bin/docker \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /data/jenkins_data:/bitnami/jenkins \
m.daocloud.io/docker.io/bitnami/jenkins:2.504.3-debian-12-r1 
~~~

6. 查看jenkins日志：

~~~sh
docker logs -f jenkins 
# 查看到这条日志说明Jenkins已完成启动 
INFO: Jenkins is fully up and running
~~~

7. 安装完成后可以通过Jenkins宿主机IP:8080端口访问UI界面。admin/admin123。

## 插件安装

进入Manage Jenkins -> Manage Plugins安装需要使用的插件。

1. 首先配置国内插件源：在Advanced Settings里面将Update Site - URL改为国内源：`https://mirrors.huaweicloud.com/jenkins/updates/update-center.json`，点击submit保存

2. 在Available Plugins里面可以看到所有的可用插件，安装这些：

   ~~~sh
   configuration-as-code
   workflow-aggregator # 搜出来名字叫 Pipeline
   Git 
   Git Parameter 
   Git Pipeline for Blue Ocean 
   GitLab 
   Credentials 
   Credentials Binding 
   Blue Ocean 
   Blue Ocean Pipeline Editor 
   Blue Ocean Core JS 
   Web for Blue Ocean 
   Pipeline SCM API for Blue Ocean 
   Dashboard for Blue Ocean 
   Build With Parameters 
   List Git Branches Parameter 
   Pipeline 
   Pipeline: Declarative 
   Kubernetes 
   Kubernetes CLI 
   Kubernetes Credentials 
   Image Tag Parameter 
   Docker 
   Docker Slaves 
   Docker Pipeline 
   Role-based Authorization Strategy
   ~~~

3. 也可以手动重启jenkins：`192.168.49.180:8080/restart`

## Jenkins插件离线安装

1. Jenkins离线插件下载地址:http://mirrors.tuna.tsinghua.edu.cn/jenkins/plugins/，可以在Jenkins官网上搜索想要下载的插件，点击“Download”按钮下载.hpi文件。

2. Jenkins离线插件安装方法：
   1. 方法一：在Jenkins管理页面点几“系统管理” -> “插件管理” -> “高级”。选择“上传插件”，并选择下载的.hpi文件。点击“上传”按钮，等待插件安装完成。
   2. 方法二：将下载的.hpi文件放到Jenkins的安装目录下的“plugins”文件夹中。重启Jenkins，等待插件安装完成。

## Jenkins版本升级

Jenkins 版本升级通常分为以下几个步骤：

1. 备份当前 Jenkins 数据在升级之前，应该备份当前 Jenkins 数据以避免数据丢失。可以通过将 Jenkins 的 JENKINS_HOME 目录复制到其他位置来备份数据。

2. 下载新版本的 Jenkins在官网下载最新版本的 Jenkins war 文件，通常可以在 https://www.jenkins.io/download/ 找到最新版本。

3. 停止当前 Jenkins 实例在进行版本升级之前，需要停止当前运行的 Jenkins 实例。

4. 启动新版本的 Jenkins将下载的新版本 Jenkins war 文件复制到 Jenkins 的安装目录下，并启动 Jenkins。在 Linux 系统中，可以使用以下命令来启动 Jenkins：`java -jar jenkins.war`
5. 升级插件在新版本的 Jenkins 中，有可能需要升级现有插件以保持兼容性。在 Jenkins 管理页面的“插件管理”中，可以检查并升级插件。
6. 验证升级启动新版本的 Jenkins 后，可以通过访问 Jenkins Web 界面来验证升级是否成功，并确保所有插件和功能正常工作。