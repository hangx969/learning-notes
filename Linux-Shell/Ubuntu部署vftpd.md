# FTP和vftpd介绍

## vftpd

- vsftpd（very secure FTP daemon）是Linux下的一款小巧轻快、安全易用的FTP服务器软件。本教程介绍如何在Linux实例上安装并配置vsftpd。

## FTP

### 工作模式

- FTP（File Transfer Protocol）是一种文件传输协议，基于客户端/服务器架构。用户通过一个支持FTP协议的客户机程序，连接到在远程主机上的FTP服务器程序。用户通过客户机程序向服务器程序发出命令，服务器程序执行用户所发出的命令，并将执行的结果返回到客户机。

- 支持以下两种工作模式：

  - 主动模式：客户端向FTP服务器发送端口信息，由**服务器主动连接**该端口。
    - 主动模式的工作顺序：
      \- Client先和Server通过21端口建立连接；
      \- Client向Server发送指令，指令中包含了Client要通过 N 号端口来传输什么数据；
      \- Server打开自己的20端口，去 **主动连接** Client的 N 号端口来传输数据

  - 被动模式：FTP服务器开启并发送端口信息给客户端，由**客户端连接该端口**，服务器被动接受连接。
    - 建立连接的方式和主动模式相同；
    - 建立连接后，与主动方式不同，Client不会提交PORT命令并允许Server来回连它的数据端口，而是提交PASV命令。
    - Server会开启一个任意的非特权端口（P > 1024），并发送PORT P命令给Client。
    - Client发起从本地端口到Server的端口 P 的连接用来传送数据。

- 说明：大多数FTP客户端都在局域网中，没有独立的公网IP地址，且有防火墙阻拦，主动模式下FTP服务器企图与客户端的高位随机端口建立连接，而这个端口很有可能被客户端的防火墙阻塞掉。因此，如无特殊需求，建议您将FTP服务器配置为被动模式。

### TCP连接机制

- FTP会话属于复合TCP连接，主动模式中开放20和21端口。
  - 控制连接： TCP port 21 ，负责发送FTP的命令信息（比如说登陆的指定，用户名和密码等）。
  - 数据连接： TCP port 20 ，负责上传/下载数据。

### 认证模式

- 匿名用户模式：
  - “ftp”或者“anonymous”。这类用户是指在FTP服务器中没有指定帐户，但是其仍然可以进行匿名访问某些公开的资源。
  - 任何人无需密码验证就可以直接登录到FTP服务器。这种模式最不安全，一般只用来保存不重要的公开文件，不推荐在生产环境中使用。

- 本地用户模式：
  - 是FTP服务器本机的系统用户账号。
  - 当这类用户登录FTP服务器的时候，其默认的主目录就是其帐号命名的目录。但是，其还可以变更到其他目录中去。如系统的主目录等等。
  - 当开放本地账户的时候，我们往往会做chroot（禁锢家目录）来保证安全。

- 虚拟用户模式：
  - 账号信息存放在独立的文件或者数据库内。不是本地账号，不能登陆操作系统，安全性比较高。
  - 只能访问服务器为其提供的FTP服务，而不能访问系统的其它资源。
  - 所以，如果想让用户对FTP服务器站内具有写权限（可以上传数据到服务器），但又不允许访问系统其它资源，可以使用虚拟用户来提高系统的安全性。
  - 创建虚拟用户需要使用pam

### 数据传输模式

- 数据的传输模式，分别为ASCII模式（文本序列）和Binary（二进制）模式。

### 端口修改

- 默认情况下，FTP服务器的控制连接端口是21，数据连接端口是20。但是，你可以通过修改vsftpd的配置文件来改变这些默认设置。


- 在vsftpd的配置文件（通常位于/etc/vsftpd/vsftpd.conf）中，你可以设置以下参数来修改端口：

  - listen_port：这个参数用于设置FTP服务器的控制连接端口。例如，如果你想将控制连接端口改为2121，你可以在配置文件中添加以下行：listen_port=2121。


  - ftp_data_port：这个参数用于设置FTP服务器的数据连接端口。例如，如果你想将数据连接端口改为2020，你可以在配置文件中添加以下行：ftp_data_port=2020。


- 修改完配置文件后，你需要重启vsftpd服务以使新的设置生效。


### 开启被动模式并指定端口范围

在vsftpd中启用被动模式（PASV）需要在vsftpd的配置文件中设置一些参数。以下是启用被动模式所需的步骤：

1. 打开vsftpd的配置文件，通常位于`/etc/vsftpd/vsftpd.conf`。
2. 在配置文件中添加或修改以下参数：
   - `pasv_enable=YES`：启用被动模式。
   - `pasv_min_port`和`pasv_max_port`：设置被动模式的端口范围。例如，`pasv_min_port=40000`和`pasv_max_port=50000`将设置端口范围为40000到50000。
3. 保存并关闭配置文件。
4. 重启vsftpd服务以使新的设置生效。

- 安装完成之后，默认的配置位于 `/etc/vsftpd.conf`

- vsftpd 对每个配置的选项都设置了一个默认值，服务器启动之后，在 `vsftpd.conf` 中配置的选项会覆盖服务器中的默认值

## 配置文件

### 访问权限

```ini
#是否允许匿名登录，默认允许，如果允许，用户名 ftp 和 anonymous 都会被当做匿名登录
#为了安全，一般不允许匿名登录
anonymous_enable=NO

#是否允许匿名上传，默认不允许，如果允许 write_enable 选项需要设置为 YES
#为了安全，一般不允许
anon_upload_enable=NO

#是否允许本地用户登录，默认不允许，如果允许，在 ``` /etc/passwd``` 中的用户都可以登录 FTP 服务器
#如果不予许匿名登录的话，这个选项需要设置为允许
local_enable=YES

#是否允许在FTP服务器上写入, 默认不允许，如果有上传文件、删除文件等需求，一般都是开启的
write_enable=YES

#设置写入服务器文件的权限掩码值，如果值是八进制需要以 0 开头，否则会当作十进制
#值为 022，能满足大部分FTP的需求
local_umask=022
```

### 锁定访问目录

```ini
#默认为 NO， 如果设置为 YES，表示用户通过FTP客户端登录之后只能在FTP服务器指定的目录中，不允许切出目录
chroot_local_user=YES

#用户名插入到本地 FTP 主目录中
user_sub_token=$USER

#定义用户 FTP 主目录，用户登录成功之后，vsftpd 服务器会切换到此目录
#此时 FTP 客户端会位于此目录中，后续的上传以及下载都是针对这个目录的
local_root=/home/$USER/ftp
```

- 把登录的用户锁定在指定的目录中，避免用户访问不应该访问的目录，这里我们设置成只允许访问自己的 home 目录中的 ftp 目录，例如：新添加一个用户 `testuser` 专门用于上传下载， `testuser` 通过 FTP 客户端成功登录后，会自动切换到 `/home/testuser/ftp` 目录，并且不允许切出该目录
- 注意：用户上传和下载都是在限定的目录中，所以一般都是把锁定目录设置到剩余空间比较大的磁盘中

### 限定用户登录

```ini
#如果设置为 YES ，vsftpd 将会从 userlist_file 选项指定的文件读取用户列表
userlist_enable=YES

#设置用户列表配置文件, 如果 /etc/vsftpd/user_list 不存在需要手工创建
userlist_file=/etc/vsftpd/user_list

#此选项检查 userlist_enable 选项，当 userlist_enable 为 YES 时
#如果 userlist_deny 设置为 NO ， 表示只允许 userlist_file 中的用户登录
#如果 userlist_deny 设置为 YES， 表示禁止 userlist_file 中的用户登录，允许其他用户登录
userlist_deny=NO
```

### 修改端口

```ini
#如果启用，vsftpd 将在独立模式下运行，vsftpd 本身将负责侦听和处理传入的连接
listen=NO

# 跟 listen 选型类似，但是此选项是侦听在 IPV6 上的 socket
# 而 listen 是 IPV4， 此选项和 listen 是互斥的，不能同时设置为 YES
listen_ipv6=YES

#服务器侦听端口，也是命令端口, 默认是21，修改之后, 防火墙需要做相应的调整
#同时 FTP 客户端登录的时候需要指定端口号
#为了增强安全性，配置的时候一般都会修改
listen_port=48888

#开启被动模式
pasv_enable=YES

#被动模式下，服务器的地址，默认是内网地址
#如果在云服务器上部署，需要修改成公网IP
pasv_address=192.168.70.20

#设置被动模式下，建立数据传输可使用的端口范围的最小值。
#建议把端口范围设置在一段比较高的范围内，例如50000~50010，有助于提高访问FTP服务器的安全性
pasv_min_port=50000

#设置被动模式下，建立数据传输可使用的端口范围的最大值
pasv_max_port=50020
```

### 日志配置

```ini
#是否记录上传下载日志，默认是不记录，如果设置为记录
#默认日志文件位于 /var/log/vsftpd.log， 如果配置了 vsftpd_log_file 选项，会覆盖默认日志文件
xferlog_enable=YES

#记录上传下载的日志
xferlog_file=/var/log/xferlog

#是否按照标准格式记录日志
xferlog_std_format=YES
```

### 其他配置

```ini
# vsftpd 使用的 PAM 服务名字
pam_service_name=vsftpd
tcp_wrappers=YES
# 这两个配置使用默认生成的选项即可，不用做任何修改
```

# Ubuntu部署vftpd服务端

## 安装

~~~sh
sudo apt-get install vsftpd
~~~

## 配置本地用户模式

~~~sh
adduser ftptest
#adduser 是 Debian 和 Ubuntu 系统中的一个脚本，它是 useradd 的一个更友好的前端。这个脚本会自动创建新用户的主目录，复制 /etc/skel 目录中的文件，以及进行其他一些设置。它也会提供一个交互式的界面来收集新用户的信息，如全名和密码。
#密码azsxdcfv
#运行以下命令创建一个供FTP服务使用的文件目录。
mkdir /var/ftp/test -p
#运行以下命令更改/var/ftp/test目录的拥有者为ftptest。
chown -R ftptest:ftptest /var/ftp/test
~~~

## 主动模式配置文件

- 编辑/etc/vsftpd.conf

~~~sh
#修改下列参数的值 
anonymous_enable=NO #禁止匿名登录FTP服务器 
local_enable=YES #允许本地用户登录FTP服务器
listen=YES #监听IPv4 sockets 
#在行首添加#注释掉以下参数
 #listen_ipv6=YES             #关闭监听IPv6 sockets #添加下列参数 
local_root=/var/ftp/test     #设置本地用户登录后所在目录 
chroot_local_user=YES #全部用户被限制在主目录 
chroot_list_enable=YES #启用例外用户名单 
chroot_list_file=/etc/vsftpd/chroot_list  #指定例外用户列表文件，列表中用户不被锁定在主目录
allow_writeable_chroot=YES 
pasv_enable=YES #开启被动模式 
pasv_address=<FTP服务器公网IP地址>     #本教程中为Linux实例公网IP 
pasv_min_port=<port number>          #设置被动模式下，建立数据传输可使用的端口范围的最小值 
pasv_max_port=<port number>          #设置被动模式下，建立数据传输可使用的端口范围的最大值
~~~

- 全配置文件

  ~~~bash
  # Example config file /etc/vsftpd.conf
  #
  # The default compiled in settings are fairly paranoid. This sample file
  # loosens things up a bit, to make the ftp daemon more usable.
  # Please see vsftpd.conf.5 for all compiled in defaults.
  #
  # READ THIS: This example file is NOT an exhaustive list of vsftpd options.
  # Please read the vsftpd.conf.5 manual page to get a full idea of vsftpd's
  # capabilities.
  #
  #
  # Run standalone?  vsftpd can run either from an inetd or as a standalone
  # daemon started from an initscript.
  listen=YES
  #
  # This directive enables listening on IPv6 sockets. By default, listening
  # on the IPv6 "any" address (::) will accept connections from both IPv6
  # and IPv4 clients. It is not necessary to listen on *both* IPv4 and IPv6
  # sockets. If you want that (perhaps because you want to listen on specific
  # addresses) then you must run two copies of vsftpd with two configuration
  # files.
  listen_ipv6=NO
  #
  # Allow anonymous FTP? (Disabled by default).
  anonymous_enable=NO
  #
  # Uncomment this to allow local users to log in.
  local_enable=YES
  #
  # Uncomment this to enable any form of FTP write command.
  write_enable=YES
  #
  # Default umask for local users is 077. You may wish to change this to 022,
  # if your users expect that (022 is used by most other ftpd's)
  local_umask=022
  #
  # Uncomment this to allow the anonymous FTP user to upload files. This only
  # has an effect if the above global write enable is activated. Also, you will
  # obviously need to create a directory writable by the FTP user.
  anon_upload_enable=NO
  #
  # Uncomment this if you want the anonymous FTP user to be able to create
  # new directories.
  #anon_mkdir_write_enable=YES
  #
  # Activate directory messages - messages given to remote users when they
  # go into a certain directory.
  dirmessage_enable=YES
  #
  # If enabled, vsftpd will display directory listings with the time
  # in  your  local  time  zone.  The default is to display GMT. The
  # times returned by the MDTM FTP command are also affected by this
  # option.
  use_localtime=YES
  #
  # Activate logging of uploads/downloads.
  xferlog_enable=YES
  #
  # Make sure PORT transfer connections originate from port 20 (ftp-data).
  connect_from_port_20=YES
  #
  # If you want, you can arrange for uploaded anonymous files to be owned by
  # a different user. Note! Using "root" for uploaded files is not
  # recommended!
  #chown_uploads=YES
  #chown_username=whoever
  #
  # You may override where the log file goes if you like. The default is shown
  # below.
  #xferlog_file=/var/log/vsftpd.log
  #
  # If you want, you can have your log file in standard ftpd xferlog format.
  # Note that the default log file location is /var/log/xferlog in this case.
  #xferlog_std_format=YES
  #
  # You may change the default value for timing out an idle session.
  #idle_session_timeout=600
  #
  # You may change the default value for timing out a data connection.
  #data_connection_timeout=120
  #
  # It is recommended that you define on your system a unique user which the
  # ftp server can use as a totally isolated and unprivileged user.
  #nopriv_user=ftpsecure
  #
  # Enable this and the server will recognise asynchronous ABOR requests. Not
  # recommended for security (the code is non-trivial). Not enabling it,
  # however, may confuse older FTP clients.
  #async_abor_enable=YES
  #
  # By default the server will pretend to allow ASCII mode but in fact ignore
  # the request. Turn on the below options to have the server actually do ASCII
  # mangling on files when in ASCII mode.
  # Beware that on some FTP servers, ASCII support allows a denial of service
  # attack (DoS) via the command "SIZE /big/file" in ASCII mode. vsftpd
  # predicted this attack and has always been safe, reporting the size of the
  # raw file.
  # ASCII mangling is a horrible feature of the protocol.
  #ascii_upload_enable=YES
  #ascii_download_enable=YES
  #
  # You may fully customise the login banner string:
  #ftpd_banner=Welcome to blah FTP service.
  #
  # You may specify a file of disallowed anonymous e-mail addresses. Apparently
  # useful for combatting certain DoS attacks.
  #deny_email_enable=YES
  # (default follows)
  #banned_email_file=/etc/vsftpd.banned_emails
  #
  # You may restrict local users to their home directories.  See the FAQ for
  # the possible risks in this before using chroot_local_user or
  # chroot_list_enable below.
  chroot_local_user=YES
  #
  # You may specify an explicit list of local users to chroot() to their home
  # directory. If chroot_local_user is YES, then this list becomes a list of
  # users to NOT chroot().
  # (Warning! chroot'ing can be very dangerous. If using chroot, make sure that
  # the user does not have write access to the top level directory within the
  # chroot)
  #chroot_local_user=YES
  #chroot_list_enable=YES
  # (default follows)
  #chroot_list_file=/etc/vsftpd/chroot_list
  #
  # You may activate the "-R" option to the builtin ls. This is disabled by
  # default to avoid remote users being able to cause excessive I/O on large
  # sites. However, some broken FTP clients such as "ncftp" and "mirror" assume
  # the presence of the "-R" option, so there is a strong case for enabling it.
  #ls_recurse_enable=YES
  #
  # Customization
  #
  # Some of vsftpd's settings don't fit the filesystem layout by
  # default.
  #
  # This option should be the name of a directory which is empty.  Also, the
  # directory should not be writable by the ftp user. This directory is used
  # as a secure chroot() jail at times vsftpd does not require filesystem
  # access.
  secure_chroot_dir=/var/run/vsftpd/empty
  #
  # This string is the name of the PAM service vsftpd will use.
  pam_service_name=vsftpd
  #
  # This option specifies the location of the RSA certificate to use for SSL
  # encrypted connections.
  rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
  rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
  ssl_enable=NO
  
  #
  # Uncomment this to indicate that vsftpd use a utf8 filesystem.
  #utf8_filesystem=YES
  local_root=/var/ftp/test
  pasv_enable=YES
  pasv_address=172.16.183.130
  pasv_min_port=50000
  pasv_max_port=50020
  allow_writeable_chroot=YES
  ~~~

## 编辑chroot_list

创建chroot_list文件，并在文件中写入例外用户名单。

1. 运行`vim /etc/vsftpd/chroot_list`命令创建chroot_list文件。

2. 输入例外用户名单。此名单中的用户不会被锁定在主目录，可以访问其他目录。
3. `chmod 644 /etc/vsftpd/chroot_list`赋权

> 说明 没有例外用户时，也必须创建chroot_list文件，内容可为空。

4. 重启vsftpd服务。

5. 服务端防火墙开启对应端口

~~~sh
sudo ufw allow 20 21 50000:50020/tcp
~~~

## 客户端测试

### 登录

~~~sh
#客户端安装ftp
sudo apt install ftp
#访问ftp,不加端口默认走21
ftp 172.16.183.130
~~~

### 常用命令

~~~sh
pwd #FTP服务器上的 /var/ftp/test 目录就是 FTP 的根目录
ls
put demo1.txt #将客户端当前目录的demo1.txt文件上传到服务端当前目录
#客户端从哪个目录下执行的ftp命令，当前目录就是那里
get demo.py #下载服务端当前目录的demo.py到客户端当前目录
#mget <filename1> <filename2> ...：下载多个文件到本地。
#mput <filename1> <filename2> ...：上传多个本地文件到服务器。
#delete <filename>：删除服务器上的指定文件。
#mkdir <directory>：在服务器上创建新的目录。
#rmdir <directory>：删除服务器上的指定目录。
#quit：退出FTP会话。
~~~

## 修改ftp监听端口

~~~sh
#配置文件添加
#服务器侦听端口，也是命令端口, 默认是21，修改之后, 防火墙需要做相应的调整
#同时 FTP 客户端登录的时候需要指定端口号
#为了增强安全性，配置的时候一般都会修改
listen_port=48888
#数据连接端口修改
ftp_data_port=48889
~~~

~~~sh
#防火墙开启48888
sudo ufw allow 48888/tcp 48889/tcp
#重启vsftpd
~~~

~~~sh
#客户端连接
ftp 172.16.183.130 48888
~~~



> 参考文档：
>
> https://zhuanlan.zhihu.com/p/111582376
>
> https://www.cnblogs.com/wanng/p/how-to-install-ftp-server.html