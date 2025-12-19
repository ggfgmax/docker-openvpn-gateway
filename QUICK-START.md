# ⚡ 3 分钟快速开始

## 🎯 最快部署方式

### 步骤 1: 获取代码

```bash
git clone https://github.com/ggfgmax/docker-openvpn-gateway.git
cd docker-openvpn-gateway
```

### 步骤 2: 一键构建和初始化

```bash
# 构建镜像
bash scripts/build-gateway.sh

# 创建数据卷
docker volume create openvpn-data

# 生成配置（⚠️ 替换为你的域名或 IP）
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://你的服务器地址

# 初始化 PKI（会提示设置 CA 密码）
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki
```

### 步骤 3: 配置并启动

```bash
# 复制配置模板
cp config/webui-config.example .env

# 编辑配置（⚠️ 必须修改密码）
vim .env
```

修改以下内容：
```bash
WEBUI_USERNAME=admin
WEBUI_PASSWORD=你的强密码
```

启动服务：
```bash
docker-compose -f docker-compose-webui.yml up -d
```

### 步骤 4: 访问 Web 界面

```
🌐 浏览器打开: http://服务器IP:8080
👤 用户名: admin
🔑 密码: 你设置的密码
```

## ✅ 完成！

现在你可以：
- ✅ 在 Web UI 中生成客户端证书
- ✅ 下载 .ovpn 配置文件
- ✅ 配置 LDAP 认证
- ✅ 添加多云站点
- ✅ 切换运行模式

## 📖 下一步

- [Web UI 使用指南](docs/quickstart-webui.md)
- [多云网络配置](docs/multi-cloud-gateway.md)
- [LDAP 认证配置](docs/ldap.md)
- [常见问题](docs/faq.md)

---

**遇到问题？** 查看 [故障排查](docs/troubleshooting.md)

