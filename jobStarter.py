'''
以定时任务的方式运行相关动作和策略
'''
import schedule
import time
import config
# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。
from get_stock_data import save_daily_data as sd
from select_stock_strategy import one_year_highest as one_year_highest
from select_stock_strategy import momentum as momentum
from us_get_stock_data import us_get_stock_base_info as usa_get_stock_base_info
from us_get_stock_data import us_save_daily_data as usa_save_daily_data
from select_stock_strategy import jianfang_final as jf
from select_stock_strategy import new_dragon_tiger_stock as new_dt_stock
from us_select_stock_strategy import us_one_year_highest as usa_one_year_highest
from select_stock_strategy import low_level_start as ll_start
from select_stock_strategy import cross_MA120
from get_stock_data import get_dragon_tiger_ranklist as gdtr
from utility import date_utility as du
import logging
logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

def scheduled_job():
    sd.daily_update()
    momentum.compute()
    one_year_highest.compute()
    jf.compute()

schedule.every().day.at("19:30").do(scheduled_job)

while True:
    schedule.run_pending()
    time.sleep(60)