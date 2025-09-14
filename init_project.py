#!/usr/bin/env python3
"""
项目初始化脚本
自动创建目录结构、安装依赖并设置基本环境
"""

import os
import subprocess
import sys
from pathlib import Path


def create_directory_structure():
    """创建必要的目录结构"""
    directories = [
        'raw_bills/alipay',
        'raw_bills/wechat',
        'raw_bills/bank',
        'raw_assets',
        'out/assets',
        'output'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"创建目录: {directory}")


def setup_virtual_environment():
    """设置Python虚拟环境"""
    print("正在创建虚拟环境...")
    try:
        subprocess.check_call([sys.executable, '-m', 'venv', 'venv'])
        print("虚拟环境创建完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"虚拟环境创建失败: {e}")
        return False


def install_dependencies():
    """在虚拟环境中安装项目依赖"""
    print("正在安装项目依赖...")
    try:
        # 使用虚拟环境中的pip安装依赖
        pip_path = os.path.join('venv', 'bin', 'pip')
        subprocess.check_call([pip_path, 'install', '-r', 'requirements.txt'])
        print("依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        sys.exit(1)


def setup_metabase():
    """初始化Metabase相关配置"""
    # 创建Metabase数据目录
    Path('metabase/data').mkdir(parents=True, exist_ok=True)
    print("Metabase目录初始化完成")


def main():
    """主函数"""
    print("开始初始化项目...")
    
    # 创建目录结构
    create_directory_structure()
    
    # 设置虚拟环境
    if setup_virtual_environment():
        # 安装依赖
        install_dependencies()
    
    # 初始化Metabase
    setup_metabase()
    
    print("项目初始化完成!")


if __name__ == "__main__":
    main()