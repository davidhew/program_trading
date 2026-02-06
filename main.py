# 这是一个示例 Python 脚本。
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


def print_hi(name):
   # fileds_to_use=['col_1','col_2']
    #print(type(fileds_to_use))
    #sd.init_data()
    #sd.daily_update()
    #ll_start.compute_low_level_start()
    #gdtr.init_dragon_tiger_ranklist()
    usa_save_daily_data.init_data()

'''
    for i in range(31,-1,-1):
        date_str = str(du.days_befor('20260204',i))
        momentum.compute(date_str)
        one_year_highest.compute(date_str)
        jf.compute(date_str)
        #cross_MA120.compute(date_str)
        #ll_start.compute(date_str)
    #print(date_str)
'''

   #momentum.compute_momentum()
   ##one_year_highest.compute_one_year_highest()
   #jf.compute('20260123')
    #usa_get_stock_base_info.get_usa_stock_base_info()
    #usa_save_daily_data.init_data()
    #usa_save_daily_data.daily_update()
    #usa_one_year_highest.compute_one_year_highest()
'''
    ts.set_token('139f4237cb789761dc43ff216bfb8ddfa2ebdb7c239a50602c1e5dbf')
    pro = ts.pro_api()
    df = pro.daily(ts_code='000001.SZ,600000.SH', start_date='20241219', end_date='20250119')
    grouped = df.groupby('ts_code')
    for group in grouped.groups:
        sd.save_daily_data( grouped.get_group(group))
'''
# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
