# 这是一个示例 Python 脚本。
import config
# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。
from get_stock_data import save_daily_data as sd
from select_stock_strategy import one_year_highest as one_year_highest
from select_stock_strategy import momentum as momentum
from us_select_stock_strategy import us_one_year_highest as us_one_year_highest
from us_get_stock_data import us_save_daily_data as usa_save_daily_data
from get_finance_data import save_profit_data as profit_data
from select_stock_strategy import jianfang_final as jf
from select_stock_strategy import new_dragon_tiger_stock as new_dt_stock
from us_select_stock_strategy import us_one_year_highest as usa_one_year_highest
from us_select_stock_strategy import us_momentum as us_momentum
from us_select_stock_strategy import us_vip_stocks_rsi as us_vip_stocks_rsi
from us_select_stock_strategy import us_low_accrual_company as us_low_accrual_company
from select_stock_strategy import low_level_start as ll_start
from select_stock_strategy import cross_MA120
from get_stock_data import get_dragon_tiger_ranklist as gdtr
from utility import date_utility as du
from get_finance_data import save_cashflow_data as cf_data
from get_finance_data import save_profit_data as profit_data
from get_finance_data import save_balancesheet_data as bs_data
from select_stock_strategy import high_gross_margin as hg_margin
from select_stock_strategy import tangchao_good_compayn_model as tc_good_company
from utility.logger_config import setup_logging
from us_select_stock_strategy import us_marketcap_lessthancash as us_mc_lessthancash
from us_get_finance_data import us_get_income
from us_get_finance_data import us_get_cashflow
from us_get_finance_data import us_get_balancesheet
from us_select_stock_strategy import us_bottoming_out
from us_select_stock_strategy import us_price_below_MA200
from us_macro_indexs import get_net_liquidity
from us_macro_indexs import get_credit_spread
from database import favorite_stocks
setup_logging()

def print_hi(name):
    #us_get_income.batch_get()
    #us_get_cashflow.batch_get()
    #us_get_balancesheet.batch_get()
    date_str = '20260325'
    #usa_save_daily_data.daily_update()
    #us_momentum.compute(date_str)
    #us_momentum.compute(date_str, 3)
    #us_one_year_highest.compute(date_str)
    #us_mc_lessthancash.compute()
    #us_vip_stocks_rsi.compute()
    #us_low_accrual_company.compute()
    favorite_stocks.test_add_stock()

    #print(type(fileds_to_use))
    #sd.init_data()
    #sd.daily_update()
    #ll_start.compute_low_level_start()
    #gdtr.init_dragon_tiger_ranklist()
    # usa_save_daily_data.init_data()
    #telegram_messenger("测试在docker里发送信息")
    #date_str = '20260303'
    #sd.daily_update()
    #momentum.compute(date_str)
    #one_year_highest.compute(date_str)
    #jf.compute(date_str)
    #momentum.compute()
    #us_momentum.compute('20260227')
    #us_momentum.compute('20260227',3)
    #us_one_year_highest.compute('20260227')

    #cf_data.update_data()
    #bs_data.update_data()
    #profit_data.update_data()
    ##one_year_highest.compute_one_year_highest()
    #date_str='20260305'
    #usa_save_daily_data.daily_update()
    #us_momentum.compute(date_str)
    #us_momentum.compute(date_str, 3)
    #us_one_year_highest.compute(date_str)
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

