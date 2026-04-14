'''
大市值公司股价暴跌（要注意暴跌原因，比如是一些突发事件导致的暴跌），预警出来，加上人工判断，可能是一个卖put的好时机
'''

import logging
from datetime import datetime
import pandas as pd
import config
from us_get_stock_data import us_get_all_stock_data as usa_gd
from us_get_company_info import us_get_company_info
from utility import im_messenger
from utility.monitor_strategy import monitor_strategy

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

@monitor_strategy
def compute():

    stock_list=list()

    for batch in usa_gd.get_stock_data_batches():

        for stock_df in batch:
            # 一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
            if (len(stock_df) < 253):
                logger.info("us_big_company_plumet, %s's data less than one year!", stock_df.iloc[0]['ts_code'])
                continue
            else:
                market_cap = us_get_company_info.get_market_cap(stock_df.iloc[-1]['ts_code'])
                #市值必须大于500亿
                if(market_cap < 500*10000*10000):
                    continue
                #单日跌幅达7%及以上
                if(stock_df.iloc[-1]['close'] <= stock_df.iloc[-2]['close']*0.93):
                    stock_list.append(stock_df.iloc[-1]['ts_code'])


    if(len(stock_list) > 0):
        dict = {'ts_code': stock_list}
        df = pd.DataFrame(dict)

        base_info_df = us_get_company_info.get_us_stock_base_info()
        result_inner = pd.merge(df, base_info_df, on='ts_code', how='inner')
        result_inner = result_inner.sort_values(by=['marketCap'], ascending=False, inplace=False)

        # 带上板块信息
        result_inner_filtered = result_inner[['ts_code', 'sector']]
        content_str = result_inner_filtered.to_string(index=False, justify='center')
        date_str = datetime.now().strftime('%Y%m%d')
        title = f"股价暴跌的大公司股票-{date_str}"
        im_messenger.send_message(title,content_str)
    else:
        print("no big company plummet")