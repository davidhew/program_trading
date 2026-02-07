'''
简放的20日动量法
1.选取出最近20日涨幅最大的前820只股票(A股整个市场大概5400家公司，取前15%)
2.汇聚计算这些公司所属的行业，从而根据算法，得出行业的动量分
'''

import pandas as pd
import pandas_ta as ta
from datetime import datetime
from us_get_stock_data import us_get_stock_base_info as usa_gd_base_info
from us_get_stock_data import us_get_all_stock_data as usa_gd
import logging

import config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

today = datetime.now()
today_str=today.strftime('%Y-%m-%d')

def compute(date_str:str =None,day_num:int =20):
    # 如果用户没有指定日期，则取系统当前时间
    if date_str == None:
        date_str = datetime.now().strftime('%Y%m%d')

    df = pd.DataFrame(columns=['ts_code','price_up_ratio'])
    for batch in usa_gd.get_stock_data_batches():

        for stock in batch:
            # 至少已经上市一年了，新近上市的剔除掉影响
            if (len(stock) < 253):
                logger.info("compute_momentum, %s's data less than one year!", stock.iloc[0]['ts_code'])
                continue
            else:
                matched_indices = stock.index[stock['trade_date'] == int(date_str)].tolist()
                if len(matched_indices) == 0:
                    continue
                row_idx = matched_indices[0]
                if row_idx - day_num >= 0 and stock.iloc[row_idx]['trade_date'] == int(date_str):
                    # 获取分母（n天前的价格）
                    denominator = stock.iloc[row_idx - day_num]['close']

                    # 只有当分母存在且大于0时才计算，否则设为 1.0 (代表不涨不跌) 或 0
                    if denominator > 0:
                        price_up_ratio = stock.iloc[row_idx]['close'] / denominator
                    else:
                        logger.info("股票:%s, 由于其:%d天前的收盘价格不合格，故在计算momentum时，对其忽略")
                        continue
                    price_up_ratio = stock.iloc[row_idx]['close'] / stock.iloc[row_idx - day_num]['close']
                    ts_code = stock.iloc[row_idx]['ts_code']
                    new_row_values = [ts_code, price_up_ratio]
                    #近20日的收盘价，平均价要高于5美金（价格太低的股票可能风险较大）
                    close_price_ok = stock.iloc[row_idx-day_num:row_idx]['close'].mean() >=5
                    if(not close_price_ok):
                        continue
                    # 最近n个交易日，每个交易日平均交易金额要大于1个亿
                    is_average_amount_enough = (
                                stock.iloc[row_idx - day_num:row_idx]['amount'].sum()  >= day_num  * 10000 * 10000)
                    if (is_average_amount_enough):
                        df.loc[len(df)] = new_row_values
    df = df.sort_values(by=['price_up_ratio'], ascending=[False], ignore_index=True)
    # 挑选最前面的200只个股，进入动量股池
    strong_df = df.head(int(config.USA_STOCK_MOMENTUM_TOP_NUMBER))

    strong_df.to_csv(config.USA_STOCK_STRATEGY_RESULT_DIR + 'momentum-stock-list-strong-' +str(day_num)+'-'+ today_str + '.csv',
                       index=False)

    df = df.sort_values(by=['price_up_ratio'], ascending=[True], ignore_index=True)
    weak_df = df.head(int(config.USA_STOCK_MOMENTUM_TOP_NUMBER))
    weak_df.to_csv(config.USA_STOCK_STRATEGY_RESULT_DIR + 'momentum-stock-list-weak-' +str(day_num)+'-' +today_str + '.csv',
                     index=False)

    '''
    #获取各行业总的上市公司数量
    df2 = gd_base_info.get_china_stock_base_info()
    industry_total_company_count = df2.groupby('industry').size().reset_index(name='total_counts')

    # 筛选出的动量名单里的公司，统计其行业分布情况
    df3 = gd_base_info.get_china_stock_base_info()
    result_inner = pd.merge(df, df3, on='ts_code', how='inner')
    counts_size = result_inner.groupby('industry').size().reset_index(name='momentum_counts')

    #计算每个行业中的动量分只；计算公式为 momentum_value=该行业动量公司的数量*（该行业动量公司数量/该行业公司总数）
    df4=pd.merge(industry_total_company_count, counts_size, on='industry',how='inner')
    df4['momentum_value']=df4['momentum_counts']*df4['momentum_counts']/df4['total_counts']
    df4 = df4.sort_values(by='momentum_value', ascending=False)
    
    df4.to_csv(config.STOCK_STRATEGY_RESULT_DIR + 'momentum-20' + today_str + '.csv', index=False)
    '''

if __name__ == "__main__":
    # test_data_integrity()
    compute('20260128')