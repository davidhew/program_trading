'''
装饰器模式，用来拦截各个函数，破获其异常，发送报警

'''
import traceback
import functools
import config
from . import telegram_messenger
from datetime import datetime

import logging

logger = logging.getLogger(__name__)

def monitor_strategy(func):
    """
    策略监控装饰器：自动记录日志并发送钉钉告警
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:

            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # 1. 构造详细的错误信息
            err_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_msg = traceback.format_exc()  # 获取完整堆栈信息

            summary = f"运行异常: {func.__name__}\n时间: {err_time}\n错误类型: {type(e).__name__}\n详情: {str(e)}"

            # 2. 打印到本地日志
            logger.error(f"函数 {func.__name__} 发生崩溃:\n{error_msg}")

            # 3. 发送钉钉告警
            telegram_messenger.send_telegram_message(summary)

            # 4. 根据需求：你可以选择继续抛出异常(raise)或者返回None
            # 在策略机器人中，通常建议抛出，由外部调度器处理
            raise e

    return wrapper
