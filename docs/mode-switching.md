# VPN 模式切换指南

## 概述

本项目支持两种运行模式：

1. **普通 VPN 模式** (Normal VPN Mode) - 标准的 OpenVPN 服务器
2. **网关模式** (Gateway Mode) - 多云网络主入口网关

可以通过 `ovpn_set_mode` 命令在两种模式之间自由切换。

## 模式对比

| 特性 | 普通 VPN 模式 | 网关模式 |
|------|--------------|----------|
| 基本 VPN 功能 | ✅ | ✅ |
| 客户端访问服务器网络 | ✅ | ✅ |
| Site-to-Site VPN | ❌ | ✅ |
| 多云网络打通 | ❌ | ✅ |
| 自动路由管理 | 基础 | 高级 |
| IP 转发 | 可选 | 自动启用 |
| iptables 规则 | 基础 | 高级 |
| 资源消耗 | 低 | 中等 |
| 适用场景 | 标准远程访问 | 多云环境统一访问 |

## 查看当前模式

```bash
docker exec openvpn-container ovpn_set_mode
```

输出示例：
```
当前模式: 普通 VPN 模式 (Normal VPN Mode)
LDAP 认证: 未启用

提示: 使用 'ovpn_set_mode normal' 或 'ovpn_set_mode gateway' 切换模式
```

## 切换到普通 VPN 模式

### 使用命令切换

```bash
docker exec openvpn-container ovpn_set_mode normal
```

### 使用环境变量

在 Docker 启动时设置：

```bash
docker run -v ovpn-data:/etc/openvpn -d -p 1194:1194/udp \
    --cap-add=NET_ADMIN \
    -e GATEWAY_MODE=0 \
    --name openvpn kylemanna/openvpn
```

或在 docker-compose.yml 中：

```yaml
services:
  openvpn:
    environment:
      - GATEWAY_MODE=0
```

### 普通模式配置

```bash
# 1. 切换到普通模式
docker exec openvpn-container ovpn_set_mode normal

# 2. 重启服务
docker restart openvpn-container
```

### 普通模式特性

- 标准的 OpenVPN 功能
- 客户端连接后可访问服务器所在网络
- 不启动 Site-to-Site VPN 连接
- 较低的资源消耗
- 适合简单的远程访问需求

## 切换到网关模式

### 使用命令切换

```bash
docker exec openvpn-container ovpn_set_mode gateway
```

### 使用环境变量

```bash
docker run -v ovpn-data:/etc/openvpn -d -p 1194:1194/udp \
    --cap-add=NET_ADMIN \
    -e GATEWAY_MODE=1 \
    --name openvpn-gateway kylemanna/openvpn
```

或在 docker-compose.yml 中：

```yaml
services:
  openvpn-gateway:
    environment:
      - GATEWAY_MODE=1
```

### 网关模式完整配置

```bash
# 1. 切换到网关模式
docker exec openvpn-container ovpn_set_mode gateway

# 2. 初始化网关（如果还没有初始化）
docker exec openvpn-container ovpn_setup_gateway -i

# 3. 添加远程站点
docker exec openvpn-container ovpn_add_remote_site \
    -n huawei \
    -h vpn.huaweicloud.example.com \
    -p 1194 \
    -s 172.16.0.0/16

docker exec openvpn-container ovpn_add_remote_site \
    -n aws \
    -h vpn.aws.example.com \
    -p 1194 \
    -s 10.0.0.0/16

# 4. 配置站点证书（重要！）
docker exec -it openvpn-container bash
# 在容器内编辑 /etc/openvpn/sites/huawei.conf 等文件
# 添加证书内容后退出

# 5. 更新路由
docker exec openvpn-container ovpn_update_routes

# 6. 重新生成配置
docker exec openvpn-container ovpn_genconfig -u udp://vpn.yourdomain.com

# 7. 重启服务
docker restart openvpn-container
```

### 网关模式特性

- 所有普通 VPN 功能
- 自动启动 Site-to-Site VPN 连接
- 自动配置路由转发
- 自动配置 iptables 规则
- 客户端可访问所有配置的远程网络
- 适合多云环境统一访问

## 模式切换最佳实践

### 1. 计划切换

在切换模式前：
- ✅ 备份当前配置
- ✅ 通知用户即将进行维护
- ✅ 选择低峰时段

### 2. 切换步骤

#### 从普通模式切换到网关模式

```bash
# 1. 备份配置
docker run -v ovpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar czf /backup/openvpn-backup-$(date +%Y%m%d).tar.gz /etc/openvpn

# 2. 切换模式
docker exec openvpn-container ovpn_set_mode gateway

# 3. 配置网关功能
docker exec openvpn-container ovpn_setup_gateway -i

# 4. 添加远程站点并配置
# （参考上面的网关模式完整配置）

# 5. 重启服务
docker restart openvpn-container

# 6. 验证
docker exec openvpn-container ovpn_set_mode
docker exec openvpn-container ovpn_list_sites
docker exec openvpn-container ovpn_setup_gateway -s
```

#### 从网关模式切换到普通模式

```bash
# 1. 备份配置
docker run -v ovpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar czf /backup/openvpn-backup-$(date +%Y%m%d).tar.gz /etc/openvpn

# 2. 停止 Site-to-Site 连接
docker exec openvpn-container ovpn_stop_site_connections

# 3. 切换模式
docker exec openvpn-container ovpn_set_mode normal

# 4. 重启服务
docker restart openvpn-container

# 5. 验证
docker exec openvpn-container ovpn_set_mode
```

### 3. 验证切换

切换后检查：

```bash
# 检查模式
docker exec openvpn-container ovpn_set_mode

# 检查服务状态
docker logs openvpn-container

# 检查网络接口
docker exec openvpn-container ip addr

# 检查路由
docker exec openvpn-container ip route

# 检查 iptables（仅网关模式）
docker exec openvpn-container iptables -L -n -v
docker exec openvpn-container iptables -t nat -L -n -v
```

## Docker Compose 配置示例

### 支持模式切换的配置

**docker-compose.yml**:

```yaml
version: "3.8"

services:
  openvpn:
    build: .
    image: openvpn-gateway:latest
    container_name: openvpn
    ports:
      - "1194:1194/udp"
    cap_add:
      - NET_ADMIN
    volumes:
      - openvpn-data:/etc/openvpn
    restart: unless-stopped
    environment:
      # 模式设置: 0=普通VPN, 1=网关模式
      - GATEWAY_MODE=${GATEWAY_MODE:-0}
      # LDAP 设置: 0=禁用, 1=启用
      - LDAP_ENABLED=${LDAP_ENABLED:-0}
      # 调试模式
      - DEBUG=${DEBUG:-0}
    networks:
      - vpn-network

volumes:
  openvpn-data:
    driver: local

networks:
  vpn-network:
    driver: bridge
```

**.env 文件**:

```bash
# 普通 VPN 模式
GATEWAY_MODE=0
LDAP_ENABLED=0
DEBUG=0
```

或

```bash
# 网关模式
GATEWAY_MODE=1
LDAP_ENABLED=0
DEBUG=0
```

### 使用不同配置启动

**启动普通 VPN**:
```bash
# 使用 .env 文件
echo "GATEWAY_MODE=0" > .env
docker-compose up -d

# 或者直接指定
GATEWAY_MODE=0 docker-compose up -d
```

**启动网关模式**:
```bash
# 使用 .env 文件
echo "GATEWAY_MODE=1" > .env
docker-compose up -d

# 或者直接指定
GATEWAY_MODE=1 docker-compose up -d
```

## 环境变量参考

| 变量名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `GATEWAY_MODE` | VPN 运行模式 | `0` (普通), `1` (网关) | `0` |
| `LDAP_ENABLED` | LDAP 认证 | `0` (禁用), `1` (启用) | `0` |
| `DEBUG` | 调试模式 | `0` (禁用), `1` (启用) | `0` |

## 故障排查

### 模式切换后服务无法启动

1. **查看日志**:
```bash
docker logs openvpn-container
```

2. **检查配置文件**:
```bash
docker exec openvpn-container cat /etc/openvpn/ovpn_env.sh
docker exec openvpn-container cat /etc/openvpn/openvpn.conf
```

3. **恢复备份**:
```bash
docker run -v ovpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar xzf /backup/openvpn-backup-20241219.tar.gz -C /
docker restart openvpn-container
```

### 网关模式下无法访问远程网络

1. **检查模式设置**:
```bash
docker exec openvpn-container ovpn_set_mode
```

2. **检查站点连接**:
```bash
docker exec openvpn-container ovpn_list_sites
```

3. **检查路由**:
```bash
docker exec openvpn-container ip route
```

4. **检查 Site-to-Site 日志**:
```bash
docker exec openvpn-container cat /var/log/openvpn-huawei.log
```

### 普通模式下 Site-to-Site 功能仍在运行

这是正常的，切换到普通模式后，Site-to-Site 连接不会自动启动，但已存在的配置文件不会被删除。

如需清理：
```bash
docker exec openvpn-container ovpn_stop_site_connections
```

## 最佳实践

1. **明确需求**: 根据实际需求选择合适的模式
2. **测试环境**: 先在测试环境验证模式切换
3. **定期备份**: 切换前必须备份配置
4. **文档记录**: 记录切换原因和时间
5. **监控验证**: 切换后监控服务状态
6. **用户通知**: 提前通知用户可能的影响

## 总结

- 使用 `ovpn_set_mode` 命令可以轻松切换模式
- 使用环境变量 `GATEWAY_MODE` 控制默认模式
- 切换前务必备份配置
- 网关模式需要额外配置 Site-to-Site 站点
- 普通模式适合简单场景，网关模式适合多云环境

