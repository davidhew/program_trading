'''
策略：
1.该股票半年内以一次上龙虎榜
2.该股票进入龙虎榜的当天，龙虎榜净买入额大过5000w rmb
2.该股票股价并没有很高（前一天的收盘价，不高于最近一年股票最低收盘价的50%）--防止已经被炒的很高
3.
'''

import pandas as pd
import pandas_ta as ta
from datetime import datetime
from get_stock_data import get_stock_base_info as gd_base_info
from get_stock_data import get_dragon_tiger_ranklist as dragon_tiger
from stock_compute import stock_compute_utility as scu
from utility import telegram_messenger as tm
import logging
from utility import monitor_strategy

import config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

from get_stock_data import get_all_stock_data as gd

@monitor_strategy
def compute(date_str:str =None):

    #如果用户没有指定日期，则取系统当前时间
    if date_str==None:
        date_str=datetime.now().strftime('%Y%m%d')

    rank_list_df = dragon_tiger.get_all_draong_tiger_ranklist()
    #获取指定日期的龙虎榜数据
    today_rank_list_df = rank_list_df[rank_list_df['trade_date'] == int(date_str)]

    if(len(today_rank_list_df)==0):
        logger.info("There is no dragon tiger ranklist for date:%s", date_str)
        return
    df = pd.DataFrame(columns=['name','ts_code','average_price','net_amount','reason'])
    for row in today_rank_list_df.itertuples():
        #不玩债券
        if(row.name.endswith("转债")):
            continue
        #必须是股价涨幅在5%以上
        if(row.pct_change<=5):
            continue
        #龙虎榜净买入额必须大于5kw
        if(row.net_amount<=50000000):
            continue
        stock_dragon_tiger_ranklist = dragon_tiger.get_stock_dragon_tiger_ranklist_records(row.ts_code,rank_list_df)
        #半年之内，第一次上龙虎榜
        if(not dragon_tiger.is_pre_record_before_than_half_year(row.ts_code,str(row.trade_date),stock_dragon_tiger_ranklist)):
            continue
        #进入龙虎榜的前一天的收盘价，不高于最近一年内最低收盘价的50%；防止进入龙虎榜之前股价涨幅已经比较大了
        if(scu.stock_price_too_high(row.ts_code, date_str, 253, 1)):
            continue
        average_price = scu.get_average_price(row.ts_code, date_str)
        #以万为单位
        net_amount = str(int(row.net_amount/10000))+"万"

        df.loc[len(df)] = [row.name,row.ts_code,average_price,net_amount,row.reason]
    if(len(df)>=1):
        df.to_csv(config.STOCK_STRATEGY_RESULT_DIR +"/new_dragon_tiger_ranklist-" + date_str + ".csv", index=True)
        if(int(config.SEND_TELEGRAM)==1):
            # 1. 将 DataFrame 转换为漂亮的字符串（不包含索引）
            # index=False 隐藏索引，justify='left' 左对齐
            table_str = df.to_string(index=False)

            # 2. 构建符合 Telegram 规范的 HTML
            # <b> 加粗替代 <h3>, <pre> 保证表格对齐
            message = f"<b>股价合理-新进龙虎榜-{date_str}</b>\n<pre>{table_str}</pre>"
            tm.send_telegram_message(message)
    logger.info("success:compute:new_dragon_tiger_ranklist:%s finished!",date_str)
