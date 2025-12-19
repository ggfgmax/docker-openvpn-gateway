# 多云网络主入口 VPN 网关

## 概述

这是一个基于 docker-openvpn 的增强版本，支持**多云网络主入口 VPN 网关**功能。通过这个功能，您可以：

- ✅ 只需连接一个 VPN，即可访问华为云、AWS、GCP 等多个云平台的内网
- ✅ 简化多云环境下的网络访问管理
- ✅ 支持 Site-to-Site VPN 隧道自动管理
- ✅ 自动配置路由和流量转发

## 🌟 Web 管理界面（推荐）

### 最简单的方式：使用 Web 管理界面

无需命令行，通过浏览器就能完成所有配置！

```bash
# 1. 构建镜像
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
# 默认密码: openvpn（请务必修改！）
```

**Web 界面功能**:
- ✅ 图形化配置，无需命令行
- ✅ 一键切换运行模式
- ✅ 可视化管理站点和客户端
- ✅ 实时状态监控
- ✅ 适合小白用户

详细说明: [Web 管理界面快速开始](WEBUI-QUICKSTART.md) | [Web UI 完整文档](docs/webui.md)

---

## 快速开始（命令行方式）

### 1. 使用快速配置脚本

```bash
# 下载快速配置脚本
docker run -v $PWD:/tmp --rm kylemanna/openvpn \
    cp /usr/share/doc/openvpn/examples/multi-cloud-setup.sh /tmp/

# 编辑脚本中的配置变量
vim multi-cloud-setup.sh

# 运行配置脚本
bash multi-cloud-setup.sh
```

### 2. 手动配置

```bash
# 1. 创建数据卷
OVPN_DATA="ovpn-gateway-data"
docker volume create --name $OVPN_DATA

# 2. 生成配置
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u udp://vpn.yourdomain.com

# 3. 初始化 PKI
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn ovpn_initpki

# 4. 初始化网关
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_setup_gateway -i

# 5. 添加远程云平台站点
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_add_remote_site \
    -n huawei \
    -h vpn.huaweicloud.example.com \
    -p 1194 \
    -s 172.16.0.0/16

docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_add_remote_site \
    -n aws \
    -h vpn.aws.example.com \
    -p 1194 \
    -s 10.0.0.0/16

docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_add_remote_site \
    -n gcp \
    -h vpn.gcp.example.com \
    -p 1194 \
    -s 192.168.0.0/16

# 6. 配置站点证书（重要！）
# 为每个站点编辑配置文件，添加证书和密钥
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn bash
# 在容器内编辑 /etc/openvpn/sites/huawei.conf 等文件

# 7. 更新路由配置
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_update_routes

# 8. 重新生成服务器配置
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u udp://vpn.yourdomain.com

# 9. 启动主入口 VPN 服务器
docker run -v $OVPN_DATA:/etc/openvpn -d -p 1194:1194/udp \
    --cap-add=NET_ADMIN --name openvpn-gateway kylemanna/openvpn

# 10. 生成客户端配置
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
    easyrsa build-client-full CLIENTNAME nopass

docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_getclient CLIENTNAME > CLIENTNAME.ovpn
```

## 架构图

```
                         互联网
                            |
                    [主入口 VPN 服务器]
                       (docker-openvpn)
                            |
        +-------------------+-------------------+
        |                   |                   |
   [华为云 VPN]         [AWS VPN]          [GCP VPN]
   172.16.0.0/16       10.0.0.0/16       192.168.0.0/16
```

## 新增管理命令

### 网关管理

| 命令 | 说明 |
|------|------|
| `ovpn_set_mode` | 切换 VPN 运行模式（普通/网关） |
| `ovpn_setup_gateway` | 初始化和管理网关配置 |
| `ovpn_add_remote_site` | 添加远程云平台站点 |
| `ovpn_list_sites` | 列出所有站点及状态 |
| `ovpn_update_routes` | 更新路由配置 |
| `ovpn_start_site_connections` | 启动 Site-to-Site 连接 |
| `ovpn_stop_site_connections` | 停止 Site-to-Site 连接 |

### LDAP 认证

| 命令 | 说明 |
|------|------|
| `ovpn_config_ldap` | 配置 LDAP 认证 |

## 命令示例

### 查看所有站点状态

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_list_sites
```

### 查看网关状态

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_setup_gateway -s
```

### 测试连通性

```bash
# 下载测试脚本
docker run -v $PWD:/tmp --rm kylemanna/openvpn \
    cp /usr/share/doc/openvpn/examples/test-connectivity.sh /tmp/

# 运行测试
bash test-connectivity.sh openvpn-gateway
```

### 查看日志

```bash
# 主服务器日志
docker logs openvpn-gateway

# Site-to-Site 连接日志
docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
docker exec openvpn-gateway cat /var/log/openvpn-aws.log
docker exec openvpn-gateway cat /var/log/openvpn-gcp.log
```

## 详细文档

完整的配置指南、故障排查和高级配置，请参阅：

- [多云网络主入口 VPN 网关完整指南](docs/multi-cloud-gateway.md)

## 运行模式

### 模式切换

支持两种运行模式，可自由切换：

**普通 VPN 模式**:
```bash
docker exec openvpn-container ovpn_set_mode normal
```

**网关模式**:
```bash
docker exec openvpn-container ovpn_set_mode gateway
```

查看当前模式:
```bash
docker exec openvpn-container ovpn_set_mode
```

详细说明请参阅：[模式切换指南](docs/mode-switching.md)

## 认证方式

### LDAP 认证

支持使用企业 LDAP/AD 进行用户认证：

```bash
# 配置 LDAP
docker run -v ovpn-data:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_config_ldap \
    -h ldap.company.com \
    -b "dc=company,dc=com" \
    -D "cn=admin,dc=company,dc=com" \
    -w "password"

# 启用 LDAP 认证
docker run -v ovpn-data:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u udp://vpn.company.com -2
```

详细说明请参阅：[LDAP 认证指南](docs/ldap.md)

## 核心特性

### 自动路由管理

- 自动从站点配置中提取远程网段
- 自动推送路由到客户端
- 支持多个网段配置

### 流量转发

- 自动配置 iptables NAT 规则
- 支持不同 VPN 隧道之间的流量转发
- 启用 IP 转发

### Site-to-Site 连接管理

- 支持 UDP/TCP 协议
- 自动启动和管理多个 Site-to-Site 连接
- 独立的日志和状态监控

### 灵活的证书管理

- 支持内联证书格式
- 支持外部证书文件
- 兼容标准 OpenVPN 客户端配置

## 适用场景

1. **多云环境统一访问**: 在华为云、AWS、GCP 等多个云平台部署资源，需要统一的访问入口
2. **混合云架构**: 连接公有云和私有云网络
3. **分支机构互联**: 连接多个分支机构的 VPN 网络
4. **开发测试环境**: 为开发人员提供一次连接访问所有环境的能力

## 安全建议

- ✅ 使用强密码保护 CA 密钥
- ✅ 定期更新证书
- ✅ 启用客户端证书吊销列表（CRL）
- ✅ 使用防火墙规则限制访问
- ✅ 定期检查连接日志
- ✅ 备份配置和证书

## 性能建议

- 选择高性能服务器（主入口 VPN 承担所有流量转发）
- 选择合适的地理位置（接近各云平台）
- 根据网络环境调整 MTU
- 监控带宽使用情况

## 故障排查

常见问题和解决方法请参阅：[多云网络主入口 VPN 网关完整指南](docs/multi-cloud-gateway.md#故障排查)

## 示例和测试

在 `examples/` 目录下提供了以下示例脚本：

- `multi-cloud-setup.sh`: 快速配置脚本
- `test-connectivity.sh`: 连通性测试脚本

## 贡献和反馈

如果您有任何问题、建议或想要贡献代码，请提交 Issue 或 Pull Request。

## 许可证

与原项目相同，采用 MIT 许可证。

---

**原项目**: [kylemanna/docker-openvpn](https://github.com/kylemanna/docker-openvpn)

