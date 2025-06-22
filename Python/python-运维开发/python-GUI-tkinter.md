# tkinter

## 介绍

tkinter 是 Python 的标准 GUI（图形用户界面）库，它提供了创建窗口、按钮、文本框、菜单等 GUI 组件的功能。tkinter 是一个跨平台的工具，可以在 Windows、macOS 和 Linux 等操作系统上运行，使得开发者可以方便地创建桌面应用程序。主要特点：

1. 易于使用：tkinter 提供了简单的 API，适合初学者和希望快速开发 GUI 应用程序的
开发者。
2. 跨平台：应用程序可以在不同操作系统上运行，提供一致的用户体验。
3. 丰富的组件：支持多种 GUI 组件，如按钮、标签、文本框、菜单、框架、画布等，能够满足大多数桌面应用的需求。
4. 支持事件驱动编程：可以轻松处理用户输入和事件，例如鼠标点击、键盘输入等。

5. 可扩展性：虽然 tkinter 是一个轻量级的库，但它也允许开发者通过其他 Python 库进行扩展。

## 基本组件

- 窗口（Tk）：应用程序的主窗口。
- 标签（Label）：用于显示文本或图像。
- 按钮（Button）：可点击的按钮。
- 文本框（Entry 和 Text）：用于单行或多行文本输入。
- 框架（Frame）：用于组织和布局其他组件。
- 菜单（Menu）：用于创建应用程序的菜单栏。

## pyinstaller打包

首先需要安装 pyinstaller，可以通过以下命令安装：

```sh
pip3 install pyinstaller
```

pyinstaller：可以把 python 代码打包成 windows 的 exe 程序。

```sh
# 进入你的脚本目录，然后运行以下命令打包为可执行文件：
pyinstaller --onefile --windowed .\nginx-gui.py
```

- --onefile: 将所有依赖打包成一个单独的文件。
- --windowed: 不显示命令行窗口（适用于 GUI 程序）。

# 案例：GUI界面自动管理nginx

基于 Python 开发的 Windows GUI 应用程序，用于远程管理 Nginx 服务。它利用 paramiko 库通过 SSH 连接到远程安装 nginx 的服务器，实现对 Nginx 服务的状态监控和基本操作，如启动、停止、重启 Nginx 服务以及查看 Nginx 错误日志。用户可以通过简洁的图形界面操作Nginx 服务，方便地维护和监控远程服务器上的服务状态。

~~~python
import tkinter as tk
from tkinter import messagebox
import paramiko

HOST = '172.16.183.80'
USERNAME = 'root'
PASSWD = '111111'

# ssh执行命令
def run_system_command(command):
    ssh = paramiko.SSHClient()
    # 自动接受远程主机host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWD)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return output.strip(), error.strip()
    except Exception as e:
        return "", str(e)
    finally:
        ssh.close()

# 获取nginx服务状态
def get_nginx_status():
    output, error = run_system_command('systemctl is-active nginx')
    if error:
        return "Status unknown"
    return output.strip()

# 自动更新nginx状态的标签
def update_status_label():
    status = get_nginx_status()
    # 动态更新状态标签的文本。status_label是一个全局变量，所以可以直接在函数里使用
    status_label.config(text=f"Nginx Status: {status}")
    # tkinter定时器函数，每5秒再次调用函数
    root.after(5000, update_status_label)

# 启动nginx服务
def start_nginx():
    output, error = run_system_command("systemctl start nginx")
    if error:
        # 定义弹窗
        messagebox.showerror("Error", f"Failed to start nginx: {error}")
    else:
        messagebox.showinfo("Success", f"Nginx has been started")
    update_status_label()

# 停止nginx服务
def stop_nginx():
    output, error = run_system_command("systemctl stop nginx")
    if error:
        messagebox.showerror("Error", f"Failed to stop nginx: {error}")
    else:
        messagebox.showinfo("Success", f"Nginx has been stopped")
    update_status_label()

# 重启nginx
def restart_nginx():
    output, error = run_system_command("systemctl restart nginx")
    if error:
        messagebox.showerror("Error", f"Failed to restart nginx: {error}")
    else:
        messagebox.showinfo("Success", f"Nginx has been restarted")
    update_status_label()

# 查看nginx日志
def view_nginx_logs():
    output, error = run_system_command("tail -n 100 /var/log/nginx/access.log")
    if error:
        messagebox.showerror("Error", f"Failed to get nginx log: {error}")
    else:
        # 创建文本框子窗口，把日志放进去
        logs_window = tk.Toplevel(root)
        logs_window.title("Nginx Log")
        # 在这个窗口中创建一个文本框 (Text)，wrap='word' 意味着在文本过长时会自动换行。
        logs_text = tk.Text(logs_window, wrap='word')
        # 将 Nginx 日志（即 output）插入到文本框中，tk.END 表示将内容插入到文本框的末尾。
        logs_text.insert(tk.END, output)
        # 将文本框布局到窗口中，fill='both' 表示文本框会填满窗口的水平和垂直方向，expand=True 文本框会随着窗口的大小变化而扩展。
        logs_text.pack(fill='both', expand=True)


if __name__ == '__main__':
    # 创建一个顶层窗口对象 root，这是整个图形界面的主窗口。
    root = tk.Tk()
    root.title("Nginx manager")

    # 显示nginx状态的标签
    status_label = tk.Label(root, text="Nginx Status: Checking...", font=('Arial', 12))
    # pack() 是用来布局组件的方法之一，它把标签添加到窗口中并设置布局
    # padx=10, pady=10: 这是为标签设置的内边距，padx 是水平方向的间距，pady 是垂直方向的间距，值为 10，表示标签与窗口边缘或其他组件之间有 10 个像素的间距。
    status_label.pack(padx=10, pady=10)

    # 创建启动按钮
    start_button = tk.Button(root, text="Start Nginx", command=start_nginx)
    start_button.pack(padx=10,pady=10)

    #创建停止按钮
    stop_button = tk.Button(root, text="Stop Nginx", command=stop_nginx)
    stop_button.pack(padx=10,pady=10)

    #创建重启按钮
    restart_button = tk.Button(root, text="Restart Nginx", command=restart_nginx)
    restart_button.pack(padx=10,pady=10)

    # 查看日志按钮
    nginx_log_button = tk.Button(root, text="Get Nginx Log", command=view_nginx_logs)
    nginx_log_button.pack(padx=10,pady=10)

    update_status_label()

    # 启动 tkinter 的主事件循环，使应用程序保持运行并响应用户输入。
    root.mainloop()
~~~

# 案例：GUI界面自动管理Tomcat

**项目描述：**

Tomcat 管理助手是一款基于图形用户界面的轻量化管理工具，旨在帮助用户通过简单的操作界面，控制 Tomcat 服务的启动、停止、重启等基本操作。同时，该工具还集成了日志监控功能，实时跟踪 Tomcat 的运行状态，以便用户快速掌握服务情况。工具主要通过与系统命令的交互，实现对Tomcat 进程的管理，并支持通过图形界面展示日志内容，帮助运维人员高效管理和诊断 Tomcat 服务。

**项目功能：**

1、启动 Tomcat: 一键启动 Tomcat 服务，并显示启动状态。

2、停止 Tomcat: 快速停止 Tomcat 服务，避免手动操作繁琐。

3、重启 Tomcat: 提供一键重启服务的功能，确保服务平稳重启。

4、查看服务状态: 实时监控 Tomcat 的运行状态，通过抓取进程信息来判断服务是否运行。

5、日志监控: 实时查看 Tomcat 的日志文件，方便用户掌握服务运行的详细情况。

~~~python
~~~

# 案例：GUI界面自动管理Mysql

通过 Tkinter 构建图形用户界面 (GUI)，结合 Paramiko 和 PyMySQL 实现对远程 MySQL 数据库的管理功能，包括： 

1. 通过 SSH 管理 MySQL 服务（启动、停止、查看状态）。 
2. 创建数据库。 
3. 创建数据表。 
4. 向表中插入数据。 
5. 在操作结果框中查看执行结果。

~~~python
~~~

# 案例：GUI界面自动管理httpd

## 介绍

httpd 服务是 Apache HTTP Server 的一个守护进程，用于运行在服务器上，它是世界上最流行的 Web 服务器软件之一，通常简称为 Apache。httpd（HTTP Daemon）是负责处理 HTTP 请求和响应的守护进程，主要用于部署和运行网站和 Web 应用程序。

你可以把它想象成一个“门卫”，它负责接收来自互联网的请求，查看请求的内容，然后将相应的网页或文件发回给请求的人。

当你在浏览器中输入一个网址（比如 www.example.com）时，你的电脑会发送一个请求到该网站的服务器。`httpd` 就是处理这个请求的程序。

它会找到你请求的网页内容，然后把它发送回你的浏览器，这样你就能看到你想要的网页。

## 基本功能

1. 处理 HTTP 请求：httpd 服务基于 HTTP 协议，处理客户端（如浏览器）发送的请求，并返回相应的内容（如 HTML 页面、图像、文件等）。
2. 跨平台支持：Apache HTTP Server 可以运行在各种操作系统上，包括 Linux、Windows、macOS 等，是一个跨平台的 Web 服务器。
3. 模块化设计：httpd 支持通过模块（modules）扩展功能，例如支持 mod_ssl 模块来实现 HTTPS 协议，或者通过 mod_rewrite 实现 URL 重写。
4. 虚拟主机支持：Apache 支持在同一台服务器上运行多个网站，通过虚拟主机（Virtual Hosts）功能，允许不同的域名或 IP 地址指向同一台服务器。
5. 高性能和稳定性：作为开源的 Web 服务器，Apache 以其稳定性和高性能著称，能够处理大量并发请求。
6. 可扩展性：用户可以根据需要加载或卸载特定功能的模块，灵活扩展 Apache 的能力。
7. 日志管理：Apache 提供了详细的访问日志和错误日志功能，方便管理员对服务器进行监控、调试和优化。

## 使用场景

1. 网站托管：httpd 是运行和托管静态网站或动态 Web 应用的核心服务之一。
2. Web 应用服务器：通过结合 PHP、Python 或 Perl 等动态编程语言，httpd 可以作为 Web 应用的服务器。
3. 反向代理服务器：使用 httpd 的代理模块，可以将其配置为反向代理服务器，转发请求到后端服务器。

## 安装和管理http服务

1. 安装：

```sh
yum install httpd -y
```

2. 启动httpd服务：

```sh
# 编辑 systemd 服务文件：
sudo vim /lib/systemd/system/httpd.service
# 修改 ExecStart 行，将 -D FOREGROUND 添加到命令中：
# 找到类似以下的行：
ExecStart=/usr/sbin/httpd $OPTIONS -k start
#修改为：
ExecStart=/usr/sbin/httpd -D FOREGROUND $OPTIONS
#保存并退出编辑器。
systemctl daemon-reload
systemctl start httpd
```

3. 设置开机自启动

```sh
systemctl enable httpd
```

## GUI管理工具

该项目是一个使用 Tkinter 创建的图形用户界面（GUI）工具，用于远程管理 HTTPD（Apache HTTP Server）服务。该工具利用 Paramiko 库实现 SSH 连接，允许用户通过简单的按钮操作来检查服务状态、启动或停止服务，以及查看服务日志。该工具适用于需要远程管理 Web 服务器的系统管理员或运维人员。

~~~python
~~~

# 案例：GUI管理k8s资源

通过python脚本开发一个GUI，并封装成windows程序，能够通过点击图标启动gui界面，可以实现：

1. 从k8s集群中选择需要操作的命名空间。

2. 选择资源类型（Deployment 和 StatefulSet）。

3. 选择资源名称。

4. 输入需要修改的副本数并提交。

~~~python
~~~

