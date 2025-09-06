#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
命令行接口
提供命令行方式使用账单转换器
"""

import click
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alipay.parser import AlipayBillParser
from wechat.parser import WechatBillParser
from bank.parser import BankBillParser
from moneypro.exporter import MoneyProExporter
from utils.converter import BillConverter


@click.group()
def cli():
    """账单转换器命令行工具"""
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='输入文件路径')
@click.option('--output', '-o', required=True, help='输出文件路径')
def alipay(input, output):
    """转换支付宝账单"""
    if not os.path.exists(input):
        click.echo(f"错误: 输入文件 {input} 不存在")
        return
    
    # 解析支付宝账单
    parser = AlipayBillParser()
    source_data = parser.parse_csv(input)
    
    # 转换为MoneyPro格式
    converter = BillConverter()
    moneypro_data = converter.convert_to_moneypro(source_data, 'alipay')
    
    # 导出为MoneyPro格式
    exporter = MoneyProExporter()
    if exporter.export_to_csv(moneypro_data, output):
        click.echo(f"成功导出到: {output}")
    else:
        click.echo("导出失败")


@cli.command()
@click.option('--input', '-i', required=True, help='输入文件路径')
@click.option('--output', '-o', required=True, help='输出文件路径')
def wechat(input, output):
    """转换微信账单"""
    if not os.path.exists(input):
        click.echo(f"错误: 输入文件 {input} 不存在")
        return
    
    # 解析微信账单
    parser = WechatBillParser()
    source_data = parser.parse_csv(input)
    
    # 转换为MoneyPro格式
    converter = BillConverter()
    moneypro_data = converter.convert_to_moneypro(source_data, 'wechat')
    
    # 导出为MoneyPro格式
    exporter = MoneyProExporter()
    if exporter.export_to_csv(moneypro_data, output):
        click.echo(f"成功导出到: {output}")
    else:
        click.echo("导出失败")


@cli.command()
@click.option('--input', '-i', required=True, help='输入文件路径')
@click.option('--output', '-o', required=True, help='输出文件路径')
@click.option('--bank', '-b', default='unknown', help='银行类型')
def bank(input, output, bank):
    """转换银行账单"""
    if not os.path.exists(input):
        click.echo(f"错误: 输入文件 {input} 不存在")
        return
    
    # 解析银行账单
    parser = BankBillParser()
    source_data = parser.parse_csv(input, bank)
    
    # 转换为MoneyPro格式
    converter = BillConverter()
    moneypro_data = converter.convert_to_moneypro(source_data, 'bank')
    
    # 导出为MoneyPro格式
    exporter = MoneyProExporter()
    if exporter.export_to_csv(moneypro_data, output):
        click.echo(f"成功导出到: {output}")
    else:
        click.echo("导出失败")


if __name__ == '__main__':
    cli()