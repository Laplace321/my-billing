#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
资产管理系统API服务
提供RESTful API接口用于管理资产数据
"""

import os
import sys
import json
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pandas as pd
import sqlite3

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from metabase.import_data import import_assets_to_sqlite
from asset_converter import get_exchange_rate

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metabase', 'data', 'billing.db')

class AssetAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        """设置响应头"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def _read_request_body(self):
        """读取请求体"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))

    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self._set_headers()

    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        # 获取所有资产
        if parsed_path.path == '/api/assets':
            self._get_assets()
        else:
            self._set_headers(404)
            self.wfile.write(b'Not Found')

    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        
        # 添加新资产
        if parsed_path.path == '/api/assets':
            self._add_asset()
        else:
            self._set_headers(404)
            self.wfile.write(b'Not Found')

    def do_PUT(self):
        """处理PUT请求"""
        parsed_path = urlparse(self.path)
        
        # 更新资产
        if parsed_path.path.startswith('/api/assets/'):
            asset_id = parsed_path.path.split('/')[-1]
            self._update_asset(asset_id)
        else:
            self._set_headers(404)
            self.wfile.write(b'Not Found')

    def do_DELETE(self):
        """处理DELETE请求"""
        parsed_path = urlparse(self.path)
        
        # 删除资产
        if parsed_path.path.startswith('/api/assets/'):
            asset_id = parsed_path.path.split('/')[-1]
            self._delete_asset(asset_id)
        else:
            self._set_headers(404)
            self.wfile.write(b'Not Found')

    def _get_assets(self):
        """获取所有资产"""
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(DB_PATH):
                self._send_json_response([])
                return
            
            # 连接到SQLite数据库
            conn = sqlite3.connect(DB_PATH)
            
            # 检查assets_records表是否存在
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='assets_records'
            """)
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                # 表不存在，返回空数组
                conn.close()
                self._send_json_response([])
                return
            
            # 读取资产数据
            df = pd.read_sql_query("SELECT * FROM assets_records", conn)
            conn.close()
            
            # 转换为资产对象数组
            assets = []
            for _, row in df.iterrows():
                # 生成唯一ID（如果没有的话）
                asset_id = str(row.get('id', '')) if row.get('id', '') else str(uuid.uuid4())
                
                asset = {
                    'id': asset_id,
                    'accountType': row.get('账户分类', ''),
                    'currency': row.get('币种', ''),
                    'amount': float(row.get('金额', 0)),
                    'description': row.get('描述', ''),
                    'timestamp': row.get('时间', ''),
                    'cnyAmount': float(row.get('对应人民币金额', 0)),
                    'assetOrLiability': row.get('资产_负债', '资产')
                }
                assets.append(asset)
            
            self._send_json_response(assets)
        except Exception as e:
            print(f"获取资产数据时出错: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': '获取资产数据失败'}).encode('utf-8'))

    def _add_asset(self):
        """添加新资产"""
        try:
            # 读取请求体
            data = self._read_request_body()
            
            # 验证必要字段
            required_fields = ['accountType', 'currency', 'amount', 'description']
            for field in required_fields:
                if field not in data or not data[field]:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': f'缺少必要字段: {field}'}).encode('utf-8'))
                    return
            
            # 创建新资产对象
            asset = {
                'id': str(uuid.uuid4()),
                '账户分类': data['accountType'],
                '币种': data['currency'],
                '金额': float(data['amount']),
                '描述': data['description'],
                '时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                '对应人民币金额': round(float(data['amount']) * get_exchange_rate(data['currency']), 2),
                '资产_负债': '负债' if data['accountType'] == '信用卡' else '资产'
            }
            
            # 连接到SQLite数据库
            conn = sqlite3.connect(DB_PATH)
            
            # 将资产数据添加到数据库
            df = pd.DataFrame([asset])
            df.to_sql('assets_records', conn, if_exists='append', index=False)
            conn.close()
            
            # 返回创建的资产
            response_asset = {
                'id': asset['id'],
                'accountType': asset['账户分类'],
                'currency': asset['币种'],
                'amount': asset['金额'],
                'description': asset['描述'],
                'timestamp': asset['时间'],
                'cnyAmount': asset['对应人民币金额'],
                'assetOrLiability': asset['资产_负债']
            }
            
            self._send_json_response(response_asset, 201)
        except Exception as e:
            print(f"添加资产时出错: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': '添加资产失败'}).encode('utf-8'))

    def _update_asset(self, asset_id):
        """更新资产"""
        try:
            # 读取请求体
            data = self._read_request_body()
            
            # 验证必要字段
            required_fields = ['accountType', 'currency', 'amount', 'description']
            for field in required_fields:
                if field not in data or not data[field]:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({'error': f'缺少必要字段: {field}'}).encode('utf-8'))
                    return
            
            # 连接到SQLite数据库
            conn = sqlite3.connect(DB_PATH)
            
            # 检查assets_records表是否存在
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='assets_records'
            """)
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                conn.close()
                self._set_headers(404)
                self.wfile.write(json.dumps({'error': '资产表不存在'}).encode('utf-8'))
                return
            
            # 读取现有资产数据
            df = pd.read_sql_query("SELECT * FROM assets_records", conn)
            
            # 查找要更新的资产
            asset_found = False
            for i, row in df.iterrows():
                if str(row.get('id', '')) == asset_id or str(uuid.uuid4()) == asset_id:
                    # 更新资产信息
                    df.at[i, '账户分类'] = data['accountType']
                    df.at[i, '币种'] = data['currency']
                    df.at[i, '金额'] = float(data['amount'])
                    df.at[i, '描述'] = data['description']
                    df.at[i, '时间'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    df.at[i, '对应人民币金额'] = round(float(data['amount']) * get_exchange_rate(data['currency']), 2)
                    df.at[i, '资产_负债'] = '负债' if data['accountType'] == '信用卡' else '资产'
                    asset_found = True
                    break
            
            if not asset_found:
                # 如果没有找到匹配的资产，添加新资产
                new_asset = {
                    'id': asset_id,
                    '账户分类': data['accountType'],
                    '币种': data['currency'],
                    '金额': float(data['amount']),
                    '描述': data['description'],
                    '时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    '对应人民币金额': round(float(data['amount']) * get_exchange_rate(data['currency']), 2),
                    '资产_负债': '负债' if data['accountType'] == '信用卡' else '资产'
                }
                df = pd.concat([df, pd.DataFrame([new_asset])], ignore_index=True)
            
            # 更新数据库
            df.to_sql('assets_records', conn, if_exists='replace', index=False)
            conn.close()
            
            # 返回更新的资产
            response_asset = {
                'id': asset_id,
                'accountType': data['accountType'],
                'currency': data['currency'],
                'amount': float(data['amount']),
                'description': data['description'],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'cnyAmount': round(float(data['amount']) * get_exchange_rate(data['currency']), 2),
                'assetOrLiability': '负债' if data['accountType'] == '信用卡' else '资产'
            }
            
            self._send_json_response(response_asset)
        except Exception as e:
            print(f"更新资产时出错: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': '更新资产失败'}).encode('utf-8'))

    def _delete_asset(self, asset_id):
        """删除资产"""
        try:
            # 连接到SQLite数据库
            conn = sqlite3.connect(DB_PATH)
            
            # 检查assets_records表是否存在
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='assets_records'
            """)
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                conn.close()
                self._send_json_response({'message': '资产删除成功'})
                return
            
            # 读取现有资产数据
            df = pd.read_sql_query("SELECT * FROM assets_records", conn)
            
            # 过滤掉要删除的资产
            if 'id' in df.columns:
                df = df[df['id'] != asset_id]
            else:
                # 如果没有ID列，返回成功但不删除任何数据
                conn.close()
                self._send_json_response({'message': '资产删除成功'})
                return
            
            # 更新数据库
            df.to_sql('assets_records', conn, if_exists='replace', index=False)
            conn.close()
            
            self._send_json_response({'message': '资产删除成功'})
        except Exception as e:
            print(f"删除资产时出错: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': '删除资产失败'}).encode('utf-8'))

def run_server(port=3001):
    """启动服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, AssetAPIHandler)
    print(f'资产管理API服务器运行在端口 {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()