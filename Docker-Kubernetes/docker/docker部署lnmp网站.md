# LNMP

- LNMP指的是Linux、Nginx、MySQL和PHP的组合，通常用于搭建和运行网站。

# 安装docker-compose

## 关闭selinux和防火墙

~~~sh
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
reboot -f
#关闭防火墙
systemctl stop firewalld ; systemctl disable firewalld
~~~

## 时间同步

~~~sh
yum install ntpdate -y
ntpdate cn.pool.ntp.org
crontab -e
* */1 * * * /usr/sbin/ntpdate   cn.pool.ntp.org
~~~

## 安装基础软件包

~~~sh
yum install -y yum-utils device-mapper-persistent-data lvm2 wget net-tools nfs-utils lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel epel-release openssh-server socat  ipvsadm conntrack ntpdate telnet ipvsadm
~~~

## 修改内核参数

~~~sh
modprobe br_netfilter
cat > /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl -p /etc/sysctl.d/k8s.conf
~~~

## 配置yum源

~~~sh
#上传kubernetes.repo到/etc/yum.repos.d/目录中
#添加docker在线源
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
~~~

## 启动docker

```sh
yum install docker-ce docker-compose -y
systemctl start docker && systemctl enable docker.service
```

# 准备镜像

~~~sh
#上传mysql、nginx、php镜像
docker load -i nginx.tar.gz
docker load -i mysql.tar.gz
docker load -i php.tar.gz
~~~

> docker-compose常用的命令
>
> ```sh
> #启动并后台运行所有的服务 
> docker-compose up -d 
> #列出项目中目前的所有容器 
> docker-compose ps 
> #停止某个服务 
> docker-compose stop 
> #启动某个服务 
> docker-compose start 
> #停止并删除容器、网络、卷、镜像 
> docker-compose down               
> ```

# docker-compose部署lnmp

## 准备nginx配置文件

~~~sh
# nginx挂载目录
mkdir /root/lnmp && cd /root/lnmp && mkdir nginx && cd nginx && mkdir conf && cd conf
# nginx默认配置文件
tee default.conf <<'EOF'
server {
    listen       80;
    root   /usr/share/nginx/html;
    index   index.html index.htm index.php;


    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

    location / {
        index  index.html index.htm index.php ;
        try_files $uri $uri/ /index.php?$query_string;
        autoindex  on;
    }

    location ~ \.php$ {
        #php73是容器命名
        fastcgi_pass   php73:9000;
        fastcgi_index  index.php;
        include        fastcgi_params;
        fastcgi_param  PATH_INFO $fastcgi_path_info;
        fastcgi_param  SCRIPT_FILENAME  /var/www/html/$fastcgi_script_name;
    }

}
EOF
~~~

## docker-compose yml文件

~~~yaml
cd /root/lnmp/
tee docker-compose.yml <<'EOF'
#定义docker compose yml版本
version: "3"  
#定义我们的服务对象
services:   
#自定义的服务名称
  nginx:    
     #镜像名称，默认拉取本地镜像，没有的话从远程获取
     image: nginx:latest
     #自定义容器的名称
     container_name: c_nginx
     #将宿主机的80端口映射到容器的80端口
     ports:
      - "80:80"
     #将宿主机的~/lnmp/www目录和容器的/usr/share/nginx/html目录进行绑定，并设置rw权限
     #将宿主机的~/lnmp/nginx/conf/default.conf和容器的/etc/nginx/conf.d/default.conf进行绑定
     volumes:
      - ~/lnmp/www/:/usr/share/nginx/html/:rw
      - ~/lnmp/nginx/conf/default.conf:/etc/nginx/conf.d/default.conf
     #设置环境变量，当前的时区
     environment:
      TZ: "Asia/Shanghai"
     #容器是否随docker服务启动重启
     restart: always
     #容器加入名为lnmp的网络
     networks:
      - lnmp
  php:
    image: php:7.3.29-fpm
    container_name: php73
    volumes:
      - ~/lnmp/www/:/var/www/html/:rw
    restart: always
    cap_add:
      - SYS_PTRACE
    networks:
      - lnmp

  mysql:
    image: mysql:5.6
    container_name: mysql56
    ports:
      - "3306:3306"
    volumes:
      - ~/lnmp/mysql/data:/var/lib/mysql/:rw
    restart: always
    networks:
      - lnmp
    environment:
      MYSQL_ROOT_PASSWORD: "123456"
      TZ: "Asia/Shanghai"
networks:   
  #创建了一个自定义的网络叫做lnmp
   lnmp:
EOF

#基于docker-compose启动容器
docker-compose up -d
~~~

## 测试网站主页

~~~sh
cd /root/lnmp/www/
echo "hello,welcome to study" > index.html
#浏览器访问docker-compose机器ip:
http://192.168.40.200/
~~~

## 测试php服务

~~~sh
tee aa.php <<'EOF' 
<?php
  phpinfo();
?>
EOF
#浏览器访问docker-compose机器ip:
http://192.168.40.186/aa.php
~~~

## 连接mysql

~~~sh
#安装了 `pdo`、`pdo_mysql` 和 `mysqli` 这三个扩展，这些扩展通常用于 PHP 与 MySQL 数据库进行交互。
docker exec -it php73 /bin/bash
docker-php-ext-install pdo pdo_mysql mysqli
docker-php-ext-enable pdo pdo_mysql mysqli
exit
#重启docker-compose
cd /root/lnmp/
docker-compose restart

#通过php脚本连接数据库
cd /root/lnmp/www/
tee mysql.php <<'EOF'
<?php
// 创建连接
$conn = new mysqli('mysql56','root','123456');
if($conn->connect_error){
    die("连接失败，错误:" . $conn->connect_error);
}
echo "mysql连接成功";
EOF

#浏览器访问docker-compose机器ip：
http://192.168.40.186/mysql.php
~~~

