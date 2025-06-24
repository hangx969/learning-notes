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
    return jsonify({'status': 'status'})

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