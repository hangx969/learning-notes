from fabric import Connection

conn = Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'})
# 连接到远程主机，并指定工作目录，后面的操作都在这个目录中进行
with conn.cd('/root/'):
    result = conn.run('ls', hide=True)
    print(result.stdout)
conn.close()