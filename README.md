# OpenVPN 多云网络主入口网关 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![OpenVPN](https://img.shields.io/badge/OpenVPN-2.x-green.svg)](https://openvpn.net/)

> 基于 [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn) 增强版，支持多云网络打通、LDAP 认证和 Web 管理界面。

## ✨ 特色功能

### 🌐 多云网络主入口网关
- **一个 VPN 访问所有云平台** - 打通华为云、AWS、GCP 等多个云平台内网
- **Site-to-Site VPN** - 自动管理到各云平台的 VPN 隧道连接
- **智能路由** - 自动配置和推送路由规则
- **流量转发** - 自动配置 iptables 规则

### 🔐 企业级认证
- **LDAP/AD 支持** - 集成企业 LDAP 或 Active Directory
- **双因素认证** - 支持证书 + 密码 / OTP
- **灵活认证** - 仅证书、仅 LDAP 或组合认证

### 🎛️ 灵活运行模式
- **普通 VPN 模式** - 标准的 OpenVPN 服务器
- **网关模式** - 多云网络主入口
- **一键切换** - 轻松切换运行模式

### 🌟 Web 管理界面 (NEW!)
- **零命令行操作** - 图形化配置和管理
- **实时监控** - 查看服务器、站点、客户端状态
- **适合小白** - 无需学习复杂命令
- **一键操作** - 证书生成、配置下载、模式切换

## 📸 界面预览

### Web 管理界面
```
┌─────────────────────────────────────────┐
│ 🔐 OpenVPN Web 管理界面                  │
│                                         │
│ 运行模式: 网关模式  LDAP: 已启用         │
│ 站点数: 3          客户端数: 5          │
└─────────────────────────────────────────┘
│ [📊 概览] [⚙️ 模式] [🔑 LDAP] [🌐 站点] [👥 客户端] │
```

### 架构示意图
```
你的电脑
    ↓ (连接一次)
主入口 VPN 网关
    ↓ (自动连接)
    ├─→ 华为云 VPN → 华为云内网 (172.16.0.0/16)
    ├─→ AWS VPN → AWS 内网 (10.0.0.0/16)
    └─→ GCP VPN → GCP 内网 (192.168.0.0/16)
```

## 🚀 快速开始

### 方式 1: Web 管理界面（推荐给小白）

```bash
# 1. 构建镜像
git clone https://github.com/ggfgmax/docker-openvpn-gateway.git
cd docker-openvpn-gateway
bash build-gateway.sh

# 2. 初始化
docker volume create openvpn-data
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki

# 3. 启动（包含 Web UI）
docker-compose -f docker-compose-webui.yml up -d

# 4. 访问 Web 界面
# 浏览器打开: http://服务器IP:8080
# 默认用户名: admin
# 默认密码: openvpn（⚠️ 请立即修改！）
```

**详细说明**: [Web UI 快速开始](WEBUI-QUICKSTART.md)

### 方式 2: 命令行方式（适合高级用户）

```bash
# 标准 OpenVPN 部署
OVPN_DATA="ovpn-data"
docker volume create --name $OVPN_DATA
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u udp://VPN.SERVERNAME.COM
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn ovpn_initpki
docker run -v $OVPN_DATA:/etc/openvpn -d -p 1194:1194/udp --cap-add=NET_ADMIN kylemanna/openvpn
```

**详细说明**: [中文完整指南](GETTING-STARTED-CN.md)

## 📚 文档

### 新手入门
- [Web 管理界面快速开始](WEBUI-QUICKSTART.md) ⭐ 推荐
- [中文快速开始指南](GETTING-STARTED-CN.md)
- [项目总结](SUMMARY.md)

### 功能文档
- [多云网络主入口网关配置](docs/multi-cloud-gateway.md)
- [LDAP/AD 认证配置](docs/ldap.md)
- [运行模式切换](docs/mode-switching.md)
- [Web UI 完整文档](docs/webui.md)

### 进阶文档
- [新功能说明](NEW-FEATURES.md)
- [更新日志](CHANGELOG-GATEWAY.md)
- [高级配置](docs/advanced.md)

## 🎯 使用场景

### 场景 1: 企业内部 VPN
```bash
# 使用 Web UI 或命令行快速部署
docker-compose -f docker-compose-webui.yml up -d
# 配置 LDAP 认证
# 生成客户端证书
```

**适用于**: 企业远程办公、内网访问

### 场景 2: 多云环境统一访问
```bash
# 切换到网关模式
# 添加华为云、AWS、GCP 站点
# 配置 Site-to-Site VPN
```

**适用于**: 混合云架构、多云环境

### 场景 3: 开发测试环境
```bash
# 连接不同的测试环境 VPN
# 开发人员一次连接访问所有环境
```

**适用于**: DevOps、测试团队

## 🔧 核心命令

### Web UI 操作（图形界面）
- 访问: `http://服务器IP:8080`
- 模式切换、LDAP 配置、站点管理、客户端管理

### 命令行操作

| 命令 | 说明 |
|------|------|
| `ovpn_set_mode` | 切换运行模式 |
| `ovpn_config_ldap` | 配置 LDAP 认证 |
| `ovpn_add_remote_site` | 添加远程站点 |
| `ovpn_list_sites` | 列出站点状态 |
| `ovpn_setup_gateway` | 初始化网关 |

完整命令列表: [README-MULTI-CLOUD.md](README-MULTI-CLOUD.md)

## 🌟 功能对比

| 功能 | 原版 | 本项目 |
|------|------|--------|
| 标准 VPN | ✅ | ✅ |
| 多云网络打通 | ❌ | ✅ |
| LDAP/AD 认证 | ❌ | ✅ |
| 运行模式切换 | ❌ | ✅ |
| Web 管理界面 | ❌ | ✅ |
| Site-to-Site VPN | ❌ | ✅ |

## 🔐 安全建议

- ✅ 修改 Web UI 默认密码
- ✅ 使用强 CA 密码
- ✅ 配置 HTTPS（生产环境）
- ✅ 限制 Web UI 访问 IP
- ✅ 启用 LDAP 认证
- ✅ 定期备份配置

## 💻 系统要求

- Docker 19.03+
- Docker Compose 1.25+
- 2 核 CPU, 4GB 内存（推荐）
- 10Mbps+ 带宽

## 🆘 故障排查

### Web UI 无法访问
```bash
# 检查容器状态
docker ps | grep openvpn

# 查看日志
docker logs openvpn-gateway

# 检查端口
docker port openvpn-gateway
```

### 连接失败
```bash
# 检查防火墙
sudo ufw status

# 查看 OpenVPN 日志
docker exec openvpn-gateway cat /var/log/openvpn.log
```

更多问题: [故障排查文档](docs/multi-cloud-gateway.md#故障排查)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 基于 [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn)
- 感谢所有贡献者

## 📮 联系方式

- 提交 Issue: [GitHub Issues](https://github.com/ggfgmax/docker-openvpn-gateway/issues)
- 项目主页: [GitHub](https://github.com/ggfgmax/docker-openvpn-gateway)

---

⭐ 如果这个项目对您有帮助，请给个 Star！

**立即开始**: [Web UI 快速开始](WEBUI-QUICKSTART.md) | [中文完整指南](GETTING-STARTED-CN.md)
