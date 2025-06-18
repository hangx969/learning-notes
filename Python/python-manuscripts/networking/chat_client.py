import socket

def start_client():
    # 创建套接字
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        # 连接到服务端
        client.connect(('localhost',8080))
        # 输入消息部分用无限循环，输入exit才推出
        while True:
            msg = input("Please input message, input 'exit' to exit.\n")
            if msg.lower() == 'exit':
                break
            # 发送套接字，用utf-8编码为字节数据
            client.send(msg.encode('utf-8'))
            # 发送完同时接收server端消息
            response = client.recv(1024)
            # server端消息要decode出来
            print(f'Server response: {response.decode("utf-8")}')
    except Exception as e:
        print(f"Client Error: {str(e)}")
    finally:
        client.close()

if __name__ == '__main__':
    start_client()