#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
账单转换器工具类
提供基础的转换功能和通用方法
"""

import datetime
import pandas as pd
import os
import sys
import json
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

# 导入jieba分词库
try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    print("警告: 未安装jieba库，将使用基础分词方法")


class BillConverter:
    """
    账单转换器基类
    """
    
    def __init__(self):
        """
        初始化转换器
        """
        self.config = Config()
        # 加载分类关键词
        self.category_keywords = self._load_category_keywords()
        # 构建关键词索引以提高匹配效率
        self.keyword_index = self._build_keyword_index()
    
    def _load_category_keywords(self):
        """
        加载分类关键词词典
        
        Returns:
            分类关键词字典
        """
        try:
            keywords_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'category_keywords.json')
            with open(keywords_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载分类关键词失败: {e}")
            # 返回默认关键词
            return {
                '食品': {
                    'keywords': ['淘宝闪购', '肯德基', '食品', '霸王茶姬', '鲜丰水果', '粥皇港式茶餐厅', 
                            'KFC', '麦当劳', '星巴克', '面包', '零食'],
                    'word_dict': ['食品', '水果', '蔬菜', '肉类', '海鲜', '粮油', '调料', '饮料', 
                            '酒水', '糖果', '巧克力', '坚果', '早餐', '午餐', '晚餐', '外卖', 
                            '餐厅', '饭店', '火锅', '烧烤', '奶茶', '咖啡', '奶茶店', '咖啡厅', 
                            '快餐', '熟食', '糕点', '甜品', '面包', '零食', '麦当劳', '肯德基', 
                            '星巴克', '霸王茶姬', '鲜丰水果', '粥皇', '火锅', '烧烤', '拿铁',
                            '汉堡', '薯条', '可乐', '雪碧', '包子', '馒头', '面条', '米饭', 
                            '炒菜', '盒饭', '便当', '寿司', '拉面', '饺子', '智盘消费', '点餐',
                            '餐台', '煲汤', '菌菇', '白塔店', '饮用水', '售货柜', '桃源人家', 
                            '炉上夜档', 'Manner', 'Coffee', '盒马', '菜鸟', '总部店',
                            '二维码', '支付', '台州市', '新荣', '实业', '有限公司', '美团']
                },
                '服装': {
                    'keywords': ['耐克', '阿迪达斯', '优衣库', 'ZARA', 'H&M', '服装', '鞋子', '衣服',
                            '裤子', '裙子', '内衣', '袜子', '帽子', '围巾', '手套', '皮带',
                            '包包', '箱包', '饰品', '首饰', '手表', '眼镜', '运动', '休闲',
                            '外套', 'T恤', '牛仔裤', '连衣裙', '高跟鞋', '运动鞋', '皮鞋'],
                    'word_dict': ['服装', '鞋子', '衣服', '裤子', '裙子', '内衣', '袜子', '帽子', 
                            '围巾', '手套', '皮带', '包包', '箱包', '饰品', '首饰', '手表', 
                            '眼镜', '运动', '休闲', '耐克', '阿迪达斯', '优衣库', 'ZARA', 'H&M',
                            '外套', 'T恤', '牛仔裤', '连衣裙', '高跟鞋', '运动鞋', '皮鞋']
                },
                '交通': {
                    'keywords': ['高德打车', '滴滴打车', '出租车', '地铁', '公交', '火车票', '机票', 
                            'uber', '出行', '高铁', '飞机', '轮船', '共享单车', '共享汽车',
                            '加油', '停车费', '过路费', '停车', '加油站', '停车', '过路',
                            '出租车', 'uber', '打车', '高速', '动车', '航班', '班机'],
                    'word_dict': ['高德打车', '滴滴打车', '出租车', '地铁', '公交', '火车票', '机票', 
                            'uber', '出行', '高铁', '飞机', '轮船', '共享单车', '共享汽车',
                            '加油', '停车费', '过路费', '停车', '加油站', '过路', '交通',
                            '打车', '高速', '动车', '航班', '班机', '浙江高速']
                }
            }
    
    def _build_keyword_index(self):
        """
        构建关键词索引以提高匹配效率
        
        Returns:
            关键词索引字典，格式为 {关键词: 类别}
        """
        keyword_index = {}
        for category, category_info in self.category_keywords.items():
            # 添加keywords中的关键词
            keywords = category_info.get('keywords', [])
            for keyword in keywords:
                # 处理转义字符
                keyword = keyword.replace('\\', '')
                keyword_index[keyword.lower()] = category
            
            # 添加word_dict中的关键词
            word_dict = category_info.get('word_dict', [])
            for word in word_dict:
                # 处理转义字符
                word = word.replace('\\', '')
                keyword_index[word.lower()] = category
        
        return keyword_index
    
    def _segment_text(self, text):
        """
        对文本进行分词处理
        
        Args:
            text: 待分词的文本
            
        Returns:
            分词结果列表
        """
        if not isinstance(text, str):
            return []
        
        # 如果jieba可用，使用jieba分词
        if JIEBA_AVAILABLE:
            return list(jieba.cut(text))
        else:
            # 基础分词方法：按空格和常见分隔符分割
            return re.split(r'[\s\-_,，。！？；;]', text.lower())
    
    def convert_to_moneypro(self, source_data, source_type):
        """
        将源数据转换为MoneyPro格式
        
        Args:
            source_data: 源账单数据 (pandas DataFrame)
            source_type: 源数据类型 ('alipay', 'wechat', 'bank')
            
        Returns:
            转换后的MoneyPro格式数据 (pandas DataFrame)
        """
        if source_data is None:
            return None
            
        # 根据不同的源类型进行转换
        if source_type == 'alipay':
            return self._convert_alipay_data(source_data)
        elif source_type == 'wechat':
            return self._convert_wechat_data(source_data)
        elif source_type == 'bank':
            return self._convert_bank_data(source_data)
        
        return None
    
    def _parse_bank_date(self, date_str):
        """
        解析银行账单中的日期字符串，转换为标准格式
        
        Args:
            date_str: 原始日期字符串
            
        Returns:
            标准格式的日期字符串，解析失败返回原始字符串
        """
        if not isinstance(date_str, str):
            return date_str
            
        # 去除前后空格
        date_str = date_str.strip()
        
        # 尝试不同的日期格式解析
        for date_format in self.config.BANK_DATE_FORMATS:
            try:
                # 尝试解析日期
                parsed_date = datetime.strptime(date_str, date_format)
                # 返回标准格式的日期
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue  # 如果当前格式不匹配，尝试下一个格式
        
        # 如果所有格式都不匹配，返回原始字符串
        return date_str
    
    def _convert_alipay_data(self, data):
        """
        转换支付宝数据为MoneyPro格式
        
        Args:
            data: 支付宝账单数据 (pandas DataFrame)
            
        Returns:
            转换后的数据 (pandas DataFrame)
        """
        if data is None or data.empty:
            return None
            
        # 创建结果DataFrame
        result = pd.DataFrame(columns=self.config.MONEYPRO_FIELDS)
        
        # 映射支付宝字段到MoneyPro字段
        # 日期字段映射
        if '付款时间' in data.columns:
            result['日期'] = data['付款时间']
        elif '交易创建时间' in data.columns:
            result['日期'] = data['交易创建时间']
        elif '最近修改时间' in data.columns:
            result['日期'] = data['最近修改时间']
        
        # 金额字段映射
        if '金额（元）' in data.columns:
            # 根据收支情况调整金额正负
            def process_amount(row):
                amount = self._convert_amount(row['金额（元）'])
                if '收/支' in row and row['收/支'] == '收入':
                    return abs(amount)
                elif '收/支' in row and row['收/支'] == '支出':
                    return -abs(amount)
                return amount
            
            result['金额'] = data.apply(process_amount, axis=1)
        elif '金额' in data.columns:
            result['金额'] = data['金额'].apply(self._convert_amount)
            
        # 描述字段映射
        if '商品名称' in data.columns:
            result['描述'] = data['商品名称']
        elif '商品说明' in data.columns:
            result['描述'] = data['商品说明']
        elif '交易名称' in data.columns:
            result['描述'] = data['交易名称']
            
        # 类别字段映射
        if '交易分类' in data.columns:
            result['类别'] = data['交易分类']
        elif '类型' in data.columns:
            result['类别'] = data['类型']
            
        # 应用类别转换逻辑
        def classify_row(row_index):
            # 获取当前行的数据
            row_data = data.iloc[row_index]
            description = row_data['商品名称'] if '商品名称' in data.columns else ''
            counterparty = row_data['交易对方'] if '交易对方' in data.columns else ''
            return self._classify_transaction(description, counterparty)
        
        result['类别'] = [classify_row(i) for i in range(len(data))]
            
        # 代理字段映射
        if '交易对方' in data.columns:
            result['代理'] = data['交易对方']
            
        # 源账户字段（默认为支付宝）
        result['源账户'] = '支付宝'
        
        # 货币字段（默认为人民币）
        result['货币'] = 'CNY'
        
        return result
    
    def _convert_wechat_data(self, data):
        """
        转换微信数据为MoneyPro格式
        
        Args:
            data: 微信账单数据 (pandas DataFrame)
            
        Returns:
            转换后的数据 (pandas DataFrame)
        """
        if data is None or data.empty:
            return None
            
        # 创建结果DataFrame
        result = pd.DataFrame(columns=self.config.MONEYPRO_FIELDS)
        
        # 映射微信字段到MoneyPro字段
        # 日期字段映射
        date_columns = ['交易时间', '----------------------微信支付账单明细列表--------------------']
        for col in date_columns:
            if col in data.columns:
                result['日期'] = data[col]
                break
        
        # 金额字段映射
        if '金额(元)' in data.columns:
            # 根据收支情况调整金额正负
            def process_amount(row):
                amount = self._convert_amount(row['金额(元)'])
                if '收/支' in row and row['收/支'] == '收入':
                    return abs(amount)
                elif '收/支' in row and row['收/支'] == '支出':
                    return -abs(amount)
                return amount
            
            result['金额'] = data.apply(process_amount, axis=1)
        
        # 描述字段映射
        description_columns = ['商品', '交易类型']
        for col in description_columns:
            if col in data.columns:
                result['描述'] = data[col]
                break
        else:
            # 如果没有找到描述列，尝试合并多个列
            desc_parts = []
            for col in ['交易类型', '交易对方', '商品']:
                if col in data.columns:
                    desc_parts.append(data[col].astype(str))
            
            if desc_parts:
                if len(desc_parts) == 1:
                    result['描述'] = desc_parts[0]
                else:
                    result['描述'] = pd.concat(desc_parts, axis=1).apply(lambda x: ' '.join(x), axis=1)
        
        # 类别字段映射
        result['类别'] = '其他'
        
        # 应用类别转换逻辑
        def classify_row(row_index):
            # 获取当前行的数据
            row_data = data.iloc[row_index]
            description = str(row_data['商品']) if '商品' in data.columns else ''
            counterparty = str(row_data['交易对方']) if '交易对方' in data.columns else ''
            # 如果是交易类型列，也考虑进去
            transaction_type = str(row_data['交易类型']) if '交易类型' in data.columns else ''
            # 合并描述信息
            full_description = f"{description} {counterparty} {transaction_type}".strip()
            return self._classify_transaction(full_description, counterparty)
        
        result['类别'] = [classify_row(i) for i in range(len(data))]
        
        # 代理字段映射
        if '交易对方' in data.columns:
            result['代理'] = data['交易对方']
            
        # 源账户字段（默认为微信）
        result['源账户'] = '微信'
        
        # 货币字段（默认为人民币）
        result['货币'] = 'CNY'
        
        return result
    
    def _convert_bank_data(self, data):
        """
        转换银行数据为MoneyPro格式
        
        Args:
            data: 银行账单数据 (pandas DataFrame)
            
        Returns:
            转换后的数据 (pandas DataFrame)
        """
        if data is None or data.empty:
            return None
            
        # 创建结果DataFrame
        result = pd.DataFrame(columns=self.config.MONEYPRO_FIELDS)
        
        # 映射银行字段到MoneyPro字段
        # 日期字段映射
        if '交易日期' in data.columns:
            result['日期'] = data['交易日期']
        
        # 金额字段映射
        if '金额' in data.columns:
            def process_amount(amount_str):
                # 银行账单中的金额可能包含正负号
                # 先提取正负号
                sign = 1
                if isinstance(amount_str, str):
                    amount_str = amount_str.strip()
                    if amount_str.startswith('-'):
                        sign = -1
                        amount_str = amount_str[1:]
                    elif amount_str.startswith('+'):
                        amount_str = amount_str[1:]
                
                # 使用_convert_amount方法转换金额
                amount = self._convert_amount(amount_str)
                return amount * sign
            
            result['金额'] = data['金额'].apply(process_amount)
        
        # 描述字段映射
        if '交易类型' in data.columns:
            result['描述'] = data['交易类型']
        
        # 代理字段映射
        if '交易对方' in data.columns:
            result['代理'] = data['交易对方']
            
        # 源账户字段（默认为银行）
        result['源账户'] = '银行'
        
        # 货币字段（默认为人民币）
        result['货币'] = 'CNY'
        
        # 应用类别转换逻辑
        def classify_row(row_index):
            # 获取当前行的数据
            row_data = data.iloc[row_index]
            description = row_data['交易类型'] if '交易类型' in data.columns else ''
            counterparty = row_data['交易对方'] if '交易对方' in data.columns else ''
            return self._classify_transaction(description, counterparty)
        
        result['类别'] = [classify_row(i) for i in range(len(data))]
        
        return result
    
    def _classify_transaction(self, description, counterparty):
        """
        根据描述和交易对方对交易进行分类
        
        Args:
            description: 商品描述
            counterparty: 交易对方
            
        Returns:
            分类结果
        """
        # 特殊处理：支付宝转账给a.k.a. 小黄蜂的记录分类为亲属类
        if 'a.k.a. 小黄蜂' in str(counterparty) and ('转账' in str(description) or 'Transfer' in str(description)):
            return '亲属'
        
        # 合并描述和交易对方用于关键词搜索
        text_for_search = (str(description) + " " + str(counterparty)).lower()
        
        # 首先使用关键词索引进行快速匹配
        # 直接匹配整个文本
        if text_for_search in self.keyword_index:
            return self.keyword_index[text_for_search]
        
        # 尝试匹配较长的关键词组合
        # 按空格分割文本，尝试不同的组合
        text_parts = text_for_search.split()
        for i in range(len(text_parts)):
            for j in range(i+1, len(text_parts)+1):
                combined_text = ' '.join(text_parts[i:j])
                if combined_text in self.keyword_index:
                    return self.keyword_index[combined_text]
        
        # 分词匹配
        words = self._segment_text(text_for_search)
        for word in words:
            if word in self.keyword_index:
                return self.keyword_index[word]
        
        # 使用分词方法进行更准确的分类
        best_category = self._classify_with_word_segmentation(text_for_search)
        if best_category:
            return best_category
        
        # 无法识别，归为其他
        return '其他'
    
    def _classify_with_word_segmentation(self, text):
        """
        使用分词方法进行分类
        
        Args:
            text: 待分类的文本
            
        Returns:
            分类结果，如果没有匹配则返回None
        """
        # 使用分词方法
        words = self._segment_text(text)
        
        # 统计每个类别匹配的词数
        category_scores = {}
        
        for category, category_info in self.category_keywords.items():
            word_dict = category_info.get('word_dict', [])
            score = 0
            for word in words:
                if word in [w.lower() for w in word_dict]:
                    score += 1
            if score > 0:
                category_scores[category] = score
        
        # 返回得分最高的类别
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return None
    
    def _convert_amount(self, amount_str):
        """
        转换金额字符串为数值，并根据收支情况调整正负号
        
        Args:
            amount_str: 金额字符串，如 "¥25.00" 或 "25.00"
            
        Returns:
            转换后的金额数值
        """
        if not isinstance(amount_str, str):
            return amount_str
            
        # 去除货币符号和千位分隔符
        amount_str = amount_str.replace('¥', '').replace('￥', '').replace(',', '').strip()
        
        try:
            amount = float(amount_str)
            return amount
        except ValueError:
            return 0.0
    
    def save_to_csv(self, data, output_path):
        """
        将数据保存为CSV格式
        
        Args:
            data: 要保存的数据 (pandas DataFrame)
            output_path: 输出文件路径
        """
        if data is None:
            return False
            
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            data.to_csv(output_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False