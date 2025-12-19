#!/bin/bash

#
# 测试多云网络连通性脚本
# 用于验证主入口 VPN 网关是否正确配置
#

set -e

CONTAINER_NAME="${1:-openvpn-gateway}"

echo "=========================================="
echo "  多云网络连通性测试"
echo "=========================================="
echo ""

# 检查容器是否运行
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "错误: 容器 $CONTAINER_NAME 未运行"
    echo "请先启动容器："
    echo "  docker run -v ovpn-gateway-data:/etc/openvpn -d -p 1194:1194/udp \\"
    echo "    --cap-add=NET_ADMIN --name openvpn-gateway kylemanna/openvpn"
    exit 1
fi

echo "✓ 容器正在运行: $CONTAINER_NAME"
echo ""

# 检查 IP 转发
echo "检查 IP 转发状态..."
IPV4_FORWARD=$(docker exec $CONTAINER_NAME sysctl -n net.ipv4.ip_forward)
if [ "$IPV4_FORWARD" == "1" ]; then
    echo "  ✓ IPv4 转发已启用"
else
    echo "  ✗ IPv4 转发未启用"
fi
echo ""

# 检查隧道接口
echo "检查隧道接口..."
docker exec $CONTAINER_NAME ip link show | grep -E "tun|tap" || echo "  ⚠ 未找到隧道接口"
echo ""

# 检查站点连接状态
echo "检查站点连接状态..."
docker exec $CONTAINER_NAME ovpn_list_sites
echo ""

# 检查 iptables 规则
echo "检查 iptables NAT 规则..."
docker exec $CONTAINER_NAME iptables -t nat -L POSTROUTING -n | grep -E "MASQUERADE|tun" || echo "  ⚠ 未找到 NAT 规则"
echo ""

echo "检查 iptables 转发规则..."
docker exec $CONTAINER_NAME iptables -L FORWARD -n | grep -E "tun|ACCEPT" || echo "  ⚠ 未找到转发规则"
echo ""

# 检查路由表
echo "检查路由表..."
docker exec $CONTAINER_NAME ip route show
echo ""

# 读取站点信息并测试连通性
SITE_DIR="/etc/openvpn/sites"
echo "测试远程网段连通性..."
echo ""

for site in huawei aws gcp; do
    if docker exec $CONTAINER_NAME test -f "$SITE_DIR/${site}.info"; then
        echo "测试站点: $site"
        
        # 读取远程网段
        REMOTE_SUBNET=$(docker exec $CONTAINER_NAME grep REMOTE_SUBNET "$SITE_DIR/${site}.info" | cut -d= -f2)
        
        # 提取第一个可用 IP（网段 + 1）
        IFS='/' read -r NETWORK MASK <<< "$REMOTE_SUBNET"
        IFS='.' read -r o1 o2 o3 o4 <<< "$NETWORK"
        TEST_IP="$o1.$o2.$o3.$((o4 + 1))"
        
        echo "  远程网段: $REMOTE_SUBNET"
        echo "  测试 IP: $TEST_IP"
        
        # Ping 测试（3次，超时3秒）
        if docker exec $CONTAINER_NAME ping -c 3 -W 3 $TEST_IP > /dev/null 2>&1; then
            echo "  ✓ 连通性测试成功"
        else
            echo "  ✗ 连通性测试失败（这可能是正常的，如果远程主机禁用了 ICMP）"
        fi
        echo ""
    else
        echo "  ⚠ 站点 $site 未配置"
    fi
done

echo "=========================================="
echo "测试完成！"
echo ""
echo "提示："
echo "- 如果连通性测试失败，可能是因为远程主机禁用了 ICMP ping"
echo "- 可以尝试使用其他方式测试，如 telnet、curl 等"
echo "- 查看详细日志: docker logs $CONTAINER_NAME"
echo "=========================================="

