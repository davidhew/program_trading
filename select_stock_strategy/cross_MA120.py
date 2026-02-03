'''
穿越120移动平均线的股票
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

logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()


def compute(date_str:str =None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')
    stocks=list()

    for batch in gd.get_stock_data_batches():

        for stock_df in batch:
            # 一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
            if (len(stock_df) < 253):
                logger.info("get_one_year_highest, %s's data less than one year!", stock_df.iloc[0]['ts_code'])
                continue
            else:
                matched_indices = stock_df.index[stock_df['trade_date'] == int(date_str)].tolist()
                if len(matched_indices) == 0:
                    continue
                row_idx = matched_indices[0]
                if (row_idx - 253 >= 0):
                    ts_code = stock_df.iloc[row_idx]['ts_code']
                    if (ts_code == '603958.SH'):
                        print('hello!')

                stock_df['MA50'] = stock_df['close'].rolling(window=50, min_periods=1).mean()
                # 需要MA50趋势向上
                if (not stock_df.iloc[row_idx]['MA50'] >= stock_df.iloc[row_idx - 1]['MA50']):
                    continue

                stock_df['MA120'] = stock_df['close'].rolling(window=120, min_periods=1).mean()

                # 需要MA120趋势向上
                if (not stock_df.iloc[row_idx]['MA120'] >= stock_df.iloc[row_idx - 1]['MA120']):
                    continue
                # 需要MA50在MA120之上
                if (not stock_df.iloc[row_idx]['MA50'] >= stock_df.iloc[row_idx]['MA120']):
                    continue
                open_below_MA_120= (stock_df.iloc[row_idx]['MA120']>stock_df.iloc[row_idx]['open'])
                close_up_MA_120=(stock_df.iloc[row_idx]['close']>stock_df.iloc[row_idx]['MA120'])
                cross_MA_120= open_below_MA_120 and close_up_MA_120

                if(not cross_MA_120):
                    continue
                #当天涨幅至少大于3%
                rise_up_enough = (stock_df.iloc[row_idx]['close']/stock_df.iloc[row_idx]['open']>=1.03)

                if(not rise_up_enough):
                    continue

                #当天成交量超过10亿
                is_amount_enough = stock_df.iloc[row_idx]['amount']*1000>10*10000*10000
                if(not is_amount_enough):
                    continue
                stocks.append(stock_df.iloc[row_idx]['ts_code'])

    stocks = ut.tonghuashun_format(stocks)
    stock_list_df = pd.DataFrame(stocks, columns=['ts_code'])
    stock_list_df.to_csv(config.STOCK_STRATEGY_RESULT_DIR +'cross-MA120-' + date_str + '.EBK', index=False, header=False)
