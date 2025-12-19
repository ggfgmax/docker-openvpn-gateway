# OpenVPN 多云网络主入口网关 🚀

一个增强版的 Docker OpenVPN，支持 **Web 管理界面**、**多云网络打通**、**LDAP 认证**。  
让小白也能轻松配置和管理 VPN！

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 🌟 为什么选择这个项目？

### 痛点
- ❌ 访问华为云要连华为云 VPN
- ❌ 访问 AWS 要断开华为云，连 AWS VPN  
- ❌ 访问 GCP 要再切换一次...
- ❌ 配置复杂，命令行操作困难

### 解决方案
- ✅ **一个 VPN 访问所有云平台**
- ✅ **Web 界面配置，零命令行**
- ✅ **5 分钟快速部署**
- ✅ **小白也能用**

## ⚡ 3 分钟快速开始

```bash
# 1. 克隆项目
git clone https://github.com/ggfgmax/docker-openvpn-gateway.git
cd docker-openvpn-gateway

# 2. 构建镜像
bash scripts/build-gateway.sh

# 3. 初始化（替换为你的域名或 IP）
docker volume create openvpn-data
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki

# 4. 配置密码
cp config/webui-config.example .env
vim .env  # 修改 WEBUI_PASSWORD

# 5. 启动（包含 Web UI）
docker-compose -f docker-compose-webui.yml up -d

# 6. 访问 Web 界面
# 浏览器打开: http://服务器IP:8080
# 用户名: admin  密码: 你设置的密码
```

**就这么简单！** 🎉

## 🎨 Web 管理界面

所有操作都可以在浏览器中完成，无需命令行！

### 主要功能

**📊 系统概览**
- 运行模式、LDAP 状态
- 站点和客户端统计
- 实时状态刷新

**⚙️ 模式切换**
- 普通 VPN 模式（标准远程访问）
- 网关模式（多云网络打通）
- 一键切换

**🔑 LDAP 配置**
- 图形化配置 LDAP/AD
- 内置 OpenLDAP 和 AD 模板
- 一键填充常用配置

**🌐 站点管理**（网关模式）
- 添加远程 VPN 站点
- **证书一键配置** - 直接粘贴 .ovpn 内容 ⭐
- 查看站点连接状态
- 删除站点

**👥 客户端管理**
- 生成客户端证书
- 一键下载 .ovpn 配置文件
- 吊销证书

## 📖 使用指南

### 场景 1: 企业内网访问（普通 VPN）

**需求**: 员工远程访问公司内网

**操作**:
1. 访问 Web UI
2. 生成客户端证书（输入员工姓名，点击生成）
3. 下载 .ovpn 文件
4. 发送给员工

**可选**: 配置 LDAP，员工用 AD 账户登录

---

### 场景 2: 多云网络打通（网关模式）⭐

**需求**: 在华为云、AWS、GCP 都有资源，需要统一访问

**操作**:

1. **切换到网关模式**
   - Web UI → 模式设置 → 选择"网关模式" → 保存

2. **添加华为云站点**
   - Web UI → 站点管理
   - 填写信息:
     - 站点名称: `huawei`
     - VPN 服务器地址: `vpn.huaweicloud.com`
     - 端口: `1194`
     - 远程网段: `172.16.0.0/16`（华为云内网网段）
     - 协议: `UDP`
   - 点击"添加站点"

3. **配置证书**（超简单！）
   - 从华为云下载客户端 `.ovpn` 文件
   - 在站点列表中点击"配置证书"按钮
   - 打开 `.ovpn` 文件，复制**全部内容**
   - 粘贴到弹出的文本框
   - 点击"保存证书配置"
   - ✅ 看到"配置成功"提示

4. **重复添加 AWS、GCP 站点**
   - 同样的步骤添加其他云平台

5. **重启服务**
   ```bash
   docker restart openvpn-gateway
   ```

6. **生成客户端证书**
   - Web UI → 客户端管理
   - 输入客户端名称，点击生成
   - 下载 .ovpn 文件

7. **客户端连接**
   - 用户导入 .ovpn 文件连接
   - 自动可以访问华为云、AWS、GCP 所有内网！

**架构示意**:
```
你的电脑
    ↓ 连接一次
主入口 VPN
    ↓ 自动连接
    ├─→ 华为云 VPN → 华为云内网 (172.16.0.0/16)
    ├─→ AWS VPN → AWS 内网 (10.0.0.0/16)
    └─→ GCP VPN → GCP 内网 (192.168.0.0/16)
```

---

### 场景 3: LDAP/AD 认证

**需求**: 使用企业 AD 账户登录 VPN

**操作**:

1. **配置 LDAP**
   - Web UI → LDAP 配置
   - 点击"Active Directory 模板"（或 OpenLDAP 模板）
   - 修改服务器地址: `ad.company.com`
   - 修改 Base DN: `dc=company,dc=com`
   - 填写绑定 DN 和密码（服务账户）
   - 点击"保存 LDAP 配置"

2. **重启服务**
   ```bash
   docker restart openvpn-gateway
   ```

3. **客户端使用**
   - 连接时会提示输入用户名密码
   - 输入 AD 账户信息即可

**LDAP 配置示例**:

```
OpenLDAP:
  服务器: ldap.company.com
  Base DN: dc=company,dc=com
  过滤器: (&(objectClass=posixAccount)(uid=%u))
  搜索属性: uid

Active Directory:
  服务器: ad.company.com
  Base DN: dc=company,dc=com
  过滤器: (&(objectClass=user)(sAMAccountName=%u))
  搜索属性: sAMAccountName
```

## 🔧 命令行方式（可选）

如果你熟悉命令行，也可以直接使用命令：

### 基础命令

```bash
# 查看当前模式
docker exec openvpn-gateway ovpn_set_mode

# 切换模式
docker exec openvpn-gateway ovpn_set_mode gateway

# 添加站点
docker exec openvpn-gateway ovpn_add_remote_site \
    -n huawei -h vpn.huawei.com -p 1194 -s 172.16.0.0/16

# 查看站点
docker exec openvpn-gateway ovpn_list_sites

# 配置 LDAP
docker exec openvpn-gateway ovpn_config_ldap \
    -h ldap.company.com -b "dc=company,dc=com"
```

### 快速配置脚本

```bash
# 多云环境快速配置
bash scripts/setup/multi-cloud-setup.sh

# LDAP 快速配置
bash scripts/setup/ldap-setup.sh

# 测试连通性
bash scripts/tests/test-connectivity.sh
```

## 🔐 安全配置

### 必做事项 ⚠️

1. **修改 Web UI 默认密码**
   ```bash
   # 在 .env 文件中
   WEBUI_USERNAME=youradmin
   WEBUI_PASSWORD=VeryStr0ng!Password
   ```

2. **使用 HTTPS**（生产环境）
   ```nginx
   # Nginx 反向代理
   server {
       listen 443 ssl;
       server_name vpn-admin.yourdomain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8080;
       }
   }
   ```

3. **限制访问 IP**
   ```bash
   # 只允许公司 IP 访问 Web UI
   sudo ufw allow from 192.168.1.0/24 to any port 8080
   sudo ufw deny 8080
   ```

4. **定期备份**
   ```bash
   docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
       tar czf /backup/backup-$(date +%Y%m%d).tar.gz /etc/openvpn
   ```

## 🆘 常见问题

### Q: Web UI 无法访问？

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

### Q: 客户端无法连接？

```bash
# 1. 检查防火墙（UDP 1194）
sudo ufw allow 1194/udp

# 2. 检查云服务商安全组
# AWS Security Groups / 华为云安全组 / GCP Firewall

# 3. 查看日志
docker logs openvpn-gateway
```

### Q: 站点连接失败？

**检查清单**:
- ✅ 是否切换到网关模式
- ✅ 证书是否正确配置（在 Web UI 中查看状态）
- ✅ 远程 VPN 服务器是否运行
- ✅ 网络是否连通

**查看站点日志**:
```bash
docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
```

### Q: LDAP 认证失败？

**测试 LDAP 连接**:
```bash
docker exec openvpn-gateway ldapsearch -x \
    -H ldap://ldap.company.com \
    -b "dc=company,dc=com" \
    "(uid=testuser)"
```

**常见问题**:
- Base DN 错误 → 检查 LDAP 服务器配置
- 绑定 DN 无权限 → 使用有搜索权限的账户
- 过滤器不匹配 → 调整用户过滤器

### Q: 无法访问远程网段？

```bash
# 1. 确认在网关模式
docker exec openvpn-gateway ovpn_set_mode

# 2. 更新路由
docker exec openvpn-gateway ovpn_update_routes
docker restart openvpn-gateway

# 3. 检查路由表
docker exec openvpn-gateway ip route

# 4. 从服务器测试
docker exec openvpn-gateway ping -c 3 172.16.0.1
```

### Q: 如何备份和恢复？

**备份**:
```bash
docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar czf /backup/openvpn-backup-$(date +%Y%m%d).tar.gz /etc/openvpn
```

**恢复**:
```bash
docker-compose -f docker-compose-webui.yml down
docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar xzf /backup/openvpn-backup-20241219.tar.gz -C /
docker-compose -f docker-compose-webui.yml up -d
```

## 📁 项目结构

```
docker-openvpn-gateway/
├── README.md                    # 本文件（主文档）
├── Dockerfile                   # Docker 镜像定义
├── docker-compose-webui.yml     # Web UI 部署（推荐）
├── docker-compose-gateway.yml   # 标准部署
│
├── bin/                         # 核心管理脚本
│   ├── ovpn_genconfig          # 生成配置
│   ├── ovpn_run                # 运行服务
│   ├── ovpn_set_mode           # 切换模式
│   ├── ovpn_config_ldap        # 配置 LDAP
│   ├── ovpn_add_remote_site    # 添加站点
│   └── ...
│
├── webui/                       # Web 管理界面
│   ├── app.py                  # Flask 后端
│   └── templates/              # HTML 页面
│
├── scripts/                     # 辅助脚本
│   ├── build-gateway.sh        # 构建镜像
│   ├── setup/                  # 快速配置脚本
│   └── tests/                  # 测试脚本
│
├── config/                      # 配置模板
│   ├── config.template
│   └── webui-config.example
│
└── docs/                        # 高级文档（可选阅读）
    └── advanced-config.md      # 高级配置说明
```

## 🎯 核心功能

### 1. 普通 VPN 模式（默认）

标准的 OpenVPN 服务器，适合：
- 员工远程访问公司内网
- 简单的远程办公场景
- 资源消耗低

### 2. 网关模式

多云网络主入口，适合：
- 多个云平台（华为云、AWS、GCP）
- 混合云架构
- 需要打通多个 VPN 网络

**自动功能**:
- Site-to-Site VPN 隧道管理
- 智能路由配置
- iptables 转发规则
- 流量自动转发

### 3. LDAP/AD 认证

企业级身份验证：
- OpenLDAP 支持
- Active Directory 支持
- 双因素认证（证书 + LDAP）

### 4. Web 管理界面

零命令行操作：
- 图形化配置
- 实时状态监控
- 证书一键配置
- 适合所有用户

## 🔧 高级配置

### 环境变量

在 `.env` 文件或 docker-compose.yml 中配置：

```yaml
environment:
  # 运行模式（0=普通VPN, 1=网关模式）
  - GATEWAY_MODE=0
  
  # LDAP 认证（0=禁用, 1=启用）
  - LDAP_ENABLED=0
  
  # Web UI 认证
  - WEBUI_USERNAME=admin
  - WEBUI_PASSWORD=your-password
  
  # 调试模式
  - DEBUG=0
```

### 使用 TCP 协议

```bash
# 生成配置时指定 TCP
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u tcp://vpn.yourdomain.com
```

### 启用压缩

```bash
# 添加 -z 参数
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com -z
```

### 自定义网段

```bash
# 指定客户端网段
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com -s 10.8.0.0/24
```

### 更多高级配置

查看 [高级配置文档](docs/advanced-config.md)

## 🛠️ 运维管理

### 查看状态

```bash
# 容器状态
docker ps | grep openvpn

# 查看日志
docker logs openvpn-gateway
docker logs -f openvpn-gateway  # 实时查看

# 查看网关状态
docker exec openvpn-gateway ovpn_setup_gateway -s

# 查看站点状态
docker exec openvpn-gateway ovpn_list_sites
```

### 重启服务

```bash
docker restart openvpn-gateway
```

### 停止服务

```bash
docker-compose -f docker-compose-webui.yml down
```

### 更新镜像

```bash
# 1. 备份配置
docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar czf /backup/backup.tar.gz /etc/openvpn

# 2. 拉取最新代码
git pull

# 3. 重新构建
bash scripts/build-gateway.sh

# 4. 重启
docker-compose -f docker-compose-webui.yml down
docker-compose -f docker-compose-webui.yml up -d
```

## 💡 使用技巧

### 1. 证书管理

**生成客户端**（Web UI）:
- 客户端管理 → 输入名称 → 生成 → 下载

**吊销客户端**:
- 客户端管理 → 找到客户端 → 点击吊销

### 2. 站点管理（网关模式）

**添加站点的关键**:
- 远程网段必须填写正确（如 `172.16.0.0/16`）
- 证书配置是必需的（直接粘贴 .ovpn 内容）
- 添加后需要重启服务

**站点证书配置步骤**:
1. 从远程云平台获取 `.ovpn` 文件
2. Web UI 中点击"配置证书"
3. 复制 `.ovpn` 全部内容
4. 粘贴并保存
5. 重启服务

### 3. 模式切换

**何时使用普通模式**:
- 简单的远程访问
- 单一网络环境
- 资源有限的服务器

**何时使用网关模式**:
- 多云环境
- 需要打通多个 VPN
- 有充足的服务器资源

**切换方法**:
- Web UI: 模式设置 → 选择 → 保存 → 重启
- 命令行: `ovpn_set_mode gateway` → 重启

### 4. 性能优化

**服务器配置建议**:
- 最小: 1 核 2GB（< 10 用户）
- 推荐: 2 核 4GB（10-50 用户）
- 高负载: 4 核 8GB（50+ 用户或网关模式）

**网络优化**:
- 调整 MTU: `ovpn_genconfig -u ... -m 1400`
- 启用压缩: `ovpn_genconfig -u ... -z`
- 使用 TCP（高延迟网络）

## 🔒 安全建议

### 必做

1. ✅ 修改 Web UI 默认密码
2. ✅ 使用强 CA 密码
3. ✅ 定期备份配置
4. ✅ 开放必要端口（1194, 8080）

### 推荐

1. 🔒 配置 HTTPS（Nginx 反向代理）
2. 🔒 限制 Web UI 访问 IP
3. 🔒 启用 LDAP 认证
4. 🔒 使用证书 + 密码（双因素）
5. 🔒 定期检查日志
6. 🔒 及时更新镜像

## 💻 系统要求

- **操作系统**: Linux（Ubuntu 20.04+/CentOS 7+）
- **Docker**: 19.03+
- **Docker Compose**: 1.25+
- **内存**: 最少 2GB，推荐 4GB
- **CPU**: 最少 1 核，推荐 2 核
- **带宽**: 最少 10Mbps

## 📱 客户端支持

- ✅ Windows: OpenVPN GUI
- ✅ macOS: Tunnelblick, OpenVPN Connect
- ✅ Linux: OpenVPN 命令行
- ✅ Android: OpenVPN Connect
- ✅ iOS: OpenVPN Connect

## 🎓 学习路径

### 第一天: 基础部署
1. 按照"3 分钟快速开始"部署
2. 访问 Web UI，熟悉界面
3. 生成一个测试客户端
4. 客户端连接测试

### 第二天: 进阶功能
1. 配置 LDAP 认证（如果需要）
2. 尝试切换运行模式
3. 理解两种模式的区别

### 第三天: 多云网络（如果需要）
1. 切换到网关模式
2. 添加第一个远程站点
3. 配置站点证书
4. 测试访问远程网段

## 🤝 获取帮助

- 📖 **详细文档**: [docs/advanced-config.md](docs/advanced-config.md)
- 💬 **提交 Issue**: [GitHub Issues](https://github.com/ggfgmax/docker-openvpn-gateway/issues)
- 📧 **问题反馈**: 在 GitHub 上提交 Issue

## 🌟 功能对比

| 功能 | 原版 docker-openvpn | 本项目 |
|------|-------------------|--------|
| 标准 VPN 功能 | ✅ | ✅ |
| Web 管理界面 | ❌ | ✅ |
| 证书一键配置 | ❌ | ✅ |
| 多云网络打通 | ❌ | ✅ |
| LDAP/AD 认证 | ❌ | ✅ |
| 模式切换 | ❌ | ✅ |
| 中文文档 | ❌ | ✅ |
| 小白友好 | ❌ | ✅ |

## 📜 更新日志

查看完整更新日志: [CHANGELOG.md](CHANGELOG.md)

### v2.0.0 (2024-12-19)

**新增**:
- ✨ Web 管理界面
- ✨ 多云网络主入口网关
- ✨ LDAP/AD 认证支持
- ✨ 运行模式切换
- ✨ 证书自动配置
- ✨ 完整中文文档

**改进**:
- 🔧 目录结构重组
- 🔧 Dockerfile 优化
- 🔧 用户体验提升

## 🙏 致谢

- 基于 [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn)
- 感谢所有贡献者

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🚀 立即开始

```bash
git clone https://github.com/ggfgmax/docker-openvpn-gateway.git
cd docker-openvpn-gateway
bash scripts/build-gateway.sh
```

**⭐ 觉得不错？给个 Star！**

---

**有问题？** 查看上面的"常见问题"部分或提交 [Issue](https://github.com/ggfgmax/docker-openvpn-gateway/issues)
