#!/bin/bash

# QQ群年度报告分析器 - 快速启动脚本
# 一键部署线上版本

set -e

echo "========================================"
echo "  QQ群年度报告分析器 - 快速部署"
echo "========================================"
echo ""

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ 错误: 未安装 Docker Compose"
    echo "请先安装 Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 使用新版或旧版 docker-compose 命令
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

echo "✅ Docker 环境检查通过"
echo ""

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建配置文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件"
    echo ""
    echo "⚠️  注意：请编辑 .env 文件配置以下内容："
    echo "   1. 修改 MYSQL_PASSWORD（数据库密码）"
    echo "   2. 修改 FLASK_SECRET_KEY（应用密钥）"
    echo "   3. （可选）配置 OSS 和 OpenAI"
    echo ""
    
    # 生成随机密钥
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        MYSQL_PASSWORD=$(openssl rand -base64 16 | tr -d '=+/')
        
        # 更新 .env 文件 (跨平台兼容)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/FLASK_SECRET_KEY=.*/FLASK_SECRET_KEY=${SECRET_KEY}/" .env
            sed -i '' "s/MYSQL_PASSWORD=.*/MYSQL_PASSWORD=${MYSQL_PASSWORD}/" .env
        else
            # Linux
            sed -i "s/FLASK_SECRET_KEY=.*/FLASK_SECRET_KEY=${SECRET_KEY}/" .env
            sed -i "s/MYSQL_PASSWORD=.*/MYSQL_PASSWORD=${MYSQL_PASSWORD}/" .env
        fi
        
        echo "✅ 已自动生成安全的密钥"
    else
        echo "⚠️  请手动设置安全的密钥"
    fi
    
    echo ""
    read -p "按回车继续，或按 Ctrl+C 退出编辑配置文件..."
    echo ""
fi

# 选择部署模式
echo "请选择部署模式："
echo "  1. 开发模式（不需要 OSS，使用本地存储）"
echo "  2. 生产模式（需要配置 OSS）"
echo ""
read -p "请输入选择 [1/2]: " MODE

if [ "$MODE" = "1" ]; then
    echo "SKIP_OSS=1" >> .env
    echo "✅ 已设置为开发模式（本地存储）"
elif [ "$MODE" = "2" ]; then
    echo "SKIP_OSS=0" >> .env
    echo "✅ 已设置为生产模式"
    echo "⚠️  请确保已在 .env 中配置 OSS 相关参数"
else
    echo "使用默认配置"
fi

echo ""
echo "🚀 开始构建和启动服务..."
echo ""

# 停止旧容器
echo "停止旧容器..."
$DOCKER_COMPOSE down 2>/dev/null || true

# 构建镜像
echo ""
echo "📦 构建 Docker 镜像（首次运行可能需要几分钟）..."
$DOCKER_COMPOSE build

# 启动服务
echo ""
echo "🚀 启动服务..."
$DOCKER_COMPOSE up -d

# 等待服务启动
echo ""
echo "⏳ 等待服务启动..."
sleep 5

# 初始化数据库
echo ""
echo "📊 初始化数据库..."
docker exec qq-reports-backend python init_db.py || true

# 检查服务状态
echo ""
echo "🔍 检查服务状态..."
$DOCKER_COMPOSE ps

# 获取服务地址
FRONTEND_PORT=$(grep FRONTEND_PORT .env 2>/dev/null | cut -d'=' -f2)
FRONTEND_PORT=${FRONTEND_PORT:-80}

BACKEND_PORT=$(grep BACKEND_PORT .env 2>/dev/null | cut -d'=' -f2)
BACKEND_PORT=${BACKEND_PORT:-5000}

echo ""
echo "========================================"
echo "  ✅ 部署完成！"
echo "========================================"
echo ""
echo "📱 访问地址："
echo "   前端：http://localhost:${FRONTEND_PORT}"
echo "   后端：http://localhost:${BACKEND_PORT}"
echo ""
echo "📝 常用命令："
echo "   查看日志：$DOCKER_COMPOSE logs -f"
echo "   停止服务：$DOCKER_COMPOSE down"
echo "   重启服务：$DOCKER_COMPOSE restart"
echo "   查看状态：$DOCKER_COMPOSE ps"
echo ""
echo "🎉 现在可以打开浏览器访问了！"
echo ""
