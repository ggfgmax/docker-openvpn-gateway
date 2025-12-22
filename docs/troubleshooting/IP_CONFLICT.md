# VPN 网段冲突问题排查

## 🐛 问题描述

**症状**：
- ✅ 网关能 ping 通远程站点内网
- ❌ 客户端无法 ping 通远程站点内网
- ✅ 客户端能连接到网关 VPN
- ✅ 路由配置正确

**根本原因**：**网段冲突**

## 🔍 问题示例

### 冲突场景

**网关 VPN 配置**：
```bash
server 192.168.255.0 255.255.255.0
# 给客户端分配：192.168.255.4 - 192.168.255.254
```

**GCP 站点连接**：
```bash
# GCP VPN 推送：
ifconfig 192.168.255.6 192.168.255.5
# 网关的 tun-gcp IP: 192.168.255.6
# GCP 对端 IP: 192.168.255.5
```

**Mac 客户端连接**：
```bash
# 网关分配给 Mac：192.168.255.6
# 和 tun-gcp 的 IP 完全一样！
```

### 导致的问题

```
Mac (192.168.255.6) → 访问 10.80.0.2
    ↓
    查路由：via 192.168.255.5
    ↓
网关收到：
    源 IP: 192.168.255.6 (Mac 的 IP)
    网关也有 192.168.255.6 (tun-gcp 的 IP)
    ↓
    路由表混乱！
    内核不知道 192.168.255.6 是 Mac 还是 tun-gcp
    ↓
    数据包丢失或路由错误 ❌
```

## ✅ 解决方案

### 方案 1：修改网关客户端网段（推荐）

使用不同的网段，避免与任何远程站点冲突：

```bash
cd /root/docker-openvpn-gateway

# 1. 停止容器
docker-compose -f docker-compose-webui.yml down

# 2. 备份 PKI 和站点配置
cp -r data/pki data/pki.backup
cp -r data/sites data/sites.backup

# 3. 删除旧配置
rm -f data/openvpn.conf data/ovpn_env.sh

# 4. 启动容器
docker-compose -f docker-compose-webui.yml up -d

# 5. 重新生成配置（使用 10.8.0.0/24）
docker exec -it openvpn-gateway ovpn_genconfig -u udp://你的服务器IP -s 10.8.0.0/24

# 6. 恢复 PKI 和站点
docker exec openvpn-gateway rm -rf /etc/openvpn/pki
docker exec openvpn-gateway cp -r /etc/openvpn/pki.backup /etc/openvpn/pki
docker exec openvpn-gateway cp -r /etc/openvpn/sites.backup/* /etc/openvpn/sites/

# 7. 添加 site-routes.conf
echo -e "\n# Site-to-Site VPN 路由配置\nconfig /etc/openvpn/site-routes.conf" >> data/openvpn.conf

# 8. 重启
docker restart openvpn-gateway

# 9. 重新下载客户端证书
# Web UI → 客户端管理 → 下载新的 .ovpn
```

### 方案 2：选择合适的网段

**推荐的客户端网段**：
- ✅ `10.8.0.0/24` - OpenVPN 常用网段
- ✅ `10.9.0.0/24` 
- ✅ `172.31.0.0/24`

**避免使用的网段**：
- ❌ `192.168.0.0/16` - 常见的内网网段
- ❌ `192.168.255.0/24` - 可能与远程站点冲突
- ❌ `10.0.0.0/16` - AWS 常用
- ❌ `172.16.0.0/16` - 阿里云等常用

## 🔍 如何检测冲突

### 检查所有 VPN 接口的 IP

```bash
# 查看所有 tun 接口
docker exec openvpn-gateway ip addr show | grep -A 3 "tun"

# 输出示例：
# tun0: inet 192.168.255.1 peer 192.168.255.2
# tun-gcp: inet 192.168.255.6 peer 192.168.255.5
# ↑ 如果网段相同，就可能有冲突
```

### 检查客户端分配的网段

```bash
docker exec openvpn-gateway cat /etc/openvpn/openvpn.conf | grep "^server"

# 如果输出是 192.168.255.0，而站点连接也用 192.168.255.x
# 就会冲突
```

### 检查已连接客户端的 IP

```bash
docker exec openvpn-gateway cat /tmp/openvpn-status.log

# 查看 Virtual Address 列
# 如果客户端 IP 和站点隧道 IP 相同，就会冲突
```

## 📊 网段规划建议

### 单个远程站点

```
网关客户端网段: 10.8.0.0/24
远程站点 VPN 网段: 192.168.255.0/24
远程站点内网: 10.80.0.0/16
✅ 完全不冲突
```

### 多个远程站点

```
网关客户端网段: 10.8.0.0/24
站点 A VPN: 192.168.1.0/24
站点 A 内网: 172.16.0.0/16

站点 B VPN: 192.168.2.0/24
站点 B 内网: 10.0.0.0/16

站点 C VPN: 192.168.3.0/24
站点 C 内网: 10.80.0.0/16

✅ 所有网段都不同
```

## ⚠️ 注意事项

### 1. 修改客户端网段后

**必须做的**：
- ✅ 重新下载所有客户端证书（.ovpn 文件会变）
- ✅ 客户端导入新的配置
- ✅ 重新连接

**不需要做的**：
- ❌ 不需要重新初始化 PKI
- ❌ 不需要重新配置站点
- ❌ 证书还是有效的

### 2. 检查清单

添加站点前，先检查：
```bash
# 1. 查看网关客户端网段
grep "^server" data/openvpn.conf

# 2. 查看要添加的站点的 VPN 网段
# 从 .ovpn 文件中查找 ifconfig 或 server 相关配置

# 3. 确保两者不冲突
```

## 💡 预防措施

### 初始化时选择合适的网段

```bash
# 使用不常见的网段
ovpn_genconfig -u udp://你的服务器IP -s 10.8.0.0/24

# 或者
ovpn_genconfig -u udp://你的服务器IP -s 172.31.0.0/24
```

### 文档化你的网段

在添加站点时记录：
```
网关客户端: 10.8.0.0/24
站点 GCP: VPN 192.168.255.0/24, 内网 10.80.0.0/16
站点 AWS: VPN 192.168.1.0/24, 内网 10.0.0.0/16
```

## 🎉 问题解决

修改客户端网段后：
- ✅ 网段不冲突
- ✅ 路由清晰
- ✅ Mac 能访问 GCP 内网
- ✅ 所有功能正常

## 📚 相关文档

- [快速启动指南](../guides/QUICK_START.md)
- [连通性排查指南](TROUBLESHOOTING_CONNECTIVITY.md)
- [站点证书配置指南](../guides/SITE_CERTIFICATE_GUIDE.md)
