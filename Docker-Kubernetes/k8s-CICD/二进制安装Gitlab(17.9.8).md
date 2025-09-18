# 部署

GitLab 在企业内经常用于代码的版本控制，也是DevOps平台中尤为重要的一个工具。

接下来在另一台服务器（4C/4G/40G以上）上安装GitLab（如果已有可用的GitLab，也可无需安装）。

1. 首先在 GitLab 国内源下载 GitLab 的安装包：https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el9/gitlab-ce-17.9.8-ce.0.el9.x86_64.rpm。

2. 关闭机器防火墙和selinux：

   ~~~sh
   setenforce 0 
   systemctl disable --now firewalld 
   vim /etc/sysconfig/selinux 
   # 改为SELINUX=disabled
   ~~~

3. 将下载后的rpm包上传到服务器，通过yum直接安装即可：

   ~~~sh
   yum install gitlab-ce-17.9.8-ce.0.el9.x86_64.rpm -y 
   ~~~

4. 更改配置：

   ~~~sh
   vim /etc/gitlab/gitlab.rb
   # 将external_url改成自己的发布地址，可以是服务器IP，也可以是可被解析的域名
   # 大部分情况下已经有了prometheus监控平台，所以自带的Prometheus可以无需安装，后期可以安装Gitlab exporter进行监控。所以关闭prometheus插件：prometheus['enable'] = false
   
   # 更新配置之后需要重新加载配置文件
   gitlab-ctl reconfigure
   ~~~

5. 之后可以通过浏览器访问GitLab，账号root，默认密码在`/etc/gitlab/initial_root_password`

6. 登录后，在Admin - General - Import and export settings里面开启import功能（勾上Github、Repository by URL、Gitlab export三项），可以从外部仓库导入代码到Gitlab。点击save changes保存配置。

# 使用

1. 首先可以创建一个组：Groups - Create Group
2. 在组内创建一个Project - Create blank project - 输入项目名称 创建

# 连接Jenkins

1. Jenkins服务器上生成ssh key(如果有可以无需生成）

~~~sh
ssh-keygen -t rsa -C "123456@xxx.com"
~~~

~~~sh
cat ~/.ssh/id_rsa.pub 
~~~

2. 将Jenkins服务器的key导入到Gitlab：Gitlab右上角 - Edit Profile - SSH Keys - Add new key，把id_rsa.pub放进去

   - Title填邮箱
   - Usage type填Authentication & Singing
   - Expiration Date可以设置一个

3. 然后就可以在Jenkins服务器上拉取Gitlab的代码：

   ~~~sh
   yum install git -y 
   git config --global user.email 123456@xx.com 
   git config --global user.name "hangx" 
   git clone git@<gitlab IP>:<group name>/<project namea>.git 
   ~~~

4. 提交码代码测试：

   ~~~sh
   echo "# Frist Commit For DevOps" > first.md
   git add .
   git commit -am "first commit"
   git push origin main
   ~~~

   
