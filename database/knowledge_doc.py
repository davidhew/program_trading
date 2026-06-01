"""
知识库文章
一些专业人士/机构对于某个行业研究，市值整体看法的文章
"""
from datetime import datetime

import logging
from utility.db_monitor_strategy import db_monitor
from utility import db_manager
from utility.logger_config import setup_logging
setup_logging()

logger = logging.getLogger("dashboard")

# 2. 获取表对象 (如果表不存在，会在第一次插入数据时自动创建)
def get_doc_table():
    """每次操作前或重置后，通过此函数安全获取表对象"""
    return db_manager.get_database()['knowledge_doc']


# --- INSERT (插入) ---
# 插入时不需要预先定义字段，dataset 会根据字典的 key 自动生成列
@db_monitor(db_manager.get_database())
def add_doc(title, tags, source,content):
    table = get_doc_table()
    table.insert({
        'title': title,
        'source':source,
        'tags': tags,  # 建议存为逗号分隔字符串，或使用 JSON 格式
        'content': content,
        'outdated': 0,#是否已过时

        'create_time': datetime.now(),
        'update_time':datetime.now()
    })
    print(f"✅ 已插入: {title}")


# --- UPDATE (更新) ---
# 只要指定“筛选条件”和“更新内容”即可
@db_monitor(db_manager.get_database())
def update_doc(id:str, fields:dict ):
    table = get_doc_table()
    table.update(fields, ['id'])
    print(f"🔄 已更新id为 {id} 的文章")

#把文章置为过时
@db_monitor(db_manager.get_database())
def outdate_doc(id:str):
    table = get_doc_table()
    table.update({"outdated",1}, ['id'])
    print(f"🔄 已更新id为 {id} 的文章")


# ==============================
# 1. 查询符合条件的总数
# ==============================
@db_monitor(db_manager.get_database())
def query_doc_count(tag_filter=None, title_filter=None,with_outdated=False):
    sql = "SELECT COUNT(*) AS total FROM knowledge_doc WHERE 1=1"
    params = {}

    if not with_outdated:
        sql += " AND outdated=0"

    if tag_filter:
        sql += " AND tags LIKE :tag"
        params["tag"] = f"%{tag_filter}%"

    if title_filter:
        sql += " AND title LIKE :title"
        params["title"] = f"%{title_filter}%"


    res = list(db_manager.get_database().query(sql, **params))
    return res[0]['total'] if res else 0


# ==============================
# 2. 分页查询数据
# ==============================
@db_monitor(db_manager.get_database())
def query_doc_by_page(tag_filter=None, title_filter=None, page=0, page_size=20,with_outdated=False):
    offset = page * page_size  # 因为页码从0开始，直接乘

    sql = "SELECT * FROM knowledge_doc WHERE 1=1"
    params = {}

    if not with_outdated:
        sql += " AND outdated=0"

    if tag_filter:
        sql += " AND tags LIKE :tag"
        params["tag"] = f"%{tag_filter}%"

    if title_filter:
        sql += " AND title LIKE :title"
        params["title"] = f"%{title_filter}%"

    sql += " ORDER BY create_time DESC LIMIT :limit OFFSET :offset"
    params["limit"] = page_size
    params["offset"] = offset

    return list(db_manager.get_database().query(sql, **params))

# --- 根据股票代码 code 查询单条股票信息 ---
@db_monitor(db_manager.get_database())
def get_doc_by_id(id):
    table = get_doc_table()
    # 精确查询：code 完全匹配
    doc = table.find_one(id=id)
    return doc  # 有数据返回字典，没有返回 None



# E. 顺便提一下 DELETE (删除)
# table.delete(code='600519')