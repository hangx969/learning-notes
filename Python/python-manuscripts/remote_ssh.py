import paramiko, os

# 创建ssh客户端
ssh = paramiko.SSHClient()
# 设置自动接受host key
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
