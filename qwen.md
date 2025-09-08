# 项目概览

## 项目名称
账单转换器 (Bill Converter)

## 项目描述
这是一个基于 Python 的账单转换工具，可以将支付宝、微信、银行信用卡等账单数据转换为 MoneyPro 支持的格式。该工具具有多种功能，包括支持多种账单格式解析、智能分类系统、跨平台转账识别与去重、投资类交易过滤、工资和公积金收入自动识别以及资产记录功能。

## 核心功能
1. **多种账单格式支持**: 支付宝CSV、微信Excel、银行PDF等多种账单格式
2. **智能分类**: 基于交易描述自动分类
3. **跨平台转账识别**: 识别并去重跨平台转账交易
4. **投资类交易过滤**: 过滤掉投资类交易
5. **收入自动识别**: 自动识别工资和公积金收入
6. **资产记录**: 支持导出当前资产快照信息
7. **增量数据导入**: SQLite数据库支持账单数据的增量导入和去重
8. **智能去重**: 基于金额、日期、源账户、描述、代理信息生成唯一主键

## 项目结构
```
bill_converter/
├── __init__.py             # 包初始化文件
├── cli.py                  # 命令行接口
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── alipay/                 # 支付宝账单处理模块
│   ├── __init__.py
│   └── parser.py           # 支付宝账单解析器
├── wechat/                 # 微信账单处理模块
│   ├── __init__.py
│   └── parser.py           # 微信账单解析器
├── bank/                   # 银行账单处理模块
│   ├── __init__.py
│   └── parser.py           # 银行账单解析器
├── moneypro/               # MoneyPro格式导出模块
│   ├── __init__.py
│   └── exporter.py         # MoneyPro格式导出器
├── utils/                  # 工具模块
│   ├── __init__.py
│   ├── converter.py        # 通用转换器
│   └── deduplicator.py     # 去重工具
├── data/                   # 数据文件
│   └── category_keywords.json  # 分类关键词
└── tests/                  # 测试模块
    ├── __init__.py
    └── test_alipay_parser.py   # 支付宝解析器测试

raw_bills/                  # 原始账单文件目录
├── alipay/                 # 支付宝账单
├── wechat/                 # 微信账单
└── bank/                   # 银行账单

raw_assets/                 # 原始资产信息文件目录
└── assets.csv              # 资产信息文件

metabase/                   # Metabase集成目录
├── docker-compose.yml      # Docker部署配置
├── import_data.py          # 数据导入脚本
└── data/                   # 数据目录（自动生成）

out/                        # 输出目录
├── alipay_moneypro.csv     # 支付宝账单转换结果
├── wechat_moneypro.csv     # 微信账单转换结果
├── bank_moneypro.csv       # 银行账单转换结果
├── final_merged_bills.csv  # 最终合并去重后的文件
└── assets/                 # 资产信息输出目录
    └── 20250904_asset.csv  # 资产信息转换结果（带时间戳）
```

## 安装说明
1. 克隆项目代码：
   ```bash
   git clone <项目地址>
   cd billing-converter
   ```

2. 创建并激活虚拟环境：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用说明

### 方法一：分步执行（推荐用于调试和学习）
1. **处理账单文件**
   ```bash
   python bill_converter/main.py --auto
   ```

2. **处理资产信息**
   ```bash
   python asset_converter.py
   ```

3. **导入数据到Metabase**
   ```bash
   cd metabase && python import_data.py
   ```

4. **启动Metabase服务**
   ```bash
   cd metabase && docker-compose up -d
   ```

### 方法二：一键执行完整流程（推荐用于日常使用）
使用整合脚本可以一键执行完整的账单处理流程：
```
python run_complete_process.py
```

该脚本会自动执行以下操作：
1. 处理raw_bills目录下的所有账单文件
2. 处理raw_assets目录下的资产信息文件
3. 将处理后的数据导入Metabase数据库
4. 启动Metabase服务

也可以使用以下选项：
- `--no-services`: 只处理账单和导入数据，不启动服务
- `--manual-bills`: 手动处理账单（非自动模式）

访问地址：https://billing.local

## 项目配置
项目配置信息定义在 `bill_converter/config.py` 文件中：
- MONEYPRO_FIELDS: MoneyPro支持的字段
- DEFAULT_ACCOUNT_MAP: 默认账户映射
- DEFAULT_OUTPUT_DIR: 默认输出目录
- DEFAULT_BILLS_DIR: 默认账单输入目录
- DEFAULT_ASSETS_DIR: 默认资产输入目录

## Metabase 集成
本项目支持将导出的账单结果导入到开源 BI 工具 Metabase 进行二次数据分析和可视化展示。

### 部署步骤
1. 安装 Docker 和 Docker Compose
2. 运行账单转换器生成最终的合并账单文件：
   ```bash
   python bill_converter/main.py --auto
   ```
3. 将数据导入到 SQLite 数据库供 Metabase 使用：
   ```bash
   python metabase/import_data.py
   ```
4. 启动 Metabase：
   ```bash
   cd metabase && docker-compose up -d
   ```
5. 在浏览器中访问 https://billing.local，按照初始化向导进行设置

## 依赖项
项目依赖定义在 `requirements.txt` 文件中：
- pandas>=1.3.0 (CSV处理)
- openpyxl>=3.0.0 (Excel文件处理)
- PyPDF2>=3.0.0 (PDF处理)
- click>=8.0.0 (命令行界面)
- chardet>=5.0.0 (字符编码检测)
- pytest>=6.2.4 (测试框架)
- black>=21.5b2 (代码格式化)
- flake8>=3.9.2 (代码检查)
- jieba>=0.42.1 (中文分词)
- forex-python>=1.8 (汇率获取)

## 脚本说明
- `bill_converter/main.py`: 账单转换器主程序
- `asset_converter.py`: 资产信息转换脚本
- `run_complete_process.py`: 完整账单处理流程脚本
- `metabase/import_data.py`: Metabase数据导入脚本

## 数据库维护
如果数据库中意外写入了测试数据或重复数据，可以通过以下SQL语句清理：
```sql
-- 删除重复的资产记录（保留每组重复记录中ROWID最小的一条）
DELETE FROM assets_records WHERE ROWID NOT IN (
    SELECT MIN(ROWID) 
    FROM assets_records 
    GROUP BY 账户分类, 币种, 金额, 描述, 时间, 对应人民币金额, 资产_负债
);

-- 删除测试账单记录
DELETE FROM billing_records WHERE 类别 IN ('测试类别', '新增类别');
```

## 域名配置
- 默认域名为 `billing.local`
- 如需修改域名，请编辑 `metabase/nginx.conf` 文件中的 `server_name` 配置项
- 确保本地 DNS 或 hosts 文件中配置了域名解析

## HTTPS访问
- 使用自签名SSL证书启用HTTPS
- 所有HTTP请求会自动重定向到HTTPS
- 默认通过HTTPS访问：https://billing.local

## 最新更新 (2025-09-08)
- 重构项目目录结构，将中文目录名改为英文目录名：
  - `原始账单` 改为 `raw_bills`
  - `原始资产` 改为 `raw_assets`
- 更新所有相关代码和文档中的目录引用
- 更新配置文件中的默认目录配置