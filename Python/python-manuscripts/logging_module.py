import logging

# logging 记录器
# 开启DEUBG级别信息，意思是所有等级日志都记录
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-%(levelname)s-%(message)s',
                    datefmt='%m%d_%H:%M:%S')

# 记录日志
logging.debug("This is debug message")
logging.info("This is info message")
logging.warning("This is warning message")
logging.error("This is error message")
logging.critical("This is critical message")