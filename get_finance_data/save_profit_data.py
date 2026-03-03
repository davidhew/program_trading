'''
从数据提供方远程获取股票财报信息-利润表数据
'''
import datetime
from datetime import timedelta
from datetime import datetime
import time
import random

import config

import pandas as pd
import logging
import tushare as ts
from get_stock_data import get_stock_base_info as gs
from utility import secrets_config as secrets_config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrets = secrets_config.load_external_config()
ts.set_token(secrets.get('TUSHARE_TOKEN'))
pro = ts.pro_api()
#项目刚启动的时候，初始化股票历史财报数据数据，目前是获取最近10年的数据
def update_data():
    stocks = gs.get_china_stock_base_info()['ts_code'].unique()
    today = datetime.now()
    #1. 计算 10 年前的年份
    target_year = today.year - 10
    #2. 构造该年份的 1 月 1 日
    ten_years_ago_jan_1st = datetime(target_year, 1, 1)

    start_date = today-timedelta(days=int(config.DAY_NUMBER))
    start_date_str=ten_years_ago_jan_1st.strftime('%Y%m%d')
    end_date_str=today.strftime('%Y%m%d')
    for stock in stocks:
        print(stock)
        update_stock_profit_data(stock)
        # 适当休眠避免触发 API 频率限制 (根据你的账户等级调整)
        time.sleep(random.uniform(0.5, 1.5))

def update_stock_profit_data(ts_code:str):

    df = pro.income(ts_code=ts_code)

    save_profit_data(ts_code,df)

def save_profit_data(ts_code:str,df:pd.DataFrame):

        df.to_csv(config.CHINA_STOCK_FINANCE_DATA_DIR+ts_code,index=True)


if __name__ == "__main__":
    # test_data_integrity()
    update_data()




