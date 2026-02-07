'''
测试美国市场的成分
'''

import sys
import os.path
import config
import time
from functools import lru_cache

import pandas as pd
import requests
import logging
import unittest
class TestUSStocks(unittest.TestCase):
    def test_us_stocks(self):
        df = pd.read_csv(config.USA_STOCK_DIR+"stock_list.csv")
        print("cool!")



if __name__ == "__main__":
    unittest.main()