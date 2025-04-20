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



