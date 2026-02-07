'''
给telegram发送信息
'''
import requests
import logging
from utility import secrets_config as secrets_config

logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()
secrest = secrets_config.load_external_config()

import config
proxies = {
    'http': config.HTTP_PROXY,
    'https': config.HTTPS_PROXY
}

def send_telegram_message(message):
    secrets = secrets_config.load_external_config()
    # 替换为你从 BotFather 获取的 Token
    token = secrets.get('TG_TOKEN')
    # 替换为你从 userinfobot 获取的 ID
    chat_id = secrets.get('CHAT_ID')


    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # 支持 HTML 格式，比如加粗、链接
    }

    try:
        response = requests.post(url, data=payload,proxies=proxies,timeout=10)
        print(response.text)
        if response.status_code == 200:
            print("信息发送成功！")
        else:
            print(f"发送失败，错误码：{response.status_code}")
    except Exception as e:
        print(f"发送出错：{e}")

if __name__ == "__main__":
    #test_data_integrity()
    send_telegram_message('测试发送telegram信息')