'''
获取公司的现金流量表
'''
import random

import requests
import pandas as pd
import time

from requests.adapters import HTTPAdapter

import config
import logging

from utility import secrets_config as secrets_config
from utility.monitor_strategy import monitor_strategy
from us_get_stock_data import us_get_common_stock_list as us_get_common_stock_list
from urllib3.util.retry import Retry
from us_get_finance_data import finance_util

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
fmp_cashflow_json={
    "date": "2025-09-27",
    "symbol": "AAPL",
    "reportedCurrency": "USD",
    "cik": "0000320193",
    "filingDate": "2025-10-31",
    "acceptedDate": "2025-10-31 06:01:26",
    "fiscalYear": "2025",
    "period": "FY",
    "netIncome": 112010000000,
    "depreciationAndAmortization": 11698000000,
    "deferredIncomeTax": 0,
    "stockBasedCompensation": 12863000000,
    "changeInWorkingCapital": -25000000000,
    "accountsReceivables": -6682000000,
    "inventory": 1400000000,
    "accountsPayables": 902000000,
    "otherWorkingCapital": -20620000000,
    "otherNonCashItems": -89000000,
    "netCashProvidedByOperatingActivities": 111482000000,
    "investmentsInPropertyPlantAndEquipment": -12715000000,
    "acquisitionsNet": 0,
    "purchasesOfInvestments": -24407000000,
    "salesMaturitiesOfInvestments": 53797000000,
    "otherInvestingActivities": -1480000000,
    "netCashProvidedByInvestingActivities": 15195000000,
    "netDebtIssuance": -8483000000,
    "longTermNetDebtIssuance": -6451000000,
    "shortTermNetDebtIssuance": -2032000000,
    "netStockIssuance": -90711000000,
    "netCommonStockIssuance": -90711000000,
    "commonStockIssuance": 0,
    "commonStockRepurchased": -90711000000,
    "netPreferredStockIssuance": 0,
    "netDividendsPaid": -15421000000,
    "commonDividendsPaid": -15421000000,
    "preferredDividendsPaid": 0,
    "otherFinancingActivities": -6071000000,
    "netCashProvidedByFinancingActivities": -120686000000,
    "effectOfForexChangesOnCash": 0,
    "netChangeInCash": 5991000000,
    "cashAtEndOfPeriod": 35934000000,
    "cashAtBeginningOfPeriod": 29943000000,
    "operatingCashFlow": 111482000000,
    "capitalExpenditure": -12715000000,
    "freeCashFlow": 98767000000,
    "incomeTaxesPaid": 43369000000,
    "interestPaid": 0
}
STANDARD_FIELDS = set(fmp_cashflow_json.keys())

pre_columns = [
    "fiscalYear",
    "period",
    "feeCashFlow"

]

columns = pre_columns + list(STANDARD_FIELDS-set(pre_columns))

def check_data_format(new_data):
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
    将 FMP 现金流量表 JSON 数据映射为中文业务解释--便于人阅读理解，程序本身没有使用这段代码
    """
mapping = {
    # 基础信息
    "date": "财报截止日期",
    "symbol": "股票代码",
    "reportedCurrency": "报表币种",
    "cik": "美国证监会中央索引号",
    "filingDate": "文件提交日期",
    "acceptedDate": "文件审核通过时间",
    "fiscalYear": "财年",
    "period": "报告期（FY=财年，Q1/Q2/Q3/Q4=季度）",

    # 净利润与非现金调整项
    "netIncome": "净利润",
    "depreciationAndAmortization": "折旧与摊销（非现金支出）",
    "deferredIncomeTax": "递延所得税（非现金调整项）",
    "stockBasedCompensation": "股权激励费用（非现金支出）",

    # 营运资金变动
    "changeInWorkingCapital": "营运资金变动净额",
    "accountsReceivables": "应收账款变动（负数=应收增加，正数=应收减少）",
    "inventory": "存货变动（负数=存货增加，正数=存货减少）",
    "accountsPayables": "应付账款变动（负数=应付减少，正数=应付增加）",
    "otherWorkingCapital": "其他营运资金变动",
    "otherNonCashItems": "其他非现金项目",

    # 经营活动现金流
    "netCashProvidedByOperatingActivities": "经营活动产生的现金流量净额",

    # 投资活动现金流
    "investmentsInPropertyPlantAndEquipment": "固定资产/厂房/设备投资支出（资本开支）",
    "acquisitionsNet": "收购业务净支出（净额）",
    "purchasesOfInvestments": "投资购买支出",
    "salesMaturitiesOfInvestments": "投资出售/到期收回金额",
    "otherInvestingActivities": "其他投资活动现金流",
    "netCashProvidedByInvestingActivities": "投资活动产生的现金流量净额",

    # 融资活动-债务相关
    "netDebtIssuance": "债务发行净额（负数=偿还债务，正数=新增债务）",
    "longTermNetDebtIssuance": "长期债务发行净额",
    "shortTermNetDebtIssuance": "短期债务发行净额",

    # 融资活动-股票相关
    "netStockIssuance": "股票发行净额（负数=回购/分红，正数=增发）",
    "netCommonStockIssuance": "普通股发行净额",
    "commonStockIssuance": "普通股发行金额",
    "commonStockRepurchased": "普通股回购支出",
    "netPreferredStockIssuance": "优先股发行净额",

    # 融资活动-股息相关
    "netDividendsPaid": "已支付股息净额",
    "commonDividendsPaid": "普通股股息支付额",
    "preferredDividendsPaid": "优先股股息支付额",

    # 融资活动-其他
    "otherFinancingActivities": "其他融资活动现金流",
    "netCashProvidedByFinancingActivities": "融资活动产生的现金流量净额",

    # 汇率与现金变动
    "effectOfForexChangesOnCash": "汇率变动对现金的影响",
    "netChangeInCash": "现金及等价物净增加额",
    "cashAtEndOfPeriod": "期末现金及现金等价物",
    "cashAtBeginningOfPeriod": "期初现金及现金等价物",

    # 衍生现金流指标
    "operatingCashFlow": "经营活动现金流（同经营净额）",
    "capitalExpenditure": "资本支出（即固定资产投资支出）",
    "freeCashFlow": "自由现金流（经营现金流-资本支出）",
    "incomeTaxesPaid": "实际支付的所得税",
    "interestPaid": "实际支付的利息"
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
        do_get_complete_cashflow_statment(symbol_list[i])
        if(i % 100 == 0 and i != 0):
            logger.info("get_finance:cashflow_statement:"+str(i/len(symbol_list)))


#年报和季报都获取，然后合并在一起
def do_get_complete_cashflow_statment(ts_code):
    file_path=config.USA_STOCK_FINANCE_DATA_DIR+"/cashflow/"+str(ts_code)
    empty_df = pd.DataFrame()
    if(finance_util.should_update_data(file_path,0)):
        df = do_get_cashflow_statment(ts_code)
        # 保存一个空白文件，这样可以避免后续重复去远端获取
        if (df is None or df.empty):
            empty_df.to_csv(file_path,index=False)
            return
        quarter_df = do_get_cashflow_statment(ts_code, "quarter")
        if (quarter_df is not None and not quarter_df.empty):
            df = pd.concat([quarter_df,df],axis=0,ignore_index=True)
        df = df.sort_values(by=['filingDate', 'period'], ascending=[True, False], inplace=False)
        df.to_csv(file_path,index=False)
        return df



@monitor_strategy
def do_get_cashflow_statment(ts_code:str,period:str="annual"):

        # 默认是查询年报
        url = f"https://financialmodelingprep.com/stable/cash-flow-statement?symbol={ts_code}"+"&limit=1000"
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
                        check_data_format(row)
                        new_row_df = pd.DataFrame([row])
                        df = pd.concat([df,new_row_df],axis=0,ignore_index=True)
                    return df

                else:
                    logger.error(f"do_get_cashflow_statment 失败，ts_code:{ts_code}，获取到的内容为空")
            logger.error(f"do_get_cashflow_statment 失败，ts_code:{ts_code}，状态码: {response.status_code}")
        except Exception as e:
            print(f"do_get_cashflow_statment,获取 {ts_code} 失败: {e}")
            return {}


        # 适当休眠避免触发 API 频率限制 (根据你的账户等级调整)
        time.sleep(random.uniform(0.1, 0.3))




if __name__ == "__main__":
    do_get_complete_cashflow_statment('AAPL')