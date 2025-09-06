#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
账单转换器主程序
用于将支付宝、微信、银行信用卡等账单数据转换为MoneyPro格式
"""

import sys
import os
import argparse
import glob

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from alipay.parser import AlipayBillParser
from wechat.parser import WechatBillParser
from bank.parser import BankBillParser
from moneypro.exporter import MoneyProExporter
from utils.converter import BillConverter
from utils.deduplicator import BillDeduplicator


def main():
    print("欢迎使用账单转换器！")
    print("本工具将帮您将支付宝、微信、银行信用卡等账单数据转换为MoneyPro格式。")
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='账单转换器')
    parser.add_argument('--source', choices=['alipay', 'wechat', 'bank'], 
                        help='源账单类型')
    parser.add_argument('--input', help='输入文件路径')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--bank-type', default='unknown', help='银行类型（仅对银行账单有效）')
    parser.add_argument('--auto', action='store_true', help='自动处理原始账单目录下的所有文件')
    
    args = parser.parse_args()
    
    if args.auto:
        # 自动处理模式
        auto_process_bills()
    elif args.source and args.input and args.output:
        # 执行转换
        convert_bill(args.source, args.input, args.output, args.bank_type)
    else:
        # 交互式模式
        interactive_mode()


def convert_bill(source_type, input_path, output_path, bank_type='unknown'):
    """
    转换账单
    
    Args:
        source_type: 源账单类型
        input_path: 输入文件路径
        output_path: 输出文件路径
        bank_type: 银行类型
    """
    # 根据源类型选择解析器
    if source_type == 'alipay':
        parser = AlipayBillParser()
    elif source_type == 'wechat':
        parser = WechatBillParser()
    elif source_type == 'bank':
        parser = BankBillParser()
    else:
        print("不支持的源账单类型")
        return
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"输入文件不存在: {input_path}")
        return
    
    # 解析账单
    print(f"正在解析 {source_type} 账单...")
    # 这里需要根据文件扩展名选择解析方法
    if source_type == 'bank':
        source_data = parser.parse_file(input_path, bank_type)
    else:
        source_data = parser.parse_file(input_path)
    
    if source_data is None:
        print("解析失败")
        return
    
    # 转换为MoneyPro格式
    converter = BillConverter()
    moneypro_data = converter.convert_to_moneypro(source_data, source_type)
    
    if moneypro_data is None:
        print("转换失败")
        return
    
    # 导出为MoneyPro格式
    exporter = MoneyProExporter()
    if exporter.export_to_csv(moneypro_data, output_path):
        print(f"成功导出到: {output_path}")
    else:
        print("导出失败")


def auto_process_bills():
    """
    自动处理原始账单目录下的所有文件
    """
    raw_bills_dir = "/Users/laplacetong/My-billing/原始账单"
    output_dir = "/Users/laplacetong/My-billing/out"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"自动处理 {raw_bills_dir} 目录下的所有账单文件")
    
    # 查找所有账单文件
    bill_files = []
    
    # 支付宝账单
    alipay_files = glob.glob(os.path.join(raw_bills_dir, "alipay_record_*.csv"))
    bill_files.extend([(f, 'alipay') for f in alipay_files])
    
    # 微信账单
    wechat_files = glob.glob(os.path.join(raw_bills_dir, "微信支付账单流水文件*.xlsx"))
    bill_files.extend([(f, 'wechat') for f in wechat_files])
    
    # 银行账单
    bank_files = glob.glob(os.path.join(raw_bills_dir, "招商银行*.pdf"))
    bill_files.extend([(f, 'bank') for f in bank_files])
    
    if not bill_files:
        print("未找到任何账单文件")
        return
    
    # 解析所有账单
    parsers = {
        'alipay': AlipayBillParser(),
        'wechat': WechatBillParser(),
        'bank': BankBillParser()
    }
    
    bill_data_list = []
    for file_path, source_type in bill_files:
        print(f"正在解析账单: {file_path}")
        
        parser = parsers[source_type]
        if source_type == 'bank':
            # 默认银行类型为cmb（招商银行）
            source_data = parser.parse_file(file_path, 'cmb')
        else:
            source_data = parser.parse_file(file_path)
        
        if source_data is not None:
            # 转换为MoneyPro格式
            converter = BillConverter()
            moneypro_data = converter.convert_to_moneypro(source_data, source_type)
            if moneypro_data is not None:
                bill_data_list.append(moneypro_data)
                # 同时导出单个文件
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                output_path = os.path.join(output_dir, f"{name}_moneypro.csv")
                exporter = MoneyProExporter()
                exporter.export_to_csv(moneypro_data, output_path)
                print(f"成功解析并转换: {file_path} -> {output_path}")
            else:
                print(f"转换失败: {file_path}")
        else:
            print(f"解析失败: {file_path}")
    
    if not bill_data_list:
        print("没有成功解析的账单")
        return
    
    # 合并并去重
    print("正在合并并去重账单...")
    deduplicator = BillDeduplicator()
    merged_data = deduplicator.deduplicate_bills(bill_data_list)
    
    if merged_data is not None:
        # 导出结果
        output_path = os.path.join(output_dir, "final_merged_bills.csv")
        
        exporter = MoneyProExporter()
        if exporter.export_to_csv(merged_data, output_path):
            print(f"成功导出合并后的账单到: {output_path}")
        else:
            print("导出失败")
    else:
        print("合并失败")


def interactive_mode():
    """
    交互式模式
    """
    while True:
        print("\n请选择操作：")
        print("1. 转换支付宝账单")
        print("2. 转换微信账单")
        print("3. 转换银行账单")
        print("4. 合并多个账单并去重")
        print("5. 自动处理原始账单目录下的所有文件")
        print("0. 退出")
        
        choice = input("请输入选项 (0-5): ").strip()
        
        if choice == '1':
            convert_alipay_bill()
        elif choice == '2':
            convert_wechat_bill()
        elif choice == '3':
            convert_bank_bill()
        elif choice == '4':
            merge_and_deduplicate_bills()
        elif choice == '5':
            auto_process_bills()
            break
        elif choice == '0':
            print("感谢使用账单转换器！")
            break
        else:
            print("无效选项，请重新输入。")


def convert_alipay_bill():
    """
    转换支付宝账单
    """
    input_path = input("请输入支付宝账单文件路径: ").strip()
    if not input_path:
        print("文件路径不能为空")
        return
        
    if not os.path.exists(input_path):
        print(f"文件不存在: {input_path}")
        return
    
    output_path = input("请输入输出文件路径: ").strip()
    if not output_path:
        print("输出路径不能为空")
        return
    
    convert_bill('alipay', input_path, output_path)


def convert_wechat_bill():
    """
    转换微信账单
    """
    input_path = input("请输入微信账单文件路径: ").strip()
    if not input_path:
        print("文件路径不能为空")
        return
        
    if not os.path.exists(input_path):
        print(f"文件不存在: {input_path}")
        return
    
    output_path = input("请输入输出文件路径: ").strip()
    if not output_path:
        print("输出路径不能为空")
        return
    
    convert_bill('wechat', input_path, output_path)


def convert_bank_bill():
    """
    转换银行账单
    """
    input_path = input("请输入银行账单文件路径: ").strip()
    if not input_path:
        print("文件路径不能为空")
        return
        
    if not os.path.exists(input_path):
        print(f"文件不存在: {input_path}")
        return
    
    bank_type = input("请输入银行类型 (默认为cmb): ").strip()
    if not bank_type:
        bank_type = 'cmb'
    
    output_path = input("请输入输出文件路径: ").strip()
    if not output_path:
        print("输出路径不能为空")
        return
    
    convert_bill('bank', input_path, output_path, bank_type)


def merge_and_deduplicate_bills():
    """
    合并多个账单并去重
    """
    print("合并多个账单并去重功能")
    print("请依次输入账单文件路径，输入空行结束：")
    
    bill_files = []
    while True:
        file_path = input("请输入账单文件路径: ").strip()
        if not file_path:
            break
            
        if os.path.exists(file_path):
            bill_files.append(file_path)
            print(f"已添加: {file_path}")
        else:
            print(f"文件不存在: {file_path}")
    
    if not bill_files:
        print("未添加任何账单文件")
        return
    
    # 解析所有账单
    parsers = {
        'alipay': AlipayBillParser(),
        'wechat': WechatBillParser(),
        'bank': BankBillParser()
    }
    
    bill_data_list = []
    for file_path in bill_files:
        print(f"正在解析账单: {file_path}")
        
        # 根据文件扩展名判断账单类型
        if 'alipay' in file_path.lower():
            parser = parsers['alipay']
            source_data = parser.parse_file(file_path)
            source_type = 'alipay'
        elif 'wechat' in file_path.lower() or '微信' in file_path:
            parser = parsers['wechat']
            source_data = parser.parse_file(file_path)
            source_type = 'wechat'
        elif '银行' in file_path or 'bank' in file_path.lower():
            parser = parsers['bank']
            # 默认银行类型为cmb（招商银行）
            source_data = parser.parse_file(file_path, 'cmb')
            source_type = 'bank'
        else:
            print(f"无法识别账单类型: {file_path}")
            continue
        
        if source_data is not None:
            # 转换为MoneyPro格式
            converter = BillConverter()
            moneypro_data = converter.convert_to_moneypro(source_data, source_type)
            if moneypro_data is not None:
                bill_data_list.append(moneypro_data)
                print(f"成功解析并转换: {file_path}")
            else:
                print(f"转换失败: {file_path}")
        else:
            print(f"解析失败: {file_path}")
    
    if not bill_data_list:
        print("没有成功解析的账单")
        return
    
    # 合并并去重
    print("正在合并并去重账单...")
    deduplicator = BillDeduplicator()
    merged_data = deduplicator.deduplicate_bills(bill_data_list)
    
    if merged_data is not None:
        # 导出结果
        output_path = input("请输入合并后文件的输出路径 (默认为output/final_merged_bills.csv): ").strip()
        if not output_path:
            output_path = "output/final_merged_bills.csv"
        
        exporter = MoneyProExporter()
        if exporter.export_to_csv(merged_data, output_path):
            print(f"成功导出合并后的账单到: {output_path}")
        else:
            print("导出失败")
    else:
        print("合并失败")


if __name__ == '__main__':
    main()