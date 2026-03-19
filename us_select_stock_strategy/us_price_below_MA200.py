'''
美股-股价低于MA200线的股票

'''
import logging
from datetime import datetime
import pandas as pd
import config
from us_get_stock_data import us_get_all_stock_data as usa_gd
from us_get_company_info import us_get_company_info
from utility import telegram_messenger
from utility.monitor_strategy import monitor_strategy

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

@monitor_strategy
def compute(date_str:str =None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')
    stock_list=list()

    for batch in usa_gd.get_stock_data_batches():

        for stock_df in batch:
            # 一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
            if (len(stock_df) < 253):
                print("price_below_MA200, %s's data less than one year!", stock_df.iloc[0]['ts_code'])
                continue
            else:
                matched_indices = stock_df.index[stock_df['trade_date'] == int(date_str)].tolist()
                if len(matched_indices) == 0:
                    continue
                row_idx = matched_indices[0]
                if (row_idx - 253 >= 0):
                    ts_code = stock_df.iloc[row_idx]['ts_code']




                stock_df['MA200'] = stock_df['close'].rolling(window=200, min_periods=1).mean()

                # 收盘价在200均线以下
                if (not stock_df.iloc[row_idx]['close'] <= stock_df.iloc[row_idx]['MA200']):
                    continue

                market_cap = us_get_company_info.get_market_cap(stock_df.iloc[row_idx]['ts_code'])
                #市值必须大于500亿
                if(market_cap < 500*10000*10000):
                    continue

                stock_list.append(stock_df.iloc[row_idx]['ts_code'])

    if(len(stock_list) > 0):
        dict = {'ts_code': stock_list}
        df = pd.DataFrame(dict)

        base_info_df = us_get_company_info.get_us_stock_base_info()
        result_inner = pd.merge(df, base_info_df, on='ts_code', how='inner')
        result_inner = result_inner.sort_values(by=['marketCap'], ascending=False, inplace=False)

        # 带上板块信息
        result_inner_filtered = result_inner[['ts_code', 'sector']]
        content_str = result_inner_filtered.to_string(index=False, justify='center')
        message = f"<b>股价在200均线以下股票-{date_str}</b>\n<pre>{content_str}</pre>"
        telegram_messenger.send_message(message,"PRICE_BELOW_MA200")
    else:
        print("no price below MA200 stocks")