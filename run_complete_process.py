#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整账单处理流程脚本
整合账单处理、导入Metabase和启动服务的完整流程
"""

import sys
import os
import subprocess
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bill_converter.main import auto_process_bills
from metabase.import_data import import_csv_to_sqlite, import_assets_to_sqlite


def run_docker_compose_command(command):
    """
    运行docker-compose命令
    """
    try:
        # 切换到metabase目录
        metabase_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metabase')
        
        # 执行命令
        result = subprocess.run(
            command, 
            cwd=metabase_dir, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"执行命令失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    except Exception as e:
        print(f"执行命令时出错: {e}")
        return False


def complete_process(auto_mode=True, start_services=True):
    """
    完整的账单处理流程
    1. 处理原始账单文件
    2. 处理原始资产文件
    3. 导入数据到Metabase
    4. 启动Metabase服务
    
    Args:
        auto_mode (bool): 是否使用自动模式处理账单
        start_services (bool): 是否启动Metabase服务
    """
    print("=" * 50)
    print("开始执行完整账单处理流程")
    print("=" * 50)
    
    # 步骤1: 处理原始账单文件
    print("\n步骤1: 处理原始账单文件")
    print("-" * 30)
    
    try:
        if auto_mode:
            print("使用自动模式处理raw_bills目录下的所有文件")
            auto_process_bills()
        else:
            print("请手动运行账单转换器:")
            print("cd bill_converter && python main.py")
            input("按回车键继续...")
    except Exception as e:
        print(f"处理账单文件时出错: {e}")
        return False
    
    # 步骤2: 处理原始资产文件
    print("\n步骤2: 处理原始资产文件")
    print("-" * 30)
    
    try:
        print("运行资产转换脚本...")
        # 切换到项目根目录并运行资产转换脚本
        project_root = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
            ['python', 'asset_converter.py'], 
            cwd=project_root, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            print(f"资产转换脚本执行失败: {result.stderr}")
            return False
            
        print(result.stdout)
        print("资产信息处理成功")
    except Exception as e:
        print(f"处理资产文件时出错: {e}")
        return False
    
    # 步骤3: 导入数据到Metabase
    print("\n步骤3: 导入数据到Metabase")
    print("-" * 30)
    
    try:
        # 导入账单数据
        print("正在导入账单数据...")
        bill_success = import_csv_to_sqlite()
        if not bill_success:
            print("账单数据导入失败")
            return False
        print("账单数据导入成功")
        
        # 导入资产数据
        print("正在导入资产数据...")
        asset_success = import_assets_to_sqlite()
        if not asset_success:
            print("资产数据导入失败")
            return False
        print("资产数据导入成功")
    except Exception as e:
        print(f"导入数据时出错: {e}")
        return False
    
    # 步骤4: 启动Metabase服务
    if start_services:
        print("\n步骤4: 启动Metabase服务")
        print("-" * 30)
        
        # 停止可能正在运行的服务
        print("停止可能正在运行的服务...")
        run_docker_compose_command(['docker-compose', 'down'])
        
        # 启动服务
        print("启动Metabase服务...")
        if not run_docker_compose_command(['docker-compose', 'up', '-d']):
            print("启动服务失败")
            return False
        
        print("Metabase服务已启动")
        print("\n服务访问信息:")
        print("- Metabase Web界面: https://billing.local")
        print("- 数据库文件路径(容器内): /metabase-data/billing.db")
        
        # 显示服务状态
        print("\n检查服务状态:")
        run_docker_compose_command(['docker-compose', 'ps'])
    
    print("\n" + "=" * 50)
    print("完整账单处理流程执行完成!")
    print("=" * 50)
    
    return True


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='完整账单处理流程')
    parser.add_argument('--no-services', action='store_true', 
                        help='不启动Metabase服务')
    parser.add_argument('--manual-bills', action='store_true',
                        help='手动处理账单（非自动模式）')
    
    args = parser.parse_args()
    
    # 执行完整流程
    success = complete_process(
        auto_mode=not args.manual_bills,
        start_services=not args.no_services
    )
    
    if success:
        print("\n✅ 所有步骤执行成功!")
        if not args.no_services:
            print("现在可以通过 https://billing.local 访问Metabase")
    else:
        print("\n❌ 执行过程中出现错误!")
        sys.exit(1)


if __name__ == '__main__':
    main()