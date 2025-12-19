# OpenVPN 网关快速启动指南

## 🚀 完整初始化步骤

### 步骤 1: 启动容器

```bash
cd /Users/lichuan/Downloads/code/docker-openvpn-gateway

# 启动容器
docker-compose -f docker-compose-webui.yml up -d

# 查看容器是否正常运行
docker ps | grep openvpn
```

### 步骤 2: 初始化 PKI（证书系统）

**重要：以下命令必须在容器内执行！**

```bash
# 进入容器
docker exec -it openvpn-gateway bash

# 在容器内执行以下命令：

# 1. 生成配置（替换为你的服务器地址）
ovpn_genconfig -u udp://你的服务器IP或域名

# 示例：
# ovpn_genconfig -u udp://vpn.example.com
# 或者使用IP：
# ovpn_genconfig -u udp://123.45.67.89

# 2. 初始化 PKI（默认使用无密码模式）
ovpn_initpki

# ✅ 默认配置：无密码 CA
#   - 简化操作，Web UI 可以直接生成客户端证书
#   - 适合开发/测试环境
#   - 所有提示直接回车即可
# 
# 🔐 如需密码保护（生产环境推荐）：
#   - 使用命令: ovpn_initpki withpass
#   - 设置CA密码时输入一个强密码
#   - 需要在 docker-compose 中设置 CA_PASSWORD 环境变量

# 其他提示：
# - Common Name (CN) 直接回车使用默认值
# - 确认各项信息时输入 yes

# 3. 退出容器
exit
```

**如果你使用了密码保护的 CA**（`ovpn_initpki withpass`），需要配置环境变量：

```bash
# 创建或编辑 .env 文件
cat > .env << 'EOF'
# CA 密码（只有使用 withpass 创建 CA 时才需要）
CA_PASSWORD=你设置的CA密码

# Web UI 认证
WEBUI_USERNAME=admin
WEBUI_PASSWORD=admin
EOF

# 设置权限
chmod 600 .env

# 重新构建镜像
docker-compose -f docker-compose-webui.yml build
```

**如果使用默认的无密码 CA**（推荐开始时使用）：
- 不需要设置 CA_PASSWORD
- 直接重启容器即可
```bash
docker restart openvpn-gateway
```

### 步骤 3: 重启容器

```bash
# 重启容器使配置生效
docker restart openvpn-gateway

# 查看日志确认启动成功
docker logs -f openvpn-gateway
```

看到类似下面的日志表示成功：
```
==========================================
  启动 OpenVPN Web 管理界面
==========================================

Web 界面地址: http://0.0.0.0:8080
...

==========================================
  OpenVPN 服务启动
==========================================
```

### 步骤 4: 访问 Web UI

```
地址: http://你的服务器IP:8080
用户名: admin
密码: admin
```

## 🔍 常见问题

### Q1: 为什么要在容器内执行命令？

A: 因为：
- OpenVPN 的配置文件需要在容器内的 `/etc/openvpn` 目录
- 虽然该目录通过 Docker Volume 持久化了，但命令行工具在容器内
- 在宿主机执行命令会找不到这些工具

### Q2: 如果之前在宿主机执行过怎么办？

A: 清理后重新初始化：

```bash
# 停止并删除容器
docker-compose -f docker-compose-webui.yml down

# 删除 volume（会删除所有配置，请谨慎！）
docker volume rm docker-openvpn-gateway_openvpn-data

# 重新启动
docker-compose -f docker-compose-webui.yml up -d

# 然后按照步骤2重新初始化
```

### Q3: ovpn_initpki 执行时卡住了？

A: 可能是在等待输入：
- 提示 "Enter PEM pass phrase": 输入密码（或直接回车留空）
- 提示 "Common Name": 直接回车使用默认值
- 提示 "yes/no": 输入 `yes` 回车

### Q4: 如何验证初始化成功？

```bash
# 进入容器
docker exec -it openvpn-gateway bash

# 检查配置文件是否存在
ls -la /etc/openvpn/ovpn_env.sh
ls -la /etc/openvpn/pki/

# 查看配置内容
cat /etc/openvpn/ovpn_env.sh

# 退出
exit
```

应该看到：
- `/etc/openvpn/ovpn_env.sh` 存在
- `/etc/openvpn/pki/` 目录下有 ca.crt 等证书文件
- `ovpn_env.sh` 包含 `OVPN_SERVER` 等配置

### Q5: Web UI 还是提示找不到配置文件？

可能的原因：
1. 没有在容器内执行初始化命令
2. 初始化过程中出错了（检查日志）
3. 容器权限问题（检查 volume 权限）

解决方法：
```bash
# 1. 检查容器日志
docker logs openvpn-gateway 2>&1 | tail -100

# 2. 进入容器手动检查
docker exec -it openvpn-gateway bash
ls -la /etc/openvpn/
cat /etc/openvpn/ovpn_env.sh  # 查看是否有内容

# 3. 如果文件不存在，重新初始化
ovpn_genconfig -u udp://你的服务器IP
ovpn_initpki
exit

# 4. 重启容器
docker restart openvpn-gateway
```

## 📝 完整初始化示例

```bash
# === 宿主机 ===
$ cd /Users/lichuan/Downloads/code/docker-openvpn-gateway
$ docker-compose -f docker-compose-webui.yml up -d
Creating network "docker-openvpn-gateway_vpn-network" ... done
Creating volume "docker-openvpn-gateway_openvpn-data" ... done
Creating openvpn-gateway ... done

$ docker exec -it openvpn-gateway bash

# === 容器内 ===
bash-5.2# ovpn_genconfig -u udp://vpn.example.com
Processing PUSH Config: 'block-outside-dns'
Processing Route Config: '192.168.254.0/24'
Successfully generated config
Cleaning up before init...

bash-5.2# ovpn_initpki

init-pki complete; you may now create a CA or requests.
Your newly created PKI dir is: /etc/openvpn/pki

Using SSL: openssl LibreSSL 3.9.2

Enter New CA Key Passphrase: [直接回车或输入密码]
Confirm New CA Key Passphrase: [直接回车或输入密码]

Common Name (eg: your user, host, or server name) [Easy-RSA CA]: [直接回车]

CA creation complete and you may now import and sign cert requests.
...

Generating DH parameters, 2048 bit long safe prime
...

DH parameters successfully generated.
...

init-pki complete; you may now create a CA or requests.
...

bash-5.2# exit

# === 宿主机 ===
$ docker restart openvpn-gateway
openvpn-gateway

$ docker logs openvpn-gateway
==========================================
  启动 OpenVPN Web 管理界面
==========================================
...
==========================================
  OpenVPN 服务启动
==========================================
...
Initialization Sequence Completed
```

## ✅ 验证成功

初始化成功后，Web UI 应该可以：
1. ✅ 切换运行模式（普通VPN / 网关模式）
2. ✅ 添加客户端
3. ✅ 下载客户端配置
4. ✅ 添加远程站点（网关模式）

## 🎯 下一步

初始化完成后，你可以：

### 1. 生成客户端证书
```bash
docker exec openvpn-gateway ovpn_getclient 客户端名称 > client.ovpn
```

或在 Web UI 中操作：
- 切换到"客户端管理"标签
- 输入客户端名称（如 zhangsan）
- 点击"生成客户端证书"
- 点击"下载"按钮获取 .ovpn 配置文件

### 2. 添加远程站点（网关模式）
- 切换到"站点管理"标签
- 填写站点信息和粘贴 .ovpn 内容
- 点击"一键添加站点"
- 重启服务

### 3. 客户端连接
将下载的 .ovpn 文件导入到 OpenVPN 客户端：
- Windows: OpenVPN GUI
- macOS: Tunnelblick
- Linux: `openvpn --config client.ovpn`
- 移动端: OpenVPN Connect

## 🆘 获取帮助

如果还有问题：

1. 查看日志：
   ```bash
   docker logs -f openvpn-gateway
   ```

2. 检查配置：
   ```bash
   docker exec openvpn-gateway ovpn_status
   ```

3. 查看文档：
   - [完整配置指南](SITE_CERTIFICATE_GUIDE.md)
   - [日志调试指南](LOGGING_GUIDE.md)
   - [认证问题修复](FIX_AUTHENTICATION.md)
