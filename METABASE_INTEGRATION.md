# Metabase 集成说明

本项目支持将导出的账单结果导入到 Metabase 进行二次数据分析和可视化展示。

## Metabase 简介

Metabase 是一款开源的商业智能（BI）工具，可以帮助用户通过简单的界面进行数据查询、分析和可视化。它支持多种数据库作为数据源，包括 SQLite、MySQL、PostgreSQL 等。

## 集成方案

本项目通过以下方式与 Metabase 集成：

1. 账单数据导出为 CSV 格式
2. 提供脚本将 CSV 数据导入到 SQLite 数据库
3. 提供 Docker 配置文件用于本地部署 Metabase
4. Metabase 连接到 SQLite 数据库进行数据分析

## 部署步骤

### 1. 安装 Docker

确保您的系统已安装 Docker 和 Docker Compose。如果未安装，请参考以下链接：

- Docker 安装指南: https://docs.docker.com/get-docker/
- Docker Compose 安装指南: https://docs.docker.com/compose/install/

### 2. 准备数据

运行账单转换器生成最终的合并账单文件：

```bash
python bill_converter/main.py --auto
```

这将在 `out/` 目录中生成 `final_merged_bills.csv` 文件。

### 3. 导入数据到 SQLite

使用我们提供的脚本将 CSV 数据导入到 SQLite 数据库：

```bash
python metabase/import_data.py
```

这将创建 `metabase/data/billing.db` 数据库文件，其中包含账单数据。

### 4. 启动 Metabase

使用 Docker Compose 启动 Metabase：

```bash
cd metabase
docker-compose up -d
```

### 5. 访问 Metabase

在浏览器中访问 http://localhost:8080，按照初始化向导进行设置：

1. 设置管理员账户
2. 添加数据库连接（选择 SQLite，数据库文件路径为 `/metabase-data/billing.db`）
3. 开始数据分析和可视化

## 目录结构

```
my-billing/
├── metabase/
│   ├── docker-compose.yml     # Docker 部署配置
│   ├── import_data.py         # 数据导入脚本
│   └── data/                  # Metabase 数据目录
│       └── billing.db         # SQLite 数据库文件
└── ...
```

## 使用说明

### 数据导入脚本

`metabase/import_data.py` 脚本会执行以下操作：

1. 读取 `out/final_merged_bills.csv` 文件
2. 将数据导入到 SQLite 数据库 `metabase/data/billing.db`
3. 创建适当的表结构以支持 Metabase 分析

### Docker Compose 配置

`metabase/docker-compose.yml` 文件定义了 Metabase 服务：

- 使用官方 metabase/metabase 镜像
- 映射端口 8080:3000
- 挂载数据卷以持久化 Metabase 配置和账单数据

## 注意事项

1. 确保 Docker 和 Docker Compose 已正确安装
2. 首次运行前请确保已生成账单数据文件
3. Metabase 初始化时需要一些时间，请耐心等待
4. 数据库文件路径在 Metabase 配置中应使用容器内的路径 `/metabase-data/billing.db`
5. 如需更新数据，重新运行数据导入脚本即可