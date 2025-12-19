# 故障排查指南

## 🔍 快速诊断

### 检查服务状态

```bash
# 检查容器是否运行
docker ps | grep openvpn

# 查看日志
docker logs openvpn-gateway

# 检查端口映射
docker port openvpn-gateway

# 查看网关状态
docker exec openvpn-gateway ovpn_setup_gateway -s
```

## 🚫 连接问题

### 客户端无法连接

**症状**: 客户端一直显示"正在连接..."

**排查步骤**:

1. **检查服务器防火墙**
   ```bash
   # 检查防火墙状态
   sudo ufw status
   
   # 开放 UDP 1194 端口
   sudo ufw allow 1194/udp
   ```

2. **检查容器状态**
   ```bash
   docker ps | grep openvpn
   # 如果没有输出，容器未运行
   
   docker logs openvpn-gateway
   # 查看启动错误
   ```

3. **测试端口连通性**
   ```bash
   # 从外部测试
   nc -u -v 服务器IP 1194
   ```

4. **检查云服务商安全组**
   - AWS: Security Groups
   - 华为云: 安全组规则
   - GCP: Firewall Rules
   
   确保允许 UDP 1194 端口

### 连接成功但无法访问网络

**症状**: VPN 已连接，但无法访问内网或互联网

**排查步骤**:

1. **检查路由**
   ```bash
   # 客户端查看路由
   # Windows
   route print
   
   # Linux/Mac
   netstat -rn
   ```

2. **检查 DNS**
   ```bash
   # 测试 DNS 解析
   nslookup google.com
   
   # 检查 DNS 配置
   # Linux/Mac
   cat /etc/resolv.conf
   ```

3. **检查服务器 NAT**
   ```bash
   docker exec openvpn-gateway iptables -t nat -L -n -v
   # 应该看到 MASQUERADE 规则
   ```

4. **检查 IP 转发**
   ```bash
   docker exec openvpn-gateway sysctl net.ipv4.ip_forward
   # 应该返回 1
   ```

## 🌐 Web UI 问题

### 无法访问 Web UI

**症状**: 浏览器无法打开 http://服务器IP:8080

**排查步骤**:

1. **检查容器和端口**
   ```bash
   docker ps | grep openvpn
   docker port openvpn-gateway
   # 应该看到 8080/tcp -> 0.0.0.0:8080
   ```

2. **检查防火墙**
   ```bash
   sudo ufw status | grep 8080
   # 如果被阻止，开放端口
   sudo ufw allow 8080/tcp
   ```

3. **查看 Web UI 日志**
   ```bash
   docker logs openvpn-gateway | grep Flask
   docker logs openvpn-gateway | grep 8080
   ```

4. **测试本地访问**
   ```bash
   docker exec openvpn-gateway curl -I http://localhost:8080
   ```

### 认证失败

**症状**: 输入用户名密码后提示认证失败

**排查步骤**:

1. **检查环境变量**
   ```bash
   docker exec openvpn-gateway env | grep WEBUI
   ```

2. **确认密码正确**
   - 检查 `.env` 文件或 docker-compose.yml
   - 注意特殊字符需要转义

3. **重置密码**
   ```bash
   # 停止容器
   docker-compose -f docker-compose-webui.yml down
   
   # 修改 .env 文件
   vim .env
   # WEBUI_PASSWORD=new-password
   
   # 重新启动
   docker-compose -f docker-compose-webui.yml up -d
   ```

## 🏢 多云网络问题

### 站点连接失败

**症状**: 站点状态显示"未运行"或"已停止"

**排查步骤**:

1. **检查站点配置**
   ```bash
   docker exec openvpn-gateway cat /etc/openvpn/sites/huawei.conf
   ```

2. **检查证书配置**
   ```bash
   # 确保包含 <ca>, <cert>, <key>
   docker exec openvpn-gateway grep -A 5 "<ca>" /etc/openvpn/sites/huawei.conf
   ```

3. **查看站点日志**
   ```bash
   docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
   ```

4. **测试远程主机连通性**
   ```bash
   docker exec openvpn-gateway ping -c 3 vpn.huaweicloud.com
   ```

5. **手动测试连接**
   ```bash
   docker exec openvpn-gateway openvpn --config /etc/openvpn/sites/huawei.conf
   # 查看错误信息
   ```

### 无法访问远程网段

**症状**: 站点已连接，但客户端无法访问远程内网

**排查步骤**:

1. **检查是否在网关模式**
   ```bash
   docker exec openvpn-gateway ovpn_set_mode
   ```

2. **检查路由配置**
   ```bash
   docker exec openvpn-gateway cat /etc/openvpn/site-routes.conf
   docker exec openvpn-gateway ip route
   ```

3. **更新路由**
   ```bash
   docker exec openvpn-gateway ovpn_update_routes
   docker restart openvpn-gateway
   ```

4. **检查转发规则**
   ```bash
   docker exec openvpn-gateway iptables -L FORWARD -n -v
   # 应该看到 tun+ 相关规则
   ```

5. **从服务器测试**
   ```bash
   docker exec openvpn-gateway ping -c 3 172.16.0.1
   # 替换为远程网段的 IP
   ```

## 🔐 LDAP 认证问题

### LDAP 连接失败

**症状**: 配置 LDAP 后客户端无法登录

**排查步骤**:

1. **测试 LDAP 连接**
   ```bash
   docker exec openvpn-gateway ldapsearch -x \
     -H ldap://ldap.company.com \
     -b "dc=company,dc=com" \
     "(uid=testuser)"
   ```

2. **检查 LDAP 配置**
   ```bash
   docker exec openvpn-gateway cat /etc/openvpn/ldap.conf
   ```

3. **检查 PAM 配置**
   ```bash
   docker exec openvpn-gateway cat /etc/pam.d/openvpn
   ```

4. **查看认证日志**
   ```bash
   docker logs openvpn-gateway | grep -i ldap
   docker logs openvpn-gateway | grep -i pam
   ```

### Active Directory 认证问题

**常见错误**:

1. **用户名格式错误**
   - AD 可能需要: `username@domain.com`
   - 或: `DOMAIN\username`

2. **搜索属性错误**
   - 确保使用 `sAMAccountName`
   - 过滤器: `(&(objectClass=user)(sAMAccountName=%u))`

3. **权限问题**
   - 绑定 DN 需要有搜索用户的权限

## 🐛 性能问题

### 连接速度慢

**排查步骤**:

1. **检查服务器负载**
   ```bash
   docker stats openvpn-gateway
   ```

2. **检查网络延迟**
   ```bash
   # 客户端 ping 服务器
   ping -c 10 服务器IP
   ```

3. **优化建议**:
   - 调整 MTU 值
   - 启用压缩: `ovpn_genconfig -u ... -z`
   - 考虑使用 TCP 协议
   - 升级服务器配置

### 内存使用过高

**排查**:
```bash
# 查看内存使用
docker stats openvpn-gateway

# 查看 OpenVPN 进程
docker exec openvpn-gateway ps aux | grep openvpn
```

**解决方法**:
- 限制容器内存: `docker run -m 2g ...`
- 减少站点数量
- 检查是否有内存泄漏

## 📝 日志分析

### 日志位置

```bash
# 容器日志
docker logs openvpn-gateway

# OpenVPN 主日志
docker exec openvpn-gateway cat /var/log/openvpn.log

# 站点日志
docker exec openvpn-gateway cat /var/log/openvpn-huawei.log
docker exec openvpn-gateway cat /var/log/openvpn-aws.log

# 实时查看
docker logs -f openvpn-gateway
```

### 常见错误信息

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| `TLS handshake failed` | 证书问题 | 检查证书有效期和配置 |
| `Connection timeout` | 网络不通 | 检查防火墙和路由 |
| `AUTH_FAILED` | 认证失败 | 检查 LDAP 配置或证书 |
| `RESOLVE: Cannot resolve host` | DNS 问题 | 检查 DNS 配置 |
| `Cannot allocate TUN/TAP dev` | 设备权限 | 添加 `--cap-add=NET_ADMIN` |

## 🔄 重置和恢复

### 完全重置

```bash
# 1. 停止并删除容器
docker-compose -f docker-compose-webui.yml down

# 2. 删除数据卷
docker volume rm openvpn-data

# 3. 重新初始化
docker volume create openvpn-data
docker run -v openvpn-data:/etc/openvpn --rm openvpn-gateway:latest \
    ovpn_genconfig -u udp://vpn.yourdomain.com
docker run -v openvpn-data:/etc/openvpn --rm -it openvpn-gateway:latest \
    ovpn_initpki

# 4. 重新启动
docker-compose -f docker-compose-webui.yml up -d
```

### 从备份恢复

```bash
# 1. 停止容器
docker-compose -f docker-compose-webui.yml down

# 2. 恢复备份
docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
    tar xzf /backup/openvpn-backup-20241219.tar.gz -C /

# 3. 重新启动
docker-compose -f docker-compose-webui.yml up -d
```

## 🆘 获取帮助

如果以上方法都无法解决问题：

1. **收集诊断信息**
   ```bash
   # 创建诊断报告
   docker logs openvpn-gateway > openvpn.log
   docker exec openvpn-gateway ovpn_setup_gateway -s > gateway-status.txt
   docker exec openvpn-gateway ovpn_list_sites > sites-list.txt
   ```

2. **提交 Issue**
   - 访问: https://github.com/ggfgmax/docker-openvpn-gateway/issues
   - 附上诊断信息
   - 描述问题现象和复现步骤

3. **查看文档**
   - [完整文档](../docs/)
   - [FAQ](faq.md)
   - [Web UI 文档](webui.md)

---

**记住**: 大多数问题都是配置问题，仔细检查每个步骤！

