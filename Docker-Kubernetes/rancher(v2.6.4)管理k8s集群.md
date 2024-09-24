# Rancher介绍

- Rancher是一个开源的企业级多集群Kubernetes管理平台，实现了Kubernetes集群在混合云+本地数据中心的集中部署与管理，以确保集群的安全性，加速企业数字化转型。

- Rancher官方文档：https://docs.rancher.cn/

- Rancher和k8s的区别
  - Rancher和k8s都是用来作为容器的调度与编排系统。但是rancher不仅能够管理应用容器，更重要的一点是能够管理k8s集群。Rancher2.x底层基于k8s调度引擎，通过Rancher的封装，用户可以在不熟悉k8s概念的情况下轻松的通过Rancher来部署容器到k8s集群当中。

## rancher优势

- 容器管理：Rancher 支持 Kubernetes，允许用户通过 Web 界面集中管理多个k8s集群。它允许用户通过简单的几步就能够部署k8s资源
- 多云支持：Rancher 提供了对多个云提供商的支持，如 AWS、Azure、Google Cloud 等，使用户能够在不同云平台之间轻松迁移容器工作负载。
- 高可用性：Rancher 可以配置为高可用模式，确保平台本身的稳定性和容错性。这意味着即使在某些节点失败的情况下，Rancher     仍然可以继续运行并提供服务。
- 安全性：Rancher 提供了多层级的安全特性，包括用户认证、访问控制、镜像安全扫描等，帮助用户保护容器化应用程序的安全。
- 资源管理：Rancher 允许用户对容器集群中的资源进行管理和调整，以确保应用程序的性能和稳定性。

- 应用商店：Rancher 提供了应用商店（Catalog）功能，允许用户浏览和安装预定义的应用程序模板，简化了应用程序部署的过程。

# Rancher部署

## 实验机器准备

- Rancher VM
  - 192.168.40.138；hostname：rancher；memory：6G；cpu：6vCPU

- K8S VM
  - version：1.23.1
  - master1：192.168.40.180
  - node1：192.168.40.181

## 安装前准备

### 配置主机名

~~~sh
#配置主机名
hostnamectl set-hostname rancher && bash
#rancher、master1、node1添加host
tee -a /etc/hosts << 'EOF'
192.168.40.180   master1
192.168.40.181   node1
192.168.40.138   rancher
EOF
~~~

### 配置ssh互信

~~~sh
ssh-keygen
ssh-copy-id -i ~/.ssh/id_rsa.pub master1 #node1 rancher
~~~

### 关闭防火墙

~~~sh
systemctl stop firewalld && systemctl disable firewalld
~~~

### 关闭selinux

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
~~~

### 关闭交换分区

~~~sh
swapoff -a
vim /etc/fstab
#注释掉swap部分
~~~

### 修改内核参数

~~~sh
#br_netfilter模块用于将桥接流量转发至iptables链，br_netfilter内核参数需要开启转发。
modprobe br_netfilter
echo "modprobe br_netfilter" >> /etc/profile
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl -p /etc/sysctl.d/k8s.conf
~~~

> ~~~sh
> cat > /etc/sysctl.d/k8s.conf <<EOF
> ...
> EOF
> ~~~
>
> - 这种方式也可以将两个EOF之间的内容写到文件中，与tee的区别是不会将内容输出到屏幕上
> - `cat > file` 也会覆盖文件的内容。如果你希望将内容追加到文件的末尾，你可以使用 `>>` 运算符，如 `cat >> file`

### 添加阿里云docker源

~~~sh
yum install -y yum-utils
mv /etc/yum.repos.d/CentOS-Base.repo  /etc/yum.repos.d/CentOS-Base.repo.backup
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
~~~

### 安装常用软件包

~~~sh
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate 
~~~

### 时间同步

~~~sh
#跟网络时间做同步
ntpdate cn.pool.ntp.org
#把时间同步做成计划任务
crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
#重启crond服务
service crond restart
~~~

## 安装docker

- 安装启动docker

~~~sh
yum install docker-ce docker-ce-cli containerd.io -y
systemctl start docker && systemctl enable docker.service
~~~

- 修改配置文件

~~~sh
tee /etc/docker/daemon.json << 'EOF'
{
"registry-mirrors":["https://rsbud4vc.mirror.aliyuncs.com","https://registry.docker-cn.com","https://docker.mirrors.ustc.edu.cn","https://dockerhub.azk8s.cn","http://hub-mirror.c.163.com","http://qtid6917.mirror.aliyuncs.com", "https://rncxm540.mirror.aliyuncs.com"],
"exec-opts": ["native.cgroupdriver=systemd"]
} 
EOF
~~~

> - `tee /etc/docker/daemon.json`：`tee` 命令会将输入的内容同时写入到指定的文件（这里是 `/etc/docker/daemon.json`）和标准输出（通常是屏幕）。
>
> - `<< 'EOF'` 和 `EOF`：这是 shell 中的 "here document" 技术，它允许你直接在命令行中输入多行文本。这个文本会被当作前面命令的输入。在 `<< 'EOF'` 和 `EOF` 之间的所有内容都会被当作输入的内容。
>
> - `tee` 命令默认会覆盖目标文件的内容。如果希望将内容追加到文件的末尾，可以使用 `-a` 或 `--append`
>
>   ~~~sh
>   tee -a /etc/docker/daemon.json << 'EOF'
>   {
>   ...
>   } 
>   EOF
>   ~~~

- 重启docker

~~~sh
systemctl daemon-reload
systemctl restart docker
systemctl status docker
~~~

## 安装rancher

~~~sh
#Rancher2.6.4支持导入已经存在的k8s1.23+集群，所以我们安装rancher2.6.4版本
#上传rancher_2.6.4.tar.gz和rancher-agent_2.6.4.tar.gz镜像包
#在master1和node1上解压agent包，在rancher上解压rancher包
docker load -i rancher-agent_2.6.4.tar.gz
docker load -i rancher_2.6.4.tar.gz
#rancher VM上启动服务
docker run -d --restart=unless-stopped -p 80:80 -p 443:443 --privileged rancher/rancher:v2.6.4
#注：unless-stopped，在容器退出时总是重启容器，除非是用户指定去停止容器。
~~~

- 浏览器访问rancher主机地址192.168.40.138

- 获取bootstrap password

~~~sh
docker ps #获取container ID
docker logs 8708d5cbcb25 2>&1 | grep "Bootstrap"
#2>&1：这是一个 Shell 命令，用于将标准错误（2）重定向到标准输出（1）。这样，无论日志条目是写入标准输出还是标准错误，都可以被后续的命令处理。
#vjvnhwxfxpc45gmg695r6rr9cs4twx5rck2c7bjtsp6f8zvzzw5plv
~~~

- 登录rancher
  - 使用本地用户登录，设置密码（u:admin,p:azsxdcfvgbhn）

## 通过rancher管理k8s集群

### 导入集群

- 导入已有集群 - 通用 - 输入集群名称 - 创建

- 复制显示的导入命令

  ~~~sh
  curl --insecure -sfL https://192.168.40.138/v3/import/kqvbv89b8vfvsp4vkwm7f47bw2sdvvd2ftz59tknlnpl8wkzm8wdnv_c-m-ktfx2cm5.yaml | kubectl apply -f -
  ~~~

  > - `--insecure` 选项表示允许 `curl` 连接到使用自签名证书的 HTTPS 站点。`-s` 选项表示静默模式，不输出错误和进度信息。`-f` 选项表示在 HTTP 错误时失败。`-L` 选项表示如果服务器报告了重定向，那么就跟随重定向。
  > - `-f -` 选项表示从标准输入读取 YAML 文件。

- 检查pod运行

  ~~~sh
  kubectl get pods -n cattle-system -o wide
  ~~~

- 访问**https://192.168.40.138/dashboard/home**，检查集群情况

### 创建示例tomcat应用

- web ui创建namespace：tomcat-ns

- 创建deploy
  - ns：tomcat-ns
  - name：tomcat-deploy
  - image：tomcat:8.5.34-jre8-alpine
  - 标签：app=tomcat

- 创建svc
  - NodePort；svc listening port：8080；target port：8080；selector：app=tomcat

- 创建ingress controller

  ~~~sh
  #导入kube-webhook-certgen_1.1.1.tar.gz、nginx-ingress-controller_v1.1.1.tar.gz、ingress-controller.yaml
  docker load -i kube-webhook-certgen_1.1.1.tar.gz
  docker load -i nginx-ingress-controller_v1.1.1.tar.gz
  mkdir ingress
  cd ingress/
  kubectl apply -f ingress-deploy.yaml
  kubectl create clusterrolebinding clusterrolebinding-user-3  --clusterrole=cluster-admin --user=system:serviceaccount:ingress-nginx:ingress-nginx
  kubectl get pods -n ingress-nginx
  ~~~

- 创建ingress规则

  - 域名：hxtomcat.com

  - 查看ingress class的名称`k get ingressclass`

  - 添加annotation：`kubernetes.io/ingress.class：nginx`

  - default backend选tomcat的svc

    ![image-20240224183125148](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402241831296.png)

  - 进到ingress-controller里面查看转发规则是否创建

    ~~~sh
    k exec -it ingress-nginx-controller-56dc9c69b9-mdqf6 -n ingress-nginx -- /bin/bash
    cat /nginx.conf | grep tomcat
    
    set $ingress_name   "ing-tomcat";
                            set $service_name   "svc-tomcat";
                            set $proxy_upstream_name "default-svc-tomcat-8080";
            ## start server hxtomcat.com
                    server_name hxtomcat.com ;
                            set $ingress_name   "ing-tomcat";
                            set $service_name   "svc-tomcat";
                            set $proxy_upstream_name "default-svc-tomcat-8080";
            ## end server hxtomcat.com
    ~~~

- 本地添加域名解析:`C:\Windows\System32\drivers\etc\hosts`

  - IP: ingress的IP，`k get ing -n tomcat-ns`查看
  - 域名：hxtomcat.com

> 问题1：
>
> - windows添加完hosts之后，浏览器访问192.168.40.181可以访问到tomcat主页。说明ingress、ingress controller、svc搭建的没问题。
>
> - 但是用域名访问hxtomcat.com就返回502 bad gateway，抓包看，域名被解析到了127.0.0.1而非192.168.40.181，查阅资料得知可能是运营商DNS劫持。尝试修改为谷歌DNS也不行。问题待解决。

![image-20240224183318326](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202402241833410.png)

> 问题2：不同rancher版本能管理的最高的K8S版本是多少，在官网并没有给出明确说明。。。
