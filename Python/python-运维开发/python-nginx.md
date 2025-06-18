# Nginx介绍

Nginx（发音为“Engine-X”）是一个开源的高性能 HTTP 和反向代理服务器，具有轻量级和高效的特点。它由 Igor Sysoev 于 2002 年首次发布，主要用于处理高负载的 HTTP 请求，并且能够作为反向代理、负载均衡器和 HTTP 缓存使用。

主要特点：

- 高性能：Nginx 设计用于处理大量并发连接，适合高流量网站。
- 高可用性：可以作为负载均衡器，将流量分配到多个服务器，提升系统的可用性。
- 反向代理：可以转发客户端请求到后端服务器，并将响应返回给客户端。
- 低资源消耗：内存和 CPU 占用较低，适合资源有限的环境。
- 灵活配置：支持模块化配置和多种扩展功能。

## 安装

### yum安装

在基于 Red Hat 的系统（如 CentOS、rockylinux、RHEL）上，可以使用 YUM 包管理工具安装 Nginx。以下是具体步骤：

~~~sh
# 1、安装 EPEL（Extra Packages for Enterprise Linux）仓库
# Nginx 在默认的 YUM 仓库中可能不可用，需要先安装 EPEL 仓库：
yum install epel-release -y
# 2、安装 Nginx
yum install nginx -y
# 3、启动 Nginx 服务
systemctl start nginx
systemctl enable nginx
# 6、检查 Nginx 服务状态
systemctl status nginx
# 7、配置防火墙
systemctl stop firewalld
systemctl disable firewalld
~~~

# 案例：检查Nginx配置文件语法

在对 Nginx 进行配置更改后，检查配置文件的语法是一个关键步骤。这可以通过 Python 脚本自动化完成：

~~~python
import subprocess

def check_nginx_config():
    try:
        subprocess.run(['nginx','-t'], capture_output=True, text=True, check=True)
        print("Nginx config is correct.")
    # subprocess.CalledProcessError 表示指定的命令运行失败了
    except subprocess.CalledProcessError as e: 
        print(e.stderr)

if __name__ == '__main__':
    check_nginx_config()
~~~

# 案例：自动重启nginx服务

检测 nginx 是否处于运行状态，如果 nginx 没运行需要执行脚本自动重启 nginx 服务。

~~~python
import subprocess

def check_nginx_alive() -> bool:
    try:
        result = subprocess.run(['systemctl','is-active', 'nginx'], capture_output=True, text=True, check=True)
        return result.stdout.strip() == 'active' # 是active就返回True，否则就返回False
    except subprocess.CalledProcessError as e: # 命令执行失败直接返回False
        return False

def restart_nginx() -> None:
    try:
        result = subprocess.run(['systemctl','restart', 'nginx'], capture_output=True, text=True, check=True)
        print("Nginx is restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart nginx: {e.stderr}.")

if __name__ == '__main__':
    if not check_nginx_alive():
        print(f"Nginx is not running, restarting nginx.")
        restart_nginx()
    else:
        print('Nginx is already running.')
~~~



# 案例：更新nginx配置文件

使用 Python 脚本动态更新 Nginx 配置文件（例如添加一个新的 server 块）。默认的配置文件在`/etc/nginx/nginx.conf`。

~~~python
import subprocess

def add_server_block(file_path, server_block) -> None:
    with open(file_path, 'a') as f:
        f.write(server_block)
    print("New server block has been added to nginx config file.")

def reload_nginx() -> None:
    try:
        result = subprocess.run(['systemctl','reload', 'nginx'], capture_output=True, text=True, check=True)
        print("Nginx is reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reload nginx: {e.stderr}.")

if __name__ == '__main__':
    config = '/etc/nginx/nginx.conf'
    new_server_block = """
    server {
    listen 8080;
    server_name example.com;
    location / {
        proxy_pass http://localhost:8000;
    }
    }
    """

    add_server_block(config, new_server_block)
    reload_nginx()

~~~

