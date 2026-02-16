'''
从数据提供方远程获取股票数据，处理后和本地的历史数据进行合并
'''
import datetime
import sys
import os.path
from datetime import timedelta
from datetime import datetime

import config

import pandas as pd
import time
import tushare as ts
import numpy as np
from utility.monitor_strategy import monitor_strategy
from us_get_stock_data import us_get_common_stock_list  as us_get_common
from utility import secrets_config as secrets_config

secrest = secrets_config.load_external_config()
ts.set_token(secrest.get('TUSHARE_TOKEN'))
pro = ts.pro_api()

import logging
logger = logging.getLogger(__name__) # 使用 __name__ 可以知道是哪个文件打印的日志

#由于有脏数据，需要过滤剩下正常的股票代码
def is_valid_stock_code(x):
    # 判断不是 NaN 且 转换字符串后不是空
    return x == x and x is not None and str(x).strip() != ""

#项目刚启动的时候，初始化股票历史日线数据，目前是获取最近1000天的数据
@monitor_strategy
def init_data():
    stocks = us_get_common.get_common_stock_list['ts_code'].unique()
    mask = np.vectorize(is_valid_stock_code)(stocks)
    stocks = stocks[mask]
    i=0
    for stock in stocks:
        print(stock)
        try:
            init_data_for_stock(stock)
        except Exception as e:
            logger.error("Error occurs when init data for stock:%s, error info:%s", stock, e)
        i=i+1
        if(i%100==0):
            time.sleep(1)

#初始化指定股票的历史数据，目前是获取最近1000天的数据
def init_data_for_stock(ts_code):

    today = datetime.now()
    start_date = today-timedelta(days=int(config.DAY_NUMBER))
    start_date_str=start_date.strftime('%Y%m%d')
    end_date_str=today.strftime('%Y%m%d')
    try:
        update_stock_datas(ts_code, start_date_str, end_date_str)
    except Exception as e:
        logger.error("Error occurs when init data for stock:%s, error info:%s", ts_code, e)


@monitor_strategy
#每日运行的任务，理论上正常情况下，只要取当天的日线数据补到历史数据即可;为了提高容错性，取最近5天的数据
def daily_update():
    today = datetime.now()
    common_stock_df = us_get_common.do_get_stock_list()
    #从1开始，因为中美时区的差异
    for i in range(2,0,-1):
        start_date = today - timedelta(days=i)
        date_str = start_date.strftime('%Y%m%d')
        #df = pro.us_daily(trade_date=date_str)

        limit = 2000  # 建议显式设置，通常该接口最大单次限制为2000
        offset = 0
        all_df = pd.DataFrame()

        while True:
            # 抓取当前页数据
            df = pro.us_daily(trade_date=date_str,limit=limit, offset=offset)
            # 1. 检查数据是否为空
            if df is None or df.empty:
                print("所有数据已取完。")
                break
            # 2. 将当前页拼接到总表
            all_df = pd.concat([all_df, df], ignore_index=True)
            # 3. 判断是否还有下一页
            print(f"当前已获取 {len(all_df)} 条数据...")
            if len(df) < limit:
                # 返回条数小于限制条数，说明是最后一页
                print("到达最后一页，停止抓取。")
                break
            else:
                # 否则，增加偏移量，继续下一页
                offset += limit
                # 为防止触发频率限制（根据积分而定），建议加一个小延迟
                time.sleep(1)

        #如果非交易日，则没有数据
        if(len(all_df)==0):
            continue
        #去除脏数据

        all_df = all_df[all_df['ts_code'].notna() & (all_df['ts_code'].str.strip() != "")]
        common_stocks = all_df[all_df['ts_code'].isin(common_stock_df['ts_code'])]
        grouped = common_stocks.groupby('ts_code')
        for group in grouped.groups:
            save_daily_data(grouped.get_group(group))

def update_stock_datas(ts_codes, start_date, end_date):

    df = pro.us_daily(ts_code=ts_codes, start_date=start_date, end_date=end_date)
    grouped = df.groupby('ts_code')
    for group in grouped.groups:
        save_daily_data(grouped.get_group(group))

def save_daily_data(df):
    ts_codes_array = df['ts_code'].unique()
    #应该只针对单一的股票数据进行处理
    if len(ts_codes_array) != 1:
        logger.critical('There are more than one ts_code want to save, ts_codes are : %s', ts_codes_array.array_str())
        sys.exit(1)
    else:
        old_df = pd.DataFrame()
        #该股票已经保留了一些历史数据，需要取出来进行合并
        if(os.path.isfile(config.USA_STOCK_DATA_DIR+ts_codes_array[0])):
            old_df=pd.read_csv(config.USA_STOCK_DATA_DIR+ts_codes_array[0])
        #新老数据合并
        concat_df = pd.concat([df,old_df],axis=0,ignore_index=True)
        #只保留有用的列数据
        concat_df=concat_df[config.USA_STOCK_DATA_COLUMN]
        #数据提供方的原因，不同历史时期的数据，trade_date这一列的数据类型有可能是不一致的
        concat_df['trade_date']= concat_df['trade_date'].astype(int)
        #根据交易日排序，最近的交易日排在前面
        concat_df=concat_df.sort_values(by=['trade_date'],ascending=True,inplace=False)
        #print(concat_df)
        #去除重复数据，一个交易日应该只有一条数据
        concat_df=concat_df.drop_duplicates(subset=['trade_date'],ignore_index=True,inplace=False)
        concat_df=concat_df.tail(int(config.DAY_NUMBER)).reset_index(drop=True)
        concat_df.to_csv(config.USA_STOCK_DATA_DIR+ts_codes_array[0],index=True)
        print('save_us_daily_data for stock:%s success!', ts_codes_array[0])


if __name__ == "__main__":
    pro = ts.pro_api()

    # 获取单一股票行情
    df = pro.us_daily(ts_code='AAPL', start_date='20260209', end_date='20260210')

    print(df)
    #test_data_integrity()
    daily_update()