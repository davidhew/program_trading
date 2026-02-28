'''
选股策略
最近一个交易日的股价高点是最近一年的股价高点
注意：使用收盘价作为比较依据
'''
import pandas as pd
import pandas_ta as ta
from datetime import datetime
from us_get_company_info import us_get_company_info
from us_get_stock_data import us_get_all_stock_data as usa_gd
from utility.monitor_strategy import monitor_strategy
from utility import telegram_messenger
import config
import logging
logger = logging.getLogger(__name__) # 使用 __name__ 可以知道是哪个文件打印的日志



@monitor_strategy
def compute(date_str:str=None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')

    stock_list = list()
    for batch in usa_gd.get_stock_data_batches():

        for stock in batch:
            #一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
            if(len(stock)<253):
                print("get_one_year_highest, %s's data less than one year!",stock.iloc[0]['ts_code'])
                continue
            else:
                matched_indices = stock.index[stock['trade_date'] == int(date_str)].tolist()
                if len(matched_indices) == 0:
                    continue
                row_idx = matched_indices[0]
                if row_idx - 253 >= 0 and stock.iloc[row_idx]['trade_date'] == int(date_str):
                    one_year_high = stock.iloc[row_idx-253:row_idx]['close'].max()
                    #平均每天成交额要大于1亿美金--股票盘子不能太小
                    amount_ok = stock['amount'].tail(20).sum()/20 > 100000000
                    #上一个交易日的收盘价，大于最近一年的最高价，证实其就是近一年的最高价
                    if(stock.iloc[row_idx]['close'] > one_year_high and amount_ok):
                        stock_list.append(stock.iloc[0]['ts_code'])
    dict={'ts_code':stock_list}
    df = pd.DataFrame(dict)

    base_info_df = us_get_company_info.get_us_stock_base_info()
    result_inner = pd.merge(df, base_info_df, on='ts_code', how='inner')
    result_inner = result_inner.sort_values(by=['marketCap'],ascending=False,inplace=False)

    #带上板块信息
    result_inner_filtered = result_inner[['ts_code','sector']]
    content_str = result_inner_filtered.to_string(index=False, justify='center')
    message = f"<b>历史新高的股票-{date_str}</b>\n<pre>{content_str}</pre>"
    telegram_messenger.send_telegram_message(message)


    counts_size = result_inner.groupby('sector').size().reset_index(name='counts')
    count_size_filtered = counts_size[['sector','counts']]
    count_size_filtered = count_size_filtered.sort_values(by=['counts'], ascending=False, inplace=False)
    count_size_filtered_1 = count_size_filtered[count_size_filtered['counts']>0]
    count_size_filtered_2 = count_size_filtered[count_size_filtered['counts']>1]

    content_str=count_size_filtered_2.to_string(index=False, justify='center')
    message = f"<b>历史新高股票板块情况-{date_str}</b>\n<pre>{content_str}</pre>"
    telegram_messenger.send_telegram_message(message)


    df.to_csv(config.USA_STOCK_STRATEGY_RESULT_DIR+'one-year-highest-list-'+date_str+'.csv',index=False)
    count_size_filtered_1.to_csv(config.USA_STOCK_STRATEGY_RESULT_DIR+'one-year-highest-sector-'+date_str+'.csv',index=False)








