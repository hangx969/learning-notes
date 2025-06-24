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