# Docker 快速部署说明

## 最简单的部署方法

### 第一步：安装 Docker

**Windows/Mac:**
1. 下载 [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. 安装并启动 Docker Desktop
3. 确保 Docker 正在运行（系统托盘可以看到 Docker 图标）

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 重新登录或运行
newgrp docker
```

### 第二步：下载项目

```bash
git clone https://github.com/shiro123444/QQgroup-annual-report-analyzer.git
cd QQgroup-annual-report-analyzer
```

### 第三步：一键启动

**Linux/Mac:**
```bash
chmod +x quick-start.sh
./quick-start.sh
```

**Windows:**
```cmd
quick-start.bat
```

### 第四步：访问系统

打开浏览器访问：http://localhost

就这么简单！🎉

## 服务说明

启动后会运行以下服务：

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 80 | Web 界面 |
| 后端 | 5000 | API 服务 |
| MySQL | 3306 | 数据库 |

## 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 只看后端
docker-compose logs -f backend

# 只看前端
docker-compose logs -f frontend
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 重新构建
```bash
docker-compose build --no-cache
docker-compose up -d
```

## 自定义配置

### 修改端口

编辑 `.env` 文件：
```env
FRONTEND_PORT=8080  # 前端端口改为 8080
BACKEND_PORT=5001   # 后端端口改为 5001
```

然后重启：
```bash
docker-compose down
docker-compose up -d
```

### 修改密码

编辑 `.env` 文件：
```env
MYSQL_PASSWORD=your_new_password
FLASK_SECRET_KEY=your_new_secret_key
```

然后重新部署：
```bash
docker-compose down -v  # -v 删除旧数据卷
docker-compose up -d
```

### 启用 OSS

编辑 `.env` 文件：
```env
SKIP_OSS=0
OSS_ACCESS_KEY_ID=your_key_id
OSS_ACCESS_KEY_SECRET=your_key_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket_name
```

## 故障排查

### 端口被占用

**错误信息：**
```
Error: port is already allocated
```

**解决方法：**
1. 修改 `.env` 中的端口号
2. 或者停止占用端口的程序

### 无法连接数据库

**解决方法：**
```bash
# 检查 MySQL 是否启动
docker-compose ps mysql

# 查看 MySQL 日志
docker-compose logs mysql

# 重启 MySQL
docker-compose restart mysql
```

### 构建失败

**解决方法：**
```bash
# 清理并重新构建
docker-compose down -v
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

### 前端无法访问后端

**解决方法：**
1. 检查 `.env` 中的 `ALLOWED_ORIGINS` 配置
2. 确保包含前端地址
3. 重启服务

## 生产环境部署

### 使用域名

1. 修改 `nginx.conf`，设置 `server_name`
2. 配置 SSL 证书
3. 修改 `.env` 中的 `ALLOWED_ORIGINS`

### 性能优化

编辑 `docker-compose.yml`：
```yaml
backend:
  command: gunicorn -w 8 -b 0.0.0.0:5000 app:app  # 增加 worker 数量
```

### 数据备份

```bash
# 备份
mkdir backups
docker exec qq-reports-mysql mysqldump -uroot -p[password] qq_reports > backups/backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i qq-reports-mysql mysql -uroot -p[password] qq_reports < backups/backup_20241212.sql
```

## 更多帮助

- [完整部署文档](./WEB_DEPLOYMENT.md)
- [使用指南](./USAGE_GUIDE.md)
- [常见问题](./USAGE_GUIDE.md#常见问题)

## 卸载

```bash
# 停止并删除所有容器和数据
docker-compose down -v

# 删除镜像（可选）
docker rmi qq-reports-backend qq-reports-frontend

# 删除项目文件
cd ..
rm -rf QQgroup-annual-report-analyzer
```

---

**需要帮助？**
- 查看 [Issues](https://github.com/shiro123444/QQgroup-annual-report-analyzer/issues)
- 提交新的 Issue
