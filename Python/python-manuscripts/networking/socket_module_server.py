import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将套接字绑定到特定地址和端口，以便接收数据
sock.bind(('localhost',8080))
# 开始监听
sock.listen(5)
# 接受客户端请求,返回新的套接字对象和客户端地址
conn, addr = sock.accept()
print(f"Connection comes from: {addr}")
# 向套接字发送数据(必须是字节对象)
conn.send(b'python')
# 从套接字接受数据
data = conn.recv(1024)
print(f"Data received: {data.decode()}")
# 关闭连接和套接字
conn.close()
sock.close()