'''
以定时任务的方式运行相关动作和策略
'''
import schedule
import time
import config
import datetime
from datetime import timedelta
from datetime import datetime

from us_get_company_info import us_get_company_info
# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。
from get_stock_data import save_daily_data as sd
from select_stock_strategy import one_year_highest as one_year_highest
from select_stock_strategy import momentum as momentum
from us_get_stock_data import us_save_daily_data as usa_save_daily_data
from select_stock_strategy import jianfang_final as jf
from us_select_stock_strategy import us_momentum as us_momentum

from us_select_stock_strategy import us_one_year_highest as us_one_year_highest
from utility.logger_config import setup_logging
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

def scheduled_us_stock_refresh_job():
    us_get_company_info.batch_refresh_company_info()

schedule.every().day.at("07:30").do(scheduled_us_stock_job)
schedule.every().day.at("16:05").do(scheduled_china_stock_job)
schedule.every().day.at("09:25").do(scheduled_us_stock_refresh_job())

while True:
    schedule.run_pending()
    time.sleep(60)