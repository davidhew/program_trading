'''
获取一些敏感配置信息，比如相关的token等
'''
import json
import logging
import config
from pathlib import Path
from typing import Any,Dict

EXTERNAL_CONFIG_PATH=config.SECRET_CONFIG_PATH


def load_external_config() -> Dict[str, Any]:
    """
    从项目外部指定的绝对路径加载敏感配置。
    """
    path = Path(config.SECRET_CONFIG_PATH)

    if not path.exists():
        # 如果文件不存在，抛出异常提醒，防止程序带空配置运行
        raise FileNotFoundError(f"致命错误：未在 {config.SECRET_CONFIG_PATH} 找到配置文件！请检查路径。")

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)