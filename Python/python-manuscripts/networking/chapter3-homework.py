import psutil

cpu_usage = psutil.cpu_percent(interval=1)
total_mem = psutil.virtual_memory().total / 2**30
used_mem = psutil.virtual_memory().used / 2**30
free_mem = psutil.virtual_memory().free / 2**30
percent_mem = used_mem / total_mem

print(f"CPU Usage: {cpu_usage}%.")
print(f"Total Memory:{total_mem: .2f} GiB.")
print(f"Used Memory:{used_mem: .2f} GiB.")
print(f"Free Memory:{free_mem: .2f} GiB.")
print(f"Memory Used Percent:{percent_mem: .1f}%.")