# tkinter介绍

tkinter 是 Python 的标准 GUI（图形用户界面）库，它提供了创建窗口、按钮、文本框、菜单等 GUI 组件的功能。tkinter 是一个跨平台的工具，可以在 Windows、macOS 和 Linux 等操作系统上运行，使得开发者可以方便地创建桌面应用程序。主要特点：

1. 易于使用：tkinter 提供了简单的 API，适合初学者和希望快速开发 GUI 应用程序的
开发者。
2. 跨平台：应用程序可以在不同操作系统上运行，提供一致的用户体验。
3. 丰富的组件：支持多种 GUI 组件，如按钮、标签、文本框、菜单、框架、画布等，能够满足大多数桌面应用的需求。
4. 支持事件驱动编程：可以轻松处理用户输入和事件，例如鼠标点击、键盘输入等。

5. 可扩展性：虽然 tkinter 是一个轻量级的库，但它也允许开发者通过其他 Python 库进行扩展。

基本组件

- 窗口（Tk）：应用程序的主窗口。
- 标签（Label）：用于显示文本或图像。
- 按钮（Button）：可点击的按钮。
- 文本框（Entry 和 Text）：用于单行或多行文本输入。
- 框架（Frame）：用于组织和布局其他组件。
- 菜单（Menu）：用于创建应用程序的菜单栏。

## pyinstaller

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

# 案例：自动管理nginx图形界面

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

# 案例：自动管理Tomcat图形界面
