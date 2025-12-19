# OpenVPN 多云网络主入口网关 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![OpenVPN](https://img.shields.io/badge/OpenVPN-2.x-green.svg)](https://openvpn.net/)

> 基于 [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn) 增强版本  
> 支持多云网络打通、LDAP 认证、Web 管理界面

## ✨ 核心特性

### 🌐 多云网络主入口
- **一键打通多云** - 连接华为云、AWS、GCP 等多个云平台
- **Site-to-Site VPN** - 自动管理站点间 VPN 隧道
- **智能路由** - 自动配置路由规则
- **流量转发** - 自动设置 iptables 转发规则

### 🌟 Web 管理界面
- **零命令行操作** - 图形化配置所有功能
- **证书一键配置** - 直接粘贴 .ovpn 内容，无需 SSH
- **实时监控** - 查看站点、客户端状态
- **适合小白** - 直观易用的操作界面

### 🔐 企业级认证
- **LDAP/AD 支持** - 集成企业目录服务
- **双因素认证** - 支持证书 + 密码/OTP
- **灵活配置** - 多种认证方式组合

### 🎛️ 灵活模式切换
- **普通 VPN 模式** - 标准远程访问
- **网关模式** - 多云网络中心
- **一键切换** - 无缝模式转换

## 🚀 5 分钟快速开始

### 使用 Web 管理界面（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/ggfgmax/docker-openvpn-gateway.git
cd docker-openvpn-gateway

# 2. 构建镜像
bash scripts/build-gateway.sh

# 3. 初始化配置
docker volume create openvpn-data
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki

# 4. 启动服务（包含 Web UI）
docker-compose -f docker-compose-webui.yml up -d

# 5. 访问 Web 界面
# 浏览器打开: http://服务器IP:8080
# 用户名: admin  密码: openvpn
```

**⚠️ 重要**: 首次登录后请立即修改默认密码！

详细文档: [Web UI 快速开始](docs/quickstart-webui.md)

## 📖 文档导航

### 新手入门
- [Web UI 快速开始](docs/quickstart-webui.md) ⭐ 推荐
- [完整部署指南](docs/getting-started.md)
- [常见问题 FAQ](docs/faq.md)

### 功能文档
- [多云网络配置](docs/multi-cloud-gateway.md)
- [LDAP 认证配置](docs/ldap.md)
- [运行模式切换](docs/mode-switching.md)
- [Web UI 完整文档](docs/webui.md)

### 进阶内容
- [API 文档](docs/api.md)
- [安全最佳实践](docs/security.md)
- [故障排查](docs/troubleshooting.md)

## 🎯 典型场景

### 场景 1: 企业内部 VPN
**需求**: 员工远程访问内网，使用 AD 账户认证

```bash
# 启动 Web UI
docker-compose -f docker-compose-webui.yml up -d

# 在 Web UI 中:
# 1. 配置 LDAP (使用 AD 模板)
# 2. 生成客户端证书
# 3. 分发给员工
```

### 场景 2: 多云环境统一访问
**需求**: 访问华为云、AWS、GCP 多个云平台内网

```bash
# 在 Web UI 中:
# 1. 切换到"网关模式"
# 2. 添加华为云、AWS、GCP 站点
# 3. 粘贴各云平台 .ovpn 内容配置证书
# 4. 重启服务
# ✅ 客户端连接后可访问所有云平台
```

### 场景 3: 开发测试环境
**需求**: 连接多个测试环境 VPN

```bash
# 配置为网关模式，添加各环境站点
# 开发人员只需一个 VPN 连接
```

## 📂 项目结构

```
docker-openvpn-gateway/
├── bin/                      # 核心管理脚本
│   ├── ovpn_genconfig       # 生成配置
│   ├── ovpn_set_mode        # 模式切换
│   ├── ovpn_config_ldap     # LDAP 配置
│   ├── ovpn_add_remote_site # 添加站点
│   └── ...
├── webui/                    # Web 管理界面
│   ├── app.py               # Flask 后端
│   ├── templates/           # 前端页面
│   └── requirements.txt
├── docs/                     # 完整文档
│   ├── quickstart-webui.md
│   ├── multi-cloud-gateway.md
│   ├── ldap.md
│   └── ...
├── scripts/                  # 辅助脚本
│   ├── setup/               # 快速配置脚本
│   ├── examples/            # 示例脚本
│   └── tests/               # 测试脚本
├── config/                   # 配置模板
│   ├── config.template
│   └── webui-config.example
├── docker-compose-webui.yml  # Web UI 部署
├── docker-compose-gateway.yml # 标准部署
└── Dockerfile
```

## 🔧 管理命令

### Web UI 操作
访问 `http://服务器IP:8080` 完成所有配置

### 命令行操作

| 命令 | 说明 |
|------|------|
| `ovpn_set_mode [normal\|gateway]` | 切换运行模式 |
| `ovpn_config_ldap` | 配置 LDAP 认证 |
| `ovpn_add_remote_site` | 添加远程站点 |
| `ovpn_list_sites` | 列出站点状态 |
| `ovpn_setup_gateway` | 初始化网关 |

完整命令: [命令参考](docs/commands.md)

## 🌟 对比原版

| 功能 | 原版 | 本项目 |
|------|------|--------|
| 标准 VPN | ✅ | ✅ |
| 多云网络打通 | ❌ | ✅ |
| LDAP/AD 认证 | ❌ | ✅ |
| 运行模式切换 | ❌ | ✅ |
| Web 管理界面 | ❌ | ✅ |
| 证书自动配置 | ❌ | ✅ |

## 🔐 安全建议

- ✅ 修改 Web UI 默认密码
- ✅ 使用 HTTPS（Nginx 反向代理）
- ✅ 限制 Web UI 访问 IP
- ✅ 使用强 CA 密码
- ✅ 启用 LDAP 认证
- ✅ 定期备份配置

详细: [安全最佳实践](docs/security.md)

## 💻 系统要求

- Docker 19.03+
- Docker Compose 1.25+
- 2 核 CPU, 4GB 内存（推荐）
- 10Mbps+ 带宽

## 🆘 获取帮助

- 📖 [文档中心](docs/)
- 💬 [提交 Issue](https://github.com/ggfgmax/docker-openvpn-gateway/issues)
- 🐛 [故障排查](docs/troubleshooting.md)

## 🤝 贡献

欢迎贡献代码！请查看 [贡献指南](CONTRIBUTING.md)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 🙏 致谢

基于 [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn)

---

⭐ **觉得不错？给个 Star 吧！**

**快速开始**: [Web UI 快速开始](docs/quickstart-webui.md) | [完整文档](docs/)

