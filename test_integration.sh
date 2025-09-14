#!/bin/bash

# 集成测试脚本
# 测试资产管理系统与Metabase的集成

echo "开始测试集成服务..."

# 测试1: 检查资产管理系统界面
echo "测试1: 检查资产管理系统界面"
response=$(curl -k -s -o /dev/null -w "%{http_code}" https://billing.local/assets/)
if [ "$response" -eq 200 ]; then
    echo "✅ 资产管理系统界面访问正常"
else
    echo "❌ 资产管理系统界面访问失败 (HTTP $response)"
fi

# 测试2: 检查资产管理系统API
echo "测试2: 检查资产管理系统API"
response=$(curl -k -s -o /dev/null -w "%{http_code}" https://billing.local/api/assets)
if [ "$response" -eq 200 ]; then
    echo "✅ 资产管理系统API访问正常"
else
    echo "❌ 资产管理系统API访问失败 (HTTP $response)"
fi

# 测试3: 检查Metabase界面
echo "测试3: 检查Metabase界面"
response=$(curl -k -s -o /dev/null -w "%{http_code}" https://billing.local/)
if [ "$response" -eq 200 ]; then
    echo "✅ Metabase界面访问正常"
else
    echo "❌ Metabase界面访问失败 (HTTP $response)"
fi

# 测试4: 检查API返回的资产数据
echo "测试4: 检查API返回的资产数据"
assets_count=$(curl -k -s https://billing.local/api/assets | grep -o "\"id\"" | wc -l | tr -d ' ')
if [ "$assets_count" -gt 0 ]; then
    echo "✅ API返回了 $assets_count 个资产记录"
else
    echo "❌ API未返回有效的资产数据"
fi

echo "集成测试完成!"