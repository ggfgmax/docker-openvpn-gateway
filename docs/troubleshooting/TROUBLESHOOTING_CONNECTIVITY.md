# Site-to-Site VPN 连通性排查指南

## 🎯 问题：客户端无法访问远程站点内网

### 症状
- ✅ 网关能 ping 通远程站点内网
- ❌ 客户端（Mac/PC）无法 ping 通远程站点内网

## 🔍 排查步骤

### 步骤 1：检查客户端是否连接到网关

**在客户端（Mac）上执行：**
```bash
# 检查 VPN 接口
ifconfig | grep -A 5 utun
# 或
ifconfig | grep -A 5 tun

# 检查是否获得了 VPN IP
# 应该看到类似：192.168.255.6
```

**如果没有 tun/utun 接口：**
→ 客户端没有连接到 VPN
→ 需要生成客户端证书并连接

### 步骤 2：检查客户端路由表

**在客户端（Mac）上执行：**
```bash
# 查看路由表
netstat -rn | grep 10.80

# 应该看到类似：
# 10.80/20         192.168.255.5      UGSc     utun3
```

**如果没有这条路由：**
→ 网关没有推送路由给客户端
→ 需要检查网关配置

### 步骤 3：检查网关路由推送配置

**在网关服务器上执行：**
```bash
# 查看主配置是否包含 site-routes.conf
docker exec openvpn-gateway grep "site-routes" /etc/openvpn/openvpn.conf

# 应该看到：
# config /etc/openvpn/site-routes.conf

# 查看路由推送配置
docker exec openvpn-gateway cat /etc/openvpn/site-routes.conf

# 应该看到：
# push "route 10.80.0.0 255.255.240.0"
```

**如果 site-routes.conf 是空的或没有 push：**
```bash
# 更新路由配置
docker exec openvpn-gateway ovpn_update_routes

# 重启主服务器
docker restart openvpn-gateway
```

### 步骤 4：检查网关 iptables 转发规则

**在网关服务器上执行：**
```bash
# 查看 FORWARD 链规则
docker exec openvpn-gateway iptables -L FORWARD -n -v

# 应该包含：
# Chain FORWARD (policy ACCEPT)
# ACCEPT     all  --  tun+   tun+     anywhere     anywhere
# ACCEPT     all  --  tun+   *        anywhere     anywhere

# 查看 NAT 规则
docker exec openvpn-gateway iptables -t nat -L POSTROUTING -n -v

# 应该包含到 10.80.0.0/20 的 MASQUERADE 规则
```

### 步骤 5：测试从网关到客户端的连通性

**在网关服务器上执行：**
```bash
# 查看已连接的客户端
docker exec openvpn-gateway cat /tmp/openvpn-status.log

# 应该看到客户端的信息：
# Common Name,Real Address,Bytes Received,Bytes Sent,Connected Since
# lichuan-mac,你的Mac公网IP:端口,xxx,xxx,日期时间

# 尝试 ping 客户端
docker exec openvpn-gateway ping -c 2 192.168.255.6
# (客户端的 VPN IP)
```

### 步骤 6：抓包分析

**在网关上抓包：**
```bash
# 终端1：抓包监听
docker exec openvpn-gateway tcpdump -i tun0 -n host 192.168.255.6
# (监听来自客户端的流量)

# 终端2：在 Mac 上 ping
ping 10.80.0.2

# 观察抓包输出，看是否有 ICMP 包经过
```

## ✅ 解决方案

### 方案 1：重启主 OpenVPN 服务器（最常见）

很多时候，site-routes.conf 更新后需要重启主服务器才能推送新路由：

```bash
# 重启网关容器
docker restart openvpn-gateway

# 等待启动
sleep 10

# 在 Mac 上断开并重新连接 VPN
# Tunnelblick: 断开 → 连接

# 重新连接后检查路由
netstat -rn | grep 10.80

# 测试 ping
ping 10.80.0.2
```

### 方案 2：检查 openvpn.conf 是否包含 site-routes.conf

```bash
# 查看主配置
docker exec openvpn-gateway cat /etc/openvpn/openvpn.conf | grep config

# 如果没有 "config /etc/openvpn/site-routes.conf"
# 需要手动添加：
docker exec openvpn-gateway bash << 'EOF'
if ! grep -q "site-routes.conf" /etc/openvpn/openvpn.conf; then
    echo "" >> /etc/openvpn/openvpn.conf
    echo "# Site-to-Site VPN 路由" >> /etc/openvpn/openvpn.conf
    echo "config /etc/openvpn/site-routes.conf" >> /etc/openvpn/openvpn.conf
fi
EOF

# 重启
docker restart openvpn-gateway
```

### 方案 3：手动在 Mac 上添加路由

如果网关没有推送路由，可以在 Mac 上手动添加：

```bash
# 在 Mac 上执行（需要 root 权限）
sudo route add -net 10.80.0.0/20 192.168.255.5

# 测试
ping 10.80.0.2
```

## 🎯 完整测试流程

```bash
# === 在网关服务器上 ===

# 1. 确保 site-routes.conf 包含推送路由
docker exec openvpn-gateway cat /etc/openvpn/site-routes.conf
# 必须包含：push "route 10.80.0.0 255.255.240.0"

# 2. 确保主配置包含 site-routes.conf
docker exec openvpn-gateway grep site-routes /etc/openvpn/openvpn.conf
# 必须有：config /etc/openvpn/site-routes.conf

# 3. 重启网关
docker restart openvpn-gateway
sleep 10

# === 在 Mac 上 ===

# 4. 断开 VPN
# Tunnelblick: 断开连接

# 5. 重新连接 VPN
# Tunnelblick: 连接

# 6. 检查路由
netstat -rn | grep 10.80
# 必须有：10.80/20

# 7. 测试
ping 10.80.0.2
```

## 🔍 常见问题

### Q1: 网关能通，客户端不通
**原因**：网关没有推送路由给客户端  
**解决**：检查 site-routes.conf 并重启网关

### Q2: 路由存在但无法访问
**原因**：
- GCP 防火墙阻止
- GCP VPC 没有配置返回路由
- 网关 iptables 没有配置 MASQUERADE

**检查 NAT 规则**：
```bash
docker exec openvpn-gateway iptables -t nat -L POSTROUTING -n -v | grep 10.80
```

如果没有 NAT 规则，添加：
```bash
docker exec openvpn-gateway iptables -t nat -A POSTROUTING -d 10.80.0.0/20 -j MASQUERADE
```

### Q3: VPN 连接成功但没有推送路由
**原因**：客户端配置中设置了 `route-nopull`  
**解决**：检查客户端的 .ovpn 文件，删除或注释掉 `route-nopull` 行

### Q4: 部分 IP 能通，部分不通
**原因**：GCP 内网防火墙或安全组规则  
**解决**：在 GCP 中配置防火墙规则，允许来自 VPN 网段的流量

## 💡 快速诊断

在 Mac 上连接 VPN 后执行：

```bash
# 1. 检查 VPN 接口
ifconfig | grep utun -A 3

# 2. 检查 VPN IP
# 应该是 192.168.255.x

# 3. 检查默认网关
netstat -rn | grep default

# 4. 检查是否收到了推送路由
netstat -rn | grep -E "10.80|192.168.255"

# 5. 测试连接
ping 192.168.255.1  # ping 网关
ping 10.80.0.2      # ping GCP 内网
```

## 📚 相关文档

- [快速启动指南](QUICK_START.md)
- [站点证书配置指南](SITE_CERTIFICATE_GUIDE.md)
