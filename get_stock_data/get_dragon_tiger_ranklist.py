'''
获取龙虎榜每日明细数据
'''

import datetime
import sys
import os.path
import time
from datetime import timedelta
from datetime import datetime

import config

import pandas as pd
import logging
import tushare as ts
from utility import secrets_config as secrets_config
from get_stock_data import get_stock_base_info as gs

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrest = secrets_config.load_external_config()
ts.set_token(secrest.get('TUSHARE_TOKEN'))

pro = ts.pro_api()


#项目刚启动的时候，初始化股票历史日线数据，目前是获取最近半年的龙虎榜数据
def init_dragon_tiger_ranklist():
    today = datetime.now()
    for i in range(0,config.DRAGON_TIGER_RANK_LIST_DAY_NUMBER):
        trade_date = today - timedelta(days=i)
        trade_date_str = trade_date.strftime('%Y%m%d')
        update_daily_dragon_tiger_ranklist(trade_date_str)
        #频率不能太快，一分钟最多200次调用，所以控制一下
        time.sleep(0.5)



def daily_update_tiger_ranklist():
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    update_daily_dragon_tiger_ranklist(date_str)

def update_daily_dragon_tiger_ranklist(trade_date_str):
    df = pro.top_list(trade_date=trade_date_str)
    old_df = pd.DataFrame()
    # 该股票已经保留了一些历史数据，需要取出来进行合并
    if (os.path.isfile(config.CHINA_STOCK_DIR + "/"+config.STOCK_DRAGON_TIGER_RANK_LIST_FILE)):
        old_df = pd.read_csv(config.CHINA_STOCK_DIR + "/" + config.STOCK_DRAGON_TIGER_RANK_LIST_FILE)

    #如果获取到的数据为空，则不需要做任何事情
    if(len(df)<=0):
        return
    df=df[config.CHINA_DRAGON_TIGER_RANK_LIST_COLUMN]
    concat_df = pd.concat([df, old_df], axis=0, ignore_index=True)
    concat_df = concat_df[config.CHINA_DRAGON_TIGER_RANK_LIST_COLUMN]
    print("concat_df size:%d", len(concat_df))

    # 数据提供方的原因，不同历史时期的数据，trade_date这一列的数据类型有可能是不一致的
    concat_df['trade_date'] = concat_df['trade_date'].astype(int)
    # 根据交易日排序，最近的交易日排在后面
    concat_df = concat_df.sort_values(by=['trade_date'], ascending=True, inplace=False)
    # print(concat_df)
    #print("df size:%d",len(df))
    # 去除重复数据，一个交易日应该只有一条数据q
    #print("before dropduplicates, rows:%d", len(concat_df))
    concat_df = concat_df.drop_duplicates(subset=['trade_date','ts_code'], ignore_index=True, inplace=False)
    #print("after dropduplicates, rows:%d", len(concat_df))
    today = datetime.now()
    days_limit = today-timedelta(days=config.DAY_NUMBER)
    days_limit_str = days_limit.strftime('%Y%m%d')
    concat_df = concat_df[concat_df['trade_date'] >= int(days_limit_str)]
    concat_df.to_csv(config.CHINA_STOCK_DIR + "/" + config.STOCK_DRAGON_TIGER_RANK_LIST_FILE, index=True)
    logger.info('save trade_date:%s daily_dragon_tiger_ranklist success!', trade_date_str)

def get_all_draong_tiger_ranklist():
    return pd.read_csv(config.CHINA_STOCK_DIR+"/"+config.STOCK_DRAGON_TIGER_RANK_LIST_FILE)


'''
    获取特定股票所有的龙虎榜历史记录
    Args:
        st_code:需要获取的股票代码，比如“688270.SH”
        all_df:目前存储的历史上所有的龙虎榜记录（注意，必须包含最近一个交易日的，否则可能逻辑不正确）       
'''
def get_stock_dragon_tiger_ranklist_records(st_code:str,all_df:pd.DataFrame)->pd.DataFrame:
    df = all_df[all_df['ts_code'] == st_code]
    #确保是按照时间升序排序
    df = df.sort_values(by=['trade_date'], ascending=True, inplace=False)
    return df

'''
    判断该股票的上一次进入龙虎榜是不是半年以前
    Args:
        st_code:需要获取的股票代码，比如“688270.SH”
        current_date:当前交易日，该股票上龙虎榜的日期
        df:存放了该股票最近1000天上龙虎榜的历史记录
'''
def is_pre_record_before_than_half_year(st_code:str,current_date:str,df:pd.DataFrame)->bool:
    if(len(df)==0):
        logger.error("check stock:%s  is_pre_record_before_than_half_year occurs error, the dataframe shouldn't be empty!", st_code)
        return False
    matched_indices = df.index[df['trade_date'] == int(current_date)].tolist()
    if len(matched_indices) == 0:
        return False
    row_idx = matched_indices[0]
    # 检查第一条记录的内容是否正确
    if (df.iloc[row_idx]['trade_date'] != int(current_date) or df.iloc[row_idx]['ts_code'] != st_code):
        logger.error(
            "check stock:%s,trade_date:%s is_pre_record_before_than_half_year occurs error,the dataframe's content is wrong!,%s,%s",
            st_code, current_date)
        return False

    if(len(df)==1):
        return True

    if(len(df)>1):
        #上一次该股票进入龙虎榜的信息
        row2_data = df.iloc[row_idx-1]
        pre_trade_date = str(row2_data['trade_date'])
        c_date = datetime.strptime(current_date, '%Y%m%d')
        pre_date = datetime.strptime(pre_trade_date, '%Y%m%d')
        diff_days = abs((c_date - pre_date).days)
        return diff_days>=180
    return False


