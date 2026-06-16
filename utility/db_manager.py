from datetime import datetime

import dataset
import config
import logging

from utility import secrets_config as secrets_config

logger = logging.getLogger("dashboard")
secrets = secrets_config.load_external_config()

# 1. 连接数据库 (如果文件不存在，会自动创建)
# 使用 SQLite 并在本地生成 stocks_manager.db 文件
db_url="mysql+pymysql://"+secrets.get("DB_USER")+":"+secrets.get("DB_PASSWD")+"@"+secrets.get("DB_SERVER")+":3306/"+secrets.get("DB_NAME")+"?charset=utf8mb4&autocommit=true"
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
    """数据库出现异常后，彻底销毁旧连接并生成全局新 db"""
    global db  # 【核心修复】声明我们要修改的是外部作用域的全局变量 db

    logger.warning("🔄 接收到重置数据库请求，正在启动重置策略...")

    # 1. 优雅释放旧连接池资源，防止连接数泄露
    if db is not None:
        try:
            #老的db已经出现问题，所以尝试对其进行rollback
            db.rollback()
            logger.info("正在销毁旧的数据库连接池...")
            # 如果之前发生了连接污染，清除 dataset 的线程本地缓存
            if hasattr(db, '_tlocal'):
                db._tlocal.__dict__.clear()
            db.engine.dispose()
        except Exception as dispose_e:
            logger.error(f"释放旧数据库资源时发生异常(可忽略): {dispose_e}")

    # 2. 生成新连接并覆写全局变量
    try:
        db = init_database()
        logger.info("✅ 成功重新生成数据库连接对象，全局变量已更新。")
    except Exception as e:
        logger.critical(f"❌ 重新初始化数据库彻底失败: {e}")
        raise e