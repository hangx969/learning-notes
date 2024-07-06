Ubuntu 2004配置静态IP: [为Ubuntu 20.04 设置静态IP简明教程（和把大象装冰箱一样简单）-腾讯云开发者社区-腾讯云 (tencent.com)](https://cloud.tencent.com/developer/article/1933335)



# 操作练习

## linux admin

1. User Admin

- Create a user with your name with uid 2001, with default config

  ~~~sh
  adduser --uid 2001 hangx
  ~~~

  > - adduser和useradd都可以在ubuntu中创建新用户。但是二者还有区别：
  >
  >   - `useradd` 是一个基本的 Linux 命令，它直接创建新的用户。它不会自动创建用户的主目录，也不会复制 `/etc/skel` 目录中的文件到新用户的主目录。如果你想要这些功能，**你需要手动指定 `-m` 或 `-k` 选项。**
  >   - `adduser` 是 Debian 和 Ubuntu 系统中的一个脚本，它是 `useradd` 的一个更友好的前端。这个脚本会自动创建新用户的主目录，复制 `/etc/skel` 目录中的文件，以及进行其他一些设置。它也会提供一个交互式的界面来收集新用户的信息，如全名和密码。
  >
  > - 什么是default config：
  >
  >   - 用户的主目录（通常是 `/home/username`）
  >   - 用户的默认 shell（通常是 `/bin/bash` 或 `/bin/sh`）
  >   - 用户的用户组（通常与用户名相同）
  >   - 用户的用户 ID 和组 ID（通常由系统自动分配）
  >
  > - 在 Ubuntu 中，用户的默认配置存储在 `/etc/default/useradd` 文件中。
  >
  > - `/etc/skel` 目录包含了一些初始化文件，这些文件会在创建新用户时复制到新用户的主目录中。这些文件通常包括一些 shell 配置文件（如 `.bashrc` 和 `.profile`），以及其他一些默认的设置文件。
  >
  >   - 这样做的目的是为了提供一个统一的初始环境给所有新创建的用户。这些文件定义了用户的 shell 环境，包括命令别名、环境变量、shell 提示符等等。通过修改 `/etc/skel` 目录中的文件，系统管理员可以控制新用户的初始环境。
  >
  >   - 例如，如果你想要所有新用户都有一个特定的命令别名，你可以在 `/etc/skel/.bashrc` 文件中添加这个别名，然后所有新创建的用户都会在他们的 `.bashrc` 文件中有这个别名。

- Create group zenseact with gid 2002 and add user into it

  ~~~sh
  groupadd -g 2002 zenseact
  usermod -aG zenseact hangx #`-aG`（指定要添加到的组）和用户名
  ~~~

  > - 如何在 Ubuntu 中查看用户所属的用户组？
  >
  >   ~~~sh
  >   groups newuser #这个命令将会列出用户 newuser 所属的所有用户组。
  >   id newuser #这个命令将会输出用户 newuser 的用户 ID、组 ID 以及所属的用户组。
  >   ~~~
  >
  > - -aG是将用户添加到组里。**-g 是修改用户的主用户组**。
  >
  > - 主用户组的作用主要是文件系统权限管理。每个文件和目录都有一个用户所有者和一个组所有者。用户所有者通常是创建这个文件或目录的用户，而组所有者默认是创建这个文件或目录的用户的**主用户组**。
  >
  >   - 文件和目录的权限被分为三组：用户权限、组权限和其他权限。用户权限适用于用户所有者，组权限适用于组所有者，其他权限适用于所有其他用户。
  >
  >   - 通过设置组所有权和组权限，你可以控制哪些用户可以读取、写入或执行这个文件或目录。
  >   - 例如，如果你想要让一个用户组的所有用户都可以读取和写入一个文件，你可以将这个文件的组所有权设置为这个用户组，然后设置组权限为读写权限。

- Verify this task if all setup correctly

  ~~~sh
  #查看用户
  cat /etc/passwd | grep hangx
  #查看用户所属的组
  groups hangx
  ~~~

2. Install sshd and ensure services start on boot

   ~~~sh
   apt install -y sshd
   systemctl enable sshd
   ~~~

   > `apt`和`apt-get`都是Ubuntu和其他基于Debian的系统中的包管理工具。它们都可以用来安装、更新、升级和删除软件包。
   >
   > 主要的区别在于：
   >
   > 1. **用户友好性**：`apt`被设计为更用户友好，它提供了颜色编码的输出和进度条等功能。
   > 2. **命令简洁性**：`apt`的命令更简洁。例如，`apt full-upgrade`相当于`apt-get dist-upgrade`。
   > 3. **输出**：`apt`提供了更简洁、更易于阅读的输出。
   > 4. **稳定性**：`apt-get`在长期支持（LTS）版本中更稳定。因此，对于服务器和其他需要稳定性的环境，`apt-get`可能是更好的选择。
   >
   > apt命令使用：
   >
   > - `apt-get install <package-name>=<version-number>` -- 安装特定版本的包
   > - `apt-cache policy package name` -- 查看一个包的可用版本
   > - `dpkg --get-selections`, `apt list --installed`可以查看已经安装的包
   > - `apt remove <package-name>` -- 卸载软件包，但是不会卸载配置文件
   > - `apt purge <package name>` -- 卸载软件包，包括配置文件 

3. Update all packages, except Kernel headers

   ~~~sh
   apt update
   apt list --upgradable
   #查看kernel header的包
   apt list --installed | grep linux-header
   apt-mark hold linux-headers-6.2.0-1018-azure linux-headers-azure
   apt upgrade
   ~~~

   > - apt update和apt upgrade的区别
   >
   > 1. **apt update**：此命令用于更新系统的包列表。它会从你在系统中配置的软件源获取最新的包信息，包括新的软件包和现有软件包的更新。这个命令不会实际安装或升级任何软件包，只是更新了系统知道的可用软件包的信息。
   > 2. **apt upgrade**：此命令用于实际升级系统中的软件包。它会查看你已经安装的软件包，并检查是否有可用的更新。如果有，它会下载并安装这些更新。这个命令需要在运行`apt update`之后运行，以确保你的系统知道所有可用的更新。
   >
   > - 如何在apt upgrade时排除掉特定的包
   >   - `apt-mark hold`排除掉特定的包
   >   - `apt-mark showhold`可以查看标记为hold的包
   >   - `apt-mark unhold`可以取消hold
   >
   > - 如何辨别哪些包是kernel header
   >   - 在Ubuntu和其他基于Debian的系统中，内核头文件通常包含在以下几个包中：
   >     - `linux-headers-generic`：这个包包含了通用内核的头文件。这些头文件对于编译大多数内核模块是必需的。
   >     - `linux-headers-$(uname -r)`：这个包包含了当前运行的特定版本内核的头文件。这些头文件对于编译针对当前内核版本的模块是必需的。
   >
   >   - 检查是否安装kernel header
   >
   >     ~~~bash
   >     dpkg-query -s linux-headers-$(uname -r)
   >     ~~~
   >
   > - 更多关于Ubuntu linux kernel的信息：[linux - ubuntu22.04 的内核版本为什么有多个？ - SegmentFault 思否](https://segmentfault.com/q/1010000044156233)
   >
   >   - ubuntu kernel：[https://ubuntu.com/kernel](https://link.segmentfault.com/?enc=wiXbkZbHsoC%2F8N1euDgGvg%3D%3D.zeyQNXTuqhLTzd3p%2B0TxOBlG%2F%2B4RYIn4VkzZz28pWhI%3D)说明，最新的LTS镜像会安装`-hwe`内核，这个是高版本的内核，通常应该是下个LTS版本使用的内核，每个版本的内核支持时间可以在上述链接找到图文说明。[https://ubuntu.com/kernel/lifecycle](https://link.segmentfault.com/?enc=N1Nt3jzKquIbBccUe3MvzA%3D%3D.B6HQsmVKJP4l21kBfysTFzGpNuij9%2BDYjvkNZtC46Fn3DcwRmjeoZiWxOuYOAUer)
   >   - 此外，ubuntu还有其他可用备选内核，参考: [https://ubuntu.com/kernel/variants#current-variant-kernels](https://link.segmentfault.com/?enc=2meiVWW6SxS0FtZ0j%2BCsHw%3D%3D.xroP7rO%2FKNQsvIjnmDu%2BE7C9%2FuRsiH4bmjz46aG%2B%2BOYbx5s933QjhuolCLSwyQeHqTPGf3%2ByrshKb5zpr8NXpw%3D%3D)
   >   - 简单来说，就是Ubuntu认为硬件更新迭代可能比较快，而LTS版本支持时间比较长(已经从20.04版本之前的5年延长到目前的10年支持)，所以旧的LTS版本可能无法跟上新硬件的适配，因此Ubuntu搞了个`HWE`包，让旧的LTS版本用上新的LTS版本的内核以便可以在不升级整个OS版本(`do-release-upgrade`)的情况下使用新版本的内核，以支持新的硬件。

4. enable your username to run a command fdisk as root (sudoers)

   ~~~sh
   visudo #visudo提供锁定和语法检查，比直接vim /etc/sudoers更有用
   #末尾添加一行：
   hangx ALL=(ALL:ALL) NOPASSWD: /usr/bin/fdisk
   #ctrkl+O 保存，ctrl+X退出
   ~~~

   > username ALL=(ALL:ALL) NOPASSWD: /path/to/command命令解释：
   >
   > - `username`：这是用户名，表示这条规则适用于哪个用户。
   > - `ALL=`：这是主机名部分，表示这条规则适用于哪些主机。在这里，`ALL`表示这条规则适用于所有主机。
   > - `(ALL:ALL)`：这是运行命令的用户和组。第一个`ALL`表示命令可以以任何其他用户的身份运行，第二个`ALL`表示命令可以以任何组的身份运行。
   > - `NOPASSWD:`：这表示用户在执行这条命令时不需要输入密码。
   > - `/path/to/command`：这是用户可以执行的命令的完整路径。
   >
   > 如何查看一个用户的sudo权限：
   >
   > ```sh
   > su - username
   > su -l
   > ```

5. login with your username

   1. generate ssh public key pair for your username and enable passwordless ssh for this VM

      ~~~sh
      ssh-keygen -t rsa
      ssh-copy-id -i /root/.ssh/id_rsa.pub hangx@<VM IP> 
      ~~~

   2. run fdisk -l

## Storage Admin

1. Check current LVM setup

   ~~~sh
   lsblk -f #看一下disk情况
   pvdisplay
   vgdisplay
   lvdisplay
   ~~~

2. Create a partition volume_zenseact of 2GB

   ~~~sh
   fdisk /dev/sda
   #使用fdisk命令启动磁盘分区工具。假设你想在/dev/sda磁盘上创建分区，你可以使用以下命令：
   #在fdisk命令提示符下，按n来创建一个新的分区。
   #接下来，它会询问你要创建主分区还是扩展分区。对于大多数情况，你应该选择创建主分区，所以按p。
   #然后，它会询问你分区的编号。如果这是磁盘上的第一个分区，那么应该输入1。
   #接下来，它会询问分区的第一个和最后一个扇区。你可以接受默认值来创建一个使用所有可用空间的分区。（+10G创建10G大小的分区）
   #最后，按w来写入分区信息并退出。
   #创建文件系统
   mkfs.ext4 /dev/sda1
   #挂载一个分区实际上就是让操作系统识别该分区的文件系统，从而可以在该分区上读写文件。如果一个分区没有文件系统，那么操作系统就无法识别和使用它。因此，通常在挂载一个分区之前，你需要先对其进行格式化，创建一个文件系统。在Linux中，常见的文件系统类型有ext4、ext3、xfs等。
   
   #给磁盘打一个标签
   e2label /dev/sda1 volume_zenseact
   #lsblk -f 查看标签
   ~~~

3. Mount this partition

   ~~~sh
   mkdir /mnt/datadisk1
   mount LABEL=volume_zenseact /mnt/datadisk1/ #通过分区的标签挂载目录
   ~~~

4. Extend this partition by 1GB

   - 思路是删除旧分区，重新创建更大的新分区

   ~~~sh
   fdisk /dev/sda
   p #查看磁盘分区情况，记住需要扩容的磁盘的起始sector号
   d #删除之前的分区
   n #建立新分区
   p #主分区
   1 #第一个分区
   2048 #起始扇区号 （这是数据不丢失的关键）
   +11G #输入新的分区大小
   #如果有提示是否删除原来的filesystem signature，选择不需要
   w #保存退出
   ~~~

   ~~~sh
   e2fsck -f /dev/sda1 #检查修复文件系统错误
   resize2fs /dev/sda1 #扩容文件系统，让文件系统识别这些新的空间。
   ~~~

   > - umount之后，执行fdisk/e2fsck/resize2fs的时候仍会有提示device busy，可以用`fuser -um`或者`lsof`查看使用分区的进程，可以用`fuser -km`杀掉占用的进程。然后再去执行resize2fs等操作。

## Filesystem

- Create a mount for a directory / volume_zenseact and export it

  ~~~sh
  mount LABEL=volume_zenseact /mnt/datadisk
  #安装nfs
  apt install -y nfs-kernel-server
  #配置nfs共享
  vim /etc/exports
  /mnt/datadisk1 *(rw,no_root_squash)
  #rw 该主机对该共享目录有读写权限
  # no_root_squash 登入 NFS 主机使用分享目录的使用者，如果是 root 的话，那么对于这个分享的目录来说，他就具有 root 的权限。根用户在 NFS 客户端上拥有和服务器上相同的权限。
  #使NFS配置生效
  exportfs -arv
  service nfs-kernel-server restart
  systemctl enable nfs-kernel-server && systemctl status nfs-kernel-server
  ~~~

  > Ubuntu中配置NFS教程参考：[Ubuntu最新版本(Ubuntu22.04LTS)安装nfs服务器及使用教程_ubuntu22.04 nfs-CSDN博客](https://blog.csdn.net/wkd_007/article/details/129092820)
  >
  > - no_root_squash的含义：
  >
  >   - 默认情况下，NFS使用`root_squash`选项，这意味着来自客户端的root用户的请求将被NFS服务器视为来自匿名（或“nobody”）用户。这是一种安全措施，以防止远程root用户在NFS共享上拥有完全的root权限。
  >
  >   - 然而，如果你设置了`no_root_squash`选项，那么远程root用户的请求将被视为本地root用户。这意味着远程root用户将在NFS共享上拥有完全的root权限，就像在本地系统上一样。

- Configure Sticky bit on this folder

  ~~~sh
  chmod +t /mnt/datadisk1
  ls -ld /mnt/datadisk1
  ~~~

  > 特殊标志位分为三种：
  >
  > - sticky
  >   - 只有文件的所有者、目录的所有者或root用户才能删除或重命名该目录中的文件。某个普通用户不能删除/改名/移动所有者不是自己的文件。
  >   - drwxrwxrwt；置于o的x位置 1777
  > - SUID
  >   - **只对有x权限的文件有效。**如果一个程序的所有者是root并且具有SUID属性；那么普通用户执行，如同是root在执行。
  >   - -rwsr-xr-x；置于u的x位置，s表示SUID位被设置。也可以用 4755 表示
  > - SGID
  >   - 一般应用在目录上，目录设置sgid，任何用户在其中创建的文件的属组都会继承该目录的属组，而不是用户的属组。
  >   - drwxrwsr-x; 置于g的x位置，s表示SGID位被设置，也可以用 2775 表示

## Network Admin

- Add a new interface and assign IP, gateway, DNS servers.

  ~~~yaml
  vim /etc/netplan/01-netcfg.yaml
  
  network:
    version: 2
    renderer: networkd
    ethernets:
      enp0s3:
        dhcp4: no
        addresses: [192.168.1.100/24]
        gateway4: 192.168.1.1
        nameservers:
          addresses: [8.8.8.8,8.8.4.4]
          
  netplan apply
  
  #也可以用nmcli来改
  nmcli con show --active #查看当前的网络连接，其中的name就是网络连接名
  sudo nmcli con mod <网络连接名> ipv4.addresses "192.168.1.100/24"
  sudo nmcli con mod <网络连接名> ipv4.gateway "192.168.1.1"
  sudo nmcli con mod <网络连接名> ipv4.method manual #手动指定IP，而非dhcp获取IP
  #重启网络以应用更改
  sudo nmcli con down <网络连接名> && sudo nmcli con up <网络连接名>
  ~~~

- Test Connectivity

  ~~~sh
  nc -vz <NIC IP>
  ~~~

- Nslookup, A record CNAME

  ~~~sh
  
  ~~~

  > **A记录**：A记录是将域名映射到对应的IPv4地址。例如，如果你有一个服务器的IP地址是`192.0.2.1`，并且你希望`www.example.com`指向这个IP地址，你可以设置一个A记录，将`www.example.com`映射到`192.0.2.1`。
  >
  > **CNAME**：CNAME记录（Canonical Name record）是将一个域名映射到另一个域名。它允许你将多个域名解析到同一个IP地址。例如，你可能有一个主域名`www.example.com`，并且你希望`blog.example.com`和`store.example.com`都指向同一个地方。在这种情况下，你可以为`blog`和`store`设置CNAME记录，将它们都映射到`www.example.com`。

- Configure nameserver to google DNS

  ~~~sh
  vim /etc/resolv.conf #修改nameserver
  
  #也可以用nmcli修改
  nmcli con show --active #查看当前的网络连接，其中的name就是网络连接名
  nmcli con mod <网络连接名> ipv4.dns "8.8.8.8" #google dns是8.8.8.8,8.8.4.4
  sudo nmcli con down <网络连接名> && sudo nmcli con up <网络连接名>
  
  #查看dns
  systemd-resolve --status #显示系统的DNS解析器状态，包括每个网络接口的DNS服务器。你可以在"DNS Servers"或"DNSSEC NTA"部分找到当前使用的DNS服务器地址。
  ~~~

- Check all open/listen port on local server

  ~~~sh
  ss -tulnp
  ~~~

# Ubuntu安全补丁

参考文档：https://zhuanlan.zhihu.com/p/74768044#%E6%96%B9%E6%B3%95%E4%B8%80%EF%BC%9A%E5%A6%82%E4%BD%95%E6%A3%80%E6%9F%A5%20Debian/Ubuntu%20%E4%B8%AD%E6%98%AF%E5%90%A6%E6%9C%89%E4%BB%BB%E4%BD%95%E5%8F%AF%E7%94%A8%E7%9A%84%E5%AE%89%E5%85%A8%E6%9B%B4%E6%96%B0%EF%BC%9F

## 使用unattended-upgrade查看和安装

~~~sh
sudo unattended-upgrade --dry-run -v #这个命令会列出所有可以被unattended-upgrade安装的安全更新。--dry-run选项意味着命令只会列出更新，而不会实际安装它们。-v选项会让命令输出verbose信息（info级别）。
sudo unattended-upgrade -d # 运行下面的命令来安装，-d输出debug信息
sudo unattended-upgrade # 直接安装
~~~

> - 在Ubuntu系统中，`unattended-upgrades`的配置文件有两个：
>
>   - vim `/etc/apt/apt.conf.d/50unattended-upgrades`
>
>     在这个文件中，你可以指定哪些类型的更新应该被自动安装。
>
>     ~~~sh
>     sudo vim /etc/apt/apt.conf.d/50unattended-upgrades
>     ~~~
>
>   - `/etc/apt/apt.conf.d/20auto-upgrades`
>     
>     ~~~sh
>     sudo vim /etc/apt/apt.conf.d/20auto-upgrades
>     ~~~
>     
>     - APT::Periodic::Update-Package-Lists "1"。表示每天都会更新包列表
>     - APT::Periodic::Unattended-Upgrade "1"。表示每天都会运行`unattended-upgrades
>     - （1=启用，0=禁止）
>
> - 默认情况下，`unattended-upgrades`只会安装安全更新。这是通过以下配置实现的：
>
>   ```json
>   Unattended-Upgrade::Allowed-Origins {
>       "${distro_id}:${distro_codename}-security";
>       // Extended Security Maintenance; doesn't necessarily exist for
>       // every release and this system may not have it installed, but if
>       // available, the policy for updates is such that unattended-upgrades
>       // should also install from here by default.
>       "${distro_id}ESMApps:${distro_codename}-apps-security";
>       "${distro_id}ESM:${distro_codename}-infra-security";
>   };
>   ```
>
>   - `"${distro_id}ESMApps:${distro_codename}-apps-security"`：这个配置代表Ubuntu的ESM（Extended Security Maintenance）应用程序的安全更新。ESM是Ubuntu为其LTS（Long Term Support）版本提供的一项服务，它可以在LTS版本的标准支持期结束后继续提供安全更新。
>   - `"${distro_id}ESM:${distro_codename}-infra-security"`：这个配置代表Ubuntu的ESM基础设施的安全更新。这包括操作系统的核心组件，如内核和系统库。
>   - 在这个配置中，只有`-security`源的更新会被自动安装，其他源的更新（`-updates`，`-proposed`，`-backports`）被注释掉了。
>
> - 修改完配置后，需要重启服务
>
>   ~~~sh
>   sudo systemctl restart unattended-upgrades
>   ~~~

## 使用unattended-upgrade每周定期自动更新

- `unattended-upgrades`包可以用于自动安装安全更新。你可以通过编辑`/etc/apt/apt.conf.d/50unattended-upgrades`文件来配置它。但是，`unattended-upgrades`默认并不提供按照星期几来设定更新的选项，它只能设定为每天运行。

- 如果你想要在每周六安装更新，你可以使用cron来设定一个定时任务。以下是具体步骤：

  1. 打开终端。

  2. 输入以下命令来编辑root用户的cron表：

      ```bash
      sudo crontab -e
      ```

  3. 在打开的编辑器中，添加以下行：

      ```bash
      0 2 * * 6 unattended-upgrade
      ```

      这个命令的意思是在每周六的凌晨2点运行`unattended-upgrade`命令。

      ~~~sh
      sudo systemctl restart cron.service && sudo systemctl status cron.service
      ~~~

  4. 另外需要disable掉unattended-upgrade的自动安装功能

      ~~~sh
      sudo vim /etc/apt/apt.conf.d/20auto-upgrades
      APT::Periodic::Update-Package-Lists "1";
      APT::Periodic::Unattended-Upgrade "0";
      
      sudo systemctl restart unattended-upgrades && sudo systemctl status unattended-upgrades
      ~~~


## 使用apt查看和安装

~~~sh
sudo apt list --upgradable | grep -e "-security"
sudo apt list --upgradable | grep -e "-security" | awk -F "/" '{print $1}' | xargs apt install
#focal-security是一个特殊的软件源，它包含了针对Ubuntu 20.04 LTS（代号为Focal Fossa）的所有安全更新。
# apt install -s是dry-run
#查看changelog，有更新时间
apt changelog packagename
~~~

## VM unattended-upgrade逻辑

~~~sh
sudo crontab -e
~~~

~~~sh
# automitically updating and installing secutiry patches on VM using unattended-upgrade. (Note that the apt update runs everyday, which is defined in `/etc/apt/apt.conf.d/20auto-upgrades`.

# Frequency of installing the security updates: [23:59] on [last Saturday of the month] every [3 months].

# Logic: If the month number of [today plus 7 days] is not equal to the month number of today, this means this week is the last week of this month. So, this Saturday is the last Saturady of the current month.
59 23 * 3,6,9,12 6 [ "$(date +\%m -d +7days)" != "$(date +\%m)" ] && unattended-upgrade
~~~

~~~sh
sudo systemctl restart cron.service && sudo systemctl status cron.service
~~~



