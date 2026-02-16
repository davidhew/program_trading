'''
做单元测试的文件
'''

import pandas as pd
from get_stock_data import get_all_stock_data as get_stock_data
from utility import stock_util as su



def test_df_search():

    df = pd.DataFrame(columns=['ts_code', 'trade_date'])
    df.loc[0] = ['0001', 20260123]
    df.loc[1] = ['0001', 20260122]
    df.loc[2] = ['0001', 20260121]
    row_idx = df.index[df['trade_date'] == 20260122].tolist()[0]
    print(row_idx)

def test_data_integrity():
    ts_code='300943.SZ'
    stock_df = get_stock_data.get_stock_data(ts_code)
    data_slice = stock_df.iloc[0:512]['close']
    min = stock_df.iloc[1:253]['close'].min()
    i = 0
    for data in data_slice:
        if(data>0 and data<=100):
            i = i+1
            #do nothing
        else:
            print(data)
    print(i)
    print(min)




if __name__ == "__main__":
    #test_data_integrity()
    df = get_stock_data.get_stock_data(ts_code='301111.SZ')
    su.is_compressed(df,0)


