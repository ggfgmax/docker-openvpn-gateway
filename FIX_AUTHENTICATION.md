# Web UI 认证问题修复说明

## 问题描述
Web UI 在执行任何操作时都提示需要认证，但浏览器不弹出认证窗口，输入账号密码后报 500 错误。

## 根本原因
1. **认证窗口不弹出**: 缺少 `WWW-Authenticate` HTTP 响应头
2. **500 错误**: 环境变量传递问题和脚本兼容性问题

## 修复内容

### 1. 修复认证窗口不弹出 (webui/app.py)
```python
# 在返回 401 状态码时添加必要的响应头
response.headers["WWW-Authenticate"] = 'Basic realm="OpenVPN Web UI"'
```

### 2. 添加详细日志记录 (webui/app.py)
- 添加 Python logging 模块
- 记录所有命令执行过程
- 输出详细的错误信息用于调试

### 3. 改进前端错误显示 (webui/templates/index.html)
- 检查 HTTP 响应状态码
- 显示详细的错误信息和命令输出
- 在浏览器控制台输出调试信息

### 4. 确保环境变量传递 (bin/ovpn_run_webui)
```bash
export OPENVPN="${OPENVPN:-/etc/openvpn}"
export EASYRSA="${EASYRSA:-/usr/share/easy-rsa}"
export EASYRSA_PKI="${EASYRSA_PKI:-$OPENVPN/pki}"
```

### 5. 修复脚本兼容性 (bin/ovpn_set_mode)
- 修复 sed -i 在 Alpine Linux 上的兼容性
- 添加更友好的错误提示
- 提示用户首次使用的初始化步骤

## 如何应用修复

### 方法1: 重建镜像（推荐）
```bash
# 停止容器
docker-compose -f docker-compose-webui.yml down

# 重新构建镜像
docker-compose -f docker-compose-webui.yml build

# 启动容器
docker-compose -f docker-compose-webui.yml up -d

# 查看日志
docker-compose -f docker-compose-webui.yml logs -f
```

### 方法2: 直接替换文件（临时方案）
```bash
# 复制修改后的文件到容器
docker cp webui/app.py openvpn-gateway:/opt/openvpn-webui/app.py
docker cp webui/templates/index.html openvpn-gateway:/opt/openvpn-webui/templates/index.html
docker cp bin/ovpn_run_webui openvpn-gateway:/usr/local/bin/ovpn_run_webui
docker cp bin/ovpn_set_mode openvpn-gateway:/usr/local/bin/ovpn_set_mode

# 重启容器
docker restart openvpn-gateway
```

## 使用说明

### 默认认证信息
- **用户名**: admin
- **密码**: openvpn

### 自定义认证信息
在 `docker-compose-webui.yml` 中设置环境变量：
```yaml
environment:
  - WEBUI_USERNAME=你的用户名
  - WEBUI_PASSWORD=你的密码
```

### 首次使用提示
如果是首次使用，在 Web UI 中切换模式前需要先初始化：
```bash
# 进入容器
docker exec -it openvpn-gateway bash

# 生成配置
ovpn_genconfig -u udp://你的服务器IP

# 初始化 PKI
ovpn_initpki

# 退出容器
exit
```

## 测试认证

1. 在浏览器中访问 Web UI: `http://你的服务器IP:8080`
2. 执行任何需要认证的操作（如切换模式、添加客户端等）
3. 浏览器会弹出认证对话框
4. 输入用户名和密码
5. 如果仍有错误，查看容器日志：
   ```bash
   docker logs openvpn-gateway
   ```

## 调试技巧

### 查看详细日志
```bash
# 实时查看日志
docker logs -f openvpn-gateway

# 查看最近的错误
docker logs openvpn-gateway 2>&1 | grep -i error
```

### 检查配置文件
```bash
# 进入容器
docker exec -it openvpn-gateway bash

# 检查配置文件是否存在
ls -la /etc/openvpn/ovpn_env.sh

# 查看当前模式
ovpn_set_mode
```

### 浏览器控制台
打开浏览器开发者工具（F12）查看：
- Console 标签: JavaScript 错误和日志
- Network 标签: HTTP 请求和响应详情

## 常见问题

### Q: 认证窗口还是不弹出？
A: 清除浏览器缓存后重试，或使用无痕模式访问

### Q: 输入账号密码后还是报错？
A: 检查容器日志中的详细错误信息，可能是配置文件未初始化

### Q: 500 错误但日志中看不到错误？
A: 确保重启容器后再测试，旧进程可能还在使用旧代码

## 安全建议

1. **立即修改默认密码**: 使用强密码并通过环境变量设置
2. **使用 HTTPS**: 在生产环境中配置反向代理（如 Nginx）启用 HTTPS
3. **限制访问**: 使用防火墙规则限制 Web UI 的访问 IP
4. **定期备份**: 备份 `/etc/openvpn` 目录中的配置和证书
