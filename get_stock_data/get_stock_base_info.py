'''
获取A股，港股，美股等股票列表原始信息
这些原始信息获取后，保存在本地，相当于作为种子列表，来获取这些股票每日的交易数据来更新股票的日级别交易历史数据
这个原始信息保存在本地，每个月更新一次即可，不需要频繁更新
'''
import sys
import os.path
import config
import time

import pandas as pd
import logging
import tushare as ts
from utility import secrets_config as secrets_config
from functools import lru_cache
logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
file_name = 'china_stock_list.csv'

@lru_cache(maxsize=1)
def get_china_stock_base_info():

    if(need_refresh()):
        secrest = secrets_config.load_external_config()
        ts.set_token(secrest.get('TUSHARE_TOKEN'))
        pro = ts.pro_api()
        china_stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        china_stock_list.to_csv(config.CHINA_STOCK_DIR+"/"+file_name)
    return pd.read_csv(config.CHINA_STOCK_DIR+"/"+file_name)

def get_name_from_code(ts_code:str):
    stocks_df = get_china_stock_base_info()
    row_idx = stocks_df.index[stocks_df['ts_code'] == ts_code].tolist()[0]
    if row_idx <= len(stocks_df) and stocks_df.iloc[row_idx]['ts_code'] == ts_code:
        return stocks_df.iloc[row_idx]['name']
    else:
        return None

def need_refresh():
    #不存在文件，则获取一次
    if(not os.path.isfile(config.CHINA_STOCK_DIR+"/"+file_name)):
        return True
    else:
        current_time=int(time.time())
        print(current_time)
        file_time=int(os.path.getmtime(config.CHINA_STOCK_DIR+"/"+file_name))
        print(file_time)
        #超过1个月没更新，需要更新一次
        if(current_time-file_time>31*24*3600):
            return True
    return False
