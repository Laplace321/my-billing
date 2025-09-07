#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Metabase 数据导入脚本
将导出的账单 CSV 文件导入到 SQLite 数据库，供 Metabase 分析使用
"""

import os
import sys
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)
# 添加项目根目录到 Python 路径
sys.path.insert(0, project_root)

from bill_converter.config import Config


def generate_bill_key(row):
    """
    生成账单的主键
    主键由金额、日期、源账户、描述、代理决定，并使用MD5哈希避免过长字符串
    """
    # 处理可能的 NaN 值
    amount = str(row.get('金额', '') or '')
    date = str(row.get('日期', '') or '')
    source_account = str(row.get('源账户', '') or '')
    description = str(row.get('描述', '') or '')
    agent = str(row.get('代理', '') or '')
    
    # 组合主键字段
    key_string = f"{amount}_{date}_{source_account}_{description}_{agent}"
    
    # 使用MD5生成固定长度的哈希值
    return hashlib.md5(key_string.encode('utf-8')).hexdigest()


def import_csv_to_sqlite():
    """
    将 CSV 文件导入到 SQLite 数据库，支持增量追加去重写入
    """
    # 确保 metabase/data 目录存在
    data_dir = os.path.join(current_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # SQLite 数据库文件路径
    db_path = os.path.join(data_dir, 'billing.db')
    
    # CSV 文件路径（相对于项目根目录）
    csv_path = os.path.join(project_root, Config.DEFAULT_OUTPUT_DIR, 'final_merged_bills.csv')
    
    # 检查 CSV 文件是否存在
    if not os.path.exists(csv_path):
        print(f"错误: CSV 文件不存在: {csv_path}")
        print("请先运行账单转换器生成账单数据:")
        print("python bill_converter/main.py --auto")
        return False
    
    try:
        # 读取 CSV 文件
        print(f"正在读取 CSV 文件: {csv_path}")
        df = pd.read_csv(csv_path)
        
        # 标准化日期格式
        if '日期' in df.columns:
            try:
                # 尝试自动识别日期格式并统一转换
                df['日期'] = pd.to_datetime(df['日期'], errors='coerce').dt.strftime('%Y-%m-%d')
                # 重命名日期列为更规范的格式
                df.rename(columns={'日期': '交易日期'}, inplace=True)
            except Exception as e:
                print(f"日期格式转换时出错: {e}")
                # 如果转换失败，保留原始值但记录错误
                df['日期格式错误'] = str(e)
        
        # 添加主键列
        df['账单主键'] = df.apply(generate_bill_key, axis=1)
        
        # 更新时间列，使用当前数据生成时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df['时间'] = current_time
        
        # 处理列名，确保符合 SQLite 要求
        # 将列名中的特殊字符替换为下划线
        df.columns = [col.replace(' ', '_').replace('-', '_').replace('/', '_') for col in df.columns]
        
        # 处理空值
        df = df.fillna('')
        
        # 连接到 SQLite 数据库
        print(f"正在连接到数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # 检查表是否存在
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='billing_records'
        """)
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 表已存在，执行增量更新
            print("检测到现有账单数据，执行增量更新...")
            
            # 读取现有数据
            existing_df = pd.read_sql_query("SELECT * FROM billing_records", conn)
            
            if not existing_df.empty:
                # 合并新旧数据，去重
                merged_df = pd.concat([existing_df, df])
                # 基于账单主键去重，保留最新的记录
                merged_df = merged_df.drop_duplicates(subset=['账单主键'], keep='last')
                print(f"去重前记录数: {len(merged_df)}")
            else:
                merged_df = df
            
            # 更新数据表
            print(f"正在更新数据到表: billing_records")
            merged_df.to_sql('billing_records', conn, if_exists='replace', index=False)
            print(f"更新后记录数: {len(merged_df)}")
        else:
            # 表不存在，直接写入
            print(f"创建新表并导入数据到表: billing_records")
            df.to_sql('billing_records', conn, if_exists='replace', index=False)
            print(f"导入记录数: {len(df)}")
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        
        print("账单数据导入完成!")
        print(f"数据库路径: {db_path}")
        print(f"表名: billing_records")
        
        return True
        
    except Exception as e:
        print(f"导入账单数据时出错: {e}")
        return False


def import_assets_to_sqlite():
    """
    将资产 CSV 文件导入到 SQLite 数据库
    """
    # 确保 metabase/data 目录存在
    data_dir = os.path.join(current_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # SQLite 数据库文件路径
    db_path = os.path.join(data_dir, 'billing.db')
    
    # 资产文件目录
    assets_dir = os.path.join(Config.DEFAULT_OUTPUT_DIR, 'assets')
    
    # 检查资产目录是否存在
    if not os.path.exists(assets_dir):
        print(f"警告: 资产目录不存在: {assets_dir}")
        return True  # 不是错误，只是没有资产数据
    
    # 查找最新的资产CSV文件
    asset_files = [f for f in os.listdir(assets_dir) if f.endswith('.csv')]
    
    if not asset_files:
        print(f"警告: 在 {assets_dir} 目录中未找到资产CSV文件")
        return True  # 不是错误，只是没有资产数据
    
    # 按文件名排序，获取最新的文件
    asset_files.sort(reverse=True)
    latest_asset_file = asset_files[0]
    asset_file_path = os.path.join(assets_dir, latest_asset_file)
    
    try:
        # 读取资产 CSV 文件
        print(f"正在读取资产文件: {asset_file_path}")
        df = pd.read_csv(asset_file_path)
        
        # 处理列名，确保符合 SQLite 要求
        # 将列名中的特殊字符替换为下划线
        df.columns = [col.replace(' ', '_').replace('-', '_').replace('/', '_') for col in df.columns]
        
        # 处理空值
        df = df.fillna('')
        
        # 连接到 SQLite 数据库
        print(f"正在连接到数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # 将资产数据导入到 SQLite 数据库，使用append模式实现增量写入
        table_name = 'assets_records'
        print(f"正在导入资产数据到表: {table_name}")
        df.to_sql(table_name, conn, if_exists='append', index=False)
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        
        print("资产数据导入完成!")
        print(f"数据库路径: {db_path}")
        print(f"表名: {table_name}")
        print(f"记录数: {len(df)}")
        
        return True
        
    except Exception as e:
        print(f"导入资产数据时出错: {e}")
        return False


def main():
    """
    主函数
    """
    print("Metabase 数据导入工具")
    print("=" * 30)
    
    # 导入账单数据
    bill_success = import_csv_to_sqlite()
    
    # 导入资产数据
    asset_success = import_assets_to_sqlite()
    
    if bill_success and asset_success:
        print("\n数据导入成功!")
        print("现在可以启动 Metabase 进行数据分析:")
        print("cd metabase && docker-compose up -d")
    else:
        print("\n数据导入失败!")
        sys.exit(1)


if __name__ == '__main__':
    main()