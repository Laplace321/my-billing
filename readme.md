# 账单转换器

本项目用于导入支付宝、微信、银行信用卡等账单数据，并对账单数据进行标准化处理，转换成适合导入 MoneyPro app 的账单。

## 项目介绍

这是一个基于 Python 的账单转换工具，可以将支付宝、微信、银行信用卡等账单数据转换为 MoneyPro 支持的格式。该工具具有以下特点：

1. 支持多种账单格式解析（支付宝CSV、微信Excel、银行PDF等）
2. 智能分类系统，基于交易描述自动分类
3. 跨平台转账识别与去重
4. 投资类交易过滤
5. 工资和公积金收入自动识别

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

metabase/                   # Metabase集成目录
├── docker-compose.yml      # Docker部署配置
├── import_data.py          # 数据导入脚本
└── data/                   # 数据目录（自动生成）
```

## 安装说明

1. 克隆项目代码：
   ```
   git clone <项目地址>
   cd billing-converter
   ```

2. 创建并激活虚拟环境：
   ```
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用说明

### 命令行使用

1. 转换支付宝账单：
   ```
   python -m bill_converter.cli alipay -i <支付宝账单文件路径> -o <输出文件路径>
   ```

2. 转换微信账单：
   ```
   python -m bill_converter.cli wechat -i <微信账单文件路径> -o <输出文件路径>
   ```

3. 转换银行账单：
   ```
   python -m bill_converter.cli bank -i <银行账单文件路径> -o <输出文件路径> --bank <银行类型>
   ```

### 批量处理

使用主程序进行批量处理：
```
python bill_converter/main.py --auto
```

程序会自动处理以下目录中的账单文件：
- `原始账单/alipay_record_*.csv` - 支付宝账单
- `原始账单/微信支付账单*.xlsx` - 微信账单
- `原始账单/招商银行*.pdf` - 招商银行账单

处理后的文件将保存在 `out/` 目录中，包括：
- 每个原始账单对应的转换后文件（文件名格式：原文件名_moneypro.csv）
- 最终合并去重后的文件（文件名：final_merged_bills.csv）

### 交互式处理

运行主程序进入交互式模式：
```
python bill_converter/main.py
```

在交互式模式下，您可以选择不同的操作：
1. 转换支付宝账单
2. 转换微信账单
3. 转换银行账单
4. 合并多个账单并去重
5. 自动处理原始账单目录下的所有文件

### 人工维护说明

#### 分类关键词维护

分类关键词存储在 `bill_converter/data/category_keywords.json` 文件中，可以根据需要添加或修改关键词。

#### 配置文件

配置文件 `bill_converter/config.py` 包含以下设置：
- 账单文件路径配置
- 输出文件路径配置
- 需要过滤的交易类型
- 需要识别的收入类型

## Metabase 集成

本项目支持将导出的账单结果导入到开源 BI 工具 Metabase 进行二次数据分析和可视化展示。

### 部署步骤

1. 安装 Docker 和 Docker Compose（如果尚未安装）
   - 确保系统已安装 Docker 和 Docker Compose
   - 如果未安装，请参考 Docker 官方文档进行安装

2. 运行账单转换器生成最终的合并账单文件：
   ```
   python bill_converter/main.py --auto
   ```

3. 将数据导入到 SQLite 数据库供 Metabase 使用：
   ```
   python metabase/import_data.py
   ```

4. 启动 Metabase：
   ```
   cd metabase && docker-compose up -d
   ```

5. 在浏览器中访问 https://billing.local，按照初始化向导进行设置

6. 添加数据库连接：
   - 选择"SQLite"作为数据库类型
   - 数据库文件路径填写：`/metabase-data/billing.db`
   - 设置数据库名称，如"billing"

7. 开始数据分析和可视化

### 域名配置说明

为了使用域名访问 Metabase，而不是 IP 地址，系统使用 Nginx 作为反向代理。

1. 默认域名为 `billing.local`
2. 如果需要修改域名，请编辑 `metabase/nginx.conf` 文件中的 `server_name` 配置项
3. 确保本地 DNS 或 hosts 文件中配置了域名解析：
   - 在 Linux/Mac 系统中，编辑 `/etc/hosts` 文件
   - 在 Windows 系统中，编辑 `C:\Windows\System32\drivers\etc\hosts` 文件
   - 添加以下行：
     ```
     127.0.0.1 billing.local
     ```

### HTTPS访问说明

为了提供安全的访问体验，系统配置了HTTPS访问：

1. 使用自签名SSL证书启用HTTPS
2. 所有HTTP请求会自动重定向到HTTPS
3. 默认通过HTTPS访问：https://billing.local

注意：由于使用的是自签名证书，浏览器可能会显示安全警告。这是正常的，可以选择继续访问或者导入证书到系统信任库中。

为了消除浏览器的安全警告，建议使用由受信任的证书颁发机构签发的证书。对于本地开发环境，可以使用以下方法之一：

1. 手动信任自签名证书（参考[METABASE_INTEGRATION.md](file:///Users/laplacetong/My-billing/METABASE_INTEGRATION.md)中的说明）
2. 使用像nip.io或sslip.io这样的服务获得基于IP的公共域名
3. 使用Let's Encrypt获取免费的受信任SSL证书（需要公共域名）

### 使用说明

- Metabase 服务通过域名 `billing.local` 访问（推荐使用HTTPS）
- 账单数据存储在 SQLite 数据库中，通过 Docker 数据卷挂载实现持久化
- 数据库文件位于项目目录的 `metabase/data/billing.db`
- 如需更新数据，重新运行步骤 2 和 3 即可

详细说明请参见 [METABASE_INTEGRATION.md](file:///Users/laplacetong/My-billing/METABASE_INTEGRATION.md) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 许可证

本项目采用 MIT 许可证，详情请参见 LICENSE 文件。