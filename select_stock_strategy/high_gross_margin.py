'''
高毛利的企业

--先将高毛利的标准设定为毛利高于70%
'''


import logging
from datetime import datetime
import pandas as pd
import config
from get_stock_data import get_all_stock_data as gd
from get_stock_data import get_stock_base_info as gd_base_info
from get_finance_data import save_profit_data as get_profit_data
from utility import util as ut
from utility.monitor_strategy import monitor_strategy

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

@monitor_strategy
def compute():

    stocks = gd_base_info.get_china_stock_base_info()['ts_code'].tolist()

    result = pd.DataFrame(columns=['ts_code','name'])

    for ts_code in stocks:

       profit_data = get_profit_data.get_profit_data(ts_code)
       if profit_data.empty:
           print(ts_code+":警告：该标的财务数据为空，无法计算毛利率。")
           continue

       gross_profit_percent = profit_data.iloc[0]['revenue']- profit_data.iloc[0]['oper_cost']/profit_data.iloc[0]['revenue']
       if (gross_profit_percent>=0.7):
           name = gd_base_info.get_name_from_code(ts_code)
           new_row_values = [ts_code, name]
           result.loc[len(result)] = new_row_values

    print(result.to_string(index=False))





