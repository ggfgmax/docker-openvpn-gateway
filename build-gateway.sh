#!/bin/bash

#
# 构建多云网络主入口 VPN 网关镜像
#

set -e

IMAGE_NAME="${1:-openvpn-gateway}"
IMAGE_TAG="${2:-latest}"

echo "=========================================="
echo "  构建多云网络主入口 VPN 网关镜像"
echo "=========================================="
echo ""
echo "镜像名称: $IMAGE_NAME:$IMAGE_TAG"
echo ""

# 构建镜像
docker build -t "$IMAGE_NAME:$IMAGE_TAG" .

echo ""
echo "=========================================="
echo "镜像构建完成！"
echo ""
echo "接下来可以使用以下命令："
echo ""
echo "1. 快速配置（推荐）："
echo "   docker run -v \$PWD:/tmp --rm $IMAGE_NAME:$IMAGE_TAG \\"
echo "       cp /usr/share/doc/openvpn/examples/multi-cloud-setup.sh /tmp/"
echo "   bash multi-cloud-setup.sh"
echo ""
echo "2. 手动配置："
echo "   参考 README-MULTI-CLOUD.md 文档"
echo ""
echo "3. 查看文档："
echo "   docker run --rm $IMAGE_NAME:$IMAGE_TAG cat /usr/share/doc/openvpn/docs/multi-cloud-gateway.md"
echo "=========================================="

