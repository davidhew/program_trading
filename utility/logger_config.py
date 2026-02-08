'''统一的处理日志'''

import logging
import config

def setup_logging():
    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 1. 创建控制台处理器 (输出到终端)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 创建文件处理器 (输出到文件)
    file_handler = logging.FileHandler(config.LOG_FILE_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger