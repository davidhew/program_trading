'''
获取公司的资产负债表
'''
import random

import requests
import pandas as pd
import time

from requests.adapters import HTTPAdapter

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
fmp_balancesheet_json={
    "date": "2025-09-27",
    "symbol": "AAPL",
    "reportedCurrency": "USD",
    "cik": "0000320193",
    "filingDate": "2025-10-31",
    "acceptedDate": "2025-10-31 06:01:26",
    "fiscalYear": "2025",
    "period": "FY",
    "cashAndCashEquivalents": 35934000000,
    "shortTermInvestments": 18763000000,
    "cashAndShortTermInvestments": 54697000000,
    "netReceivables": 72957000000,
    "accountsReceivables": 39777000000,
    "otherReceivables": 33180000000,
    "inventory": 5718000000,
    "prepaids": 0,
    "otherCurrentAssets": 14585000000,
    "totalCurrentAssets": 147957000000,
    "propertyPlantEquipmentNet": 49834000000,
    "goodwill": 0,
    "intangibleAssets": 0,
    "goodwillAndIntangibleAssets": 0,
    "longTermInvestments": 77723000000,
    "taxAssets": 20777000000,
    "otherNonCurrentAssets": 62950000000,
    "totalNonCurrentAssets": 211284000000,
    "otherAssets": 0,
    "totalAssets": 359241000000,
    "totalPayables": 82876000000,
    "accountPayables": 69860000000,
    "otherPayables": 13016000000,
    "accruedExpenses": 8919000000,
    "shortTermDebt": 20329000000,
    "capitalLeaseObligationsCurrent": 2117000000,
    "taxPayables": 0,
    "deferredRevenue": 9055000000,
    "otherCurrentLiabilities": 42335000000,
    "totalCurrentLiabilities": 165631000000,
    "longTermDebt": 78328000000,
    "capitalLeaseObligationsNonCurrent": 11603000000,
    "deferredRevenueNonCurrent": 0,
    "deferredTaxLiabilitiesNonCurrent": 0,
    "otherNonCurrentLiabilities": 29946000000,
    "totalNonCurrentLiabilities": 119877000000,
    "otherLiabilities": 0,
    "capitalLeaseObligations": 13720000000,
    "totalLiabilities": 285508000000,
    "treasuryStock": 0,
    "preferredStock": 0,
    "commonStock": 93568000000,
    "retainedEarnings": -14264000000,
    "additionalPaidInCapital": 0,
    "accumulatedOtherComprehensiveIncomeLoss": -5571000000,
    "otherTotalStockholdersEquity": 0,
    "totalStockholdersEquity": 73733000000,
    "totalEquity": 73733000000,
    "minorityInterest": 0,
    "totalLiabilitiesAndTotalEquity": 359241000000,
    "totalInvestments": 96486000000,
    "totalDebt": 112377000000,
    "netDebt": 76443000000
}
STANDARD_FIELDS = set(fmp_balancesheet_json.keys())

'''
 将 FMP 资产负债表 JSON 数据映射为中文业务解释--便于人阅读理解，程序本身没有使用这段代码
'''
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

    # 流动资产
    "cashAndCashEquivalents": "现金及现金等价物",
    "shortTermInvestments": "短期投资",
    "cashAndShortTermInvestments": "现金及短期投资合计",
    "netReceivables": "应收账款净额",
    "accountsReceivables": "应收账款",
    "otherReceivables": "其他应收款",
    "inventory": "存货",
    "prepaids": "预付款项",
    "otherCurrentAssets": "其他流动资产",
    "totalCurrentAssets": "流动资产合计",

    # 非流动资产
    "propertyPlantEquipmentNet": "固定资产净额（厂房/设备等，扣除折旧）",
    "goodwill": "商誉",
    "intangibleAssets": "无形资产",
    "goodwillAndIntangibleAssets": "商誉及无形资产合计",
    "longTermInvestments": "长期投资",
    "taxAssets": "税务资产",
    "otherNonCurrentAssets": "其他非流动资产",
    "totalNonCurrentAssets": "非流动资产合计",
    "otherAssets": "其他资产",
    "totalAssets": "资产总计",

    # 流动负债
    "totalPayables": "应付款项总计",
    "accountPayables": "应付账款",
    "otherPayables": "其他应付款",
    "accruedExpenses": "应计费用",
    "shortTermDebt": "短期债务",
    "capitalLeaseObligationsCurrent": "一年内到期的融资租赁负债",
    "taxPayables": "应付税费",
    "deferredRevenue": "递延收入（预收款项）",
    "otherCurrentLiabilities": "其他流动负债",
    "totalCurrentLiabilities": "流动负债合计",

    # 非流动负债
    "longTermDebt": "长期债务",
    "capitalLeaseObligationsNonCurrent": "长期融资租赁负债",
    "deferredRevenueNonCurrent": "非当期递延收入",
    "deferredTaxLiabilitiesNonCurrent": "非当期递延所得税负债",
    "otherNonCurrentLiabilities": "其他非流动负债",
    "totalNonCurrentLiabilities": "非流动负债合计",
    "otherLiabilities": "其他负债",
    "capitalLeaseObligations": "资本租赁负债总计",
    "totalLiabilities": "负债总计",

    # 股东权益
    "treasuryStock": "库存股(公司回购但未注销的股票)",
    "preferredStock": "优先股",
    "commonStock": "普通股",
    "retainedEarnings": "留存收益",
    "additionalPaidInCapital": "资本公积",
    "accumulatedOtherComprehensiveIncomeLoss": "其他综合收益累计额（损失为负）",
    "otherTotalStockholdersEquity": "其他股东权益",
    "totalStockholdersEquity": "股东权益总计",
    "totalEquity": "权益总计",
    "minorityInterest": "少数股东权益",
    "totalLiabilitiesAndTotalEquity": "负债及股东权益总计（应等于资产总计）",

    # 衍生指标
    "totalInvestments": "投资总额（短期+长期投资）",
    "totalDebt": "债务总额（短期+长期债务）",
    "netDebt": "净债务（债务总额-现金及现金等价物）"
}
pre_columns = [
    "fiscalYear",
    "period",
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
        do_get_complete_balancesheet_statment(symbol_list[i])
        if(i % 100 == 0 and i != 0):
            logger.info("get_finance:balancesheet_statement:"+str(i/len(symbol_list)))


#年报和季报都获取，然后合并在一起
def do_get_complete_balancesheet_statment(ts_code):
    file_path=config.USA_STOCK_FINANCE_DATA_DIR+"/balancesheet/"+str(ts_code)
    empty_df = pd.DataFrame()
    if(finance_util.should_update_data(file_path,90)):

        df = do_get_balancesheet_statment(ts_code)
        #可能标的刚上市还没有财报；或者标的是一个ETF没有财报
        # 保存一个空白文件，这样可以避免后续重复去远端获取
        if (df is None or df.empty):
            empty_df.to_csv(file_path, index=False)
            return
        quarter_df=do_get_balancesheet_statment(ts_code, "quarter")
        if (quarter_df is not None and not quarter_df.empty):
            df = pd.concat([quarter_df, df], axis=0, ignore_index=True)

        df = df.sort_values(by=['filingDate','period'], ascending=[True,False], inplace=False)
        df.to_csv(file_path,index=False)
        return df



@monitor_strategy
def do_get_balancesheet_statment(ts_code:str, period:str= "annual"):

        # 默认是查询年报
        url = f"https://financialmodelingprep.com/stable/balance-sheet-statement?symbol={ts_code}"+"&limit=1000"
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
                        # 根据年份排序，早的年份排在前面
                    return df

                else:
                    logger.error(f"do_get_balancesheet_statment 失败，ts_code:{ts_code}，获取到的内容为空")
            logger.error(f"do_get_balancesheet_statment 失败，ts_code:{ts_code}，状态码: {response.status_code}")
        except Exception as e:
            print(f"do_get_balancesheet_statment,获取 {ts_code} 失败: {e}")
            return {}


        # 适当休眠避免触发 API 频率限制 (根据你的账户等级调整)
        time.sleep(random.uniform(0.1, 0.3))


def get_balancesheet(ts_code:str):
    print("get_balancesheet"+ts_code)
    file_path = config.USA_STOCK_FINANCE_DATA_DIR + "/balancesheet/" + str(ts_code)
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"{ts_code} get_balancesheet失败: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    do_get_complete_balancesheet_statment('AAPL')