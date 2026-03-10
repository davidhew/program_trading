'''
从数据提供方远程获取股票财报信息-资产负债表数据
'''
import datetime
from datetime import timedelta
from datetime import datetime
from pathlib import Path
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
balancesheet_suffix='_balancesheet'
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
        if(should_update_data(stock)):
            print(stock)
            update_stock_cashflow_data(stock)
            # 适当休眠避免触发 API 频率限制 (根据你的账户等级调整)
            time.sleep(random.uniform(0.5, 1.5))

def update_stock_cashflow_data(ts_code:str):

    df = pro.balancesheet(ts_code=ts_code)

    save_cashflow_data(ts_code,df)

def save_cashflow_data(ts_code:str,df:pd.DataFrame):

        df.to_csv(config.CHINA_STOCK_FINANCE_DATA_DIR+ts_code+balancesheet_suffix,index=True)

def should_update_data(ts_code:str):

    if("1"==config.FORCE_GET_CHINA_STOCK_FINANCE_DATA):
        return True

    path = Path(config.CHINA_STOCK_FINANCE_DATA_DIR + ts_code + balancesheet_suffix)
    if (not path.exists() or not path.is_file()):
        return True
    mtime = path.stat().st_mtime
    last_modified_time = datetime.fromtimestamp(mtime)
    now = datetime.now()

    # 3. 判断是否超过 3 个月 (按 90 天计算更为精确)
    if now - last_modified_time > timedelta(days=90):
        return True
    else:
        return False
    return True

def get_balancesheet_data(ts_code):
    path = Path(config.CHINA_STOCK_FINANCE_DATA_DIR+ts_code+balancesheet_suffix)
    if not path.exists() or not path.is_file():
        logger.error("%s stock data balance sheet file not exist! pls check reason",ts_code)
    return pd.read_csv(path.resolve())

if __name__ == "__main__":
    # test_data_integrity()
    update_data()




