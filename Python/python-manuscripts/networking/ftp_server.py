import socket


def send_file(conn,filename):
    with open(filename,'rb') as f:
        # 分块读取文件,防止内存占用过高
        # := 海象运算符，将右边的值赋值给左边，同时返回赋值结果。即while判断的是赋值结果（右边的值）
        while(chunk := f.read(1024)):
            conn.send(chunk)
        print("File transfer finished.")

try:
    # 创建套接字
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 绑定IP和端口号
    server.bind(('192.168.71.66',8080))
    # 开始监听
    server.listen(1)
    print("FTP server started, waiting for client connection.")
    # 接受客户端连接
    conn,addr = server.accept()
    print(f"Client {addr} has connected.")
    # 调用发送文件的函数分块传输文件
    send_file(conn, 'requests_module.py')

except Exception as e:
    print(f"Server Error: {str(e)}")

finally:
    conn.close()
    server.close()
    print(f"Connetion to {addr} has closed.")