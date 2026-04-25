"""
重点关注的股票
对于这些股票，会记录一些重要信息，并且保持持续的更新
"""
from datetime import datetime

import dataset

from utility import secrets_config as secrets_config
secrets = secrets_config.load_external_config()

# 1. 连接数据库 (如果文件不存在，会自动创建)
# 使用 SQLite 并在本地生成 stocks_manager.db 文件
db_url="mysql+pymysql://"+secrets.get("DB_USER")+":"+secrets.get("DB_PASSWD")+"@"+secrets.get("DB_SERVER")+":3306/"+secrets.get("DB_NAME")+"?charset=utf8"
print("db_url:"+db_url)
#db = dataset.connect('mysql+pymysql://user:pass@host:port/dbname?charset=utf8mb4')
db = dataset.connect(db_url)


# 2. 获取表对象 (如果表不存在，会在第一次插入数据时自动创建)
table = db['favorite_stocks']


# --- INSERT (插入) ---
# 插入时不需要预先定义字段，dataset 会根据字典的 key 自动生成列
def add_stock(code, name, tags, market,business, advantage,disadvantage,milestones):
    table.insert({
        'code': code,
        'name': name,
        'tags': ",".join(tags),  # 建议存为逗号分隔字符串，或使用 JSON 格式
        'market': market,
        'business': business,
        'advantage':advantage,
        'disadvantage':disadvantage,
        'milestones': milestones,
        'create_time': datetime.now(),
        'update_time':datetime.now()
    })
    print(f"✅ 已插入: {name}")


# --- UPDATE (更新) ---
# 只要指定“筛选条件”和“更新内容”即可
def update_stock(code:str, fields:dict ):
    # 根据 code 定位，更新 business 字段
    table.update(fields, ['code'])
    print(f"🔄 已更新代码为 {code} 的股票情况")


# --- SELECT (查询) ---
def query_stocks(tag_filter=None):
    if tag_filter:
        # 简单模糊查询
        results = table.find(tags={'like': f'%{tag_filter}%'})
    else:
        # 获取全部数据
        results = table.find(order_by=['-create_time'], _limit=50)

    return list(results)

# --- 根据股票代码 code 查询单条股票信息 ---
def get_stock_by_code(code):
    # 精确查询：code 完全匹配
    stock = table.find_one(code=code)
    return stock  # 有数据返回字典，没有返回 None

# --- 实际运行演示 ---

def test_add_stock():
# A. 录入数据
    add_stock('600519', '贵州茅台', ['白酒', '大消费'], '高端白酒生产', '2023年利润新高','政策持续打压','暂无明显时间计划')


# B. 查询所有
print("\n--- 当前所有关注股票 ---")
for s in query_stocks():
    print(f"[{s['code']}] {s['name']} - 标签: {s['tags']}")

# C. 按条件查询 (基于标签)
print("\n--- 筛选【新能源】标签 ---")
energy_stocks = query_stocks('新能源')
for s in energy_stocks:
    print(f"找到: {s['name']}")


# E. 顺便提一下 DELETE (删除)
# table.delete(code='600519')