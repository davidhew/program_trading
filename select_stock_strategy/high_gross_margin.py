'''
高毛利的企业

--先将高毛利的标准设定为毛利高于70%

--费用情况：（下面来自唐朝）
费用率也可以用费用占毛利润的比例来观察，这个角度去除了生产成本的影响。
大体来说，如果费用能够控制在毛利润的30%以内，就算是优秀的企业了；在30%~70%区域，仍然是具有一定竞争优势的企业；
如果费用超过毛利润的70%，通常而言，关注价值不大。
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

    result = pd.DataFrame(columns=['ts_code','name','revenue','oper_cost','sell_exp','fin_exp','admin_exp','rd_exp'])

    for ts_code in stocks:

       profit_data = get_profit_data.get_profit_data(ts_code)
       profit_data.fillna(0, inplace = True)
       if profit_data.empty:
           print(ts_code+":警告：该标的财务数据为空，无法计算毛利率。")
           continue

       revenue = profit_data.iloc[0]['revenue']
       oper_cost = profit_data.iloc[0]['oper_cost']
       sell_exp = profit_data.iloc[0]['sell_exp']
       fin_exp = profit_data.iloc[0]['fin_exp']
       admin_exp = profit_data.iloc[0]['admin_exp']
       rd_exp = profit_data.iloc[0]['rd_exp']

       #净利润
       n_income = profit_data.iloc[0]['n_income']

       total_exp = sell_exp + fin_exp + admin_exp + rd_exp
       gross_profit = revenue - oper_cost

       #需要毛利润和净利润都为正
       if(gross_profit <=0 or n_income <= 0):
           continue
       #费用占毛利润的比例
       exp_percent = total_exp/gross_profit

       #净利润率
       n_income_percent = n_income/revenue

       gross_profit_percent = (revenue- oper_cost)/revenue
       if (gross_profit_percent>=0.7 and exp_percent<0.3 and n_income_percent>=0.1):
           name = gd_base_info.get_name_from_code(ts_code)
           new_row_values = [ts_code, name,revenue,oper_cost,sell_exp,fin_exp,admin_exp,rd_exp]
           result.loc[len(result)] = new_row_values

    print(result.to_string(index=False))





