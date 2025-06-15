import re

def make_log_praser(service_name):


    def nginx_praser(line):
    # IP、日期、请求方法、状态码、返回值大小、用户代理
        parts = line.split(' ')
        # ['192.168.40.80', '-', '-', '[30/Aug/2030:11:27:18', '+0800]', '"GET', '/', 'HTTP/1.1"', '200', '3429', '"-"', '"curl/7.61.1"', '"-"']

        # 直接用字符串切片获取对应的值
        return {
            'IP': parts[0],
            'date': parts[3][1:] + ' ' + parts[4][:-1],
            'request': ' '.join(parts[5:8]),
            'status': parts[8],
            'size': parts[9],
            'referer': parts[10],
            'user_agent': parts[11][1:-1]
        }


    def messages_praser(line):
        # 日期、时间、主机名、服务信息、日志消息
        #['Aug', '30', '18:08', 'myhost sshd[1234]: Accepted password for user from 192.168.1.2 port 22 ssh2']
        parts = line.split(' ', 3) # 只分割前三个空格，拿出来日期时间

        if len(parts) < 4:
            raise ValueError('Log line is too short to parse')

        date = parts[0] + ' ' + parts[1]
        time = parts[2]

        # 提取主机名部分
        rest = parts[3]
        host_part = re.match(r'(\S+)', rest) # 匹配剩余部分开头的主机名部分
        if host_part:
            hostname = host_part.group(1) # 提取正则表达式中的第一个捕获组
            rest = rest[len(hostname):].lstrip()
            # 从左边开始切片，去掉hostname部分
            # 'sshd[1234]: Accepted password for user from 192.168.1.2 port 22 ssh2'
        else:
            raise ValueError('Log line is malformed')

        # 获取 sshd 部分，去掉[1234]
        service_message_split = rest.split(':', 1) # 剩余部分用冒号分割一次，分割成两部分 ['sshd[1234]', 'Accepted......']
        if len(service_message_split) < 2:
            return ValueError('Log line is malformed')
        service_message = service_message_split[0].strip()
        # 去掉[1234]
        service_message = re.match(r'(\S+)(?:\[\d+\])', service_message)
        if service_message:
            # 匹配到就取出第1个捕获组的值
            service = service_message.group(1)
        else:
            # 没匹配到说明没有[1234]部分，service就是它本身？（有没有可能是没有前面的部分？）
            service = service_message

        # 获取 Accepted password ... 部分
        message = service_message_split[1].strip()

        # 返回字典结果
        return {
            'date': date,
            'time': time,
            'hostname': hostname,
            'service': service,
            'message': message
        }

    if service_name == 'nginx':
        return nginx_praser
    elif service_name == 'messages':
        return messages_praser
    else:
        raise ValueError('Unknown service name')

if __name__=='__main__':
    nginx_log_praser = make_log_praser('nginx')
    messages_log_praser = make_log_praser('messages')

    nginx_log = '192.168.40.80 - - [30/Aug/2030:11:27:18 +0800] "GET / HTTP/1.1" 200 3429 "-" "curl/7.61.1" "-"'
    messages_log = 'Aug 30 18:08 myhost sshd[1234]: Accepted password for user from 192.168.1.2 port 22 ssh2'

    print(nginx_log_praser(nginx_log))
    print(messages_log_praser(messages_log))