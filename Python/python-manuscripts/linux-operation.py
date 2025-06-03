import subprocess, time

process = subprocess.Popen(['sleep','30'])
time.sleep(5)

print(f"subprocess running, PID: {process.pid}")

# 使用terminate终止子进程
process.terminate()
print("SIGTERM has been sent.")
time.sleep(1)

#使用poll检查进程状态。如果返回None说明还没终止。已经终止会返回exit code
status = process.poll()
if status is None:
    print ("subprocess is still running, will kill it.")

    # 使用kill强行终止子进程
    process.kill()
    print("SIGKILL has been sent.")

else:
    print(f"subprocess has exited, exit code is {status}")
