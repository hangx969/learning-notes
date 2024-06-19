# 安装JDK11

~~~sh
#Jenkins是Java编写的，所以需要先安装JDK11，这里采用yum安装，如果对版本有需求，可以直接在Oracle官网下载JDK。
yum install java-11-openjdk* -y
#安装jenkins 2.319，需要的jdk版本是11，所以需要切换jdk版本
alternatives --config java
#选择jdk11的版本
rm -rf /usr/bin/java
ln -s /usr/lib/jvm/java-11-openjdk-11.0.16.1.1-1.el7_9.x86_64/bin/java /usr/bin/java
~~~

# 安装Jenkins

~~~sh
#离线安装
wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins.io/redhat/jenkins.repo --no-check-certificate
yum install jenkins-2.319-1.1.noarch.rpm -y
#在线安装
yum install jenkins-2.319 –y
#要是报错执行如下命令：
rpm --import http://pkg.jenkins.io/redhat/jenkins.io.key
~~~

~~~sh
#修改jenkins配置文件
vim /etc/sysconfig/jenkins
#改：31 JENKINS_USER="jenkins"
#为：31 JENKINS_USER="root" 
#改：58 JENKINS_PORT="8080"
#为：58 JENKINS_PORT="198"
systemctl restart jenkins 
systemctl enable jenkins
~~~

# 访问jenkins

- 访问jenkins机器ip:198登录jenkins
- 自动升级jenkins到最新版本，如果不升级到最新版，好多插件无法安装，升级之后在页面重启jenkins即可：http://192.168.40.186:198/restart

# 内网环境安装jenkins离线插件

- 离线插件安装地址
  - http://mirrors.tuna.tsinghua.edu.cn/jenkins/plugins/
  - http://updates.jenkins-ci.org/download/plugins/
  - 可以在Jenkins官网上搜索想要下载的插件，点击“Download”按钮下载.hpi文件。
- Jenkins离线插件安装方法：
  1. 方法一：
  1.在Jenkins管理页面点几“系统管理” -> “插件管理” -> “高级”。
  2.选择“上传插件”，并选择下载的.hpi文件。
  3.点击“上传”按钮，等待插件安装完成。
  2. 方法二：
  1.将下载的.hpi文件放到Jenkins的安装目录下的“plugins”文件夹中。
  2.重启Jenkins，等待插件安装完成。

# jenkins连接k8s集群

1. 配置kubernetes plugin连接kubernetes集群
   - 点击系统管理->系统设置-添加一个云,在下拉菜单中选择kubernets并添加。注：Name值任意添加，Kubernetes URL值添加K8S apiserver连接地址和端口
2. 配置云kubernetes连接K8S集群的验证文件
   - 获取K8S的/root/.kube/config文件：`cat ~/.kube/config`
   - 获取 /home/hanxianchao/.kube/config中certificate-authority-data的内容并转化成base64 encoded文件:`ecbo xxxx | base64 -d > /opt/crt/ca.crt`
   - 将ca.crt的内容填写到jenkins kubernetes的Kubernetes server certificate key栏中
   - 获取 ~/.kube/config中client-certificate-data和client-key-data的内容并转化成base64 encoded文件:
     - `echo xxxx  | base64 -d > /opt/crt/client.crt`
     - `echo xxx | base64 -d > /opt/crt/client.key`

3. 生产Client P12认证文件cert.pfx，并下载至本地
   - `openssl pkcs12 -export -out /opt/crt/cert.pfx -inkey /opt/crt/client.key -in /opt/crt/client.crt -certfile /opt/crt/ca.crt` (password需要自定义并牢记)
4. 在jenkins-云k8s中添加凭证（注：Upload certificate上次刚生成并下载至本地的cert.pfx文件，Password值添加生成cert.pfx文件时输入的密钥）

![image-20240619212217567](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202406192122634.png)

5. 测试连接kubernetes集群（**注：**Kubernetes Namespace值添加~/.kube/config文件中cluster部分中name的内容）

   ![image-20240619212409671](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202406192124714.png)
