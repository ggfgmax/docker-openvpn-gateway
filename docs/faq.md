# 常见问题 FAQ

## 📋 通用问题

### Q: 这个项目和原版有什么区别？

**A**: 主要增强功能包括：
- ✅ 多云网络打通（Site-to-Site VPN）
- ✅ LDAP/AD 认证支持
- ✅ Web 管理界面
- ✅ 运行模式切换
- ✅ 证书自动配置

原版的所有功能都保留。

### Q: 我应该用普通模式还是网关模式？

**A**: 
- **普通模式**: 适合简单的远程访问场景（员工访问公司内网）
- **网关模式**: 适合多云环境，需要打通多个 VPN 网络

### Q: 必须使用 Web UI 吗？

**A**: 不是必须的。
- Web UI 适合小白用户和日常管理
- 命令行适合高级用户和自动化场景
- 两种方式功能相同

## 🌐 Web UI 相关

### Q: Web UI 的默认密码是什么？

**A**: 
- 默认用户名: `admin`
- 默认密码: `openvpn`
- ⚠️ **首次登录后必须修改密码**

修改方法：在 `.env` 文件中设置 `WEBUI_PASSWORD`

### Q: 如何配置 HTTPS？

**A**: 使用 Nginx 反向代理：

```nginx
server {
    listen 443 ssl;
    server_name vpn-admin.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
    }
}
```

### Q: 站点证书配置失败怎么办？

**A**: 检查以下几点：
1. 确保粘贴的是完整 .ovpn 文件内容
2. 检查是否包含 `<ca>`, `<cert>`, `<key>` 标签
3. 查看浏览器控制台错误信息
4. 查看容器日志: `docker logs openvpn-gateway`

## 🌍 多云网络相关

### Q: 需要在远程云平台做什么配置？

**A**: 远程云平台需要：
1. 部署 OpenVPN 服务器
2. 为主入口网关生成客户端证书
3. 提供 .ovpn 客户端配置文件

### Q: 可以连接几个远程站点？

**A**: 理论上没有限制，但建议：
- 不超过 10 个站点（性能考虑）
- 确保服务器有足够的带宽和 CPU

### Q: 站点添加后无法连接？

**A**: 排查步骤：
1. 检查证书是否正确配置
2. 检查远程 VPN 服务器是否运行
3. 检查网络连通性: `ping 远程主机`
4. 查看站点日志: `docker exec openvpn-gateway cat /var/log/openvpn-站点名.log`

### Q: 客户端无法访问远程网段？

**A**: 检查：
1. 确认已切换到网关模式
2. 运行 `ovpn_update_routes` 更新路由
3. 检查 IP 转发: `sysctl net.ipv4.ip_forward`
4. 查看路由表: `docker exec openvpn-gateway ip route`

## 🔐 LDAP 认证相关

### Q: 支持哪些 LDAP 服务器？

**A**: 支持：
- OpenLDAP
- Active Directory
- 389 Directory Server
- 其他兼容 LDAP 协议的服务器

### Q: LDAP 配置后无法登录？

**A**: 排查：
1. 测试 LDAP 连接:
   ```bash
   docker exec openvpn-gateway ldapsearch -x \
     -H ldap://ldap.company.com \
     -b "dc=company,dc=com" \
     "(uid=testuser)"
   ```
2. 检查 Base DN 是否正确
3. 检查用户过滤器是否匹配
4. 查看 OpenVPN 日志

### Q: 可以同时使用证书和 LDAP 吗？

**A**: 可以！这提供双因素认证：
- 客户端需要有效证书
- 连接时需要输入 LDAP 用户名密码

## 🚀 部署和运维

### Q: 推荐的服务器配置？

**A**: 
- **最小配置**: 1 核 CPU, 2GB 内存, 5Mbps 带宽
- **推荐配置**: 2 核 CPU, 4GB 内存, 10Mbps 带宽
- **多用户**: 4 核 CPU, 8GB 内存, 100Mbps 带宽

### Q: 如何备份配置？

**A**:
```bash
docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
  tar czf /backup/openvpn-backup-$(date +%Y%m%d).tar.gz /etc/openvpn
```

恢复:
```bash
docker run -v openvpn-data:/etc/openvpn -v $PWD:/backup --rm alpine \
  tar xzf /backup/openvpn-backup-20241219.tar.gz -C /
```

### Q: 如何更新镜像？

**A**:
```bash
# 1. 备份配置
# 2. 拉取最新代码
git pull

# 3. 重新构建
bash scripts/build-gateway.sh

# 4. 重新启动
docker-compose -f docker-compose-webui.yml down
docker-compose -f docker-compose-webui.yml up -d
```

### Q: 可以在 Kubernetes 上运行吗？

**A**: 可以，但需要：
- 使用 PersistentVolume 存储配置
- 配置 NET_ADMIN 权限
- 注意网络策略配置

## 🔧 故障排查

### Q: 客户端无法连接？

**A**: 排查步骤：
1. 检查服务器防火墙（UDP 1194）
2. 检查容器是否运行: `docker ps`
3. 查看日志: `docker logs openvpn-gateway`
4. 测试端口: `nc -u -v 服务器IP 1194`

### Q: 连接成功但无法上网？

**A**: 检查：
1. DNS 配置是否正确
2. 客户端路由是否生效
3. 服务器 NAT 是否启用
4. 防火墙规则

### Q: 性能问题？

**A**: 优化建议：
1. 升级服务器配置
2. 调整 MTU 值
3. 使用 TCP 协议（高延迟网络）
4. 启用压缩: `ovpn_genconfig -u ... -z`

### Q: 日志在哪里查看？

**A**: 
- 主日志: `docker logs openvpn-gateway`
- OpenVPN 日志: `docker exec openvpn-gateway cat /var/log/openvpn.log`
- 站点日志: `docker exec openvpn-gateway cat /var/log/openvpn-站点名.log`
- Web UI 中也可以查看日志

## 🔒 安全相关

### Q: 如何限制 Web UI 访问？

**A**: 
```bash
# UFW
sudo ufw allow from 192.168.1.0/24 to any port 8080
sudo ufw deny 8080

# iptables
iptables -A INPUT -p tcp --dport 8080 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
```

### Q: 如何吊销客户端证书？

**A**: 
- Web UI: 客户端管理 → 点击"吊销"
- 命令行:
  ```bash
  docker exec openvpn-gateway easyrsa revoke 客户端名
  docker exec openvpn-gateway easyrsa gen-crl
  docker restart openvpn-gateway
  ```

### Q: CA 密码忘记了怎么办？

**A**: 无法恢复。需要：
1. 重新初始化 PKI: `ovpn_initpki`
2. 重新生成所有客户端证书
3. 客户端需要使用新证书

⚠️ 建议妥善保管 CA 密码

## 📱 客户端相关

### Q: 支持哪些客户端？

**A**: 
- Windows: OpenVPN GUI
- macOS: Tunnelblick, OpenVPN Connect
- Linux: OpenVPN 命令行
- Android: OpenVPN Connect
- iOS: OpenVPN Connect

### Q: 客户端如何使用 LDAP 认证？

**A**: 
1. 使用生成的 .ovpn 文件连接
2. 连接时会提示输入用户名密码
3. 输入 LDAP 账户信息
4. 如果配置了证书+LDAP，两者都需要

### Q: 可以给客户端分配静态 IP 吗？

**A**: 可以，参考 [docs/static-ips.md](static-ips.md)

## 💡 其他问题

### Q: 项目会持续更新吗？

**A**: 是的，我们会：
- 修复 Bug
- 添加新功能
- 更新文档
- 关注 GitHub Issues

### Q: 如何贡献代码？

**A**: 
1. Fork 项目
2. 创建特性分支
3. 提交 Pull Request
4. 查看 [CONTRIBUTING.md](../CONTRIBUTING.md)

### Q: 商业使用需要授权吗？

**A**: 不需要，MIT 许可证允许商业使用。

---

**还有问题？**
- 📖 查看 [完整文档](../docs/)
- 💬 [提交 Issue](https://github.com/ggfgmax/docker-openvpn-gateway/issues)
- 📧 联系维护者

