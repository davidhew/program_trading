'''
选股策略
最近一个交易日的股价高点是最近一年的股价高点
注意：使用的是盘中最高价作为比较依据，而非收盘价
'''
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from get_stock_data import get_stock_base_info as gd_base_info
from us_get_stock_data import us_get_all_stock_data as usa_gd
import logging

import config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()


today = datetime.now()
today_str=today.strftime('%Y-%m-%d')
def compute_one_year_highest():
    stock_list = list()
    stock_datas = usa_gd.get_all_stock_data()
    for stock in stock_datas:
        #一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
        if(len(stock)<253):
            logger.info("get_one_year_highest, %s's data less than one year!",stock.iloc[0]['ts_code'])
            continue
        else:
            one_year_high = stock.iloc[1:253]['high'].max()
            #平均每天成交额要大于1亿美金--股票盘子不能太小
            amount_ok = stock['amount'].tail(20).sum()/20 > 100000000
            #上一个交易日的盘中最高价，大于最近一年的最高价，证实其就是近一年的最高价
            if(stock.iloc[0]['high'] > one_year_high and amount_ok):
                stock_list.append(stock.iloc[0]['ts_code'])
    dict={'ts_code':stock_list}
    df = pd.DataFrame(dict)
    df.to_csv(config.USA_STOCK_STRATEGY_RESULT_DIR+'one-year-highest-list-'+today_str+'.csv',index=False)

    #近一年新高的统计其行业分布情况
    #df2 = gd_base_info.get_china_stock_base_info()
    #result_inner = pd.merge(df,df2,on='ts_code',how='inner')
    #counts_size = result_inner.groupby('industry').size().reset_index(name='counts')
    #counts_size = counts_size.sort_values(by='counts',ascending=False)
    #counts_size.to_csv(config.STOCK_STRATEGY_RESULT_DIR+'industry-one-year-highest-list'+today_str+'.csv',index=False)






