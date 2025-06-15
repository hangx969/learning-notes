import socket


def recv_file(conn, filename):
    with open(filename, 'wb') as f:
        while True:
            # 分块接收数据
            data = conn.recv(1024)
            # 接收到空数据说明发完了
            if not data:
                break
            f.write(data,encoding='utf-8')
        print("File received.")

try:
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(('192.168.71.66',8080))
    recv_file(client, 'requests_module.py')
except Exception as e:
    print(f"Client Error: {str(e)}")
finally:
    client.close()
