#!/bin/bash

# 构建资产管理系统前端应用

echo "开始构建资产管理系统..."

# 创建dist目录（如果不存在）
mkdir -p dist

# 构建前端应用
npm run build

# 检查构建是否成功
if [ $? -eq 0 ]; then
    echo "前端应用构建成功！"
    echo "构建文件已放置在 dist/ 目录中"
    echo "运行 python run_complete_process.py 启动完整服务"
else
    echo "构建失败，请检查错误信息"
    exit 1
fi