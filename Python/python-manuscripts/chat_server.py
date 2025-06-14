import socket, threading

# 定义处理客户端请求的函数
def client_handler(conn, addr):
    print(f"Client {addr} has connected")
    try:
        while True:
            msg = conn.recv(1024)
            if not msg:
                print(f"Client {addr} has closed connection")
                break
            print(f"Message from {addr}: {msg.decode()}")
            conn.send(b"Message is sent")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        conn.close()
        print(f"Connection from {addr} has closed")


try:
    # 创建tcp套接字
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # 绑定IP和端口
    server.bind(('localhost',8080))
    # 开始监听连接，在服务器处理现有连接请求之前，最多可以排队等待的连接请求的数量是 5。
    # 如果此队列已满，新到的连接请求将被拒绝或导致客户端出现连接错误。
    server.listen(5)
    print(f"Chat server has started, waiting for client connection.")

    while True:
        # 使用accept()方法阻塞等待客户端连接。
        conn, addr = server.accept()
        # 为每个客户端创建一个线程，处理请求
        # 指定线程的目标函数为 handle_client，即当这个线程启动时，会执行 handle_client 函数。
        client_thread = threading.Thread(target=client_handler, args=(conn, addr))
        # 启动这个线程。
        # 此时，handle_client 函数将在新的线程中运行，服务端能继续接受新的客户端连接，而不被当前连接的处理所阻塞
        client_thread.start()

except Exception as e:
    print(f"Server error: {str(e)}")

finally:
    server.close()

