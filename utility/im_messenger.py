'''
给IM工具发送消息
'''
import io

import logging

import dingtalk_messenger as dingtalk_messenger
import telegram_messenger as telegram_messenger
import util as util
import config

logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()



def send_message(title:str,content:str):
    if(config.USE_DINGTALK=="1"):
        message = util.format_dd_message(title,content)
        return dingtalk_messenger.send_message(message)
    else:
        message = util.format_telegram_message(title, content)
        return telegram_messenger.send_message(message)


if __name__ == "__main__":
    #test_data_integrity()
    send_message('测试发送钉钉机器人信息')