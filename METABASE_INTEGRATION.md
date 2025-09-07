# Metabase 集成说明

本项目支持将导出的账单结果导入到 Metabase 进行二次数据分析和可视化展示。

## Metabase 简介

Metabase 是一款开源的商业智能（BI）工具，可以帮助用户通过简单的界面进行数据查询、分析和可视化。它支持多种数据库作为数据源，包括 SQLite、MySQL、PostgreSQL 等。

## 集成方案

本项目通过以下方式与 Metabase 集成：

1. 账单数据导出为 CSV 格式
2. 提供脚本将 CSV 数据导入到 SQLite 数据库
3. 提供 Docker 配置文件用于本地部署 Metabase
4. 使用 Nginx 反向代理实现域名访问
5. Metabase 连接到 SQLite 数据库进行数据分析

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

### 4. 配置域名解析

为了使用域名访问 Metabase，需要在本地配置域名解析：

- 在 Linux/Mac 系统中，编辑 `/etc/hosts` 文件
- 在 Windows 系统中，编辑 `C:\Windows\System32\drivers\etc\hosts` 文件
- 添加以下行：
  ```
  127.0.0.1 billing.local
  ```

### 5. 启动 Metabase

使用 Docker Compose 启动 Metabase 和 Nginx 反向代理：

```bash
cd metabase
docker-compose up -d
```

### 6. 访问 Metabase

在浏览器中访问 https://billing.local，按照初始化向导进行设置：

1. 设置管理员账户
2. 添加数据库连接（选择 SQLite，数据库文件路径为 `/metabase-data/billing.db`）
3. 开始数据分析和可视化

## 目录结构

```
my-billing/
├── metabase/
│   ├── docker-compose.yml     # Docker 部署配置
│   ├── nginx.conf             # Nginx 反向代理配置
│   ├── import_data.py         # 数据导入脚本
│   ├── ssl/                   # SSL证书目录
│   │   ├── nginx.crt          # SSL证书
│   │   └── nginx.key          # SSL私钥
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

`metabase/docker-compose.yml` 文件定义了 Metabase 和 Nginx 服务：

- 使用官方 metabase/metabase 镜像
- 使用 Nginx 作为反向代理实现域名访问
- Metabase 服务监听在内部端口 3000
- Nginx 代理监听在外部端口 80 和 443
- 挂载数据卷以持久化 Metabase 配置和账单数据
- 挂载SSL证书目录以支持HTTPS访问

### 域名配置

默认使用 `billing.local` 作为访问域名。如需修改域名，请：

1. 编辑 `metabase/nginx.conf` 文件中的 `server_name` 配置项
2. 更新本地 hosts 文件中的域名映射

### HTTPS配置

为了提供安全的访问体验，系统配置了HTTPS访问：

1. 使用自签名SSL证书启用HTTPS
2. 所有HTTP请求会自动重定向到HTTPS
3. 默认通过HTTPS访问：https://billing.local

注意：由于使用的是自签名证书，浏览器可能会显示安全警告。这是正常的，可以选择继续访问或者导入证书到系统信任库中。

为了消除浏览器的安全警告，建议使用由受信任的证书颁发机构签发的证书，例如Let's Encrypt。以下是获取和配置受信任SSL证书的步骤：

1. 确保您的域名已正确解析到服务器IP地址
   - 如果您在本地运行，需要一个指向本地IP的公共域名
   - 可以使用服务如nip.io或sslip.io来获得基于IP的域名，例如：`billing.127.0.0.1.nip.io`

2. 安装Certbot（Let's Encrypt客户端）
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install certbot
   
   # CentOS/RHEL
   sudo yum install certbot
   
   # macOS
   brew install certbot
   ```

3. 获取SSL证书
   ```bash
   # 使用standalone模式获取证书（会临时占用80端口）
   sudo certbot certonly --standalone -d billing.yourdomain.com
   
   # 或者如果您已有Web服务器运行，可以使用webroot模式
   sudo certbot certonly --webroot -w /path/to/webroot -d billing.yourdomain.com
   ```

4. 更新Nginx配置以使用新证书
   ```nginx
   # 将以下行：
   ssl_certificate /etc/nginx/ssl/nginx.crt;
   ssl_certificate_key /etc/nginx/ssl/nginx.key;
   
   # 替换为：
   ssl_certificate /etc/letsencrypt/live/billing.yourdomain.com/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/billing.yourdomain.com/privkey.pem;
   ```

5. 设置证书自动续期
   ```bash
   # 添加到crontab以自动续期证书
   sudo crontab -e
   # 添加以下行：
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

对于本地开发环境，如果无法获取公共域名，可以继续使用自签名证书，但需要手动将证书添加到系统或浏览器的信任存储中。

### 手动信任自签名证书

如果您希望在本地环境中信任自签名证书，可以按照以下步骤操作：

#### Windows系统：
1. 在浏览器中访问 https://billing.local
2. 点击"高级"或"继续访问"（具体选项因浏览器而异）
3. 或者将证书导入到Windows证书存储：
   - 打开`certmgr.msc`
   - 导航到"受信任的根证书颁发机构"
   - 右键点击"证书"，选择"所有任务" -> "导入"
   - 选择证书文件并完成导入向导

#### macOS系统：
1. 打开"钥匙串访问"应用
2. 选择"系统"钥匙串
3. 将证书文件拖拽到钥匙串中
4. 双击导入的证书
5. 展开"信任"部分
6. 将"使用此证书时"设置为"始终信任"

#### Linux系统：
1. 将证书复制到系统证书目录：
   ```bash
   sudo cp nginx.crt /usr/local/share/ca-certificates/billing.local.crt
   sudo update-ca-certificates
   ```

## 注意事项

1. 确保 Docker 和 Docker Compose 已正确安装
2. 首次运行前请确保已生成账单数据文件
3. Metabase 初始化时需要一些时间，请耐心等待
4. 数据库文件路径在 Metabase 配置中应使用容器内的路径 `/metabase-data/billing.db`
5. 如需更新数据，重新运行数据导入脚本即可
6. 确保本地 hosts 文件已正确配置域名解析
7. 由于使用自签名证书，浏览器可能会显示安全警告，可以选择继续访问
