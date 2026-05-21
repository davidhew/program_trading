'''统一的处理日志'''

import logging
import config

from logging.handlers import RotatingFileHandler


def setup_logging():
    # 获取根日志记录器
    core_logger = logging.getLogger("app_core")
    core_logger.setLevel(logging.INFO)

    # 格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 1. 创建控制台处理器 (输出到终端)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    core_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        config.LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'  # 建议加上编码，防止跨境系统/跨平台乱码
    )


    file_handler.setFormatter(formatter)
    core_logger.addHandler(file_handler)
    # 【核心改动 1】阻止 core_logger 向 Root 传递
    core_logger.propagate = False

    # 获取根日志记录器
    dashboard_logger = logging.getLogger("dashboard")
    dashboard_logger.setLevel(logging.INFO)

    file_handler2 = RotatingFileHandler(
        config.DASHBOARD_LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding='utf-8'  # 建议加上编码，防止跨境系统/跨平台乱码
    )
    file_handler2.setFormatter(formatter)

    dashboard_logger.addHandler(file_handler2)
    dashboard_logger.addHandler(console_handler)
    # 【核心改动 2】阻止 dashboard_logger 向 Root 传递
    dashboard_logger.propagate = False

    # 可选：顺手给 Root Logger 穿件衣裳，防止第三方库（如 SQLAlchemy）打印裸日志
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.addHandler(console_handler)
