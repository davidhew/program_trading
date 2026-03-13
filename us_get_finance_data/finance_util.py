from pathlib import Path
import datetime
from datetime import timedelta
from datetime import datetime
import config

"""
是否要更新财报：
1.如果该财报的数据之前根本没获取过，则需要更新
2.如果之前获取过，但是上次获取事件离当前已经超过N天，则需要更新

"""
def should_update_data(file_path:str,days_before:int=90):

    if("1"==config.FORCE_GET_CHINA_STOCK_FINANCE_DATA):
        return True

    path = Path(file_path)
    if (not path.exists() or not path.is_file()):
        return True
    mtime = path.stat().st_mtime
    last_modified_time = datetime.fromtimestamp(mtime)
    now = datetime.now()

    # 3. 判断是否超过 3 个月 (按 90 天计算更为精确)
    if now - last_modified_time > timedelta(days=days_before):
        return True
    else:
        return False
    return True