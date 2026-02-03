'''
用切面实现统一的日志打印
'''
import functools
import logging
import traceback
import os

logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()


def aspect_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # 正常执行被调用的函数
            result = func(*args, **kwargs)
        except Exception as e:
            # 获取切面信息
            func_name = func.__name__  # 函数名
            file_name = os.path.basename(func.__code__.co_filename)  # 文件名
            line_no = func.__code__.co_firstlineno  # 函数定义的起始行号

            # 构建错误日志
            error_msg = (
                f"\n--- 异常切面捕捉 ---\n"
                f"位置: 文件 {file_name} [第 {line_no} 行]\n"
                f"函数: {func_name}\n"
                f"参数: args={args}, kwargs={kwargs}\n"
                f"错误类型: {type(e).__name__}\n"
                f"错误原因: {str(e)}\n"
                f"堆栈信息:\n{traceback.format_exc()}"
                f"--------------------"
            )

            logging.error(error_msg)

            # 根据需求：是继续抛出异常还是返回空/默认值
            # raise e  # 如果希望程序停止，取消此行注释
            return None

    return wrapper
