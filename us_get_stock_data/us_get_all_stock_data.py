'''
获取本地的所有股票数据，通过列表进行返回
主要是用在执行选股策略的场景
'''

from pathlib import Path

import config
import sys
import pandas as pd
import logging
logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

def get_all_stock_data():
    stock_datas = list()
    stock_data_folder = Path(config.USA_STOCK_DATA_DIR)
    if stock_data_folder.exists() and stock_data_folder.is_dir():
        for file in stock_data_folder.iterdir():
            if file.is_file():
                stock_datas.append(pd.read_csv(file.resolve()))
            else:
                logger.error("In stock data dir, there exist no cvs file, the file name is:%s",file.resolve())
        return stock_datas
    else:
        logger.error("The stock data dir isn't exist or is not a directory, stock data dir is:%s",stock_data_folder.resolve())
        sys.exit(1)
