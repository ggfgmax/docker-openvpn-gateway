# 删除站点行为说明

## 🎯 删除站点后会发生什么？

### ✅ 自动完成的操作

1. **删除站点文件**
   - `gcp.conf` - 站点配置
   - `gcp.info` - 站点信息
   - `gcp.key` - 客户端密钥（如果有）
   - `gcp.crt` - 客户端证书（如果有）
   - `gcp-ca.crt` - CA 证书（如果有）

2. **停止站点连接进程**
   - 查找并停止 `openvpn --config gcp.conf` 进程
   - 删除 PID 文件
   - 关闭 tun-gcp 隧道接口

3. **更新路由配置**
   - 重新生成 `site-routes.conf`
   - 只包含剩余站点的路由
   - 已删除站点的路由被移除

### ⚠️ 需要手动操作

**重要：路由配置已更新，但需要重启主 OpenVPN 服务器才能生效！**

```bash
# 在宿主机上执行
docker restart openvpn-gateway
```

**为什么需要重启？**
- OpenVPN 主服务器在启动时读取配置
- 通过 `config` 指令引用的外部文件不会被热重载
- 已连接的客户端使用的是连接时推送的路由
- 必须重启服务器并让客户端重新连接

## 📋 完整的删除流程

### 在 Web UI 中

1. 切换到"站点管理"标签
2. 找到要删除的站点
3. 点击"删除"按钮
4. 确认删除
5. 等待成功消息

### 成功消息示例

```
✅ 站点 gcp 删除成功！

已完成操作：
• 删除站点文件: gcp.conf, gcp.info
• 停止站点连接进程
• 更新路由配置（已从 site-routes.conf 中移除）

⚠️ 重要：需要重启服务使配置生效
在服务器上执行: docker restart openvpn-gateway

💡 提示：
• 主 OpenVPN 服务器需要重启才能应用新路由
• 客户端需要重新连接
• 已连接的客户端不会自动更新路由
```

### 在服务器上

```bash
# 重启容器
docker restart openvpn-gateway

# 等待启动
sleep 10

# 验证站点已删除
docker exec openvpn-gateway ls -la /etc/openvpn/sites/

# 验证路由已更新
docker exec openvpn-gateway cat /etc/openvpn/site-routes.conf

# 验证主服务器启动成功
docker logs openvpn-gateway | grep "Initialization Sequence Completed"
```

### 客户端重新连接

在客户端（Mac/Windows）：
1. 断开 VPN 连接
2. 重新连接
3. 检查路由表（已删除站点的路由应该消失）

## 🔍 验证删除效果

### 1. 文件已删除
```bash
docker exec openvpn-gateway ls /etc/openvpn/sites/gcp.*
# 应该显示: No such file or directory
```

### 2. 进程已停止
```bash
docker exec openvpn-gateway ps aux | grep gcp
# 应该没有 gcp 相关进程
```

### 3. 隧道接口已关闭
```bash
docker exec openvpn-gateway ip link show | grep tun-gcp
# 应该没有 tun-gcp 接口（重启后）
```

### 4. 路由配置已更新
```bash
docker exec openvpn-gateway cat /etc/openvpn/site-routes.conf
# 应该不包含 gcp 的路由
```

### 5. 客户端路由已移除
```bash
# 在 Mac 上（重新连接后）
netstat -rn | grep 10.80
# 应该没有 10.80 的路由了
```

## 📊 对比：删除前 vs 删除后

### 删除前
```bash
# 服务器
docker exec openvpn-gateway ls /etc/openvpn/sites/
# gcp.conf  gcp.info

docker exec openvpn-gateway cat /etc/openvpn/site-routes.conf
# push "route 10.80.0.0 255.255.240.0"

# Mac 路由表
netstat -rn | grep 10.80
# 10.80/20         192.168.255.5      UGSc     utun5
```

### 删除后（重启后）
```bash
# 服务器
docker exec openvpn-gateway ls /etc/openvpn/sites/
# (空的或只有其他站点)

docker exec openvpn-gateway cat /etc/openvpn/site-routes.conf
# (空的或只有其他站点的路由)

# Mac 路由表（重新连接后）
netstat -rn | grep 10.80
# (没有输出)
```

## 💡 批量删除站点

如果需要删除所有站点：

```bash
# 方式 1：在 Web UI 中逐个删除

# 方式 2：在服务器上批量删除
docker exec openvpn-gateway bash << 'EOF'
# 停止所有站点连接
pkill -f "/etc/openvpn/sites/"

# 删除所有站点配置
rm -rf /etc/openvpn/sites/*
rm -f /etc/openvpn/site-pids/*

# 清空路由配置
cat > /etc/openvpn/site-routes.conf << 'ROUTESEOF'
# Site-to-Site VPN 路由配置
# 自动生成
ROUTESEOF

EOF

# 重启
docker restart openvpn-gateway
```

## 🔄 添加新站点替换已删除的站点

删除站点后，可以立即添加新站点：

1. **不需要重启**即可在 Web UI 中添加新站点
2. 添加完成后，**一起重启**即可

例如：
- 删除 gcp
- 添加 aws
- 添加 aliyun
- 一次重启，所有变更生效

## ⚠️ 注意事项

### 1. 删除站点不会自动断开客户端

已连接的客户端：
- 仍然连接到主服务器
- 但访问已删除站点的网络会失败
- 需要客户端重新连接才能更新路由

### 2. 删除操作不可恢复

删除前建议备份：
```bash
# 备份站点配置
docker exec openvpn-gateway tar czf /tmp/gcp-backup.tar.gz /etc/openvpn/sites/gcp.*
docker cp openvpn-gateway:/tmp/gcp-backup.tar.gz ./gcp-backup.tar.gz
```

恢复：
```bash
# 恢复站点配置
docker cp gcp-backup.tar.gz openvpn-gateway:/tmp/
docker exec openvpn-gateway tar xzf /tmp/gcp-backup.tar.gz -C /
docker exec openvpn-gateway ovpn_update_routes
docker restart openvpn-gateway
```

### 3. 建议在维护窗口操作

删除站点需要重启服务：
- 会短暂中断所有客户端连接（几秒钟）
- 建议在低峰期或维护窗口操作
- 提前通知用户

## 📚 相关文档

- [站点证书配置指南](SITE_CERTIFICATE_GUIDE.md)
- [连通性排查指南](TROUBLESHOOTING_CONNECTIVITY.md)
- [快速启动指南](QUICK_START.md)
