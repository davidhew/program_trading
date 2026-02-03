'''
股票相关的一些工具类
'''
import pandas as pd

'''
钻潜交易里的统一区间的概念
现在针对A股，先写死，需要满足如下几个条件：
1.股票的MA[120]本身是向上的
2.股票的MA[50]是向上的
3.股票的MA[50]位于MA[120]之上
4.最后一天的股价，是在MA[120]之上
5.最近3个交易日的股价(row_idx指代的交易日之前的3个交易日)，每天的涨跌幅绝对值不超过2%;3天累加的涨跌幅绝对值不超过3%
'''
def is_compressed(stock_df:pd.DataFrame,row_idx:int)->bool:
    #已经上市超过一年时间（从交易日往前推）
    if (row_idx - 253 < 0):
        return False

    stock_df['MA50']=stock_df['close'].rolling(window=50, min_periods=1).mean()
    #需要MA50趋势向上
    if(not stock_df.iloc[row_idx]['MA50']>=stock_df.iloc[row_idx-1]['MA50']):
        return False

    stock_df['MA120'] = stock_df['close'].rolling(window=120, min_periods=1).mean()

    # 需要MA120趋势向上
    if (not stock_df.iloc[row_idx]['MA120'] >= stock_df.iloc[row_idx - 1]['MA120']):
        return False
    #需要MA50在MA120之上
    if(not stock_df.iloc[row_idx]['MA50'] >= stock_df.iloc[row_idx]['MA120']):
        return False
    #前3个交易日的振幅不能过大
    if(abs(stock_df.iloc[row_idx-1]['pct_chg'])>2 or abs(stock_df.iloc[row_idx-2]['pct_chg'])>2 or abs(stock_df.iloc[row_idx-3]['pct_chg'])>2):
        return False
    if(abs(1-stock_df.iloc[row_idx-1]['close']/stock_df.iloc[row_idx-3]['close'])*100>3):
        return False

    return True