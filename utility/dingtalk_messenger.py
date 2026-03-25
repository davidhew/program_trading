'''
给钉钉发送信息
'''
import io

import logging

import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json
from utility import secrets_config as secrets_config

logging.basicConfig(filename='../program_trading_log.log', level=logging.INFO)
logger = logging.getLogger()

secrets = secrets_config.load_external_config()
# 替换为你从 BotFather 获取的 Token
secret = secrets.get('DD_SECRET')
# 替换为你从 userinfobot 获取的 ID
webhook = secrets.get('DD_WEBHOOK')


def get_sign_url():
    """
    根据钉钉文档要求的加签算法生成带签名的 URL
    """

    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    # 拼接最终的 Webhook URL
    final_url = f"{webhook}&timestamp={timestamp}&sign={sign}"
    return final_url

def send_message(message,filename="analysis.txt"):
    url = get_sign_url()
    headers = {"Content-Type": "application/json"}
    # 构建消息体（Text类型）
    data = {
        "msgtype": "text",
        "text": {
            "content": message
        },
        "at": {
            "isAtAll": False  # 是否 @ 所有人
        }
    }
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            print("信息发送成功！")
        else:
            print(f"发送失败，错误码：{response.status_code}")

    except Exception as e:
        print(f"发送出错：{e}")



if __name__ == "__main__":
    #test_data_integrity()
    send_message('测试发送钉钉机器人信息')