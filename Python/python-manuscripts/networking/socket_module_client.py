import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 连接到特定地址和端口
sock.connect(('localhost',8080))
# 向服务端发送数据(必须是字节对象)
sock.send(b'Hello from client')
# 从套接字接受数据
data = sock.recv(1024)
print(f"Data received from server: {data.decode()}")
# 关闭连接和套接字
sock.close()