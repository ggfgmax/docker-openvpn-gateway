#!/bin/bash

#
# 构建多云网络主入口 VPN 网关镜像
#

set -e

IMAGE_NAME="${1:-openvpn-gateway}"
IMAGE_TAG="${2:-latest}"

echo "=========================================="
echo "  构建 OpenVPN 多云网络主入口网关"
echo "=========================================="
echo ""
echo "镜像名称: $IMAGE_NAME:$IMAGE_TAG"
echo ""

# 构建镜像
docker build -t "$IMAGE_NAME:$IMAGE_TAG" .

echo ""
echo "=========================================="
echo "✅ 镜像构建完成！"
echo ""
echo "下一步:"
echo ""
echo "1. 初始化配置:"
echo "   docker volume create openvpn-data"
echo "   docker run -v openvpn-data:/etc/openvpn --rm $IMAGE_NAME:$IMAGE_TAG \\"
echo "       ovpn_genconfig -u udp://vpn.yourdomain.com"
echo "   docker run -v openvpn-data:/etc/openvpn --rm -it $IMAGE_NAME:$IMAGE_TAG \\"
echo "       ovpn_initpki"
echo ""
echo "2. 启动 Web 管理界面:"
echo "   docker-compose -f docker-compose-webui.yml up -d"
echo "   浏览器访问: http://服务器IP:8080"
echo ""
echo "3. 查看文档:"
echo "   docs/quickstart-webui.md"
echo "=========================================="

