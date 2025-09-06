#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
银行账单解析器
用于解析银行信用卡账单文件
"""

import pandas as pd
import PyPDF2
import re


class BankBillParser:
    """
    银行账单解析器类
    """
    
    def __init__(self):
        """
        初始化解析器
        """
        pass
    
    def parse_csv(self, file_path, bank_type="unknown"):
        """
        解析银行CSV格式账单
        
        Args:
            file_path: CSV文件路径
            bank_type: 银行类型
            
        Returns:
            解析后的账单数据
        """
        # TODO: 实现具体的解析逻辑
        pass
    
    def parse_pdf(self, file_path, bank_type="cmb"):
        """
        解析银行PDF格式账单
        
        Args:
            file_path: PDF文件路径
            bank_type: 银行类型 (默认招商银行 cmb)
            
        Returns:
            解析后的账单数据 (pandas DataFrame)
        """
        if bank_type == "cmb":  # 招商银行
            return self._parse_cmb_pdf(file_path)
        else:
            print(f"暂不支持的银行类型: {bank_type}")
            return None
    
    def _parse_cmb_pdf(self, file_path):
        """
        解析招商银行PDF格式账单
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            解析后的账单数据 (pandas DataFrame)
        """
        try:
            transactions = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 遍历每一页
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    
                    # 查找交易记录
                    lines = text.split('\n')
                    
                    for line in lines:
                        # 更灵活的正则表达式匹配
                        # 匹配模式：日期 货币 金额 余额 交易类型 交易对方
                        pattern = r'(\d{4}-\d{2}-\d{2})\s+([A-Z]{3})\s+([-,]?\d+(?:,\d{3})*\.\d{2})\s+([-,]?\d+(?:,\d{3})*\.\d{2})\s+(.+?)\s+(.+)'
                        match = re.search(pattern, line)
                        
                        if match:
                            date = match.group(1)
                            currency = match.group(2)
                            amount = match.group(3).replace(',', '')  # 移除千位分隔符
                            balance = match.group(4)  # 余额字段
                            transaction_type = match.group(5)
                            counter_party = match.group(6)
                            
                            transactions.append({
                                '交易日期': date,
                                '货币': currency,
                                '金额': amount,
                                '余额': balance,
                                '交易类型': transaction_type,
                                '交易对方': counter_party
                            })
            
            # 转换为DataFrame
            if transactions:
                df = pd.DataFrame(transactions)
                
                # 将金额转换为数值类型
                df['金额'] = pd.to_numeric(df['金额'])
                
                # 添加一个用于去重的原始日期字段，只包含日期部分
                df['_raw_date'] = df['交易日期']
                
                # 将交易日期格式化为 yyyy-MM-dd hh:mm:ss 格式，填充默认时间 00:00:00
                df['交易日期'] = df['交易日期'] + ' 00:00:00'
                
                # 应用过滤逻辑（去除还款记录和投资记录）
                df = self._apply_filters(df)
                
                # 按日期排序
                if '交易日期' in df.columns:
                    df = df.sort_values('交易日期')
                
                return df
            else:
                print("未解析到有效的银行账单记录")
                return None
                
        except Exception as e:
            print(f"解析银行PDF账单时出错: {e}")
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
        
        # 过滤银行账户对信用卡还款的记录
        df = self._filter_repayment_records(df)
        print(f"过滤还款记录后剩余 {len(df)} 条记录")
        
        # 过滤投资类记录
        df = self._filter_investment_records(df)
        print(f"过滤投资记录后剩余 {len(df)} 条记录")
        
        filtered_count = len(df)
        if original_count != filtered_count:
            print(f"总共过滤了 {original_count - filtered_count} 条记录")
        
        return df
    
    def _filter_repayment_records(self, df):
        """
        过滤还款记录（银行账户对信用卡还款）
        
        Args:
            df: 原始数据
            
        Returns:
            过滤后的数据
        """
        if df.empty:
            return df
            
        # 创建过滤条件
        filter_condition = pd.Series([False] * len(df), index=df.index)
        
        # 检查交易类型和交易对方是否包含还款相关关键词
        repayment_keywords = ['信用卡', '还款']
        
        for keyword in repayment_keywords:
            if '交易类型' in df.columns:
                filter_condition |= df['交易类型'].str.contains(keyword, case=False, na=False)
            if '交易对方' in df.columns:
                filter_condition |= df['交易对方'].str.contains(keyword, case=False, na=False)
        
        # 过滤掉匹配还款关键词的交易
        filtered_df = df[~filter_condition]
        
        print(f"银行还款记录过滤: 原始 {len(df)} 条记录，过滤后 {len(filtered_df)} 条记录")
        
        return filtered_df
    
    def _filter_investment_records(self, df):
        """
        过滤投资类记录（如朝朝宝、理财产品等）
        
        Args:
            df: 原始数据
            
        Returns:
            过滤后的数据
        """
        if df.empty:
            return df
            
        # 创建过滤条件
        filter_condition = pd.Series([False] * len(df), index=df.index)
        
        # 投资相关关键词
        investment_keywords = [
            '朝朝宝', '理财', '基金', '收益', '分红', '利息', '赎回', 
            '申购', '定投', '余额宝', '招银理财', '货币基金', '嘉实货币'
        ]
        
        for keyword in investment_keywords:
            if '交易类型' in df.columns:
                filter_condition |= df['交易类型'].str.contains(keyword, case=False, na=False)
            if '交易对方' in df.columns:
                filter_condition |= df['交易对方'].str.contains(keyword, case=False, na=False)
        
        # 过滤掉匹配投资关键词的交易
        filtered_df = df[~filter_condition]
        
        print(f"银行投资记录过滤: 原始 {len(df)} 条记录，过滤后 {len(filtered_df)} 条记录")
        
        return filtered_df
    
    def parse_file(self, file_path, bank_type="unknown"):
        """
        根据文件扩展名自动选择解析方法
        
        Args:
            file_path: 文件路径
            bank_type: 银行类型
            
        Returns:
            解析后的账单数据
        """
        if file_path.endswith('.pdf'):
            return self.parse_pdf(file_path, bank_type)
        elif file_path.endswith('.csv'):
            return self.parse_csv(file_path, bank_type)
        else:
            print(f"不支持的文件格式: {file_path}")
            return None