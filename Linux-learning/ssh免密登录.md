# Vscode配置远程服务器免密连接

> 参考文档：[VSCode——SSH免密登录_vscode免密登录ssh_Irving.Gao的博客-CSDN博客](https://blog.csdn.net/qq_45779334/article/details/129308235)

1. 首先需要在vscode电脑上生成公钥私钥对：

   ```bash
   ssh-keygen
   ```

   从命令输出中查看到保存路径。

2. id_rsa.pub是公钥，需要将其中内容复制到远程主机上：

   ```bash
   vim ~/.ssh/authorized_keys #新建authorized_keys文件
   #将公钥值复制进去
   ```

3. 赋权限

   ```bash
   chmod 700 /home/userName # 我是root用户，就跳过了这一步
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

4. 修改ssh配置文件

   ```bash
   sudo vim /etc/ssh/sshd_config
   #PubkeyAuthentication yes注释去掉，才可以使用公钥验证
   ```

5. 重启sshd服务

   ```bash
   systemctl restart sshd.service 
   ```

6. 在vscode的ssh配置文件中加入远程主机信息

   ```bash
   Host 60.204.142.111
     HostName 60.204.142.111
     User root
     Port 23333
     IdentityFile C:\Users\hangx\.ssh\id_rsa
   ```

此时可以vscode免密远程登录到虚拟机。

