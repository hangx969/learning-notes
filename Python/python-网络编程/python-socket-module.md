# 介绍

socket 模块是 Python 标准库，专门用于网络通信的套接字编程。套接字是进行网络通信的端点，通过它可以在网络中发送和接收数据。它在实现网络应用程序时起到关键作用，支持多种网络协议，包括传输控制协议（TCP）和用户数据报协议（UDP）。

套接字的基本概念:

- 套接字（Socket）：在客户端和服务器之间进行通信的端点。每个套接字都有一个唯一的 IP 地址和端口号组合，标识网络中的特定服务。

- IP 地址：用于标识网络中的设备。可以是 IPv4 或 IPv6 格式。
- 端口号：用于标识特定的应用程序或服务。常用的端口号如 80（HTTP）和 443（HTTPS）

客户端-服务器模型

- 服务器（Server）：

  - 服务器是一个长期运行的程序，它在特定的**IP地址和端口**上监听来自客户端的请求。

  - 服务器接收到请求后，可以处理该请求并返回相应的数据

  - 使用 `socket.socket()` 创建一个套接字并调用 `bind()` 方法绑定到指定的地址和端口，接着使用 `listen()` 方法开始监听。

- 客户端（Client）：

  - 客户端是发起请求的程序，它连接到服务器以请求服务或数据。

  - 客户端使用 `socket.socket()` 创建一个套接字，并使用 `connect()` 方法连接到服务器的 IP 地址和端口。

  - 连接成功后，客户端可以发送请求并接收服务器的响应。

# Server端实现

## 创建套接字socket.socket()

功能： 创建一个新的套接字对象，用于建立服务器端的网络连接。

语法：

`socket.socket([family[, type[, proto]]])`

参数：

- family：地址簇，决定套接字所使用的网络协议。常见的值有：

  - socket.AF_INET：IPv4 地址族。

  - socket.AF_INET6：IPv6 地址族。

- type：套接字类型，决定套接字的通信方式。常见的值有：

  - socket.SOCK_STREAM：TCP 套接字，提供可靠的、面向连接的服务。

  - socket.SOCK_DGRAM：UDP 套接字，提供无连接的服务。

- proto：协议号，通常为 0，表示使用默认协议。

返回值 ：返回一个套接字对象。

示例：

~~~python
import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
~~~

## 绑定到IP端口socket.bind()

功能：将套接字绑定到特定的地址和端口，以便接收数据。

语法：`socket.bind(address)`

参数:

- address：一个二元组 (host, port)，表示要绑定的地址和端口。例如 ('localhost', 8080)。

返回值：无返回值

示例：

~~~python
import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将套接字绑定到特定地址和端口，以便接收数据
sock.bind(('localhost',8080)) # 注意参数必须是一个元组，括号括起来
~~~

## 开始监听socket.listen()

功能：使套接字进入监听状态，准备接受客户端的连接请求。

语法:`socket.listen([backlog])`

参数:

- backlog：表示可以挂起的连接请求的最大数量。通常设置为 5 或更高。

返回值: 无返回值

示例：

~~~python
import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将套接字绑定到特定地址和端口，以便接收数据
sock.bind(('localhost',8080))
# 开始监听
sock.listen(5)
~~~

## 接受连接请求socket.accept()

功能：接受一个客户端连接请求，返回新的套接字对象和客户端地址。

语法: `socket.accept`()

返回值: 返回一个二元组 (conn, addr)：

- conn：新的套接字对象，用于与客户端进行通信。
- addr：客户端的地址信息，通常是 (IP 地址, 端口号)

示例：

~~~python
import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将套接字绑定到特定地址和端口，以便接收数据
sock.bind(('localhost',8080))
# 开始监听
sock.listen(5)
# 接受客户端请求,返回新的套接字对象和客户端地址
conn, addr = socket.accept()
print(f"Connection comes from: {addr}")
~~~

## 发送数据socket.send()

功能：向套接字发送数据。

语法：`socket.send`(bytes)

参数：

- bytes：要发送的数据，必须是字节对象。

返回值：返回实际发送的字节数。

示例：

~~~python
import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将套接字绑定到特定地址和端口，以便接收数据
sock.bind(('localhost',8080))
# 开始监听
sock.listen(5)
# 接受客户端请求,返回新的套接字对象和客户端地址
conn, addr = socket.accept()
print(f"Connection comes from: {addr}")
# 向套接字发送数据(必须是字节对象)
conn.send(b'python')
~~~

## 接收数据socket.recv()

功能：从套接字接收数据。

语法:`socket.recv`(bufsize)

参数:

- bufsize：接收数据的最大字节数。

返回值: 返回接收到的数据，类型为字节对象。

示例：

~~~python
import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将套接字绑定到特定地址和端口，以便接收数据
sock.bind(('localhost',8080))
# 开始监听
sock.listen(5)
# 接受客户端请求,返回新的套接字对象和客户端地址。
conn, addr = socket.accept() # conn是新的套接字对象，用于与客户端进行通信。
print(f"Connection comes from: {addr}")
# 向套接字发送数据(必须是字节对象)
conn.send(b'python')
# 从套接字接受数据，注意这里用的是conn.recv，从这个特定的套接字对象获取数据
data = conn.recv(1024)
print(f"Data received: {data.decode()}") # 把字节对象decode
~~~

## 关闭套接字socket.close()

功能：关闭套接字，释放相关资源。

语法：`socket.close`()

返回值：无返回值。

示例：

~~~python
import socket
# 创建TCP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 将套接字绑定到特定地址和端口，以便接收数据
sock.bind((('localhost',8080)))
# 开始监听
sock.listen(5)
# 接受客户端请求,返回新的套接字对象和客户端地址
conn, addr = socket.accept()
print(f"Connection comes from: {addr}")
# 向套接字发送数据(必须是字节对象)
conn.send(b'python')
# 从套接字接受数据
data = conn.recv(1024)
print(f"Data received: {data.decode()}")
# 关闭连接和套接字
conn.close()
sock.close()
~~~

# Client端的实现

## 创建套接字socket.socket()

与server端相同

## 连接到服务端socket.connect()

功能： 连接到指定的服务端地址。

语法：

`socket.connect(ADDRESS)`

参数：

- address: 一个二元组（host, port），表示服务端的地址和端口，例如：(‘localhost’,8080)

返回值 ：无返回值

## 发送数据socket.send()

与server端相同

## 接受数据socket.recv()

与server端相同

## 客户端代码

~~~python
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
~~~

1. 服务端
   - 等待客户端连接。连接成功后，服务端向客户端发送“python”。然后等待从客户端接收数据。
   - 当接收到客户端发送的数据“Hello from client”时，客户端接收并打印。
2. 客户端
   - 服务端向客户端发送“python”，客户端接收到并打印。
   - 客户端向服务端发送“Hello from client”，服务端接收并打印。

这样双方完成一次双向数据传输。

# 案例：简易聊天服务器

构建一个简单的聊天服务器，允许多个客户端连接并交换信息。

## 服务端

~~~python
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
	
    # 开始接收客户端消息
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
~~~

## 客户端

~~~python
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
~~~

# 案例：创建FTP服务器

创建一个 TCP 服务器，服务器端负责传输文件，而客户端连接到服务器并接收文件。

## 服务端

创建套接字并发送文件

~~~python
import socket


def send_file(conn,filename):
    # 要用rb模式，二进制打开文件，可以直接用conn.send发数据
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
~~~

> `:=` 运算符，也称为“海象运算符”（Walrus Operator），是 Python 3.8 引入的一种语法，用于在表达式中进行赋值操作。它允许在一个表达式中同时完成变量赋值和使用赋值结果，从而提高代码的简洁性和可读性。
>
> 1. **赋值与返回值结合**:
>    
>    - `:=` 运算符将右侧的值赋给左侧的变量，同时返回赋值的结果。
>    - 这使得可以在表达式中直接使用赋值后的值，而无需单独写一行赋值代码。
>    
> 2. **简化代码**:
>    
>    - 在循环、条件判断等场景中，`:=` 运算符可以减少代码冗余。例如：
>      ```python
>      # 使用 := 运算符
>      while (chunk := f.read(1024)):
>          process(chunk)
>      ```
>      等价于：
>      ```python
>      # 不使用 := 运算符
>      chunk = f.read(1024)
>      while chunk:
>          process(chunk)
>          chunk = f.read(1024)
>      ```
>    
> 3. **适用场景**:
>    - **循环**: 在循环中动态更新变量值。
>    - **条件判断**: 在 `if` 或 `while` 中直接使用赋值结果。
>    - **列表推导**: 在列表推导中保存中间结果以避免重复计算。
>
> ### 示例：
>
> #### 在循环中使用：
> ```python
> while (data := socket.recv(1024)):
>     print(data)
> ```
> - `data := socket.recv(1024)` 将接收到的数据赋值给 `data`，同时返回数据以供 `while` 判断是否继续循环。
>
> #### 在条件判断中使用：
> ```python
> if (result := expensive_function()) > 0:
>     print(f"Result is {result}")
> ```
> - `result := expensive_function()` 调用函数并将结果赋值给 `result`，同时返回结果以供 `if` 判断。
>

## 客户端

连接到服务端并接收文件

~~~python
import socket


def recv_file(conn, filename):
    # 要用wb模式写文件，因为recv就是接收的二进制
    # 不写b就会报错：Client Error: write() argument must be str, not bytes
    with open(filename, 'wb') as f:
        while True:
            # 分块接收数据
            data = conn.recv(1024)
            # 接收到空数据说明发完了
            if not data:
                break
            f.write(data)
        print("File received.")

try:
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(('192.168.71.66',8080))
    recv_file(client, 'requests_module.py')
except Exception as e:
    print(f"Client Error: {str(e)}")
finally:
    client.close()
~~~

# 案例：创建简单HTTP服务器

实现一个简单的HTTP服务器，可以接收客户端的请求并返回静态网页内容

~~~python
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
# 客户端连接后，调用函数来接收并处理请求（返回一个静态页面）
handler_request(conn)
server.close()
~~~

