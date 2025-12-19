# 站点证书配置完整指南

## 🎯 为什么需要配置证书？

在 **Site-to-Site VPN** 模式下，本网关需要作为客户端连接到远程 VPN 服务器。就像你用 VPN 客户端连接 VPN 服务器一样，网关也需要证书和密钥来建立连接。

## 📋 完整流程（最新简化版）

### 步骤1️⃣: 从远程站点获取 .ovpn 文件

向远程 VPN 服务器管理员获取 `.ovpn` 配置文件，这个文件包含：
- 服务器地址和端口 (remote 行)
- 协议 (proto 行)
- CA 证书 (<ca>标签)
- 客户端证书 (<cert>标签)
- 客户端私钥 (<key>标签)
- TLS 认证密钥 (<tls-auth>标签，可选)

**示例 .ovpn 文件内容：**
```
client
dev tun
proto udp
remote vpn.huaweicloud.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
verb 3

<ca>
-----BEGIN CERTIFICATE-----
MIIDSzCCAjOgAwIBAgIUX... (CA证书内容)
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIRAP... (客户端证书内容)
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w... (客户端私钥内容)
-----END PRIVATE KEY-----
</key>

<tls-auth>
-----BEGIN OpenVPN Static key V1-----
6acef03f62675b4b1bbd03e5... (TLS密钥内容)
-----END OpenVPN Static key V1-----
</tls-auth>
key-direction 1
```

### 步骤2️⃣: 在 Web UI 中一键添加站点

1. 登录 Web UI: `http://你的服务器IP:8080`
2. 切换到 **"站点管理"** 标签
3. 在"添加新站点"区域填写：
   - **站点名称**: `huawei` （自定义标识，仅支持字母、数字、下划线）
   - **远程VPC内网网段**: `172.16.0.0/16` （这是远程云平台的VPC网段，不是OpenVPN虚拟网段）
   - **.ovpn 配置文件内容**: 将整个 .ovpn 文件内容粘贴到文本框
4. 点击 **"一键添加站点"** 按钮

**系统会自动完成：**
- ✅ 从 .ovpn 文件中提取服务器地址、端口、协议
- ✅ 从 .ovpn 文件中提取证书和密钥
- ✅ 创建站点配置
- ✅ 配置证书
- ✅ 显示完整的配置信息

### 步骤3️⃣: 重启服务

```bash
docker restart openvpn-gateway
```

### 步骤4️⃣: 验证连接

```bash
# 查看站点连接日志
docker exec openvpn-gateway tail -f /var/log/openvpn-huawei.log

# 查看连接状态
docker exec openvpn-gateway ps aux | grep openvpn

# 测试连接到远程VPC内网
docker exec openvpn-gateway ping 172.16.0.1
```

## 🖥️ Web UI 改进说明

### ✨ 最新功能（v2.0）

1. **一键添加站点**
   - 只需填写：站点名称 + 远程VPC网段
   - 直接粘贴 .ovpn 文件内容
   - 系统自动提取服务器地址、端口、协议、证书
   - 无需手动重复输入

2. **智能配置解析**
   - 自动从 .ovpn 文件中提取 `remote` 行
   - 自动识别协议（UDP/TCP）
   - 自动识别端口
   - 自动提取所有证书信息

3. **清晰的字段说明**
   - **站点名称**: 明确说明只支持字母、数字、下划线
   - **远程VPC内网网段**: 详细说明这是云平台的VPC网段，不是OpenVPN虚拟网段，并提供多个云平台示例
   - **.ovpn 内容**: 完整的示例格式

4. **即时验证**
   - 站点名称格式验证
   - CIDR 格式验证
   - .ovpn 内容完整性验证（检查必需的标签）
   - 服务器地址提取验证

5. **详细反馈**
   - 显示提取到的服务器信息
   - 显示配置完成的详细信息
   - 提供重启服务的命令提示

6. **证书状态显示**
   - 已配置：绿色徽章 ✅
   - 未配置：红色徽章 ❌

## 🔍 常见问题

### Q1: "远程VPC内网网段"是什么意思？
A: 这是远程云平台的虚拟私有云（VPC）的内网网段，**不是** OpenVPN 的虚拟网段。

**示例：**
- 阿里云ECS在 VPC 172.16.0.0/16 中，填写 `172.16.0.0/16`
- 华为云ECS在 VPC 192.168.0.0/16 中，填写 `192.168.0.0/16`
- AWS EC2在 VPC 10.0.0.0/16 中，填写 `10.0.0.0/16`

填写后，客户端连接到本网关时，访问这个网段的流量会被路由到远程站点。

### Q2: 为什么不需要手动填写服务器地址、端口、协议了？
A: 系统会自动从 .ovpn 文件中提取这些信息：
- 从 `remote vpn.example.com 1194` 行提取服务器地址和端口
- 从 `proto udp` 行提取协议类型
- 这样避免了重复输入和信息不一致的问题

### Q3: 如果 .ovpn 文件中没有 remote 行怎么办？
A: 标准的 .ovpn 客户端配置文件必须包含 `remote` 行来指定服务器地址。如果没有，请联系远程 VPN 管理员提供完整的客户端配置文件。

### Q4: 我只有证书文件（.crt, .key），没有 .ovpn 文件怎么办？
A: 你需要手动创建 .ovpn 文件。示例模板：

```
client
dev tun
proto udp
remote <远程VPN地址> <端口>
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
verb 3

<ca>
将 ca.crt 文件的内容粘贴到这里
</ca>

<cert>
将 client.crt 文件的内容粘贴到这里
</cert>

<key>
将 client.key 文件的内容粘贴到这里
</key>
```

### Q5: 粘贴 .ovpn 内容后报错 "无法从 .ovpn 文件中提取证书"
A: 检查 .ovpn 文件是否包含以下必需的标签：
- `<ca>...</ca>` - CA证书
- `<cert>...</cert>` - 客户端证书
- `<key>...</key>` - 客户端私钥

如果使用的是文件引用方式（如 `ca ca.crt`），需要转换为内联格式（`<ca>...</ca>`）。

### Q6: 如何获取远程站点的 .ovpn 文件？
A: 联系远程 VPN 管理员，请求生成客户端配置文件。通常步骤：
1. 在远程 VPN 服务器上生成客户端证书
2. 导出为 .ovpn 格式（包含内联证书）
3. 通过安全方式传输给你

### Q7: 站点名称有什么要求？
A: 站点名称：
- ✅ 只能包含字母、数字、下划线、连字符
- ✅ 推荐使用云平台名称，如: `aliyun`, `huawei`, `aws`
- ❌ 不能包含空格、中文、特殊字符
- ❌ 不能与已有站点重名

### Q8: 删除站点会删除证书吗？
A: 是的。删除站点会同时删除所有相关文件，包括配置和证书。删除前请确认。

### Q9: 配置后多久才能生效？
A: 需要重启 OpenVPN 服务：
```bash
docker restart openvpn-gateway
```
重启后，网关会自动连接到已配置的所有站点。

### Q10: 如何验证站点连接成功？
A: 
```bash
# 1. 查看连接日志
docker exec openvpn-gateway tail -100 /var/log/openvpn-huawei.log

# 2. 查看进程
docker exec openvpn-gateway ps aux | grep openvpn

# 3. 测试连接（ping远程VPC内网IP）
docker exec openvpn-gateway ping 172.16.0.1

# 4. 查看路由表
docker exec openvpn-gateway ip route
```

## 🎨 UI 界面说明（v2.0 简化版）

### 添加站点界面（新版）
```
┌───────────────────────────────────────────────────────────────┐
│ 添加新站点                                                    │
│                                                               │
│ 💡 使用说明：只需填写站点名称和远程VPC网段，然后粘贴远程VPN   │
│    提供的 .ovpn 文件内容即可。系统会自动从 .ovpn 文件中提取   │
│    服务器地址、端口、协议、证书等信息。                       │
│                                                               │
│ 站点名称 *                                                    │
│ [huawei________________________________________]              │
│ 自定义站点标识，例如: huawei, aliyun, aws 等                  │
│ (仅支持字母、数字、下划线)                                    │
│                                                               │
│ 远程VPC内网网段 (CIDR) *                                      │
│ [172.16.0.0/16_________________________________]              │
│ 这是远程云平台的VPC内网网段（如阿里云ECS所在的VPC网段），      │
│ 不是OpenVPN的虚拟网段。填写后客户端可以通过本网关访问该网段。  │
│ 示例: 阿里云 172.16.0.0/16, 华为云 192.168.0.0/16             │
│                                                               │
│ .ovpn 配置文件内容 *                                          │
│ ┌───────────────────────────────────────────────────────┐    │
│ │将远程VPN服务器提供的 .ovpn 文件的完整内容粘贴到这里... │    │
│ │                                                       │    │
│ │示例内容：                                             │    │
│ │client                                                 │    │
│ │dev tun                                                │    │
│ │proto udp                                              │    │
│ │remote vpn.example.com 1194                            │    │
│ │...                                                    │    │
│ │<ca>                                                   │    │
│ │-----BEGIN CERTIFICATE-----                            │    │
│ │...                                                    │    │
│ └───────────────────────────────────────────────────────┘    │
│ 📝 打开远程VPN提供的 .ovpn 文件，复制全部内容粘贴到这里。     │
│    系统会自动提取服务器地址、端口、协议和证书信息。           │
│                                                               │
│ [一键添加站点]                                                │
└───────────────────────────────────────────────────────────────┘
```

### 站点列表界面（新版）
```
┌─────────────────────────────────────────────────────────────┐
│ 已配置的站点                                                │
│                                                             │
│ ✅ 完成添加后的操作：                                        │
│ 1. 站点显示为"已配置"状态（绿色徽章）                        │
│ 2. 重启服务: docker restart openvpn-gateway                │
│ 3. 查看日志: docker logs -f openvpn-gateway                │
│ 4. 客户端连接到本网关后，即可访问远程VPC内网                 │
│                                                             │
│ ┌────────┬──────────────┬──────────┬────┬────┬─────────┐   │
│ │站点名称│远程主机       │远程网段   │协议│状态│操作     │   │
│ ├────────┼──────────────┼──────────┼────┼────┼─────────┤   │
│ │huawei  │vpn.hw.com:119│172.16/16 │UDP │✅  │[更新证书]│   │
│ │        │              │          │    │    │[删除]   │   │
│ ├────────┼──────────────┼──────────┼────┼────┼─────────┤   │
│ │aliyun  │vpn.ali.com:11│192.168/16│UDP │✅  │[更新证书]│   │
│ │        │              │          │    │    │[删除]   │   │
│ └────────┴──────────────┴──────────┴────┴────┴─────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 添加成功提示
```
┌─────────────────────────────────────────┐
│  ✅ 站点 huawei 添加成功！              │
│                                         │
│  服务器: vpn.huaweicloud.com:1194       │
│  协议: UDP                              │
│  远程网段: 172.16.0.0/16                │
│                                         │
│  ⚠️ 请重启服务使配置生效:                │
│  docker restart openvpn-gateway         │
└─────────────────────────────────────────┘
```

## 🚀 快速测试

### 完整测试流程（v2.0 简化版）
```bash
# 1. 启动服务
docker-compose -f docker-compose-webui.yml up -d

# 2. 访问 Web UI
# 浏览器打开: http://localhost:8080
# 用户名: admin
# 密码: openvpn
```

**在 Web UI 中操作：**
1. 切换到 **"站点管理"** 标签
2. 填写表单：
   - 站点名称: `huawei`
   - 远程VPC内网网段: `172.16.0.0/16`
   - .ovpn 配置文件内容: 粘贴完整的 .ovpn 文件内容
3. 点击 **"一键添加站点"** 按钮
4. 等待提示 "✅ 站点 huawei 添加成功！"

**重启和验证：**
```bash
# 5. 重启服务
docker restart openvpn-gateway

# 6. 查看启动日志
docker logs openvpn-gateway

# 7. 查看站点连接日志
docker exec openvpn-gateway tail -100 /var/log/openvpn-huawei.log

# 8. 查看连接进程
docker exec openvpn-gateway ps aux | grep openvpn

# 9. 测试连接到远程VPC（替换为实际的远程VPC内网IP）
docker exec openvpn-gateway ping -c 4 172.16.0.1

# 10. 查看路由表
docker exec openvpn-gateway ip route | grep 172.16
```

### 预期结果
如果配置成功，你应该看到：
- ✅ 日志中显示 "Initialization Sequence Completed"
- ✅ 进程列表中有 `openvpn --config /etc/openvpn/sites/huawei.conf`
- ✅ ping 远程VPC内网IP 能够成功
- ✅ 路由表中有指向远程网段的路由

## 📚 相关文档

- [日志和调试指南](LOGGING_GUIDE.md)
- [认证问题修复](FIX_AUTHENTICATION.md)
- [主README](README.md)
