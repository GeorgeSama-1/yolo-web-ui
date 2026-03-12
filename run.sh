#!/bin/bash

# 绝缘子检测 Web UI 启动脚本

echo "======================================"
echo "   绝缘子检测 Web UI 启动中..."
echo "======================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
pip install -r requirements.txt -q

# 创建必要的目录
echo "创建目录..."
mkdir -p uploads outputs

# 启动服务
echo ""
echo "======================================"
echo "   服务启动成功！"
echo "======================================"
echo ""
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务"
echo ""

python3 app.py
