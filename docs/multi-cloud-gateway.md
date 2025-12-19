# 多云网络主入口 VPN 网关配置指南

## 概述

本指南介绍如何将 docker-openvpn 配置为多云网络的主入口 VPN 网关，实现一次连接即可访问华为云、AWS、GCP 等多个云服务商的内网资源。

## 架构说明

```
                         互联网
                            |
                            |
                    [主入口 VPN 服务器]
                       (Hub Gateway)
                            |
        +-------------------+-------------------+
        |                   |                   |
   [华为云 VPN]         [AWS VPN]          [GCP VPN]
   172.16.0.0/16       10.0.0.0/16       192.168.0.0/16
        |                   |                   |
   [华为云内网]         [AWS 内网]         [GCP 内网]
```

### 工作原理

1. **客户端连接**: 用户只需连接到主入口 VPN 服务器
2. **Site-to-Site 隧道**: 主入口 VPN 服务器建立到各个云平台 VPN 的隧道连接
3. **路由转发**: 主入口 VPN 服务器将客户端流量转发到对应的云平台内网
4. **统一访问**: 客户端可以直接访问所有云平台的内网资源

## 快速开始

### 1. 初始化主入口 VPN 服务器

首先，创建并初始化主入口 VPN 服务器：

```bash
# 创建数据卷
OVPN_DATA="ovpn-gateway-data"
docker volume create --name $OVPN_DATA

# 生成配置（使用你的服务器域名或 IP）
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u udp://vpn.yourdomain.com

# 初始化 PKI
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn ovpn_initpki

# 初始化网关配置
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_setup_gateway -i
```

### 2. 添加远程云平台站点

为每个云平台添加 Site-to-Site VPN 连接配置：

#### 添加华为云站点

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
  ovpn_add_remote_site \
  -n huawei \
  -h vpn.huaweicloud.example.com \
  -p 1194 \
  -s 172.16.0.0/16
```

#### 添加 AWS 站点

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
  ovpn_add_remote_site \
  -n aws \
  -h vpn.aws.example.com \
  -p 1194 \
  -s 10.0.0.0/16
```

#### 添加 GCP 站点

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
  ovpn_add_remote_site \
  -n gcp \
  -h vpn.gcp.example.com \
  -p 1194 \
  -s 192.168.0.0/16
```

### 3. 配置站点证书

每个远程站点需要相应的客户端证书来建立连接。有两种方式：

#### 方式 1: 使用远程站点提供的证书

如果远程云平台已经为你提供了 VPN 客户端配置文件（.ovpn），你可以提取证书：

```bash
# 进入容器
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn bash

# 手动编辑站点配置文件，添加证书内容
vi /etc/openvpn/sites/huawei.conf
```

在配置文件中添加证书内容（内联格式）：

```
<ca>
-----BEGIN CERTIFICATE-----
... CA 证书内容 ...
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
... 客户端证书内容 ...
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
... 私钥内容 ...
-----END PRIVATE KEY-----
</key>

<tls-auth>
-----BEGIN OpenVPN Static key V1-----
... TLS 认证密钥内容 ...
-----END OpenVPN Static key V1-----
</tls-auth>
key-direction 1
```

#### 方式 2: 使用添加站点时指定证书文件

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
  ovpn_add_remote_site \
  -n huawei \
  -h vpn.huaweicloud.example.com \
  -p 1194 \
  -s 172.16.0.0/16 \
  -k /path/to/client.key \
  -c /path/to/client.crt \
  -a /path/to/ca.crt
```

### 4. 更新路由配置

添加完所有站点后，更新路由配置：

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_update_routes
```

### 5. 重新生成服务器配置

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u udp://vpn.yourdomain.com
```

### 6. 启动主入口 VPN 服务器

```bash
docker run -v $OVPN_DATA:/etc/openvpn -d -p 1194:1194/udp \
  --cap-add=NET_ADMIN \
  --name openvpn-gateway \
  kylemanna/openvpn
```

### 7. 生成客户端配置

为最终用户生成客户端配置文件：

```bash
# 生成客户端证书
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
  easyrsa build-client-full CLIENTNAME nopass

# 导出客户端配置
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
  ovpn_getclient CLIENTNAME > CLIENTNAME.ovpn
```

### 8. 客户端连接

客户端使用生成的 `.ovpn` 文件连接到主入口 VPN 后，即可访问所有配置的云平台内网：

```bash
# Linux/Mac
sudo openvpn --config CLIENTNAME.ovpn

# Windows
# 使用 OpenVPN GUI 导入 CLIENTNAME.ovpn
```

## 管理命令

### 查看所有站点状态

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_list_sites
```

### 查看网关状态

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_setup_gateway -s
```

### 手动启动 Site-to-Site 连接

```bash
docker exec openvpn-gateway ovpn_start_site_connections
```

### 停止 Site-to-Site 连接

```bash
docker exec openvpn-gateway ovpn_stop_site_connections
```

### 删除站点

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn bash
rm /etc/openvpn/sites/SITENAME.*
ovpn_update_routes
exit
```

## 高级配置

### 使用 TCP 协议

如果某个云平台的 VPN 使用 TCP 协议：

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
  ovpn_add_remote_site \
  -n huawei \
  -h vpn.huaweicloud.example.com \
  -p 443 \
  -P tcp \
  -s 172.16.0.0/16
```

### 配置多个网段

如果一个云平台有多个内网网段，可以添加多个站点配置，或者手动编辑配置文件添加额外的路由：

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn bash
echo "route 172.17.0.0 255.255.0.0" >> /etc/openvpn/sites/huawei.conf
```

### 自定义 iptables 规则

如果需要特殊的防火墙规则：

```bash
docker exec openvpn-gateway iptables -t nat -A POSTROUTING -s 192.168.255.0/24 -d 172.16.0.0/16 -j MASQUERADE
```

### 持久化 iptables 规则

创建启动脚本：

```bash
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn bash
cat > /etc/openvpn/custom-iptables.sh <<'EOF'
#!/bin/bash
# 自定义 iptables 规则
iptables -t nat -A POSTROUTING -s 192.168.255.0/24 -d 172.16.0.0/16 -j MASQUERADE
EOF
chmod +x /etc/openvpn/custom-iptables.sh
```

在 `ovpn_run` 中会自动执行此脚本。

## 故障排查

### 检查隧道接口

```bash
docker exec openvpn-gateway ip addr show | grep tun
```

### 检查路由表

```bash
docker exec openvpn-gateway ip route
```

### 检查 iptables 规则

```bash
docker exec openvpn-gateway iptables -t nat -L -n -v
docker exec openvpn-gateway iptables -L FORWARD -n -v
```

### 查看 OpenVPN 日志

```bash
# 主服务器日志
docker logs openvpn-gateway

# Site-to-Site 连接日志
docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
docker exec openvpn-gateway cat /var/log/openvpn-aws.log
docker exec openvpn-gateway cat /var/log/openvpn-gcp.log
```

### 测试连通性

从容器内测试到远程网段的连通性：

```bash
docker exec openvpn-gateway ping -c 3 172.16.0.1  # 华为云内网 IP
docker exec openvpn-gateway ping -c 3 10.0.0.1     # AWS 内网 IP
docker exec openvpn-gateway ping -c 3 192.168.0.1  # GCP 内网 IP
```

### 常见问题

#### 1. Site-to-Site 连接无法建立

- 检查远程 VPN 服务器是否允许客户端连接
- 确认证书和密钥配置正确
- 检查防火墙是否允许 UDP/1194 端口

#### 2. 客户端无法访问远程内网

- 确认路由配置已更新：`ovpn_update_routes`
- 检查 IP 转发是否启用：`sysctl net.ipv4.ip_forward`
- 检查 iptables 转发规则：`iptables -L FORWARD -n -v`

#### 3. 连接频繁断开

- 调整 keepalive 参数
- 检查网络质量
- 考虑使用 TCP 协议

## 安全建议

1. **使用强密码保护 CA 密钥**: 在 `ovpn_initpki` 时设置强密码
2. **定期更新证书**: 证书过期前及时更新
3. **启用客户端证书吊销**: 使用 CRL 管理客户端访问权限
4. **限制客户端权限**: 使用防火墙规则限制客户端只能访问必要的资源
5. **监控日志**: 定期检查连接日志，发现异常行为
6. **备份配置**: 定期备份 `/etc/openvpn` 目录

## 性能优化

1. **使用高性能服务器**: 主入口 VPN 服务器承担所有流量转发，需要足够的 CPU 和网络带宽
2. **选择合适的地理位置**: 将主入口 VPN 服务器部署在离各云平台较近的位置
3. **启用压缩**: 对于高延迟网络，可以启用 `comp-lzo`
4. **调整 MTU**: 根据网络环境调整 MTU 值避免分片

## 示例配置文件

### 完整的站点配置示例 (sites/huawei.conf)

```
# Site-to-Site VPN 配置: huawei
client
dev tun-huawei
dev-type tun
proto udp
remote vpn.huaweicloud.example.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
verb 3

# 路由配置
route 172.16.0.0 255.255.0.0
route-nopull

# 日志
log /var/log/openvpn-huawei.log
status /var/log/openvpn-huawei-status.log

# 证书和密钥（内联格式）
<ca>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
</key>

<tls-auth>
-----BEGIN OpenVPN Static key V1-----
...
-----END OpenVPN Static key V1-----
</tls-auth>
key-direction 1
```

## 总结

通过本指南，你可以将 docker-openvpn 配置为一个功能强大的多云网络主入口 VPN 网关。客户端只需连接一次，即可访问华为云、AWS、GCP 等多个云服务商的内网资源，大大简化了多云环境下的网络访问管理。

