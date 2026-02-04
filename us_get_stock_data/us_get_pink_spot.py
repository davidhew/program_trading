'''
获取粉单市场的列表
'''

import akshare as ak
import sys
import os.path
import config
import time
from functools import lru_cache

import pandas as pd
import logging

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
file_name = 'usa_stock_pink_list.csv'
@lru_cache(maxsize=1)
def get_pink_spot():
    if (need_refresh()):
        stock_us_pink_spot_em_df = ak.stock_us_pink_spot_em()
        stock_us_pink_spot_em_df = stock_us_pink_spot_em_df['代码']
        stock_us_pink_spot_em_df.rename(columns={'代码': 'ts_code'}, inplace=True)
        ##把"153."前缀去除掉
        stock_us_pink_spot_em_df['ts_code'] = stock_us_pink_spot_em_df['ts_code'].str.replace('153.', '', regex=False)
        stock_us_pink_spot_em_df.to_csv(config.USA_STOCK_DIR + "/" + file_name,index=False)
    return pd.read_csv(config.USA_STOCK_DIR + "/" + file_name)

def need_refresh():
    #不存在文件，则获取一次
    if(not os.path.isfile(config.USA_STOCK_DIR+"/"+file_name)):
        return True
    else:
        current_time=int(time.time())
        print(current_time)
        file_time=int(os.path.getmtime(config.USA_STOCK_DIR+"/"+file_name))
        print(file_time)
        #超过1个月没更新，需要更新一次
        time_elapsed=current_time-file_time
        if(time_elapsed>31*24*3600):
            return True
        else:
            logger.info('stocks base info created:%s days, do not need refresh',time_elapsed)
    return False

if __name__ == "__main__":
    #stock_us_pink_spot_em_df = pd.read_csv(config.USA_STOCK_DIR + "/" + file_name)
    #stock_us_pink_spot_em_df.rename(columns={'代码': 'ts_code'}, inplace=True)
    ##把"153."前缀去除掉
    #stock_us_pink_spot_em_df['ts_code'] = stock_us_pink_spot_em_df['ts_code'].str.replace('153.', '', regex=False)
    #stock_us_pink_spot_em_df = stock_us_pink_spot_em_df[['ts_code']]
    #stock_us_pink_spot_em_df.to_csv(config.USA_STOCK_DIR + "/" + file_name,index=False)
    #test_data_integrity()
    get_pink_spot()