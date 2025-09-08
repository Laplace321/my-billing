# 账单转换器项目概述

## 项目描述
这是一个基于Python的账单转换工具，可将支付宝、微信和银行信用卡账单数据转换为与MoneyPro兼容的格式。该工具支持多种账单格式、智能分类、跨平台转账检测和去重、投资交易过滤，以及自动识别工资和公积金收入。

## 主要功能
1. **多格式账单支持**：解析CSV（支付宝）、Excel（微信）和PDF（银行）账单格式
2. **智能分类**：根据交易描述自动分类交易
3. **跨平台转账检测**：识别并去重跨平台转账
4. **投资交易过滤**：过滤掉投资相关交易
5. **收入识别**：自动识别工资和住房公积金收入
6. **资产记录**：导出当前资产快照
7. **增量数据导入**：SQLite数据库支持带去重的增量账单数据导入
8. **智能去重**：基于金额、日期、源账户、描述和代理生成唯一键

## 项目结构
```
.
├── asset_converter.py              # 资产信息转换脚本
├── bill_converter/                 # 主要账单转换模块
│   ├── __init__.py
│   ├── alipay/                     # 支付宝账单处理模块
│   │   ├── __init__.py
│   │   └── parser.py
│   ├── bank/                       # 银行账单处理模块
│   │   ├── __init__.py
│   │   └── parser.py
│   ├── cli.py                      # 命令行界面
│   ├── config.py                   # 配置文件
│   ├── data/                       # 数据文件
│   │   └── category_keywords.json  # 分类关键词
│   ├── main.py                     # 主程序入口点
│   ├── moneypro/                   # MoneyPro格式导出模块
│   │   ├── __init__.py
│   │   └── exporter.py
│   ├── tests/                      # 测试模块
│   │   ├── __init__.py
│   │   └── test_alipay_parser.py
│   ├── utils/                      # 工具模块
│   │   ├── __init__.py
│   │   ├── converter.py
│   │   └── deduplicator.py
│   └── wechat/                     # 微信账单处理模块
│       ├── __init__.py
│       └── parser.py
├── metabase/                       # Metabase集成目录
│   ├── data/                       # 数据目录（自动生成）
│   ├── docker-compose.yml          # Docker部署配置
│   ├── import_data.py              # 数据导入脚本
│   └── nginx.conf                  # Nginx反向代理配置
├── out/                            # 输出目录
├── raw_assets/                     # 原始资产信息目录
├── raw_bills/                      # 原始账单文件目录
├── requirements.txt                # 项目依赖
├── run_complete_process.py         # 完整账单处理工作流脚本
├── setup.py                        # 包设置文件
└── venv/                           # 虚拟环境（git忽略）
```

## 依赖项
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

## 安装说明
1. 克隆项目：
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

## 使用方法

### 方法1：分步执行（推荐用于调试和学习）
1. **处理账单文件**：
   ```bash
   python bill_converter/main.py --auto
   ```

2. **处理资产信息**：
   ```bash
   python asset_converter.py
   ```

3. **导入数据到Metabase**：
   ```bash
   cd metabase && python import_data.py
   ```

4. **启动Metabase服务**：
   ```bash
   cd metabase && docker-compose up -d
   ```

### 方法2：一键执行（推荐日常使用）
使用集成脚本执行完整的账单处理工作流：
```bash
python run_complete_process.py
```

选项：
- `--no-services`：处理账单并导入数据但不启动服务
- `--manual-bills`：手动账单处理（非自动模式）

访问地址：https://billing.local

## 核心组件

### 1. 账单处理 (`bill_converter/`)
- **支付宝解析器**：处理CSV格式的支付宝账单
- **微信解析器**：处理Excel格式的微信账单
- **银行解析器**：处理PDF格式的银行账单（初始支持招商银行）
- **转换器**：将解析的数据转换为MoneyPro格式
- **去重器**：删除跨平台的重复交易

### 2. 资产处理 (`asset_converter.py`)
将原始资产信息转换为带时间戳的CSV格式，包含：
- 货币转换为人民币
- 资产/负债分类

### 3. Metabase集成 (`metabase/`)
- 将处理后的账单数据导入SQLite数据库
- 提供Metabase部署的Docker Compose配置
- 使用Nginx作为域名访问的反向代理
- 默认域名：`billing.local`

### 4. 完整流程 (`run_complete_process.py`)
编排整个工作流程：
1. 处理原始账单文件
2. 处理原始资产文件
3. 将数据导入Metabase
4. 启动Metabase服务

## 配置说明
主要配置在 `bill_converter/config.py` 中：
- `MONEYPRO_FIELDS`：MoneyPro支持的字段
- `DEFAULT_ACCOUNT_MAP`：默认账户映射
- `DEFAULT_OUTPUT_DIR`：默认输出目录
- `DEFAULT_BILLS_DIR`：默认账单输入目录
- `DEFAULT_ASSETS_DIR`：默认资产输入目录

## 数据分类
系统使用在 `bill_converter/data/category_keywords.json` 中定义的基于关键词的分类。分类包括：
- 食品
- 服装
- 交通
- 亲属
- 住宅
- 杂货
- 娱乐
- 购物
- 教育
- 医疗
- 旅游
- 数码
- 保险
- 投资
- 债务
- 日常开支
- 工资
- 住房公积金

## 数据库维护
如果意外将测试数据或重复记录写入数据库，可以使用SQL清理：
```sql
-- 删除重复的资产记录（保留每组中ROWID最小的记录）
DELETE FROM assets_records WHERE ROWID NOT IN (
    SELECT MIN(ROWID) 
    FROM assets_records 
    GROUP BY 账户分类, 币种, 金额, 描述, 时间, 对应人民币金额, 资产_负债
);

-- 删除测试账单记录
DELETE FROM billing_records WHERE 类别 IN ('测试类别', '新增类别');
```

## HTTPS访问
- 使用自签名SSL证书实现HTTPS
- 所有HTTP请求自动重定向到HTTPS
- 默认通过HTTPS访问：https://billing.local
- 对于自签名证书，浏览器安全警告是正常的

## 开发指南
- 在配置中使用相对路径以确保可移植性
- 遵循现有的代码结构和命名约定
- 需要时将新的分类关键词添加到 `category_keywords.json`
- 在 `tests/` 目录中为新功能编写测试
- 使用提供的代码格式化工具（black, flake8）保持一致性