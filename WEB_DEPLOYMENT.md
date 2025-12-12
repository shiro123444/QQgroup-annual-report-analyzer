# QQ群年度报告分析器 - 线上版快速部署指南

## 🚀 一键部署（推荐）

使用 Docker Compose，只需一条命令即可完成部署！

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+ 或 Docker Compose V2

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/shiro123444/QQgroup-annual-report-analyzer.git
cd QQgroup-annual-report-analyzer

# 2. 运行快速启动脚本
chmod +x quick-start.sh
./quick-start.sh
```

脚本会自动：
- ✅ 检查 Docker 环境
- ✅ 创建并配置 `.env` 文件
- ✅ 生成安全的密钥
- ✅ 构建 Docker 镜像
- ✅ 启动所有服务
- ✅ 初始化数据库

完成后访问：http://localhost

### 部署模式选择

**开发模式（推荐新手）：**
- 不需要配置 OSS
- 文件存储在本地
- 快速上手

**生产模式：**
- 需要配置阿里云 OSS
- 文件存储在云端
- 适合正式环境

## 📋 手动部署

### 方案 A：Docker Compose（推荐）

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件
nano .env  # 至少修改 MYSQL_PASSWORD 和 FLASK_SECRET_KEY

# 3. 启动服务
docker-compose up -d

# 4. 初始化数据库
docker exec qq-reports-backend python init_db.py

# 5. 查看状态
docker-compose ps
```

### 方案 B：本地运行

#### 后端部署

```bash
# 1. 创建虚拟环境
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt
pip install -r ../requirements.txt

# 3. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置

# 4. 初始化数据库
python init_db.py

# 5. 启动服务
python app.py
```

#### 前端部署

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 开发模式
npm run dev

# 3. 生产构建
npm run build

# 4. 预览生产版本
npm run preview
```

## 🔧 配置说明

### 必须配置项

编辑 `.env` 文件：

```env
# 数据库密码（必须修改）
MYSQL_PASSWORD=your_secure_password_here

# Flask 密钥（必须修改）
FLASK_SECRET_KEY=your_random_secret_key_here
```

生成安全密钥：
```bash
# Flask Secret Key
openssl rand -hex 32

# MySQL Password
openssl rand -base64 16
```

### 可选配置项

#### 1. 阿里云 OSS（生产环境推荐）

```env
SKIP_OSS=0
OSS_ACCESS_KEY_ID=your_key_id
OSS_ACCESS_KEY_SECRET=your_key_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket_name
```

#### 2. OpenAI API（AI 评论功能）

```env
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

#### 3. 端口配置

```env
FRONTEND_PORT=80
BACKEND_PORT=5000
```

## 📝 使用说明

### 访问应用

- **前端界面**：http://localhost （或 http://localhost:FRONTEND_PORT）
- **后端 API**：http://localhost:5000 （或 http://localhost:BACKEND_PORT）
- **健康检查**：http://localhost:5000/api/health

### 用户操作流程

1. **上传分析**
   - 选择模式：手动选词 或 AI 自动选词
   - 上传 QQ 群聊 JSON 文件（使用 [qq-chat-exporter](https://github.com/Yiyuery/qq-chat-exporter) 导出）
   - 等待分析完成

2. **选择热词**（仅手动模式）
   - 浏览热词列表
   - 选择最能代表这一年的词汇（最多 10 个）
   - 确认生成报告

3. **查看报告**
   - 在线查看精美报告
   - 分享报告链接

4. **历史记录**
   - 查看所有生成的报告
   - 搜索、删除报告

## 🛠️ 常用命令

### Docker Compose

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 查看某个服务的日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看状态
docker-compose ps

# 重新构建
docker-compose build --no-cache

# 进入容器
docker exec -it qq-reports-backend bash
docker exec -it qq-reports-mysql mysql -uroot -p
```

### 数据库操作

```bash
# 备份数据库
docker exec qq-reports-mysql mysqldump -uroot -p[password] qq_reports > backup.sql

# 恢复数据库
docker exec -i qq-reports-mysql mysql -uroot -p[password] qq_reports < backup.sql

# 连接数据库
docker exec -it qq-reports-mysql mysql -uroot -p
```

## 🌐 生产环境部署

### 使用 Nginx 反向代理

如果你有自己的域名和服务器：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }

    client_max_body_size 100M;
}
```

### HTTPS 配置（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 📊 监控和日志

### 查看应用日志

```bash
# 所有服务日志
docker-compose logs -f

# 后端日志
docker-compose logs -f backend

# 前端日志
docker-compose logs -f frontend

# MySQL 日志
docker-compose logs -f mysql
```

### 健康检查

访问 http://localhost:5000/api/health 查看服务状态

## 🔒 安全建议

1. **生产环境必须**：
   - [ ] 修改默认密码
   - [ ] 使用强密钥
   - [ ] 配置 HTTPS
   - [ ] 限制数据库访问
   - [ ] 定期备份数据

2. **建议配置**：
   - [ ] 配置防火墙
   - [ ] 使用 CDN
   - [ ] 启用日志监控
   - [ ] 配置速率限制

## ❓ 故障排查

### 问题 1：端口被占用

```bash
# 修改 .env 中的端口
FRONTEND_PORT=8080
BACKEND_PORT=5001
```

### 问题 2：数据库连接失败

```bash
# 检查 MySQL 是否启动
docker-compose ps mysql

# 查看 MySQL 日志
docker-compose logs mysql

# 重新初始化数据库
docker exec qq-reports-backend python init_db.py
```

### 问题 3：前端无法访问后端

```bash
# 检查 CORS 配置
# 编辑 .env
ALLOWED_ORIGINS=http://localhost,http://localhost:80,http://localhost:5173
```

### 问题 4：构建失败

```bash
# 清理并重新构建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 📚 更多文档

- [完整部署文档](./DEPLOYMENT.md)
- [API 接口文档](./DEPLOYMENT.md#api-接口说明)
- [开发指南](./README.md)

## 🆘 获取帮助

- 查看 [Issues](https://github.com/shiro123444/QQgroup-annual-report-analyzer/issues)
- 提交新的 Issue
- 联系项目维护者

## 📄 许可证

MIT License

---

**祝你使用愉快！如果觉得有用，请给个 Star ⭐️**
