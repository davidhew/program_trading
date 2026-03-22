'''
美股-市值低于现金及等价物的公司

'''
import logging
from datetime import datetime
import pandas as pd
import config
from us_get_stock_data import us_get_all_stock_data as usa_gd, us_get_all_stock_data
from us_get_finance_data import us_get_balancesheet as us_gb
from us_get_company_info import us_get_company_info
from utility import telegram_messenger
from utility.monitor_strategy import monitor_strategy

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

@monitor_strategy
def compute(date_str:str =None):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')
    stock_list=us_get_company_info.get_us_stock_base_info()['ts_code'].tolist()
    result = list()

    for stock in stock_list:

                market_cap = us_get_company_info.get_market_cap(stock)
                #市值必须大于等于10亿
                if(market_cap < 10*10000*10000):
                    continue
                balancesheet = us_gb.get_balancesheet(stock)
                if(balancesheet is None):
                    print("us_marketcap_lessthancash,warning, %s's balancesheet is None",stock)
                    continue
                if(balancesheet.empty):
                    print("us_marketcap_lessthancash,warning, %s's balancesheet is empty", stock)
                    continue
                cash = balancesheet.iloc[-1]['cashAndCashEquivalents']
                if(market_cap < cash):
                    result.append(stock)


    if(len(result) > 0):
        dict = {'ts_code': result}
        df = pd.DataFrame(dict)

        base_info_df = us_get_company_info.get_us_stock_base_info()
        result_inner = pd.merge(df, base_info_df, on='ts_code', how='inner')
        result_inner = result_inner.sort_values(by=['marketCap'], ascending=False, inplace=False)

        # 带上板块信息
        result_inner_filtered = result_inner[['ts_code', 'sector']]
        content_str = result_inner_filtered.to_string(index=False, justify='center')
        message = f"<b>市值小于现金的公司-{date_str}</b>\n<pre>{content_str}</pre>"
        telegram_messenger.send_message(message)
    else:
        print("no bottoming out stocks")