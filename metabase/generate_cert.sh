#!/bin/bash

# 脚本用于为Metabase生成更强的自签名SSL证书

# 检查OpenSSL是否已安装
if ! command -v openssl &> /dev/null
then
    echo "错误：未找到OpenSSL，请先安装OpenSSL"
    exit 1
fi

# 创建SSL目录（如果不存在）
SSL_DIR="./ssl"
if [ ! -d "$SSL_DIR" ]; then
    mkdir -p "$SSL_DIR"
fi

# 生成更强的私钥和证书
echo "正在生成SSL私钥和证书..."

# 生成私钥
openssl genrsa -out $SSL_DIR/nginx.key 2048

# 生成证书签名请求配置文件
cat > $SSL_DIR/cert.conf <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
C = CN
ST = Beijing
L = Beijing
O = My Billing
CN = billing.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = billing.local
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF

# 生成自签名证书
openssl req -new -x509 -key $SSL_DIR/nginx.key -out $SSL_DIR/nginx.crt -days 365 -config $SSL_DIR/cert.conf -extensions v3_req

# 清理临时配置文件
rm $SSL_DIR/cert.conf

echo "SSL证书生成完成！"
echo ""
echo "证书文件位置："
echo "  私钥: $SSL_DIR/nginx.key"
echo "  证书: $SSL_DIR/nginx.crt"
echo ""
echo "要信任此证书，请根据您的操作系统执行以下操作："
echo ""
echo "macOS:"
echo "  1. 打开'钥匙串访问'应用"
echo "  2. 选择'系统'钥匙串"
echo "  3. 将 $SSL_DIR/nginx.crt 文件拖拽到钥匙串中"
echo "  4. 双击导入的证书"
echo "  5. 展开'信任'部分"
echo "  6. 将'使用此证书时'设置为'始终信任'"
echo ""
echo "Windows:"
echo "  1. 在命令提示符中执行以下命令："
echo "     certutil -addstore -f \"ROOT\" $SSL_DIR/nginx.crt"
echo ""
echo "Linux (Ubuntu/Debian):"
echo "  1. 复制证书到系统证书目录："
echo "     sudo cp $SSL_DIR/nginx.crt /usr/local/share/ca-certificates/billing.local.crt"
echo "  2. 更新CA证书存储："
echo "     sudo update-ca-certificates"
echo ""
echo "生成证书后，请重启Metabase服务："
echo "  cd metabase && docker-compose down && docker-compose up -d"