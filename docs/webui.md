# Web 管理界面使用指南

## 概述

OpenVPN Web 管理界面提供了简单易用的图形化配置和管理功能，让不熟悉命令行的用户也能轻松管理 OpenVPN 服务器。

## 功能特性

- ✅ **友好的图形界面** - 无需命令行操作
- ✅ **实时状态监控** - 查看服务器、站点和客户端状态
- ✅ **模式切换** - 一键切换普通 VPN 和网关模式
- ✅ **LDAP 配置** - 图形化配置 LDAP/AD 认证
- ✅ **站点管理** - 添加、删除远程 VPN 站点
- ✅ **客户端管理** - 生成、下载、吊销客户端证书
- ✅ **基础认证** - 用户名密码保护

## 快速开始

### 方法一：使用 Docker Compose（推荐）

1. **创建配置文件**

```bash
cd /path/to/docker-openvpn-2.0.0
cp config.template .env
```

2. **编辑 .env 文件**

```bash
# VPN 配置
SERVER_URL=udp://vpn.yourdomain.com
GATEWAY_MODE=0  # 0=普通模式, 1=网关模式
LDAP_ENABLED=0  # 0=禁用, 1=启用

# Web UI 认证（请务必修改！）
WEBUI_USERNAME=admin
WEBUI_PASSWORD=your-secure-password-here
```

3. **启动服务**

```bash
# 首次启动需要初始化
docker-compose -f docker-compose-webui.yml run --rm openvpn-gateway ovpn_genconfig -u udp://vpn.yourdomain.com
docker-compose -f docker-compose-webui.yml run --rm openvpn-gateway ovpn_initpki

# 启动服务
docker-compose -f docker-compose-webui.yml up -d
```

4. **访问 Web 界面**

浏览器打开: `http://服务器IP:8080`

- 用户名: `admin`（或你设置的 WEBUI_USERNAME）
- 密码: `openvpn`（或你设置的 WEBUI_PASSWORD）

### 方法二：直接运行

```bash
# 构建镜像
docker build -t openvpn-gateway .

# 运行容器（包含 Web UI）
docker run -d \
  -v openvpn-data:/etc/openvpn \
  -p 1194:1194/udp \
  -p 8080:8080 \
  -e WEBUI_USERNAME=admin \
  -e WEBUI_PASSWORD=your-password \
  --cap-add=NET_ADMIN \
  --name openvpn-gateway \
  openvpn-gateway \
  sh -c "ovpn_run_webui & ovpn_run"
```

## 界面功能介绍

### 📊 概览页面

显示系统整体状态：
- 运行模式（普通/网关）
- LDAP 认证状态
- 站点数量和状态
- 客户端数量

### ⚙️ 模式设置

切换 VPN 运行模式：

**普通 VPN 模式**:
- 标准的 OpenVPN 功能
- 适合简单远程访问
- 资源消耗低

**网关模式**:
- 多云网络打通
- Site-to-Site VPN
- 适合多云环境

操作步骤：
1. 选择要切换的模式
2. 点击"保存模式设置"
3. 重启容器使配置生效

### 🔑 LDAP 配置

图形化配置 LDAP/AD 认证：

**快速配置**:
1. 点击"OpenLDAP 模板"或"Active Directory 模板"
2. 修改服务器地址和 Base DN
3. 填写绑定 DN 和密码（如需要）
4. 点击"保存 LDAP 配置"

**配置项说明**:
- **LDAP 服务器地址**: LDAP 服务器的主机名或 IP
- **端口**: 默认 389 (LDAP) 或 636 (LDAPS)
- **Base DN**: LDAP 搜索的基础 DN
- **绑定 DN**: 用于连接 LDAP 的账户（可选）
- **绑定密码**: 绑定 DN 的密码（可选）
- **用户过滤器**: 用户搜索过滤器
- **搜索属性**: 用户名属性（uid 或 sAMAccountName）
- **使用 LDAPS**: 启用 TLS 加密

### 🌐 站点管理

管理远程 VPN 站点（网关模式）：

**添加站点**:
1. 填写站点信息：
   - 站点名称（如 huawei, aws, gcp）
   - VPN 服务器地址
   - 端口（默认 1194）
   - 远程网段（如 172.16.0.0/16）
   - 协议（UDP 或 TCP）
2. 点击"添加站点"
3. **重要**: 需要手动配置站点证书（见下文）

**配置站点证书**:

添加站点后，需要配置证书才能连接：

```bash
# 方法 1: 进入容器手动配置
docker exec -it openvpn-gateway bash
vi /etc/openvpn/sites/huawei.conf
# 在文件末尾添加证书内容（从远程 VPN 的 .ovpn 文件复制）
exit

# 方法 2: 从宿主机直接编辑
docker exec -it openvpn-gateway vi /etc/openvpn/sites/huawei.conf
```

证书格式示例：
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
```

**删除站点**:
1. 在站点列表中找到要删除的站点
2. 点击"删除"按钮
3. 确认删除

### 👥 客户端管理

管理客户端证书：

**生成新客户端**:
1. 输入客户端名称（如 zhangsan）
2. 点击"生成客户端证书"
3. 等待生成完成

**下载配置文件**:
1. 在客户端列表中找到对应客户端
2. 点击"下载配置"按钮
3. 将下载的 .ovpn 文件发送给用户

**吊销客户端**:
1. 在客户端列表中找到要吊销的客户端
2. 点击"吊销"按钮
3. 确认吊销（此操作不可恢复）

## 安全建议

### 1. 修改默认密码

**必须修改默认密码！** 默认密码 `openvpn` 不安全。

方法：
```bash
# 在 .env 文件中设置
WEBUI_USERNAME=your-username
WEBUI_PASSWORD=your-strong-password

# 或在 docker run 中设置
-e WEBUI_USERNAME=your-username \
-e WEBUI_PASSWORD=your-strong-password
```

### 2. 使用 HTTPS

生产环境建议在 Web UI 前面配置反向代理（如 Nginx），启用 HTTPS。

Nginx 配置示例：

```nginx
server {
    listen 443 ssl;
    server_name vpn-admin.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 启用 Basic Auth
        auth_basic "OpenVPN Admin";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }
}
```

### 3. 限制访问

使用防火墙限制只允许特定 IP 访问 Web UI：

```bash
# UFW
sudo ufw allow from 192.168.1.0/24 to any port 8080

# iptables
iptables -A INPUT -p tcp --dport 8080 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
```

### 4. 定期备份

定期备份 OpenVPN 配置：

```bash
docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar czf /backup/openvpn-backup-$(date +%Y%m%d).tar.gz /etc/openvpn
```

## 故障排查

### Web UI 无法访问

1. **检查容器是否运行**:
```bash
docker ps | grep openvpn-gateway
```

2. **检查端口映射**:
```bash
docker port openvpn-gateway
```

3. **查看日志**:
```bash
docker logs openvpn-gateway
```

4. **检查防火墙**:
```bash
# 确保 8080 端口开放
sudo ufw status
sudo iptables -L -n | grep 8080
```

### 认证失败

检查环境变量是否正确设置：

```bash
docker exec openvpn-gateway env | grep WEBUI
```

### 功能操作失败

1. **检查容器权限**:
```bash
# 确保容器有 NET_ADMIN 权限
docker inspect openvpn-gateway | grep -A 5 CapAdd
```

2. **查看详细错误**:
打开浏览器开发者工具（F12），查看 Console 和 Network 标签

### 站点连接失败

1. **检查证书配置**:
```bash
docker exec openvpn-gateway cat /etc/openvpn/sites/huawei.conf
```

2. **查看站点连接日志**:
```bash
docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
```

## API 文档

Web UI 提供了 RESTful API，可以用于脚本自动化。

### 认证

所有 API 请求都需要 HTTP Basic 认证：

```bash
curl -u admin:password http://localhost:8080/api/status
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/status` | GET | 获取系统状态 |
| `/api/mode` | GET/POST | 获取/设置运行模式 |
| `/api/ldap` | GET/POST | 获取/设置 LDAP 配置 |
| `/api/sites` | GET/POST/DELETE | 管理站点 |
| `/api/clients` | GET/POST/DELETE | 管理客户端 |
| `/api/clients/<name>/download` | GET | 下载客户端配置 |
| `/api/logs` | GET | 获取日志 |

### 示例

**获取状态**:
```bash
curl -u admin:password http://localhost:8080/api/status
```

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

## 常见问题

### Q: Web UI 可以用于生产环境吗？

A: 可以，但需要：
1. 修改默认密码
2. 配置 HTTPS（使用 Nginx 反向代理）
3. 限制访问 IP
4. 定期备份配置

### Q: Web UI 支持多用户吗？

A: 当前版本使用简单的 HTTP Basic 认证，所有用户使用相同的用户名密码。如需多用户支持，建议在 Nginx 层面配置。

### Q: 可以禁用 Web UI 吗？

A: 可以，使用原始的 docker-compose-gateway.yml 而不是 docker-compose-webui.yml。

### Q: Web UI 会影响 VPN 性能吗？

A: 影响很小。Web UI 是独立进程，只在访问管理界面时才会使用资源。

### Q: 如何更新 Web UI？

A: 重新构建镜像：
```bash
docker-compose -f docker-compose-webui.yml build
docker-compose -f docker-compose-webui.yml up -d
```

## 总结

Web 管理界面大大简化了 OpenVPN 的配置和管理：

- ✅ 无需记忆复杂的命令
- ✅ 图形化操作，直观易懂
- ✅ 实时状态监控
- ✅ 适合小白用户
- ✅ 同时支持高级功能

对于不熟悉命令行的用户，Web UI 是最佳选择！

