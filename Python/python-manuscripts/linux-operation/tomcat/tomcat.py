import time, subprocess

def check_tomcat() -> bool:
    try:
        result = subprocess.run("ps aux | grep tomcat | grep -v grep | grep -v python", shell=True, capture_output=True, check=True, text=True)
        if result.stdout:
            print("Tomcat is running.")
            return True
        else:
            print("Tomcat is not running")
            return False
    except Exception as e:
        print(f"An error occurred while checking TOmcat status: {e}.")
        return False

def start_tomcat():
    try:
        tomcat_start_command="/opt/tomcat/bin/catalina.sh start"
        result = subprocess.run(tomcat_start_command, shell=True, text=True, capture_output=True, check=True)
        if result.returncode == 0:
            print("Tomcat started successfully.")
        else:
            print("Failed to start tomcat.")
    except Exception as e:
        print(f"{e}")

def monitor_tomcat(interval):
    while True:
        if not check_tomcat():
            start_tomcat()
        else:
            print("No actionneeded, tomcat is running.")
        time.sleep(interval)

if __name__ == '__main__':
    monitor_tomcat(60)