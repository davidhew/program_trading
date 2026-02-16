'''
获取公司的市值,所属行业，所属板块的信息
'''
import random

import requests
import pandas as pd
import time

from requests.adapters import HTTPAdapter

import config
import logging
import os.path

from utility import secrets_config as secrets_config
from utility.monitor_strategy import monitor_strategy
from us_get_stock_data import us_get_common_stock_list as us_get_common_stock_list
from datetime import datetime
from urllib3.util.retry import Retry

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrest = secrets_config.load_external_config()

file_name = 'usa_common_stock_list.csv'
out_file_name = 'us_company_info.csv'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "apikey": secrest.get('PMF_KEY')
}

def get_session_with_retries():
    session = requests.Session()
    # 定义重试策略
    retries = Retry(
        total=5,              # 总重试次数
        backoff_factor=1,     # 重试间隔指数级增加 (1s, 2s, 4s...)
        status_forcelist=[500, 502, 503, 504], # 遇到这些状态码也重试
        raise_on_status=False
    )
    # 将重试策略应用到 http 和 https 请求
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_company_info():
    sucess_count=0
    df_old =  pd.DataFrame(columns=['ts_code','marketCap','industry','sector','date'])
    if(os.path.isfile(config.USA_STOCK_DIR+"/"+out_file_name)):
        df_old  = pd.read_csv(config.USA_STOCK_DIR+"/"+out_file_name)
    df_old.set_index("ts_code")


    df_stocks = us_get_common_stock_list.get_common_stock_list()
    symbol_list = df_stocks['ts_code'].tolist()

    results = []

    print(f"开始获取数据，共计 {len(symbol_list)} 个股票...")

    for i in range(0, len(symbol_list)):
        info = do_get_company_info(symbol_list[i])
        #从文件里获取的一些股票代码，其可能是etf，不是公司，获取不到相关数据，这种情况直接忽略即可
        if(len(info)>0):
            results.append(info)
            sucess_count=sucess_count+1
        if(sucess_count%50==0):
            print("sucess_count:",sucess_count)



    df_new = pd.DataFrame(results).set_index("ts_code")
    #加上更新日期列，便于后续排查数据的及时性
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    df_new['date'] = date_str
    # 步骤 B: 使用 update 更新已存在的行
    # 这会直接修改 df_old 中 index 匹配的行，用 df_new 的值覆盖它
    df_old.update(df_new)

    # 步骤 C: 使用 concat 插入不存在的行
    # 找出在 df_new 中但不在 df_old 中的索引 (即 NVDA)
    new_indices = df_new.index.difference(df_old.index)

    if not new_indices.empty:
        df_to_insert = df_new.loc[new_indices]
        df_old = pd.concat([df_old, df_to_insert])

@monitor_strategy
def do_get_company_info(ts_code:str):

        # 2. 调用 FMP 接口 (Company Profile)
        url = f"https://financialmodelingprep.com/stable/profile?symbol={ts_code}"
        try:
            session = get_session_with_retries()

            response = session.get(url,headers=headers,timeout=10)
            if response.status_code == 200:
                data = response.json()
                if(len(data) > 0):
                    result = data[0]
                    # 3. 提取指定字段
                    return{
                            "ts_code": result.get("symbol"),
                            "marketCap": result.get("marketCap"),
                            "industry": result.get("industry"),
                            "sector": result.get("sector")
                        }
                else:
                    return{}
            else:
                logger.error(f"us_get_company_info 失败，ts_code:{ts_code}，状态码: {response.status_code}")
        except Exception as e:
            print(f"us_get_company_info,获取 {ts_code} 失败: {e}")
            return {}


        # 适当休眠避免触发 API 频率限制 (根据你的账户等级调整)
        time.sleep(random.uniform(0.5, 1.5))

if __name__ == "__main__":
    get_company_info()