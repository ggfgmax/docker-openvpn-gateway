# 修复：GATEWAY_MODE 环境变量不生效

## 🐛 问题描述

在 `docker-compose-webui.yml` 中设置了 `GATEWAY_MODE=1`，但启动后 Web UI 显示的仍然是"普通VPN模式"。

## 🔍 根本原因

**问题链路：**
1. `docker-compose-webui.yml` 中设置 `GATEWAY_MODE=1` 环境变量
2. `ovpn_genconfig` 生成配置时**没有读取**这个环境变量
3. 配置文件 `/etc/openvpn/ovpn_env.sh` 中**没有** `OVPN_GATEWAY_MODE` 设置
4. `ovpn_run` 启动时从配置文件读取，默认值是 `0`（普通模式）

**代码层面：**
- `ovpn_genconfig` 只保存 `OVPN_` 开头的环境变量
- docker-compose 中的 `GATEWAY_MODE` 没有 `OVPN_` 前缀
- 因此模式设置没有被保存到配置文件

## ✅ 修复内容

修改了 `bin/ovpn_genconfig`，在保存配置前添加：

```bash
# 读取并保存运行模式设置（从环境变量或使用默认值）
export OVPN_GATEWAY_MODE="${GATEWAY_MODE:-0}"
export OVPN_LDAP_ENABLED="${LDAP_ENABLED:-0}"
```

现在 `ovpn_genconfig` 会：
1. ✅ 读取 docker-compose 中的 `GATEWAY_MODE` 环境变量
2. ✅ 转换为 `OVPN_GATEWAY_MODE` 并保存到配置文件
3. ✅ 在生成配置后显示模式信息

## 🚀 如何应用修复

### 方案1：新用户（推荐，完全重新初始化）

如果你还没有生成客户端证书，或者可以重新生成，使用这个方案：

```bash
# 1. 停止并删除容器
docker-compose -f docker-compose-webui.yml down

# 2. 删除旧的配置 volume（⚠️ 会删除所有配置和证书）
docker volume rm docker-openvpn-gateway_openvpn-data

# 3. 确认 docker-compose-webui.yml 中的设置
# 应该有: GATEWAY_MODE=${GATEWAY_MODE:-1}

# 4. 重新构建镜像（应用修复的代码）
docker-compose -f docker-compose-webui.yml build

# 5. 启动容器
docker-compose -f docker-compose-webui.yml up -d

# 6. 进入容器初始化（会自动使用 GATEWAY_MODE=1）
docker exec -it openvpn-gateway bash
ovpn_genconfig -u udp://你的服务器IP
# 现在应该显示: 运行模式: 网关模式 (GATEWAY_MODE=1)
ovpn_initpki
exit

# 7. 重启容器
docker restart openvpn-gateway

# 8. 查看日志确认模式
docker logs openvpn-gateway | grep "运行模式"
# 应该显示: 运行模式: 多云网络主入口网关模式
```

### 方案2：已有用户（保留现有配置，使用 Web UI 切换）

如果你已经生成了客户端证书，不想重新初始化：

```bash
# 1. 重新构建镜像（应用修复的代码）
docker-compose -f docker-compose-webui.yml build

# 2. 重启容器
docker restart openvpn-gateway

# 3. 访问 Web UI
# http://你的服务器IP:8080

# 4. 在 Web UI 中切换模式
# - 登录后切换到"模式设置"标签
# - 选择"网关模式"
# - 点击"保存模式设置"

# 5. 再次重启容器
docker restart openvpn-gateway

# 6. 验证
docker logs openvpn-gateway | grep "运行模式"
```

### 方案3：已有用户（命令行切换模式）

如果你不想使用 Web UI，可以通过命令行切换：

```bash
# 1. 重新构建镜像
docker-compose -f docker-compose-webui.yml build

# 2. 进入容器
docker exec -it openvpn-gateway bash

# 3. 切换到网关模式
ovpn_set_mode gateway

# 4. 退出容器
exit

# 5. 重启容器
docker restart openvpn-gateway

# 6. 验证
docker logs openvpn-gateway | grep "运行模式"
```

## 🔍 验证修复

### 1. 检查配置文件
```bash
# 查看配置文件内容
docker exec openvpn-gateway cat /etc/openvpn/ovpn_env.sh | grep GATEWAY

# 应该看到：
# declare -x OVPN_GATEWAY_MODE="1"
```

### 2. 查看启动日志
```bash
docker logs openvpn-gateway | grep -A 5 "OpenVPN 启动配置"

# 应该看到：
# ==========================================
#   OpenVPN 启动配置
# ==========================================
# 运行模式: 多云网络主入口网关模式
# ...
```

### 3. 检查 Web UI
访问 `http://你的服务器IP:8080`，首页应该显示：
- 运行模式：**网关模式** ✅

## 📊 对比：修复前 vs 修复后

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| 读取环境变量 | ❌ 不读取 | ✅ 读取 `GATEWAY_MODE` |
| 保存到配置文件 | ❌ 不保存 | ✅ 保存为 `OVPN_GATEWAY_MODE` |
| 显示配置摘要 | ❌ 无 | ✅ 显示模式信息 |
| 默认模式 | 普通模式 | 根据环境变量（默认网关模式） |

## 🎯 docker-compose-webui.yml 配置说明

现在 `docker-compose-webui.yml` 中的环境变量会正确生效：

```yaml
environment:
  # 模式设置: 0=普通VPN, 1=网关模式
  - GATEWAY_MODE=${GATEWAY_MODE:-1}  # ✅ 现在会生效！
  
  # LDAP 设置: 0=禁用, 1=启用
  - LDAP_ENABLED=${LDAP_ENABLED:-0}  # ✅ 现在会生效！
```

**环境变量优先级：**
1. 宿主机的环境变量 `GATEWAY_MODE`（如果设置了）
2. docker-compose 中的默认值 `:-1`
3. 配置文件中的值（初始化后）

**示例：**
```bash
# 使用默认值（网关模式）
docker-compose -f docker-compose-webui.yml up -d

# 或者明确指定为普通模式
GATEWAY_MODE=0 docker-compose -f docker-compose-webui.yml up -d

# 或者在 .env 文件中设置
echo "GATEWAY_MODE=1" > .env
docker-compose -f docker-compose-webui.yml up -d
```

## 🔄 模式切换

初始化后，如果需要切换模式：

### 方法1：Web UI（推荐）
1. 访问 `http://你的服务器IP:8080`
2. 切换到"模式设置"标签
3. 选择需要的模式
4. 点击"保存模式设置"
5. 重启容器: `docker restart openvpn-gateway`

### 方法2：命令行
```bash
docker exec -it openvpn-gateway ovpn_set_mode gateway  # 或 normal
docker restart openvpn-gateway
```

### 方法3：手动编辑（不推荐）
```bash
docker exec -it openvpn-gateway vi /etc/openvpn/ovpn_env.sh
# 修改或添加: export OVPN_GATEWAY_MODE=1
docker restart openvpn-gateway
```

## 💡 常见问题

### Q1: 我已经初始化过了，必须重新初始化吗？
A: 不是必须的。你可以：
- 使用 Web UI 切换模式（推荐）
- 使用 `ovpn_set_mode` 命令切换
- 手动编辑配置文件

### Q2: 重新初始化会影响什么？
A: 会删除：
- ✅ 所有客户端证书（需要重新生成）
- ✅ 所有站点配置（需要重新添加）
- ✅ CA 证书（会生成新的）

### Q3: 修改环境变量后需要重新初始化吗？
A: 取决于：
- 如果**还没有**初始化，环境变量会在初始化时生效
- 如果**已经**初始化，需要切换模式（Web UI 或命令行）

### Q4: 为什么不直接读取容器的环境变量？
A: 因为配置需要持久化：
- 环境变量只在容器创建时设置
- 配置文件保存在 Docker Volume 中，不受容器重建影响
- 这样可以在不修改容器的情况下切换模式

### Q5: 我在 docker-compose 中设置的其他环境变量也不生效？
A: 只有在 `ovpn_genconfig` 中明确导出的变量才会保存：
```bash
export OVPN_GATEWAY_MODE="${GATEWAY_MODE:-0}"
export OVPN_LDAP_ENABLED="${LDAP_ENABLED:-0}"
```
如果需要其他变量生效，需要在 `ovpn_genconfig` 中添加类似的代码。

## 🎉 修复效果

修复后：
- ✅ `docker-compose-webui.yml` 中的 `GATEWAY_MODE=1` 正确生效
- ✅ 初始化时自动配置为网关模式
- ✅ 启动日志显示"多云网络主入口网关模式"
- ✅ Web UI 显示"网关模式"
- ✅ 支持添加远程站点
- ✅ 自动启动 Site-to-Site VPN 连接

## 📚 相关文档

- [快速启动指南](QUICK_START.md)
- [站点证书配置指南](SITE_CERTIFICATE_GUIDE.md)
- [日志调试指南](LOGGING_GUIDE.md)
- [Web UI v2.0 改进](WEBUI_V2_IMPROVEMENTS.md)
