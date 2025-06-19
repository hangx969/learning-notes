import subprocess, time, requests

def check_es() -> bool:
    try:
        response = requests.get('http://172.16.183.101:9200/_cluster/health')
        if response.status_code == 200:
            print("ES is running.")
            return True
        else:
            return False
    except requests.exceptions.RequestException: # 这里会包括ConnectionError、Timeout、InvalidURL、SSLError等
        print("ES is not running.")
        return False

def restart_es():
    try:
        print("Restarting ES.")
        result = subprocess.run(["systemctl", "restart","elasticsearch"], check=True, capture_output=True, text=True)
        print("ES restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart es: {e}.")

if __name__ == '__main__':
    while True:
        if not check_es():
            restart_es()
        else:
            print("ES is running, do nothing.")
        time.sleep(60)