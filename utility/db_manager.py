from datetime import datetime

import dataset
import config
import logging

from utility import secrets_config as secrets_config

logger = logging.getLogger("dashboard")
secrets = secrets_config.load_external_config()

# 1. 连接数据库 (如果文件不存在，会自动创建)
# 使用 SQLite 并在本地生成 stocks_manager.db 文件
db_url="mysql+pymysql://"+secrets.get("DB_USER")+":"+secrets.get("DB_PASSWD")+"@"+secrets.get("DB_SERVER")+":3306/"+secrets.get("DB_NAME")+"?charset=utf8&autocommit=true"
logger.info("db_url:"+db_url)
print("db_url:"+db_url)
#db = dataset.connect('mysql+pymysql://user:pass@host:port/dbname?charset=utf8mb4')
# 每隔 3600 秒回收连接，防止 MySQL 8 小时断连导致的事务异常


def init_database():

    db = dataset.connect(
        db_url,
        engine_kwargs={
            'pool_recycle': 3600, # Re-establish connection every hour
            'pool_pre_ping': True, # Check if connection is alive before every query
            'pool_size': 10
        }
    )
    return db

db = init_database()

def get_database():
    return db

#数据库出现异常后，更新一下，丢弃掉旧的有问题的数据库连接
def reset_database():
    db = init_database()