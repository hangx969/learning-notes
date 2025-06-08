# Linux Basic

## 001 绪论

- Linux学习阶段：

​	基本操作命令 - 各种配置（网络 存储等） - shell 脚本 - 系统调优 - 深入了解Linux内核

- 学习方法：

  先整体后细节 - 要知道怎么查 怎么用 - 先how 再why

  计算机是 做中学

  Linux是实操性 用指令要非常溜 拿过来就敲 

- 学习大纲：

  基础篇：Linux入门 - vim和Linux的安装 - Linux目录结构

## 002 Linux应用范围 

- Linux应用场景

​	Linux开发项目（JavaEE、Python、PHP、C等）、运维、嵌入式等

- Linux应用领域

  **服务器：**免费、高效。**这是Linux最主要的应用领域**

  嵌入式：对软件进行裁剪，可对内核进行定制

## 003 Linux介绍

- 免费、稳定、开源、可高并发的系统
- 主要发行版：**ubuntu、Redhat、CentOS**、Debain、Fedora、SuSE、CoreOS、OracleLinux等

- Linux是内核，发行版是内核+程序包等扩展功能形成的封装版

Linux发行版与Windows或Mac OS（操作系统）一样，Linux由多种类型组成，称为分发,每个发行版都很相似，但是不完全一样。一般情况下，Linux发行版是各种应用程序（软件）的集合，从而来适应使用目的，除了在服务器上安装之外，其他还要提前设置，以便可以立即进行实际使用。

Linux发行版主要有：Debian类型、Slackware系列、Red Hat
1.Debian类型：
Debian拥有出色的性能，可用于嵌入式设备等众多应用。此外，它已经发展成为一种流行的Linux发行版，名为Ubuntu。 
2.Slackware系列：
Slackware管理方法比其他线路更复杂，对于初学者来说相对困难。Slackware著名的发行版包括openSUSE，Plamo Linux和Puppy Linux。 
3.Red Hat：
目前Red Hat大致分为两类，第一个是红帽企业Linux（RHEL），有些服务是要收费的。另一种是名为Fedora（Fedora）的免费发行版。
4、Centos
CentOS是Linux发行版之一，它是来自于Red Hat Enterprise Linux依照开放源代码规定释出的源代码所编译而成。由于出自同样的源代码，因此有些要求高度稳定性的服务器以CentOS替代商业版的Red Hat Enterprise Linux使用。

## 004 Unix与Linux

-  1970s 贝尔实验室+Ken Tompson + Dennis = Unix诞生 （多用户分时操作系统）
-  1980s Unix发行版 高端机型才能用 PC用不了
-  著名黑客Richard Stallman发起了**GNU计划 倡导开源精神**，大家都能阅读源代码，软件公司提供服务和培训。
-  Linus贡献了Linux Kernel（可在x86系统上运行），越来越多的人贡献了FTP、editor等功能 => GNU/Linux

## 005 VMWARE 16和CentOS 7 安装

- win10系统，安装之后要 控制面板-程序-打开或关闭windows功能-虚拟机 开启

- 手动配置分区：

  Linux磁盘空间分区一般分三个区：Boot分区、Swap分区、根分区 

  - Boot分区：包含启动文件和内核
  - Swap分区：交换分区，系统内存不足时，调用硬盘的一部分，可以理解为虚拟内存。
  - 根分区：存放用户文件

- 安装模式

  实际生产环境会选择Minimal，不带用户界面的那种

- KDUMP 生产环境会开启 

## 007 Linux虚拟机网络连接的三种方式

- 桥接模式：虚拟系统可以与外部进行通信，但用的是主机的网段，容易发生IP冲突（占用同一个网段）
- NAT模式：网络地址转换，虚拟系统可以和外部系统通信，不造成外部冲突 
- 主机模式：独立系统，不与外界通信 

## 008 Linux虚拟机克隆

- 直接复制虚拟机文件
- vmware自带克隆功能

## 009 虚拟机快照

- 就是Save and Load功能

## 011 安装vmtools

- 详见教程

- 设置与主机的共享文件夹

  在CentOS中，共享文件夹位于/mnt/hgfs/下

- 实际生产环境下，上传下载是使用远程方式完成的

## 012 Linux 目录结构

- 树状结构 根目录下有各种子目录（规定好的）
- Linux会把硬件
- 资源映射成文件来管理，所以Linux里面一切皆文件，隐藏文件是以 . 开头的
- 具体目录结构：
  - **/bin** 存放最常使用的指令，单人维护模式下也可以执行的指令。
  
  - /sbin 存放系统管理员的管理程序
  
  - /home 用户的家目录。~表示当前用户的家目录
  
  - /root 系统管理员的用户主目录
  
  - /lib 动态链接共享库，函数库
  
  - **/etc 系统管理所需要的配置文件和子目录。**
  
  - /opt 安装包 约定俗成 放在这里
  
  - **/usr**：Unix System Resource，操作系统软件资源，里面放着/sbin /bin /lib等
  
  - **/boot Linux启动引导**
  
  - /proc 系统内存映射 /srv 服务启动 /sys  【这些都不能动】
  
  - /dev 类似windows的设备管理器，将硬件映射为文件的形式
  
  - /mnt 自动识别的设备 U盘 光驱等
  
  - /mnt 让用户临时挂载别的文件系统
  
  - /var 存放经常变动的文件 一般可以把日志文件放进去 （**/var/log** 系统日志）
  
  - /run centos7之后才有，将经常变动的项目移动到内存中暂存，不占用硬盘容量。放在内存中每次开机都变动。
- 系统变量
  - 位置查看：echo $PATH
  - 作用：当输入一个命令的时候，系统需要寻找这个命令的路径，系统变量就是告诉系统去哪里寻找命令，节省时间
  - 将新增系统变量：将目录加入到~/.bash_profile

### FHS

Filesystem Hierarchy Standard

linux目录结构的标准规范。 定义了根目录以及/usr, /var中的内容以及应该放置的数据。 

## 014 远程登录Linux

- 实际生产环境中，Linux服务器是开发小组共享；上线的项目运行在公网
- Xshell远程登录（只能做一些命令性指令），Xftp文件远程上传下载
- XShell远程连接的条件：1、知道Linux公网IP 2、能ping通远程服务器
- ifconfig 查看Linux公网IP地址，windows终端ping一下这个IP试试

- windows编码是gbk，Linux编码用的是UTF-8
- Telnet和SSH是用于远程访问服务器的两大协议，telnet是明码传输，ssh是加密传输

### Linux终端机界面

- tty1-tty6
- linux预设6个terminal可供登录，使用 ctrl+alt+f1-f6 来切换

- 开机之后默认提供一个tty，切换之后才产生新的

### 远程登录的服务

- systemctl status sshd.service

  是通过OpenSSH server.daemon来实现的

## 016 Vi和Vim

Linux的文本编辑器

- 三种模式：

  - 正常模式（不能输入内容）
  - 插入模式：按i进入
  - 命令行模式：按/ or : 进入

- 实例：

  ```Shell
  vim hello.java  # 创建新文件或者打开文件
  i #进入编辑模式
  # 按Esc 再输入:wq即可退出vim
  # 按:可以进入命令行模式 :wq 保存退出 :q! 强制退出
  ```

- ### 快捷键

  - 正常模式下：yy 复制当前行；5yy复制当前行下面的5行；p 粘贴
  - 正常模式下：dd 删除当前行；5dd 删除当前行下面的5行
  - 查找单词：正常模式输入/ 进入命令行模式，输入单词，回车，按n切到下一个
  - 显示行号：正常模式输入/进入命令行模式，输入set nu，set nonu
  - 大文件：正常模式下，移动到首行 小写gg；移动到末尾，大写G，移动到首行
  - 撤销：正常模式，输入u
  - 快速到某一行：1、可以在正常模式下输入 20 shift+g；2、可以在命令模式下输入:20

## 017 关机 重启 用户

### linux启动过程

![090eb76673404b3ff67ee7ed697224f](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312042155530.jpg)

![dc019cdb971d2f32c75f931de48252d](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312042155497.jpg)

1. 按电源键，服务器启动，首先会加载BIOS或者UEFI
2. BIOS会检测硬件是否准备就绪，例如内存、硬盘、CPU等。
3. 硬件检测通过，会选择启动设备，可以是硬盘、光驱、网络服务器。
4. 从设备中读取引导文件（grub），读取到之后会提示选择内核版本，操作系统等。
5. Linux内核启动，运行用户环境，systemd将成为第一个用户空间的进程。用于管理系统中的进程和服务，并挂载文件系统。
6. 在操作系统启动时，也会启动相关的服务或者进程，比如sshd，syslog，或者用户设置的开机启动服务。
7. 运行启动脚本，并配置用户环境。
8. 然后显示登录界面，提示输入用户名密码。

### 关机

- shutdown -h now 立刻关机

- shutdown -h 1  1min之后关机

- shutdown -r noe 现在重启

- reboot 现在重启


- **sync** 将内存数据同步到磁盘 关机之前要进行一遍

```shell
sync; sync; sync; reboot
```

- shutdown / halt / poweroff这几个命令都是去call systemctl

### 用户类型

- root用户：UID=0，GID=0
- 普通用户：UID>1000
- 系统用户：伪用户，nologin 无法登陆，0<UID<1000，是为系统中某些进程准备的，即nobody用户：

  - nobody在linux中是一个不能登陆的帐号，一些服务进程如Apache，aquid等都采用一些特殊的帐号来运行，比如nobody,news,games等等，这是就可以防止程序本身有安全问题的时候，不会被黑客获得root权限。

    1、Windows系统在安装后会自动建立一些用户帐户，在Linux系统中同样有一些用户帐户是在系统安装后就有的，就像Windows系统中的内置帐户一样。

    2、它们是用来完成特定任务的，比如nobody和ftp等，我们访问网页程序时，官网的服务器就是让客户以 nobody 身份登录的(相当于Windows系统中的匿名帐户); 我们匿名访问ftp时，会用到用户ftp或nobody。

    3、首先，nobody是一个普通用户，非特权用户。 使用nobody用户名的'目的'是，使任何人都可以登录系统，但是其 UID 和 GID 不提供任何特权，即该uid和gid只能访问人人皆可读写的文件。
    4、其次，许多系统中都按惯例地默认创建一个nobody，尽量'限制它的权限至最小'，当服务器向外服务时，可能会让client以nobody的身份登录。

    5、nobody就是一个普通账户，因为默认登录shell是 '/sbin/nologin'，所以这个用户是无法直接登录系统的，也就是黑客很难通过漏洞连接到你的服务器来做破坏。此外这个用户的权限也给配置的很低。因此有比较高的安全性。一切都只给最低权限。这就是nobody存在的意义。


### 用户登录与注销

- 登录

  一般不会给你root用户权限，普通用户想要切换成root用户，输入 su - 用户名，切换成root用户（直接 su - 也行

- 注销：logout 在**用户级别3**时才有效

- su 命令 申请切换root用户，需要输入root用户密码；sudo su 是临时申请root权限，所输入的是用户密码。

### 账户

- 每个用户的登陆环境在家目录中有 ~/.bash.profile 和 ~/.bashrc两个配置文件，通常个人bash环境设置都定义在~/.bashrc中

- 对所有用户生效的配置文件：/etc/bash.profile 和 /etc/bash.rc 

## 018 用户管理   

### 添加用户

useradd 用户名

1、创建用户成功后，自动创建该用户的家目录，位于/home/用户名

2、通过 useradd -d 指定目录 用户名 :可以给新创建的用户制定家目录

### 制定、修改密码

passwd 用户名 密码  （注意加上用户名，否则是给当前用户改密码）

### 删除用户

userdel 用户名 （保留了家目录）一般建议保留家目录

userdel -r 用户名 （删除家目录）

### 查询用户

id 用户名

### 切换用户

- su - 用户名 （带 - 是切换用户的同时切换环境变量）

- su 直接切换，不是登录shell，该用户的环境变量没有被切换。

- 命令行#代表root用户 $代表普通用户
- root用户切其他用户是不需要输入密码的，即使该user没设置密码。

### 查看当前用户

who am i 显示的是第一次登录到的用户信息

### **用户组**

（给组设置具体权限，把用户拉进来）

groupadd 组名

groupdel 删除组

（如果新建用户时没有指定的组，系统会自动建一个用户名同名的组，放进去）

groupadd -g 用户组 用户名：新建用户同时放到一个组里

groupmod -g 用户组 用户名 ：更改用户组

### **把用户拉进组** / 更改用户所在组

usermod -aG 组名 用户名

### 更换文件所在组

chgrp 组名 文件名

### 用户配置文件

/etc/passwd  用户配置文件，记录用户的各种信息

（查询已有用户：cat /etc/passwd）

/etc/shadow  口令的配置文件 ，记录密码，登录信息啥的

/etc/group  组的配置文件

## 019 Bash shell

shell：类似解释器的进程，把命令转换为Linux内核可以识别的命令，中国一般用bash shell

Azure 用的是 Bourne Again shell （Bash）

## 025 **实用指令**-01

### 指定运行级别

- 0 关机
- 1 单用户【找回丢失密码】（单人维护模式仅挂载根目录）
- 2 多用户状态没有网络
- 3 多用户状态 有网络服务 【**使用最多**】
- 4 保留给用户
- 5 图形界面 【也常用】
- 6 系统重启

​		centOS 7 以后，运行级别3 等同于 multi-user.target；运行级别5 等同于 graphical.target

​		查看默认的运行级别：systemctl get-default

​		设置默认的运行级别：systemctl set-default multiuser.target

- 找回root密码

  开机界面进入单用户模式

### 帮助指令

- man 查看帮助信息

  查询某指令时候，指令后面会带一个括号数字：

  ![image-20220914230526292](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209171633422.png)

  1-9含义不同：

  ![image-20220914231244428](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209171633462.png)

- help 查看 shell 内置指令的帮助


> curl cheat.sh/tree #可以查看命令的常用方法

### 快捷键

- ctrl + a 光标移动到最前面；ctrl+e 光标移动到最后面

### ls 列出当前目录文件

-  -l 按行详细输出
- -a 显示所有文件包含隐藏文件(以. 开头的是隐藏文件)
- ls -lh 将文件大小显示为适合人类看的格式

- ls -al 的时候，列出的信息的第二列的数字：

  ![image-20220917160920543](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209171636268.png)

​		是link数；每个文件都会将权限和属性记录到文件系统的i-node中；每个文件名也会连接到一个inode。

​		第二列的数字就是该文件的硬连接数，相当于该文件有多少个别名。

## 028 文件类实用指令-02

### 文件目录

- pwd  （print working directory）

- cd：

  cd **~** 回到家目录（root回到/root，普通用户回到家目录）

  cd .. 回到上一级目录（cd ../.. 可以连着用）

  . 或者 ./ 代表当前目录；.. 或者 ../s 代表上一级目录

- mkdir 创建目录

  - mkdir /home/animal

  - mkdir -p 创建多级目录

    mkdir -p /home/animal/tiger

- rmdir 删除目录

  - 默认删除空目录，里面有内容不生效

  - 里面有东西可以用这个恐怖指令：

    rm -rf 目录路径

  这里推荐用 **mv指令 移动到 /delete 文件夹 定期清理**

- touch 创建空文件

  当这个文件已经存在时，可以将其时间标签更新为系统当前时间

### 文件操作

- cp 文件复制

  - 单个文件：cp 文件名 目录


  ```shell
  cp hello.py /opt/
  ```

- 复制整个目录： cp -r 源目录 目标目录


  ```
  cp -r /home/bbb /opt # 直接复制过去 若有同名文件 会一个一个提示是否覆盖
  \cp -r /home/bbb /opt # 不提示 直接覆盖 （cp -rf也可以）
  ```

  - cp -p 旧文件 新文件：将修改时间和访问权限也复制到新文件

- cut 文件提取

- sort 能把文件里面的行排好序显示出来，不改变原始内容

- awk 命令行编程工具 不需要编译 可以用变量 字符、数字函数等。

  ``` shell
  awk '{print $1,$2}' # 输出前两行
  awk '/Enlish {print}' 
  ```

- sed 文本替换

  ```shell
  sed -i 's/[old text]/[new text]/g' xxx.txt
  ```

- rm 删除文件或者目录

  -r 递归删除

  -f 强制删除不提示

### 文件时间

有三个主要的变动时间：

- mtime：修改时间，更改文件内容
- ctime：status time，修改文件状态会更新这个时间，例如改文件属性
- atime：access time，文件内容被读取就会更新

其中，ls -ll 默认显示mtime；想要看其他的time，要加参数，例如

```shell
ls -ll --time=atime /var/log/messages
```

touch可以修改mtime和atime

### 文件比较

- cmp 一个字母一个字母的比较
- comm 比较两个sorted的文件
- diff 按行比较

### mv 移动/重命名

mv 旧文件名 新文件名

mv 源目录 新目录

mv 源文件 新目录/新名字 (移动并且重命名)

### cat 查看文件内容

更加安全 只能看不能改

- cat -n 显示行号
- 一般会带上管道命令 | more (管道命令是将前面的结果交给后面处理) 

### head 查看开头指定行数

head 默认查看前10行

head -n 5 看前5行

### tail 查看末尾指定行数

- tail -f  可以实时监控文件末尾改变

  ```shell
  tail -f /opt/mylog.txt
  tail -fn 10 test.log #循环实时查看最后10行记录(最常用的)
  ```
  
  实时监控 按ctrl + C 中断指令
  
  tail -f 只能监控echo写入的内容，vim写入的不行。因为tail -f 是基于文件的inode监控，而vim会改变文件的inode
  
  （Unix/Linux系统内部不使用文件名，而使用inode号码来识别文件。对于系统来说，文件名只是inode号码便于识别的别称或者绰号。）

### more 基于Vi的文本过滤器

按回车一行一行看，空格一页一页看

### less

分屏查看 支持各种终端 动态加载 适合查看大文件 效率高 

### echo 将内容输出至控制台

- echo [选项] 输出内容

  echo $HOSTNAME

  echo "Hello World"

  写shell脚本的时候相当于printf

- echo "xxx" >  xxx.txt  新建文件的方法2

### \> 和 >> 

\> 是覆写 >> 是追加

- ```shell
  echo “Hello World” > /home/mylog.txt
  ```

- ls -l > 文件  （将ls -l显示出来的列表内容写入到文件）文件不存在的话，自动创建

  ls -al >> 文件  （将列表内容追加到文件末尾）

  cat 文件1 > 文件2  （将文件1的内容覆写到文件2）

- cal >> /home/mycal  可以把日历信息输出到文件中

- cat 文件1 文件2 > 文件3  把两个文件的信息合并到一起

- **cat 文件1 > 文件2  快捷复制文件 速度非常快**

### 文件链接

- ln -s **软链接/符号链接**

  - 类似快捷方式，不占用磁盘空间


  - 基本语法： ln -s [源文件或目录]  [软连接名]
  - 注意：如果软链接的目的路径和源文件路径不同的话，都需要使用绝对路径才能成功创建
  - 软链接的文件Inode是不同的
- ln  **硬链接**

  - 基本语法： ln [源文件或目录]  [软连接名]
  - 硬链接只能链接文件，不能链接目录
  - **链接与源文件的inode相同**，代表这是同一个文件
  - 把源文件移走或重命名，都不影响内容或者权限的同步改变
  - 删掉原文件之后，硬链接文件仍然保持着原内容
- 改变内容：

  - 对于软硬链接而言，改变链接文件的内容，源文件会都同步改变
- 改变权限：

  - 改变软链接文件的权限，软链接的权限并不会改变，源文件的权限会改变
  - 改变硬连接和原文件的权限一旦改变，另一个文件随之也改变
- 文件系统：

  - 软链接可以跨越文件系统；硬链接不能

### 文件指针

inode 代表文件的数据结构

dentry 代表目录的数据结构

inode和dentry一起构成了cache，磁盘上的文件系统

### history 查看已经执行过的命令

history 所有的；history 10 看最近10个；

history !5 执行 history列表中行号为5的指令

### 文件系统类型

Ext3

Ext4

XFS ：large data files

## 034 时间日期指令

### date 

- date 显示当前时间
- date "+%Y-%m-%d %H:%M:%S"按占位符规定的格式显示日期
- date -s [新时间] 设置系统时间

- cal 显示日历

## 035 查找指令

### find

从当前目录向下递归遍历各个子目录，将查到的显示在终端

- 基本语法：find [搜索范围] [选项]

  - find -name / -user / -size (+n 大于；-n 小于；n等于；单位 k M G )
  
  
  - find /目录 -iname xxx.txt  (-i 忽略大小写)
  - find /目录 -f -name xxx.txt (加上-f是查找文件)
  - find /目录 -d -name xxx.txt (加上-f是查找目录)
  - 不加 -f-d都查找 

### whereis

- find有时候会比较慢，whereis会比较快。但是whereis只是去找特定的几个目录

### locate

- 利用事先建立的查找数据库，快速定位文件；保证精确度，定时更新索引数据库（大概是系统每天自动更新一次数据库）
- 先 updatedb
- 再 locate xxx.txt

### which

- 是找 PATH环境变量下面目录的指令

- 查看某个指令在哪个目录下：which ls

### grep

- 过滤查找，常常与管道符结合使用
-  基本语法：grep [选项] 查找内容 源文件
- 例如：cat /opt/mylog | grep -n "Hello"
- -n：显示行号；-i：忽略大小写

## 037 压缩和解压缩

### gzip/gunzip

- gzip 压缩文件，只能压缩为.gz；gunzip 解压缩，只能解压.gz
- 压缩完，源文件就没了
- 语法 gzip *

### zip/unzip

压缩/解压，项目打包发布有用

- zip/unzip [选项] [文件名].zip [文件或者目录名] 
- zip -r ：递归压缩，压缩整个目录（该文件夹内必须有子文件夹，才能-r递归压缩成功）
- unzip -d [指定目录]  [待解压文件]：解压后放到指定目录

### tar 

- 既能压缩，又能解压；压缩成.tar.gz文件（.tar是打包文件，没压缩；.tar.gz是压缩文件）

- 基本语法：tar  [选项]  xxx.tar.gz 打包的内容

- -c 产生.tar打包文件；-v 显示详细信息；-f 指定压缩后的文件名；-z 用gzip格式对文档进行压缩或解压；-x 解包.tar文件

- 文件名后缀有.gz，得加上-z解压缩

  ```bash
  # 压缩文件夹
  tar -zcvf /opt/my.tar.gz /opt/mytest/
  # 压缩俩文件
  tar -zcvf /opt/my.tar.gz /opt/my1.txt /opt/my2.txt
  # 解压到指定目录 -C 后面加上指定目录
  tar -zxvf /opt/my.tar.gz -C /opt/tmp
  ```

## 040 组管理

1. 每一个用户都必须属于一个组，可以属于多个组
2. 每个文件而言，有：**所有者、所在组、其他组** 三个概念，每种组，都有一定的权限可以设置。每个文件只能由一个组

- 查看所有者

  ls -ahl / ls -ll 一样

- 修改所有者 得有root权限

  chown 所有者：所有组 /文件、目录

- 创建组，把人放进去

  groupadd [组名]

  useradd -g [组名] [用户名]

- 文件的创作者就是所有者，所有者所在组就是文件的所在组

- chgrp 更改**文件**所在组；usermod -g 新组名 用户名（改变**用户**所在组）；usermod -d 目录名 用户名 该用户登录的初始目录；（该用户得有该目录的进入权限）

- **小技巧**：查找有没有某个组

  ```shell
  cat /etc/group | grep root
  ```

## 044 权限

- Linux中，任何一个文件都具有User、Group、Others三种身份的权限；即：**所有者、所在组、其他组**。
- User信息记录在：/etc/passwd里面；个人密码记录在/etc/shadow里面；群组信息记录在/etc/group里面。
- 命令：
  - chgrp：改变群组
  - chown：改变所有者
  - chmod：改变权限

### 权限详解

0-9 总共10位：- rwx rw- r--

- 第0位：文件类型

  - — 普通文件，l 链接，d 目录，c 字符设备文件（鼠标键盘等） ，b 块设备（硬盘），p管道文件，s socket文件

  - 查看文件状态 stat <filename>

- 1-3位：**所有者**权限 rwx

  r 可读 w可写 x可执行 ，某一位是 - 代表无此权限 

- 4-6位：**所在组**权限（与文件所有者同一组的用户权限）

- 7-9位：**其他组**权限

- 对文件：

  r：可以读取、查看（读取一个文件的话，如果知道该文件路径，则需要对目录具有x权限，对文件具有r权限才能读取该文件。不必对目录具有r权限，因为已经提前知道文件路径了，不用列出目录下的文件。）

  w：可以修改，不代表可以删除。可删除的前提是，用户对该文件所在**目录**有**w**的权限

  x：可以执行（Windows下的可执行与Linux下不同，windows是由扩展名来决定；linux是由x权限位来表示）

- 对目录：

  r：可以ls查看文件列表

  w：可以修改，可创建/删除/重命名目录

  x：可以进入该目录。如果要开放目录给别人浏览的时候，至少要给到r和x。

- 可用数字表示

  r = 4；w = 2；x = 1；rwx  = 7
  
  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111347288.jpeg" alt="img" style="zoom:50%;" />
  
  <img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111348269.png" alt="img" style="zoom:50%;" />

### 修改权限 chmod

- chmod -v 显示权限变更的过程

- 方式1：+ - = / u g o a

  u：所有者；g：所有组；o：其他人；a：所有人（对三种角色同时做操作）

  ```shell
  chmod u=rwx,g=rx,o=x log.txt
  chmod o+w log.txt
  chmod a-x log.txt
  ```

- 方式2：r=4 w=2 x=1

  ```bash
  # 将log.txt文件的权限更改为rwxr-xr-x
  chmod 755 log.txt
  ```

  注意这九位数是默认u g o 的顺序

### 新文件的默认权限

可以用umask查看：例如，0022，第一位是特殊标志位，后3位是权限位。

规则如下：

- 默认规定，新文件要拿掉x权限，即默认最大给到：-rw-rw-rw-；默认规定，新目录不拿掉任何权限，即默认给到：drwxrwxrwx
- umask的0022规定了在以上基础上继续拿掉哪些权限。022表示：user不被拿掉任何权限；group和others拿掉2（w）
- 默认权限基础上减掉被umask拿掉的权限就是新创建文件和目录的默认权限：
  - 文件：-rw-r--r--
  - 目录：drwxr-xr-x

![image-20220917205951750](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209172059809.png)

### SUID SGID Sticky：特殊标志位

- SUID
  - **只对有x权限的文件有效。**如果一个程序的所有者是root并且具有SUID属性；那么普通用户执行，如同是root在执行。
  - -rwsr-xr-x；置于u的x位置，s 表示SUID位被设置。也可以用 4755 表示
  - 比如/etc/passwd: ----------（即passwd只有root用户可以读写）; 但是修改密码的命令：/usr/bin/passwd: -rwsr-xr-x，那么普通用户在用passwd改自己的密码时可以跟root一样获得权限去写入passwd文件。
- SGID
  - 对目录设置后，该目录中【新建的文件】的所在组 都是该目录的所在组
  - drwxrwsr-x; 置于g的x位置，也可以用 2775 表示
- sticky
  - 针对目录而言，如果设置了粘滞位，在该目录下的文件，只能是**root**和**创建者**可以删改，某个普通用户不能删除/改名/移动别人的文件。
  - drwxrwxrwt；置于o的x位置 1777

##  052 任务调度

### crontab 定时任务设置 （反复执行）

科隆表达式，科隆是古代掌握时间的神

- 定时调用脚本or指令

- crontab 

  - 设置任务调度文件：/etc/crontab

  - 设置个人任务到调度文件：

    先输入 crontab -e 

    再输入任务：

    */1 * * * * ls -l etc/ > /tmp/to.txt  (每小时的每分钟执行)

- 可以用工具生成？

- 实例：每隔一分钟，将当前日历和时间追加到mycal.txt中。

  - 思路：写一个脚本，里面包含两条指令，然后在crontab中添加定时任务执行脚本

    - 写脚本：

      ```shell
      vim my.sh
      ```

      写入：

      ```shell
      date >> /opt/mycal.txt
      cal >> /opt/mycal.txt
      ```

    - **给my.sh 添加执行权限：**

      ```shell
      chmod 744 /opt/my.sh
      ```

    - 添加定时任务：

      ```shell
      crontab -e
      ```

      写入：

      ```shell
      */1 * * * * /opt/my.sh
      ```

- 实例：每天凌晨两点，将数据库testdb备份到文件中

  ```shell
  crontab -e
  0 2 * * * mysqldump -u -proot testdb > /home/test.bak
  ```

### at 定时任务 （一次性执行）

- at是一次性定时计划任务，at的守护进程atd以后台模式运行，检查作业队列来运行。

  ps -ef | grep atd  (检测atd进程有没有在运行)

  atd守护进程每60 s检查一次作业队列，匹配则运行此作业

- at [选项] [时间]   然后输入指令  然后**ctrl+d 两次**

- arq 查看任务

- atrm [任务序号]： 删除任务

## 058 Linux 磁盘分区和挂载

### 磁盘组成

- 扇区sector：最小的物理储存单位。目前有512bytes和4k两种格式。

- 将扇区围成一个圆，叫磁柱。

### Linux磁盘分区

#### MBR

- 主引导记录，硬盘第一个扇区放着512字节的主要启动记录和分区表。
- 特点：最大支持2T硬盘，最多支持4个主分区；更多分区可以用扩展分区和逻辑分区来实现。

#### GPT

- 与MBR仅使用第一个512byte来记录不同，GPT使用了34个LBA区块来记录分区信息。
- 解决了主要分区的数量限制。
- 并不是所有操作系统都可以读取GPT分区，与开机检测程序有关。

- 分区与文件系统的关系

- 挂载：把某个目录分配磁盘的空间，将文件系统与目录树结合；挂载点一定是目录，该目录是进入该文件系统的入口。

- Linux分区

  - 一般采用SCSI硬盘，标识为 sda1、sda2、sdb1、sdb2等等
- 查看挂载情况：lsblk / lsblk -f

### 开机检测程序

> **即基本输入输出系统，是服务器启动后最先运行的软件。它包括基本输入输出控制程序、上电自检程序、系统启动自举程序、系统设置信息。**BIOS是服务器硬件和OS之间的抽象层，用来设置硬件，为OS运行做准备。**BIOS设置程序是储存在BIOS芯片中的。BIOS的进化版本是UEFI（Unified Extensible FirmwareInterface），即统一的可扩展固定接口。**这种接口用于操作系统自动从预启动的操作环境，加载到一种操作系统上，从而使开机程序化繁为简，节省时间。

#### BIOS

写入到主板上的程序，是开机的时候计算机运行的第一个程序。

- 上电后，**BIOS**会确认**硬件**是否正常运行，随后去找能够开机的硬盘，并且去读取MBR
- 没问题的话就**启动开机引导程序**。
- 引导程序的作用是把硬盘中的OS加载到内存中运行。（OS负责启动应用程序，但是OS没有办法自己启动自己，需要引导程序来启动。）
- 开机管理程序除了可以除了可以安装到MBR之外，还可以安装到分区槽的启动扇区（boot loader）中。实现多重引导。

#### UEFI

BIOS无法读取GPT格式；UEFI出现，为了代替BIOS。省去了开机自检，开机速度较快。

通常磁盘分区格式会与开机检测程序一起提到：

- legacy方式：MBR+BIOS方式
- UEFI+GPT方式

### 增加磁盘的操作实例

- 步骤1：虚拟机设置中增加一块磁盘

- 步骤2：分区命令 fdisk /dev/sdb

  输入 m 看说明；输入n分区；输入 p （primary）；输入分区数量；回车 回车 回车 全部默认

  再输入w 保存退出；（不想保存，输入q）

- 步骤3：格式化sdb1（指定文件格式）

  ```shell
  mkfs -t ext4 /dev/sdb1 # ext4
  mkfs.xfs /dev/sdb1 # xfs
  ```

- 步骤4 挂载到指定目录 mount /dev/sdb1 /...

​	**注意：**

​	**0.并不是所有目录都可以作为挂载点，挂载操作会使得原有目录隐藏，因此根目录以及系统原有目录不能作为挂载点**

​	**1.挂载点一定是已经建立的空目录**。（也可以不为空，但是挂载之后，已有的内容将不可用）

​	**2.用命令行挂载，是临时的，重启之后，会失效。**

​	**3.MBR分区用fdisk分区；GPT用gdisk分区**

- 步骤5：永久挂载

  修改/etc/fstab

  输入mount -a 即刻生效

  - fstab 文件
  
    每行数据分了六个字段
  
    1. 分区设备文件名或者UUID
    2. 挂载点
    3. 文件系统的类型
    4. 挂载参数 defaults等（auto/noauto代表是否会被mount -a主动测试挂载）
    5. 分区是否被dump备份 （0是不备份 1 代表备份 2 不定期备份）
    6. 分区是否被fsck检测  (0 不检测 1 高优先级 2 稍低的优先级) (先检测1优先级)
  
  - fstab的挂载记录是写入到/etc/mtab 和 /proc/mounts中。
  
- 重新挂载remount 

  ```shell
  mount -o remount,rw,auto /
  ```

  当进入单人维护模式时，根目录通常被重新挂载为只读，用这个命令重新挂载为rw
  
- 挂载image等大文件：mount -o loop

### 查看磁盘使用情况

- df -h ：查询文件系统占用情况，要是读取superblock信息，会非常快。

- du：查询**某个目录**的磁盘占用

  -s 指定目录占用大小汇总

  -h 带计量单位

  -a **含文件  （不写-a，列出来的仅仅是子目录；写上-a才是连文件带目录都列出来）**

  --max-depth = 1 子目录深度

  -c 列出明细，增加汇总值

- 实例：

  ```bash
  #查询/opt占用情况，深度为1
  du -hac --max-depth=1 /opt
  #按照目录占用空间大小排序本层目录里面的子目录
  du -sh * | sort -hr
  ```

- df （disk free）和 du (disk usage)的区别

  - 不同点：

    - 统计范围不同

      df统计磁盘总体使用情况；du既能统计总体使用情况，也能统计某个文件夹和文件大小

    - 计算方式不同

      df通过文件系统快速获取；du通过逐级进入目录来统计，相对较慢，如果没有文件夹访问权限也无法读取。

    - 计算结果差异

      df可以获取已删除的文件，由于df是通过文件系统获取空间大小，当删除一个文件之后，他不是立即消失的，而是确认没有进程使用它才完全删除。

      而du只能看到当前存在的未删除的文件。

- blkid

  查看文件系统和和装置的UUID

- parted

  列出磁盘的分区表类型和分区信息

  ```shell
  parted /dev/vda1 print
  ```

- partprobe

  更新核心分区表

### 工作常用指令

1. 统计/opt文件夹下的目录个数

   ```shell
   ls -l | grep "^-" | wc -l
   # 列出了目录内容容，用正则表达式筛选 - 开头的，-开头的就是文件，再用wc -l 列出文件个数
   ```

2. 统计/opt文件夹下目录的个数

   ```shell
   ls -l | grep "^d" | wc -l 
   ```

3. 统计/opt 文件夹下的所有文件个数，包括子文件夹下的

   ```shell
   ls -lR | grep "^-" | wc -l
   ```

4. 统计/opt 文件夹下的所有目录个数，包括子文件夹下的

   ```shell
   ls -lR | grep "^d" | wc -l
   ```

   **ls的递归列出文件 -R** 

5. 树形结构展示目录

   ```shell
   yum install tree
   tree /home/
   ```

### 逻辑卷管理 LVM

- What
  - Logical Volume Manager 逻辑卷管理，Linux中对磁盘分区进行管理的机制
- Why
  - 直接用fdisk挂载的话，当硬盘空间满了的话，必须挂载新硬盘，做数据迁移，导致业务暂停，不符合企业需求。
  - LVM可以自由调整文件系统大小，实现文件系统跨越不同磁盘和分区。封装底层物理硬盘，以逻辑卷的形式表现给上层系统，逻辑卷可以调整 

- About

  - 物理卷 physical volume：硬盘分区或者与分区具有相同功能的设备（如RAID）。PV是LVM的基本存储逻辑块，包含LVM的管理参数
  - 卷组 volume group：由物理卷组成，可在卷组中创建一个或多个LVM（逻辑卷）分区
  - 逻辑卷 logical volume：类似硬盘分区，可以格式化后挂载使用。
  - PE physical extent：物理卷划分为PE单元，是可被LVM寻址的最小单元，默认4MB

- summary

  一款硬盘，被格式化为物理卷（PV），其内部分为若干PE，在PV基础上创建了卷组（VG），可以把若干PV加入VG；VG相当于空间池，基于VG创建逻辑卷（LV），将LV格式化，再挂载。扩充LV的过程就是增减PE的数量，不会影响数据

### 磁盘阵列 RAID

- Redundant Arrays of Independent Disks. 利用许多独立的便宜磁盘，组成容量巨大的磁盘组，利用个别磁盘提供数据所产生的加成效果提升整个磁盘系统的效能
- 最大优点：提高数据传输速率，在多个磁盘上同时存储数据
- RAID0：数据并行写入每个磁盘，并行读取；但是没有冗余，一个盘坏掉，数据全部丢失。不适用于安全性要求高的场景
- 注意：别把空间不同的磁盘RAID，否则性能将会被限制在最小容量的那个盘

### 磁盘完整性检查 FSCK

- 磁盘没有mount的时候运行fsck

  ```bash
  umount /dev/sdc1
  fcsk -y /dev/sdc1  # -y可以自动修复错误
  xfs_repair /dev/sdc1 # xfs文件系统用这个
  ```


### 初始化磁盘（Initrd）

- 是系统引导过程中挂载的一个临时根文件系统，用来支持两阶段的引导过程，initrd中包含了各种可执行程序和驱动，可以挂载实际的根文件系统，然后再将initrd磁盘卸载，释放内存。

### 启动管理

- UEFI or BIOS？

  ```shell
  [ -d /sys/firmware/efi ] && echo UEFI || echo BIOS
  ```

- 版本？

  ```shell
  dmesg | grep -i "EFI"  # "BIOS"
  ```

- Check if secure boot?

  ```shell
  mokutil -sb-state
  ```

## 059 Linux文件系统

### EXT2 文件系统特性

inode、block、superblock

- inode：存放文件属性信息，一个文件占用一个inode；同时也记录该文件数据所在的block号码
- block：记录文件的数实际内容。
- superblock：记录此文件系统的整体信息，包括inode的使用量、使用总量等。

举例：假设一个文件的inode记录了文件数据的实际放置点为2 3 5 7，那么操作系统就可以据此排列磁盘的阅读顺序，一口气将多个block的内容都读取出来。这种数据存取的方法称为**索引式文件系统**。

与之对比的是FAT文件系统，没有inode存在，每个block记录了下一个block位置，像链表一样一个一个顺序来读。【碎片整理】说的就是FAT文件系统里面的bolck太过分散，通过碎片整理来将同一个文件的block汇总到一起。提升读写速度。

### block大小

- 文件大于block大小，会占用多个block；文件小于单个block大小，还是会占用单个block。
- block过大，存小文件会造成空间浪费；block过小，存大文件会造成block太多，读写缓慢。根据实际情况合理选择。
- 格式化的时候会分为多个block groups，每个组都有super block

### inode

- 每个inode大小固定（128 bytes for ext2；256 bytes for ext4 and xfs）。
- 文件系统能够创建的文件数量与inode数量有关。

### 查看ext文件系统信息

dumpe2fs /dev/sda1

### 目录的占用

- 目录也会被分配一个inode，存储目录的权限和属性，以及分配的block的号码；block则记录目录下的文件名以及每个文件的inode号码。
- 文件太多，一个block放不下的话，多个block来放。
- 注意：由于文件名是存储在block里面的，所以涉及到文件名修改的操作，需要目录的w权限。

### bitmap

- bitmap记录了文件系统中可用的inode和block信息
- inode bitmap，block bitmap和superblock称为metadata

### 一致性检查

如果在写入文件过程中，发生意外系统中断，造成inode、block与bitmap数据不一致。如果要检查就得整个文件系统检查。

### 日志式文件系统：ext4/ext4

在文件系统中规划出了一个区块，记录写入和修订文件的步骤：

- 预备：会在日志记录区中记录准备写入的信息
- 实际写入：开始写入文件的权限和数据，更新metadata的数据
- 完成数据和metadata更新后，记录为完成。

一致性出问题只需根据日志针对性的去找，快速恢复。

### 文件系统的读写运作

CPU只能读取内存中的数据，如果文件比较大，需要频繁写入磁盘、读到内存；会效率低下。

Linux采用异步（async）来处理：

- 系统加载到内存，如果文件被更改过；该内存区段的文件会被标记为dirty；没改过就是clean；磁盘会不定时将dirty的文件写回磁盘，保持内存磁盘的一致性。
- 可以手动采用sync来将dirty数据写回到磁盘；正常关机之后会调用sync；但是非正常关机之后，数据未写入磁盘，再次启动可能会导致文件系统损坏。

### 其他文件系统

更新的速度更快的文件系统，比如xfs、reiserfs等。CentOS7开始，预设的文件系统已经开始默认为xfs了。

```shell
# 查看Linux支持的文件系统有哪些。（这个路径下是支持的文件系统的驱动程序）
ls -l /lib/$(uname -r)/kernel/fs
```

### xfs文件系统简介

ext文件系统是预先规划出所有的inode/block/superblock，不再需要进行动态配置；在磁盘容量巨大之后，格式化的时候会特别慢。而xfs文件系统就被用于高容量磁盘和高性能文件系统而用。

#### 组成

- 资料区

  存放superblock、inode分配与追踪；inode和block都是系统需要的时候才动态配置产生。

- 文件系统活动登陆区

  记录文件系统的变化；异常中断后，系统会拿这个区块进行一致性检验修复，有点像日志区。

- 实时运作区

  有文件要建立的时候，xfs会将文件暂时放置在里面，inode分配完毕之后再写到data section中。

### 查看信息

```shell
xfs_info
```

![image-20221017185539855](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202210171855949.png)

### 修改UUID和label name

xfs_admin 和 tune2fs

## Cloud 相关配置

### waagent

- Windows Azure Agent 控制了资源盘和交换区

- resource disk

  - temporary storage （located in /dev/sdb1）in VM
  - 重启不友好，灾难恢复后VM重新分配

- waagent 日志路径

  /var/log/waagent.log

- 交换区 

  - 作用：当物理内存不够用的时候，释放一部分内存；被释放掉的进程可以先保存在交换区内；等到有空间时再加载回去
  - 启用交换区

  ```shell
  vim /etc/waagent.conf  # waagent means Windows Azure Agent
  ```

  - 修改参数：


  ​	ResourceDisk.Format=y

  ​	ResourceDisk.EnableSwap=y

  ​	ResourceDisk.SwapSizeMB=4096

### cloud-init

- 云端部署时，设置默认配置
- waagent是Azure专属；cloud-init是通用；后者可以覆盖前者

### extension

- 部署之后的一些扩展功能
- 可通过CLI Powershell Azure Resource Manager启动
- 查看extensions路径：/var/log/azure/*

## 063 网络配置

- windows查看VMnet8网络配置 （ipconfig）
- Linux查看网络配置 ifconfig  （interface configuring）

### IP获取方式

- 自动获取：自己用可以，但服务器不适用
- 指定IP：详见老韩图解

### 设置主机名和hosts映射

- hostname 查看主机名
- hosts文件是主机名和IP地址的映射
- windows：C:\Windows\System32\drivers\etc\hosts 中指定主机和IP映射即可
- Linux：/etc/hosts  指定主机名和IP的映射，在不适用DNS服务器的情况下

### interface设置

- 路径：/etc/network/network-scripts/ifcfg-**eth0**(device名)

### 验证DNS域名解析

- **dig** @8.8.8.8 Microsoft.com
  - A 地址记录，用来指定域名的 IPv4 地址，如果需要将域名指向一个 IP 地址，就需要添加 A 记录。
- **nslookup** microsoft.com
- **getent hosts** microsoft.com
- 本地DNS解析：/etc/hosts
- DNS优先级定义：/etc/nsswitch.conf
- **/etc/nsswitch.conf** 这个文件定义了DNS解析的优先级过程，默认下，先从本地寻找（**/etc/hosts**），如果找不到，再从**/etc/resolv.conf**中定义的DNS服务器中寻找
- **nslookup**和**dig**直接从**/etc/resolv.conf**中定义的nameserver寻找，并不会查找本地/etc/hosts；然而**getent**会按照**/etc/nsswitch.conf** 定义的顺序来查找（默认时就会先查找/etc/hosts）

### 检查端口监听状态

```shell
netstat -an | grep 80 | grep LISTEN
```

### 连接端口

- 使用netcat telnet curl 连接指定端口  （http80 https 443）
- netcat 亦可检查UDP连接；telnet只能检查TCP连接

### 路由表

- Information on how packets are forwarded

- Assist customers to add static route

- check routing table

  ```shell
  netstat -r
  route -n
  ```

- Add route

  ```shell
  route add -net 10.0.2.0 netmask 255.255.255.0 dev eth0
  route add -net 127.0.0.0 netmask 255.0.0.0 lo  # add loopback interface
  route add default gw 192.168.10.1  # add default gateway
  ```

### iptables

- a set of rules to decide what to do

- Rules are organized into groups called **chains**

  INPUT: This chain handles packets that are addressed to your server

  OUTPUT: This chain handles packets that are created by your server

  FORWARD: Configure your server to route requests to other machines

- Chians contain 0 or more policies including ACCEPT/DROP/REJECT

- how to check

  ```shell
  iptables -S
  iptables -L
  ```

### Network trace

- Net connectivity problem - network captures from source to destination to analyze

- **tcpdump** : most commonly used tool to capture or filter packets

- eg

  ```shell
  tcpdump -w /tmp/traces.pcap -i eth0  # capture traces in device eth0 and save it
  ^C
  ls -l /tmp/traces.pcap
  ```

### Network File Share (NFS)

Azure Linux Academy - Foundation P.104   

### Firewalld basics

- Zones utilized for trust for network connections: block, drop, public, external, dmz, internal, trusted, work, home.

- firewalld

  ```bash
  firewalld-cmd --state # check status
  firewalld-cmd --list-all # list configuration
  firewalld-cmd --get-zones # list zones
  firewalld-cmd --get-active-zones # list active zones
  firewalld-cmd --list-services # list allowed services
  firewalld-cmd --list-ports # list allowed ports
  firewall-cmd --add-service=<service name> --zone=<zone name> --pernament # allow a service
  firewall-cmd --add-port=<port number/protocol> --zone=<zone name> --permanent # allow a port
  firewall-cmd --remove-service=<service name> --zone=<zone name> --permanent
  firewall-cmd --remove-port=<portnumber/protocol> --zone=<zone name> --permanent
  firewall-cmd --reload
  
  ```

### SELinux

- An architecture for Linux that defines access to apps, processes, files by security policies.
- Configuration file: /etc/sysconfig/selinux  (symlink to /etc/selinux/config)
- SElinux modes: enforcing (policies are enforced), permissive (logs warnings/violations), disabled
- SElinux policies: Targeted, miminum, MLS
- How it works:
  - all files, processes, ports have a label and are logically grouped 
  - Access Vector Cache (avc) caches permissions and is checked shen a request is made.
  - If permission is denied, an "avc:denied" massage appears in /var/log/messages and /var/log/audit/audit.log	

```
sestatus  
getenforce  # check status of selinux

setenforce 0 # temporarily enable permissive
setenforce 1 # temporarily enable enforcing
```

- Trouble shooting

  ```shell
  grep -i denied | /var/log/audit/*  # 找到日志里面带denied的信息
  ```


## 068 进程管理

- 执行中的程序都是一个进程，每一个进程分配一个PID。程序是静态的，程序run起来，加载到内存中，就是一个进程。
- 每个进程可能以两种方式存在，**前台** or **后台** ， 一般而言，系统服务以后台形式常驻

### 显示进程

- ps

  - 字段 PID、TTY（终端机号）、TIME（消耗CPU时间）、CMD（进程名）

  - -a 显示所有进程；-u 以用户格式显示进程；-x 显示运行参数

  - 常用：

    ```shell
    ps -aux | more
    ps -aux | grep ...
    ps -ef # 与-aux一样，只是显示的格式不同
    ```

    VSZ：进程占用虚拟内存大小

    RSS：进程占用的物理内存大小

    TT：终端名称

    STAT：进程状态

- 查看父进程，可以用ps -ef | more

  ps -ef 能显示出父进程号（PPID）

- pgrep -l 进程名 （查找指定名称的进程）

### 终止进程

- kill [选项] 进程号

- killall 进程名    （子进程同时被杀掉）

- 常用选项 -9  强迫终止

- 案例：

  1、踢掉非法登录用户

  ```
  ps -ef | grep sshd   # sshd 远程连接服务 先查看sshd的进程号
  kill 11421 
  ```

  2、暂停远程登录功能

  ```shell
  ps -ef | grep sshd # 找到名称为/usr/sbin/sshd -D的进程号
  kill xxxxx
  # 恢复远程登录
  /bin/systemctl start sshd.service
  ```

  3、终止多个gedit

  ```shell
  killall gedit  # 这是一种编辑器
  ```

  可以用于系统负载过大变卡

  4、强制杀掉终端

  ```shell
  kill -9 11405
  ```

### 查看进程树

- pstree -p (带进程号)
- pstree -u （带用户名）

### 服务管理

- 服务是运行在后台的进程，例如 mysqld，SSHD  （d：deamon 守护进程）

  mysqld、sshd守护进程 分别通过3306 or 22 端口进行监听。network停止之后，监控端口就关闭了

- service [status | start | stop | reload]  service在CentOS7.0之后被弱化，更多的是systemctl

- setup 可以看到所有服务

  [*]的是自动启动的服务，按空格可以取消


### 服务的运行级别

- 0 - 6 与前面的级别一样 （常用的是3 和 5）

- 开机流程

  开机 -> BIOS -> /boot -> systemd 进程1  -> 运行级别 -> 运行级别对应的服务

- 设置运行级别的自启动 chkconfig

  让某些服务，在某个运行级别下自启动或者不启动，重启机器生效

### systemV和systemd

- `SystemV`和`systemd`都是Linux系统中的初始化系统（init system），负责在系统启动时启动和管理系统服务。

- `SystemV`是一个传统的初始化系统，它使用脚本来启动和停止服务。这些脚本通常位于`/etc/init.d/`目录下，服务的启动顺序由这些脚本的名字决定。

- `systemd`是一个新的初始化系统，它使用单元（units）来管理服务。这些单元的配置文件通常位于`/etc/systemd/system/`目录下，服务的启动顺序由这些配置文件中的依赖关系决定。

他们的主要区别如下：

- 启动速度：`systemd`使用并行处理来加快启动速度，而`SystemV`则是按顺序启动服务。
- 配置方式：`systemd`使用单元配置文件，而`SystemV`使用脚本。
- 日志管理：`systemd`内置了日志管理系统`journald`，而`SystemV`没有内置的日志管理系统。
- 依赖管理：`systemd`可以自动处理服务之间的依赖关系，而`SystemV`需要手动管理。

### 服务管理

- systemctl   管理指令

  systemctl [start | stop | restart | status]  （start和stop重启失效；enable是永久性）

  systemctl指令管理的服务在 **/usr/lib/systemd/system**   可在里面查找服务名

- systemctl 设置服务的**开机启动**状态

  systemctl list-unit-files [| grep 服务名] 查看服务的自启动状态

  systemctl enable | disable 服务名 （设置服务开机启动，3和5的运行级别同时生效）

  systemctl is-enabled  查询是否是自启动的

- 讲了**firewalld** 防火墙守护进程

  firewalld中关闭的端口无法被外部程序访问到；关闭防火墙之后，相当于裸奔

  防火墙相当于家里防盗门；端口相当于家里的成员

- firewall 指令 可以管理端口

  - 打开防火墙，外部请求数据包，无法与内部端口进行通讯，所以需要手动开启某些端口

  - 打开端口：firewall-cmd --permanent --add-port=端口号/协议

    关闭端口：firewall-cmd --permanent --remove-port=端口号/协议

  - 操作完后，得重新载入才能生效：firewall-cmd --reload

  - 查询端口是否开放：firewall-cmd --query-port=端口号/协议

  - 举例：查看111端口

    firewall-cmd --query-port=111/tcp

- 高位端口？

### Service trouble-shooting

- Init and systemd

  - init is a process trees

- Service

  - process that run in background, mainly for resource management, interface to access resources

- traditional init systems: SysV and BSD

  other init schema: SMF, launchd, PoenRC, Upstart

- systemctl and journalctl

  - systemctl: control services; journalctl: read and filter systemd journal

- other important commands and services

  - commands: timetablectl (synchronizayion), hostnamectl(hostname, location, ...), systemmd-resolve
  - services: 

- Tools in systemd commands:

  - systemctl

    ```bash
    systemctl status service
    journalctl -u service
    systemctl cat service
    systemctl list-dependencies service
    ```


### 动态监控进程

**top**

- 与ps相似，不过可以更新

- top -d 秒数   （每隔5秒，默认是3 s）

  top -i  （不显示闲置进程）

  top -p PID （指定监视某个进程）

  load average：三个值平均值大于7%的话说明负载过大，需要优化

  zombie 僵尸进程，进程已经死掉，但是仍然占用着内存

  %CPU 的各项指标含义 ：

  - `us`：用户空间占用CPU的百分比。
  - `sy`：内核空间占用CPU的百分比。
  - `ni`：用户空间内改变过优先级的进程占用CPU的百分比。
  - `id`：空闲CPU百分比。
  - `wa`：等待I/O的CPU时间百分比。
  - `hi`：处理硬中断的CPU时间百分比。
  - `si`：处理软中断的CPU时间百分比。
  - `st`：在虚拟环境中等待实际CPU的百分比。

- top 交互操作

  在动态显示界面 输入：

  P （按照%CPU排序）

  M （按照内存排序）

  N （按照PID排序）

  输入k 再输入进程号，就直接杀掉了；强制结束可以继续输入 9  （9是信号量）

​	  剔除用户：就是kill掉该用户的bash进程。

### 监控网络状态

- **netstat -anp** [-an 按照一定顺序排列输出 -p 显示哪个进程在监听端口]

  - 0.0.0.0:22  本地程序在监听22端口


  - 192.168.13.128:22 这是本地Linux的IP地址和端口


  - 192.168.13.1:8226 这是windows中xshell的IP与端口

- ### 验证端口

  ```shell
  netstat -tulpn | grep -i ssh
  ```

## rpm包管理

### 介绍

- rpm：RedHat Package Manager  软件包管理工具，.RPM扩展名的文件。虽然是基于RedHat 但是被广泛采用，算是行业标准。

### 查询已安装的rpm

- rpm -qa | grep firefox

- 返回结果：firefox-60.2.2-1.el7.centos.x86_64

  - 名称：firefox

  - 版本号：60.2.2-1

  - 适用操作系统：el7.centos.x86_64 （如果是i686、i386表示32位系统，noarch表示通用）

### 其他查询指令

- rpm -qa  查询所有已安装的rpm软件包
- rpm -qa | more、grep
- rpm | q 软件包名 查询软件包是否安装
- rpm -qi  查询软件包信息
- rpm -ql 查询软件安装到哪里了，包里包含着什么文件
- rpm -qf [文件]  查询这个文件隶属于哪个rpm包

### rpm包卸载

- rpm -e 包名（比如只写firefox即可）  //erase的意思
- 注意：如果其他软件包依赖你要删除的软件包，可能会报错

### rpm安装

- rpm -ivh RPM包全路径名称  （install 安装；verbose 提示；hash 进度条）

### yum

- shell前端包管理器，基于RPM管理，可以自动下载安装，处理依赖性关系。
- yum list | grep xxx  查询服务器是否有需要安装的软件；yum list installed | grep xxx 查询已安装的
- yum install xxx  下载安装
- yum -y install xxx  安装过程中的选项都默认自动选择

### EPEL

Extra Packages for Enterprise [Linux](https://www.linuxprobe.com/)

Fedora推出的免费软件包的源

### 干净重装 (以 waagent为例)

1. Stop

   ```shell
   systemctl stop waagent
   ```

2. Move current /var/lib/waagent

   ```shell
   mv /var/lib/waagent /var/lib/waagent.old
   ```

3. Unintsall

   ```shell
   yum remove WALinuxAgent -y
   ```

4. Reinstall

   ```shell
   yum install WALinuxAgent -y
   ```

5. Restart the Azure waagent

   ```shell
   systemctl start waagent
   ```

6. Validate current status

   ```shell
   systemctl status waagent
   ```

7. check contents

   ```shell
   ls -l /var/lib/waagent
   cat /var/log/waagent.conf
   ```

8. Check extensions

   ```shell
   cd /var/log/azure
   ls -l
   ```

### 包管理 Package Management

- Package：一个压缩文件，包含一个特定应用的所有文件。可以是.rpm .deb .tgz 类型

- Packages stored in **respositories** which is a collection of packages. (资源库)

- Linux respositories: a storage location from which system retrives and installs OS updates and applications

- 查看仓库：

  ```bash
  yum repolist all
  ```


## 打印服务

Common UNIX Printer System （CUPS）

- Package name

  cups

## 系统信息查看

可以用 stress功能

```shell
# 首先安装EPEL源
yum -y install epel-release
# 再安装stress
yum --enbaleerepo=epel install stress -y
# 复制一个Terminal，查看CPU
stress -c 4
# CPU
cat /proc/cpuinfo
# memory
cat /proc/meminfo
# 内存 缓存 交换区
free -m
```

### 系统行为报告

System Activity Report

```shell
yum install sysstat -y
systemctl enable sysstat
systemctl start sysstat
sar
```

### sosreport

把系统配置、诊断信息等打包起来，可以发给Technical Support

### OS 信息查看

- 查看OS版本

  ```shell
  cat /etc/*release
  ```

- 查看kernel信息

  ```shell
  uname -a
  ```

- 查看安装的版本

  ```shell
  lsmod
  ```

- 查看CPU信息

  ```shell
  cat /proc/cpuinfo
  ```

- 查看存储信息

  ```shell
  cat /proc/meminfo
  ```

- 查看kernel参数

  ```shell
  sysctl -a
  ```

## 默认kernel变更

- 启动时，如果有多个kernel存在，可以选择用哪个。通过GRUB（grand unified bootloader），GRUB配置文件：/boot/grub/grub.conf或者/boot/grub2/grub.cfg

- 在一些case中，客户升级了kernel后，VM不能重新启动，所以我们要更改grub配置

  查看所有kernel版本

  ```shell
  awk -F \' '$1==menuentry " {print $2}' /boot/grub2/grub.cfg
  ```

  查看默认启动kernel版本

  ```shell
  grep -i default /etc/default/grub
  ```

  改变kernel默认启动版本

  ```shell
  vi /etc/default/grub
  # GRUB_DEFAULT = saved (saved意思是使用GRUB_SAVEDEFAULT变量所保存的，或者grub-set-default命令设置的选项作为默认)
  grub2-set-default 1  # 这里的序号是系统中存在的kernel列表从0开始的编号
  ```

  将配置写入cfg文件，以永久保存

  ```shell
  grub2-mkconfig -o /boot/grub2/grub.cfg
  ```

  重启

  ```shell
  reboot
  uname -r
  ```

## 日志管理

### 日志简介

- 系统信息文件，记录系统事件

  常用日志的位置：

- 日志管理服务

  - CentOS6：**syslogd**；CentOS7.6：**rsyslogd**

  -   查询日志管理服务是否启动：

    ```shell
    ps aux | grep "rsyslog"
    systemctl status rsyslog.service
    systemctl list-all-units | grep rsyslog
    ```

- 日志配置文件

​		/etc/rsyslog.conf

​		记录了什么日志往哪放；还有日志级别：

- 日志轮替

  - 配置文件：/etc/logrotate.conf

  - 被轮替下来的日志会被命名为 xxx1.log，再被轮替下来就会有 xxx1.log和 xxx2.log，可以设置最大保存的副本数量。

  - 也可以设置日志大小必须超过多少MB才会被轮替，不到这个大小，即使到了规定的轮替时间也不会被轮替。

  - 日志轮替是通过系统定时任务来实现的。**rsyslogd负责往哪里写什么，logrotate后台定时任务负责什么时候写和删除**

- 查看内存日志
  - 有一部分日志是先写到内存里，还没写到文件里；内存日志重启就清空了
  - journalctl -o verbose

## 数据备份dump

### 语法说明

- dump - [cu c是个具体数字：0123456789] [-f 备份后文件名] -[T 日期] [目录或者文件系统]
  - -0123456789 ：备份层级，0为最完整备份，>0是增量备份，指定最多备份几次。

- 注意：xfs文件系统要用xfsdump；ext4才能用dump命令

## Shell 编程

### 基础

- shell是命令行解释器，负责向Linux内核发送请求

- 脚本格式要求

  - 脚本以 #!/bin/bash 开头 

- 脚本执行方式

  - 方式1 赋予x权限，再执行

    ```shell
    chmod u+x /opt/shcode/hello.sh
    ./hello.sh
    ```

    方式2 sh +脚本 不用赋予权限也能执行

    ```shell
    sh hello.sh
    ```

### 变量

- 系统变量：$HOME $USER $PATH $PWD $SHELL 等；用户自定义变量

- 显示系统中的所有变量 set

- 变量定义：

  - 定义：名字=值 （注意：中间不能有空格）
  - 撤销变量：unset A （变量名）
  - 声明静态变量：readonly 变量 无法被unset
  - 注：vim中显示行号：命令行模式 :set nu
  - 规则
    - 变量定义中等号两侧不能有空格
    - 变量名习惯为大写字母，不能以数字开头
    - 将某条命令的返回值赋值给变量：
      - A=\`date\` (`是反引号)  或者  A=$(date) 

- 环境变量

  - 基本语法

    - 在/etc/profile中加入 export 变量名=变量值  （将shell变量输出为环境变量/全局变量，可以被多个文件共用）
    - source /etc/profile  (写入新的环境变量之后，应该用source刷新一下)

    - echo $变量名

  - 注：多行注释

    ```shell
    :<<!
    xxxx 
    !
    ```

- 位置参数变量

  - 运行脚本时，希望获取到命令行手动输入的一些参数，就要用到位置参数变量。例如 sh myshell.sh 100 200，100 200这两个参数就能被传进去
  - 基本语法：
    - **$n** n=代表命令本身；**n=$1**代表命令行传入的第一个参数；n=$2-9；n=${10} 10以上要用{}
    - **$*** 代表所有参数；**$@**也代表所有参数，把各个参数区分对待？ $#代表参数的个数

- 预定义变量

  - 基本语法

    - **$$**当前进程号PID；$!后台运行的最后一个进程号PID；**$?**最后一次执行命令的返回状态，0代表成功，非0代表失败

    - 在shell脚本中运行另一个脚本

      ```shell
      /opt/shellcode/myshell.sh &
      ```

### 运算符

- $((运算式)) 或者 $[运算式] 或者 expr m + n (这种写法 运算符之间有空格)；想把结果赋给某个变量，要用 ``
- expr 乘 \\* 除/ 取余%   （用了expr才要用转义）

### 判断语句

- ```shell
  if [ 23 -ge 22 ]  # [xxx]非空返回true true就是0；[ ]空的就返回false，false是>1;判断符与数字之间有空格，[ 后面 与 ] 前面都有空格
  then echo "greater" 
  fi
  ```

- 判断条件

  - = 字符串比较

  - 整数比较

    - -lt 小于；-le 小于等于；-eq 等于；-gt 大于；-ne 不等于

  - 文件权限判断

    -r -w -x

  - 文件类型判断

    -f 文件存在并且是常规文件

    -e 文件存在

    -d 文件存在并且是个目录

    ```shell
    if [ -f aaa.txt ]
    then
    	echo "Yes"
    fi
    ```


### 流程控制

- if

```shell
if [ condition ]
then
代码
fi

if [condition]
then
代码
elif
代码
fi

if [ condition ]
then
代码
else
代码
fi
```

- case

```shell
case $1 in
"1" )
echo "one"
;;

"2")
echo "two"
;;
*)

echo "other"
;;
esac
```

- for

  ```shell
  # 方式1
  for i in "$*" # $*把命令行参数看作一个整体；$@分开看命令行参数
  do  
  	echo "num is $i" # i在in的里面就不停的输出；但是因为$*看作整体，所以一次就一口气全输出了；$@有几个参数，for就输出几次
  done
  
  #方式2
  SUM=0
  for((i=1; i<=100; i++))  # 这里；后面要有空格 小括号旁边没有空格
  do
  	SUM=$[$SUM+$i]
  done
  ```

- while

  ```shell
  while [ condition ]   # 只要是中括号后面就一律加上空格
  do
  代码
  done
  
  SUM=0
  i=0
  while [ $i -le $1]  # 中括号里面的条件判断不能用<= 还得用 -le那一套
  do
  	SUM=$[$SUM+$i]
  	i=$[$i+1]  #自增操作
  done
  ```

  ### 读取输入read

  read(选项)(参数)

  -p 指定读取时的屏幕输出提示符

  -t 指定读取时的指定时间，超过时间没输入就不等待了	

```shell
read -p "Input NUM1=" NUM1
echo "num1=$NUM1"

read -t 10 -p "Input NUM2=" NUM2
echo "num2=$NUM2" 
```

### 函数

系统函数和自定义函数

- 系统函数

  - 例如：basename 返回完整路径 / 最后的部分，用于获取文件名
  - basename [pathname] [suffix]
  - dirname 返回完整路径 / 前面的部分

- 自定义函数

  function funname()

  {

  ​	action;

  ​	[return int;]

  }

### shell 编程综合案例

- 需求：

  - 每天凌晨2:30备份
  - 备份开始结束，给出提示信息
  - 备份文件以时间为文件名
  - 检查是否有10天前的备份文件，有的话就删除

- 思路分析：

  编写脚本实现2 3 4项功能，用crond定时执行即可

```shell
#!/bin/bash

# Backup to which location
BACKUP=/opt/shcode/backup

#get current time
DATETIME=$(date +%Y-%m-%d_%H%M%S)

#judge if backup location exists
# 这是一个短路与 表达式 []里面的表达式为真 则执行&&后面的；这里是如果文件夹不存在的话，就创建一个 mkdir -p 代表创建多级文件夹
[ ! -d "${BACKUP}/${DATETIME}" ] && mkdir -p "${BACKUP}/${DATETIME}"

#create tar.gz for fun.sh
tar -zcvf /opt/shcode/fun.sh ${BACKUP}/${DATETIME}/${DATETIME}.tar.gz

# create tar.gz for the directory then remove the tar.gz file
cd ${BACKUP}
tar -zcvf ${DATETIME}.tar.gz ${DATETIME}
rm -rf ${BACKUP}/${DATETIME}

# remove the backupc files which is created before 10 days；
#find -atime 表示寻找到多少天之前的文件；-exec 表示对前面生成的文件进行操作；{}表示对前面所有文件；/;表示结束符
find ${BACKUP} -atime +10 -name "*.tar.gz" -exec rm {} \;
echo "Backup completed"
```

## Ubuntu

### root用户

- 一开始root没有密码，用su命令会失败；要先设置密码：

  ```shell
  sudo passwd
  ```

  设置好密码再用su，输入密码即可切换为root用户

- $ 代表普通用户；# 代表root用户

### apt

- Advanced Package Tools

- 国内的镜像网站：会定时去国外服务器同步资源，访问速度会快一些。可以在sourcelist里面设置成从镜像网站安装，例如，在清华大学镜像站中，找到使用帮助，在对应系统版本中找到sources.list的配置

- 常用命令 （新版Ubuntu用apt代替apt-get）

  sudo apt-get update

  sudo apt-get install xxx

  sudo apt-get remove xxx

  sudo apt-cache show xxx（获取包的相关信息）

  sudo apt-get source xxx (下载该包的源代码)

### 远程登录

- SSH：Secure Shell：是建立在应用层和传输层的安全协议；如果A机器想要被B机器远程操作，A要安装SSH服务器，B要安装SSH客户端

- Ubuntu 默认没有安装ssh服务

  ```shell
  apt install openssh-server
  ```

-    打开sshd服务

  ```shell
  systemctl restart sshd
  ```

- 从一个Linux登录到另一个Linux (服务器集群中有用)

  ```shell
  ssh username@ip # 输入目标服务器的登陆用户名和密码
  ```



# Redhat Enterprise Administrator Guide

## Chapter 1

### System locale （specify bitmap fonts and code pages）

- stored in /etc/locale.conf
- system locale and keyboard can be configured by **localectl**

## Chapter 2

### Date and time

- RTC (real time clock): hardware clock. Independent, run even shut down
- UTC (Coordinated Unviersal Time); DST (daylight saving time): local time
- **timedatectl** **date** **hwclock** : configure the system clock
- after changes made, use **systemctl restart systemd-timedated.service** to restart
- Changing current time\date : **timedatectl set-time HH:MM:SS / YYYY-MM-DD HH:MM:SS**
- Changing time zone: **timedatectl list-timezones** / **timedatectl set-timezone xxx**
- sync with remote server **timedatectl set-ntp yee/no**
- **hwclock /etc/adjtime**

- if NTP is used, hardware clock automatically synchronized every 11 mins.

- Recommand to keep the hardware clock in UTC.

## Chapter 3

### Users and Groups

- The settings defines what permissions are applied to a newly created file or directory is **umask**, which is configured in /etc/bashrc. Default is **022**, which only allows creators to modify, even creator's group are not allowed.
- a list of groups: /etc/group

### Passwds

- /etc/passwd move to-> /etc/shadow which is only read by root user. Passwd aging Policy is also contained

- Users setting tool (Graphical): Super -> Users

- Connamd line tools:

  - useradd usermod userdel
  - groupadd groupmod groupdel
  - gpasswd: for administering /etc/group

  - pwck, grpck
  - pwconv, pwunconv; grpconv, grpunconv

- Default UID range:

  - Previously 1 - 499 : system users; 500 + normal user

    now:      1 - 999 : system users; 1000 + normal user

    Default ranges of UID and GID can be changed in /etc/login.defs

- Dafault GID range:

  - below 1000 are for system and could not be used by users

- useradd user1

  then /etc/passwd is changed as follow:

  ```shell
  user1:x:1001:1001::/home/user1:bin/bash
  # user name；x: systyem using shadow passwd; UID; GID; GECOS left blank;home directory;default shell
  ```

  Meanwhile, /etc/shadow /etc/group /etc/gshadow is also changed accordingly

  /home/user1 is added. but this new user is activitated after the root user set a passwd 

### group directories-setgid bit

Situation: By default, in a directory, when sb. creates a file, it belongs to the primary group he belongs.

Setgid bit：对一个目录设置，目录中的文件 便自动会分配上 [与目录的组相同] 的组。让文件执行者以 目录组 的权限去执行。

Eg：

Several users are working on files in /myproject; some are trusted to modify files.

```shell
mkdir /myproject
groupadd myproject
chown root:myproject /myproject
chmod 2775 /myproject  # setgid bit设置为2了
ls -ld /myproject
usermod -aG myproject username # add user into myproject group 
```

## Chapter 4

### gain privilege

- A special administrative group called **wheel**

  ```shell
  useradd -aG username
  ```

  you can configure who has the privilege to use **su** and **sudo** command

  - edit PAM configuration file for su: /etc/pam.d/su

    uncomment it:

    ```shell
    # auth	required	pam_wheel.so 	use_uid
    ```

    which means that only **members in wheel** can use su command.

  - **/etc/sudoers** in default: gives every user in wheel group with unlimited root access.

  - only users listed in **/etc/sudoers** are allowed to use **sudo** command

    - each successful authentication using sudo is logged into **/var/log/messages**,

    - issuer's name is logged into **/var/log/secure**

      - which one to be logged can be controlled in **/etc/pam.d/system-auth**:

        add line: **session	required	pam_tty_audit.so disabled=user1,user2 enabled=user1,user2**

    - To give sb. full privilege to use sudo:

      type **visudo**  (visudo is a tool to manage /etc/sudoers)

      find sth like root ALL=(ALL) ALL

      add username ALL=(ALL) ALL

      which means username can use sudo from any host and execute any command

    - sudoers' passwd intervals can also be managed.


## Chapter 5

### Registering

- **subscription-manager register** (register your system with the same username and passwd as Redhat Customer portal)

- **subscription-manager list --available** (lsit all subscriptions)

- subscription-manager attach --pool=pool_id (attach a subscription to the system)

  - after system subscribed, a repository file is created in /etc/yum.repos.d/
  - use **yum repolist** to check

- remove subscription

  - check sub lists: **subscription-manager list --consumed**

  - find serial number
  - **subscription-manager remove --serial= *serial_number***

## Chapter 6

### Redhat support tool

- install -> register

### Case management

- Open and update
- viewing cases

## Chapter 9

### OpenSSH

- client-server architecture, encoded session, more secure than telnet
- openssh package required
- version1 and version2 

### Configuring OpenSSH

- files  记录着服务端、客户端的一些身份验证信息等
  - system-wide files: **/etc/ssh**
  - user-specific files: **~/.ssh/**
  - 如果重装了系统，可以备份相应的文件夹，以恢复之前的设置 

- generate key-pair then send the public key
- configure ssh-agent
- using ssh-client
- scp: file transfer between machines, encrypted
- sftp: open an FTP session

### X11 

Previously insecure port connections between systems can be mapped to specific SSH channels

- yum group install X windows system
- X11 forwarding

## Chapter 12

- Client - server architecture
- server -> recipient's server -> recipient's client

### Emial transport protocols

- SMTP
  - no authentication, making junk email, use **relay restriction** to limit it

### Email access protocols

used by clients to retrive email from servers，规定了怎样将个人计算机连接到网络上的邮件服务器的协议

- Post office Protocol (POP) 

  - 用户将邮件从服务器上下载到本地主机，同时删除服务器上的邮件
  - Redhat use **Dovecot** provided by dovecot package to use POP server
  - email are downloaded by email client apps
  - compatible for Internet standards, such as **Multipurpose Internet Mail Extensions (MIME)**, which allows **Mail Attachments**

  - most current version: POP3; POP3s service provided SSL encryprion

- Internet Message Access Protocol (IMAP)
  - 从客户端收取的邮件都保留在服务器上，同时在客户端的操作在服务器上都有标记
  - emails remain on the server which can be checked 
  - dovecot is also used;SSL is also supported by using syunnel program

### Email program

- Mail Transport Agent
  - use SMTP (Simple Mail Transfer Protocol), 一组用于从源地址到目的地址传输邮件的规范，控制邮件的中转方式，属于TCP/IP协议簇
  - Postfix and Sendmail
  - fetchmail: retrieves email from remote servers and delivers it to the local MTA

- Mail Delivery Program
  - Procmail: deliver email to be read by client apps
- Mail User Agent
  - ### Graphical: Evolution; text-based: Mutt 
