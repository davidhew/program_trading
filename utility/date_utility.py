'''
提供一些常用的日期相关的工具函数
'''
from datetime import timedelta
from datetime import datetime
'''
计算特定日期多少天之前的日期
    Args:
        date_str:特定日期，比如“20251220”
        days_num:向前推移的天数
    Returns:
        int: 计算出来的日期的int值，内容如“20251210”，但是以int形势返回

'''
def days_befor(date_str:str,days_num:int)->int:
    current_date = datetime.strptime(date_str, '%Y%m%d')
    previous_date = current_date - timedelta(days=days_num)

    return int(previous_date.strftime('%Y%m%d'))

def days_plus(date_str:str,days_num:int)->str:
    current_date = datetime.strptime(date_str, '%Y%m%d')
    return_date = current_date + timedelta(days=days_num)

    return return_date.strftime('%Y%m%d')

'''
计算2个日期之间是否超过了相隔的天数
    Args:
        date_str1:日期1， 格式“%Y%m%d”
        date_str2:日期2，格式“%Y%m%d”
        diff:相隔的天数
    Returns:
        int:2个日期相差的天数是否大于diff，大于则返回true
'''
def is_days_before(date_str1:str,dayte_str2:str,diff:int)->bool:
    current_date = datetime.strptime(date_str1, '%Y%m%d')
    last_date = datetime.strptime(dayte_str2, '%Y%m%d')
    abs_diff = abs(current_date - last_date).days
    if abs_diff > diff:
        return True
    return False

