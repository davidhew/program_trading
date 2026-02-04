'''
针对A股的策略--低位突破启动
1.该股票至少上市一年
2.该股票目前离（最后一个交易日收盘价）最近一年的低点价格上涨不超过20%（防止高位接盘）
3.最后一个交易日的成交量是最近20天的3倍以上
'''

import pandas as pd
import pandas_ta as ta
from datetime import datetime
from get_stock_data import get_stock_base_info as gd_base_info
from utility import date_utility as du
from utility import stock_util as su
from datetime import datetime
from datetime import timedelta
import logging
import os

import config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

from get_stock_data import get_all_stock_data as gd

def compute(date_str:str =None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')
    df_date = pd.DataFrame(columns=['ts_code', 'trade_date'])

    if (os.path.isfile(config.STOCK_STRATEGY_RESULT_DIR + 'low-level-start-pool.csv')):
        df_date = pd.read_csv(config.STOCK_STRATEGY_RESULT_DIR + 'low-level-start-pool.csv')
    stock_list = list()
    stock_datas = gd.get_all_stock_data()
    for stock in stock_datas:
        # 一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
        if (len(stock) < 253):
            logger.info("get_one_year_highest, %s's data less than one year!", stock.iloc[0]['ts_code'])
            continue
        else:
            matched_indices = stock.index[stock['trade_date'] == int(date_str)].tolist()
            if len(matched_indices) == 0:
                continue
            row_idx = matched_indices[0]
            if(row_idx -253 >=0):
                ts_code = stock.iloc[row_idx]['ts_code']

                one_year_low = stock.iloc[row_idx-253:row_idx]['close'].min()
                price_not_high = (stock.iloc[row_idx]['close'] <= one_year_low*2)
                #当天成交量是最近20天平均成交量的2倍及以上
                vol_expand = (stock.iloc[row_idx]['vol']>=2*stock.iloc[row_idx-20:row_idx]['vol'].mean())
                if(not vol_expand):
                    continue

                #不能过于波动，单天的涨跌幅不能超过5%
                is_fluctuant = False

                for i in range(1,20):
                    if(abs(stock.iloc[row_idx-i]['pct_chg']) > 5):
                        is_fluctuant = True

                if(is_fluctuant):
                    continue


                #当天收盘价超过了最近20个交易日的最高价
                highest_in_20_days=stock.iloc[row_idx]['close']>=stock.iloc[row_idx-20:row_idx]['high'].max()

                if(not highest_in_20_days):
                    continue

                #当天涨幅至少5个点
                price_up = stock.iloc[row_idx]['close'] > stock.iloc[row_idx-1]['close']*1.05

                if(not price_up):
                    continue

                #该股票当日成交额要大于5亿（盘子太小可能有问题）;成交额数据是以千为单位的
                amount_enough = (stock.iloc[row_idx]['amount']*1000) >(50000*10000)
                if(not amount_enough):
                    continue

                matched_indices_2 = df_date.index[df_date['ts_code'] == ts_code].tolist()
                if (len(matched_indices_2) > 0):
                    last_date = df_date.iloc[matched_indices_2[0]]['trade_date']
                    #最近一个月内第一次启动才行
                    if(not du.is_days_before(date_str,str(last_date),30)):
                        continue
                # 上一个交易日的盘中最高价，大于最近一年的最高价，证实其就是近一年的最高价
                if (price_not_high and vol_expand and price_up and highest_in_20_days):
                    #计算是否压缩区间工作量比较大，所以符合特定条件后，才进行计算
                    if(su.is_compressed(stock,row_idx)):
                        stock_list.append(stock.iloc[row_idx]['ts_code'])
                        newrow=[stock.iloc[row_idx]['ts_code'],int(date_str)]
                        df_date.loc[len(df_date)] = newrow

    if(len(df_date) > 0):
        # 根据交易日排序，最近的交易日排在前面
        df_date = df_date.sort_values(by=['trade_date'], ascending=True, inplace=False)
        #汰换掉过期的日期，保留最近的日期的数据
        df_date = df_date.drop_duplicates(subset=['ts_code'], keep='last')
    dict = {'ts_code': stock_list}
    df = pd.DataFrame(dict)
    df.to_csv(config.STOCK_STRATEGY_RESULT_DIR + 'low-level-start-' + date_str + '.txt', index=False)
    df_date.to_csv(config.STOCK_STRATEGY_RESULT_DIR + 'low-level-start-pool.csv', index=False)

if __name__ == "__main__":
    today = datetime.now()
    for i in range(180,0, -1):
        start_date = today - timedelta(days=i)
        date_str = start_date.strftime('%Y%m%d')
        compute(date_str)