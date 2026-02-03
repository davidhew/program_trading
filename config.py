import os
from dotenv import load_dotenv

# 1. 确定当前环境（通过系统变量 APP_ENV 确定，默认 dev）
env = os.getenv("APP_ENV", "dev")

# 2. 根据环境加载对应的 .env 文件
env_file = f".env.{env}"
if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"--- 已从 {env_file} 加载配置 ---")
else:
    # 如果文件不存在，可能直接读取系统环境变量（如 Docker 注入的）
    print("--- 未发现 .env 文件，直接从系统环境读取 ---")
##全局配置文件
#A股日线数据的存放目录
CHINA_STOCK_DATA_DIR=os.getenv('CHINA_STOCK_DATA_DIR')
#A股股票基础信息存放目录
CHINA_STOCK_DIR=os.getenv('CHINA_STOCK_DIR')

#美股日线数据的存放目录
USA_STOCK_DATA_DIR=os.getenv('USA_STOCK_DATA_DIR')
#美股股票基础信息存放目录
USA_STOCK_DIR=os.getenv('USA_STOCK_DIR')

#策略/选股策略跑出的内容保存的目录
STOCK_STRATEGY_RESULT_DIR=os.getenv('STOCK_STRATEGY_RESULT_DIR')

#A股龙虎榜数据保存文件
STOCK_DRAGON_TIGER_RANK_LIST_FILE=os.getenv('STOCK_DRAGON_TIGER_RANK_LIST_FILE')

#美股策略/选股策略跑出的内容保存的目录
USA_STOCK_STRATEGY_RESULT_DIR=os.getenv('USA_STOCK_STRATEGY_RESULT_DIR')

#动量策略时，按照涨幅排序后，挑取前面的多少家公司进行后续的分析处理
CHINA_STOCK_MOMENTUM_TOP_NUMBER=os.getenv('CHINA_STOCK_MOMENTUM_TOP_NUMBER')

#动量策略时，按照涨幅排序后，挑取前面的多少家公司进行后续的分析处理
USA_STOCK_MOMENTUM_TOP_NUMBER=os.getenv('USA_STOCK_MOMENTUM_TOP_NUMBER')

#A股日线数据存放时保留的列
CHINA_STOCK_DATA_COLUMN=os.getenv('CHINA_STOCK_DATA_COLUMN')

#美股日线数据存放时保留的列
USA_STOCK_DATA_COLUMN=os.getenv('USA_STOCK_DATA_COLUMN')

CHINA_DRAGON_TIGER_RANK_LIST_COLUMN=os.getenv('CHINA_DRAGON_TIGER_RANK_LIST_COLUMN')

#简放的股池数据保存时保留的列
JIANFANG_STOCK_POOL_DATA_COLUMN=os.getenv('JIANFANG_STOCK_POOL_DATA_COLUMN')

#一只股票日线最多存放多少个自然日的数据（太久远的数据对交易没有作用）
DAY_NUMBER=os.getenv('DAY_NUMBER')
#龙虎榜历史数据存放的最长天数
DRAGON_TIGER_RANK_LIST_DAY_NUMBER=os.getenv('DRAGON_TIGER_RANK_LIST_DAY_NUMBER')

SECRET_CONFIG_PATH=os.getenv('SECRET_CONFIG_PATH')
#是否发送telegram，0表示不发送--调试场景；1表示发送--生产场景
SEND_TELEGRAM=os.getenv('SEND_TELEGRAM')

#简放股池策略里，股池里股票的淘汰周期（以自然天计算，而非只算交易日）
#暂时先赋值一个月；后续观察是否要扩大到2个月
JIANFANG_POOL_EXPIRE_DAYS=os.getenv('JIANFANG_POOL_EXPIRE_DAYS')