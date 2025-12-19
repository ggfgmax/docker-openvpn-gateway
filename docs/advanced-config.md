# 高级配置文档

本文档包含所有高级配置选项和详细说明。

## 📖 目录

- [LDAP 详细配置](#ldap-详细配置)
- [多云网络详细配置](#多云网络详细配置)
- [性能优化](#性能优化)
- [安全加固](#安全加固)
- [网络配置](#网络配置)

---

## LDAP 详细配置

### OpenLDAP 配置

```bash
docker exec openvpn-gateway ovpn_config_ldap \
    -h ldap.company.com \
    -p 389 \
    -b "dc=company,dc=com" \
    -D "cn=readonly,dc=company,dc=com" \
    -w "password" \
    -f "(&(objectClass=posixAccount)(uid=%u))" \
    -s uid
```

### Active Directory 配置

```bash
docker exec openvpn-gateway ovpn_config_ldap \
    -h ad.company.com \
    -p 389 \
    -b "dc=company,dc=com" \
    -D "CN=VPN Service,OU=Service Accounts,DC=company,DC=com" \
    -w "password" \
    -f "(&(objectClass=user)(sAMAccountName=%u)(memberOf=CN=VPN Users,OU=Groups,DC=company,DC=com))" \
    -s sAMAccountName
```

### LDAPS (TLS 加密)

```bash
docker exec openvpn-gateway ovpn_config_ldap \
    -h ldaps.company.com \
    -S \
    -b "dc=company,dc=com"
```

### 测试 LDAP 连接

```bash
docker exec openvpn-gateway ldapsearch -x \
    -H ldap://ldap.company.com \
    -b "dc=company,dc=com" \
    -D "cn=admin,dc=company,dc=com" \
    -w "password" \
    "(uid=testuser)"
```

---

## 多云网络详细配置

### 添加远程站点（命令行）

```bash
# 华为云
docker exec openvpn-gateway ovpn_add_remote_site \
    -n huawei \
    -h vpn.huaweicloud.com \
    -p 1194 \
    -s 172.16.0.0/16 \
    -P udp

# AWS
docker exec openvpn-gateway ovpn_add_remote_site \
    -n aws \
    -h vpn.aws.com \
    -p 1194 \
    -s 10.0.0.0/16

# GCP
docker exec openvpn-gateway ovpn_add_remote_site \
    -n gcp \
    -h vpn.gcp.com \
    -p 1194 \
    -s 192.168.0.0/16
```

### 手动配置站点证书

如果不使用 Web UI，可以手动配置：

```bash
# 进入容器
docker exec -it openvpn-gateway bash

# 编辑站点配置
vi /etc/openvpn/sites/huawei.conf

# 在文件末尾添加证书内容（从 .ovpn 文件复制）
```

证书格式：
```
<ca>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
</key>

<tls-auth>
-----BEGIN OpenVPN Static key V1-----
...
-----END OpenVPN Static key V1-----
</tls-auth>
key-direction 1
```

### 更新路由

```bash
docker exec openvpn-gateway ovpn_update_routes
```

### 查看站点状态

```bash
# 列出所有站点
docker exec openvpn-gateway ovpn_list_sites

# 查看站点日志
docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
```

---

## 性能优化

### 调整 MTU

```bash
# 生成配置时指定 MTU
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com -m 1400
```

### 启用压缩

```bash
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com -z
```

### 使用 TCP（高延迟网络）

```bash
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u tcp://vpn.yourdomain.com
```

### 限制容器资源

```bash
docker run -v openvpn-data:/etc/openvpn \
    -p 1194:1194/udp -p 8080:8080 \
    --memory="2g" \
    --cpus="2" \
    --cap-add=NET_ADMIN \
    --name openvpn-gateway \
    openvpn-gateway:latest
```

---

## 安全加固

### 使用 HTTPS

Nginx 配置：

```nginx
server {
    listen 80;
    server_name vpn-admin.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name vpn-admin.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 防火墙配置

```bash
# UFW
sudo ufw allow 1194/udp              # OpenVPN
sudo ufw allow from 192.168.1.0/24 to any port 8080  # Web UI 限制 IP
sudo ufw enable

# iptables
iptables -A INPUT -p udp --dport 1194 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
```

### 启用客户端证书吊销

```bash
# 吊销客户端
docker exec openvpn-gateway easyrsa revoke client-name

# 生成 CRL
docker exec openvpn-gateway easyrsa gen-crl

# 重启服务
docker restart openvpn-gateway
```

---

## 网络配置

### IPv6 支持

```bash
# 生成配置时会自动检测并启用 IPv6
docker exec openvpn-gateway sysctl net.ipv6.conf.all.forwarding
```

### 自定义 DNS

```bash
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com \
    -n 1.1.1.1 -n 8.8.8.8
```

### 禁用默认路由

```bash
# 客户端不使用 VPN 作为默认网关
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com -d
```

### 静态 IP 分配

```bash
# 为特定客户端分配静态 IP
echo "ifconfig-push 192.168.254.10 192.168.254.11" | \
    docker exec -i openvpn-gateway tee /etc/openvpn/ccd/client-name
```

---

## 故障排查

### 启用调试模式

```bash
# 启动时添加 DEBUG=1
docker run -v openvpn-data:/etc/openvpn \
    -e DEBUG=1 \
    -p 1194:1194/udp \
    --cap-add=NET_ADMIN \
    openvpn-gateway:latest
```

### 查看详细日志

```bash
# 主日志
docker logs -f openvpn-gateway

# OpenVPN 日志
docker exec openvpn-gateway tail -f /var/log/openvpn.log

# 站点日志
docker exec openvpn-gateway tail -f /var/log/openvpn-huawei.log
```

### 网络诊断

```bash
# 检查路由
docker exec openvpn-gateway ip route

# 检查 iptables
docker exec openvpn-gateway iptables -L -n -v
docker exec openvpn-gateway iptables -t nat -L -n -v

# 检查隧道接口
docker exec openvpn-gateway ip addr show | grep tun
```

---

## Docker Compose 高级配置

### 完整配置示例

```yaml
version: "3.8"

services:
  openvpn-gateway:
    build: .
    image: openvpn-gateway:latest
    container_name: openvpn-gateway
    ports:
      - "1194:1194/udp"
      - "8080:8080"
    cap_add:
      - NET_ADMIN
    volumes:
      - openvpn-data:/etc/openvpn
      - ./custom-config:/etc/openvpn/custom:ro
    restart: unless-stopped
    environment:
      - GATEWAY_MODE=${GATEWAY_MODE:-0}
      - LDAP_ENABLED=${LDAP_ENABLED:-0}
      - WEBUI_USERNAME=${WEBUI_USERNAME:-admin}
      - WEBUI_PASSWORD=${WEBUI_PASSWORD:-openvpn}
      - DEBUG=${DEBUG:-0}
    networks:
      - vpn-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  openvpn-data:
    driver: local

networks:
  vpn-network:
    driver: bridge
```

---

## API 参考

Web UI 提供 RESTful API：

### 认证

所有 API 需要 HTTP Basic 认证：

```bash
curl -u admin:password http://localhost:8080/api/status
```

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/status` | GET | 获取系统状态 |
| `/api/mode` | GET/POST | 获取/设置运行模式 |
| `/api/ldap` | GET/POST | 获取/设置 LDAP 配置 |
| `/api/sites` | GET/POST/DELETE | 管理站点 |
| `/api/sites/<name>/cert` | GET/POST | 管理站点证书 |
| `/api/clients` | GET/POST/DELETE | 管理客户端 |
| `/api/clients/<name>/download` | GET | 下载客户端配置 |
| `/api/logs` | GET | 获取日志 |

### 示例

**切换模式**:
```bash
curl -u admin:password \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"mode": "gateway"}' \
  http://localhost:8080/api/mode
```

**添加站点**:
```bash
curl -u admin:password \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "huawei",
    "host": "vpn.huaweicloud.com",
    "port": "1194",
    "subnet": "172.16.0.0/16",
    "protocol": "udp"
  }' \
  http://localhost:8080/api/sites
```

---

**返回**: [主文档](../README.md)

