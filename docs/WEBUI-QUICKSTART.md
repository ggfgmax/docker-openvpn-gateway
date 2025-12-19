# Web 管理界面快速开始

## 🎯 一键启动指南（3 步完成）

### 步骤 1: 构建镜像

```bash
cd /path/to/docker-openvpn-2.0.0
bash build-gateway.sh
```

### 步骤 2: 初始化配置

```bash
# 创建数据卷
docker volume create openvpn-data

# 生成基础配置（替换为你的服务器地址）
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com

# 初始化证书系统（会提示设置 CA 密码）
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki
```

### 步骤 3: 启动服务（包含 Web 管理界面）

```bash
docker run -d \
  --name openvpn-gateway \
  -v openvpn-data:/etc/openvpn \
  -p 1194:1194/udp \
  -p 8080:8080 \
  -e WEBUI_USERNAME=admin \
  -e WEBUI_PASSWORD=请修改这个密码 \
  -e GATEWAY_MODE=0 \
  --cap-add=NET_ADMIN \
  openvpn-gateway:latest \
  sh -c "ovpn_run_webui & ovpn_run"
```

### 访问 Web 界面

打开浏览器访问: **http://服务器IP:8080**

- 用户名: `admin`
- 密码: `请修改这个密码`（你在步骤 3 设置的密码）

## 🚀 使用 Docker Compose（更简单）

### 1. 准备配置文件

```bash
cd /path/to/docker-openvpn-2.0.0

# 创建环境变量文件
cat > .env <<EOF
# 服务器配置
SERVER_URL=udp://vpn.yourdomain.com

# 模式配置
GATEWAY_MODE=0
LDAP_ENABLED=0

# Web UI 认证（请务必修改！）
WEBUI_USERNAME=admin
WEBUI_PASSWORD=your-secure-password

# 调试
DEBUG=0
EOF
```

### 2. 初始化

```bash
# 创建数据卷
docker volume create openvpn-data

# 生成配置
docker-compose -f docker-compose-webui.yml run --rm openvpn-gateway \
    ovpn_genconfig -u udp://vpn.yourdomain.com

# 初始化 PKI
docker-compose -f docker-compose-webui.yml run --rm -it openvpn-gateway \
    ovpn_initpki
```

### 3. 启动

```bash
docker-compose -f docker-compose-webui.yml up -d
```

### 4. 访问

浏览器打开: **http://服务器IP:8080**

## 📱 Web 界面使用

### 首次使用

1. **登录 Web 界面**
   - 输入你设置的用户名和密码
   
2. **查看概览**
   - 首页显示当前系统状态
   - 运行模式、LDAP 状态、站点数量等

3. **生成第一个客户端**
   - 点击 "👥 客户端管理" 标签
   - 输入客户端名称（如 `zhangsan`）
   - 点击 "生成客户端证书"
   - 点击 "下载配置"
   - 将 .ovpn 文件发送给用户

### 常用操作

#### 切换运行模式

1. 点击 "⚙️ 模式设置"
2. 选择 "普通 VPN 模式" 或 "网关模式"
3. 点击 "保存模式设置"
4. 重启容器：`docker restart openvpn-gateway`

#### 配置 LDAP 认证

1. 点击 "🔑 LDAP 配置"
2. 点击 "OpenLDAP 模板" 或 "Active Directory 模板"
3. 修改服务器地址和 Base DN
4. 填写绑定凭据（如果需要）
5. 点击 "保存 LDAP 配置"
6. 重启容器

#### 添加远程站点（网关模式）

1. 先切换到网关模式
2. 点击 "🌐 站点管理"
3. 填写站点信息：
   - 站点名称：`huawei`
   - VPN 服务器地址：`vpn.huaweicloud.com`
   - 远程网段：`172.16.0.0/16`
4. 点击 "添加站点"
5. **重要**：配置站点证书（见下文）

#### 配置站点证书

添加站点后，需要配置证书：

```bash
# 进入容器
docker exec -it openvpn-gateway bash

# 编辑站点配置
vi /etc/openvpn/sites/huawei.conf

# 在文件末尾添加从远程 VPN 下载的证书内容
# （从 .ovpn 文件中复制 <ca>, <cert>, <key> 部分）

# 保存退出
exit

# 重启容器
docker restart openvpn-gateway
```

## 🔐 安全配置

### 必做：修改默认密码

**默认密码 `openvpn` 不安全！**

修改方法：

1. **使用环境变量**:
```bash
docker run ... \
  -e WEBUI_USERNAME=myadmin \
  -e WEBUI_PASSWORD=VeryStr0ng!Pass \
  ...
```

2. **使用 Docker Compose**:
在 `.env` 文件中：
```
WEBUI_USERNAME=myadmin
WEBUI_PASSWORD=VeryStr0ng!Pass
```

### 推荐：使用 HTTPS

生产环境建议配置 Nginx 反向代理：

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
    }
}
```

### 限制访问

使用防火墙限制 Web UI 访问：

```bash
# 只允许特定 IP 访问
sudo ufw allow from 192.168.1.0/24 to any port 8080
sudo ufw deny 8080
```

## 📊 完整示例

### 示例 1: 普通 VPN + LDAP

```bash
# 1. 启动服务
docker run -d \
  --name openvpn \
  -v openvpn-data:/etc/openvpn \
  -p 1194:1194/udp \
  -p 8080:8080 \
  -e GATEWAY_MODE=0 \
  -e WEBUI_USERNAME=admin \
  -e WEBUI_PASSWORD=SecurePass123 \
  --cap-add=NET_ADMIN \
  openvpn-gateway:latest \
  sh -c "ovpn_run_webui & ovpn_run"

# 2. 访问 Web UI: http://服务器IP:8080

# 3. 在 Web UI 中配置 LDAP:
#    - 点击 "LDAP 配置"
#    - 填写 LDAP 服务器信息
#    - 保存配置

# 4. 生成客户端证书并下载
```

### 示例 2: 网关模式 + 多云

```bash
# 1. 启动服务（网关模式）
docker run -d \
  --name openvpn-gateway \
  -v openvpn-data:/etc/openvpn \
  -p 1194:1194/udp \
  -p 8080:8080 \
  -e GATEWAY_MODE=1 \
  -e WEBUI_USERNAME=admin \
  -e WEBUI_PASSWORD=SecurePass123 \
  --cap-add=NET_ADMIN \
  openvpn-gateway:latest \
  sh -c "ovpn_run_webui & ovpn_run"

# 2. 访问 Web UI: http://服务器IP:8080

# 3. 在 Web UI 中添加远程站点:
#    - 点击 "站点管理"
#    - 添加华为云站点
#    - 添加 AWS 站点
#    - 添加 GCP 站点

# 4. 手动配置各站点的证书（通过 SSH）

# 5. 重启服务
docker restart openvpn-gateway

# 6. 生成客户端证书并下载
```

## 🆘 常见问题

### Q: 无法访问 Web UI

**检查清单**:
1. 容器是否运行：`docker ps`
2. 端口是否映射：`docker port openvpn-gateway`
3. 防火墙是否开放：`sudo ufw status`
4. 查看日志：`docker logs openvpn-gateway`

### Q: 认证失败

**解决方法**:
1. 确认用户名密码正确
2. 检查环境变量：`docker exec openvpn-gateway env | grep WEBUI`

### Q: 客户端生成失败

**可能原因**:
1. PKI 未初始化：运行 `ovpn_initpki`
2. 客户端名称已存在：换一个名称

### Q: 站点连接失败

**检查步骤**:
1. 确认已切换到网关模式
2. 检查站点证书是否配置
3. 查看站点日志：`docker exec openvpn-gateway cat /var/log/openvpn-huawei.log`

## 📚 相关文档

- [Web UI 完整文档](docs/webui.md)
- [多云网关配置](docs/multi-cloud-gateway.md)
- [LDAP 认证配置](docs/ldap.md)
- [模式切换指南](docs/mode-switching.md)

## 💡 提示

1. **首次使用**：建议先熟悉 "概览" 和 "客户端管理" 功能
2. **生产环境**：务必修改默认密码并配置 HTTPS
3. **网关模式**：需要手动配置站点证书才能连接
4. **定期备份**：定期备份 `/etc/openvpn` 目录
5. **查看日志**：遇到问题先查看容器日志

## 🎉 开始使用

按照上面的步骤，3 分钟内就能启动带有 Web 管理界面的 OpenVPN 服务器！

有问题请查看完整文档或提交 Issue。

祝您使用愉快！

