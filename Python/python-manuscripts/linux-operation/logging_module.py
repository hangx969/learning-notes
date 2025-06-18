import logging, os
from logging.handlers import SMTPHandler

os.chdir('/home/s0001969/Documents/learning-notes-git/Python/python-manuscripts/')

# 创建一个日志记录器
logger = logging.getLogger('smtp_logger')
logger.setLevel(logging.ERROR)

# 创建SMTP处理器,password是发件邮箱的smtp的授权码
smtp_handler = SMTPHandler(mailhost=('smtp.163.com', 25),
                           fromaddr='xxxxxx@163.com',
                           toaddrs=['xxxxx@qq.com'],
                           subject="Error log",
                           credentials=('user','password'),
                           secure=()
                           )

# 创建格式化器
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s: %(message)s', datefmt='%Y%m%d_%H:%M:%S')
smtp_handler.setFormatter(formatter)

# 将处理器添加到记录器上
logger.addHandler(smtp_handler)

# 记录日志，每一条日志独立发送
logger.error(f'This is an error message.')
logger.critical(f'This is an critical message.')