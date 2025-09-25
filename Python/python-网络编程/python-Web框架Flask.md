# Flask介绍

Flask 是一个用 Python 编写的轻量级 Web 框架，主要用于快速开发 Web 应用程序和 API。

**什么是 Flask？**

Flask 就像一个工具箱，可以帮助你搭建网站或 Web 应用。它提供了一些基本的功能，让你可以快速开始，而不需要从头写很多代码。

**核心功能**：

- 路由：Flask 允许你定义 URL 路径（例如 http://你的网址/home），并将其映射到处理请求的函数上。

- 请求处理：Flask 能接收用户发送的数据（比如表单输入）并做出相应的处理。

- 返回响应：Flask 可以返回网页内容、JSON 数据或其他类型的信息给用户。

**安装：**

~~~sh
pip3 install Flask
# 国内安装速度慢，可以用清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Flask
~~~

示例：

~~~python
from flask import Flask

app = Flask(__name__) # 创建一个Flask应用，__name__是当前模块的名字

@app.route("/") # 装饰器，定义根路径的路由
def home(): # 当访问这个路径时调用这个函数
    return "Hello from Flask"

if __name__ == "__main__": # 只有在直接运行这个文件的时候才会执行这段代码
    app.run(debug=True)
~~~

## 路由Routes

路由是指用户访问某个特定 URL 时，Flask 应该执行的代码。你可以为每个页面定义不同的路由。

示例：

~~~python
@app.route('/about')
def about():
    return 'This is the About page.'
~~~

## 请求Requests

处理一个用户登录表单，接收用户输入的用户名，并返回一个带有用户名的欢迎信息。

示例：

~~~python
from flask import request, Flask # request是flask提供的对象，用来获取用户发送的数据

@app.route('/login',methods=['POST']) # 定义一个路由，只接受POST请求
def login():
    username = request.form(['username']) # 从表单中获取用户名。意思是用户的post请求需要提交这个字段
    return f'Welcome, {username}.' # 返回欢迎信息
~~~

## 返回响应Responses

Flask 的处理函数可以返回文本、HTML 或 JSON 数据。

示例：

~~~python
@app.route('/json')
def json_response():
    return {'message': 'Hello, JSON!'} # 返回JSON格式的数据
~~~

# 案例：监控服务器健康状态

在现代 IT 环境中，确保服务器的稳定性和性能至关重要。监控服务器的健康状态可以帮助运维团队及时发现和解决潜在问题，从而避免系统宕机、数据丢失或性能下降等严重后果。通过开发一个**健康状态监控 API**，可以实现以下目标：
1. 自动化监控：定期检查服务器资源使用情况，自动记录和响应异常状态。
2. 实时告警：在资源使用超过设定阈值时及时告警，确保运维人员可以迅速采取措施。
3. 数据可视化：生成健康状态报告，为后续的性能分析和资源规划提供数据支持。

步骤：

1. 通过 API 获取服务器的监控数据。
2. 解析响应数据，提取 CPU、内存和磁盘使用率。
3. 设置阈值判断，如果 CPU 或内存使用率超过阈值，记录日志并发送告警。
4. 生成健康状态报告，包括资源使用详情和服务器状态。

创建新目录health_check用于存放项目文件，创建app.py文件。定义`/api/health`接口，用于返回服务器健康状态。

~~~python
from flask import Flask, jsonify
import psutil

#创建flask应用
app = Flask(__name__)

@app.route('/')
def home():
    return 'This is a demo healthy check api.'

# 定义健康检查api
@app.route('/api/health',methods=['GET'])
def health_check():
    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=1)
    # 获取内存使用率
    mem_usage = psutil.virtual_memory().percent
    # 获取磁盘使用情况
    disk_usage = psutil.disk_usage('/').percent
    # 判断服务器状态
    status='unhealthy' if cpu_usage > 80 or mem_usage > 80 or disk_usage > 90 else 'healthy'
    # 返回json数据
    return jsonify ({
        'cpu_usage': cpu_usage,
        'mem_usage': mem_usage,
        'disk_usage': disk_usage,
        'status': status
    })

# 启动flask服务
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
~~~

# 案例：监控服务器状态并输出到日志

基于上面的flask接口，希望把服务器的状态信息记录到日志文件中，那么在app.py同级目录再创建一个monitor.py

~~~python
import requests, logging
from logging import Formatter

# 配置基本日志记录器
logging.basicConfig(
    level=logging.INFO,
    filename='health_monitor/health.log',
    format='%(asctime)s-%(levelname)s: %(message)s',
    encoding='utf-8'
    )

# 自定义时间格式化器
formatter = Formatter('%(asctime)s-%(levelname)s: %(message)s', datefmt='%Y%m%d %H:%M:%S')
# logging.getLogger返回房前日志记录器
# .handlers是日志记录器中负责输出日志的处理器（比如输出到控制台、文件等）
for handler in logging.getLogger().handlers:
    # 这里遍历了所有处理器，都给他应用自定义好的格式化器
    handler.setFormatter(formatter)

# 定义api接口和报警阈值
url = 'http://192.168.71.56:5000/api/health'
threshold_cpu = 80
threshold_mem = 75

def check_health():
    # GET api获取数据
    response = requests.get(url)
    if response.status_code == 200:
        # 返回内容的json格式
        data = response.json()

        # 直接用get方法获取json的某个字段
        cpu_usage = data.get('cpu_usage')
        mem_usage = data.get('mem_usage')
        status = data.get('status')

        # 告警逻辑，超过阈值就输出到日志
        if cpu_usage > threshold_mem:
            logging.warning(f"Warning: CPU Usage {threshold_cpu}%, exceed threshold {threshold_cpu}%.")
        if mem_usage > threshold_mem:
            logging.warning(f"Warning: CPU Usage {threshold_mem}%, exceed threshold {threshold_mem}%.")

        # 日志输出获取到的数据
        logging.info(f"Status: {status}.")
        logging.info(f"CPU Usage: {cpu_usage}%.")
        logging.info(f"Memory Usage: {mem_usage}%.")
    else:
        logging.error('Cannot get server health status')

if __name__ == '__main__':
    check_health()
~~~

# 案例：自动检查并重启服务

某个关键服务在服务器上运行，当该服务异常停止时，需要通过 API 检查并自动重启该服务。

步骤:
1. 通过 API 获取服务状态。
2. 如果服务停止，则通过 API 重启服务。
3. 确认重启操作是否成功。

## 判断逻辑

~~~python
import requests

# 定义服务状态查询接口
status_url = 'https://server/api/service/status'
restart_url = 'https://server/api/service/restart'

# 发送请求获取服务状态
response = requests.get(status_url, headers={'Authorization': 'Bearer YOUR_API_KEY'})

# 判断服务是否停止
if response.status_code == 200:
    # 在返回值的json格式中获取status字段（需要api接口预先返回status字段）
    service_status = response.json().get('status')
    if service_status != 'running':
        print('Service has stopped running, trying to restart it...')
        # 发送重启请求
        restart_response = requests.post(restart_url, headers={'Authorization': 'Bearer YOUR_API_KEY'})
        # 重启成功，返回值200
        if restart_response.status_code == 200:
            print('Service restarted successfully')
        # 重启失败
        else:
            print('Service restarted failed.')
# 状态吗不是200，未能获取到服务状态
else:
    print('Cannot obtain service status.')
~~~

## API接口定义

上面脚本中的status_url和restart_url都需要在flask应用中预先定义好。

通过 Flask 来实现服务状态的检查和重启操作，特别是针对 Nginx 服务的监控。可以使用Flask 来创建这两个 API (/service/status 和 /service/restart) 并结合系统命令来获取和重启Nginx 服务。

以下是一个示例，展示如何通过 Flask 实现该需求：

实现步骤：

1. 获取 Nginx 服务状态：使用 systemctl 命令来检查 Nginx 服务是否在运行。
1. 重启 Nginx 服务：通过 systemctl 命令来重启 Nginx。
1. 通过 Flask 暴露 API：创建 /service/status 和 /service/restart 两个 API。

~~~python
from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__)

# 检查nginx服务状态
# # 返回running说明服务正在运行，返回stopped说明服务已停止
def check_status():
    try:
        # 通过systemctl检查状态
        result = subprocess.run(['systemctl', 'is-active', 'nginx'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        return 'running' if (result.returncode == 0 and result.stdout.strip() == 'active') else 'stopped'
    except Exception as e:
        return f"Error: {str(e)}."

# 重启nginx
# 返回restarted说明已经重启
# 返回其他说明产生报错
def restart_service():
    try:
        result = subprocess.run(
            ['systemctl', 'restart', 'nginx'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return 'restarted' if result.returncode == 0 else f"Failed to restart: {result.returncode}."
    except Exception as e:
        # 在函数里面的try...except，要用return来返回
        return f'Error: {str(e)}'

# flask定义服务状态查询接口
@app.route('/api/service/status', methods=['GET'])
def service_status_api():
    status = check_status()
    # 定义http请求的返回
    return jsonify({'status': status})

# flask定义重启服务接口
@app.route('/api/service/restart', methods=['POST'])
def restart_service_api():
    # 先检查api key认证
    if request.headers.get('Authorization') == 'Bearer YOUR_API_KEY':
        # 执行重启操作获取返回结果
        result = restart_service()
        if result == 'restarted':
            # flask的路由返回值可以在第二个参数显式设定status_code
            return jsonify({'message': 'Service restarted successfully'}), 200
        else:
            return jsonify({'error': f'Unexpected result: {result}'}), 500
    # 认证不通过返回401
    else:
        return jsonify({'error': 'Unauthorized'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
~~~

# 案例：系统资源监控Web应用

我们需要完成以下功能：

- 使用 Python 获取系统资源信息：CPU 使用率、内存使用率、根磁盘使用率和网络带宽。
- 使用 Flask 框架提供一个 Web 前端页面，显示这些实时信息。
- 使用 systemctl 将 Flask 应用作为服务启动。
- 使用 Docker 容器化 Flask 应用。
- 使用 Kubernetes 部署 Flask 应用。

## 编写后端接口

~~~python
from flask import Flask, render_template, jsonify
import psutil, time

# 获取系统指标
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent


def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent

def get_network_usage():
    net_io = psutil.net_io_counters()
    return {
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv
    }


# 创建flask应用
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_system_info')
def get_system_info():
    system_info = {
        'cpu': get_cpu_usage(),
        'memory': get_memory_usage(),
        'disk': get_disk_usage(),
        'network': get_network_usage()
    }
    return jsonify(system_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
~~~

## 编写前端页面

前端页面文件名为index.html，放到app.py同级目录的子目录templates/里面

~~~html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { font-size: 20px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>System Monitoring Dashboard</h1>

    <div class="status">
        <strong>CPU Usage:</strong> <span id="cpu">Loading...</span>%
    </div>
    <div class="status">
        <strong>Memory Usage:</strong> <span id="memory">Loading...</span>%
    </div>
    <div class="status">
        <strong>Disk Usage:</strong> <span id="disk">Loading...</span>%
    </div>
    <div class="status">
        <strong>Network Sent:</strong> <span id="net_sent">Loading...</span> bytes
    </div>
    <div class="status">
        <strong>Network Received:</strong> <span id="net_recv">Loading...</span> bytes
    </div>

    <script>
        function updateSystemInfo() {
            fetch('/get_system_info')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu').innerText = data.cpu;
                    document.getElementById('memory').innerText = data.memory;
                    document.getElementById('disk').innerText = data.disk;
                    document.getElementById('net_sent').innerText = data.network.bytes_sent;
                    document.getElementById('net_recv').innerText = data.network.bytes_recv;
                });
        }

        setInterval(updateSystemInfo, 1000);
        updateSystemInfo();
    </script>
</body>
</html>


~~~

## linux机器安装依赖

~~~sh
# reuiqrements.txt
Flask==2.2.3
psutil==5.9.4

# 安装依赖
yum install  python3.12-devel libffi-devel -y
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install --upgrade Flask Werkzeug -i https://pypi.tuna.tsinghua.edu.cn/simple
~~~

## 配置systemd启动

~~~sh
chown -R root:root /data/monitor-app
chmod -R 755 /data/monitor-app

# 为了让 Flask 应用作为 Linux 服务运行，创建 app.service 文件。/etc/systemd/system/app.service：systemd 服务配置
tee /usr/lib/systemd/system/app.service <<'EOF'
[Unit]
Description=System Monitoring Flask App
After=network.target

[Service]
[Service]
User=root
WorkingDirectory=/data/monitor-app
ExecStart=/usr/bin/python /data/monitor-app/app.py
Restart=always
Environment=FLASK_APP=/data/monitor-app/app.py
StandardOutput=file:/data/monitor-app/app.log
StandardError=file:/data/monitor-app/app_error.log

[Install]
WantedBy=multi-user.target
EOF

#启动服务
systemctl daemon-reload
systemctl start app.service
systemctl status app.service
~~~

## docker运行

~~~sh
tee Dockerfile <<'EOF'
# 使用官方 Python 镜像
FROM python:3.7
# 设置工作目录
WORKDIR /app
# 复制项目文件到容器内
COPY . /app
# 安装依赖
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --upgrade Flask Werkzeug
# 开放 5000 端口
EXPOSE 5000
# 启动 Flask 应用
CMD ["python", "app.py"]
EOF

# 做镜像
docker build -t system-monitoring-app:v1 .
# 启动容器
docker run -d -p 15000:5000 system-monitoring-app:v1
~~~

## K8s运行

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-flask-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-flask-app
  template:
    metadata:
      labels:
        app: python-flask-app
    spec:
      containers:
      - name: python-flask-app
        image: system-monitoring-app:v1
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: python-flask-app-service
spec:
  selector:
    app: python-flask-app
  ports:
    - protocol: TCP
      port: 80          # 服务暴露的端口
      targetPort: 5000   # 容器内运行的端口
      nodePort: 30080    # (可选)指定 NodePort 的端口号，通常在 30000-32767 范围内
  type: NodePort         # 设置服务类型为 NodePort
~~~
