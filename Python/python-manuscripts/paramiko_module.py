import paramiko, os

# 创建ssh客户端
ssh = paramiko.SSHClient()
# 设置自动接受host key
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

# 准备本地文件路径
local_dir = '/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/'
local_file = 'oop.py'
local_path = os.path.join(local_dir,local_file)

# 连接到的远程服务器
hostname = '172.16.183.81'
port = 22
username = 'root'
password = 'root'
# 远程路径必须要具体到文件名才能成功sftp put。
remote_path = '/root/oop.py'

try:
    # 创建本地目录，检查本地文件
    os.makedirs(local_dir, exist_ok=True)
    if not os.path.exists(local_path):
        with open(local_path, 'w') as f:
            f.write("test")
        print(f"File {local_path} has been created.")

    # 创建ssh客户端
    ssh.connect(hostname, port, username, password)
    print(f"Connected to {hostname}.")
    # 创建sftp客户端
    sftp = ssh.open_sftp()
    # sftp上传文件
    sftp.put(local_path, remote_path)
    print(f"File transferred from {local_path} to {remote_path}.")

    # sftp下载文件
    # sftp.get(remote_path, local_path)

except Exception as e:
    print(f"Error occurred: {e}")

finally:
    sftp.close()
    ssh.close()
    print("Connection has closed.")