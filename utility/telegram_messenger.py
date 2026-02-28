'''
给telegram发送信息
'''
import io
import requests
import logging
from . import secrets_config as secrets_config

logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()
secrest = secrets_config.load_external_config()

import config
proxies = {
    'http': config.HTTP_PROXY,
    'https': config.HTTPS_PROXY
}

secrets = secrets_config.load_external_config()
# 替换为你从 BotFather 获取的 Token
token = secrets.get('TG_TOKEN')
# 替换为你从 userinfobot 获取的 ID
chat_id = secrets.get('CHAT_ID')

def send_message(message):
    if(len(message)>4000):
        send_text_as_file(message)
    else:
        send_telegram_message(message)


def send_text_as_file(message, filename="analysis.txt"):


    url = f"https://api.telegram.org/bot{token}/sendDocument"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"  # 支持 HTML 格式，比如加粗、链接
    }

    # 将字符串转换为内存中的二进制流
    bio = io.BytesIO(message.encode('utf-8'))
    bio.name = filename  # Telegram 需要文件名来显示

    files = {'document': bio}
    payload = {'chat_id': chat_id, 'caption': "内容过长，已转为文件发送"}

    try:
        response=requests.post(url, data=payload, files=files,proxies=proxies,timeout=10)
        print(response.text)
        if response.status_code == 200:
            print("信息发送成功！")
        else:
            print(f"发送失败，错误码：{response.status_code}")

    except Exception as e:
        print(f"发送出错：{e}")


def send_telegram_message(message):

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