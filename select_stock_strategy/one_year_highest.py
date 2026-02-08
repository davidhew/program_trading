'''
选股策略
最近一个交易日的股价高点是最近一年的股价高点
注意：使用的是盘中最高价作为比较依据，而非收盘价
'''
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from get_stock_data import get_stock_base_info as gd_base_info
import logging
from utility.monitor_strategy import monitor_strategy

import config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

from get_stock_data import get_all_stock_data as gd
today = datetime.now()

@monitor_strategy
def compute(date_str:str =None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')

    stoack_list_df = pd.DataFrame(columns=['ts_code','name'])
    for batch in gd.get_stock_data_batches():

        for stock in batch:

            #一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
            if(len(stock)<253):
                print("one_year_highest, %s's data less than one year!",stock.iloc[0]['ts_code'])
                continue
            else:
                matched_indices = stock.index[stock['trade_date'] == int(date_str)].tolist()
                if len(matched_indices) == 0:
                    continue
                row_idx = matched_indices[0]
                if row_idx - 253 >=0 and stock.iloc[row_idx]['trade_date'] == int(date_str):
                    one_year_high = stock.iloc[row_idx-253:row_idx]['close'].max()
                    #上一个交易日的盘中最高价，大于最近一年的最高价，证实其就是近一年的最高价
                    if(stock.iloc[row_idx]['close'] > one_year_high):
                        ts_code = stock.iloc[row_idx]['ts_code']
                        name = gd_base_info.get_name_from_code(ts_code)
                        new_row_values = [ts_code, name]
                        stoack_list_df.loc[len(stoack_list_df)] = new_row_values

    stoack_list_df.to_csv(config.STOCK_STRATEGY_RESULT_DIR +'one-year-highest-list-' + date_str + '.csv', index=False)

    #近一年新高的统计其行业分布情况
    df2 = gd_base_info.get_china_stock_base_info()
    result_inner = pd.merge(stoack_list_df,df2,on='ts_code',how='inner')
    counts_size = result_inner.groupby('industry').size().reset_index(name='counts')
    counts_size = counts_size.sort_values(by='counts',ascending=False)
    counts_size.to_csv(config.STOCK_STRATEGY_RESULT_DIR +'industry-one-year-highest-list-' + date_str + '.csv', index=False)

    logger.info("success:compute:one_year_highest:%s finished!",date_str)




