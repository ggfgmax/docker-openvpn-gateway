#!/bin/bash

# 提交到 GitHub 的脚本
# 执行前请确保已经配置 GitHub 认证

echo "=========================================="
echo "  推送代码到 GitHub"
echo "=========================================="
echo ""
echo "仓库地址: https://github.com/ggfgmax/docker-openvpn-gateway.git"
echo ""

# 检查 Git 状态
echo "1. 检查 Git 状态..."
git status

echo ""
echo "2. 推送到 GitHub..."
git push -u origin main

echo ""
echo "=========================================="
echo "完成！"
echo ""
echo "访问您的仓库:"
echo "https://github.com/ggfgmax/docker-openvpn-gateway"
echo "=========================================="

