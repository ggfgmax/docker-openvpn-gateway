# 多云网络主入口 VPN 网关更新日志

## v2.0.0 - 多云网络主入口功能 (2024-12)

### 新增功能

#### 核心功能
- ✨ **多云网络主入口网关**: 支持通过单一 VPN 连接访问多个云平台内网
- ✨ **Site-to-Site VPN 管理**: 自动管理到各云平台的 VPN 隧道连接
- ✨ **智能路由管理**: 自动配置和推送路由规则到客户端
- ✨ **流量转发优化**: 自动配置 iptables 规则，支持跨隧道流量转发

#### 新增管理命令
- `ovpn_setup_gateway`: 初始化和管理网关配置
- `ovpn_add_remote_site`: 添加远程云平台站点配置
- `ovpn_list_sites`: 列出所有配置的站点及其状态
- `ovpn_update_routes`: 更新路由配置
- `ovpn_start_site_connections`: 启动所有 Site-to-Site VPN 连接
- `ovpn_stop_site_connections`: 停止所有 Site-to-Site VPN 连接

#### 配置增强
- 📝 支持 UDP/TCP 协议的 Site-to-Site 连接
- 📝 支持内联和外部证书文件格式
- 📝 支持自定义端口配置
- 📝 支持多网段路由配置

#### 文档和示例
- 📚 完整的多云网络配置指南 (`docs/multi-cloud-gateway.md`)
- 📚 快速入门文档 (`README-MULTI-CLOUD.md`)
- 🎯 快速配置脚本 (`examples/multi-cloud-setup.sh`)
- 🎯 连通性测试脚本 (`examples/test-connectivity.sh`)
- 🎯 Docker Compose 配置示例 (`docker-compose-gateway.yml`)
- 🎯 配置模板文件 (`config.template`)

#### 容器增强
- 🐳 添加 `iproute2` 和 `curl` 工具支持
- 🐳 预创建站点配置目录
- 🐳 自动包含示例脚本

### 修改内容

#### `bin/ovpn_run`
- 添加 IP 转发启用逻辑
- 添加 iptables 转发规则配置
- 添加 Site-to-Site VPN NAT 规则配置
- 自动启动 Site-to-Site VPN 连接

#### `bin/ovpn_genconfig`
- 支持包含 site-routes.conf 配置文件
- 自动集成 Site-to-Site 路由

#### `Dockerfile`
- 添加 iproute2 和 curl 包
- 创建必要的目录结构
- 包含示例脚本

### 支持的云平台

理论上支持所有提供 OpenVPN 服务的云平台，包括但不限于：
- 华为云
- AWS (Amazon Web Services)
- GCP (Google Cloud Platform)
- Azure (Microsoft Azure)
- 阿里云
- 腾讯云
- 任何支持 OpenVPN 的私有云或 VPS

### 架构说明

```
客户端 → [主入口 VPN] → [华为云 VPN] → 华为云内网
                      → [AWS VPN] → AWS 内网
                      → [GCP VPN] → GCP 内网
```

### 使用场景

1. **多云环境统一访问**: 企业在多个云平台部署资源，需要统一访问入口
2. **混合云架构**: 连接公有云和私有云网络
3. **分支机构互联**: 连接多个分支机构的网络
4. **开发测试环境**: 开发人员一次连接访问所有测试环境

### 兼容性

- ✅ 完全向后兼容原有 docker-openvpn 功能
- ✅ 支持现有客户端配置
- ✅ 不影响标准 OpenVPN 功能

### 安全性

- 🔒 使用标准 OpenVPN 加密
- 🔒 支持证书认证
- 🔒 支持双因素认证 (OTP)
- 🔒 支持客户端证书吊销 (CRL)
- 🔒 支持自定义 iptables 防火墙规则

### 性能建议

- 建议使用至少 2 核 CPU，4GB 内存的服务器
- 建议带宽至少 100Mbps
- 根据实际流量需求选择合适的服务器规格

### 已知限制

- Site-to-Site 连接需要远程 VPN 服务器允许客户端连接
- 需要手动配置远程站点的证书和密钥
- 大量并发连接时可能需要优化系统参数

### 升级说明

从原版 docker-openvpn 升级：
1. 使用新的 Dockerfile 构建镜像
2. 原有配置和证书完全兼容
3. 可选择性启用多云网络功能

### 贡献者

基于 [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn) 项目开发

### 许可证

MIT License - 与原项目保持一致

---

## 原版功能保留

所有原版 docker-openvpn 的功能都得到保留，包括：
- 标准 OpenVPN 服务器功能
- EasyRSA PKI 管理
- 客户端配置生成
- OTP 双因素认证
- 静态 IP 分配
- IPv6 支持
- 所有原有脚本和命令

