'''

美股上低accruals的公司

accrual=accounting earnings（这里使用净利润） - cashflow

这个值越低，说明利润的质量越高
'''

import pandas as pd
import pandas_ta as ta
from datetime import datetime
from us_get_company_info import us_get_company_info
from us_get_stock_data import us_get_all_stock_data as usa_gd
from utility.monitor_strategy import monitor_strategy
from utility import im_messenger
from us_get_finance_data import us_get_income
from us_get_finance_data import us_get_cashflow
import config
import logging
logger = logging.getLogger(__name__) # 使用 __name__ 可以知道是哪个文件打印的日志



@monitor_strategy
def compute():


    stock_list = list()
    for batch in usa_gd.get_stock_data_batches():

        for stock in batch:
            #一年认为是252个交易日，然后再用最后一个交易日去和这252个交易日价格相比，所以总共需要253个
            #希望对上市一年以上的公司进行筛选，有些上市时间太短的公司，波动性非常大
            if(len(stock)<253):
                #print("get_one_year_highest, %s's data less than one year!",stock.iloc[0]['ts_code'])
                continue
            else:
                ts_code=stock.iloc[0]['ts_code']

                market_cap = us_get_company_info.get_market_cap(ts_code)
                # 市值必须大于等于10亿
                if (market_cap < 10 * 10000 * 10000):
                    continue

                cashflow_df = us_get_cashflow.get_cashflow_df(ts_code)
                income_df = us_get_income.get_income(ts_code)
                #确保两张表的时间周期是对齐的
                if(cashflow_df.iloc[-1]['fiscalYear']==income_df.iloc[-1]['fiscalYear'] and cashflow_df.iloc[-1]['period']==income_df.iloc[-1]['period']):
                    if(cashflow_df.iloc[-1]['freeCashFlow']<=0):
                        continue
                    if(income_df.iloc[-1]['netIncome']<=0):
                        continue
                    #low的不够多
                    if(income_df.iloc[-1]['netIncome']/cashflow_df.iloc[-1]['freeCashFlow']>0.9):
                        continue
                    stock_list.append(ts_code)

    if (len(stock_list) > 0):
        date_str = datetime.now().strftime('%Y%m%d')
        dict = {'ts_code': stock_list}
        df = pd.DataFrame(dict)
        df.to_csv(config.USA_STOCK_STRATEGY_RESULT_DIR + 'low_accrual_companys_' + date_str + '.csv', index=False)







