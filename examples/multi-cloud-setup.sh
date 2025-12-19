#!/bin/bash

#
# 多云网络主入口 VPN 网关快速配置示例脚本
# 此脚本演示如何配置一个连接华为云、AWS、GCP 的主入口 VPN
#

set -e

# 配置变量
OVPN_DATA="ovpn-gateway-data"
SERVER_URL="udp://vpn.example.com"  # 修改为你的服务器域名或 IP

# 云平台配置
HUAWEI_HOST="vpn.huaweicloud.example.com"
HUAWEI_PORT="1194"
HUAWEI_SUBNET="172.16.0.0/16"

AWS_HOST="vpn.aws.example.com"
AWS_PORT="1194"
AWS_SUBNET="10.0.0.0/16"

GCP_HOST="vpn.gcp.example.com"
GCP_PORT="1194"
GCP_SUBNET="192.168.0.0/16"

echo "=========================================="
echo "  多云网络主入口 VPN 网关配置"
echo "=========================================="
echo ""

# 步骤 1: 创建数据卷
echo "步骤 1: 创建数据卷..."
if ! docker volume inspect $OVPN_DATA > /dev/null 2>&1; then
    docker volume create --name $OVPN_DATA
    echo "  ✓ 数据卷已创建: $OVPN_DATA"
else
    echo "  ℹ 数据卷已存在: $OVPN_DATA"
fi

# 步骤 2: 生成配置
echo ""
echo "步骤 2: 生成 OpenVPN 配置..."
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_genconfig -u $SERVER_URL
echo "  ✓ 配置已生成"

# 步骤 3: 初始化 PKI
echo ""
echo "步骤 3: 初始化 PKI（证书系统）..."
echo "  ⚠ 请输入 CA 密码（建议使用强密码）"
docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \
    ovpn_initpki
echo "  ✓ PKI 已初始化"

# 步骤 4: 初始化网关
echo ""
echo "步骤 4: 初始化网关配置..."
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_setup_gateway -i
echo "  ✓ 网关已初始化"

# 步骤 5: 添加站点
echo ""
echo "步骤 5: 添加远程云平台站点..."

echo "  添加华为云站点..."
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_add_remote_site \
    -n huawei \
    -h $HUAWEI_HOST \
    -p $HUAWEI_PORT \
    -s $HUAWEI_SUBNET

echo "  添加 AWS 站点..."
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_add_remote_site \
    -n aws \
    -h $AWS_HOST \
    -p $AWS_PORT \
    -s $AWS_SUBNET

echo "  添加 GCP 站点..."
docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \
    ovpn_add_remote_site \
    -n gcp \
    -h $GCP_HOST \
    -p $GCP_PORT \
    -s $GCP_SUBNET

echo "  ✓ 所有站点已添加"

# 步骤 6: 配置证书提醒
echo ""
echo "=========================================="
echo "  ⚠ 重要提示"
echo "=========================================="
echo ""
echo "现在需要为每个远程站点配置证书和密钥。"
echo "请按照以下步骤操作："
echo ""
echo "1. 从各云平台获取 VPN 客户端配置文件（.ovpn）"
echo ""
echo "2. 编辑站点配置文件，添加证书内容："
echo ""
echo "   docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn bash"
echo ""
echo "   然后编辑以下文件："
echo "   - /etc/openvpn/sites/huawei.conf"
echo "   - /etc/openvpn/sites/aws.conf"
echo "   - /etc/openvpn/sites/gcp.conf"
echo ""
echo "   在每个文件中添加证书内容（参考文档中的示例）"
echo ""
echo "3. 配置完成后，继续执行："
echo ""
echo "   # 更新路由配置"
echo "   docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_update_routes"
echo ""
echo "   # 重新生成服务器配置"
echo "   docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn ovpn_genconfig -u $SERVER_URL"
echo ""
echo "   # 启动主入口 VPN 服务器"
echo "   docker run -v $OVPN_DATA:/etc/openvpn -d -p 1194:1194/udp \\"
echo "     --cap-add=NET_ADMIN --name openvpn-gateway kylemanna/openvpn"
echo ""
echo "   # 生成客户端配置"
echo "   docker run -v $OVPN_DATA:/etc/openvpn --rm -it kylemanna/openvpn \\"
echo "     easyrsa build-client-full CLIENTNAME nopass"
echo ""
echo "   docker run -v $OVPN_DATA:/etc/openvpn --rm kylemanna/openvpn \\"
echo "     ovpn_getclient CLIENTNAME > CLIENTNAME.ovpn"
echo ""
echo "=========================================="
echo "配置脚本执行完成！请按照上述提示完成证书配置。"
echo "=========================================="

