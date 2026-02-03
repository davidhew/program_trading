'''
提供一些常用的工具函数
'''

import logging
logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()
def tonghuashun_format(stock_list:list)->list:
    result = list()
    for stock in stock_list:
        #带来交易所缩写的形式，把交易所信息去掉
        if(len(stock)==9):
            stock = stock[:6]

        if(len(stock)==6):
            if(stock[0]=='3'):
                result.append("0"+stock)
            elif(stock[0]=='0'):
                result.append("0"+stock)
            elif(stock[0]=='6'):
                result.append("1"+stock)
            elif(stock[0]=='9'):
                result.append("2"+stock)
        else:
            logger.error("tonghuashun_format: illegal stock format:"+stock)
    return result

