import re

report = """
CPU Usage: 45%
Memory Usage: 73%
CPU Usage: 55%
Memory Usage: 80%
"""
cpu_pattern = r'CPU Usage:\s*(\d+)%'
mem_pattern = r'Memory Usage:\s*(\d+)%'

# 直接构造整型数组
cpu_usage = [int(match) for match in re.findall(cpu_pattern,report)]
mem_usage = [int(match) for match in re.findall(mem_pattern,report)]

avg_cpu = sum(cpu_usage) / len(cpu_usage)
avg_mem = sum(mem_usage) / len(mem_usage)
print(f"Average CPU Usage: {avg_cpu}%")
print(f"Average Memory Usage: {avg_mem}%")