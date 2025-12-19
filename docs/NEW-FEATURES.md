# 新功能说明

## 概述

本版本新增了三个重要功能：

1. **Web 管理界面** - 图形化配置和管理，小白也能轻松使用
2. **LDAP 认证支持** - 支持使用企业 LDAP/Active Directory 账户登录
3. **模式开关** - 可以自由切换普通 VPN 和网关模式

## 🌟 功能一：Web 管理界面（重磅功能）

### 特性

- ✅ **零命令行操作** - 所有配置都可通过浏览器完成
- ✅ **直观的图形界面** - 清晰的标签页布局
- ✅ **实时状态监控** - 查看服务器、站点、客户端状态
- ✅ **一键操作** - 模式切换、LDAP 配置、证书生成等
- ✅ **适合小白** - 无需学习复杂命令
- ✅ **基础认证保护** - 用户名密码访问控制

### 快速开始

```bash
# 1. 启动服务（包含 Web UI）
docker run -d \
  --name openvpn-gateway \
  -v openvpn-data:/etc/openvpn \
  -p 1194:1194/udp \
  -p 8080:8080 \
  -e WEBUI_USERNAME=admin \
  -e WEBUI_PASSWORD=your-password \
  --cap-add=NET_ADMIN \
  openvpn-gateway:latest \
  sh -c "ovpn_run_webui & ovpn_run"

# 2. 访问 Web 界面
# 浏览器打开: http://服务器IP:8080
# 用户名: admin
# 密码: your-password
```

### 界面功能

**📊 概览页面**:
- 系统状态总览
- 运行模式显示
- LDAP 认证状态
- 站点和客户端统计

**⚙️ 模式设置**:
- 可视化选择普通 VPN 或网关模式
- 一键切换运行模式
- 清晰的模式特性说明

**🔑 LDAP 配置**:
- 图形化配置 LDAP/AD 认证
- 内置 OpenLDAP 和 AD 模板
- 一键填充常用配置

**🌐 站点管理**:
- 添加/删除远程 VPN 站点
- 查看站点连接状态
- 管理站点配置

**👥 客户端管理**:
- 生成客户端证书
- 一键下载 .ovpn 配置文件
- 吊销客户端证书

### 界面截图说明

**首页概览**:
```
┌─────────────────────────────────────────┐
│ 🔐 OpenVPN Web 管理界面                  │
│                                         │
│ 运行模式: 网关模式                       │
│ LDAP: 已启用                            │
│ 站点数: 3    客户端数: 5                 │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│ [📊 概览] [⚙️ 模式] [🔑 LDAP] [🌐 站点] [👥 客户端] │
└─────────────────────────────────────────┘
```

### 详细文档

- [Web UI 快速开始](WEBUI-QUICKSTART.md)
- [Web UI 完整指南](docs/webui.md)

---

## 🔐 功能二：LDAP 认证支持

## 🔐 功能一：LDAP 认证

### 特性

- ✅ 支持 OpenLDAP
- ✅ 支持 Active Directory
- ✅ 支持 LDAP 和 LDAPS (TLS)
- ✅ 支持自定义用户过滤器
- ✅ 支持绑定 DN 认证
- ✅ 可与客户端证书结合实现双因素认证

### 快速使用

#### 1. 配置 LDAP (OpenLDAP)

```bash
docker run -v ovpn-data:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_config_ldap \
    -h ldap.company.com \
    -b "dc=company,dc=com" \
    -D "cn=admin,dc=company,dc=com" \
    -w "password"
```

#### 2. 配置 LDAP (Active Directory)

```bash
docker run -v ovpn-data:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_config_ldap \
    -h ad.company.com \
    -b "dc=company,dc=com" \
    -D "CN=VPN Service,OU=Service Accounts,DC=company,DC=com" \
    -w "password" \
    -f "(&(objectClass=user)(sAMAccountName=%u))" \
    -s sAMAccountName
```

#### 3. 启用 LDAP 认证

```bash
# 重新生成配置（-2 参数启用用户认证）
docker run -v ovpn-data:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u udp://vpn.company.com -2

# 重启服务
docker restart openvpn-container
```

#### 4. 客户端连接

客户端配置文件会包含 `auth-user-pass`，连接时提示输入：
- **用户名**: LDAP 用户名（如 `zhangsan`）
- **密码**: LDAP 密码

### 使用快速配置脚本

```bash
# 下载脚本
docker run -v $PWD:/tmp --rm kylemanna/openvpn \
    cp /usr/share/doc/openvpn/examples/ldap-setup.sh /tmp/

# 编辑配置
vim ldap-setup.sh
# 修改 LDAP_HOST, LDAP_BASE_DN 等变量

# 运行脚本
bash ldap-setup.sh
```

### 详细文档

查看完整的 LDAP 配置指南：[docs/ldap.md](docs/ldap.md)

---

## 🔄 功能二：模式开关

### 两种运行模式

#### 普通 VPN 模式（默认）
- 标准的 OpenVPN 服务器功能
- 客户端连接后访问服务器所在网络
- 适合简单的远程访问场景
- 资源消耗低

#### 网关模式
- 多云网络主入口功能
- 自动启动 Site-to-Site VPN 连接
- 客户端可访问所有配置的远程网络
- 适合多云环境统一访问
- 需要额外配置远程站点

### 快速使用

#### 查看当前模式

```bash
docker exec openvpn-container ovpn_set_mode
```

输出示例：
```
当前模式: 普通 VPN 模式 (Normal VPN Mode)
LDAP 认证: 未启用

提示: 使用 'ovpn_set_mode normal' 或 'ovpn_set_mode gateway' 切换模式
```

#### 切换到普通 VPN 模式

```bash
docker exec openvpn-container ovpn_set_mode normal
docker restart openvpn-container
```

#### 切换到网关模式

```bash
# 1. 切换模式
docker exec openvpn-container ovpn_set_mode gateway

# 2. 初始化网关（如果还未初始化）
docker exec openvpn-container ovpn_setup_gateway -i

# 3. 添加远程站点
docker exec openvpn-container ovpn_add_remote_site \
    -n huawei \
    -h vpn.huaweicloud.example.com \
    -p 1194 \
    -s 172.16.0.0/16

# 4. 配置站点证书（进入容器编辑）
docker exec -it openvpn-container bash
vi /etc/openvpn/sites/huawei.conf
# 添加证书内容后 exit

# 5. 更新路由
docker exec openvpn-container ovpn_update_routes

# 6. 重启服务
docker restart openvpn-container
```

#### 使用环境变量设置默认模式

**docker-compose.yml**:
```yaml
services:
  openvpn:
    environment:
      # 0=普通VPN, 1=网关模式
      - GATEWAY_MODE=0
      # 0=禁用LDAP, 1=启用LDAP
      - LDAP_ENABLED=0
```

**直接运行**:
```bash
# 普通模式
docker run -e GATEWAY_MODE=0 -v ovpn-data:/etc/openvpn ...

# 网关模式
docker run -e GATEWAY_MODE=1 -v ovpn-data:/etc/openvpn ...
```

### 详细文档

查看完整的模式切换指南：[docs/mode-switching.md](docs/mode-switching.md)

---

## 🎯 组合使用示例

### 场景 1: 普通 VPN + LDAP 认证

适合：企业内部远程访问，使用 AD 账户

```bash
# 1. 配置 LDAP
docker run -v ovpn-data:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_config_ldap \
    -h ad.company.com \
    -b "dc=company,dc=com" \
    -D "CN=VPN Service,DC=company,DC=com" \
    -w "password" \
    -f "(&(objectClass=user)(sAMAccountName=%u))" \
    -s sAMAccountName

# 2. 设置为普通模式
docker exec openvpn ovpn_set_mode normal

# 3. 生成配置（启用 LDAP）
docker run -v ovpn-data:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u udp://vpn.company.com -2

# 4. 启动服务
docker run -v ovpn-data:/etc/openvpn -d -p 1194:1194/udp \
    -e GATEWAY_MODE=0 -e LDAP_ENABLED=1 \
    --cap-add=NET_ADMIN --name openvpn kylemanna/openvpn
```

### 场景 2: 网关模式 + LDAP 认证

适合：多云环境，使用 LDAP 统一账户

```bash
# 1. 配置 LDAP
docker run -v ovpn-data:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_config_ldap \
    -h ldap.company.com \
    -b "dc=company,dc=com" \
    -D "cn=readonly,dc=company,dc=com" \
    -w "password"

# 2. 设置为网关模式
docker exec openvpn ovpn_set_mode gateway

# 3. 初始化网关
docker exec openvpn ovpn_setup_gateway -i

# 4. 添加远程站点（华为云、AWS、GCP）
docker exec openvpn ovpn_add_remote_site -n huawei -h vpn.huawei.com -p 1194 -s 172.16.0.0/16
docker exec openvpn ovpn_add_remote_site -n aws -h vpn.aws.com -p 1194 -s 10.0.0.0/16
docker exec openvpn ovpn_add_remote_site -n gcp -h vpn.gcp.com -p 1194 -s 192.168.0.0/16

# 5. 配置站点证书（手动）
docker exec -it openvpn bash
# 编辑各站点配置添加证书...
exit

# 6. 更新路由
docker exec openvpn ovpn_update_routes

# 7. 生成配置
docker run -v ovpn-data:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u udp://vpn.company.com -2

# 8. 启动服务
docker run -v ovpn-data:/etc/openvpn -d -p 1194:1194/udp \
    -e GATEWAY_MODE=1 -e LDAP_ENABLED=1 \
    --cap-add=NET_ADMIN --name openvpn-gateway kylemanna/openvpn
```

### 场景 3: 网关模式 + 证书认证（无 LDAP）

适合：多云环境，使用证书认证

```bash
# 设置为网关模式
docker exec openvpn ovpn_set_mode gateway

# 启动服务
docker run -v ovpn-data:/etc/openvpn -d -p 1194:1194/udp \
    -e GATEWAY_MODE=1 -e LDAP_ENABLED=0 \
    --cap-add=NET_ADMIN --name openvpn-gateway kylemanna/openvpn
```

---

## 📁 新增文件

### 管理脚本
- `bin/ovpn_config_ldap` - LDAP 配置脚本
- `bin/ovpn_set_mode` - 模式切换脚本

### 文档
- `docs/ldap.md` - LDAP 认证完整指南
- `docs/mode-switching.md` - 模式切换完整指南
- `NEW-FEATURES.md` - 本文件

### 示例脚本
- `examples/ldap-setup.sh` - LDAP 快速配置脚本

### 配置文件
- `config.template` - 更新，包含 LDAP 和模式配置
- `docker-compose-gateway.yml` - 更新，支持环境变量控制

---

## 🔧 环境变量

| 变量名 | 说明 | 默认值 | 可选值 |
|--------|------|--------|--------|
| `GATEWAY_MODE` | VPN 运行模式 | `0` | `0` (普通), `1` (网关) |
| `LDAP_ENABLED` | LDAP 认证 | `0` | `0` (禁用), `1` (启用) |
| `DEBUG` | 调试模式 | `0` | `0` (禁用), `1` (启用) |

---

## 📝 升级说明

### 从旧版本升级

1. **重新构建镜像**（包含 LDAP 依赖）:
```bash
bash build-gateway.sh
```

2. **原有配置兼容**: 
   - 所有原有配置和证书完全兼容
   - 默认为普通 VPN 模式（`GATEWAY_MODE=0`）
   - 默认不启用 LDAP（`LDAP_ENABLED=0`）

3. **可选择性启用新功能**:
   - 需要 LDAP：运行 `ovpn_config_ldap`
   - 需要网关模式：运行 `ovpn_set_mode gateway`

### 向后兼容性

✅ 完全向后兼容
- 不使用新功能时，行为与原版完全一致
- 所有原有脚本和命令继续工作
- 客户端配置无需更改（除非启用 LDAP）

---

## 🎓 学习资源

### 快速开始
1. [GETTING-STARTED-CN.md](GETTING-STARTED-CN.md) - 中文快速开始指南
2. [README-MULTI-CLOUD.md](README-MULTI-CLOUD.md) - 多云网关简明指南

### 详细文档
1. [docs/ldap.md](docs/ldap.md) - LDAP 认证配置
2. [docs/mode-switching.md](docs/mode-switching.md) - 模式切换
3. [docs/multi-cloud-gateway.md](docs/multi-cloud-gateway.md) - 多云网关完整指南

### 示例脚本
1. `examples/multi-cloud-setup.sh` - 多云网关快速配置
2. `examples/ldap-setup.sh` - LDAP 快速配置
3. `examples/test-connectivity.sh` - 连通性测试

---

## 🆘 常见问题

### Q: 切换模式后需要重新生成客户端配置吗？

A: 不需要。模式切换主要影响服务器端的路由和转发行为，客户端配置不受影响。但如果启用了 LDAP，客户端配置会包含 `auth-user-pass`。

### Q: 可以同时使用证书和 LDAP 认证吗？

A: 可以！这提供了双因素认证：
- 客户端需要有效的证书文件
- 连接时需要输入正确的 LDAP 用户名密码

### Q: LDAP 配置后原有的证书认证还能用吗？

A: 可以。启用 LDAP 后：
- 如果客户端配置有 `auth-user-pass`，需要输入用户名密码
- 证书认证依然生效
- 两者可以组合使用

### Q: 普通模式和网关模式可以随时切换吗？

A: 可以。使用 `ovpn_set_mode` 切换后重启服务即可。但注意：
- 切换前建议备份配置
- 切换到网关模式需要配置远程站点
- 切换会影响路由行为

### Q: 网关模式下的 Site-to-Site 连接会自动重连吗？

A: 会。OpenVPN 具有自动重连功能，连接断开后会自动尝试重连。

---

## 📊 性能影响

### LDAP 认证
- **延迟**: 每次连接时增加 LDAP 查询延迟（通常 < 100ms）
- **资源**: 几乎无影响
- **建议**: 生产环境使用 LDAPS 并确保 LDAP 服务器高可用

### 网关模式
- **CPU**: 需要处理转发流量，建议至少 2 核
- **内存**: 根据连接数，建议至少 4GB
- **网络**: 所有流量经过网关，需要足够带宽
- **建议**: 使用高性能服务器部署在网络中心位置

---

## 🔒 安全建议

1. **LDAP 配置**:
   - ✅ 使用 LDAPS (TLS) 加密连接
   - ✅ 使用只读服务账户
   - ✅ 使用组过滤器限制访问
   - ✅ 定期轮换服务账户密码

2. **网关模式**:
   - ✅ 定期审计 Site-to-Site 连接
   - ✅ 监控异常流量
   - ✅ 使用防火墙限制访问范围
   - ✅ 定期更新证书

3. **双因素认证**:
   - ✅ 推荐使用证书 + LDAP
   - ✅ 或使用证书 + OTP
   - ✅ 监控认证失败日志

---

## 📞 获取帮助

- 📚 查看文档：`docs/` 目录
- 💬 提交问题：GitHub Issues
- 📧 联系支持：参考项目 README

---

**祝您使用愉快！** 🎉

