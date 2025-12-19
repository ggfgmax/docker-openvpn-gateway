# 更新日志

## v2.0.0 - 多云网络主入口网关 (2024-12-19)

### 🎉 重大更新

#### 新增功能

**多云网络主入口网关**
- ✨ Site-to-Site VPN 自动管理
- ✨ 支持打通华为云、AWS、GCP 等多个云平台
- ✨ 智能路由配置和推送
- ✨ 自动 iptables 转发规则

**Web 管理界面** ⭐
- ✨ 零命令行操作的图形化界面
- ✨ 证书一键配置（直接粘贴 .ovpn 内容）
- ✨ 实时状态监控
- ✨ 适合小白用户

**LDAP/AD 认证**
- ✨ OpenLDAP 支持
- ✨ Active Directory 支持
- ✨ 图形化 LDAP 配置界面
- ✨ 双因素认证（证书 + LDAP）

**运行模式切换**
- ✨ 普通 VPN 模式
- ✨ 网关模式
- ✨ 一键切换
- ✨ 环境变量控制

#### 新增管理命令

- `ovpn_set_mode` - 切换运行模式
- `ovpn_config_ldap` - 配置 LDAP 认证
- `ovpn_add_remote_site` - 添加远程站点
- `ovpn_list_sites` - 列出站点状态
- `ovpn_setup_gateway` - 初始化网关
- `ovpn_start_site_connections` - 启动站点连接
- `ovpn_stop_site_connections` - 停止站点连接
- `ovpn_update_routes` - 更新路由配置
- `ovpn_run_webui` - 运行 Web UI

#### Web UI 功能

- 📊 系统状态概览
- ⚙️ 运行模式切换
- 🔑 LDAP 配置界面
- 🌐 站点管理（添加、删除、配置证书）
- 👥 客户端管理（生成、下载、吊销）
- 📝 日志查看

#### 文档体系

- `docs/quickstart-webui.md` - Web UI 快速开始
- `docs/faq.md` - 常见问题
- `docs/troubleshooting.md` - 故障排查
- `docs/multi-cloud-gateway.md` - 多云配置指南
- `docs/ldap.md` - LDAP 配置指南
- `docs/mode-switching.md` - 模式切换指南
- `docs/webui.md` - Web UI 完整文档
- `PROJECT-STRUCTURE.md` - 项目结构说明

#### 脚本工具

- `scripts/build-gateway.sh` - 镜像构建脚本
- `scripts/setup/multi-cloud-setup.sh` - 多云快速配置
- `scripts/setup/ldap-setup.sh` - LDAP 快速配置
- `scripts/tests/test-connectivity.sh` - 连通性测试

#### 配置模板

- `config/config.template` - 主配置模板
- `config/webui-config.example` - Web UI 配置示例

### 🔧 改进和优化

**目录结构重组**
- 脚本分类到 `scripts/` 目录
- 配置模板移到 `config/` 目录
- 文档统一在 `docs/` 目录
- 更清晰的项目结构

**Dockerfile 增强**
- 添加 Python 和 Flask 支持
- 添加 LDAP 客户端工具
- 添加 iproute2 网络工具
- 预创建必要目录

**bin/ovpn_run 增强**
- 添加模式检测
- 条件性启用 Site-to-Site VPN
- 自动配置 iptables 规则
- 启动 Site-to-Site 连接

**bin/ovpn_genconfig 增强**
- 支持 site-routes.conf 包含
- 自动集成远程站点路由

### 🔒 安全改进

- Web UI 基础认证
- 环境变量配置敏感信息
- .gitignore 排除敏感文件
- 配置模板示例

### 📚 文档完善

- 完整的中文文档
- 多云网络配置指南
- LDAP 认证配置指南
- Web UI 使用指南
- 故障排查指南
- 常见问题 FAQ

### 🎯 用户体验

- 降低使用门槛
- 图形化操作界面
- 一键操作
- 快速配置脚本
- 清晰的文档结构

### ✅ 向后兼容

- 完全兼容原版功能
- 默认行为与原版一致
- 可选择性启用新功能
- 不影响现有配置

## 已知问题

无重大已知问题

## 下一个版本计划

- [ ] Web UI 中文界面
- [ ] 用户权限管理
- [ ] 更详细的日志分析
- [ ] 监控和告警
- [ ] API 文档完善
- [ ] 性能监控面板

## 贡献者

感谢所有贡献者的支持！

## 基于项目

- [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn)

---

**查看详细变更**: [GitHub Commits](https://github.com/ggfgmax/docker-openvpn-gateway/commits)

