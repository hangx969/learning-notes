---
title: Linux 学习笔记
tags:
  - linux
  - shell
  - system-admin
  - ssh
  - zsh
  - network
  - monitoring
aliases:
  - Linux基础
  - Linux学习笔记
  - SSH连接
  - 配置zsh终端
  - Linux系统信息查看
  - direnv环境变量管理
  - Samba SMB文件共享
---

# Linux 学习笔记

这篇笔记按主题整理 Linux 基础、常用命令、系统管理及发行版操作。示例分别来自 CentOS 7、RHEL、Ubuntu、Azure 等环境；执行前请核对发行版版本、设备名和路径。

## 阅读导航

- [[#入门与虚拟机]] · [[#终端与常用命令]] · [[#用户、权限与计划任务]] · [[#存储与文件系统]]
- [[#云平台与网络]] · [[#进程、软件与系统服务]] · [[#脚本与自动化]] · [[#发行版操作补充]] · [[#RHEL 管理摘录]] · [[#Linux 运维实操专题]]

## 入门与虚拟机

### 学习路径

建议按以下顺序学习：

1. 掌握基本命令和文件目录操作。
2. 学习网络、存储等系统配置。
3. 编写 Shell 脚本，理解系统调优。
4. 进一步研究 Linux 内核。

先建立整体认识，再查阅命令用法并动手练习；在会用的基础上理解原理。入门内容包括 Linux 安装、Vim 和目录结构。

### Linux 的应用场景

- **服务器与运维**：运行网络服务、开发项目和自动化任务，是 Linux 的主要使用场景。
- **开发环境**：支持 Java、Python、PHP、C 等语言及其工具链。
- **嵌入式设备**：可以按设备需求裁剪系统和定制内核。

### Linux 概览

Linux 是内核；发行版在内核之上组合系统工具、软件包及管理方式，面向桌面、服务器或嵌入式等用途。常见发行版包括 Ubuntu、Debian、Fedora、RHEL、CentOS Stream、openSUSE 和 Oracle Linux。

- **Debian 系**：Debian 和基于它的 Ubuntu。
- **Red Hat 生态**：Fedora、RHEL 与 CentOS Stream。传统 CentOS Linux 是 RHEL 的重建版；CentOS Stream 则处于 RHEL 开发流程上游，两者不应混为一谈。
- **SUSE 与 Slackware**：openSUSE 属于 SUSE 生态；Slackware 和 Plamo Linux 可分别查阅。Puppy Linux 有不同构建基础，不能统一归入 Slackware 系。

### Unix 与 Linux

- Unix 起源于 20 世纪 70 年代的贝尔实验室，发展为多用户、分时操作系统。
- Richard Stallman 发起 GNU 计划，推动自由软件工具链的发展。
- Linus Torvalds 开发 Linux 内核。Linux 内核与 GNU 工具及其他软件组合，形成可使用的操作系统发行版。

### VMware 16 与 CentOS 7 安装

在 Windows 10 上使用 VMware 16 时，先检查宿主机虚拟化支持与相关 Windows 功能设置；是否需要启用或关闭 Hyper-V 等组件取决于 VMware 版本及宿主机环境。

安装 CentOS 7 时，可手动规划 `/boot`、swap 和根分区 `/`：`/boot` 保存内核及引导文件，swap 提供交换空间，`/` 承载其余系统目录和文件。服务器常选 Minimal 安装；生产环境是否启用 kdump 应结合故障分析需求和内存预留决定。CentOS 7 已结束维护，本节主要保留历史实验环境的操作背景。

### 虚拟机网络模式

- **桥接**：虚拟机作为同一局域网的独立设备，通常从该网段获取地址；需避免地址冲突。
- **NAT**：虚拟机通过宿主机的网络地址转换访问外部网络，外部主动访问通常需要额外配置。
- **仅主机**：虚拟机与宿主机或同一虚拟网络内的机器通信，默认不能直接访问外网。

### 虚拟机克隆、快照与 VMware Tools

- **克隆**：可通过 VMware 的克隆功能创建新虚拟机，也可在确认虚拟机关闭且文件完整的前提下复制虚拟机文件。克隆后需检查主机名、网络标识与地址。
- **快照**：用于在实验前保存虚拟机状态并在需要时回退；长期保留快照会增加存储占用，不能代替备份。
- **VMware Tools**：提供虚拟机集成功能。启用共享文件夹后，CentOS 中常见的挂载路径是 `/mnt/hgfs/`；实际取决于 VMware Tools 与挂载配置。生产环境的文件传输通常通过受控远程方式完成。

### Linux 目录结构

Linux 以目录树组织文件、设备及部分内核接口；以 `.` 开头的文件名通常在普通列表中隐藏。以下列出常见目录的用途：

| 目录 | 用途 |
| --- | --- |
| `/bin`、`/sbin` | 常用命令和系统管理命令；现代发行版可能将其链接到 `/usr` 下。 |
| `/home`、`/root` | 普通用户家目录与 root 用户家目录；`~` 表示当前用户家目录。 |
| `/lib` | 运行时库；部分发行版同样采用到 `/usr` 的链接。 |
| `/etc` | 系统配置。 |
| `/opt` | 可选的第三方软件。 |
| `/usr` | 系统提供的程序、库和只读共享数据。 |
| `/boot` | 启动文件和内核。 |
| `/proc`、`/sys` | 内核与进程信息的虚拟文件系统。 |
| `/srv` | 服务提供的数据。 |
| `/dev` | 设备文件。 |
| `/media` | 可移动设备的挂载点。 |
| `/mnt` | 临时手动挂载点。 |
| `/var`、`/var/log` | 经常变化的数据及日志。 |
| `/run` | 本次启动期间的运行时数据，通常位于内存文件系统。 |

输入命令时，Shell 会按 `PATH` 中的目录查找可执行文件。可用 `echo "$PATH"` 查看；用户级配置可写入适用的 Shell 启动文件，例如 Bash 的 `~/.bash_profile` 或 `~/.bashrc`。

#### FHS

Filesystem Hierarchy Standard（文件系统层次结构标准）描述根目录及 `/usr`、`/var` 等目录的用途；实际目录布局仍以发行版为准。

## 终端与常用命令

### 远程登录 Linux

生产环境中的 Linux 服务器通常通过网络远程管理。SSH 加密终端连接；文件可通过 SFTP、SCP 等方式传输。Telnet 默认不加密，不宜用于远程管理。

连接前确认目标地址、端口、用户名和 SSH 服务状态。`ping` 只能测试 ICMP 连通性；目标禁用 ICMP 时，仍可能可以连接 SSH。Windows 与 Linux 的文本编码也取决于具体终端和系统配置，不应统一假设为 GBK 或 UTF-8。

#### 本地终端

Linux 可提供多个虚拟终端（TTY）；可用 `Ctrl+Alt+F1` 等组合键切换，具体数量和桌面会话位置依发行版而异。

#### SSH 服务

服务端通常由 OpenSSH 的 `sshd` 提供服务。在使用 systemd 的系统上，可检查其状态：

```sh
systemctl status sshd.service # RHEL/CentOS/Rocky 等
```

Ubuntu 的服务单元通常名为 `ssh.service`。

### Vi 与 Vim

Vim 常见操作有普通模式、插入模式和命令行模式。普通模式下按 `i` 输入文本；按 `Esc` 返回普通模式，再输入 `:wq` 保存退出或 `:q!` 放弃修改。

```sh
vim hello.java
```

#### 常用快捷键

- 复制与粘贴：普通模式下 `yy` 复制当前行，`5yy` 复制从当前行开始的五行，`p` 粘贴。
- 删除与撤销：`dd` 删除当前行，`5dd` 删除五行，`u` 撤销。
- 查找：输入 `/关键词` 后按回车，用 `n` 跳到下一个结果。
- 行号：输入 `:set nu` 显示，`:set nonu` 关闭。
- 跳转：`gg` 到文件开头，`G` 到末尾；输入 `20G` 或 `:20` 到第 20 行。

### Bash Shell

Shell 负责解释用户输入并启动程序；Bash（Bourne Again Shell）是常见实现。登录 Shell 取决于账户与系统配置，不能按云平台统一判断。脚本编写方法见 [[#Shell 编程]]。

### 常用命令

#### 运行级别与 systemd 目标

传统 SysV 运行级别使用数字 0～6：0 表示关机、1 为单用户维护、3 通常为多用户文本模式、5 通常为图形模式、6 为重启；2 和 4 的含义可能随发行版配置变化。

CentOS 7 等使用 systemd 的系统，常以 `multi-user.target` 表示多用户文本模式，以 `graphical.target` 表示图形模式：

```sh
systemctl get-default
sudo systemctl set-default multi-user.target
```

系统恢复或重设 root 密码需遵循对应发行版的恢复流程，不能仅凭旧运行级别编号操作。

#### 帮助指令

- man 查看帮助信息

  查询某指令时候，指令后面会带一个括号数字：

  ![image-20220914230526292](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209171633422.png)

  1-9含义不同：

  ![image-20220914231244428](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209171633462.png)

- help 查看 shell 内置指令的帮助


> [!tip] 查看命令常用方法
> curl cheat.sh/tree #可以查看命令的常用方法

#### 快捷键

- ctrl + a 光标移动到最前面；ctrl+e 光标移动到最后面

#### ls 列出目录内容

- `ls -l`：逐行显示权限、所有者、大小和修改时间等信息。
- `ls -a`：包含以 `.` 开头的隐藏文件。
- `ls -lh`：以易读单位显示文件大小。
- `ls -al`：同时显示隐藏文件与详细信息。

下图中权限字段之后的数字为硬链接计数：多个目录项可以引用同一个 inode。

![image-20220917160920543](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209171636268.png)

### 文件与目录命令

#### 文件目录

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

#### 文件操作

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
  awk '{print $1,$2}' file.txt # 输出每行前两个字段
  awk '/English/ {print}' file.txt # 输出包含 English 的行
  ```

- sed 文本替换

  ```shell
  sed -i 's/old text/new text/g' xxx.txt
  ```

- rm 删除文件或者目录

  -r 递归删除

  -f 强制删除不提示

#### 文件时间

有三个主要的变动时间：

- mtime：修改时间，更改文件内容
- ctime：status time，修改文件状态会更新这个时间，例如改文件属性
- atime：access time，文件内容被读取就会更新

其中，ls -ll 默认显示mtime；想要看其他的time，要加参数，例如

```shell
ls -ll --time=atime /var/log/messages
```

touch可以修改mtime和atime

#### 文件比较

- cmp 一个字母一个字母的比较
- comm 比较两个sorted的文件
- diff 按行比较

#### mv 移动/重命名

mv 旧文件名 新文件名

mv 源目录 新目录

mv 源文件 新目录/新名字 (移动并且重命名)

#### cat 查看文件内容

更加安全 只能看不能改

- cat -n 显示行号
- 一般会带上管道命令 | more (管道命令是将前面的结果交给后面处理) 

#### head 查看开头指定行数

head 默认查看前10行

head -n 5 看前5行

#### tail 查看文件末尾

`tail` 默认显示末尾十行，`-n` 可指定行数；按 `Ctrl+C` 停止持续跟踪。

```sh
tail -n 10 test.log
tail -f /opt/mylog.txt
tail -Fn 10 test.log # 按文件名跟踪，适合可能被替换或轮替的日志
```

`tail -f` 默认跟踪已打开的文件描述符；当编辑器通过替换文件保存，或日志轮替生成新文件时，改用 `tail -F` 跟踪文件名。

#### more 基于Vi的文本过滤器

按回车一行一行看，空格一页一页看

#### less

分屏查看 支持各种终端 动态加载 适合查看大文件 效率高 

#### echo 将内容输出至控制台

- echo [选项] 输出内容

  echo $HOSTNAME

  echo "Hello World"

  写shell脚本的时候相当于printf

- echo "xxx" >  xxx.txt  新建文件的方法2

#### \> 和 >>

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

#### 文件链接

- ln -s **软链接/符号链接**

  - 类似快捷方式，不占用磁盘空间


  - 基本语法： ln -s [源文件或目录]  [软连接名]
  - 相对路径也可用于软链接，但链接目标的相对路径是相对于软链接所在目录解析的；不确定时使用绝对路径
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

#### 文件指针

inode 代表文件的数据结构

dentry 代表目录的数据结构

inode和dentry一起构成了cache，磁盘上的文件系统

#### history 查看已经执行过的命令

history 所有的；history 10 看最近10个；

!5 重新执行当前 Shell 历史记录中事件编号为 5 的命令；执行前先核对历史内容

#### 文件系统类型

Ext3

Ext4

XFS ：large data files

### 时间与日期命令

#### date

- date 显示当前时间
- date "+%Y-%m-%d %H:%M:%S"按占位符规定的格式显示日期
- date -s [新时间] 设置系统时间

- cal 显示日历

### 查找命令

#### find

`find` 从指定路径递归搜索，可用 `-name`、`-iname`、`-user`、`-size` 等条件过滤。`-iname` 忽略文件名大小写；`-type f` 筛选普通文件，`-type d` 筛选目录。

```sh
find /path -iname 'xxx.txt'
find /path -type f -name 'xxx.txt'
find /path -type d -name 'dirname'
```

`-size +n`、`-size -n` 分别表示超过、小于指定大小；单位可用 `k`、`M`、`G` 等。

#### whereis

- find有时候会比较慢，whereis会比较快。但是whereis只是去找特定的几个目录

#### locate

- 利用事先建立的查找数据库，快速定位文件；保证精确度，定时更新索引数据库（大概是系统每天自动更新一次数据库）
- 先 updatedb
- 再 locate xxx.txt

#### which

- 是找 PATH环境变量下面目录的指令

- 查看某个指令在哪个目录下：which ls

#### grep

- 过滤查找，常常与管道符结合使用
-  基本语法：grep [选项] 查找内容 源文件
- 例如：cat /opt/mylog | grep -n "Hello"
- -n：显示行号；-i：忽略大小写

### 压缩与解压

#### gzip 与 gunzip

`gzip file` 将单个文件压缩为 `file.gz`，默认会替换原文件；`gunzip file.gz` 解压。压缩多个文件为一个归档时，可与 `tar` 配合。

#### zip 与 unzip

`zip -r archive.zip directory/` 递归打包目录；`unzip archive.zip -d /target` 解压到指定目录。目录无需预先包含子目录才能使用 `-r`。

#### tar

`tar` 负责归档，`-z` 让 gzip 处理压缩或解压。常用选项：`-c` 创建归档、`-x` 解包、`-v` 显示详情、`-f` 指定归档文件；`-C` 指定解包目录。

```sh
tar -zcvf /opt/my.tar.gz /opt/mytest/
tar -zcvf /opt/my.tar.gz /opt/my1.txt /opt/my2.txt
tar -zxvf /opt/my.tar.gz -C /opt/tmp
```

`.tar` 仅表示归档格式，`.tar.gz` 表示经 gzip 压缩的 tar 归档。

## 用户、权限与计划任务

### 启动、关机、重启与用户登录

#### Linux 启动过程

![090eb76673404b3ff67ee7ed697224f](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312042155530.jpg)

![dc019cdb971d2f32c75f931de48252d](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312042155497.jpg)

1. 按电源键，服务器启动，首先会加载BIOS或者UEFI
2. BIOS会检测硬件是否准备就绪，例如内存、硬盘、CPU等。
3. 硬件检测通过，会选择启动设备，可以是硬盘、光驱、网络服务器。
4. 从设备中读取引导文件（grub），读取到之后会提示选择内核版本，操作系统等。
5. Linux 内核启动；使用 systemd 的系统由其作为 PID 1 初始化用户空间、管理服务和文件系统挂载。
6. 在操作系统启动时，也会启动相关的服务或者进程，比如sshd，syslog，或者用户设置的开机启动服务。
7. 运行启动脚本，并配置用户环境。
8. 然后显示登录界面，提示输入用户名密码。

#### 关机与重启

| 命令 | 用途 |
| --- | --- |
| `shutdown -h now` | 立即关机。 |
| `shutdown -h +1` | 一分钟后关机。 |
| `shutdown -r now` | 立即重启。 |
| `reboot` | 立即重启。 |
| `sync` | 请求将缓存的文件系统数据写回存储。 |

关机和重启命令通常会处理文件系统同步；在特殊维护场景可先单独运行 `sync`。

#### 用户类型

- **root**：超级用户，UID 为 0；其主组 GID 由系统配置决定，不必等于 0。
- **普通用户**：用于交互登录，UID 范围由 `/etc/login.defs` 等配置决定，不能只凭“是否大于 1000”判断。
- **系统用户**：供服务或后台进程使用，通常不提供交互登录。`nobody` 是常见的低权限账号，可能使用 `/sbin/nologin`；它不表示“任何人都可以登录”。服务也可以使用各自的专用账号，例如 `ftp`。

为服务分配低权限账号可以限制进程可访问的资源，但具体权限仍由文件权限和其他安全策略决定。

#### 用户登录与注销

- `su - 用户名` 切换为目标用户的登录环境；省略用户名时通常切换为 root，需要相应身份验证。
- `sudo 命令` 按 sudoers 策略以指定身份执行单条命令；需要密码时通常输入当前用户的密码。`sudo -i` 可申请交互式 root 登录 Shell。
- `exit` 或 `logout` 退出当前登录 Shell，与旧式运行级别 3 没有必然关系。

#### 账户配置文件

- 用户级 Bash 配置常见于 `~/.bashrc` 和 `~/.bash_profile`；实际加载顺序取决于是否为登录 Shell。
- 全局环境可在 `/etc/profile` 等文件中配置。RHEL 系常见 `/etc/bashrc`，Debian/Ubuntu 常见 `/etc/bash.bashrc`。

### 用户管理

#### 创建用户与设置密码

`useradd` 的默认行为受发行版和 `/etc/login.defs` 影响。需要明确创建家目录时使用 `-m`；自定义家目录使用 `-d` 并配合 `-m`。

```sh
sudo useradd -m username
sudo useradd -m -d /home/custom username
sudo passwd username # 交互输入新密码
```

不带用户名的 `passwd` 修改当前用户的密码；命令末尾不能直接追加明文密码参数。

#### 查询、切换与删除用户

```sh
id username
whoami
who am i
su - username
sudo userdel username    # 默认保留家目录
sudo userdel -r username # 同时删除家目录和邮件目录
```

`whoami` 显示当前有效用户名；`who am i` 查询当前登录会话。`su -` 会加载目标用户的登录环境，`su` 则保留更多当前环境。root 切换到其他用户通常无需输入目标密码。

#### 用户组与账户文件

```sh
sudo groupadd groupname
sudo groupdel groupname
sudo groupmod -g 2001 groupname # 修改组的数字 GID
sudo useradd -m -g groupname username # 新用户的主组
sudo usermod -aG groupname username   # 加入附加组，保留现有附加组
sudo chgrp groupname filename         # 修改文件所属组
```

新建用户是否自动建立同名主组，由系统配置决定。账户信息见 `/etc/passwd`，密码散列和密码有效期信息见 `/etc/shadow`，组信息见 `/etc/group`；可用 `cat /etc/passwd` 查看现有本地账户。

### 用户组管理

用户可属于一个主组和多个附加组。文件有一个所有者与一个所属组，访问控制分别考虑所有者、所属组和其他用户。

- `ls -l` 或 `stat filename` 查看文件所有者和组。
- `chown owner:group filename` 修改文件所有者与所属组；`chgrp group filename` 只改所属组。
- `groupadd group` 创建组；`useradd -g group username` 创建用户并指定主组；`usermod -g group username` 修改已有用户主组。
- `usermod -d /new/home username` 修改账号记录中的家目录路径；需要迁移已有内容时还需使用相应选项并检查权限。
- `getent group groupname` 查询组信息。

### 文件权限

文件权限通常写成十位字符，例如 `-rwxrw-r--`：首位表示文件类型，其后三组分别对应所有者、所属组和其他用户。`-` 是普通文件，`d` 是目录，`l` 是符号链接；还可能有字符设备 `c`、块设备 `b`、管道 `p`、套接字 `s`。账户和组信息分别见 `/etc/passwd`、`/etc/shadow`、`/etc/group`。

#### 文件与目录的读写执行权限

| 对象 | `r` | `w` | `x` |
| --- | --- | --- | --- |
| 文件 | 读取内容 | 修改内容；删除文件还取决于父目录权限 | 执行文件 |
| 目录 | 列出目录项 | 创建、删除或重命名目录项，通常还需要 `x` | 进入目录并按路径访问其中对象 |

权限位可用数字表示：`r=4`、`w=2`、`x=1`，每组相加得到如 `755`。下图保留原有示意：

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111347288.jpeg" alt="权限位示意" style="zoom:50%;" />

<img src="https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209111348269.png" alt="数字权限示意" style="zoom:50%;" />

#### 修改权限

`chmod -v` 显示变更过程；符号模式使用 `u`（所有者）、`g`（组）、`o`（其他人）、`a`（全部）。数字模式按“所有者、组、其他人”的顺序指定权限：

```sh
chmod u=rwx,g=rx,o=x log.txt
chmod o+w log.txt
chmod a-x log.txt
chmod 755 log.txt # rwxr-xr-x
```

#### 默认权限与 umask

新建普通文件的权限上限通常是 `666`，新建目录通常是 `777`；`umask 022` 会去掉组和其他用户的写权限，得到文件 `644`、目录 `755`。实际结果还可能受默认 ACL 等因素影响。

![image-20220917205951750](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202209172059809.png)

#### SUID、SGID 与 sticky bit

- **SUID**：对可执行文件设置后，执行时可使用文件所有者的有效 UID，例如 `/usr/bin/passwd` 需要受控地更新 `/etc/shadow`。`4755` 是一种数字表示。
- **SGID**：对目录设置后，其中新建文件通常继承目录的所属组；`2775` 是一种数字表示。
- **sticky bit**：常用于多人可写目录，限制用户删除或重命名其他用户的文件；`1777` 是一种数字表示。

### 定时任务

#### crontab：重复执行

`crontab -e` 编辑当前用户的定时任务；系统级计划任务还可定义在 `/etc/crontab`。表达式 `* * * * *` 依次表示分钟、小时、日期、月份和星期。以下任务每分钟运行一次：

```cron
* * * * * ls -l /etc/ > /tmp/to.txt
```

例如将日期和日历追加到日志，保存为 `/opt/my.sh`：

```sh
#!/bin/sh
date >> /opt/mycal.txt
cal >> /opt/mycal.txt
```

保存脚本后执行 `chmod 744 /opt/my.sh`，再在 `crontab -e` 中添加：

```cron
* * * * * /opt/my.sh
```

数据库备份同样可以按计划执行。原命令将密码写在命令行且 `-u` 缺少用户名；下例改为从预先配置、只允许目标用户读取的 MySQL 选项文件获取凭据：

```cron
0 2 * * * mysqldump --defaults-extra-file=/root/.my.cnf testdb > /home/test.bak
```

请按运行该任务的用户、MySQL 版本和实际备份目录调整路径。

#### at：一次性执行

`atd` 负责运行一次性任务。可用 `systemctl status atd` 检查服务状态，`at 10:00` 进入交互输入并用 `Ctrl+D` 结束；`atq` 查看队列，`atrm 作业号` 删除任务。

## 存储与文件系统

### 磁盘分区与挂载

#### 磁盘、分区与启动方式

- 磁盘按扇区寻址，常见逻辑扇区大小为 512 字节或 4 KiB；具体大小以设备报告为准。
- 分区表描述磁盘上的分区范围。MBR 通常最多支持四个主分区，可借助扩展分区创建逻辑分区；采用 512 字节逻辑扇区时，其容量上限约为 2 TiB。
- GPT 使用分区条目记录分区信息，并保留备份分区表，突破了 MBR 的主分区数量和容量限制。现代 `fdisk` 支持 GPT，也可以使用 `gdisk` 或 `parted`。
- 文件系统创建在分区或其他块设备上；挂载是把文件系统接入目录树。挂载点必须是目录，挂载后原目录中的内容会暂时被遮蔽。
- 设备名可能是 `/dev/sda1`、`/dev/vda1`、`/dev/nvme0n1p1` 等。用 `lsblk -f` 确认设备、文件系统、UUID 与挂载点，不要仅凭设备名猜测用途。
- BIOS 与 UEFI 是两种固件启动方式。常见组合是 BIOS + MBR 或 UEFI + GPT；BIOS 也能从 GPT 磁盘启动，但 GRUB 等引导程序通常需要 BIOS Boot Partition。UEFI 通常从 EFI 系统分区加载引导程序。

#### 增加磁盘的示例

以下以虚拟机新增的 `/dev/sdb` 为例。**执行前用 `lsblk` 核实目标磁盘；分区与格式化会清除目标设备上的数据。**

1. 在虚拟机设置中添加磁盘，运行 `lsblk` 确认设备。
2. 运行 `fdisk /dev/sdb`；按 `m` 查看帮助，按 `n` 新建分区，按提示选择分区编号和范围，最后按 `w` 写入分区表（放弃用 `q`）。创建后用 `lsblk -f` 确认分区名。
3. 为新分区选择**一种**文件系统，例如：

   ```sh
   mkfs.ext4 /dev/sdb1
   # 或：mkfs.xfs /dev/sdb1
   ```

4. 创建空目录并挂载；命令行挂载在重启后通常不会保留：

   ```sh
   mkdir -p /mnt/data
   mount /dev/sdb1 /mnt/data
   ```

5. 需要开机自动挂载时，先运行 `blkid /dev/sdb1` 获取 UUID，再在 `/etc/fstab` 中添加对应条目。以下以 ext4 为例，UUID 需替换为实际值：

   ```text
   UUID=<实际UUID> /mnt/data ext4 defaults 0 2
   ```

   六列依次为设备或 UUID、挂载点、文件系统类型、挂载选项、dump 备份标记和 `fsck` 检查顺序。`0` 表示不检查，`1` 通常留给根文件系统，`2` 用于其他需要检查的文件系统。运行 `mount -a` 检查配置。

维护时可用 `mount -o remount,rw /` 将已挂载的根文件系统重新挂载为可写；只读模式下仍需注意故障原因。挂载磁盘映像可使用 `mount -o loop`。

#### 查看磁盘使用情况

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
  parted /dev/vda print
  ```

- partprobe

  更新核心分区表

#### 工作常用指令

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

#### 逻辑卷管理 LVM

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

#### 磁盘阵列 RAID

- Redundant Arrays of Independent Disks. 利用许多独立的便宜磁盘，组成容量巨大的磁盘组，利用个别磁盘提供数据所产生的加成效果提升整个磁盘系统的效能
- 最大优点：提高数据传输速率，在多个磁盘上同时存储数据
- RAID0：数据并行写入每个磁盘，并行读取；但是没有冗余，一个盘坏掉，数据全部丢失。不适用于安全性要求高的场景
- 注意：别把空间不同的磁盘RAID，否则性能将会被限制在最小容量的那个盘

#### 磁盘完整性检查 FSCK

- 磁盘没有mount的时候运行fsck

  ```bash
  umount /dev/sdc1
  fsck -y /dev/sdc1  # 仅用于适用 fsck 的文件系统；-y 自动确认修复
  xfs_repair /dev/sdc1 # XFS 文件系统使用此命令，修复前必须卸载
  ```


#### 初始化磁盘（Initrd）

- 是系统引导过程中挂载的一个临时根文件系统，用来支持两阶段的引导过程，initrd中包含了各种可执行程序和驱动，可以挂载实际的根文件系统，然后再将initrd磁盘卸载，释放内存。

#### 启动管理

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

### Linux 文件系统

#### inode、block 与 superblock

以 ext 系列文件系统为例：

- **inode** 记录文件类型、权限、所有者、时间戳及数据块位置等元数据；文件名保存在目录项中。每个文件或目录通常对应一个 inode。
- **block** 保存文件内容或目录项。文件很小也会占用分配单位；块太大可能浪费小文件空间，太小会增加元数据开销。格式化时会将空间组织为块组。
- **superblock** 保存文件系统的总体信息，例如块和 inode 的数量、状态等。
- **bitmap** 标记空闲或已用的 inode 与 block，属于文件系统元数据。

例如，一个文件的 inode 指向数据块 2、3、5、7，文件系统据此定位内容。目录自己的 inode 指向目录数据块，目录项保存名称与 inode 的对应关系，因此重命名或删除目录中的条目通常需要该目录的写权限。

FAT 使用文件分配表记录簇链，结构与 ext 的 inode 索引不同；碎片较多时，读取同一文件可能需要跨越较远的磁盘位置。inode 的大小由文件系统类型及创建参数决定，不能用固定的 ext4/XFS 字节数概括；文件数量还受可用 inode、空间及文件系统实现等限制。

`dumpe2fs /dev/sda1` 可查看 ext 文件系统信息；应先核实设备路径。

#### 一致性、日志与写回

意外断电可能使 inode、数据块与空闲位图不一致。ext3/ext4 的日志机制会先记录相应元数据操作，再据此缩短故障后的一致性恢复时间；日志并不等于完整数据备份。

Linux 使用页缓存改善读写性能。内存中修改过的页会标记为 dirty，并在适当时机写回磁盘；`sync` 可请求写回缓存。正常卸载或关机会尽力完成写回，突然掉电仍可能导致数据丢失或文件系统不一致。

#### 其他文件系统与 XFS

CentOS 7 的默认文件系统通常是 XFS。`ls -l /lib/$(uname -r)/kernel/fs` 可查看当前内核安装的部分文件系统模块；实际支持情况还包括内建驱动。

XFS 适合大容量和高并发工作负载。其分配组（allocation group）管理数据与元数据，日志记录需要恢复的变更；可选的实时设备（realtime device）用于特殊场景，并非普通文件写入的临时区。

```sh
xfs_info /实际挂载点
# 或：xfs_info /dev/实际设备
```

![image-20221017185539855](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202210171855949.png)

XFS 的标签与 UUID 可用 `xfs_admin` 管理；ext 文件系统可用 `tune2fs` 管理相关属性。修改前应检查文件系统是否需要卸载，并核实命令选项。
## 云平台与网络

### 云平台相关配置

#### Azure Linux Agent（waagent）

waagent 负责 Azure Linux VM 的部分代理与扩展功能；资源盘和交换区的管理方式取决于镜像、代理版本和 cloud-init 配置。资源盘属于临时存储，不能存放需要持久保存的数据；设备名可能因 SCSI/NVMe 控制器和 VM 规格不同而变化，先用 `lsblk` 核实。

代理日志通常在 `/var/log/waagent.log`，配置文件为 `/etc/waagent.conf`。以下是旧版笔记中的资源盘及交换区参数，**仅作为配置项示例**，启用前需核对当前镜像、代理与 cloud-init 的实际管理权：

```ini
ResourceDisk.Format=y
ResourceDisk.EnableSwap=y
ResourceDisk.SwapSizeMB=4096
```

swap 用于在内存紧张时将部分页面换出到磁盘，性能与数据持久性不能等同于 RAM。

#### cloud-init 与扩展

`cloud-init` 用于云主机初始化，适用于多个云平台；Azure Linux Agent 则是 Azure 平台组件。两者功能可能交叠，资源盘、网络等配置应明确由哪一方管理。Azure VM 扩展可通过 Azure CLI、PowerShell 或 Azure Resource Manager 部署；扩展日志通常位于 `/var/log/azure/` 下。

### 网络配置

在 Windows 上可用 `ipconfig` 查看 VMnet8 等虚拟网络配置；在 Linux 上优先用 `ip addr` 查看接口地址，旧系统也可能提供 `ifconfig`。

#### 地址、主机名与解析

- DHCP 自动分配地址；服务器也可以使用 DHCP 地址保留或配置静态地址，按实际网络环境选择。
- `hostname` 查看主机名。Linux 的 `/etc/hosts` 和 Windows 的 `C:\Windows\System32\drivers\etc\hosts` 可维护本地主机名与 IP 映射。
- 旧版 RHEL/CentOS 的网络接口配置常位于 `/etc/sysconfig/network-scripts/ifcfg-<接口名>`；较新的 NetworkManager 通常管理 keyfile 连接配置，可用 `nmcli` 查看和修改。接口名以 `ip link` 的结果为准。
- `dig @8.8.8.8 microsoft.com` 查询指定 DNS 服务器，A 记录对应 IPv4 地址；`nslookup microsoft.com` 也可查询 DNS。
- `getent hosts microsoft.com` 依照 `/etc/nsswitch.conf` 的 `hosts` 顺序解析，通常会考虑 `/etc/hosts`。`dig` 和 `nslookup` 直接查询 DNS，不读取 `/etc/hosts`。DNS 服务器配置通常可从 `/etc/resolv.conf` 查看。

#### 端口与路由

`ss -lnt` 查看监听的 TCP 端口；`netstat -an` 是旧系统中常见的替代命令。可用 `nc`、`telnet` 或 `curl` 测试目标连接；`telnet` 只测试 TCP，`nc` 可测试 TCP 或 UDP，但 UDP 探测结果需结合应用响应判断。

`ip route` 查看路由表，旧命令还有 `netstat -r`、`route -n`。以下旧式 `route` 示例用于说明目的网络、设备和默认网关，实际地址与接口名需按环境替换：

```sh
route add -net 10.0.2.0 netmask 255.255.255.0 dev eth0
route add -net 127.0.0.0 netmask 255.0.0.0 lo
route add default gw 192.168.10.1
```

#### iptables 与抓包

iptables 规则按链组织：`INPUT` 处理发往本机的数据包，`OUTPUT` 处理本机发出的数据包，`FORWARD` 处理转发的数据包。规则或默认策略可以采用 `ACCEPT`、`DROP`、`REJECT` 等目标。用 `iptables -S` 或 `iptables -L` 查看规则；现代发行版也可能使用 nftables 或 firewalld 管理防火墙。

网络连通性故障可在源端和目的端抓包分析：

```sh
tcpdump -w /tmp/traces.pcap -i eth0
# 按 Ctrl-C 停止抓包
ls -l /tmp/traces.pcap
```

#### NFS

相关原始资料：Azure Linux Academy - Foundation，P.104。

#### firewalld

firewalld 用 zone 表示网络连接的信任范围，常见 zone 有 `block`、`drop`、`public`、`external`、`dmz`、`internal`、`trusted`、`work`、`home`。

```sh
firewall-cmd --state
firewall-cmd --list-all
firewall-cmd --get-zones
firewall-cmd --get-active-zones
firewall-cmd --list-services
firewall-cmd --list-ports

# 示例：在 public zone 中开放 SSH 服务或 TCP 8080 端口
firewall-cmd --zone=public --add-service=ssh --permanent
firewall-cmd --zone=public --add-port=8080/tcp --permanent
# 移除时分别使用 --remove-service=ssh 或 --remove-port=8080/tcp
firewall-cmd --reload
```

#### SELinux

SELinux 通过安全策略和标签控制进程、文件、端口等对象的访问。配置文件为 `/etc/selinux/config`（部分系统的 `/etc/sysconfig/selinux` 是其符号链接）。模式有 enforcing、permissive、disabled；常见策略类型有 targeted、minimum 和 MLS。访问向量缓存（AVC）保存权限判定；拒绝事件通常可在审计日志中查询。

```sh
sestatus
getenforce
setenforce 0  # 临时切换为 permissive
setenforce 1  # 临时切换为 enforcing
grep -i denied /var/log/audit/audit.log
```

## 进程、软件与系统服务

### 进程管理

- 执行中的程序都是一个进程，每一个进程分配一个PID。程序是静态的，程序run起来，加载到内存中，就是一个进程。
- 每个进程可能以两种方式存在，**前台** or **后台** ， 一般而言，系统服务以后台形式常驻

#### 显示进程

- ps

  - 字段 PID、TTY（终端机号）、TIME（消耗CPU时间）、CMD（进程名）

  - -a 显示所有进程；-u 以用户格式显示进程；-x 显示运行参数

  - 常用：

    ```shell
    ps aux | more
    ps aux | grep ...
    ps -ef # 与-aux一样，只是显示的格式不同
    ```

    VSZ：进程占用虚拟内存大小

    RSS：进程占用的物理内存大小

    TT：终端名称

    STAT：进程状态

- 查看父进程，可以用ps -ef | more

  ps -ef 能显示出父进程号（PPID）

- pgrep -l 进程名 （查找指定名称的进程）

#### 终止进程

`kill PID` 默认向指定进程发送 TERM 信号，请进程正常退出；`kill -9 PID` 发送 KILL 信号，适合无法正常退出时使用。`killall 进程名` 按名称向匹配的进程发送信号，使用前先确认匹配范围。

例如，先用 `ps -ef | grep sshd` 确认 SSH 会话进程，再向特定会话的 PID 发送信号。停止 SSH 服务应通过 `systemctl stop sshd`（Ubuntu 通常是 `ssh`）管理；**远程操作时停止服务会中断新的连接，应预留恢复途径。**

`killall gedit` 可结束匹配的编辑器进程；终端或其他进程同样应先确认 PID，再决定是否发送强制信号。

#### 查看进程树

- pstree -p (带进程号)
- pstree -u （带用户名）

#### 服务管理

- 服务是运行在后台的进程，例如 mysqld，SSHD  （d：deamon 守护进程）

  mysqld、sshd守护进程 分别通过3306 or 22 端口进行监听。network停止之后，监控端口就关闭了

- service [status | start | stop | reload]  service在CentOS7.0之后被弱化，更多的是systemctl

- setup 可以看到所有服务

  [*]的是自动启动的服务，按空格可以取消


#### 服务的运行级别

- 0 - 6 与前面的级别一样 （常用的是3 和 5）

- 开机流程

  开机 -> BIOS -> /boot -> systemd 进程1  -> 运行级别 -> 运行级别对应的服务

- 设置运行级别的自启动 chkconfig

  让某些服务，在某个运行级别下自启动或者不启动，重启机器生效

#### systemV和systemd

- `SystemV`和`systemd`都是Linux系统中的初始化系统（init system），负责在系统启动时启动和管理系统服务。

- `SystemV`是一个传统的初始化系统，它使用脚本来启动和停止服务。这些脚本通常位于`/etc/init.d/`目录下，服务的启动顺序由这些脚本的名字决定。

- `systemd`是一个新的初始化系统，它使用单元（units）来管理服务。这些单元的配置文件通常位于`/etc/systemd/system/`目录下，服务的启动顺序由这些配置文件中的依赖关系决定。

他们的主要区别如下：

- 启动速度：`systemd`使用并行处理来加快启动速度，而`SystemV`则是按顺序启动服务。
- 配置方式：`systemd`使用单元配置文件，而`SystemV`使用脚本。
- 日志管理：`systemd`内置了日志管理系统`journald`，而`SystemV`没有内置的日志管理系统。
- 依赖管理：`systemd`可以自动处理服务之间的依赖关系，而`SystemV`需要手动管理。

#### 服务管理

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

#### Service trouble-shooting

- Init and systemd

  - init is a process trees

- Service

  - process that run in background, mainly for resource management, interface to access resources

- traditional init systems: SysV and BSD

  other init schema: SMF, launchd, PoenRC, Upstart

- systemctl and journalctl

  - systemctl: control services; journalctl: read and filter systemd journal

- other important commands and services

  - commands: timedatectl（时间同步）、hostnamectl（主机名等）、resolvectl（名称解析）
  - services: 

- Tools in systemd commands:

  - systemctl

    ```bash
    systemctl status service
    journalctl -u service
    systemctl cat service
    systemctl list-dependencies service
    ```


#### 动态监控进程

**top**

- 与ps相似，不过可以更新

- top -d 秒数   （每隔5秒，默认是3 s）

  top -i  （不显示闲置进程）

  top -p PID （指定监视某个进程）

  load average：依次为过去 1、5、15 分钟的平均运行队列长度；需结合 CPU 核数和 I/O 等待判断负载，不能按百分比理解。

  zombie 僵尸进程：子进程已退出，但父进程尚未回收退出状态；它保留进程表项，不再像运行中的进程那样占用完整内存。

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

#### 监控网络状态

- **netstat -anp** [-an 按照一定顺序排列输出 -p 显示哪个进程在监听端口]

  - 0.0.0.0:22  本地程序在监听22端口


  - 192.168.13.128:22 这是本地Linux的IP地址和端口


  - 192.168.13.1:8226 这是windows中xshell的IP与端口

#### 验证端口

  ```shell
  netstat -tulpn | grep -i ssh
  ```

### RPM 与软件仓库

RPM 用于管理 `.rpm` 软件包。示例包名 `firefox-60.2.2-1.el7.centos.x86_64` 包含名称、版本/发行号、发行版标识和架构等信息；`i686`、`i386` 常见于 32 位包，`noarch` 表示与 CPU 架构无关。

| 命令 | 用途 |
| --- | --- |
| `rpm -qa` | 列出已安装包，可接 `grep firefox` 过滤。 |
| `rpm -q 包名` | 查询指定包是否已安装。 |
| `rpm -qi 包名` | 查看包信息。 |
| `rpm -ql 包名` | 列出安装文件。 |
| `rpm -qf /文件路径` | 查询文件所属的包。 |
| `rpm -ivh /包路径.rpm` | 安装本地 RPM 包。 |
| `rpm -e 包名` | 卸载包；如有依赖，可能无法直接卸载。 |

`yum` 或 `dnf` 可从仓库安装软件并处理依赖，例如 `yum list installed`、`yum install 包名`、`yum -y install 包名`、`yum repolist all`。`-y` 自动确认交互提示，应先了解将发生的变更。EPEL（Extra Packages for Enterprise Linux）是面向 RHEL 及兼容发行版的附加软件包仓库。`.deb`、`.tgz` 等属于其他打包或归档格式，不由 RPM 直接管理。

#### waagent 重装示例

原示例说明在 Azure VM 中移走旧状态目录，再卸载并重装 WALinuxAgent。**更改代理可能影响 VM 扩展、资源盘和配置；执行前应核对当前版本、服务状态及 Azure 官方修复流程。** 以下保留操作顺序以便排查：

```sh
systemctl stop waagent
mv /var/lib/waagent /var/lib/waagent.old
yum remove WALinuxAgent -y
yum install WALinuxAgent -y
systemctl start waagent
systemctl status waagent
ls -l /var/lib/waagent
cat /etc/waagent.conf
ls -l /var/log/azure
```

代理日志通常位于 `/var/log/waagent.log`，配置文件为 `/etc/waagent.conf`；重新安装包是否生成新的配置和状态，应按具体发行版验证。

### 打印服务

Common UNIX Printer System （CUPS）

- Package name

  cups

### 系统信息与压力测试

可用 `stress` 制造 CPU 负载，再用 `free` 和 `/proc` 观察系统资源。

```shell
# 首先安装EPEL源
yum -y install epel-release
# 再安装stress
yum --enablerepo=epel install stress -y
# 复制一个Terminal，查看CPU
stress -c 4
# CPU
cat /proc/cpuinfo
# memory
cat /proc/meminfo
# 内存 缓存 交换区
free -m
```

#### 系统行为报告

System Activity Report

```shell
yum install sysstat -y
systemctl enable sysstat
systemctl start sysstat
sar
```

#### sosreport

把系统配置、诊断信息等打包起来，可以发给Technical Support

更多内存、CPU、磁盘、OS 和硬件信息命令见 [[#系统信息与资源监控]]。

### 默认内核与 GRUB

系统安装多个内核后，可通过 GRUB 选择默认启动项。更改内核前应确认目标版本及恢复途径，尤其是在远程虚拟机上。

在 RHEL 系统中，优先使用 `grubby` 查看和设置默认内核，避免手工解析生成的 GRUB 配置文件：

```sh
grubby --info=ALL
grubby --default-kernel
grubby --set-default "/boot/vmlinuz-<目标版本>"  # 替换为实际内核路径
grubby --default-kernel
```

重启后运行 `uname -r` 核实当前内核。旧系统也可能使用 `grub2-set-default` 配置保存的启动项；具体 GRUB 配置路径因发行版和 BIOS/UEFI 启动方式不同而异。

### 日志管理

#### 日志简介

- 系统信息文件，记录系统事件

  常用日志的位置：

- 日志管理服务

  - CentOS6：**syslogd**；CentOS7.6：**rsyslogd**

  -   查询日志管理服务是否启动：

    ```shell
    ps aux | grep "rsyslog"
    systemctl status rsyslog.service
    systemctl list-units --all | grep rsyslog
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

### dump 备份

#### 语法说明

- dump - [cu c是个具体数字：0123456789] [-f 备份后文件名] -[T 日期] [目录或者文件系统]
  - -0123456789 ：备份层级，0为最完整备份，>0是增量备份，指定最多备份几次。

- 注意：xfs文件系统要用xfsdump；ext4才能用dump命令


## 脚本与自动化

### Shell 编程

#### 基础与执行方式

Shell 是命令解释器。Bash 脚本通常以 `#!/usr/bin/env bash` 或 `#!/bin/bash` 开头。赋予执行权限后可运行 `chmod u+x /opt/shcode/hello.sh` 和 `/opt/shcode/hello.sh`；也可以运行 `bash hello.sh`。若脚本用了 Bash 特性，应使用 Bash 执行，不能假定 `sh` 一定指向 Bash。

#### 变量与环境变量

- 常见环境变量有 `HOME`、`USER`、`PATH`、`PWD`、`SHELL`。`set` 可列出当前 Shell 的变量和函数。
- 赋值写作 `A=value`，等号两侧不能有空格；变量名不能以数字开头。`unset A` 删除变量；`readonly A` 声明只读变量。
- 用 `A=$(date)` 保存命令输出；反引号写法也可用，但嵌套时不如 `$(...)` 清晰。
- `export A=value` 把变量传给后续子进程。持久配置可按使用范围放在 Shell 启动文件或 `/etc/profile` 中；修改后可用 `source /etc/profile` 在当前 Shell 重新加载。
- `echo "$A"` 查看变量。Vim 可通过 `:set nu` 显示行号。多行注释可用 here document 写法 `: <<'COMMENT' ... COMMENT`。

#### 参数与状态

- `$0` 是脚本名；`$1`、`$2` 等是位置参数，第 10 个及之后写作 `${10}`；`$#` 是参数个数。
- 引用时，`"$@"` 将每个参数保留为独立字段；`"$*"` 将所有参数合并为一个字段。脚本遍历参数通常用 `for arg in "$@"; do ...; done`。
- `$$` 是当前 Shell 的 PID，`$!` 是最近一次后台任务的 PID，`$?` 是上一条命令的退出状态（0 通常表示成功）。`/opt/shellcode/myshell.sh &` 在后台运行脚本。

#### 算术与条件

推荐用 `$((表达式))` 进行整数运算，例如 `SUM=$((SUM + i))`。旧写法 `expr 1 + 2` 要在运算符两侧留空格，乘号需转义。`$[...]` 是旧式算术扩展写法。

`[ ... ]` 两侧必须留空格；条件成立时退出状态为 0。整数比较包括 `-lt`、`-le`、`-eq`、`-gt`、`-ge`、`-ne`；字符串可用 `=` 比较。文件测试包括 `-r`、`-w`、`-x`、`-f`（普通文件）、`-e`（存在）和 `-d`（目录）。

```bash
if [ 23 -ge 22 ]; then
  echo "greater"
elif [ -f aaa.txt ]; then
  echo "file exists"
else
  echo "other"
fi
```

#### 流程控制

```bash
case "$1" in
  1) echo "one" ;;
  2) echo "two" ;;
  *) echo "other" ;;
esac

for arg in "$@"; do
  echo "num is $arg"
done

SUM=0
for ((i = 1; i <= 100; i++)); do
  SUM=$((SUM + i))
done

i=0
while [ "$i" -le "${1:-0}" ]; do
  SUM=$((SUM + i))
  i=$((i + 1))
done
```

`read -p "Input NUM1=" NUM1` 显示提示并读取输入；`read -t 10 -p "Input NUM2=" NUM2` 最多等待 10 秒。

#### 函数

`basename /path/to/file` 返回路径末尾的文件名，可加后缀参数去掉后缀；`dirname /path/to/file` 返回上级目录。自定义函数可写为：

```bash
funname() {
  # 执行动作
  return 0
}
```

#### 定时备份示例

目标：每天 02:30 备份 `/opt/shcode/fun.sh`，按时间命名归档，并删除超过 10 天的备份。先保存以下脚本为 `/opt/shcode/backup.sh`：

```bash
#!/usr/bin/env bash
set -e

BACKUP=/opt/shcode/backup
DATETIME=$(date +%Y-%m-%d_%H%M%S)
mkdir -p "$BACKUP"

echo "Backup started: $DATETIME"
tar -czvf "$BACKUP/$DATETIME.tar.gz" -C /opt/shcode fun.sh
find "$BACKUP" -maxdepth 1 -type f -name '*.tar.gz' -mtime +10 -delete
echo "Backup completed: $DATETIME"
```

赋予执行权限后，先手动运行并检查归档内容：

```sh
chmod u+x /opt/shcode/backup.sh
/opt/shcode/backup.sh
tar -tzf /opt/shcode/backup/2026-01-01_023000.tar.gz  # 替换为实际归档名
```

再用 `crontab -e` 添加 `30 2 * * * /opt/shcode/backup.sh`。`-mtime +10` 按文件修改时间筛选超过 10 个完整 24 小时周期的文件；如果需要精确到 10 天整，可按实际保留策略调整。
## 发行版操作补充

### Ubuntu 操作补充

#### root 与 sudo

Ubuntu 通常不为 root 账户设置可直接使用的密码；管理任务优先用 `sudo`。如确需为 root 设置密码，可运行 `sudo passwd root`，随后才能用 `su -` 输入该密码切换。Shell 提示符常用 `$` 表示普通用户、`#` 表示 root，但不能仅凭提示符判断实际权限。

#### APT 包管理

APT（Advanced Package Tool）管理 Debian/Ubuntu 软件包。可按发行版版本选择官方或可信镜像源，并检查 `sources.list` 或 `sources.list.d/` 中的仓库配置。

```sh
sudo apt update
sudo apt install 包名
sudo apt remove 包名
apt show 包名
apt source 包名  # 需启用对应的源码仓库
```

旧版命令 `apt-get`、`apt-cache` 仍可用于脚本或特定用途。

#### 远程登录

SSH 提供加密的远程登录。目标主机需要运行 OpenSSH 服务器，客户端使用 `ssh` 连接。如果 Ubuntu 尚未安装服务端，可运行：

```sh
sudo apt install openssh-server
sudo systemctl status ssh.service
# 修改服务端配置后：
sudo systemctl restart ssh.service
ssh username@目标主机IP
```

远程修改 SSH 配置前应检查语法并保留现有会话，以便恢复连接。

## RHEL 管理摘录

以下整理原 Red Hat Enterprise Administrator Guide 摘录。命令和默认值随 RHEL 版本及系统配置而异，操作前应核对当前系统。

### 区域设置与时间

- 系统区域设置通常保存在 `/etc/locale.conf`；用 `localectl` 查看或调整 locale、键盘布局。
- RTC 是硬件时钟，关机后仍运行；UTC 是协调世界时，DST 是夏令时。`date`、`timedatectl` 和 `hwclock` 分别用于查看或管理相关时间设置。
- `timedatectl set-time "YYYY-MM-DD HH:MM:SS"` 设置系统时间；`timedatectl list-timezones` 查看时区，`timedatectl set-timezone <时区>` 更改时区；`timedatectl set-ntp yes` 或 `no` 控制自动时间同步。`/etc/adjtime` 保存硬件时钟相关配置。通常建议硬件时钟使用 UTC。

### 用户与组

- `umask` 决定新文件和目录默认权限中被屏蔽的位。常见值 `022` 使同组和其他用户无写权限，但实际值需用 `umask` 查看；系统级 Shell 配置可能位于 `/etc/bashrc`。
- `/etc/passwd` 保存用户基本信息，密码哈希及有效期信息保存在权限更严格的 `/etc/shadow`；组信息位于 `/etc/group` 和 `/etc/gshadow`。
- 用户管理命令有 `useradd`、`usermod`、`userdel`；组管理命令有 `groupadd`、`groupmod`、`groupdel`、`gpasswd`。`pwck`、`grpck` 检查账户文件，`pwconv`、`pwunconv`、`grpconv`、`grpunconv` 转换 shadow 文件。
- 较早系统常将 1–499 留给系统账户、500 起用于普通用户；较新系统常将 1–999 留给系统账户、1000 起用于普通用户。具体范围以 `/etc/login.defs` 和系统设置为准。
- 创建用户后，`/etc/passwd` 中的示例记录为 `user1:x:1001:1001::/home/user1:/bin/bash`：依次是用户名、密码占位符、UID、主组 GID、注释字段、家目录和登录 Shell。是否创建家目录取决于发行版默认设置或 `useradd -m`；用 `passwd user1` 设置密码。

#### 共享目录的 SGID

默认情况下，新文件通常继承创建者的主组。对共享目录设置 SGID 后，新建文件和子目录通常继承目录所属组，适合项目协作：

```sh
groupadd myproject
mkdir -p /myproject
chown root:myproject /myproject
chmod 2775 /myproject
usermod -aG myproject username
ls -ld /myproject
```

用户需要重新登录或刷新组会话，新的附加组才会生效。

### 权限提升

RHEL 常用 `wheel` 组管理特权用户。`usermod -aG wheel username` 为用户添加附加组，具体 sudo 权限仍以 `/etc/sudoers` 和 `/etc/sudoers.d/` 的实际规则为准；通过 `visudo` 编辑并校验语法。典型的完整授权规则为 `username ALL=(ALL) ALL`，应按最小权限原则配置。

`/etc/pam.d/su` 中的 `pam_wheel.so` 规则可限制哪些用户能运行 `su`。sudo 和认证事件可通过 `journalctl` 及系统安全日志查看，日志路径随版本和 rsyslog 配置而异。原摘录还提到通过 PAM 的 `pam_tty_audit.so` 配置终端审计；启用前应先验证参数及审计范围。

### 系统注册与支持

- `subscription-manager register` 注册系统；`subscription-manager list --available` 查看可用订阅；`subscription-manager list --consumed` 查看已使用订阅。
- 旧的池绑定流程可用 `subscription-manager attach --pool=<池 ID>`，`subscription-manager remove --serial=<序列号>` 解绑。启用 Simple Content Access 的组织通常无需手动绑定订阅池。
- 用 `dnf repolist`（旧系统可用 `yum repolist`）查看仓库。Red Hat 支持工具可用于查看、创建和更新支持案例，具体功能取决于订阅与工具版本。

### OpenSSH

OpenSSH 提供加密的客户端与服务端通信，取代明文 Telnet。当前使用 SSH 协议版本 2；版本 1 已淘汰。系统级配置在 `/etc/ssh/`，用户级密钥与配置在 `~/.ssh/`。可生成密钥对，将公钥加入服务端授权列表，并用 `ssh-agent` 管理密钥。`scp` 用于加密复制文件，`sftp` 用于通过 SSH 传输文件。X11 forwarding 可把图形会话通过 SSH 通道转发；相关组件与安全配置按实际发行版安装。

### 邮件服务

邮件从客户端提交到邮件服务器，再经传输服务器送达收件人的服务器和客户端：

- **SMTP** 用于邮件提交和服务器之间的传输。现代邮件提交通常要求身份验证和加密；中继限制用于防止开放式转发和垃圾邮件。
- **POP3** 用于客户端取信，是否在服务器保留邮件由客户端和服务器配置决定；POP3S 使用 TLS 保护连接。Dovecot 可提供 POP3 服务。
- **IMAP** 让邮件保存在服务器并同步文件夹、已读等状态；Dovecot 也可提供 IMAP 服务。MIME 定义邮件内容格式，支持附件等内容。
- 邮件传输代理（MTA）如 Postfix、Sendmail；`fetchmail` 可从远端取回邮件交给本地投递流程。Procmail 可处理本地投递；邮件用户代理（MUA）如图形客户端 Evolution 和文本客户端 Mutt。
## Linux 运维实操专题

以下章节集中记录终端与环境、系统监控、网络配置、远程访问和文件共享的操作示例。执行网络切换、服务重启或同步命令前，请先核对当前系统和路径。

### 配置 Zsh 终端

Zsh 是命令解释器。它提供命令补全等功能，也可以通过插件添加语法高亮和输入建议。


#### Oh My Zsh

Oh My Zsh 是管理 Zsh 配置的开源框架，提供主题与插件。


#### macOS 配置

macOS 15 默认使用 Zsh，可直接安装 Oh My Zsh。安装、主题和插件示例也适用于 [[Linux-Shell/MacBook开发环境配置|MacBook 开发环境]]。

```sh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

安装器会将旧的 `~/.zshrc` 备份为 `~/.zshrc.pre-oh-my-zsh`；安装后将需要保留的配置迁移到新的 `~/.zshrc`。例如：

```sh
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="robbyrussell"
plugins=(git)
source "$ZSH/oh-my-zsh.sh"
```

下文的主题与插件章节说明 `af-magic`、Powerlevel9k/10k、`zsh-syntax-highlighting` 和 `zsh-autosuggestions` 的配置。


#### Linux 安装 Zsh

- 安装Zsh的方法很多，使用yum来安装很方便，不过OhMyZsh官方建议安装`5.0.8`以上版本，我们先来看下yum中的zsh版本号；

```sh
yum info zsh
```

- 如果你的版本号大于`5.0.8`可以使用yum来安装，使用如下命令即可，如果小于可以使用源码来安装；

```
yum -y install zsh
```

- 源码安装需要先下载Zsh的源码包，下载地址：https://zsh.sourceforge.io/Arc/source.html

- 先把下载好的源码包放到指定目录，然后使用如下命令进行解压安装；

```sh
# 安装依赖
yum -y install gcc perl-ExtUtils-MakeMaker git
yum -y install ncurses-devel
# 解压
tar xvf zsh-5.9.tar.xz
cd zsh-5.9
# 检查安装环境依赖是否完善
./configure
# 编译并安装
make && make install
```

- 安装完成后可以使用如下命令查看Zsh的路径；

```sh
whereis zsh
```

- 再把Zsh的路径添加到`/etc/shells`文件中去，在这里我们可以看到系统支持的所有命令解释器；

```sh
vim /etc/shells
# 添加内容如下
/usr/local/bin/zsh
```

- 最后查看下Zsh版本号，用于检测Zsh是否安装成功了。

```sh
zsh --version
```


#### 安装 Oh My Zsh

- 接下来我们来安装OhMyZsh，直接使用如下命令安装；

```sh
#墙外
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
#墙内
sh -c "$(curl -fsSL https://install.ohmyz.sh/)"
```

- 如果遇到下载不下来的情况，可以先创建一个`install.sh`文件，然后从Github上复制该文件内容，再使用如下命令安装：

```
# install.sh 地址：https://github.com/ohmyzsh/ohmyzsh/blob/master/tools/install.sh
./install.sh
```

- 安装完成后会提示你修改Linux使用的默认shell，使用如下命令可查看修改默认shell；

```sh
# 查看当前在使用的shell
echo $SHELL
# 也可以使用下面命令自行修改默认shell
chsh -s $(which zsh)
```

- 安装成功后配置文件为`.zshrc`，安装目录为`.oh-my-zsh`，安装目录结构如下。

![图片](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401081016712.png)

#### 主题配置

- OhMyZsh的主题非常丰富，自带主题都在`themes`文件夹中；

- 修改主题只需修改配置文件`.zshrc`的`ZSH_THEME`属性即可，下面我们把主题改为`af-magic`；

```sh
vim ~/.zshrc
# 修改如下内容
ZSH_THEME="af-magic"
# 刷新配置，每次修改后都需要
source ~/.zshrc
```

##### powerlevel9k

~~~sh
git clone https://github.com/bhilburn/powerlevel9k.git ~/.oh-my-zsh/custom/themes/powerlevel9k
vim ~/.zshrc
#修改主题配置为powerlevel9k
ZSH_THEME="powerlevel9k/powerlevel9k"
source ~/.zshrc
~~~

##### powerlevel10k

```sh
git clone https://github.com/romkatv/powerlevel10k.git "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
vim ~/.zshrc
#修改主题配置为powerlevel10k
ZSH_THEME="powerlevel10k/powerlevel10k"
exec zsh
```

#### 插件

Oh My Zsh 自带的插件位于 `plugins` 目录，也可以从第三方仓库安装插件。

##### zsh-syntax-highlighting

> [!tip] 平时我们输入Linux命令的时候，只有在执行的时候才知道输错命令了，这款插件可以实时检测命令是否出错。

- 下载插件到指定目录，使用如下命令即可；

```sh
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

- 然后修改配置文件`.zshrc`，在plugins中添加插件`zsh-syntax-highlighting`；

```sh
plugins=(
        git
        zsh-syntax-highlighting
)
```

- 接下来再输入命令时就有高亮提示了，正确命令会显示绿色。

##### zsh-autosuggestions

> [!tip] 自动补全插件，输入命令后会自动提示相关命令，使用方向键`→`可以实现自动补全。

- 下载插件到指定目录，使用如下命令即可；

```sh
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

- 然后修改配置文件`.zshrc`，在plugins中添加插件`zsh-autosuggestions`；
- 此时我们输入命令前缀就会直接提示命令，然后按方向键`→`就可以实现自动补全了。

##### zsh-history-substring-search

> [!tip] 输入历史命令中的任意片段后，可通过绑定的按键切换匹配结果。

- 下载插件到指定目录，使用如下命令即可；

```
git clone https://github.com/zsh-users/zsh-history-substring-search ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-history-substring-search
```

- 然后修改配置文件`.zshrc`，在plugins中添加插件`zsh-history-substring-search`；
- 在 `~/.zshrc` 中绑定按键；以下示例使用方向键上、下切换匹配结果：

```sh
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down
```

##### docker

> [!tip] 自带插件，可以实现docker命令补全和自动提示。

- 作为自带插件无需下载，直接修改配置文件`.zshrc`，在plugins中添加插件`docker`；
- 当我们输入docker开头的命令时，使用`Tab`键可以出现提示并自动补全。

##### git

> [!tip] 自带插件，添加了很多git的快捷命令。

- 直接修改配置文件`.zshrc`，在plugins中添加插件`git`；
- 该插件对于Git命令提供了非常多的快捷使用方式，比如下面的常用命令；

| 快捷别名 | 命令           |
| :------- | :------------- |
| g        | git            |
| gcl      | git clone      |
| ga       | git add        |
| gc       | git commit     |
| ggp      | git push       |
| ggl      | git pull       |
| gst      | git status     |
| gb       | git branch     |
| glg      | git log --stat |

##### z

> [!tip] 自带插件，根据目录访问历史匹配并跳转到常用目录。

- 直接修改配置文件`.zshrc`，在plugins中添加插件`z`，最终配置效果如下；

```
plugins=(
        git
        zsh-syntax-highlighting
        zsh-autosuggestions
        zsh-history-substring-search
        docker
        z
)
```

- 先访问 `~/.oh-my-zsh/custom/plugins`，离开后输入 `z plug`，即可按访问历史匹配并跳转到该目录。

### 项目环境变量与 direnv

#### 概述

direnv是一个环境变量管理工具，它可以扩展你的shell的环境变量。它的工作原理是根据当前目录动态地改变环境变量。具体来说，当你进入一个目录时，它会加载该目录下的.envrc文件来改变环境变量，这个过程被称为"装载"（loading）。相反，当你离开该目录时，它会卸载这些环境变量，这个过程被称为"卸载"（unloading）。

#### 功能

direnv的主要功能是管理和隔离环境变量。它可以让你在不同的项目中使用不同的环境变量，而不需要手动地去更改它们。这对于开发者来说非常有用，因为他们经常需要在不同的项目中切换，而每个项目可能需要不同的环境变量设置。通过使用direnv，开发者可以为每个项目创建一个.envrc文件，定义该项目所需的环境变量，然后direnv会自动地根据当前目录来装载和卸载这些环境变量。

#### 应用场景

1. 项目依赖管理：在Python项目中，你可能需要使用不同版本的Python或者不同的Python库。通过使用direnv，你可以为每个项目设置不同的Python路径和库。例如，你可以在.envrc文件中设置PYTHONPATH环境变量，指向该项目所需的Python库的路径。

2. 保密信息管理：如果你的项目需要一些保密的环境变量（如API密钥），你可以使用direnv来管理这些信息，而不是把它们硬编码到你的代码中。你可以在.envrc文件中设置这些保密的环境变量，然后在代码中通过环境变量来使用这些信息。请勿将包含真实密钥的 `.envrc` 提交到版本库；这样可以避免把保密信息暴露在代码中，同时，你也可以方便地在不同的环境中使用不同的保密信息。

#### 用法

##### 安装direnv

在Ubuntu上，你可以使用以下命令来安装direnv：

```sh
sudo apt-get install direnv
```

安装后按当前 Shell 在相应配置文件中启用 hook，并重启 Shell：

```sh
# Bash：加入 ~/.bashrc
eval "$(direnv hook bash)"

# Zsh：加入 ~/.zshrc
eval "$(direnv hook zsh)"
```

##### 创建.envrc文件

在你的项目目录中，创建一个.envrc文件，并在其中添加一些环境变量。例如，你可以使用以下命令来创建一个.envrc文件，并设置API_KEY环境变量：

```sh
echo export API_KEY=my_secret_key > .envrc
```

##### 允许direnv加载.envrc文件

由于安全原因，direnv默认不会加载.envrc文件。你需要使用以下命令来允许direnv加载该文件：

```sh
direnv allow
```

现在，每当你进入该目录时，API_KEY环境变量就会被设置为my_secret_key。当你离开该目录时，API_KEY环境变量就会被卸载，这样就可以防止这个保密信息被其他项目或命令误用。

### 终端代理配置

通过 `http_proxy` 和 `https_proxy` 为支持这些变量的命令行程序配置代理。以下函数修改当前 Shell 及其后续启动的子进程；将函数加载语句加入 Shell 配置后，新终端也可调用。请按实际代理地址和端口调整示例。

#### 定义代理开关

```sh
tee ~/network_proxy.sh <<'EOF'
proxy_on() {
    export http_proxy=http://127.0.0.1:7890
    export https_proxy="$http_proxy"
    echo "终端代理已开启。"
}

proxy_off() {
    unset http_proxy https_proxy
    echo "终端代理已关闭。"
}
EOF

# 在当前 Shell 加载函数
source ~/network_proxy.sh
```

#### 在新终端中加载

Bash 交互终端通常读取 `~/.bashrc`，Zsh 读取 `~/.zshrc`。按当前 Shell，在相应配置文件中加入一行：

```sh
source ~/network_proxy.sh
```

#### 使用与检查

- 运行 `proxy_on` 开启代理，运行 `proxy_off` 关闭代理。
- 可用 `curl cip.cc` 或 `curl myip.ipip.net` 查看出口 IP；查询服务是否可用取决于当前网络。

### screen 后台会话

一些任务需要在一个终端运行，能够保留运行日志，并不随着终端的关闭而终止。这个时候，就需要screen命令来执行这样的事。

#### screen命令后台运行

##### 创建会话

```sh
screen -S baidudl
```

- 这样，我们就创建了一个名为baidudl的会话（session）。

- 接下来，我们执行Ctrl-A D，就可以退出并保持当面会话。

- 接下来，我们通过`screen -ls`查看系统运行了哪些screen会话。

- 可以看到刚创建的baidudl已经创建了，接下来我们通过`screen -r baidudl`重新进入刚创建的会话

##### 退出会话

```sh
#方法一：
exit
#方法二：
screen -S 209684.baidudl -X quit
```

##### 分离会话

- screen -r进入不了会话，报错："There is no screen to be resumed matching"，这通常意味着该会话正在被另一个终端使用，或者没有被正确分离（Detached）。

- 如果确定会话没有被其他用户使用，可以尝试强制分离当前会话并重新附加：

```sh
screen -D -r 209652
```

##### 保存日志

```sh
screen -L -S download # 在当前目录创建 screenlog.0 日志
```

### 系统信息与资源监控

#### 查看内存使用情况

- /proc/meminfo

  这个动态更新的虚拟文件实际上是许多其他内存相关工具(如：free / ps / top)等的组合显示。/proc/meminfo列出了所有你想了解的内存的使用情况。进程的内存使用信息也可以通过 /proc/\<pid>/statm 和 /proc/\<pid>/status 来查看。

- free -h

  是对 /proc/meminfo 收集到的信息的一个概述。

- ps

  ps 命令显示执行时各进程的内存使用快照，可以按 RSS 排序输出。

  - %MEM (percent of physical memory used),

  - VSZ (total amount of virtual memory used)

  - RSS (total amount of physical memory used)。

```bash
ps aux --sort -rss
```

- top

  与ps作用相似，优点是可以动态更新。top命令提供了实时的运行中的程序的资源使用统计。你可以根据内存的使用和大小来进行排序。

  - `top`命令的界面中，按`M`键。这将按照内存使用量对进程进行排序。（P：按CPU排序；N：按照PID排序）
  - `RES`列代表了每个进程实际使用的物理内存大小，`%MEM`列则显示了每个进程使用的物理内存占总内存的百分比。

- vmstat -s -S M

  vmstat命令显示实时的和平均的统计，覆盖CPU、内存、I/O等内容。例如内存情况，不仅显示物理内存，也统计虚拟内存。

- atop

- htop


#### 查看CPU使用情况

- top

  ![image-20231204193316963](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202312041933186.png)

  - cpu相关参数解释
    - us：用户空间占CPU的百分比（像shell程序、各种语言的编译器、各种应用、web服务器和各种桌面应用都算是运行在用户地址空间的进程，这些程序如果不是处于idle状态，那么绝大多数的CPU时间都是运行在用户态）。
    - sy：内核空间占CPU的百分比（所有进程要使用的系统资源都是由Linux内核处理的，对于操作系统的设计来说，消耗在内核态的时间应该是越少越好，在实践中有一类典型的情况会使sy变大,那就是大量的IO操作，因此在调查IO相关的问题时需要着重关注它）。
    - ni：用户进程空间改变过优先级（ni是nice的缩写，可以通过nice值调整进程用户态的优先级，这里显示的ni表示调整过nice值的进程消耗掉的CPU时间，如果系统中没有进程被调整过nice值，那么ni就显示为0）。
    - id：空闲CPU占用率。
    - wa：等待输入输出的CPU时间百分比（和CPU的处理速度相比，磁盘IO操作是非常慢的，有很多这样的操作，比如，CPU在启动一个磁盘读写操作后，需要等待磁盘读写操作的结果。在磁盘读写操作完成前，CPU只能处于空闲状态。Linux系统在计算系统平均负载时会把CPU等待IO操作的时间也计算进去，所以在我们看到系统平均负载过高时，可以通过wa来判断系统的性能瓶颈是不是过多的IO操作造成的）。
    - hi：硬中断占用百分比【硬中断是硬盘、网卡等硬件设备发送给CPU的中断消息，当CPU收到中断消息后需要进行适当的处理(消耗CPU时间)】。
    - si：软中断占用百分比（软中断是由程序发出的中断，最终也会执行相应的处理程序，消耗CPU时间）
  - 某个进程的%CPU超过100%，说明系统有多核，按1可以看到每个核的cpu占用情况。


#### Disk使用情况

- df -h
  - `df -h` provides information on the overall disk space usage, showing statistics for each mounted file system.

- du -h
  - `du -h` provides information about the sizes of directories and files in a specified directory or a list of directories.
  - du -sh (summary，而不是列出全部)

- lsblk -f

  - `lsblk -f` command is used to list information about block devices, including file system information.

- fdisk -l

  - `fdisk -l` command is used to list information about the **disk partitions** on a system.


#### OS 信息查看

- 查看OS版本

```shell
cat /etc/*release
```

- 查看kernel信息

```shell
uname -a
```

- 查看已加载的内核模块

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


#### 查看硬件信息

- lshw
- lspci

### inotifywait 文件监控与同步

- 有时候我们常需要当文件变化的时候便触发某些脚本操作，比如说有文件更新了就同步文件到远程机器。在实现这个操作上，主要用到两个工具，一个是rsync，一个是inotifywait。inotifywait的作用是监控文件夹变化,rsync是用来同步，可同步到本机的其他目录或者远程服务器上。

> [!info] inotify相关工具
> - inotify 是一个 Linux 内核提供的 API，它可以监视文件系统事件，比如文件或目录的创建、删除、修改等。
>
> - inotify-tools 是一套用户空间的工具，包括 inotifywait 和 inotifywatch，用于使用 inotify API。这些工具可以对文件系统事件进行监控，并生成相应的警告或日志。
>
> - inotifywait是一个非常实用的命令，它属于inotify-tools包，可以用来监控Linux文件系统事件。

#### 安装rsync+inotifywait

```sh
# 以下为固定旧版本的源码安装示例；下载地址和依赖可能已变化
wget http://rsync.samba.org/ftp/rsync/src/rsync-3.1.1.tar.gz
tar zxvf rsync-3.1.1.tar.gz
cd rsync-3.1.1
./configure --prefix=/usr/local/rsync-3.1.1
make
make install

wget http://github.com/downloads/rvoicilas/inotify-tools/inotify-tools-3.14.tar.gz
tar zxvf inotify-tools-3.14.tar.gz
cd inotify-tools-3.14
./configure
make
make install

# Ubuntu 上优先使用包管理器
sudo apt install rsync inotify-tools
```

#### inotifywait基本使用

```sh
#监控文件的修改操作：
inotifywait -m -r -e modify /path/to/file
#监控目录或文件的属性变化：
inotifywait -m -r -e attrib /path/to/directory
#监控多个目录或文件的事件：
inotifywait -m -r -e create,delete,move /path/to/directory1 /path/to/directory2 /path/to/file1 /path/to/file2
# 监控事件并在每次事件后执行命令：
inotifywait -m -r -e create,delete,move /path/to/directory |
  while IFS= read -r event; do
    /path/to/command
  done
```

#### 创建监控同步脚本

> [!warning] 同步方向
> 下例按事件触发 `rsync`。带 `--delete` 的示例会删除目标端多余文件；运行前先确认源目录和目标目录。

```sh
#!/bin/bash
export CNROMS_SRC=/home/ftpuser/gri/   # 同步的路径，请根据实际情况修改
inotifywait --exclude '\.(part|swp)' -r -mq -e  modify,move_self,create,delete,move,close_write "$CNROMS_SRC" |
  while read event;
    do
    rsync -vazu --progress  --password-file=/etc/rsyncd_rsync.secret  /home/ftpuser/gri/sla  rsync@10.208.1.1::gri ##这里执行同步的命令，可以改为其他的命令

  done
```

```sh
#后台运行脚本
chmod +x inotifywait.sh
#如果不想生成日志
nohup bash inotifywait.sh > /dev/null 2>&1
#如果想生成日志
nohup bash inotifywait.sh > output.log 2>&1
```


#### systemd 管理 rsync 同步任务

##### 编写rsync脚本

```sh
#!/bin/bash

SRC_DIR="/home/s0001969/Documents/learning-notes-git"
DEST_DIR="/home/backup/"
LOGFILE="/var/log/rsync_sync.log"
DELAY=10 #增加延迟时间以减少频繁同步

while inotifywait -e modify,move_self,create,delete,move,close_write -r "$SRC_DIR"
do
    echo "Sync started at $(date)" >> "$LOGFILE"

    if rsync -avhz --delete "$SRC_DIR" "$DEST_DIR"; then
        echo "Sync successful at $(date)" >> "$LOGFILE"
    else
        echo "Sync failed at $(date)" >> "$LOGFILE"
    fi

    sleep $DELAY
done
```

##### 创建systemd服务单元

```sh
tee rsync-inotifywait.service <<'EOF'
[Unit]
Description=Sync Service
After=network.target

[Service]
ExecStart=/bin/bash /home/s0001969/rsync-inotifywait.sh
Restart=Always
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo cp rsync-inotifywait.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable rsync-inotifywait.service
sudo systemctl start rsync-inotifywait.service && sudo systemctl status rsync-inotifywait.service
```

- 查看所有service

```sh
sudo systemctl --type=service
#只查看active的
sudo systemctl --type=service --state=active
```

- 禁用service

```sh
sudo systemctl disable rsync-inotifywait.service
```

### nmcli 网络配置

`nmcli` 用于管理 NetworkManager 的网络设备和连接配置。以下示例适用于由 NetworkManager 管理的 CentOS、RHEL、Rocky Linux 或 Ubuntu；执行前先确认目标网卡和连接配置的实际名称，不能仅凭发行版推断网络管理器。

#### 查看与创建连接

```sh
nmcli device            # 查看网卡及管理状态
nmcli connection show   # 查看连接配置名称
nmcli connection add con-name ens33 ifname ens33 type ethernet
```

`ens33` 在这里既是连接配置名，也是网卡名；实际环境中两者可能不同。需要删除旧配置时，传入 `nmcli connection show` 列出的**连接配置名**，例如 `nmcli connection delete ens33`。新建以太网连接时，默认 IPv4 方法通常为自动获取地址，以下示例再改为静态地址。

#### 配置静态 IPv4

假设想把网卡配置改为如下：

- IP地址：192.168.211.201
- 掩  码：255.255.255.0
- 网  关：192.168.211.2
- DNS地址：8.8.8.8和114.114.114.114

> [!warning] 远程修改网络
> 停用连接可能中断当前 SSH 会话；请准备控制台或其他恢复方式，并核实 IP、网关和 DNS。

```sh
nmcli connection modify ens33 ipv4.method manual connection.autoconnect yes # 静态 IPv4 与自动连接
nmcli connection modify ens33 ipv4.addresses 192.168.211.201/24 # IP 地址与掩码
nmcli connection modify ens33 ipv4.gateway 192.168.211.2 # 网关
nmcli connection modify ens33 ipv4.dns 8.8.8.8,114.114.114.114 # 多个 DNS 以逗号分隔
nmcli connection down ens33 # 停用连接
nmcli connection up ens33   # 重新启用连接
```

```sh
# 也可以用一条命令修改
nmcli connection modify ens33 ipv4.addresses 192.168.211.201/24 ipv4.gateway 192.168.211.2 ipv4.dns 8.8.8.8,114.114.114.114 ipv4.method manual connection.autoconnect yes
```

### SSH 连接与远程执行

SSH（Secure Shell）为远程登录和通信提供加密与身份认证，常见实现是 OpenSSH。下文用“SSH”指协议，用 `ssh` 指客户端命令。

#### 登录服务器与验证主机

```sh
ssh user@hostname
ssh -p 2222 user@hostname # 指定非默认端口
```

`user` 是远端用户名，`hostname` 可以是主机名或 IP；默认端口是 22。首次连接时，客户端会提示确认主机密钥指纹。应先核对指纹，再信任该主机；以后会使用 `~/.ssh/known_hosts` 中的记录核对服务器身份。该文件保存主机密钥，也可以使用哈希形式保存主机名。身份认证可使用密码或公钥。

#### 客户端连接配置

用户配置文件位于 `~/.ssh/config`。可以为常用服务器设置别名、用户名和端口：

```sshconfig
Host remote
    HostName xxxx.yyyy.com
    User us
    Port 2222
```

之后执行 `ssh remote`，相当于 `ssh -p 2222 us@xxxx.yyyy.com`。

#### 公钥登录

公钥认证省去每次输入账户密码。客户端保管私钥，服务器将对应公钥加入该用户的 `~/.ssh/authorized_keys`。认证时客户端用私钥签名，服务器用已登记的公钥验证签名。

1. 在客户端生成密钥。当前 OpenSSH 默认生成 Ed25519 密钥，通常保存为 `~/.ssh/id_ed25519` 和 `~/.ssh/id_ed25519.pub`；如果显式使用 `-t rsa`，文件名通常为 `id_rsa` 和 `id_rsa.pub`。

   ```sh
   ssh-keygen
   ```

2. 将公钥加入远端账户的 `~/.ssh/authorized_keys`，或在客户端用 `ssh-copy-id` 自动上传：

   ```sh
   ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host
   ```

   首次上传通常仍需现有的登录方式；不要向服务器复制私钥。

#### scp 复制文件

`scp` 通过 SSH 在本地和远端之间加密复制文件，也支持两台远端主机之间复制。基本语法是 `scp source destination`，远端路径中的主机名和文件名用冒号连接：

```sh
scp user@host:example.txt ./temp.txt # 从远端用户主目录复制到本地当前目录
```

#### VS Code 配置远程服务器免密连接

> [!info] 参考文档
> [VSCode——SSH免密登录_vscode免密登录ssh_Irving.Gao的博客-CSDN博客](https://blog.csdn.net/qq_45779334/article/details/129308235)

1. 首先需要在vscode电脑上生成公钥私钥对：

   ```bash
   ssh-keygen
   ```

   从命令输出中查看到保存路径。

2. 将生成的公钥（默认 `id_ed25519.pub`）内容复制到远程主机上：

   ```bash
   vim ~/.ssh/authorized_keys #新建authorized_keys文件
   #将公钥值复制进去
   ```

3. 赋权限

   ```bash
   chmod 700 /home/userName # 远端用户主目录需要限制写权限
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

4. 修改ssh配置文件

   ```bash
   sudo vim /etc/ssh/sshd_config
   # 确认 PubkeyAuthentication yes；默认配置可能已允许公钥认证
   ```

5. 如果实际修改了 sshd 配置，先运行 `sshd -t` 检查，再按发行版重启 `sshd`（RHEL 系）或 `ssh`（Ubuntu）。

   ```bash
   sudo sshd -t
   sudo systemctl restart sshd.service # RHEL/CentOS/Rocky
   ```

6. 在vscode的ssh配置文件中加入远程主机信息

   ```bash
   Host 60.204.142.111
     HostName 60.204.142.111
     User root
     Port 23333
     IdentityFile C:\Users\hangx\.ssh\id_ed25519
   ```

此时可以vscode免密远程登录到虚拟机。


#### 连接故障排查

- windows从公司账户切换到个人账户后，将公司账户配置文件里面的/.ssh/config文件拷贝到了个人账户的/.ssh中，在个人账户的vscode中尝试ssh连接时，报错：`Bad owner or permissions on C:\\Users\\xuhan/.ssh/config`

  - 解决办法：

![image-20240113075011013](https://raw.githubusercontent.com/hangx969/upload-images-md/main/202401130750113.png)

- vscode ssh登录vmware虚拟机时报错：Address 192.168.*.* maps to localhost, but this does not map back to the address - POSSIBLE BREAK-IN ATTEMPT!

  - 是因为DNS服务器把 192.168.x.x 的地址都反向解析成 localhost 。 解决的办法就是，编辑 ssh 客户端的 /etc/hosts 文件，把出问题的IP 地址和主机名加进去，就不会报这样的错了。

  - 核对客户端 `/etc/hosts` 和 DNS 的正反向解析。若客户端 `/etc/hosts` 中为目标 IP 配置了正确主机名，可尝试用该主机名连接；无需为客户端解析问题重启服务端 `sshd`。


#### Azure 上修改 SSH 端口（CentOS 8 示例）

以下示例将端口从 22 改为 2222。保持现有会话，直到新端口登录成功。示例使用 PuTTY 连接 Azure VM，并假定本机由 firewalld 管理防火墙。

1. 登录 VM，按需获取管理员权限：

   ```sh
   sudo su
   ```

2. 修改 `/etc/ssh/sshd_config`，将默认端口注释 `#Port 22` 改为：

   ```text
   Port 2222
   ```

3. 若使用 firewalld，先确认它的状态，然后放行 TCP 2222。启动 firewalld 前也应确认现有 SSH 端口仍允许连接。

   ```sh
   systemctl status firewalld
   sudo firewall-cmd --permanent --zone=public --add-port=2222/tcp
   sudo firewall-cmd --reload
   sudo firewall-cmd --zone=public --list-ports
   ```

4. 若 SELinux 为 enforcing，为 SSH 服务登记新端口；无需为此把 SELinux 改为 permissive。

   ```sh
   getenforce
   sudo semanage port -a -t ssh_port_t -p tcp 2222
   ```

   如果 TCP 2222 已有其他 SELinux 映射，先用 `semanage port -l` 查明归属。缺少 `semanage` 时，先安装系统对应的软件包。

5. 在 Azure 门户的 VM 入站网络安全组规则中放行 TCP 2222。先保留 TCP 22 规则，以免新端口尚不可用时失去连接。

6. 检查 `sshd` 配置，重启服务；在另一 PuTTY 窗口用端口 2222 重新登录：

   ```sh
   sudo sshd -t
   sudo systemctl restart sshd.service
   ```

7. 仅在确认新连接成功后，才按需删除旧的 TCP 22 入站规则。

References:

[Changing the SSH port for a RHEL Azure VM - Paul S. Randal (sqlskills.com)](https://www.sqlskills.com/blogs/paul/changing-the-ssh-port-for-a-rhel-azure-vm/)

[How to Change the SSH Port on Dedicated and VPS | HostGator Support](https://www.hostgator.com/help/article/how-to-change-the-ssh-port-on-dedicated-and-vps)

[SELinux入门 | 《Linux就该这么学》 (linuxprobe.com)](https://www.linuxprobe.com/selinux-introduction.html)

[SSHD服务启动失败 – 笛声 (hqidi.com)](https://hqidi.com/133.html)

#### 远程执行多个命令

##### 单台服务器

通过 here document 向远端 Bash 传递多条命令：

```sh
ssh user@remote_host /usr/bin/bash <<'EOF'
pwd
ls -l
whoami
EOF
```

##### 多台服务器

以下示例逐台连接 `cn01dl001` 至 `cn01dl004`，调整 Munge 目录和密钥权限：

```sh
for i in $(seq 1 4); do
  ssh -t "test@cn01dl00$i" "sudo chown munge: /etc/munge/munge.key; sudo chmod 400 /etc/munge/munge.key; sudo chmod 700 /etc/munge/; sudo chmod 711 /var/lib/munge/; sudo chmod 700 /var/log/munge/; sudo chmod 755 /var/run/munge/; sudo chown munge.munge /etc/munge/munge.key;"
done
```

### Samba 文件共享

Samba 在 Linux/Unix 上提供 SMB 文件与打印共享服务，使 Windows 和 Linux 客户端可以访问共享资源。`smb` 提供文件共享，`nmb` 用于旧式 NetBIOS 名称解析；是否需要 `nmb` 取决于客户端和网络环境。以下以 RHEL/CentOS 风格系统上的 `/share` 共享为例。

#### 服务端：创建用户和共享目录

1. 创建两个不允许交互登录的系统用户，并安装 Samba：

   ```sh
   useradd -s /bin/nologin user01
   useradd -s /bin/nologin user02
   yum -y install samba
   ```

2. 创建共享目录。原实验使用 `777` 以便快速验证；该权限允许本机所有用户写入，只适用于隔离测试。正式环境应按用户或用户组配置文件系统权限，Samba 的 `writable` 不会绕过文件系统权限。

   ```sh
   mkdir /share
   chmod -R 777 /share/
   ```

3. 为系统用户创建 Samba 账号并交互设置密码。`smbpasswd` 与 `pdbedit` 都可添加 Samba 用户：

   ```sh
   smbpasswd -a user01
   pdbedit -a -u user02
   ```

#### 服务端：配置共享与访问控制

在 `/etc/samba/smb.conf` 中添加共享定义，随后重启 `smb`：

```ini
[myshare]
    comment = public document
    path = /share
    public = no
    browseable = Yes
    writable = Yes
```

```sh
systemctl restart smb
```

防火墙启用时，放行 Samba 服务并重新加载规则。原实验通过停止 firewalld 测试，但正常配置应保留防火墙：

```sh
firewall-cmd --add-service=samba --permanent
firewall-cmd --reload
```

为共享目录设置 SELinux 类型：

```sh
chcon -R -t samba_share_t /share
```

`chcon` 设置可能在重新标记文件系统时被覆盖；需要持久化时应使用相应的 SELinux 文件上下文规则。仅在确实需要访问用户家目录时，检查并开启对应布尔值：

```sh
getsebool -a | grep samba
setsebool -P samba_enable_home_dirs on
```

原实验列出的相关布尔值还有 `samba_create_home_dirs`、`samba_domain_controller`、`samba_export_all_ro`、`samba_export_all_rw`、`samba_load_libgfapi`、`samba_portmapper`、`samba_run_unconfined`、`samba_share_fusefs`、`samba_share_nfs`、`sanlock_use_samba`、`tmpreaper_use_samba`、`use_samba_home_dirs`、`virt_use_samba`。应按实际共享目录和权限需求选择，不必全部开启。

#### Windows 客户端

在文件资源管理器地址栏访问 `\\192.168.147.11`，输入前述 Samba 用户名和密码。若要排查已缓存的 Windows 网络连接，可先在命令提示符运行 `net use * /del`，再重新连接。

#### Linux 客户端

安装客户端工具，列出共享并连接 `myshare`：

```sh
yum -y install samba-client cifs-utils
smbclient -L 192.168.147.11 -U user01
smbclient //192.168.147.11/myshare -U user01
```

连接后可在 `smbclient` 提示符中运行 `mkdir test_share`，验证写入权限。也可以临时挂载共享目录：

```sh
mkdir /usershare
mount -t cifs //192.168.147.11/myshare /usershare/ -o username=user01
ls -l /usershare/
```
