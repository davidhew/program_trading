'''
简放最终选股策略
将动量股池，一年新高股池，最强逻辑股池（暂时还缺）进行求交集，得出最终的股池
'''

import pandas as pd
import pandas_ta as ta
import os.path
from datetime import datetime
from get_stock_data import get_stock_base_info as gd_base_info
from get_stock_data import get_all_stock_data as gd
from utility import date_utility as du
from utility import util as ut
import logging

import config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

today = datetime.now()

def compute(date_str:str =None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')
    momentum_stock_df=pd.read_csv(config.STOCK_STRATEGY_RESULT_DIR + 'momentum-stock-list-20-' + date_str + '.csv')
    one_year_highest_df=pd.read_csv(config.STOCK_STRATEGY_RESULT_DIR +'one-year-highest-list-' + date_str + '.csv')
    result_inner = pd.merge(one_year_highest_df, momentum_stock_df, on=['ts_code'], how='inner')


    result_inner['trade_date'] = int(date_str)

    old_df = pd.DataFrame()
    file_path=config.STOCK_STRATEGY_RESULT_DIR + "jianfang-final-list-withdate.csv"
    # 该股票已经保留了一些历史数据，需要取出来进行合并
    if (os.path.isfile(file_path)):
        old_df = pd.read_csv(file_path)

    if old_df is not None and not old_df.empty and 'ts_code' in old_df.columns:
        old_enlist_set = set(old_df['ts_code'])
    else:
        old_enlist_set = set()

    new_enlist = list(set(result_inner['ts_code'])-old_enlist_set)

    # 新老数据合并
    concat_df = pd.concat([result_inner, old_df], axis=0, ignore_index=True)
    print(f"DEBUG: concat_df columns:{concat_df.columns.tolist()}")
    concat_df = concat_df[config.JIANFANG_STOCK_POOL_DATA_COLUMN]

    # 数据提供方的原因，不同历史时期的数据，trade_date这一列的数据类型有可能是不一致的
    concat_df['trade_date'] = concat_df['trade_date'].astype(int)
    # 根据交易日排序，最近的交易日排在后面
    concat_df = concat_df.sort_values(by=['trade_date'], ascending=True, inplace=False)
    # print(concat_df)
    # 去除重复数据，一只股票,保留其最近的记录
    concat_df = concat_df.drop_duplicates(subset=['ts_code'], keep='last')

    expired_date = du.days_befor(date_str, config.JIANFANG_POOL_EXPIRE_DAYS)

    expired_df = concat_df[concat_df['trade_date'] <= expired_date]
    logger.info("jianfang_final compute: remove expired_stocks:"+expired_df['name'].to_string(index=False))

    alive_df = concat_df[concat_df['trade_date'] > expired_date].reset_index(drop=True)

    alive_df.to_csv(file_path, index=True)

    stocks = alive_df['ts_code'].tolist()

    #处理成同花顺能够接受导入的格式
    stock_list = ut.tonghuashun_format(stocks)
    stock_list_df_ths = pd.DataFrame(stock_list, columns=['ts_code'])

    stock_list_df = pd.DataFrame(alive_df['ts_code'].tolist(),columns=['ts_code'])

    new_enlist_df = pd.DataFrame(new_enlist, columns=['ts_code'])

    stock_list_df_ths.to_csv(config.STOCK_STRATEGY_RESULT_DIR +'jianfang-final-list-ths-' + date_str + '.EBK', index=False, header=False)
    stock_list_df.to_csv(config.STOCK_STRATEGY_RESULT_DIR +'jianfang-final-list-' + date_str + '.txt', index=False, header=True)
    new_enlist_df.to_csv(config.STOCK_STRATEGY_RESULT_DIR +'jianfang-final-list-newen-' + date_str + '.txt', index=False, header=False)
    logger.info('jianfang_final:compute:%s success!', date_str)