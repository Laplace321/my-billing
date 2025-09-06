#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
支付宝账单解析器
用于解析支付宝账单文件
"""

import pandas as pd
import re
import chardet


class AlipayBillParser:
    """
    支付宝账单解析器类
    """
    
    def __init__(self):
        """
        初始化解析器
        """
        pass
    
    def parse_csv(self, file_path):
        """
        解析支付宝CSV格式账单
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            解析后的账单数据 (pandas DataFrame)
        """
        try:
            # 检测文件编码
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # 读取前10000字节用于检测编码
                encoding_info = chardet.detect(raw_data)
                encoding = encoding_info['encoding']
                print(f"检测到文件编码: {encoding}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                lines = f.readlines()
            
            # 查找列标题行
            header_line_index = -1
            for i, line in enumerate(lines):
                if '交易创建时间' in line and '付款时间' in line and '交易对方' in line:
                    header_line_index = i
                    break
            
            if header_line_index == -1:
                print("未找到有效的列标题行")
                return None
            
            # 提取标题行和数据行
            header_line = lines[header_line_index].strip()
            data_lines = lines[header_line_index + 1:]
            
            # 处理标题行
            headers = [h.strip() for h in header_line.split(',')]
            
            # 处理数据行
            data_rows = []
            for line in data_lines:
                if line.strip():  # 跳过空行
                    # 简单按逗号分割，注意这可能不完美处理包含逗号的字段
                    row = [field.strip().strip('"').strip("'") for field in line.split(',')]
                    # 确保行数据长度与标题一致
                    if len(row) >= len(headers):
                        data_rows.append(row[:len(headers)])
            
            # 创建DataFrame
            if data_rows:
                df = pd.DataFrame(data_rows, columns=headers)
                # 应用过滤逻辑
                df = self._apply_filters(df)
                return df
            else:
                print("未解析到有效数据")
                return None
            
        except Exception as e:
            print(f"解析支付宝账单时出错: {e}")
            import traceback
            traceback.print_exc()
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
        
        # 过滤【收/支】类型为不计收支的记录，因其为内部交易订单，不需要计入账单
        if '收/支' in df.columns:
            df = df[df['收/支'] != '不计收支']
            print(f"过滤不计收支记录后剩余 {len(df)} 条记录")
        
        # 过滤支付宝余额/余额宝对花呗还款、银行账户对信用卡还款的记录
        df = self._filter_repayment_records(df)
        print(f"过滤还款记录后剩余 {len(df)} 条记录")
        
        filtered_count = len(df)
        if original_count != filtered_count:
            print(f"总共过滤了 {original_count - filtered_count} 条记录")
        
        return df
    
    def _filter_repayment_records(self, df):
        """
        过滤还款记录（花呗还款、信用卡还款等）
        
        Args:
            df: 原始数据
            
        Returns:
            过滤后的数据
        """
        if df.empty:
            return df
            
        # 创建过滤条件
        filter_condition = pd.Series([False] * len(df), index=df.index)
        
        # 检查商品名称和交易对方是否包含还款相关关键词
        repayment_keywords = ['花呗', '信用卡', '还款', '借款', '借呗', '贷款', '房贷', '车贷']
        
        for keyword in repayment_keywords:
            # 检查商品名称列
            if '商品名称' in df.columns:
                filter_condition |= df['商品名称'].str.contains(keyword, case=False, na=False)
            
            # 检查交易对方列
            if '交易对方' in df.columns:
                filter_condition |= df['交易对方'].str.contains(keyword, case=False, na=False)
        
        # 过滤掉匹配还款关键词的交易
        filtered_df = df[~filter_condition]
        
        print(f"还款记录过滤: 原始 {len(df)} 条记录，过滤后 {len(filtered_df)} 条记录")
        
        return filtered_df
    
    def parse_file(self, file_path):
        """
        根据文件扩展名自动选择解析方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的账单数据
        """
        if file_path.endswith('.csv'):
            return self.parse_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return self.parse_xlsx(file_path)
        else:
            print(f"不支持的文件格式: {file_path}")
            return None
    
    def parse_xlsx(self, file_path):
        """
        解析支付宝Excel格式账单
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            解析后的账单数据
        """
        # TODO: 实现具体的解析逻辑
        pass