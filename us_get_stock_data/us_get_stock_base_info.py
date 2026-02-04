'''
获取A股，港股，美股等股票列表原始信息
这些原始信息获取后，保存在本地，相当于作为种子列表，来获取这些股票每日的交易数据来更新股票的日级别交易历史数据
这个原始信息保存在本地，每个月更新一次即可，不需要频繁更新
'''
import sys
import os.path
import config
import time

import pandas as pd
import logging
import tushare as ts
logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
file_name = 'usa_stock_list.csv'

from utility import secrets_config as secrets_config

pro = ts.pro_api()
def get_usa_stock_base_info():

    if(need_refresh()):
        secrest = secrets_config.load_external_config()
        ts.set_token(secrest.get('TUSHARE_TOKEN'))
        pro = ts.pro_api()
        limit = 2000  # 建议显式设置，通常该接口最大单次限制为2000
        offset = 0
        all_df = pd.DataFrame()

        while True:
            # 抓取当前页数据
            df = pro.us_basic(limit=limit, offset=offset)
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

        all_df.to_csv(config.USA_STOCK_DIR+"/"+file_name)
    return pd.read_csv(config.USA_STOCK_DIR+"/"+file_name)


def need_refresh():
    #不存在文件，则获取一次
    if(not os.path.isfile(config.USA_STOCK_DIR+"/"+file_name)):
        return True
    else:
        current_time=int(time.time())
        print(current_time)
        file_time=int(os.path.getmtime(config.USA_STOCK_DIR+"/"+file_name))
        print(file_time)
        #超过1个月没更新，需要更新一次
        time_elapsed=current_time-file_time
        if(time_elapsed>31*24*3600):
            return True
        else:
            logger.info('stocks base info created:%s days, do not need refresh',time_elapsed)
    return False
