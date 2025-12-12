.PHONY: help install dev build up down restart logs clean test monitor backup

# 默认目标
help:
	@echo "QQ群年度报告分析器 - 常用命令"
	@echo ""
	@echo "部署和运行:"
	@echo "  make install    - 安装依赖"
	@echo "  make dev        - 启动开发环境"
	@echo "  make build      - 构建 Docker 镜像"
	@echo "  make up         - 启动服务（Docker）"
	@echo "  make down       - 停止服务（Docker）"
	@echo "  make restart    - 重启服务（Docker）"
	@echo ""
	@echo "监控和维护:"
	@echo "  make logs       - 查看日志"
	@echo "  make monitor    - 运行监控脚本"
	@echo "  make backup     - 备份数据库"
	@echo "  make migrate    - 运行数据库迁移"
	@echo ""
	@echo "开发和测试:"
	@echo "  make test       - 运行测试"
	@echo "  make demo       - 生成演示数据"
	@echo "  make clean      - 清理临时文件"
	@echo ""

# 安装依赖
install:
	@echo "📦 安装 Python 依赖..."
	pip install -r requirements.txt
	pip install -r backend/requirements.txt
	@echo "📦 安装前端依赖..."
	cd frontend && npm install
	@echo "✅ 依赖安装完成"

# 开发模式
dev:
	@echo "🚀 启动开发环境..."
	@echo "请在不同终端运行以下命令:"
	@echo "  终端 1: cd backend && python app.py"
	@echo "  终端 2: cd frontend && npm run dev"

# 构建 Docker 镜像
build:
	@echo "🔨 构建 Docker 镜像..."
	docker-compose build --no-cache
	@echo "✅ 构建完成"

# 启动服务
up:
	@echo "🚀 启动服务..."
	docker-compose up -d
	@sleep 5
	@echo "📊 初始化数据库..."
	docker exec qq-reports-backend python init_db.py || true
	@echo "✅ 服务已启动"
	@docker-compose ps

# 停止服务
down:
	@echo "⏹️  停止服务..."
	docker-compose down
	@echo "✅ 服务已停止"

# 重启服务
restart:
	@echo "🔄 重启服务..."
	docker-compose restart
	@echo "✅ 服务已重启"

# 查看日志
logs:
	docker-compose logs -f

# 监控
monitor:
	@echo "🔍 运行监控脚本..."
	python monitor.py

# 备份数据库
backup:
	@echo "💾 备份数据库..."
	@mkdir -p backups
	@TIMESTAMP=$$(date +%Y%m%d_%H%M%S) && \
	docker exec qq-reports-mysql mysqldump -uroot -p$${MYSQL_PASSWORD:-changeme} qq_reports > backups/backup_$$TIMESTAMP.sql
	@echo "✅ 备份完成: backups/backup_$$(date +%Y%m%d_%H%M%S).sql"

# 数据库迁移
migrate:
	@echo "🔄 运行数据库迁移..."
	docker exec qq-reports-backend python migrate_db.py || python backend/migrate_db.py
	@echo "✅ 迁移完成"

# 生成演示数据
demo:
	@echo "🎨 生成演示数据..."
	python generate_demo_data.py
	@echo "✅ 演示数据已生成: demo_chat.json"

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.log" -delete 2>/dev/null || true
	rm -rf runtime_outputs/temp/* 2>/dev/null || true
	@echo "✅ 清理完成"

# 测试
test:
	@echo "🧪 运行测试..."
	@echo "⚠️  暂未实现测试功能"

# 完整部署流程
deploy: build up
	@echo ""
	@echo "=========================================="
	@echo "  ✅ 部署完成！"
	@echo "=========================================="
	@echo ""
	@echo "访问地址:"
	@echo "  前端: http://localhost"
	@echo "  后端: http://localhost:5000"
	@echo ""
