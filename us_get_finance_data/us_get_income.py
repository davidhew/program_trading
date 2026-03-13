'''
获取公司的收入报表
'''
import random

import requests
import pandas as pd
import time

from requests.adapters import HTTPAdapter
from pathlib import Path
import datetime
from datetime import timedelta
from datetime import datetime

import config
import logging

from us_get_finance_data import finance_util

from utility import secrets_config as secrets_config
from utility.monitor_strategy import monitor_strategy
from us_get_stock_data import us_get_common_stock_list as us_get_common_stock_list
from urllib3.util.retry import Retry

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrets = secrets_config.load_external_config()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "apikey": secrets.get('PMF_KEY')
}

'''
20260312时fmp返回的数据格式
'''
fmp_income_json={
    "date": "2025-09-27",
    "symbol": "AAPL",
    "reportedCurrency": "USD",
    "cik": "0000320193",
    "filingDate": "2025-10-31",
    "acceptedDate": "2025-10-31 06:01:26",
    "fiscalYear": "2025",
    "period": "FY",
    "revenue": 416161000000,
    "costOfRevenue": 220960000000,
    "grossProfit": 195201000000,
    "researchAndDevelopmentExpenses": 34550000000,
    "generalAndAdministrativeExpenses": 8077000000,
    "sellingAndMarketingExpenses": 19524000000,
    "sellingGeneralAndAdministrativeExpenses": 27601000000,
    "otherExpenses": 0,
    "operatingExpenses": 62151000000,
    "costAndExpenses": 283111000000,
    "netInterestIncome": 0,
    "interestIncome": 0,
    "interestExpense": 0,
    "depreciationAndAmortization": 11698000000,
    "ebitda": 144427000000,
    "ebit": 132729000000,
    "nonOperatingIncomeExcludingInterest": 321000000,
    "operatingIncome": 133050000000,
    "totalOtherIncomeExpensesNet": -321000000,
    "incomeBeforeTax": 132729000000,
    "incomeTaxExpense": 20719000000,
    "netIncomeFromContinuingOperations": 112010000000,
    "netIncomeFromDiscontinuedOperations": 0,
    "otherAdjustmentsToNetIncome": 0,
    "netIncome": 112010000000,
    "netIncomeDeductions": 0,
    "bottomLineNetIncome": 112010000000,
    "eps": 7.49,
    "epsDiluted": 7.46,
    "weightedAverageShsOut": 14948500000,
    "weightedAverageShsOutDil": 15004697000
}
STANDARD_FIELDS = set(fmp_income_json.keys())

pre_columns = [
    "fiscalYear",
    "period",
    "revenue",
    "costOfRevenue"
]

columns = pre_columns + list(STANDARD_FIELDS-set(pre_columns))

def check_income_data(new_data):
    """
    校验并插入新数据，字段不符则抛出异常
    """
    new_fields = set(new_data.keys())

    # 计算差异
    missing_fields = STANDARD_FIELDS - new_fields
    extra_fields = new_fields - STANDARD_FIELDS

    # 2. 严格校验逻辑
    if missing_fields or extra_fields:
        error_msg = "财报字段匹配失败！\n"
        if missing_fields:
            error_msg += f"缺少字段: {missing_fields}\n"
        if extra_fields:
            error_msg += f"多余字段: {extra_fields}\n"
        raise ValueError(error_msg)  # 触发报错并停止程序


"""
    将 FMP 利润表 JSON 数据映射为中文业务解释--便于人阅读理解，程序本身没有使用这段代码
    """
mapping = {
    # 核心业绩指标
    "date": "财报截止日期",
    "symbol": "股票代码",
    "reportedCurrency": "报表币种",
    "fiscalYear": "财年",
    "revenue": "营业总收入",
    "costOfRevenue": "营业成本",
    "grossProfit": "毛利(revenue-costOfRevenue)",

    # 经营开支
    "researchAndDevelopmentExpenses": "研发费用(A)",
    "generalAndAdministrativeExpenses": "管理费用(B)",
    "sellingAndMarketingExpenses": "销售费用(C)",
    "sellingGeneralAndAdministrativeExpenses": "管理及销售费用(D,D=B+C)",
    "operatingExpenses": "期间费用合计(E,E=A+B+C)",
    "costAndExpenses": "期间成本和费用的和(F,F=营业成本+E)",


    # 盈利能力
    "depreciationAndAmortization": "折旧与摊销--在美股，一般这一部分都已经记入到各种费用里去了",
    "ebitda": "税息折旧及摊销前利润(EBITDA)",
    "ebit": "息税前利润(EBIT)",
    "operatingIncome":"营业利润(G,G=revenue-costOfRevenue-operatingExpenses)",

    # 利润与税收
    "totalOtherIncomeExpensesNet": "其他损益净额（这一项不能太大，太大有可能在操纵财务报表）",
    "incomeBeforeTax": "利润总额",
    "incomeTaxExpense": "所得税费用",
    "netIncome": "净利润",

    # 每股指标
    "eps": "基本每股收益",
    "epsDiluted": "稀释每股收益",
    "weightedAverageShsOut": "流通股本",
    "weightedAverageShsOutDil": "稀释后总股本"
}


def get_session_with_retries():
    session = requests.Session()
    # 定义重试策略
    retries = Retry(
        total=5,              # 总重试次数
        backoff_factor=1,     # 重试间隔指数级增加 (1s, 2s, 4s...)
        status_forcelist=[500, 502, 503, 504], # 遇到这些状态码也重试
        raise_on_status=False
    )
    # 将重试策略应用到 http 和 https 请求
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def batch_get():

    df_stocks = us_get_common_stock_list.get_common_stock_list()
    symbol_list = df_stocks['ts_code'].tolist()

    print(f"开始获取数据，共计 {len(symbol_list)} 个股票...")


    for i in range(0, len(symbol_list)):
        do_get_complete_income_statment(symbol_list[i])
        if(i % 100 == 0 and i != 0):
            logger.info("get_finance:income_statement:"+str(i/len(symbol_list)))


#年报和季报都获取，然后合并在一起
def do_get_complete_income_statment(ts_code):
    file_path=config.USA_STOCK_FINANCE_DATA_DIR+"/income/"+ts_code
    if(finance_util.should_update_data(file_path,90)):
        df = do_get_income_statment(ts_code)
        quarter_df=do_get_income_statment(ts_code,"quarter")
        df = pd.concat([quarter_df,df],axis=0,ignore_index=True)
        df = df.sort_values(by=['filingDate', 'period'], ascending=[True, False], inplace=False)
        df.to_csv(file_path,index=False)
        return df



@monitor_strategy
def do_get_income_statment(ts_code:str,period:str="annual"):

        # 默认是查询年报
        url = f"https://financialmodelingprep.com/stable/income-statement?symbol={ts_code}"+"&limit=1000"
        if period == "quarter":
            url += f"&period=quarter"

        try:
            session = get_session_with_retries()

            response = session.get(url,headers=headers,timeout=10)
            if response.status_code == 200:
                data = response.json()
                if(len(data) > 0):
                    df = pd.DataFrame(columns=columns)

                    for row in data:
                        check_income_data(row)
                        new_row_df = pd.DataFrame([row])
                        df = pd.concat([df,new_row_df],axis=0,ignore_index=True)

                    return df

                else:
                    logger.error(f"do_get_income_statment 失败，ts_code:{ts_code}，获取到的内容为空")
            logger.error(f"do_get_income_statment 失败，ts_code:{ts_code}，状态码: {response.status_code}")
        except Exception as e:
            print(f"do_get_income_statment,获取 {ts_code} 失败: {e}")
            return {}


        # 适当休眠避免触发 API 频率限制 (根据你的账户等级调整)
        time.sleep(random.uniform(0.5, 1))

def should_update_data(ts_code:str):

    if("1"==config.FORCE_GET_CHINA_STOCK_FINANCE_DATA):
        return True

    path = Path(config.USA_STOCK_FINANCE_DATA_DIR+"/income/"+ts_code)
    if (not path.exists() or not path.is_file()):
        return True
    mtime = path.stat().st_mtime
    last_modified_time = datetime.fromtimestamp(mtime)
    now = datetime.now()

    # 3. 判断是否超过 3 个月 (按 90 天计算更为精确)
    if now - last_modified_time > timedelta(days=90):
        return True
    else:
        return False
    return True

if __name__ == "__main__":
    do_get_complete_income_statment('AAPL')