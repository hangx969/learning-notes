from fabric import Connection

# 连接到远程主机
with Connection(host='172.16.183.81', user='root', connect_kwargs={'password': 'root'}) as conn:
    conn.cd('/root/')
    result = conn.run('ls', hide=True)
    print(result.stdout)