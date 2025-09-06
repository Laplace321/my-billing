#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信账单解析器
用于解析微信账单文件
"""

import pandas as pd
import re


class WechatBillParser:
    """
    微信账单解析器类
    """
    
    def __init__(self):
        """
        初始化解析器
        """
        pass
    
    def parse_csv(self, file_path):
        """
        解析微信CSV格式账单
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            解析后的账单数据
        """
        # TODO: 实现具体的解析逻辑
        pass
    
    def parse_xlsx(self, file_path):
        """
        解析微信Excel格式账单
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            解析后的账单数据 (pandas DataFrame)
        """
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path)
            
            # 查找包含"交易时间"的行作为标题行
            header_row = None
            for i, row in df.iterrows():
                row_values = [str(val) for val in row.values if pd.notna(val)]
                row_text = ' '.join(row_values)
                if '交易时间' in row_text and '交易类型' in row_text:
                    header_row = i
                    print(f"找到标题行在第 {i} 行")
                    break
            
            if header_row is None:
                print("警告: 未找到标题行，使用默认标题行")
                header_row = 15  # 默认标题行位置
            
            # 重新读取Excel文件，设置正确的列标题
            df = pd.read_excel(file_path, header=header_row)
            
            # 重命名列，去除"Unnamed"列名
            new_columns = []
            for col in df.columns:
                if col.startswith('Unnamed:'):
                    # 使用上一行的值作为列名
                    new_columns.append(df.iloc[0][col])
                else:
                    new_columns.append(col)
            
            df.columns = new_columns
            # 删除第一行（原来的标题行）
            df = df.drop(df.index[0]).reset_index(drop=True)
            
            # 应用过滤逻辑
            df = self._apply_filters(df)
            
            # 处理交易时间字段
            if '交易时间' in df.columns:
                # 转换为datetime类型
                df['交易时间'] = pd.to_datetime(df['交易时间'])
                # 重命名列为英文
                df = df.rename(columns={'交易时间': 'transaction_time'})
            
            return df
            
        except Exception as e:
            print(f"解析微信账单时出错: {e}")
            return None
    
    def _apply_filters(self, df):
        """
        应用过滤逻辑
        
        Args:
            df: 原始数据
            
        Returns:
            过滤后的数据
        """
        original_count = len(df)
        
        # 过滤微信内部转账记录（同一交易对象的一对支出和收入）
        df = self._filter_internal_transfers(df)
        print(f"过滤内部转账记录后剩余 {len(df)} 条记录")
        
        filtered_count = len(df)
        if original_count != filtered_count:
            print(f"总共过滤了 {original_count - filtered_count} 条记录")
        
        return df
    
    def _filter_internal_transfers(self, df):
        """
        过滤微信内部转账记录（同一交易对象的一对支出和收入）
        
        Args:
            df: 原始数据
            
        Returns:
            过滤后的数据
        """
        if df.empty:
            return df
            
        # 获取所有唯一的交易对方
        if '交易对方' not in df.columns:
            return df
            
        unique_agents = df['交易对方'].unique()
        rows_to_drop = []
        
        for agent in unique_agents:
            # 获取该交易对方的所有记录
            agent_records = df[df['交易对方'] == agent]
            
            if len(agent_records) > 1:
                # 检查是否有金额相同但符号相反的记录（转账对）
                amounts = agent_records['金额(元)'].tolist()
                indices = agent_records.index.tolist()
                
                # 简单的配对逻辑：尝试将正负金额配对
                matched_indices = set()
                for i in range(len(amounts)):
                    if indices[i] in matched_indices:
                        continue
                        
                    amount_i = float(str(amounts[i]).replace('¥', '').replace(',', '').replace('−', '-'))
                    for j in range(i+1, len(amounts)):
                        if indices[j] in matched_indices:
                            continue
                            
                        amount_j = float(str(amounts[j]).replace('¥', '').replace(',', '').replace('−', '-'))
                        
                        # 如果金额相同但符号相反，则标记为需要删除的转账对
                        if abs(amount_i + amount_j) < 0.01 and amount_i * amount_j < 0:
                            rows_to_drop.extend([indices[i], indices[j]])
                            matched_indices.add(indices[i])
                            matched_indices.add(indices[j])
                            break
        
        # 删除标记的行
        if rows_to_drop:
            df = df.drop(rows_to_drop)
                    
        # 重置索引
        df = df.reset_index(drop=True)
            
        return df
    
    def parse_file(self, file_path):
        """
        根据文件扩展名自动选择解析方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的账单数据
        """
        if file_path.endswith('.xlsx'):
            return self.parse_xlsx(file_path)
        elif file_path.endswith('.csv'):
            return self.parse_csv(file_path)
        else:
            print(f"不支持的文件格式: {file_path}")
            return None