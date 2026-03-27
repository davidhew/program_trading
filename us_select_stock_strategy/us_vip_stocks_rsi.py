'''
监控重点股票的rsi情况来驱动做一些短线交易决策
使用前提：
1.要实时跟进对应公司的业务情况，确保其业务基本面没有发生变化，这种情况下，才能用rsi等技术指标去捕捉技术角度的机会

'''
import logging
from datetime import datetime
import pandas as pd
import pandas_ta as ta
import config
from us_get_stock_data import us_get_all_stock_data as usa_gd, us_get_all_stock_data
from utility.monitor_strategy import monitor_strategy
from utility import im_messenger

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()


file_name = 'usa_vip_stock_list.csv'


import logging
logger = logging.getLogger(__name__) # 使用 __name__ 可以知道是哪个文件打印的日志

@monitor_strategy
def get_vip_stock_list():
    print("config value is:"+config.USA_STOCK_DIR)

    df= pd.read_csv(config.USA_STOCK_DIR + "/" + file_name,dtype={'ts_code': str})
    return df['ts_code'].tolist()

def get_vip_stock_rsi_low_limit(ts_code:str):
    df = pd.read_csv(config.USA_STOCK_DIR + "/" + file_name, dtype={'ts_code': str})
    return df.loc[df['ts_code'] == ts_code, 'low_limit'].iloc[0]

def get_vip_stock_rsi_upper_limit(ts_code:str):
    df = pd.read_csv(config.USA_STOCK_DIR + "/" + file_name, dtype={'ts_code': str})
    return df.loc[df['ts_code'] == ts_code, 'upper_limit'].iloc[0]

@monitor_strategy
def compute(date_str:str =None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')
    vip_list=get_vip_stock_list()
    
    message_content = ""

    for ts_code in vip_list:
        stock_df = us_get_all_stock_data.get_stock_df(ts_code)
        # 一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
        if (len(stock_df) < 253):
            print("us_vip_stock_rsi, %s's data less than one year!", ts_code)
            continue
        else:
                matched_indices = stock_df.index[stock_df['trade_date'] == int(date_str)].tolist()
                if len(matched_indices) == 0:
                    continue
                row_idx = matched_indices[0]

                stock_df['RSI6'] = ta.rsi(stock_df['close'], length=6)
                stock_df['RSI14'] = ta.rsi(stock_df['close'], length=14)
                stock_df['RSI24'] = ta.rsi(stock_df['close'], length=24)
                print("save file:"+config.USA_STOCK_DATA_DIR + ts_code)
                stock_df.to_csv(config.USA_STOCK_DATA_DIR + ts_code, index=True)
                
                if(stock_df.iloc[row_idx]['RSI6']<=get_vip_stock_rsi_low_limit(ts_code)):
                    message_content+=ts_code+":进入超卖区间，考虑买入正股或者卖PUT！\n"

                if (stock_df.iloc[row_idx]['RSI6'] >= get_vip_stock_rsi_upper_limit(ts_code)):
                    message_content+=ts_code+":进入超买区间，考虑抛售正股或者卖Covered Call！\n"



    if(len(message_content) > 0):

        title = f"重点股票交易时机-{date_str}"
        im_messenger.send_message(title,message_content)
    else:
        print("重点股票没有交易时机")