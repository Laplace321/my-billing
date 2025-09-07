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

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
project_root = os.path.dirname(current_dir)
# 添加项目根目录到 Python 路径
sys.path.insert(0, project_root)

from bill_converter.config import Config


def import_csv_to_sqlite():
    """
    将 CSV 文件导入到 SQLite 数据库
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
        
        # 处理列名，确保符合 SQLite 要求
        # 将列名中的特殊字符替换为下划线
        df.columns = [col.replace(' ', '_').replace('-', '_').replace('/', '_') for col in df.columns]
        
        # 处理空值
        df = df.fillna('')
        
        # 连接到 SQLite 数据库
        print(f"正在连接到数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # 将数据导入到 SQLite 数据库
        table_name = 'billing_records'
        print(f"正在导入数据到表: {table_name}")
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        
        print("数据导入完成!")
        print(f"数据库路径: {db_path}")
        print(f"表名: {table_name}")
        print(f"记录数: {len(df)}")
        
        return True
        
    except Exception as e:
        print(f"导入数据时出错: {e}")
        return False


def main():
    """
    主函数
    """
    print("Metabase 数据导入工具")
    print("=" * 30)
    
    success = import_csv_to_sqlite()
    
    if success:
        print("\n数据导入成功!")
        print("现在可以启动 Metabase 进行数据分析:")
        print("cd metabase && docker-compose up -d")
    else:
        print("\n数据导入失败!")
        sys.exit(1)


if __name__ == '__main__':
    main()