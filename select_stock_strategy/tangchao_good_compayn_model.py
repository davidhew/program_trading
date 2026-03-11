"""
唐朝的好的企业的模型--从现金流角度

（1）经营活动产生的现金流量净额＞净利润>0；
（2）销售商品、提供劳务收到的现金≥营业收人；
（3）投资活动现金流出>投资活动现金流人，且主要是用于扩张，而
非用于维持原有盈利能力；①
（4）现金及现金等价物净增加额>0，可放宽为：排除当年实施的现
金分红因素影响后，现金及现金等价物净增加额>0；
（5）期末现金及现金等价物余额≥有息负债，可放宽为：期末现金及
现金等价物+可迅速变现的金融资产净值＞有息负债。
"""


import logging
import pandas as pd
import config
from get_stock_data import get_stock_base_info as gd_base_info
from get_finance_data import save_profit_data as get_profit_data
from get_finance_data import save_cashflow_data as get_cashflow_data
from get_finance_data import save_balancesheet_data as get_balancesheet_data
from utility.monitor_strategy import monitor_strategy

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

@monitor_strategy
def compute():

    stocks = gd_base_info.get_china_stock_base_info()['ts_code'].tolist()

    result = pd.DataFrame(columns=['ts_code','name'])

    for ts_code in stocks:

       profit_data_df = get_profit_data.get_profit_data(ts_code)
       cashflow_data_df = get_cashflow_data.get_cashflow_data(ts_code)
       balancesheet_data_df = get_balancesheet_data.get_balancesheet_data(ts_code)
       merge_df = pd.merge(profit_data_df,cashflow_data_df,on=['ts_code','end_date'])
       merge_df = pd.merge(merge_df,balancesheet_data_df,on=['ts_code','end_date'])

       merge_df.fillna(0, inplace = True)
       if merge_df.empty:
           print(ts_code+":警告：该标的财务数据为空，无法计算毛利率。")
           continue

       #营业收入
       revenue = merge_df.iloc[0]['revenue']
       #同期的经营活动现金流净额（非常有质量的财务数据）
       n_cashflow_act = merge_df.iloc[0]['n_cashflow_act']

       #销售商品、提供劳务收到的现金
       c_fr_sale_sg = merge_df.iloc[0]['c_fr_sale_sg']

       #净利润
       n_income = merge_df.iloc[0]['n_income']

       #经营活动产生的现金流量净额＞净利润>0；
       if(not(n_cashflow_act >0 and n_income > 0 and n_cashflow_act>n_income)):
           continue

       if(not (c_fr_sale_sg>=revenue)):
           continue
       #投资活动产生的现金流量净额；
       n_cashflow_inv_act = merge_df.iloc[0]['n_cashflow_inv_act']

       #投资活动现金流出>投资活动现金流人
       if(n_cashflow_inv_act > 0):
           continue
       #分配股利、利润或偿付利息支付的现金
       c_pay_dist_dpcp_int_exp = merge_df.iloc[0]['c_pay_dist_dpcp_int_exp']

       #现金及现金等价物净增加额
       n_incr_cash_cash_equ = merge_df.iloc[0]['n_incr_cash_cash_equ']

       #现金及现金等价物净增加额>0，可放宽为：排除当年实施的现金分红因素影响后，现金及现金等价物净增加额>0；
       if(c_pay_dist_dpcp_int_exp+n_incr_cash_cash_equ<0):
           continue

       #期末现金及现金等价物余额
       c_cash_equ_end_period = merge_df.iloc[0]['c_cash_equ_end_period']

       #流动负债合计
       total_cur_liab = merge_df.iloc[0]['total_cur_liab']

       #期末现金及现金等价物余额≥有息负债，可放宽为：期末现金及现金等价物+可迅速变现的金融资产净值＞有息负债。
       #这里修改成期末现金及现金等价物>流动负债
       if (c_cash_equ_end_period < total_cur_liab):
           continue

       name = gd_base_info.get_name_from_code(ts_code)
       new_row_values = [ts_code, name]
       result.loc[len(result)] = new_row_values

    print(result.to_string(index=False))





