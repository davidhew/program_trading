'''
装饰器模式，用来拦截各个函数，破获其异常，发送报警

'''
import traceback
import functools
import config
from utility import im_messenger
from datetime import datetime

import logging

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

def db_monitor(db_instance):
    """
    策略监控装饰器：自动记录日志并发送钉钉告警
    """
    """
        数据库监控装饰器
        :param db_instance: dataset 的数据库连接对象 (db)
        """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:

                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # 1. 【关键修复步骤】立即重置连接池，防止 PendingRollbackError 蔓延
                try:
                    logger.warning(f"检测到数据库异常，正在重置连接池: {func.__name__}")
                    db_instance.engine.dispose()
                except Exception as dispose_e:
                    logger.error(f"释放数据库连接失败: {dispose_e}")

                # 2. 构造详细错误信息
                err_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                error_msg = traceback.format_exc()

                summary = (
                    f"🛑 数据库操作异常\n"
                    f"函数: {func.__name__}\n"
                    f"时间: {err_time}\n"
                    f"错误类型: {type(e).__name__}\n"
                    f"详情: {str(e)}"
                )

                # 3. 日志记录与钉钉告警
                logger.error(f"函数 {func.__name__} 运行崩溃:\n{error_msg}")

                # 4. 根据需求：你可以选择继续抛出异常(raise)或者返回None
                # 在策略机器人中，通常建议抛出，由外部调度器处理
                raise e

        return wrapper
    return decorator
