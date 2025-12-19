# Web UI 日志和调试指南

## 📍 日志位置

### 1. Web UI 应用日志
Web UI 使用 Python logging 模块，日志输出到**容器的标准输出**。

查看方式：
```bash
# 实时查看 Web UI 日志
docker logs -f openvpn-gateway

# 查看最近100行
docker logs --tail 100 openvpn-gateway

# 只看错误日志
docker logs openvpn-gateway 2>&1 | grep -i error

# 只看 Web UI 相关日志
docker logs openvpn-gateway 2>&1 | grep -E "(INFO|WARNING|ERROR)"
```

### 2. OpenVPN 主服务日志
- **容器内路径**: `/var/log/openvpn.log`
- **查看方式**:
  ```bash
  # 进入容器查看
  docker exec -it openvpn-gateway tail -f /var/log/openvpn.log
  
  # 或直接在宿主机查看
  docker exec openvpn-gateway cat /var/log/openvpn.log
  ```

### 3. Site-to-Site 连接日志
每个远程站点都有独立的日志文件：
- **容器内路径**: `/var/log/openvpn-<站点名称>.log`
- **示例**: `/var/log/openvpn-huawei.log`

查看方式：
```bash
# 查看华为云站点连接日志
docker exec openvpn-gateway tail -f /var/log/openvpn-huawei.log

# 查看所有站点日志
docker exec openvpn-gateway ls -la /var/log/openvpn-*.log
```

### 4. Docker Compose 日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose-webui.yml logs

# 实时跟踪
docker-compose -f docker-compose-webui.yml logs -f

# 只看最近50行
docker-compose -f docker-compose-webui.yml logs --tail 50
```

## 🔍 日志内容说明

### Web UI 日志示例
```
2025-12-19 07:19:01 - __main__ - INFO - 切换模式请求: gateway
2025-12-19 07:19:01 - __main__ - INFO - 执行命令: ovpn_set_mode gateway
2025-12-19 07:19:01 - __main__ - INFO - 命令返回码: 0
2025-12-19 07:19:01 - __main__ - INFO - 命令输出: 已切换到网关模式
2025-12-19 07:19:01 - __main__ - INFO - 模式切换成功: gateway
```

### 常见日志级别
- **INFO**: 正常操作信息
- **WARNING**: 警告信息（命令执行有 stderr 输出）
- **ERROR**: 错误信息（操作失败）

## 🛠️ 调试技巧

### 1. 查看 Web UI 启动日志
```bash
docker logs openvpn-gateway 2>&1 | grep -A 5 "启动 OpenVPN Web 管理界面"
```

输出示例：
```
==========================================
  启动 OpenVPN Web 管理界面
==========================================

Web 界面地址: http://0.0.0.0:8080
默认用户名: admin
默认密码: openvpn

配置目录: /etc/openvpn
==========================================
```

### 2. 查看命令执行日志
所有通过 Web UI 执行的命令都会记录：
```bash
docker logs openvpn-gateway 2>&1 | grep "执行命令"
```

### 3. 查看 HTTP 请求日志
Flask 会记录所有 HTTP 请求：
```bash
docker logs openvpn-gateway 2>&1 | grep "GET\|POST\|DELETE"
```

示例：
```
222.212.88.121 - - [19/Dec/2025 07:18:51] "GET /api/status HTTP/1.1" 200 -
222.212.88.121 - - [19/Dec/2025 07:18:55] "POST /api/mode HTTP/1.1" 401 -
```

### 4. 查看认证相关日志
```bash
docker logs openvpn-gateway 2>&1 | grep -i "auth\|401"
```

### 5. 监控实时日志
在一个终端窗口持续监控：
```bash
# 终端1: Web UI 日志
docker logs -f openvpn-gateway

# 终端2: OpenVPN 主日志
docker exec -it openvpn-gateway tail -f /var/log/openvpn.log

# 终端3: 站点连接日志
docker exec -it openvpn-gateway tail -f /var/log/openvpn-*.log
```

## 📊 浏览器调试

### 1. 打开浏览器开发者工具
- Chrome/Edge: 按 `F12` 或 `Ctrl+Shift+I`
- Firefox: 按 `F12`
- Safari: `Command+Option+I`

### 2. Console 标签
查看 JavaScript 日志和错误：
```javascript
// Web UI 会输出详细调试信息
模式切换失败: {error: "...", stdout: "...", success: false}
请求异常: Error: Failed to fetch
```

### 3. Network 标签
查看所有 HTTP 请求：
- 请求 URL
- 请求方法 (GET/POST/DELETE)
- 状态码 (200/401/500)
- 请求头 (Headers)
- 请求体 (Payload)
- 响应内容 (Response)

**调试认证问题**：
1. 找到返回 401 的请求
2. 查看 Response Headers 中是否有 `WWW-Authenticate`
3. 查看 Request Headers 中是否有 `Authorization`

**调试 500 错误**：
1. 找到返回 500 的请求
2. 查看 Response 标签中的错误详情
3. 对照容器日志查找详细错误信息

## 🔧 常见问题排查

### 问题1: Web UI 无法访问
```bash
# 1. 检查容器是否运行
docker ps | grep openvpn

# 2. 检查端口映射
docker port openvpn-gateway

# 3. 查看启动日志
docker logs openvpn-gateway | tail -50

# 4. 检查防火墙
sudo ufw status  # Ubuntu
firewall-cmd --list-all  # CentOS
```

### 问题2: 操作提示认证失败
```bash
# 1. 检查环境变量
docker exec openvpn-gateway env | grep WEBUI

# 2. 查看认证日志
docker logs openvpn-gateway 2>&1 | grep "401"

# 3. 清除浏览器缓存后重试
```

### 问题3: 操作报 500 错误
```bash
# 1. 查看详细错误
docker logs openvpn-gateway 2>&1 | grep -A 10 ERROR

# 2. 检查配置文件是否存在
docker exec openvpn-gateway ls -la /etc/openvpn/ovpn_env.sh

# 3. 检查脚本权限
docker exec openvpn-gateway ls -la /usr/local/bin/ovpn_*

# 4. 手动执行命令测试
docker exec openvpn-gateway ovpn_set_mode
```

### 问题4: 站点无法连接
```bash
# 1. 检查站点配置
docker exec openvpn-gateway ls -la /etc/openvpn/sites/

# 2. 查看站点日志
docker exec openvpn-gateway tail -100 /var/log/openvpn-<站点名>.log

# 3. 检查证书配置
docker exec openvpn-gateway cat /etc/openvpn/sites/<站点名>.conf

# 4. 手动测试连接
docker exec openvpn-gateway ping <远程站点IP>
```

## 💾 导出日志

### 导出所有日志到本地
```bash
# 创建日志目录
mkdir -p openvpn-logs

# 导出容器日志
docker logs openvpn-gateway > openvpn-logs/container.log 2>&1

# 导出 OpenVPN 主日志
docker exec openvpn-gateway cat /var/log/openvpn.log > openvpn-logs/openvpn-main.log 2>/dev/null || echo "主日志不存在"

# 导出所有站点日志
docker exec openvpn-gateway sh -c 'cat /var/log/openvpn-*.log 2>/dev/null' > openvpn-logs/sites.log || echo "无站点日志"

# 打包日志
tar -czf openvpn-logs-$(date +%Y%m%d-%H%M%S).tar.gz openvpn-logs/

echo "日志已导出并打包！"
```

## 📈 日志持久化

如果需要在宿主机持久化日志：

修改 `docker-compose-webui.yml`：
```yaml
services:
  openvpn-gateway:
    volumes:
      - openvpn-data:/etc/openvpn
      - ./logs:/var/log:rw  # 新增：映射日志目录到宿主机
```

然后重启容器：
```bash
docker-compose -f docker-compose-webui.yml down
docker-compose -f docker-compose-webui.yml up -d
```

日志将保存到宿主机的 `./logs` 目录。

## 🔐 生产环境建议

1. **使用日志收集工具**: 如 ELK Stack、Loki、Fluentd
2. **设置日志轮转**: 避免日志文件过大
3. **监控告警**: 监控错误日志并及时告警
4. **定期备份**: 定期导出和备份关键日志
