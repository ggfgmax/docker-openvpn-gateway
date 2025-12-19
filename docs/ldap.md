# LDAP 认证配置指南

## 概述

本指南介绍如何为 OpenVPN 配置 LDAP 认证，允许用户使用企业 LDAP/AD 账户进行身份验证。

## 功能特性

- ✅ 支持标准 LDAP 服务器（OpenLDAP, 389 Directory Server 等）
- ✅ 支持 Active Directory
- ✅ 支持 LDAP 和 LDAPS（TLS 加密）
- ✅ 支持绑定 DN 认证
- ✅ 支持自定义用户过滤器
- ✅ 集成到 OpenVPN PAM 认证

## 快速开始

### 1. 配置 LDAP 认证

```bash
docker run -v ovpn-data:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_config_ldap \
    -h ldap.company.com \
    -b "dc=company,dc=com" \
    -D "cn=admin,dc=company,dc=com" \
    -w "admin_password"
```

### 2. 启用 LDAP 认证的 OpenVPN 配置

重新生成配置时添加 `-2` 参数启用用户认证：

```bash
docker run -v ovpn-data:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u udp://vpn.company.com -2
```

或者手动编辑 `openvpn.conf`，添加以下内容：

```
plugin /usr/lib/openvpn/plugins/openvpn-plugin-auth-pam.so openvpn
username-as-common-name
```

### 3. 重启 OpenVPN 服务

```bash
docker restart openvpn-container
```

## 详细配置

### 基本 LDAP 配置

```bash
ovpn_config_ldap \
    -h ldap.example.com \           # LDAP 服务器地址
    -b "dc=example,dc=com" \        # Base DN
    -D "cn=readonly,dc=example,dc=com" \  # 绑定 DN（可选）
    -w "password"                   # 绑定密码（可选）
```

### Active Directory 配置

```bash
ovpn_config_ldap \
    -h ad.company.com \
    -b "dc=company,dc=com" \
    -D "CN=Service Account,OU=Service Accounts,DC=company,DC=com" \
    -w "service_password" \
    -f "(&(objectClass=user)(sAMAccountName=%u))" \
    -s sAMAccountName
```

### LDAPS（TLS 加密）配置

```bash
ovpn_config_ldap \
    -h ldaps.example.com \
    -b "dc=example,dc=com" \
    -S \                            # 启用 LDAPS
    -D "cn=admin,dc=example,dc=com" \
    -w "password"
```

### 自定义端口

```bash
ovpn_config_ldap \
    -h ldap.example.com \
    -p 10389 \                      # 自定义端口
    -b "dc=example,dc=com"
```

### 自定义用户过滤器

```bash
ovpn_config_ldap \
    -h ldap.example.com \
    -b "ou=users,dc=example,dc=com" \
    -f "(&(objectClass=inetOrgPerson)(mail=%u@example.com))" \
    -s mail
```

## 配置参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `-h` | LDAP 服务器地址 | `ldap.company.com` |
| `-b` | Base DN | `dc=company,dc=com` |
| `-D` | 绑定 DN（可选） | `cn=admin,dc=company,dc=com` |
| `-w` | 绑定密码（可选） | `password` |
| `-f` | 用户过滤器 | `(&(objectClass=person)(uid=%u))` |
| `-s` | 搜索属性 | `uid` 或 `sAMAccountName` |
| `-p` | LDAP 端口 | `389` (LDAP) 或 `636` (LDAPS) |
| `-S` | 启用 LDAPS | - |
| `-t` | 超时时间（秒） | `15` |

### 用户过滤器变量

- `%u` - 用户输入的用户名

### 常用过滤器示例

**OpenLDAP (posixAccount)**:
```
(&(objectClass=posixAccount)(uid=%u))
```

**OpenLDAP (inetOrgPerson)**:
```
(&(objectClass=inetOrgPerson)(uid=%u))
```

**Active Directory (用户名)**:
```
(&(objectClass=user)(sAMAccountName=%u))
```

**Active Directory (邮箱)**:
```
(&(objectClass=user)(mail=%u))
```

**限制特定组的成员**:
```
(&(objectClass=user)(sAMAccountName=%u)(memberOf=CN=VPN Users,OU=Groups,DC=company,DC=com))
```

## 客户端配置

启用 LDAP 认证后，客户端配置文件需要添加用户认证参数。

### 生成客户端配置

**不需要客户端证书的配置**（仅用户名密码）:

1. 编辑 `ovpn_getclient` 脚本或手动生成不包含证书的配置

2. 客户端配置文件示例：

```
client
dev tun
proto udp
remote vpn.company.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server

# 使用用户名密码认证
auth-user-pass
auth-nocache

# CA 证书（仅验证服务器）
<ca>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</ca>
```

**同时使用证书和用户名密码**（双因素认证）:

保留证书配置，添加：
```
auth-user-pass
```

## 测试 LDAP 连接

### 使用 ldapsearch 测试

```bash
# 进入容器
docker exec -it openvpn-container bash

# 测试匿名绑定
ldapsearch -x -H ldap://ldap.company.com \
    -b "dc=company,dc=com" \
    "(uid=testuser)"

# 测试认证绑定
ldapsearch -x -H ldap://ldap.company.com \
    -b "dc=company,dc=com" \
    -D "cn=admin,dc=company,dc=com" \
    -w "password" \
    "(uid=testuser)"

# 测试 LDAPS
ldapsearch -x -H ldaps://ldaps.company.com \
    -b "dc=company,dc=com" \
    "(uid=testuser)"
```

## 故障排查

### 1. 连接失败

**检查 LDAP 服务器可达性**:
```bash
docker exec openvpn-container ping ldap.company.com
docker exec openvpn-container telnet ldap.company.com 389
```

**检查防火墙**:
- LDAP: 端口 389
- LDAPS: 端口 636

### 2. 认证失败

**检查 Base DN**:
```bash
ldapsearch -x -H ldap://ldap.company.com -b "" -s base namingContexts
```

**检查用户存在**:
```bash
ldapsearch -x -H ldap://ldap.company.com \
    -b "dc=company,dc=com" \
    "(uid=username)" dn
```

**检查用户可以认证**:
```bash
ldapsearch -x -H ldap://ldap.company.com \
    -b "dc=company,dc=com" \
    -D "uid=username,ou=users,dc=company,dc=com" \
    -w "user_password" \
    "(uid=username)"
```

### 3. 查看日志

**OpenVPN 日志**:
```bash
docker logs openvpn-container
```

**PAM 日志** (容器内):
```bash
tail -f /var/log/messages
# 或
journalctl -u openvpn -f
```

### 4. 常见错误

**"LDAP bind failed"**:
- 检查绑定 DN 和密码是否正确
- 检查 LDAP 服务器是否允许绑定

**"User not found"**:
- 检查 Base DN 是否正确
- 检查用户过滤器是否匹配
- 检查搜索属性是否正确

**"TLS connection failed"**:
- 检查 LDAPS 端口是否正确（636）
- 检查证书是否有效
- 尝试禁用证书验证（仅测试）

## 安全建议

1. **使用只读账户**: 绑定 DN 应该是只读服务账户
2. **使用 LDAPS**: 生产环境建议使用 TLS 加密
3. **限制访问**: 使用组过滤器限制只有特定组成员才能访问
4. **定期轮换密码**: 定期更换服务账户密码
5. **监控日志**: 监控认证失败的日志，发现异常登录

## 高级配置

### 多个 LDAP 服务器（高可用）

编辑 `/etc/openvpn/ldap.conf`:

```
URI ldap://ldap1.company.com ldap://ldap2.company.com
BASE dc=company,dc=com
```

### 使用 LDAP 组授权

配置只允许特定组的成员访问：

```bash
ovpn_config_ldap \
    -h ldap.company.com \
    -b "dc=company,dc=com" \
    -f "(&(objectClass=user)(sAMAccountName=%u)(memberOf=CN=VPN Users,OU=Groups,DC=company,DC=com))"
```

### 结合证书和 LDAP（双因素认证）

1. 正常生成客户端证书
2. 启用 LDAP 认证
3. 客户端需要同时提供：
   - 客户端证书
   - 用户名密码

## 示例配置文件

### OpenLDAP 示例

**LDAP 配置** (`/etc/openvpn/ldap.conf`):
```
URI ldap://ldap.example.com:389
BASE ou=users,dc=example,dc=com
BINDDN cn=readonly,dc=example,dc=com
BINDPW readonly_password
TIMEOUT 15
SCOPE sub
FILTER (&(objectClass=posixAccount)(uid=%u))
```

**PAM 配置** (`/etc/pam.d/openvpn`):
```
auth required pam_ldap.so
account required pam_ldap.so
```

### Active Directory 示例

**LDAP 配置**:
```
URI ldap://ad.company.com:389
BASE dc=company,dc=com
BINDDN CN=VPN Service,OU=Service Accounts,DC=company,DC=com
BINDPW service_password
TIMEOUT 15
SCOPE sub
FILTER (&(objectClass=user)(sAMAccountName=%u)(memberOf=CN=VPN Users,OU=Security Groups,DC=company,DC=com))
```

## 与其他认证方式结合

### LDAP + OTP（双因素认证）

同时启用 LDAP 和 OTP:

```bash
# 配置 LDAP
ovpn_config_ldap -h ldap.company.com -b "dc=company,dc=com"

# 配置 OTP
ovpn_otp_user username

# 生成配置时启用双因素认证
ovpn_genconfig -u udp://vpn.company.com -2
```

客户端登录时需要：
- 用户名: LDAP 用户名
- 密码: LDAP密码 + OTP代码（拼接在一起）

## 参考资料

- [OpenVPN PAM Plugin](https://github.com/threerings/openvpn-pam-plugin)
- [pam_ldap Documentation](http://www.padl.com/OSS/pam_ldap.html)
- [OpenLDAP Documentation](https://www.openldap.org/doc/)
- [Active Directory LDAP Syntax](https://docs.microsoft.com/en-us/windows/win32/adsi/search-filter-syntax)

