'''
获取本地的所有股票数据，通过列表进行返回
主要是用在执行选股策略的场景
'''

from pathlib import Path

import config
import sys
import pandas as pd
import logging
from utility import monitor_strategy
logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

@monitor_strategy
def get_stock_data_batches(batch_size=10):

    stock_data_folder = Path(config.USA_STOCK_DATA_DIR)
    if not (stock_data_folder.exists() and stock_data_folder.is_dir()):
        logging.error(f"路径不存在或非目录: {stock_data_folder.resolve()}")
        sys.exit(1)

    # 获取所有符合条件的 csv 文件列表
    file_list = [f for f in stock_data_folder.iterdir() if f.is_file()]

    if not file_list:
        logging.warning(f"目录中没有 CSV 文件: {stock_data_folder.resolve()}")
        return
    current_batch = []
    for i, file_path in enumerate(file_list):
        try:
            # 读取数据
            df = pd.read_csv(file_path.resolve())
            current_batch.append(df)

            # 当达到批次大小，或者到达最后一个文件时，返回当前批次
            if len(current_batch) == batch_size:
                yield current_batch
                # 关键：手动清理当前批次，释放内存
                current_batch = []

        except Exception as e:
            logging.error(f"读取文件失败 {file_path.name}: {e}")

        # 处理最后一组不满 batch_size 的数据
    if current_batch:
        yield current_batch
