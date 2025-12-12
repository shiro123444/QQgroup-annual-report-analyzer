@echo off
chcp 65001 >nul
REM QQ群年度报告分析器 - Windows 快速启动脚本
REM 一键部署线上版本

echo ========================================
echo   QQ群年度报告分析器 - 快速部署
echo ========================================
echo.

REM 检查 Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [X] 错误: 未安装 Docker
    echo 请先安装 Docker Desktop - https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 检查 Docker Compose
docker compose version >nul 2>nul
if %errorlevel% equ 0 (
    set DOCKER_COMPOSE=docker compose
) else (
    docker-compose version >nul 2>nul
    if %errorlevel% equ 0 (
        set DOCKER_COMPOSE=docker-compose
    ) else (
        echo [X] 错误: 未安装 Docker Compose
        echo 请先安装 Docker Compose
        pause
        exit /b 1
    )
)

echo ✅ Docker 环境检查通过
echo.

REM 检查 .env 文件
if not exist .env (
    echo 📝 创建配置文件...
    copy .env.example .env
    echo ✅ 已创建 .env 文件
    echo.
    echo ⚠️  注意: 请编辑 .env 文件配置以下内容:
    echo    1. 修改 MYSQL_PASSWORD (数据库密码)
    echo    2. 修改 FLASK_SECRET_KEY (应用密钥)
    echo    3. (可选) 配置 OSS 和 OpenAI
    echo.
    echo 按任意键继续...
    pause >nul
)

REM 选择部署模式
echo 请选择部署模式:
echo   1. 开发模式 (不需要 OSS, 使用本地存储)
echo   2. 生产模式 (需要配置 OSS)
echo.
set /p MODE="请输入选择 [1/2]: "

if "%MODE%"=="1" (
    echo SKIP_OSS=1>> .env
    echo [OK] 已设置为开发模式 (本地存储)
) else if "%MODE%"=="2" (
    echo SKIP_OSS=0>> .env
    echo ✅ 已设置为生产模式
    echo [!] 请确保已在 .env 中配置 OSS 相关参数
) else (
    echo 使用默认配置
)

echo.
echo 🚀 开始构建和启动服务...
echo.

REM 停止旧容器
echo 停止旧容器...
%DOCKER_COMPOSE% down 2>nul

REM 构建镜像
echo.
echo [BUILD] 构建 Docker 镜像 (首次运行可能需要几分钟)...
%DOCKER_COMPOSE% build

REM 启动服务
echo.
echo 🚀 启动服务...
%DOCKER_COMPOSE% up -d

REM 等待服务启动
echo.
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

REM 初始化数据库
echo.
echo 📊 初始化数据库...
docker exec qq-reports-backend python init_db.py

REM 检查服务状态
echo.
echo 🔍 检查服务状态...
%DOCKER_COMPOSE% ps

REM 获取服务地址
for /f "tokens=2 delims==" %%a in ('findstr /C:"FRONTEND_PORT" .env 2^>nul') do set FRONTEND_PORT=%%a
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=80

for /f "tokens=2 delims==" %%a in ('findstr /C:"BACKEND_PORT" .env 2^>nul') do set BACKEND_PORT=%%a
if "%BACKEND_PORT%"=="" set BACKEND_PORT=5000

echo.
echo ========================================
echo   ✅ 部署完成！
echo ========================================
echo.
echo 📱 访问地址:
echo    前端: http://localhost:%FRONTEND_PORT%
echo    后端: http://localhost:%BACKEND_PORT%
echo.
echo 📝 常用命令:
echo    查看日志: %DOCKER_COMPOSE% logs -f
echo    停止服务: %DOCKER_COMPOSE% down
echo    重启服务: %DOCKER_COMPOSE% restart
echo    查看状态: %DOCKER_COMPOSE% ps
echo.
echo 🎉 现在可以打开浏览器访问了！
echo.
pause
