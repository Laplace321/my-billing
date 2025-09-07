#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
资产信息转换脚本
将原始资产信息转换为带时间戳的CSV格式
"""

import os
import sys
import pandas as pd
from datetime import datetime
import socket
import requests

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from forex_python.converter import CurrencyRates
    FOREX_PYTHON_AVAILABLE = True
except ImportError:
    FOREX_PYTHON_AVAILABLE = False
    print("警告: forex-python包未安装，将使用预设汇率")

from bill_converter.config import Config


def get_exchange_rate(currency):
    """
    获取汇率（优先使用外部API获取实时汇率，失败时使用预设汇率）
    
    Args:
        currency: 货币代码
        
    Returns:
        对应货币到人民币的汇率
    """
    # 如果forex-python可用，尝试获取实时汇率
    if FOREX_PYTHON_AVAILABLE:
        try:
            # 设置网络超时
            socket.setdefaulttimeout(10)
            
            c = CurrencyRates()
            # 获取货币对人民币的汇率
            if currency == 'CNY':
                return 1.0
            
            # 对于其他货币，获取对美元的汇率，再通过美元对人民币的汇率计算
            rate_to_usd = c.get_rate(currency, 'USD', timeout=10)
            usd_to_cny = c.get_rate('USD', 'CNY', timeout=10)
            return round(rate_to_usd * usd_to_cny, 4)
        except requests.exceptions.Timeout:
            print(f"获取实时汇率超时，使用预设汇率")
        except requests.exceptions.ConnectionError:
            print(f"网络连接错误，无法获取实时汇率，使用预设汇率")
        except Exception as e:
            print(f"获取实时汇率失败: {e}，使用预设汇率")
    
    # 预设汇率（作为备选方案）
    exchange_rates = {
        'CNY': 1.0,
        'USD': 7.2,
        'EUR': 7.8,
        'JPY': 0.05,
        'HKD': 0.92,
    }
    
    return exchange_rates.get(currency, 1.0)


def convert_assets():
    """
    转换资产信息
    """
    # 原始资产目录
    raw_assets_dir = "raw_assets"
    
    # 检查原始资产目录是否存在
    if not os.path.exists(raw_assets_dir):
        print(f"错误: 原始资产目录不存在: {raw_assets_dir}")
        return False
    
    # 查找资产CSV文件
    asset_files = [f for f in os.listdir(raw_assets_dir) if f.endswith('.csv')]
    
    if not asset_files:
        print(f"错误: 在 {raw_assets_dir} 目录中未找到CSV文件")
        return False
    
    # 使用第一个CSV文件
    asset_file = asset_files[0]
    asset_file_path = os.path.join(raw_assets_dir, asset_file)
    
    try:
        # 读取资产信息
        print(f"正在读取资产文件: {asset_file_path}")
        df = pd.read_csv(asset_file_path)
        
        # 检查必要的列是否存在
        required_columns = ['账户分类', '币种', '金额', '描述']
        for col in required_columns:
            if col not in df.columns:
                print(f"错误: 缺少必要的列 '{col}'")
                return False
        
        # 添加时间戳列
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['时间'] = timestamp
        
        # 处理新增列：对应人民币金额
        def convert_to_cny(row):
            currency = row['币种']
            amount = row['金额']
            exchange_rate = get_exchange_rate(currency)
            return round(amount * exchange_rate, 2)
        
        print("正在处理汇率转换...")
        df['对应人民币金额'] = df.apply(convert_to_cny, axis=1)
        print("汇率转换完成")
        
        # 处理新增列：资产/负债
        def determine_asset_or_liability(account_type):
            if account_type == '信用卡':
                return '负债'
            else:
                return '资产'
        
        df['资产/负债'] = df['账户分类'].apply(determine_asset_or_liability)
        
        # 确保输出目录存在
        output_dir = os.path.join(Config.DEFAULT_OUTPUT_DIR, 'assets')
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成带时间戳的文件名
        timestamp_filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_asset.csv"
        output_path = os.path.join(output_dir, timestamp_filename)
        
        # 保存转换后的资产信息
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"资产信息已转换并保存到: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"转换资产信息时出错: {e}")
        return False


def main():
    """
    主函数
    """
    print("资产信息转换工具")
    print("=" * 30)
    
    success = convert_assets()
    
    if success:
        print("\n资产信息转换成功!")
    else:
        print("\n资产信息转换失败!")
        sys.exit(1)


if __name__ == '__main__':
    main()