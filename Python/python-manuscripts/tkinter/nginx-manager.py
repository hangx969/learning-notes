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