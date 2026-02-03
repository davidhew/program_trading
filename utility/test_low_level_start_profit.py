'''
回低位启动的收益情况
假设条件：
1.起始资金100万，平等分成5份；
2.买入规则：
    2.1一只启动的股票，如果第二天其只要没有涨停（默认就是开盘价没有超过第一天收盘价9.97%），就以第二天开盘价买入
    2.2在符合2.1的条件下，需要有剩余资金，比如一开始的100万，如果已经买入了5只股票且正在持有，则此时没有资金再买入，这种情况下认为没有执行该笔交易
    2.3系统会记录当前持有几只股票；比如持有了3只股票；那么当前剩余2只股票的购买机会，当发现购买机会时，会用剩余的1/2的金额，买入该只股票
3.卖出规则：
    3.1最多持有20个交易日，如果在20个交易日内没有止盈止损，则以第20个交易日的close价格卖出
    3.2在20个交易日内，如果价格涨到买入价的20%，以该价格卖出，获利20%
    3.3在20个交易日内，如果价格跌倒买入价的7%，以该价格卖出，亏损7%
3.从25年1月2号开始，到25年12月31号的交易日期
'''
from zoneinfo import available_timezones

import pandas as pd
import config
import date_utility
from get_stock_data import get_all_stock_data as get_stock_data



def back_test_low_level_start_profit():
    start_date = '20251103'
    end_date = '20251231'
    #最多同时持有5只股票
    max_hold_stock_number = 5
    current_hold_number = 0
    total_money=1000000
    available_cash = total_money


    stock_holds = pd.DataFrame(columns=['ts_code','buy_total_money','sell_total_money','start_date','end_date'])

    trade_date = start_date
    while trade_date <= end_date:

        try:

            stock_list_df = pd.read_csv(config.STOCK_STRATEGY_RESULT_DIR + 'low-level-start-' + trade_date + '.txt')
            #已经售出的股票清除掉
            if(trade_date == '20251202'):
                print("haha")
            stock_holds=stock_holds[stock_holds['end_date'] >= int(trade_date)]
            # 此时索引可能是不连续的，执行重置
            stock_holds = stock_holds.reset_index(drop=True)
            print(trade_date+":available_cash:"+str(available_cash)+":stock_hold_total:"+str(stock_holds['sell_total_money'].sum()))
            print(trade_date+":total_money:"+str(available_cash+stock_holds['sell_total_money'].sum()))

            #最大持有数-还在持有期间的股票数
            available_nums= max_hold_stock_number- len(stock_holds)
            print(trade_date+":available_num:"+str(available_nums))


            if(available_nums==0):
                continue
            if(len(stock_list_df) > 0):
                for idx in range(len(stock_list_df)):
                    stock_code = stock_list_df.iloc[idx]['ts_code']
                    stock_df = get_stock_data.get_stock_data(stock_code)
                    matched_indices = stock_df.index[stock_df['trade_date'] == int(trade_date)].tolist()
                    if len(matched_indices) == 0:
                        continue
                    if(len(matched_indices) > 1):
                        print("error, one trade_date should just has one row:%s,%s",stock_code,trade_date)
                    row_idx = matched_indices[0]
                    #第二天是否开盘价格过高，过高则忽略该次交易机会
                    is_zhangting = (stock_df.iloc[row_idx+1]['open']/stock_df.iloc[row_idx]['close'] >=1.097)
                    buy_price =0
                    if(is_zhangting):
                        continue
                    buy_price = stock_df.iloc[row_idx+1]['open']

                    available_nums = max_hold_stock_number - len(stock_holds)
                    if(available_nums <= 0):
                        continue
                    amount = available_cash / available_nums
                    available_cash=available_cash-amount

                    low_sell_date=20301231
                    high_sell_date=20301231
                    if (trade_date == '20251201'):
                        print("haha")
                    for i in range(2,21):
                        if(stock_df.iloc[row_idx+i]['low']/buy_price<=0.93 and low_sell_date==20301231):
                            low_sell_date=stock_df.iloc[row_idx+i]['trade_date']
                        if(stock_df.iloc[row_idx+i]['high']/buy_price>=1.2 and high_sell_date==20301231):
                            high_sell_date=stock_df.iloc[row_idx+i]['trade_date']
                    #止损在止盈之前，所以计入止损
                    if(low_sell_date !=20301231 and low_sell_date <=high_sell_date):
                        row =[stock_code,amount,amount*0.93,trade_date,low_sell_date]
                        stock_holds.loc[len(stock_holds)] =row

                        print("sell low, loss money:"+str(amount*0.07)+":row:"+str(row))
                    elif (high_sell_date != 20301231 and high_sell_date <= low_sell_date):
                        row =[stock_code, amount, amount * 1.2, trade_date, high_sell_date]
                        stock_holds.loc[len(stock_holds)] = row
                        print("sell high, earn money:"+str(amount * 0.20)+":row:"+str(row))
                    #在规定时间内没有触发止盈止损，则以第20个交易日的收盘价卖出
                    elif(low_sell_date == 20301231 and high_sell_date ==20301231):
                        sell_amount = amount*stock_df.iloc[row_idx]['open']/stock_df.iloc[row_idx+20]['close']
                        sell_date = stock_df.iloc[row_idx+20]['trade_date']
                        row = [stock_code, amount, sell_amount, trade_date, sell_date]
                        stock_holds.loc[len(stock_holds)] = row
                        if(amount>=sell_amount):
                            print("20day,sell low, loss money:"+str(amount-sell_amount)+":row:"+str(row))
                        else:
                            print("20day,sell high, earn money:"+str(sell_amount-amount)+":row:"+str(row))
                    else:
                        print("can't reach here!, ts_code:%s,trade_date:%s,low_sell_date:%s,high_sell_date:%s",stock_code,str(trade_date),str(low_sell_date),str(high_sell_date))



        finally:

            #当天到期的售出股票逻辑处理
            expired_stocks = stock_holds[stock_holds['end_date'] == int(trade_date)]
            if len(expired_stocks) > 0:
                available_cash += expired_stocks['sell_total_money'].sum()
                print('trade_date:'+trade_date+":available_cash:"+str(available_cash))
            trade_date=date_utility.days_plus(str(trade_date),1)

    total_money = available_cash + stock_holds['sell_total_money'].sum()
    print("total_money is:%s",str(total_money))


if __name__ == "__main__":
    back_test_low_level_start_profit()
