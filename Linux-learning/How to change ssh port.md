# How to change ssh port on Azure

NOTE：CentOS 8 is used

### 1.Log in using PuTTY

### 2. Log into root user

```shell
sudo su
```

### 3. Modify the parameter within sshd_config

```shell
vi /etc/ssh/sshd_config
```

the default SSH port appears like this:

```shell
#Port 22
```

To change the SSH port to 2222, you will need to make the line appear like this:

```shell
Port 2222
```

### 3. Update Iptables and firewall

Firewalld.service is not activated on the newly created VM, so you need to start it firstly.

```shell
systemctl enable firewalld
systemctl start firewalld
```

Check the firewall service:

```shell
systemctl status firewalld
```

To allow the port in the firewall:

```shell
sudo firewall-cmd --permanent --zone=public --add-port=52019/tcp
sudo firewall-cmd --reload
```

You should see a ‘Success’ message after each of these commands.

To update iptables, please enter the following:

```shell
iptables -A INPUT -m state --state NEW -m tcp -p tcp --dport 2222 -j ACCEPT
```

you can double check that the firewall rule was added using:

```shell
sudo iptables-save | grep '2222'
```

And you should see:

```shell
-A IN_public_allow -p tcp -m tcp --dport 52019 -m conntrack --ctstate NEW -j ACCEPT
```

### 4. Modify the selinux configuration

Enforcing in selinux may lead to the failure of binding to the 2222 port, which will lead to the unsuccessfully restart of sshd.service. Enter:

```shell
getenforce 
```

you may see:

```shell
enforcing
```

So close the selinux as following:

```shell
vi /etc/selinux/config
SELINUX=permissive
```

### 5. Restart sshd.service

```shell
systemctl restart sshd.service
```

### 6. Add inbound port rule on Azure Portal

Settings - Add inbound rule

<img src="C:\Users\v-hangx.FAREAST\AppData\Roaming\Typora\typora-user-images\image-20220113162527481.png" alt="image-20220113162527481" style="zoom: 67%;" />

### 7. Restart PuTTY using new port

```shell
exit
```

Log in with new port.

### 8. Delete the old security rule with 22 port

References:

[Changing the SSH port for a RHEL Azure VM - Paul S. Randal (sqlskills.com)](https://www.sqlskills.com/blogs/paul/changing-the-ssh-port-for-a-rhel-azure-vm/)

[How to Change the SSH Port on Dedicated and VPS | HostGator Support](https://www.hostgator.com/help/article/how-to-change-the-ssh-port-on-dedicated-and-vps)

[SELinux入门 | 《Linux就该这么学》 (linuxprobe.com)](https://www.linuxprobe.com/selinux-introduction.html)

[SSHD服务启动失败 – 笛声 (hqidi.com)](https://hqidi.com/133.html)