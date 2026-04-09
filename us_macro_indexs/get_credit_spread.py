"""
信用利差：企业债的利率-美国国债利率，可以反映经济的基本面
如果信用利差扩大，说明企业违约率上升，经济基本面变差

1. 核心信用利差指标 (FRED Series ID)

｜          指标名称        ｜     FRED代码     ｜                   说明                          ｜
｜         投资级利差       ｜     BAA10Y       ｜穆迪BAA级企业债收益率减去10年期国债收益率（最经典指标） ｜
｜  高收益债利差 (垃圾债)    ｜   BAMLH0A0HYM2  ｜   ICE BofA 美国高收益指数期权调整利差 (OAS)         ｜
｜       中等风险利差       ｜   BAMLC0A4CBBB   ｜BBB 级企业债利差（反映经济衰退前兆的敏感指标）         ｜
｜       金融压力指数       ｜      STLFSI4     ｜ 圣路易斯联储金融压力指数（综合了利差、波动率等）        ｜
"""

from fredapi import Fred
import pandas as pd
import config
import logging



from utility import secrets_config as secrets_config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrets = secrets_config.load_external_config()
file_name="credit_spread.csv"

def get_data():
    # 建议在你的 config.py 中统一管理 API KEY
    # fred = Fred(api_key=config.FRED_KEY)
    fred = Fred(api_key=secrets.get('FRED_KEY'))

    # 获取高收益债利差 (High Yield Spread)
    hy_spread = fred.get_series('BAMLH0A0HYM2')

    # 获取投资级利差 (Investment Grade Spread - BAA)
    ig_spread = fred.get_series('BAA10Y')

    # 合并数据
    df_spreads = pd.DataFrame({
        'high_yield_spread': hy_spread,
        'investment_grade_spread': ig_spread
    }).ffill()
    df_spreads.index.name = 'date'
    df_spreads.to_csv(config.USA_STOCK_MACRO_DATA_DIR + file_name, index=True)
    print(df_spreads.tail())