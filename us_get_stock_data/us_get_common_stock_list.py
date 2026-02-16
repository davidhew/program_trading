'''
获取common stock list
这里common的含义：
1.不包含otc（场外交易）的标的
2.不包含ETF
3.不包含数字货币
4.其实主要是包含:纳斯达克--NASDAQ，纽约交易所--NYSE,美国证券交易所--AMEX这3个交易所的股票
'''

import sys
import os.path
import config
import time
from functools import lru_cache

import pandas as pd
import requests
from utility import secrets_config as secrets_config
from utility.monitor_strategy import monitor_strategy

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest

file_name = 'usa_common_stock_list.csv'
secrets = secrets_config.load_external_config()

import logging
logger = logging.getLogger(__name__) # 使用 __name__ 可以知道是哪个文件打印的日志
@lru_cache(maxsize=1)
@monitor_strategy
def get_common_stock_list():
    print("config value is:"+config.USA_STOCK_DIR)
    if (need_refresh()):
        stocks_pd = do_get_stock_list()
        stocks_pd.to_csv(config.USA_STOCK_DIR + "/" + file_name,index=False)
    return pd.read_csv(config.USA_STOCK_DIR + "/" + file_name)

def need_refresh():
    #不存在文件，则获取一次
    if(not os.path.isfile(config.USA_STOCK_DIR+"/"+file_name)):
        return True
    else:
        current_time=int(time.time())
        print(current_time)
        file_time=int(os.path.getmtime(config.USA_STOCK_DIR+"/"+file_name))
        print(file_time)
        #超过7天没更新，需要更新一次
        time_elapsed=current_time-file_time
        if(time_elapsed>7*24*3600):
            return True
        else:
            logger.info('us common stock list created:%s days before, do not need refresh',time_elapsed/24/3600)
    return False

HEADERS = {
    'APCA-API-KEY-ID': secrets.get('ALPACA_KEY'),
    'APCA-API-SECRET-KEY': secrets.get('ALPACA_SECRET')
}


def do_get_stock_list():
    # 接口文档：获取所有活跃状态的证券
    url = "https://paper-api.alpaca.markets/v2/assets?status=active"

    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())

        stocks_df = df[['symbol', 'name', 'exchange', 'tradable']]
        stocks_df.to_csv(config.USA_STOCK_DIR+"full_stock_list.csv",index=False)
        # 筛选 OTC 市场的标的
        # Alpaca 中 OTC 市场通常标识为 'OTC'


        exclude_list = ['OTC','BATS','ARCA','CRYPTO','ASCX']
        # 进一步筛选：通常我们会选可空头或易于成交的 (easy_to_borrow)
        # 或者仅仅保留 symbol 和 name
        filtered_list = stocks_df[~stocks_df['exchange'].isin(exclude_list)]

        filtered_list = filtered_list[['symbol']].rename(columns={'symbol':'ts_code'})
        filtered_list.to_csv(config.USA_STOCK_DIR+file_name,index=False)
        return filtered_list
    else:
        print(f"Error: {response.status_code}")
        return None


if __name__ == "__main__":
    trading_client = TradingClient(secrets.get('ALPACA_KEY'), secrets.get('ALPACA_SECRET'))
    asset = trading_client.get_asset('AAPL')
    print(asset)
    do_get_stock_list()
