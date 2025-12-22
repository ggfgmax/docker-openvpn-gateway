# OpenVPN 多云网络主入口网关 🚀

一个增强版的 Docker OpenVPN，支持 **Web 管理界面**、**多云网络打通**、**LDAP 认证**。  
让小白也能轻松配置和管理 VPN！

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Version](https://img.shields.io/badge/version-2.0.0-brightgreen.svg)](CHANGELOG.md)

## ✨ v2.0 核心特性

### 🎯 Web 管理界面
- **零命令行操作** - 所有配置在浏览器中完成
- **一键添加站点** - 30 秒添加 Site-to-Site VPN
- **自动提取配置** - 从 .ovpn 文件自动提取服务器、端口、协议、证书
- **证书过期监控** - 自动显示证书过期时间和剩余天数（颜色预警）
- **实时状态监控** - 自动刷新运行状态

### 🌐 多云网络打通
- **一个 VPN 访问所有云** - 华为云、AWS、GCP、阿里云等
- **自动路由管理** - 自动配置和推送路由
- **自动重启恢复** - 重启后自动连接所有站点
- **网段智能检测** - 避免 IP 冲突

### 🔓 开箱即用
- **默认无密码 CA** - 初始化时所有提示直接回车
- **自动确认操作** - expect 自动输入 "yes"
- **自动创建配置** - vars 文件自动生成
- **环境变量生效** - GATEWAY_MODE 自动应用

## ⚡ 5 分钟快速开始

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/docker-openvpn-gateway.git
cd docker-openvpn-gateway

# 2. 启动容器
docker-compose -f docker-compose-webui.yml up -d

# 3. 初始化（在容器内执行）
docker exec -it openvpn-gateway ovpn_genconfig -u udp://你的服务器IP -s 10.8.0.0/24
docker exec -it openvpn-gateway ovpn_initpki
# 提示：所有提示直接回车即可（默认无密码 CA）

# 4. 重启服务
docker restart openvpn-gateway

# 5. 访问 Web 界面
# 浏览器打开: http://服务器IP:8080
# 默认用户名: admin  默认密码: openvpn
```

**就这么简单！** 🎉

## 🎨 Web UI 功能

### 📊 系统概览
- 实时显示：运行模式、LDAP 状态、站点数量、客户端数量
- 自动刷新（每 30 秒）

### 🌐 站点管理（网关模式）
**一键添加站点**（只需 3 步）：
1. 填写站点名称（如：`gcp`）
2. 填写远程 VPC 网段（如：`10.80.0.0/16`）
3. 粘贴 .ovpn 文件完整内容
4. 点击"一键添加" → 完成！

**系统自动**：
- ✅ 提取服务器地址、端口、协议
- ✅ 提取 CA 证书、客户端证书、密钥
- ✅ 配置路由和连接
- ✅ 更新路由推送配置

**站点管理功能**：
- 查看所有站点状态
- 证书过期时间监控（绿/橙/红色预警）
- 更新站点证书
- 删除站点（自动清理）

### 👥 客户端管理
- **生成客户端证书**：输入名称 → 生成 → 下载 .ovpn
- **证书过期监控**：显示过期日期和剩余天数（颜色预警）
- **吊销证书**：一键吊销（自动更新 CRL）
- **下载配置**：一键下载 .ovpn 文件

### ⚙️ 模式设置
- **普通 VPN 模式** - 标准远程访问
- **网关模式** - 多云网络打通
- Web UI 一键切换

### 🔑 LDAP 配置
- 图形化配置 OpenLDAP / Active Directory
- 内置配置模板（OpenLDAP 和 AD）
- 一键填充常用配置

## 📖 使用场景

### 场景 1: 多云网络打通（推荐）

**需求**: 统一访问华为云、AWS、GCP 等多个云平台

**步骤**：

1. **初始化网关**（使用不冲突的客户端网段）
```bash
docker exec -it openvpn-gateway ovpn_genconfig -u udp://服务器IP -s 10.8.0.0/24
docker exec -it openvpn-gateway ovpn_initpki
docker restart openvpn-gateway
```

2. **切换到网关模式**
- Web UI → 模式设置 → 网关模式 → 保存
- 重启：`docker restart openvpn-gateway`

3. **添加 GCP 站点**（示例）
```
Web UI → 站点管理：
• 站点名称: gcp
• 远程VPC网段: 10.80.0.0/16
• .ovpn配置: [粘贴GCP提供的完整.ovpn内容]
点击"一键添加站点"
```

4. **添加更多站点**（AWS、阿里云等）
- 重复上面的步骤
- 每个站点用不同的名称

5. **重启服务**
```bash
docker restart openvpn-gateway
```

6. **生成客户端证书并连接**
```
Web UI → 客户端管理 → 生成证书 → 下载 → 连接
```

**完成后**：
- ✅ 客户端连接一次网关
- ✅ 自动访问所有云平台内网
- ✅ 无需切换 VPN

**网络架构**：
```
你的电脑 (10.8.0.6)
    ↓ 连接网关 VPN
网关 (10.8.0.1)
    ├─→ GCP VPN → 10.80.0.0/16
    ├─→ AWS VPN → 10.0.0.0/16
    └─→ 阿里云 VPN → 172.16.0.0/16
```

### 场景 2: 企业内网访问（普通 VPN）

**需求**: 员工远程访问公司内网

**步骤**：
1. 按照快速开始初始化
2. Web UI → 客户端管理 → 生成证书 → 下载
3. 发送给员工 → 员工连接

**可选**: 配置 LDAP，员工用 AD 账户登录

## 🔧 环境变量配置

```yaml
environment:
  # 运行模式（0=普通VPN, 1=网关模式）
  - GATEWAY_MODE=1
  
  # LDAP 认证（0=禁用, 1=启用）
  - LDAP_ENABLED=0
  
  # Web UI 认证（⚠️ 生产环境务必修改密码）
  - WEBUI_USERNAME=admin
  - WEBUI_PASSWORD=openvpn
  
  # CA 密码（可选，默认无密码）
  - CA_PASSWORD=
```

## 🆘 常见问题

### Q1: 认证窗口不弹出？
**已修复**！现在会自动弹出认证窗口。

### Q2: 生成客户端证书失败？
**已修复**！默认使用无密码 CA，expect 自动确认。

### Q3: 添加/删除站点后需要重启吗？
**是的**！OpenVPN 在启动时加载配置。
```bash
docker restart openvpn-gateway
# 客户端也需要重新连接
```

### Q4: 客户端无法访问远程站点内网？
**检查清单**：
1. 网关能否 ping 通远程内网？ → `docker exec openvpn-gateway ping 10.80.0.2`
2. 是否重启了网关？
3. 客户端是否重新连接了？
4. **是否有网段冲突**？

**网段冲突**（重要！）：
```bash
# 查看网关客户端网段
docker exec openvpn-gateway grep "^server" /etc/openvpn/openvpn.conf

# 查看站点 VPN 网段
docker exec openvpn-gateway ip addr show | grep -A 2 tun

# 如果网段相同（如都是 192.168.255.0/24），需要修改：
docker exec -it openvpn-gateway ovpn_genconfig -u udp://服务器IP -s 10.8.0.0/24
# 然后重新初始化
```

### Q5: 吊销证书后客户端还能连接？
**需要重启服务器**才能加载新的 CRL（证书吊销列表）：
```bash
docker restart openvpn-gateway
# 客户端重新连接时会被拒绝
```

### Q6: 如何查看日志？
```bash
# 容器日志
docker logs -f openvpn-gateway

# OpenVPN 主日志
docker exec openvpn-gateway tail -f /var/log/openvpn.log

# 站点连接日志
docker exec openvpn-gateway tail -f /var/log/openvpn-gcp.log

# 查看所有错误
docker logs openvpn-gateway 2>&1 | grep -i error
```

### Q7: 站点连接 TLS 握手失败？
**可能原因**：
1. **证书/密钥过期或更新** - 从远程重新下载 .ovpn 文件
2. **tls-auth 密钥不匹配** - 更新证书
3. **UDP 连接问题** - 尝试使用 TCP 协议
4. **防火墙阻止** - 检查双方防火墙规则

**解决**：
- 从远程 VPN 获取最新的 .ovpn 文件
- Web UI → 站点管理 → 更新证书
- 重启网关

### Q8: 使用 TCP 还是 UDP 协议？
**UDP**：
- ✅ 性能更好，延迟更低
- ❌ 在某些网络环境下可能不稳定

**TCP**：
- ✅ 更稳定，穿透性更好
- ✅ 适合 NAT/防火墙复杂的环境
- ❌ 性能略低

**建议**：先尝试 UDP，如果不稳定再改用 TCP。

### Q9: VPN 连接后要等多久才能 ping 通？
**正常需要 1-2 分钟**：
- 0-10秒：TLS 握手
- 10-30秒：推送配置、建立数据通道
- 30-60秒：路由生效、ARP 解析
- 60-120秒：完全稳定 ✅

**首次连接或重新连接时，前几次 ping 可能超时，这是正常的！**

## 🔒 安全建议

### 必做（生产环境）
1. ✅ **修改 Web UI 默认密码**
   ```yaml
   environment:
     - WEBUI_PASSWORD=你的强密码
   ```

2. ✅ **选择合适的客户端网段**
   ```bash
   # 推荐：10.8.0.0/24 或 172.31.0.0/24
   # 避免：192.168.x.0/24（容易与远程站点冲突）
   ovpn_genconfig -u udp://服务器IP -s 10.8.0.0/24
   ```

3. ✅ **开放必要端口**
   ```bash
   # 防火墙规则
   sudo ufw allow 1194/udp  # OpenVPN
   sudo ufw allow 8080/tcp  # Web UI
   ```

4. ✅ **定期备份**
   ```bash
   docker exec openvpn-gateway tar czf /tmp/backup.tar.gz /etc/openvpn
   docker cp openvpn-gateway:/tmp/backup.tar.gz ./openvpn-backup-$(date +%Y%m%d).tar.gz
   ```

### 推荐（提高安全性）
1. 🔒 使用 HTTPS（Nginx 反向代理）
2. 🔒 限制 Web UI 访问 IP
3. 🔒 启用 LDAP/AD 认证
4. 🔒 定期检查日志和证书过期时间

## 🛠️ 运维管理

### 查看状态
```bash
# 容器状态
docker ps | grep openvpn

# 查看日志
docker logs -f openvpn-gateway

# 查看站点连接
docker exec openvpn-gateway ps aux | grep openvpn

# 查看路由
docker exec openvpn-gateway ip route

# 查看已连接客户端
docker exec openvpn-gateway cat /tmp/openvpn-status.log
```

### 重启服务
```bash
docker restart openvpn-gateway
```

### 停止服务
```bash
docker-compose -f docker-compose-webui.yml down
```

### 备份和恢复
```bash
# 备份
docker exec openvpn-gateway tar czf /tmp/backup.tar.gz /etc/openvpn
docker cp openvpn-gateway:/tmp/backup.tar.gz ./backup.tar.gz

# 恢复
docker cp ./backup.tar.gz openvpn-gateway:/tmp/
docker exec openvpn-gateway tar xzf /tmp/backup.tar.gz -C /
docker restart openvpn-gateway
```

## 🔧 高级配置

### 使用 TCP 协议
```bash
# 初始化时指定 TCP
ovpn_genconfig -u tcp://你的服务器IP -s 10.8.0.0/24
```

### 自定义客户端网段
```bash
# 指定不冲突的网段
ovpn_genconfig -u udp://你的服务器IP -s 10.8.0.0/24
# 或
ovpn_genconfig -u udp://你的服务器IP -s 172.31.0.0/24
```

### 启用 LDAP 认证
```
Web UI → LDAP 配置：
1. 选择模板（OpenLDAP 或 AD）
2. 填写服务器地址和 Base DN
3. 配置绑定账户
4. 保存并重启
```

### 使用密码保护的 CA
```bash
# 初始化时使用 withpass
docker exec -it openvpn-gateway ovpn_initpki withpass

# 设置环境变量
echo "CA_PASSWORD=你的密码" >> .env

# 重新构建
docker-compose -f docker-compose-webui.yml build
docker restart openvpn-gateway
```

## 📋 故障排查

### 问题：站点连接失败（TLS 握手失败）

**症状**：
```
TLS Error: TLS key negotiation failed to occur within 60 seconds
TLS Error: TLS handshake failed
```

**可能原因**：
1. **证书/密钥过期或更新** - 远程 VPN 可能更新了证书
2. **tls-auth 密钥不匹配** - 远程日志显示 "HMAC authentication failed"
3. **UDP 连接问题** - 网络环境不适合 UDP
4. **防火墙阻止** - 双方防火墙检查

**解决方法**：
```bash
# 1. 从远程 VPN 重新下载最新的 .ovpn 文件
# 2. Web UI → 站点管理 → 更新证书
# 3. 粘贴新的 .ovpn 内容 → 保存
# 4. 重启：docker restart openvpn-gateway
# 5. 如果还是失败，尝试使用 TCP 协议
```

### 问题：客户端无法访问远程内网

**检查网段冲突**：
```bash
# 1. 查看网关客户端网段
docker exec openvpn-gateway grep "^server" /etc/openvpn/openvpn.conf
# 输出如：server 192.168.255.0 255.255.255.0

# 2. 查看站点 VPN 网段
docker exec openvpn-gateway ip addr show | grep -A 2 tun

# 3. 如果网段相同 → 有冲突！
```

**解决冲突**：
```bash
# 使用不冲突的网段重新初始化
# 1. 备份 PKI 和站点配置
# 2. 删除 openvpn.conf 和 ovpn_env.sh
# 3. 重新 genconfig 使用 10.8.0.0/24
# 4. 恢复 PKI 和站点
# 5. 重启并重新生成客户端证书
```

### 问题：网关能通，客户端不通

**原因**：路由没有推送或客户端没有重新连接

**解决**：
```bash
# 1. 检查 PUSH_REPLY
docker logs openvpn-gateway | grep "PUSH_REPLY" | tail -1
# 应该包含：route 10.80.0.0 ...

# 2. 检查主配置
docker exec openvpn-gateway grep "site-routes" /etc/openvpn/openvpn.conf
# 应该有：config /etc/openvpn/site-routes.conf

# 3. 如果缺失，添加它
echo -e "\n# Site-to-Site VPN 路由配置\nconfig /etc/openvpn/site-routes.conf" >> data/openvpn.conf

# 4. 重启
docker restart openvpn-gateway

# 5. 客户端重新连接
```

### 问题：站点自动启动失败

**症状**：
```
已启动 0 个站点连接
或
站点 xxx 已经在运行 (PID: xx)（但实际没运行）
```

**原因**：PID 文件残留（容器重启后 PID 可能被其他进程复用）

**解决**：
```bash
# 清理 PID 文件
docker exec openvpn-gateway rm -f /etc/openvpn/site-pids/*.pid

# 重启
docker restart openvpn-gateway
```

### 问题：日志太多（404 等）

**已修复**！系统自动过滤无用日志（404、健康检查等）。

## 💻 系统要求

- **操作系统**: Linux（Ubuntu 20.04+ / CentOS 7+ / Debian 10+）
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

## 🌟 功能对比

| 功能 | 原版 docker-openvpn | 本项目 v2.0 |
|------|-------------------|-----------|
| 标准 VPN 功能 | ✅ | ✅ |
| Web 管理界面 | ❌ | ✅ |
| 一键添加站点 | ❌ | ✅ ⭐ |
| 自动提取配置 | ❌ | ✅ ⭐ |
| 多云网络打通 | ❌ | ✅ |
| LDAP/AD 认证 | ❌ | ✅ |
| 默认 nopass CA | ❌ | ✅ ⭐ |
| 路由自动管理 | ❌ | ✅ ⭐ |
| 证书过期监控 | ❌ | ✅ ⭐ |
| 网段冲突检测 | ❌ | ✅ |
| 完整中文文档 | ❌ | ✅ |
| 小白友好度 | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 📜 更新日志

### v2.0.0 (2025-12-22) 🎉

**重大功能**：
- ✨ Web UI v2.0 - 一键添加站点
- ✨ 多云网络网关 - Site-to-Site VPN 自动管理
- ✨ 证书过期监控 - 自动显示并颜色预警
- ✨ LDAP/AD 认证 - 企业级身份验证

**核心改进**：
- 🔧 一键添加站点（3 字段，1 步完成）
- 🔧 路由自动管理（CIDR 转换，自动推送）
- 🔧 认证体验（自动弹出窗口）
- 🔧 默认 nopass CA（开箱即用）
- 🔧 日志优化（过滤无用信息）
- 🔧 OpenVPN 2.6+ 兼容

**Bug 修复**：
- 🐛 修复认证窗口不弹出
- 🐛 修复客户端证书生成失败
- 🐛 修复 GATEWAY_MODE 环境变量不生效
- 🐛 修复路由格式错误（CIDR → IP+掩码）
- 🐛 修复 push 命令引号问题
- 🐛 修复站点 PID 检查 Bug
- 🐛 修复吊销证书交互问题
- 🐛 识别并文档化网段冲突问题

**测试验证**：
- ✅ GCP Site-to-Site VPN 连接成功（TCP 协议）
- ✅ 客户端可访问 GCP 内网
- ✅ 解决网段冲突问题
- ✅ 所有功能完整可用

## 🙏 致谢

- 基于 [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn)
- 感谢所有测试和反馈的用户

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🚀 立即开始

```bash
git clone https://github.com/your-repo/docker-openvpn-gateway.git
cd docker-openvpn-gateway
docker-compose -f docker-compose-webui.yml up -d
docker exec -it openvpn-gateway ovpn_genconfig -u udp://你的IP -s 10.8.0.0/24
docker exec -it openvpn-gateway ovpn_initpki
docker restart openvpn-gateway
```

**Web UI**: `http://你的服务器IP:8080`  
**默认账号**: admin / openvpn

---

**有问题？** 参考上面的"常见问题"部分
