'''
提供一些股票常用的计算功能，供其他模块使用
'''
from get_stock_data import get_all_stock_data as gd
import logging
logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()

'''
计算单个股票在某个时间区间内（period），最后一个交易日的收盘价，相比该区间内的最低收盘价，其涨幅是否超过某个幅度（range）
Args:
    ts_code:股票代码，A股的类似“688516.SH”
    current_date:最后的一个交易日，计算区间的时候，要从该交易日往前的一个交易日计算
    period:时间区间，比如像计算半年，那么period应该是126（我们认为一年的交易日为252个）
    range:股价上涨幅度，比如希望在该区间内，最后一个日的收盘价没有超过该区间最低收盘价的50%，那么range传递的参数就是0.5
'''
def stock_price_too_high(ts_code:str,current_date:str,period:int,range:float) -> bool:
    df = gd.get_stock_data(ts_code)
    row_idx=df.index[df['trade_date'] == int(current_date)].tolist()[0]
    if row_idx<len(df) and df.iloc[row_idx]['trade_date']==int(current_date):
        close_end = df.iloc[row_idx+1]['close']
        min_close = df.iloc[row_idx+1:row_idx+1+period]['close'].min()
        return close_end >= min_close * (1+range)

    else:
        logger.error("stock_price_not_high, ts_code:%s,current_date:%s illegal, didn't exist daily data",ts_code,current_date)
        return False
'''
计算单个股票在某个交易日的均价 
Args:
    ts_code:股票代码，A股的类似“688516.SH”
    trade_date:指定交易日
    均价算法：成交额/成交的股数
'''
def get_average_price(ts_code:str,trade_date:str)->float:
    df = gd.get_stock_data(ts_code)
    row_idx = df.index[df['trade_date'] == int(trade_date)].tolist()[0]
    if row_idx < len(df) and df.iloc[row_idx]['trade_date'] == int(trade_date):
        #成交额单位为千元；成交量单位为100股
        price= (df.iloc[row_idx]['amount']*1000)/(df.iloc[row_idx]['vol']*100)
        return round(price,2)
    else:
        logger.error("get_average_price, ts_code:%s,trade_date:%s illegal, didn't exist daily data", ts_code,
                     trade_date)
        return 0