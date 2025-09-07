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

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bill_converter.config import Config


def convert_assets():
    """
    转换资产信息
    """
    # 原始资产目录
    raw_assets_dir = "原始资产"
    
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