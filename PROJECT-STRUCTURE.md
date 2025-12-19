# 项目目录结构

## 📂 目录说明

```
docker-openvpn-gateway/
├── bin/                          # 核心管理脚本
│   ├── ovpn_genconfig           # 生成 OpenVPN 配置
│   ├── ovpn_initpki             # 初始化 PKI 证书系统
│   ├── ovpn_run                 # 运行 OpenVPN 服务
│   ├── ovpn_run_webui           # 运行 Web 管理界面
│   ├── ovpn_set_mode            # 切换运行模式
│   ├── ovpn_config_ldap         # 配置 LDAP 认证
│   ├── ovpn_add_remote_site     # 添加远程站点
│   ├── ovpn_list_sites          # 列出站点状态
│   ├── ovpn_setup_gateway       # 设置网关
│   ├── ovpn_update_routes       # 更新路由配置
│   ├── ovpn_start_site_connections  # 启动站点连接
│   ├── ovpn_stop_site_connections   # 停止站点连接
│   └── ...                      # 其他管理脚本
│
├── webui/                        # Web 管理界面
│   ├── app.py                   # Flask 后端应用
│   ├── templates/               # HTML 模板
│   │   └── index.html          # 主页面
│   ├── requirements.txt         # Python 依赖
│   └── README.md                # Web UI 说明
│
├── docs/                         # 完整文档
│   ├── quickstart-webui.md      # Web UI 快速开始 ⭐
│   ├── faq.md                   # 常见问题
│   ├── troubleshooting.md       # 故障排查指南
│   ├── multi-cloud-gateway.md   # 多云网络配置
│   ├── ldap.md                  # LDAP 认证配置
│   ├── mode-switching.md        # 模式切换指南
│   ├── webui.md                 # Web UI 完整文档
│   ├── advanced.md              # 高级配置
│   ├── security.md              # 安全最佳实践
│   └── ...                      # 其他文档
│
├── scripts/                      # 辅助脚本
│   ├── build-gateway.sh         # 构建 Docker 镜像
│   ├── setup/                   # 设置脚本
│   │   ├── multi-cloud-setup.sh # 多云环境快速配置
│   │   └── ldap-setup.sh        # LDAP 快速配置
│   ├── tests/                   # 测试脚本
│   │   └── test-connectivity.sh # 连通性测试
│   └── examples/                # 示例脚本（预留）
│
├── config/                       # 配置模板
│   ├── config.template          # 主配置模板
│   └── webui-config.example     # Web UI 配置示例
│
├── init/                         # 系统初始化脚本
│   ├── docker-openvpn@.service  # Systemd 服务文件
│   └── upstart.init             # Upstart 初始化脚本
│
├── otp/                          # OTP 双因素认证
│   └── openvpn                  # PAM 配置
│
├── tests/                        # 原项目测试脚本
│   ├── basic.sh
│   ├── otp.sh
│   └── ...
│
├── docker-compose-webui.yml      # Web UI 部署配置
├── docker-compose-gateway.yml    # 标准部署配置
├── Dockerfile                    # Docker 镜像定义
├── README.md                     # 项目主文档
├── LICENSE                       # MIT 许可证
├── CONTRIBUTING.md               # 贡献指南
└── .gitignore                    # Git 忽略文件
```

## 📋 核心文件说明

### 配置文件

| 文件 | 说明 |
|------|------|
| `Dockerfile` | Docker 镜像构建定义 |
| `docker-compose-webui.yml` | Web UI 部署配置（推荐） |
| `docker-compose-gateway.yml` | 标准部署配置 |
| `config/config.template` | 环境变量配置模板 |
| `.gitignore` | Git 忽略文件配置 |

### 文档文件

| 文件 | 说明 | 优先级 |
|------|------|--------|
| `README.md` | 项目主文档 | ⭐⭐⭐ |
| `docs/quickstart-webui.md` | Web UI 快速开始 | ⭐⭐⭐ |
| `docs/faq.md` | 常见问题 | ⭐⭐ |
| `docs/troubleshooting.md` | 故障排查 | ⭐⭐ |
| `docs/multi-cloud-gateway.md` | 多云配置完整指南 | ⭐⭐ |
| `docs/ldap.md` | LDAP 认证配置 | ⭐ |
| `docs/webui.md` | Web UI 完整文档 | ⭐ |

### 脚本文件

| 文件 | 说明 | 使用场景 |
|------|------|----------|
| `scripts/build-gateway.sh` | 构建镜像 | 首次部署/更新 |
| `scripts/setup/multi-cloud-setup.sh` | 多云快速配置 | 多云环境 |
| `scripts/setup/ldap-setup.sh` | LDAP 快速配置 | LDAP 认证 |
| `scripts/tests/test-connectivity.sh` | 连通性测试 | 故障排查 |

## 🎯 不同用户的入口

### 新手用户 (小白)

1. 开始: `README.md`
2. 快速部署: `docs/quickstart-webui.md`
3. 遇到问题: `docs/faq.md`

### 中级用户 (IT 管理员)

1. 快速开始: `docs/quickstart-webui.md`
2. 多云配置: `docs/multi-cloud-gateway.md`
3. LDAP 配置: `docs/ldap.md`
4. 故障排查: `docs/troubleshooting.md`

### 高级用户 (DevOps/开发者)

1. 项目结构: `PROJECT-STRUCTURE.md`
2. 脚本说明: `scripts/` 目录
3. API 文档: `docs/api.md`
4. 贡献指南: `CONTRIBUTING.md`

## 🔄 工作流程

### 首次部署

```
README.md
  ↓
docs/quickstart-webui.md
  ↓
scripts/build-gateway.sh
  ↓
docker-compose-webui.yml
```

### 多云配置

```
docs/multi-cloud-gateway.md
  ↓
Web UI 或 scripts/setup/multi-cloud-setup.sh
  ↓
配置站点证书
  ↓
重启服务
```

### LDAP 配置

```
docs/ldap.md
  ↓
Web UI 或 scripts/setup/ldap-setup.sh
  ↓
测试连接
  ↓
重启服务
```

### 故障排查

```
遇到问题
  ↓
docs/faq.md (查找常见问题)
  ↓
docs/troubleshooting.md (详细排查)
  ↓
scripts/tests/test-connectivity.sh (测试)
```

## 📦 运行时目录 (容器内)

```
/etc/openvpn/                    # OpenVPN 配置目录
├── openvpn.conf                 # 主配置文件
├── ovpn_env.sh                  # 环境变量
├── ldap.conf                    # LDAP 配置
├── sites/                       # 站点配置
│   ├── huawei.conf             # 华为云站点
│   ├── huawei.info             # 站点信息
│   ├── aws.conf                # AWS 站点
│   └── ...
├── site-pids/                   # 站点进程 PID
├── pki/                         # PKI 证书
│   ├── ca.crt                  # CA 证书
│   ├── private/                # 私钥
│   ├── issued/                 # 已签发证书
│   └── ...
├── clients/                     # 客户端配置
└── ccd/                         # 客户端自定义配置

/opt/openvpn-webui/              # Web UI 应用
├── app.py
├── templates/
└── ...

/var/log/                        # 日志文件
├── openvpn.log                 # 主日志
├── openvpn-huawei.log          # 华为云站点日志
├── openvpn-aws.log             # AWS 站点日志
└── ...
```

## 🔧 开发目录

### 添加新功能

- 脚本: `bin/`
- 文档: `docs/`
- 示例: `scripts/examples/`
- 测试: `scripts/tests/`

### 添加新文档

- 快速开始类: `docs/quickstart-*.md`
- 配置指南类: `docs/*-gateway.md`, `docs/*-config.md`
- 参考类: `docs/api.md`, `docs/commands.md`

## 📝 维护说明

### 定期维护

- 更新文档: `docs/`
- 更新脚本: `scripts/`
- 更新依赖: `webui/requirements.txt`, `Dockerfile`

### 版本发布

1. 更新 `CHANGELOG.md`
2. 更新版本号
3. 构建镜像: `scripts/build-gateway.sh`
4. 测试: `scripts/tests/`
5. 发布: Git tag + Docker Hub

## 🎓 学习路径

### 第一周: 基础使用

- [ ] 阅读 `README.md`
- [ ] 完成 `docs/quickstart-webui.md`
- [ ] 生成第一个客户端证书
- [ ] 熟悉 Web UI 界面

### 第二周: 进阶配置

- [ ] 配置 LDAP 认证
- [ ] 切换运行模式
- [ ] 理解路由配置

### 第三周: 多云环境

- [ ] 添加第一个远程站点
- [ ] 配置站点证书
- [ ] 测试 Site-to-Site 连接
- [ ] 客户端测试连通性

### 第四周: 运维和优化

- [ ] 性能优化
- [ ] 安全加固
- [ ] 备份和恢复
- [ ] 故障排查

---

**保持项目结构的清晰和一致性，有利于维护和协作！**

