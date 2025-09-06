#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目配置文件
定义项目中使用的常量和配置项
"""


class Config:
    """项目配置类"""
    
    # MoneyPro支持的字段
    MONEYPRO_FIELDS = [
        '类别', '金额', '已收金额', '日期', '源账户', '目标账户',
        '描述', '代理', '货币', '检查编号', '时间'
    ]
    
    # 默认账户映射
    DEFAULT_ACCOUNT_MAP = {
        'alipay': '支付宝',
        'wechat': '微信',
        'bank': '银行'
    }
    
    # 默认输出目录
    DEFAULT_OUTPUT_DIR = 'output'