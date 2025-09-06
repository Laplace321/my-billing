#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
支付宝账单解析器测试
"""

import sys
import os
import unittest
import pandas as pd
from unittest.mock import patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alipay.parser import AlipayBillParser


class TestAlipayBillParser(unittest.TestCase):
    
    def setUp(self):
        """测试前准备"""
        self.parser = AlipayBillParser()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, AlipayBillParser)
    
    @patch('pandas.read_csv')
    def test_parse_csv(self, mock_read_csv):
        """测试CSV解析功能"""
        # 模拟pandas读取CSV的结果
        mock_df = pd.DataFrame({
            '交易时间': ['2023-01-01 10:00:00'],
            '交易名称': ['测试交易'],
            '金额': [100.00],
            '收/支': ['支出']
        })
        mock_read_csv.return_value = mock_df
        
        # 调用被测试的方法
        result = self.parser.parse_csv('test_alipay.csv')
        
        # 验证结果
        mock_read_csv.assert_called_once_with('test_alipay.csv')
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()