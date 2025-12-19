# 快速开始指南（中文）

## 目录

1. [基本概念](#基本概念)
2. [前置要求](#前置要求)
3. [快速部署](#快速部署)
4. [详细步骤](#详细步骤)
5. [常见问题](#常见问题)

## 基本概念

### 什么是多云网络主入口 VPN？

这是一个增强的 OpenVPN 服务器，它作为"主入口"，连接到多个云平台的 VPN 服务器。用户只需连接这一个 VPN，就能访问所有云平台的内网资源。

### 架构示意图

```
你的电脑
    ↓ (连接一次)
主入口 VPN 服务器
    ↓ (自动连接)
    ├─→ 华为云 VPN → 华为云内网 (172.16.0.0/16)
    ├─→ AWS VPN → AWS 内网 (10.0.0.0/16)
    └─→ GCP VPN → GCP 内网 (192.168.0.0/16)
```

### 解决的问题

**之前**: 需要在不同云平台的 VPN 之间来回切换
- 访问华为云 → 连接华为云 VPN
- 访问 AWS → 断开华为云，连接 AWS VPN
- 访问 GCP → 断开 AWS，连接 GCP VPN

**现在**: 只需连接主入口 VPN
- 连接主入口 VPN → 自动访问所有云平台

## 🌟 新功能：Web 管理界面

### 最简单的方式

如果您不熟悉命令行，可以使用 Web 管理界面！通过浏览器就能完成所有配置。

**3 步快速开始**:

```bash
# 1. 构建镜像
bash build-gateway.sh

# 2. 初始化
docker volume create openvpn-data
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki

# 3. 启动（带 Web UI）
docker-compose -f docker-compose-webui.yml up -d
```

**访问 Web 界面**: `http://服务器IP:8080`
- 默认用户名: `admin`
- 默认密码: `openvpn` ⚠️ 请立即修改！

**Web 界面能做什么**:
- ✅ 切换运行模式（普通/网关）
- ✅ 配置 LDAP 认证
- ✅ 添加远程站点
- ✅ 生成客户端证书
- ✅ 下载客户端配置
- ✅ 监控系统状态

**详细说明**: [Web 管理界面快速开始](WEBUI-QUICKSTART.md)

如果您熟悉命令行，可以继续阅读下面的内容。

---

## 前置要求

### 服务器要求

- **操作系统**: Linux（推荐 Ubuntu 20.04+ 或 CentOS 7+）
- **配置**: 至少 2 核 CPU，4GB 内存
- **网络**: 公网 IP，带宽至少 10Mbps
- **软件**: Docker 和 Docker Compose

### 云平台要求

在各个云平台（华为云、AWS、GCP 等）上，你需要已经部署了 OpenVPN 服务器，并获得：
- VPN 服务器地址和端口
- 客户端证书（.ovpn 配置文件或证书文件）
- 内网网段信息

### 安装 Docker

如果还没有安装 Docker：

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

## 快速部署

### 方法一：使用快速配置脚本（最简单）

1. **构建镜像**

```bash
cd /path/to/docker-openvpn-2.0.0
bash build-gateway.sh
```

2. **下载配置脚本**

```bash
docker run -v $PWD:/tmp --rm openvpn-gateway:latest \
    cp /usr/share/doc/openvpn/examples/multi-cloud-setup.sh /tmp/

chmod +x multi-cloud-setup.sh
```

3. **编辑配置**

```bash
vim multi-cloud-setup.sh
```

修改以下变量：
```bash
SERVER_URL="udp://你的服务器域名或IP"
HUAWEI_HOST="华为云VPN地址"
HUAWEI_SUBNET="华为云内网网段"
AWS_HOST="AWS VPN地址"
AWS_SUBNET="AWS内网网段"
GCP_HOST="GCP VPN地址"
GCP_SUBNET="GCP内网网段"
```

4. **运行配置脚本**

```bash
bash multi-cloud-setup.sh
```

5. **配置证书**（重要！）

```bash
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest bash
```

在容器内，编辑各站点配置文件：
```bash
vi /etc/openvpn/sites/huawei.conf
vi /etc/openvpn/sites/aws.conf
vi /etc/openvpn/sites/gcp.conf
```

从各云平台的 .ovpn 文件中复制证书内容，粘贴到对应的配置文件末尾。

证书格式示例：
```
<ca>
-----BEGIN CERTIFICATE-----
... 从 .ovpn 文件复制 ...
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
... 从 .ovpn 文件复制 ...
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
... 从 .ovpn 文件复制 ...
-----END PRIVATE KEY-----
</key>

<tls-auth>
-----BEGIN OpenVPN Static key V1-----
... 从 .ovpn 文件复制 ...
-----END OpenVPN Static key V1-----
</tls-auth>
key-direction 1
```

配置完成后输入 `exit` 退出容器。

6. **更新路由并启动服务**

```bash
# 更新路由配置
docker run -v ovpn-gateway-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_update_routes

# 重新生成配置
docker run -v ovpn-gateway-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://你的服务器域名或IP

# 启动服务
docker run -v ovpn-gateway-data:/etc/openvpn -d -p 1194:1194/udp \
    --cap-add=NET_ADMIN --name openvpn-gateway openvpn-gateway:latest
```

7. **生成客户端配置**

```bash
# 生成客户端证书
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    easyrsa build-client-full 你的用户名 nopass

# 导出客户端配置文件
docker run -v ovpn-gateway-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_getclient 你的用户名 > 你的用户名.ovpn
```

8. **客户端连接**

将生成的 `.ovpn` 文件导入 OpenVPN 客户端并连接。

### 方法二：使用 Docker Compose（推荐用于生产环境）

1. **准备配置**

```bash
cd /path/to/docker-openvpn-2.0.0
cp config.template config.env
vim config.env  # 编辑配置
```

2. **初始化配置**

```bash
# 创建数据卷
docker volume create ovpn-gateway-data

# 生成配置
docker run -v ovpn-gateway-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://你的服务器域名或IP

# 初始化 PKI
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki

# 初始化网关
docker run -v ovpn-gateway-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_setup_gateway -i
```

3. **添加站点并配置证书**（参考方法一的步骤 5-6）

4. **启动服务**

```bash
docker-compose -f docker-compose-gateway.yml up -d
```

5. **查看日志**

```bash
docker-compose -f docker-compose-gateway.yml logs -f
```

## 详细步骤

### 第一步：准备工作

1. **获取各云平台的 VPN 信息**

从华为云、AWS、GCP 等云平台获取以下信息：
- VPN 服务器地址（如 `vpn.example.com`）
- VPN 端口（通常是 1194）
- 协议（UDP 或 TCP）
- 内网网段（如 `172.16.0.0/16`）
- 客户端配置文件（.ovpn）

2. **准备主入口服务器**

确保你有一台可以作为主入口的服务器，并且：
- 已安装 Docker
- 有公网 IP
- 防火墙开放 UDP 1194 端口（或你自定义的端口）

### 第二步：构建镜像

```bash
cd /path/to/docker-openvpn-2.0.0
bash build-gateway.sh openvpn-gateway latest
```

### 第三步：初始化配置

```bash
# 创建数据卷
OVPN_DATA="ovpn-gateway-data"
docker volume create --name $OVPN_DATA

# 生成配置（替换为你的服务器地址）
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com

# 初始化 PKI（会提示输入 CA 密码，请使用强密码并记住）
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki

# 初始化网关
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_setup_gateway -i
```

### 第四步：添加云平台站点

为每个云平台添加站点配置：

```bash
# 添加华为云
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_add_remote_site \
    -n huawei \
    -h vpn.huaweicloud.example.com \
    -p 1194 \
    -s 172.16.0.0/16

# 添加 AWS
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_add_remote_site \
    -n aws \
    -h vpn.aws.example.com \
    -p 1194 \
    -s 10.0.0.0/16

# 添加 GCP
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_add_remote_site \
    -n gcp \
    -h vpn.gcp.example.com \
    -p 1194 \
    -s 192.168.0.0/16
```

### 第五步：配置证书（关键步骤）

这是最重要的一步，需要将各云平台的 VPN 客户端证书配置到对应的站点。

1. **进入容器**

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-gateway:latest bash
```

2. **编辑站点配置**

```bash
vi /etc/openvpn/sites/huawei.conf
```

3. **添加证书内容**

从各云平台下载的 `.ovpn` 文件中，找到证书部分（通常在文件末尾），复制到站点配置文件末尾。

需要复制的部分：
- `<ca>...</ca>`: CA 证书
- `<cert>...</cert>`: 客户端证书
- `<key>...</key>`: 客户端私钥
- `<tls-auth>...</tls-auth>`: TLS 认证密钥（如果有）

完整示例：
```
# ... 站点配置的其他内容 ...

<ca>
-----BEGIN CERTIFICATE-----
MIIDSzCCAjOgAwIBAgIUXxxx...
... 完整的证书内容 ...
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
MIIDYTCCAkmgAwIBAgIRAOxxx...
... 完整的证书内容 ...
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0B...
... 完整的私钥内容 ...
-----END PRIVATE KEY-----
</key>

<tls-auth>
-----BEGIN OpenVPN Static key V1-----
6acef03f62675b4b1bbd03bf...
... 完整的密钥内容 ...
-----END OpenVPN Static key V1-----
</tls-auth>
key-direction 1
```

4. **对所有站点重复此操作**

```bash
vi /etc/openvpn/sites/aws.conf
vi /etc/openvpn/sites/gcp.conf
```

5. **保存并退出**

```bash
exit
```

### 第六步：更新路由配置

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_update_routes
```

### 第七步：重新生成服务器配置

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com
```

### 第八步：启动主入口 VPN 服务器

```bash
docker run -v $OVPN_DATA:/etc/openvpn -d -p 1194:1194/udp \
    --cap-add=NET_ADMIN --name openvpn-gateway openvpn-gateway:latest
```

### 第九步：生成客户端配置

```bash
# 生成客户端证书
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-gateway:latest \
    easyrsa build-client-full zhangsan nopass

# 导出客户端配置
docker run -v $OVPN_DATA:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_getclient zhangsan > zhangsan.ovpn
```

### 第十步：客户端连接

将生成的 `zhangsan.ovpn` 文件发送给用户，使用 OpenVPN 客户端连接。

**Windows**: 安装 OpenVPN GUI，右键导入配置文件
**macOS**: 安装 Tunnelblick，拖拽配置文件到 Tunnelblick
**Linux**: `sudo openvpn --config zhangsan.ovpn`
**Android**: 安装 OpenVPN Connect，导入配置文件
**iOS**: 安装 OpenVPN Connect，导入配置文件

## 验证和测试

### 查看服务状态

```bash
# 查看容器状态
docker ps | grep openvpn-gateway

# 查看日志
docker logs openvpn-gateway

# 查看站点状态
docker exec openvpn-gateway ovpn_list_sites

# 查看网关状态
docker exec openvpn-gateway ovpn_setup_gateway -s
```

### 测试连通性

```bash
# 下载测试脚本
docker run -v $PWD:/tmp --rm openvpn-gateway:latest \
    cp /usr/share/doc/openvpn/examples/test-connectivity.sh /tmp/

# 运行测试
bash test-connectivity.sh openvpn-gateway
```

### 手动测试

在客户端连接后：

```bash
# Ping 华为云内网 IP
ping 172.16.0.1

# Ping AWS 内网 IP
ping 10.0.0.1

# Ping GCP 内网 IP
ping 192.168.0.1
```

## 常见问题

### Q1: 客户端无法连接到主入口 VPN

**检查清单**:
1. 防火墙是否开放 UDP 1194 端口
2. 服务器安全组规则是否允许
3. 容器是否正常运行：`docker ps`
4. 查看容器日志：`docker logs openvpn-gateway`

### Q2: 连接成功但无法访问云平台内网

**可能原因**:
1. Site-to-Site 连接未建立
2. 证书配置错误
3. 路由配置错误

**解决方法**:
```bash
# 检查站点连接状态
docker exec openvpn-gateway ovpn_list_sites

# 检查路由
docker exec openvpn-gateway ip route

# 查看 Site-to-Site 连接日志
docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
```

### Q3: Site-to-Site 连接无法建立

**检查清单**:
1. 远程 VPN 服务器地址是否正确
2. 证书是否正确配置
3. 远程 VPN 服务器是否允许客户端连接
4. 网络是否可达：`docker exec openvpn-gateway ping vpn.huaweicloud.example.com`

### Q4: 如何添加更多站点

```bash
# 添加新站点
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_add_remote_site \
    -n azure \
    -h vpn.azure.example.com \
    -p 1194 \
    -s 172.17.0.0/16

# 配置证书
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest bash
vi /etc/openvpn/sites/azure.conf
exit

# 更新路由
docker run -v ovpn-gateway-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_update_routes

# 重启容器
docker restart openvpn-gateway
```

### Q5: 如何删除站点

```bash
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest bash
rm /etc/openvpn/sites/站点名.*
ovpn_update_routes
exit

docker restart openvpn-gateway
```

### Q6: 如何备份配置

```bash
# 备份整个数据卷
docker run -v ovpn-gateway-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar czf /backup/openvpn-backup-$(date +%Y%m%d).tar.gz /etc/openvpn

# 恢复备份
docker run -v ovpn-gateway-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar xzf /backup/openvpn-backup-20241219.tar.gz -C /
```

### Q7: 性能优化建议

1. **增加服务器配置**: 至少 4 核 CPU，8GB 内存用于大量用户
2. **调整 MTU**: 如果有分片问题，降低 MTU 值
3. **使用 TCP**: 对于不稳定的网络，可以使用 TCP 协议
4. **启用压缩**: `ovpn_genconfig -u udp://... -z`

### Q8: 如何查看详细日志

```bash
# 主服务器日志
docker logs -f openvpn-gateway

# Site-to-Site 连接日志
docker exec openvpn-gateway tail -f /var/log/openvpn-huawei.log
docker exec openvpn-gateway tail -f /var/log/openvpn-aws.log
docker exec openvpn-gateway tail -f /var/log/openvpn-gcp.log
```

## 进阶配置

### 使用 TCP 协议

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_add_remote_site \
    -n huawei \
    -h vpn.huaweicloud.example.com \
    -p 443 \
    -P tcp \
    -s 172.16.0.0/16
```

### 启用双因素认证

参考原项目文档: `docs/otp.md`

### 配置静态 IP

参考原项目文档: `docs/static-ips.md`

## 获取帮助

- 📚 查看完整文档: `docs/multi-cloud-gateway.md`
- 📝 查看更新日志: `CHANGELOG-GATEWAY.md`
- 💬 提交问题: 在 GitHub 创建 Issue

## 高级功能

### 模式切换

支持在普通 VPN 和网关模式之间切换：

```bash
# 查看当前模式
docker exec openvpn-gateway ovpn_set_mode

# 切换到普通 VPN 模式
docker exec openvpn-gateway ovpn_set_mode normal

# 切换到网关模式
docker exec openvpn-gateway ovpn_set_mode gateway

# 重启服务生效
docker restart openvpn-gateway
```

详细说明: [模式切换指南](docs/mode-switching.md)

### LDAP 认证

支持使用企业 LDAP/AD 账户登录：

```bash
# 配置 LDAP（OpenLDAP）
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_config_ldap \
    -h ldap.company.com \
    -b "dc=company,dc=com" \
    -D "cn=admin,dc=company,dc=com" \
    -w "password"

# 配置 LDAP（Active Directory）
docker run -v ovpn-gateway-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_config_ldap \
    -h ad.company.com \
    -b "dc=company,dc=com" \
    -D "CN=VPN Service,OU=Service Accounts,DC=company,DC=com" \
    -w "password" \
    -f "(&(objectClass=user)(sAMAccountName=%u))" \
    -s sAMAccountName

# 重新生成配置启用 LDAP
docker run -v ovpn-gateway-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com -2

# 重启服务
docker restart openvpn-gateway
```

客户端连接时会提示输入 LDAP 用户名和密码。

详细说明: [LDAP 认证指南](docs/ldap.md)

### 快速配置脚本

**LDAP 配置脚本**:
```bash
# 下载脚本
docker run -v $PWD:/tmp --rm openvpn-gateway:latest \
    cp /usr/share/doc/openvpn/examples/ldap-setup.sh /tmp/

# 编辑配置
vim ldap-setup.sh

# 运行脚本
bash ldap-setup.sh
```

## 总结

通过本指南，你应该能够成功部署一个多云网络主入口 VPN 网关。关键步骤是：

1. ✅ 构建镜像
2. ✅ 初始化配置和 PKI
3. ✅ 添加云平台站点
4. ✅ **配置证书**（最重要）
5. ✅ 更新路由配置
6. ✅ 启动服务
7. ✅ 生成客户端配置
8. ✅ 测试连接

祝你使用愉快！🎉

