'''
以定时任务的方式运行相关动作和策略
'''
import schedule
import time
import datetime
from datetime import timedelta
from datetime import datetime

from us_get_company_info import us_get_company_info

from get_stock_data import save_daily_data as sd
from select_stock_strategy import one_year_highest as one_year_highest
from select_stock_strategy import momentum as momentum
from us_get_stock_data import us_save_daily_data as usa_save_daily_data
from us_get_stock_data import us_get_common_stock_list as us_get_common_stock_list
from select_stock_strategy import jianfang_final as jf
from us_select_stock_strategy import us_momentum as us_momentum
from us_select_stock_strategy import us_price_below_MA200
from us_select_stock_strategy import us_vip_stocks_rsi as us_vip_stocks_rsi

from us_select_stock_strategy import us_one_year_highest as us_one_year_highest
from utility.logger_config import setup_logging


from us_get_finance_data import us_get_income
from us_get_finance_data import us_get_cashflow
from us_get_finance_data import us_get_balancesheet

setup_logging()

def scheduled_china_stock_job():
    sd.daily_update()
    momentum.compute()
    one_year_highest.compute()
    jf.compute()

def scheduled_us_stock_job():
    ##处理美股和中国的时差
    today = datetime.now()
    start_date = today - timedelta(1)
    date_str = start_date.strftime('%Y%m%d')

    usa_save_daily_data.daily_update()
    us_momentum.compute(date_str)
    us_momentum.compute(date_str,3)
    us_one_year_highest.compute(date_str)
    us_vip_stocks_rsi.compute(date_str)

def scheduled_us_stock_finance_refresh_job():
    us_get_income.batch_get()
    us_get_cashflow.batch_get()
    us_get_balancesheet.batch_get()
'''
每周更新一次的数据：
1.美股公司的市值
2.美股公司的股票列表（主要是去除OTC等交易所的列表，保留纳斯达克，纽交所等核心交易所的股票列表）
'''
def scheduled_us_stock_refresh_weekly():
    us_get_company_info.batch_refresh_company_info()
    us_get_common_stock_list.do_get_stock_list()


def scheduled_us_stock_price_below_MA200_job():
    ##处理美股和中国的时差
    today = datetime.now()
    start_date = today - timedelta(1)
    date_str = start_date.strftime('%Y%m%d')
    us_price_below_MA200.compute(date_str)

china_stock_workdays = [
    schedule.every().monday,
    schedule.every().tuesday,
    schedule.every().wednesday,
    schedule.every().thursday,
    schedule.every().friday
]

#有时差
us_stock_workdays = [
    schedule.every().tuesday,
    schedule.every().wednesday,
    schedule.every().thursday,
    schedule.every().friday,
    schedule.every().saturday

]
print("jobStarter")
for day in china_stock_workdays:
    day.at("16:05").do(scheduled_china_stock_job)

for day in us_stock_workdays:
    day.at("08:13").do(scheduled_us_stock_job)

#每个礼拜六，获取美股公司的最新市值
schedule.every().saturday.at("08:19").do(scheduled_us_stock_refresh_weekly)

#每个礼拜六，获取美股公司收盘价低于200均线的公司
schedule.every().saturday.at("08:03").do(scheduled_us_stock_price_below_MA200_job)

#每个礼拜天，更新美股财报数据
schedule.every().sunday.at("08:19").do(scheduled_us_stock_finance_refresh_job)



while True:
    schedule.run_pending()
    time.sleep(60)