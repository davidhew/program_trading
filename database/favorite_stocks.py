"""
重点关注的股票
对于这些股票，会记录一些重要信息，并且保持持续的更新
"""
from datetime import datetime

import dataset
import config
import logging
from utility.db_monitor_strategy import db_monitor


from utility import secrets_config as secrets_config

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.INFO)
logger = logging.getLogger()
secrets = secrets_config.load_external_config()

# 1. 连接数据库 (如果文件不存在，会自动创建)
# 使用 SQLite 并在本地生成 stocks_manager.db 文件
db_url="mysql+pymysql://"+secrets.get("DB_USER")+":"+secrets.get("DB_PASSWD")+"@"+secrets.get("DB_SERVER")+":3306/"+secrets.get("DB_NAME")+"?charset=utf8&autocommit=true"
print("db_url:"+db_url)
#db = dataset.connect('mysql+pymysql://user:pass@host:port/dbname?charset=utf8mb4')
# 每隔 3600 秒回收连接，防止 MySQL 8 小时断连导致的事务异常
db = dataset.connect(
    'mysql+pymysql://user:password@localhost/dbname',
    engine_kwargs={
        'pool_recycle': 3600, # Re-establish connection every hour
        'pool_pre_ping': True # Check if connection is alive before every query
    }
)


# 2. 获取表对象 (如果表不存在，会在第一次插入数据时自动创建)
table = db['favorite_stocks']


# --- INSERT (插入) ---
# 插入时不需要预先定义字段，dataset 会根据字典的 key 自动生成列
@db_monitor(db)
def add_stock(code, name, tags, market,business, advantage,disadvantage,milestones,institution_view,financial_statements):
    table.insert({
        'code': code,
        'name': name,
        'tags': tags,  # 建议存为逗号分隔字符串，或使用 JSON 格式
        'market': market,
        'business': business,
        'advantage':advantage,
        'disadvantage':disadvantage,
        'milestones': milestones,
        'institution_view': institution_view,
        'financial_statements': financial_statements,
        'create_time': datetime.now(),
        'update_time':datetime.now()
    })
    print(f"✅ 已插入: {name}")


# --- UPDATE (更新) ---
# 只要指定“筛选条件”和“更新内容”即可
@db_monitor(db)
def update_stock(code:str, fields:dict ):
    # 根据 code 定位，更新 business 字段
    table.update(fields, ['code'])
    print(f"🔄 已更新代码为 {code} 的股票情况")


# ==============================
# 1. 查询符合条件的总数
# ==============================
@db_monitor(db)
def query_stocks_count(tag_filter=None, code_filter=None, name_filter=None):
    sql = "SELECT COUNT(*) AS total FROM favorite_stocks WHERE 1=1"
    params = {}

    if tag_filter:
        sql += " AND tags LIKE :tag"
        params["tag"] = f"%{tag_filter}%"

    if code_filter:
        sql += " AND code LIKE :code"
        params["code"] = f"%{code_filter}%"

    if name_filter:
        sql += " AND name LIKE :name"
        params["name"] = f"%{name_filter}%"

    res = list(db.query(sql, **params))
    return res[0]['total'] if res else 0


# ==============================
# 2. 分页查询数据
# ==============================
@db_monitor(db)
def query_stocks_by_page(tag_filter=None, code_filter=None, name_filter=None, page=0, page_size=20):
    offset = page * page_size  # 因为页码从0开始，直接乘

    sql = "SELECT * FROM favorite_stocks WHERE 1=1"
    params = {}

    if tag_filter:
        sql += " AND tags LIKE :tag"
        params["tag"] = f"%{tag_filter}%"

    if code_filter:
        sql += " AND code LIKE :code"
        params["code"] = f"%{code_filter}%"

    if name_filter:
        sql += " AND name LIKE :name"
        params["name"] = f"%{name_filter}%"

    sql += " ORDER BY create_time DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset

    return list(db.query(sql, **params))

# --- 根据股票代码 code 查询单条股票信息 ---
@db_monitor(db)
def get_stock_by_code(code):
    # 精确查询：code 完全匹配
    stock = table.find_one(code=code)
    return stock  # 有数据返回字典，没有返回 None

# --- 实际运行演示 ---

def test_add_stock():
# A. 录入数据
    add_stock('600519', '贵州茅台', ['白酒', '大消费'], '高端白酒生产', '2023年利润新高','政策持续打压','暂无明显时间计划')




# E. 顺便提一下 DELETE (删除)
# table.delete(code='600519')