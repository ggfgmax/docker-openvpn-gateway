# Web 管理界面快速开始

## 🎯 5 分钟部署指南

### 步骤 1: 获取代码并构建

```bash
# 克隆项目
git clone https://github.com/ggfgmax/docker-openvpn-gateway.git
cd docker-openvpn-gateway

# 构建镜像
bash scripts/build-gateway.sh
```

### 步骤 2: 初始化配置

```bash
# 创建数据卷
docker volume create openvpn-data

# 生成配置（替换为你的域名或 IP）
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com

# 初始化 PKI（会提示设置 CA 密码，请使用强密码并记住）
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki
```

### 步骤 3: 配置环境变量（重要！）

```bash
# 复制配置模板
cp config/webui-config.example .env

# 编辑配置
vim .env
```

修改以下内容：
```bash
# 服务器配置
SERVER_URL=udp://vpn.yourdomain.com

# Web UI 认证（⚠️ 必须修改）
WEBUI_USERNAME=admin
WEBUI_PASSWORD=your-secure-password-here

# 运行模式（0=普通VPN, 1=网关模式）
GATEWAY_MODE=0
```

### 步骤 4: 启动服务

```bash
docker-compose -f docker-compose-webui.yml up -d
```

### 步骤 5: 访问 Web 界面

```
浏览器打开: http://服务器IP:8080
用户名: admin（或你设置的用户名）
密码: 你在 .env 中设置的密码
```

## 🎨 Web 界面功能

### 📊 概览页面
- 系统状态总览
- 运行模式显示
- 站点和客户端统计

### ⚙️ 模式设置
- 普通 VPN 模式
- 网关模式
- 一键切换

### 🔑 LDAP 配置
- 图形化 LDAP/AD 配置
- OpenLDAP 和 AD 模板
- 测试连接

### 🌐 站点管理
- 添加远程 VPN 站点
- **证书一键配置**（粘贴 .ovpn 内容）
- 查看站点状态

### 👥 客户端管理
- 生成客户端证书
- 一键下载 .ovpn 配置
- 吊销证书

## 🚀 典型使用流程

### 场景 1: 普通 VPN（企业内网访问）

```bash
# 1. 访问 Web UI

# 2. 生成客户端
# 点击 "👥 客户端管理"
# 输入客户端名称: zhangsan
# 点击 "生成客户端证书"
# 点击 "下载配置"

# 3. 分发给用户
# 将下载的 zhangsan.ovpn 发送给用户
```

### 场景 2: 多云网关

```bash
# 1. 切换到网关模式
# 点击 "⚙️ 模式设置"
# 选择 "网关模式"
# 点击 "保存模式设置"

# 2. 添加华为云站点
# 点击 "🌐 站点管理"
# 填写表单:
#   - 站点名称: huawei
#   - VPN 服务器地址: vpn.huaweicloud.com
#   - 端口: 1194
#   - 远程网段: 172.16.0.0/16
#   - 协议: UDP
# 点击 "添加站点"

# 3. 配置证书（超简单！）
# 在站点列表中找到 "huawei"
# 点击 "配置证书" 按钮
# 从华为云下载 .ovpn 文件
# 打开文件，复制全部内容
# 粘贴到弹出的文本框
# 点击 "保存证书配置"
# ✅ 完成！

# 4. 重复添加 AWS、GCP 等站点

# 5. 重启服务
docker restart openvpn-gateway

# 6. 生成客户端证书并分发
```

### 场景 3: LDAP 认证

```bash
# 1. 配置 LDAP
# 点击 "🔑 LDAP 配置"
# 点击 "Active Directory 模板"（或 OpenLDAP 模板）
# 修改服务器地址: ad.company.com
# 修改 Base DN: dc=company,dc=com
# 填写绑定 DN 和密码
# 点击 "保存 LDAP 配置"

# 2. 重启服务
docker restart openvpn-gateway

# 3. 客户端使用 AD 账户登录
```

## 🔐 安全配置

### 必做事项

1. **修改默认密码**
   ```bash
   # 在 .env 文件中
   WEBUI_PASSWORD=VeryStr0ng!Password
   ```

2. **配置 HTTPS**（生产环境）
   ```nginx
   # Nginx 反向代理配置
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

3. **限制访问 IP**
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8080
   sudo ufw deny 8080
   ```

## 🆘 常见问题

### Q: Web UI 无法访问

**解决方法**:
```bash
# 1. 检查容器状态
docker ps | grep openvpn

# 2. 查看日志
docker logs openvpn-gateway

# 3. 检查端口
docker port openvpn-gateway

# 4. 检查防火墙
sudo ufw status
```

### Q: 登录认证失败

**解决方法**:
```bash
# 检查环境变量
docker exec openvpn-gateway env | grep WEBUI

# 重新设置密码并重启
vim .env  # 修改 WEBUI_PASSWORD
docker-compose -f docker-compose-webui.yml restart
```

### Q: 站点证书配置失败

**解决方法**:
- 确保粘贴的是完整的 .ovpn 文件内容
- 检查是否包含 `<ca>`, `<cert>`, `<key>` 标签
- 查看浏览器控制台错误信息

### Q: 配置后需要重启吗？

**答**: 
- 模式切换: 需要重启
- LDAP 配置: 需要重启
- 添加站点: 需要重启
- 生成客户端: 不需要重启

重启命令:
```bash
docker restart openvpn-gateway
```

## 📚 进一步学习

- [多云网络配置详解](multi-cloud-gateway.md)
- [LDAP 认证配置](ldap.md)
- [Web UI 完整文档](webui.md)
- [故障排查指南](troubleshooting.md)

## 💡 小贴士

1. **首次使用**: 建议先在测试环境熟悉操作流程
2. **定期备份**: 
   ```bash
   docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
       tar czf /backup/openvpn-backup-$(date +%Y%m%d).tar.gz /etc/openvpn
   ```
3. **查看日志**: Web UI 中可以直接查看日志
4. **性能监控**: 关注服务器资源使用情况

---

**祝您使用愉快！** 🎉

有问题？查看 [完整文档](webui.md) 或 [提交 Issue](https://github.com/ggfgmax/docker-openvpn-gateway/issues)

