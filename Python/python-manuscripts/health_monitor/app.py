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