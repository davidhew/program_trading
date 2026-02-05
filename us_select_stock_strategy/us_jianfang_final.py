'''
简放最终选股策略
将动量股池，一年新高股池，最强逻辑股池（暂时还缺）进行求交集，得出最终的股池
'''

import pandas as pd
import pandas_ta as ta
from datetime import datetime
from get_stock_data import get_stock_base_info as gd_base_info
from get_stock_data import get_all_stock_data as gd
import logging

import config

logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()

today = datetime.now()
today_str=today.strftime('%Y-%m-%d')

def compute_final_stock_list():
    momentum_stock_df=pd.read_csv(config.STOCK_STRATEGY_RESULT_DIR + 'momentum-stock-list' + today_str + '.csv')
    one_year_highest_df=pd.read_csv(config.STOCK_STRATEGY_RESULT_DIR+'one-year-highest-list-'+today_str+'.csv')
    result_inner = pd.merge(one_year_highest_df, momentum_stock_df, on='ts_code', how='inner')
    #只需要获取股票代码
    result = result_inner[['ts_code']].copy()
    #只保留前6位数字股票代码，交易所代码简写去掉
    result['ts_code'] = result['ts_code'].str[:6]
    result.to_csv(config.STOCK_STRATEGY_RESULT_DIR+'jianfang-final-list'+today_str+'.txt',index=False,header=False)