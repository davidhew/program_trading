'''
获取同花顺的二级行业信息
'''

import akshare as ak

def get_ths_industry():
    print('hello')
    ths_index_df = ak.stock_board_industry_name_ths()
    print('hello'+str(ths_index_df))

    result_df = ak.stock_board_industry_cons_ths('半导体')
    print(result_df[['代码','名称']])

if __name__ == "__main__":
    #test_data_integrity()
    get_ths_industry()