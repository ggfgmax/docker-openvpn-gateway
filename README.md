# OpenVPN 多云网络主入口网关 🚀

一个增强版的 Docker OpenVPN，支持 **Web 管理界面**、**多云网络打通**、**LDAP 认证**。  
让小白也能轻松配置和管理 VPN！

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](CHANGELOG.md)

## ✨ v2.0 核心亮点

### 🎯 一键添加站点（重大改进！）
- **之前**：填 7 个字段，分 2 步操作，信息重复
- **现在**：填 3 个字段，1 步完成，自动提取配置
- **效果**：添加站点从 5 分钟缩短到 30 秒！

### 🔓 开箱即用
- **默认无密码 CA** - 所有提示直接回车
- **自动确认生成证书** - 无需交互输入 "yes"
- **自动创建配置文件** - vars 文件自动创建
- **自动应用环境变量** - GATEWAY_MODE 自动生效

### 🛠️ 完善的错误处理
- 认证窗口自动弹出
- 详细的错误提示和解决方案
- 完整的日志记录
- 路由格式自动转换

### 📚 完整的文档体系
- 10+ 个详细指南
- 涵盖快速开始、配置、排查等所有场景
- 中文文档，小白友好

## 🌟 为什么选择这个项目？

### 痛点
- ❌ 访问华为云要连华为云 VPN
- ❌ 访问 AWS 要断开华为云，连 AWS VPN  
- ❌ 访问 GCP 要再切换一次...
- ❌ 配置复杂，命令行操作困难
- ❌ 证书配置繁琐，容易出错

### 解决方案
- ✅ **一个 VPN 访问所有云平台**
- ✅ **Web 界面配置，零命令行**
- ✅ **一键添加站点，30 秒完成**
- ✅ **开箱即用，小白也能用**
- ✅ **自动化管理，减少错误**

## ⚡ 5 分钟快速开始

```bash
# 1. 克隆项目
git clone https://github.com/ggfgmax/docker-openvpn-gateway.git
cd docker-openvpn-gateway

# 2. 启动容器
docker-compose -f docker-compose-webui.yml up -d

# 3. 初始化（在容器内执行，替换为你的服务器 IP）
docker exec -it openvpn-gateway ovpn_genconfig -u udp://你的服务器IP
docker exec -it openvpn-gateway ovpn_initpki
# 所有提示直接回车即可（默认无密码 CA）

# 4. 重启服务
docker restart openvpn-gateway

# 5. 访问 Web 界面
# 浏览器打开: http://服务器IP:8080
# 默认用户名: admin  默认密码: openvpn
```

**就这么简单！** 🎉

> 💡 **详细步骤**: 参考 [快速启动指南](docs/guides/QUICK_START.md)  
> 📚 **所有文档**: 参考 [文档索引](docs/INDEX.md)

## 🎯 v2.0 新功能速览

### 一键添加站点（革命性改进！）

**旧版流程** ❌:
```
1. 填写 7 个字段（名称、服务器、端口、网段、协议等）
2. 点击"添加站点"
3. 找到站点，点击"配置证书"  
4. 粘贴 .ovpn 文件内容
5. 保存证书
   ⚠️ 问题：信息重复，可能不一致，步骤繁琐
```

**新版流程** ✅:
```
1. 填写 2 个字段：
   • 站点名称: gcp
   • 远程VPC网段: 10.80.0.0/20
2. 粘贴 .ovpn 文件完整内容
3. 点击"一键添加站点"
   ✅ 自动提取：服务器地址、端口、协议、证书
   ✅ 自动配置：路由、证书、连接
   ✅ 30 秒完成！
```

### 默认无密码 CA（开箱即用）

**旧版** ❌:
```
运行 ovpn_initpki
→ 输入 CA 密码
→ 记住密码
→ 配置 CA_PASSWORD 环境变量
→ 重新构建镜像
→ 重启容器
   ⚠️ 问题：步骤多，容易出错
```

**新版** ✅:
```
运行 ovpn_initpki
→ 所有提示直接回车
→ 完成！
   ✅ Web UI 可直接生成客户端证书
```

### 智能配置管理

- ✅ **自动创建 vars 文件** - 无需手动准备
- ✅ **自动确认证书** - expect 自动输入 "yes"
- ✅ **自动应用环境变量** - GATEWAY_MODE 自动生效
- ✅ **自动转换路由格式** - CIDR → IP+掩码
- ✅ **自动包含路由配置** - site-routes.conf 总是包含

## 🎨 Web 管理界面 (v2.0)

**所有操作都可以在浏览器中完成，零命令行！**

### 核心功能

#### 📊 系统概览
- 实时显示运行模式（普通VPN / 网关模式）
- LDAP 认证状态
- 站点和客户端数量统计
- 自动刷新

#### ⚙️ 模式设置
- **普通 VPN 模式** - 标准远程访问（适合企业内网）
- **网关模式** - 多云网络打通（适合混合云架构）
- Web UI 一键切换，自动应用环境变量

#### 🌐 站点管理（网关模式）⭐ 重点功能
**一键添加站点**（v2.0 全新体验）：
- ✅ **只需填写 2 项**：站点名称 + 远程VPC网段
- ✅ **粘贴 .ovpn 内容**：系统自动提取服务器地址、端口、协议、证书
- ✅ **一步完成**：无需分步操作，无需重复输入
- ✅ **字段验证**：自动验证格式，防止错误
- ✅ **详细说明**：清晰说明每个字段的含义和示例

**站点管理功能**：
- 查看所有已配置站点
- 证书配置状态（绿色✅/红色❌）
- 更新站点证书
- 删除站点（自动更新路由）

#### 👥 客户端管理
- **生成客户端证书**：输入名称，一键生成（自动确认）
- **下载配置文件**：一键下载 .ovpn 文件
- **吊销证书**：撤销客户端访问权限
- **自动创建 vars 文件**：无需手动准备

#### 🔑 LDAP 配置
- 图形化配置 OpenLDAP / Active Directory
- 内置配置模板（一键填充）
- 实时保存和应用

## 📖 使用指南

### 场景 1: 企业内网访问（普通 VPN）

**需求**: 员工远程访问公司内网

**操作**:
1. Web UI → 客户端管理
2. 输入员工姓名 → 生成客户端证书
3. 下载 .ovpn 文件 → 发送给员工
4. 员工导入配置连接

**可选**: 配置 LDAP，员工用 AD 账户登录

---

### 场景 2: 多云网络打通（网关模式）⭐ **推荐**

**需求**: 在华为云、AWS、GCP 都有资源，需要统一访问

#### 🚀 v2.0 简化流程（只需 3 步）

**1. 切换到网关模式**
```
Web UI → 模式设置 → 选择"网关模式" → 保存 → 重启服务
```

**2. 添加云平台站点**（以 GCP 为例）
```
Web UI → 站点管理 → 填写信息：

• 站点名称: gcp
• 远程VPC网段: 10.80.0.0/20  ← 这是 GCP 的 VPC 内网网段
• .ovpn 配置文件内容: [粘贴完整的 .ovpn 文件内容]

点击"一键添加站点" → 完成！
```

**系统自动提取**：
- ✅ VPN 服务器地址和端口
- ✅ 协议（UDP/TCP）
- ✅ CA 证书、客户端证书、密钥
- ✅ 自动配置路由

**3. 生成客户端并连接**
```
Web UI → 客户端管理 → 生成证书 → 下载 → 连接
```

**完成后**：
- ✅ 客户端连接一次 VPN 网关
- ✅ 自动可访问所有云平台内网
- ✅ 无需切换 VPN，无缝访问

**网络架构**:
```
你的电脑 (一次连接)
    ↓ VPN 网关
    ├─→ 华为云 VPN → 172.16.0.0/16
    ├─→ AWS VPN → 10.0.0.0/16  
    └─→ GCP VPN → 10.80.0.0/20
```

> 📖 **详细指南**: [站点证书配置完整指南](docs/guides/SITE_CERTIFICATE_GUIDE.md)

---

### 场景 3: LDAP/AD 认证

**需求**: 使用企业 AD 账户登录 VPN

**操作**:
1. Web UI → LDAP 配置 → 选择模板（AD 或 OpenLDAP）
2. 填写服务器地址、Base DN、绑定账户
3. 保存并重启服务

**客户端使用**: 连接时输入 AD 用户名和密码

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

### Q: 认证窗口不弹出？
已修复！现在会自动弹出。如遇问题查看：[认证问题修复](docs/troubleshooting/FIX_AUTHENTICATION.md)

### Q: 生成客户端证书失败？
已优化！默认使用无密码 CA，开箱即用。详见：[证书生成修复](docs/troubleshooting/FIX_CLIENT_CERT_GENERATION.md)

### Q: GATEWAY_MODE 环境变量不生效？
已修复！现在会自动读取并应用。详见：[网关模式修复](docs/troubleshooting/FIX_GATEWAY_MODE.md)

### Q: 客户端无法访问远程站点内网？
参考完整排查指南：[连通性排查](docs/troubleshooting/TROUBLESHOOTING_CONNECTIVITY.md)

### Q: 如何查看日志？
```bash
# Web UI 和容器日志
docker logs -f openvpn-gateway

# OpenVPN 主日志
docker exec openvpn-gateway tail -f /var/log/openvpn.log

# 站点连接日志
docker exec openvpn-gateway tail -f /var/log/openvpn-gcp.log
```
详见：[日志调试指南](docs/guides/LOGGING_GUIDE.md)

### Q: 如何删除站点？
Web UI → 站点管理 → 删除按钮 → 重启服务
详见：[删除站点行为说明](docs/guides/DELETE_SITE_BEHAVIOR.md)

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

## 🔧 配置说明

### 环境变量

在 `.env` 文件或 `docker-compose-webui.yml` 中配置：

```yaml
environment:
  # 运行模式（0=普通VPN, 1=网关模式）
  - GATEWAY_MODE=1  # 默认网关模式
  
  # LDAP 认证（0=禁用, 1=启用）
  - LDAP_ENABLED=0
  
  # Web UI 认证（重要：请修改默认密码！）
  - WEBUI_USERNAME=admin
  - WEBUI_PASSWORD=openvpn  # ⚠️ 生产环境务必修改
  
  # CA 密码（可选，仅当使用密码保护的 CA 时需要）
  - CA_PASSWORD=  # 默认无密码 CA，无需设置
  
  # 调试模式
  - DEBUG=0
```

**重要**：
- ⚠️ 生产环境必须修改 `WEBUI_PASSWORD`
- ✅ 默认使用无密码 CA（开箱即用）
- ✅ 如需密码保护 CA：`ovpn_initpki withpass` + 设置 `CA_PASSWORD`

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

## 📚 文档导航

### 🚀 快速开始
- **[快速启动指南](docs/guides/QUICK_START.md)** - 从零到部署的完整步骤
- **[站点证书配置](docs/guides/SITE_CERTIFICATE_GUIDE.md)** - Site-to-Site VPN 详细配置
- **[日志调试指南](docs/guides/LOGGING_GUIDE.md)** - 日志位置和调试技巧

### 🔧 问题排查
- **[认证问题修复](docs/troubleshooting/FIX_AUTHENTICATION.md)** - 认证窗口不弹出等
- **[证书生成修复](docs/troubleshooting/FIX_CLIENT_CERT_GENERATION.md)** - 生成客户端证书失败
- **[网关模式修复](docs/troubleshooting/FIX_GATEWAY_MODE.md)** - 环境变量不生效
- **[连通性排查](docs/troubleshooting/TROUBLESHOOTING_CONNECTIVITY.md)** - 无法访问远程内网

### 📖 更多文档
- **[Web UI v2.0 改进](docs/WEBUI_V2_IMPROVEMENTS.md)** - 最新功能和优化说明
- **[默认 nopass 变更](docs/CHANGELOG_NOPASS_DEFAULT.md)** - CA 密码策略变更
- **[删除站点行为](docs/guides/DELETE_SITE_BEHAVIOR.md)** - 删除站点的完整流程
- **[高级配置](docs/advanced-config.md)** - 高级功能和参数

## 🤝 获取帮助

- 💬 **提交 Issue**: [GitHub Issues](https://github.com/ggfgmax/docker-openvpn-gateway/issues)
- 📖 **查看文档**: 参考上面的文档导航
- 🔍 **搜索问题**: 先查看 [连通性排查指南](docs/troubleshooting/TROUBLESHOOTING_CONNECTIVITY.md)

## 🌟 功能对比

| 功能 | 原版 docker-openvpn | 本项目 v1.0 | 本项目 v2.0 |
|------|-------------------|-----------|-----------|
| 标准 VPN 功能 | ✅ | ✅ | ✅ |
| Web 管理界面 | ❌ | ✅ | ✅ |
| 一键添加站点 | ❌ | ❌ | ✅ ⭐ |
| 自动提取配置 | ❌ | ❌ | ✅ ⭐ |
| 多云网络打通 | ❌ | ✅ | ✅ |
| LDAP/AD 认证 | ❌ | ✅ | ✅ |
| 默认 nopass CA | ❌ | ❌ | ✅ ⭐ |
| 路由自动管理 | ❌ | 部分 | ✅ ⭐ |
| 详细错误提示 | ❌ | ❌ | ✅ |
| 完整中文文档 | ❌ | 基础 | ✅ 10+篇 |
| 小白友好度 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 📜 更新日志

查看完整更新日志: [CHANGELOG.md](CHANGELOG.md)

### v2.0.0 (2025-12-19) 🎉

**重大功能**:
- ✨ **Web UI v2.0** - 一键添加站点，自动提取配置
- ✨ **多云网络网关** - Site-to-Site VPN 自动管理
- ✨ **LDAP/AD 认证** - 企业级身份验证
- ✨ **运行模式切换** - 普通VPN / 网关模式
- ✨ **完整中文文档** - 10+ 个详细指南

**核心改进**:
- 🔧 **一键添加站点** - 从 7 个字段简化到 3 个，从 2 步简化到 1 步
- 🔧 **路由自动管理** - CIDR 自动转换，自动推送给客户端
- 🔧 **认证体验** - 自动弹出认证窗口，支持 CA 密码
- 🔧 **默认 nopass CA** - 开箱即用，无需密码
- 🔧 **日志优化** - 过滤无用日志，保留关键信息
- 🔧 **OpenVPN 2.6+** - 兼容最新版本语法

**Bug 修复**:
- 🐛 修复认证窗口不弹出
- 🐛 修复客户端证书生成失败
- 🐛 修复 GATEWAY_MODE 环境变量不生效
- 🐛 修复路由格式错误（CIDR → IP+掩码）
- 🐛 修复 push 命令引号问题
- 🐛 修复 .info 文件格式错误
- 🐛 修复路由冲突问题

**测试验证**:
- ✅ GCP Site-to-Site VPN 连接成功
- ✅ 客户端可访问 GCP 内网 10.80.0.0/20
- ✅ 路由自动推送正常
- ✅ 所有功能完整可用

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
