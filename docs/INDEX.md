# 📚 文档索引

## 🚀 快速开始指南

### 新手必读
1. **[快速启动指南](guides/QUICK_START.md)** ⭐ **推荐首先阅读**
   - 从零到部署的完整步骤
   - 初始化 PKI 详细说明
   - 环境变量配置
   - 验证方法

2. **[站点证书配置指南](guides/SITE_CERTIFICATE_GUIDE.md)**
   - Site-to-Site VPN 配置详解
   - .ovpn 文件说明
   - 一键添加站点流程
   - 常见问题解答

3. **[日志和调试指南](guides/LOGGING_GUIDE.md)**
   - 所有日志位置说明
   - 50+ 调试命令
   - 浏览器调试技巧
   - 日志导出和持久化

4. **[删除站点行为说明](guides/DELETE_SITE_BEHAVIOR.md)**
   - 删除站点完整流程
   - 路由更新机制
   - 需要重启的原因
   - 批量操作建议

## 🔧 问题排查

### 认证和登录问题
- **[认证问题修复](troubleshooting/FIX_AUTHENTICATION.md)**
  - 认证窗口不弹出
  - 输入账号密码后失败
  - 500 错误排查

### 证书生成问题
- **[客户端证书生成修复](troubleshooting/FIX_CLIENT_CERT_GENERATION.md)**
  - vars 文件缺失
  - CA 密码问题
  - expect 自动确认
  - 三种解决方案对比

### 模式和配置问题
- **[网关模式环境变量修复](troubleshooting/FIX_GATEWAY_MODE.md)**
  - GATEWAY_MODE 不生效的原因
  - 三种修复方案
  - 验证方法

### 连通性问题
- **[连通性排查指南](troubleshooting/TROUBLESHOOTING_CONNECTIVITY.md)**
  - 网关能通，客户端不通
  - 路由推送问题
  - iptables 规则检查
  - 完整的诊断流程

## 📖 深入理解

### 功能说明
- **[Web UI v2.0 改进说明](WEBUI_V2_IMPROVEMENTS.md)**
  - 一键添加站点的设计
  - 用户体验对比
  - 技术实现细节
  - 验证功能

- **[默认 nopass CA 变更说明](CHANGELOG_NOPASS_DEFAULT.md)**
  - 为什么改为默认无密码
  - 向后兼容性
  - 安全性考虑
  - 迁移指南

### 高级配置
- **[高级配置](advanced-config.md)**
  - TCP 协议配置
  - 压缩配置
  - 自定义网段
  - IPv6 支持
  - 静态 IP
  - OTP 双因素认证

## 📋 按使用场景查找

### 场景 1：首次部署
1. [快速启动指南](guides/QUICK_START.md) - 必读
2. [日志调试指南](guides/LOGGING_GUIDE.md) - 了解日志位置

### 场景 2：添加 Site-to-Site VPN
1. [站点证书配置指南](guides/SITE_CERTIFICATE_GUIDE.md) - 完整流程
2. [连通性排查指南](troubleshooting/TROUBLESHOOTING_CONNECTIVITY.md) - 如遇问题

### 场景 3：遇到认证问题
1. [认证问题修复](troubleshooting/FIX_AUTHENTICATION.md)
2. [日志调试指南](guides/LOGGING_GUIDE.md)

### 场景 4：生成证书失败
1. [客户端证书生成修复](troubleshooting/FIX_CLIENT_CERT_GENERATION.md)
2. [默认 nopass CA 说明](CHANGELOG_NOPASS_DEFAULT.md)

### 场景 5：环境变量不生效
1. [网关模式修复](troubleshooting/FIX_GATEWAY_MODE.md)

## 🎯 快速参考

### 常用命令
```bash
# 查看日志
docker logs -f openvpn-gateway

# 进入容器
docker exec -it openvpn-gateway bash

# 重启服务
docker restart openvpn-gateway

# 查看站点状态
docker exec openvpn-gateway ps aux | grep openvpn

# 查看路由
docker exec openvpn-gateway ip route

# 测试连接
docker exec openvpn-gateway ping 10.80.0.2
```

### 常见问题快速链接
- 认证窗口不弹出 → [FIX_AUTHENTICATION.md](troubleshooting/FIX_AUTHENTICATION.md)
- 生成证书失败 → [FIX_CLIENT_CERT_GENERATION.md](troubleshooting/FIX_CLIENT_CERT_GENERATION.md)
- 模式不生效 → [FIX_GATEWAY_MODE.md](troubleshooting/FIX_GATEWAY_MODE.md)
- 无法访问远程内网 → [TROUBLESHOOTING_CONNECTIVITY.md](troubleshooting/TROUBLESHOOTING_CONNECTIVITY.md)
- 查看日志方法 → [LOGGING_GUIDE.md](guides/LOGGING_GUIDE.md)

## 📊 文档统计

- **指南文档**: 4 篇
- **排查文档**: 4 篇
- **说明文档**: 2 篇
- **总计**: 10 篇详细文档

## 🔄 文档更新

所有文档基于 **v2.0.0 (2025-12-19)** 版本编写，反映最新的功能和修复。

## 💡 阅读建议

### 新用户
1. 先读 [快速启动指南](guides/QUICK_START.md)
2. 部署时遇到问题，查看对应的排查文档
3. 功能使用参考主 [README.md](../README.md)

### 有经验用户
1. 直接参考主 [README.md](../README.md) 快速部署
2. 遇到特定问题，查看对应的排查文档
3. 深入了解改进，阅读 [Web UI v2.0 改进](WEBUI_V2_IMPROVEMENTS.md)

### 开发者
1. [Web UI v2.0 改进说明](WEBUI_V2_IMPROVEMENTS.md) - 技术实现
2. [默认 nopass 变更](CHANGELOG_NOPASS_DEFAULT.md) - 行为变更说明
3. 查看主 [CHANGELOG.md](../CHANGELOG.md)

---

**返回**: [主 README](../README.md) | [GitHub 仓库](https://github.com/ggfgmax/docker-openvpn-gateway)
