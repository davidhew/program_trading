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
import logging
import tushare as ts
from get_stock_data import get_stock_base_info as gs
from utility import secrets_config as secrets_config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrest = secrets_config.load_external_config()
ts.set_token(secrest.get('TUSHARE_TOKEN'))
pro = ts.pro_api()
#项目刚启动的时候，初始化股票历史日线数据，目前是获取最近1000天的数据
def init_data():
    stocks = gs.get_china_stock_base_info()['ts_code'].unique()
    today = datetime.now()
    start_date = today-timedelta(days=int(config.DAY_NUMBER))
    start_date_str=start_date.strftime('%Y%m%d')
    end_date_str=today.strftime('%Y%m%d')
    for stock in stocks:
        print(stock)
        update_stock_datas(stock, start_date_str, end_date_str)

#每日运行的任务，理论上正常情况下，只要取当天的日线数据补到历史数据即可;为了提高容错性，取最近5天的数据
def daily_update():
    today = datetime.now()
    for i in range(0, 7):
        start_date = today - timedelta(days=i)
        date_str = start_date.strftime('%Y%m%d')
        df = pro.daily(trade_date=date_str)
        grouped = df.groupby('ts_code')
        for group in grouped.groups:
            save_daily_data(grouped.get_group(group))

def update_stock_datas(ts_codes, start_date, end_date):

    df = pro.daily(ts_code=ts_codes, start_date=start_date, end_date=end_date)
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
        if(os.path.isfile(config.CHINA_STOCK_DATA_DIR+ts_codes_array[0])):
            old_df=pd.read_csv(config.CHINA_STOCK_DATA_DIR+ts_codes_array[0])
        #新老数据合并
        concat_df = pd.concat([df,old_df],axis=0,ignore_index=True)
        #只保留有用的列数据
        concat_df=concat_df[config.CHINA_STOCK_DATA_COLUMN]
        #数据提供方的原因，不同历史时期的数据，trade_date这一列的数据类型有可能是不一致的
        concat_df['trade_date']= concat_df['trade_date'].astype(int)
        #根据交易日排序，最近的交易日排在后面；这样才是遵守pandas的规则
        concat_df=concat_df.sort_values(by=['trade_date'],ascending=True,inplace=False)
        #print(concat_df)
        #去除重复数据，一个交易日应该只有一条数据
        concat_df=concat_df.drop_duplicates(subset=['trade_date'],ignore_index=True,inplace=False)
        concat_df=concat_df.tail(int(config.DAY_NUMBER)).reset_index(drop=True)
        concat_df.to_csv(config.CHINA_STOCK_DATA_DIR+ts_codes_array[0],index=True)
        logger.info('save_daily_data for stock:%s success!', ts_codes_array[0])

if __name__ == "__main__":
    # test_data_integrity()
    daily_update()




