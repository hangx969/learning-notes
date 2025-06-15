import socket

def handler_request(conn):
    # 接收客户端请求
    request = conn.recv(1024).decode()
    print(f"Request received: {request}")
    # 构造返回内容是一个静态网页
    response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Hello,World!</h1>"
    # 发送返回值
    conn.send(response)
    conn.close()

# 创建套接字
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('localhost',8080))
server.listen(1)
print("HTTP server has started, waiting for client connection.")

conn,addr = server.accept()
print(f"Client {addr} connected.")

handler_request(conn)
server.close()