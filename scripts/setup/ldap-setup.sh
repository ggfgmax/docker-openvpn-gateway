#!/bin/bash

#
# LDAP 认证快速配置示例脚本
#

set -e

# 配置变量 - 请根据实际情况修改
OVPN_DATA="${OVPN_DATA:-ovpn-data}"
SERVER_URL="${SERVER_URL:-udp://vpn.example.com}"

# LDAP 配置 - OpenLDAP 示例
LDAP_TYPE="${LDAP_TYPE:-openldap}"  # openldap 或 ad (Active Directory)

# OpenLDAP 配置
OPENLDAP_HOST="ldap.example.com"
OPENLDAP_PORT="389"
OPENLDAP_BASE_DN="dc=example,dc=com"
OPENLDAP_BIND_DN="cn=readonly,dc=example,dc=com"
OPENLDAP_BIND_PASSWORD="readonly_password"
OPENLDAP_FILTER="(&(objectClass=posixAccount)(uid=%u))"
OPENLDAP_SEARCH_ATTR="uid"

# Active Directory 配置
AD_HOST="ad.company.com"
AD_PORT="389"
AD_BASE_DN="dc=company,dc=com"
AD_BIND_DN="CN=VPN Service,OU=Service Accounts,DC=company,DC=com"
AD_BIND_PASSWORD="service_password"
AD_FILTER="(&(objectClass=user)(sAMAccountName=%u)(memberOf=CN=VPN Users,OU=Security Groups,DC=company,DC=com))"
AD_SEARCH_ATTR="sAMAccountName"

echo "=========================================="
echo "  LDAP 认证快速配置脚本"
echo "=========================================="
echo ""
echo "LDAP 类型: $LDAP_TYPE"
echo "数据卷: $OVPN_DATA"
echo "服务器 URL: $SERVER_URL"
echo ""

# 根据类型选择配置
if [ "$LDAP_TYPE" == "ad" ]; then
    echo "使用 Active Directory 配置..."
    LDAP_HOST="$AD_HOST"
    LDAP_PORT="$AD_PORT"
    LDAP_BASE_DN="$AD_BASE_DN"
    LDAP_BIND_DN="$AD_BIND_DN"
    LDAP_BIND_PASSWORD="$AD_BIND_PASSWORD"
    LDAP_FILTER="$AD_FILTER"
    LDAP_SEARCH_ATTR="$AD_SEARCH_ATTR"
else
    echo "使用 OpenLDAP 配置..."
    LDAP_HOST="$OPENLDAP_HOST"
    LDAP_PORT="$OPENLDAP_PORT"
    LDAP_BASE_DN="$OPENLDAP_BASE_DN"
    LDAP_BIND_DN="$OPENLDAP_BIND_DN"
    LDAP_BIND_PASSWORD="$OPENLDAP_BIND_PASSWORD"
    LDAP_FILTER="$OPENLDAP_FILTER"
    LDAP_SEARCH_ATTR="$OPENLDAP_SEARCH_ATTR"
fi

echo ""
echo "LDAP 配置详情:"
echo "  服务器: $LDAP_HOST:$LDAP_PORT"
echo "  Base DN: $LDAP_BASE_DN"
echo "  绑定 DN: $LDAP_BIND_DN"
echo "  过滤器: $LDAP_FILTER"
echo "  搜索属性: $LDAP_SEARCH_ATTR"
echo ""

read -p "是否继续? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# 检查数据卷是否存在
if ! docker volume inspect $OVPN_DATA > /dev/null 2>&1; then
    echo "错误: 数据卷 $OVPN_DATA 不存在"
    echo "请先运行基本配置脚本或手动创建数据卷"
    exit 1
fi

# 配置 LDAP
echo ""
echo "步骤 1: 配置 LDAP 认证..."
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_config_ldap \
    -h "$LDAP_HOST" \
    -p "$LDAP_PORT" \
    -b "$LDAP_BASE_DN" \
    -D "$LDAP_BIND_DN" \
    -w "$LDAP_BIND_PASSWORD" \
    -f "$LDAP_FILTER" \
    -s "$LDAP_SEARCH_ATTR"

echo "  ✓ LDAP 配置完成"

# 重新生成配置启用 LDAP 认证
echo ""
echo "步骤 2: 重新生成 OpenVPN 配置（启用 LDAP 认证）..."
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u "$SERVER_URL" -2

echo "  ✓ OpenVPN 配置已更新"

# 提示重启
echo ""
echo "=========================================="
echo "LDAP 认证配置完成！"
echo ""
echo "下一步:"
echo "1. 重启 OpenVPN 服务:"
echo "   docker restart openvpn-container"
echo ""
echo "2. 测试 LDAP 认证:"
echo "   a. 生成不包含证书的客户端配置（仅用户名密码）"
echo "   b. 或使用现有证书 + 用户名密码（双因素认证）"
echo ""
echo "3. 客户端连接时将提示输入:"
echo "   - 用户名: LDAP 用户名（如: $LDAP_SEARCH_ATTR）"
echo "   - 密码: LDAP 密码"
echo ""
echo "4. 测试 LDAP 连接:"
echo "   docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn bash"
echo "   ldapsearch -x -H ldap://$LDAP_HOST:$LDAP_PORT \\"
echo "       -b \"$LDAP_BASE_DN\" \\"
echo "       -D \"$LDAP_BIND_DN\" \\"
echo "       -w \"$LDAP_BIND_PASSWORD\" \\"
echo "       \"(uid=testuser)\""
echo "=========================================="

