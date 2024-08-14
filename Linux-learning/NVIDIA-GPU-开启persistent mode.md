- 以下为利用GPU驱动自带工具配置GPU驱动内存常驻模式开机自启动，该脚本需要系统下预安装sed、useradd、userdel、id命令，否则会执行失败。

~~~sh
cd /usr/share/doc/NVIDIA_GLX-1.0/samples/
ls
#nvidia-persistenced-init.tar.bz2  systemd
tar xvf nvidia-persistenced-init.tar.bz2 
ls
#nvidia-persistenced-init  nvidia-persistenced-init.tar.bz2  systemd
cd nvidia-persistenced-init/
./install.sh 
######
Checking for common requirements...
  sed found in PATH?  Yes
  useradd found in PATH?  Yes
  userdel found in PATH?  Yes
  id found in PATH?  Yes
Common installation/uninstallation supported

Creating sample System V script... done.
Creating sample systemd service file... done.
Creating sample Upstart service file... done.

Checking for systemd requirements...
  /usr/lib/systemd/system directory exists?  Yes
  systemctl found in PATH?  Yes
systemd installation/uninstallation supported

Installation parameters:
  User  : nvidia-persistenced
  Group : nvidia-persistenced
  systemd service installation path : /usr/lib/systemd/system

Adding user 'nvidia-persistenced' to group 'nvidia-persistenced'... done.
Installing sample systemd service nvidia-persistenced.service... done.
Enabling nvidia-persistenced.service... done.
Starting nvidia-persistenced.service... done.

systemd service successfully installed.
######
#以上表示脚本配置成功
~~~

~~~sh
#通过以下命令检查服务状态是否正常，并执行nvidia-smi确认Persistence-M状态为on
systemctl status nvidia-persistenced.service
#配置完成后重启OS验证systemctl status nvidia-persistenced.service是否正常启动
~~~

