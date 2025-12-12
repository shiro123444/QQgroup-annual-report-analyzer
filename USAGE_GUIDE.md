# QQ群年度报告分析器 - 完整使用指南

## 📚 目录

1. [概述](#概述)
2. [部署方式选择](#部署方式选择)
3. [快速开始](#快速开始)
4. [详细配置](#详细配置)
5. [使用教程](#使用教程)
6. [高级功能](#高级功能)
7. [常见问题](#常见问题)
8. [维护和监控](#维护和监控)

## 概述

QQ群年度报告分析器提供两种使用方式：

- **本地版**：适合个人使用，在本地电脑运行
- **线上版**：适合多人使用，部署在服务器提供 Web 服务

## 部署方式选择

### 场景 1：个人使用，快速分析

**推荐：本地版**

优点：
- ✅ 安装简单
- ✅ 无需服务器
- ✅ 数据完全本地
- ✅ 无需数据库

缺点：
- ❌ 每次需要运行命令
- ❌ 无法在线分享
- ❌ 不支持多用户

### 场景 2：团队使用，长期服务

**推荐：线上版（Docker 部署）**

优点：
- ✅ Web 界面友好
- ✅ 支持多用户
- ✅ 报告永久保存
- ✅ 可在线分享
- ✅ 一次部署长期使用

缺点：
- ❌ 需要服务器
- ❌ 需要配置数据库
- ❌ 配置相对复杂

### 场景 3：快速体验功能

**推荐：演示数据 + 本地版**

```bash
# 生成演示数据
python generate_demo_data.py

# 运行分析
python main.py demo_chat.json
```

## 快速开始

### 🚀 方式一：Docker 一键部署（最快）

```bash
# 1. 克隆项目
git clone https://github.com/shiro123444/QQgroup-annual-report-analyzer.git
cd QQgroup-annual-report-analyzer

# 2. 一键启动
./quick-start.sh  # Linux/Mac
# 或
quick-start.bat   # Windows

# 3. 访问
# 打开浏览器访问 http://localhost
```

### 💻 方式二：本地版快速使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 准备配置
cp config.example.py config.py
# 编辑 config.py，设置 INPUT_FILE

# 3. 运行分析
python main.py [your_chat.json]
```

## 详细配置

### 线上版配置

编辑 `.env` 文件：

```env
# 【必须配置】数据库密码
MYSQL_PASSWORD=your_secure_password

# 【必须配置】Flask 密钥
FLASK_SECRET_KEY=your_random_secret_key

# 【可选】OSS 配置（生产环境推荐）
SKIP_OSS=1  # 设为 0 启用 OSS
OSS_ACCESS_KEY_ID=your_key
OSS_ACCESS_KEY_SECRET=your_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket

# 【可选】AI 功能
OPENAI_API_KEY=sk-your-key
```

### 本地版配置

编辑 `config.py`：

```python
# 输入文件
INPUT_FILE = "path/to/your/chat.json"

# 词频统计参数
TOP_N = 200
MIN_FREQ = 1

# AI 功能
OPENAI_API_KEY = "sk-..."
AI_COMMENT_MODE = 'ask'  # 'always', 'never', 'ask'

# 图片导出
ENABLE_IMAGE_EXPORT = True
```

## 使用教程

### 步骤 1：导出 QQ 群聊天记录

使用 [qq-chat-exporter](https://github.com/Yiyuery/qq-chat-exporter) 工具：

```bash
# 安装工具
pip install qq-chat-exporter

# 导出聊天记录（示例）
qq-chat-exporter export --qq-number YOUR_QQ --group-id GROUP_ID
```

### 步骤 2：分析聊天记录

#### 线上版操作流程：

1. **上传文件**
   - 访问 http://localhost
   - 选择"上传分析"
   - 选择模式：手动选词 或 AI 自动选词
   - 上传 JSON 文件

2. **选择热词**（仅手动模式）
   - 浏览系统提取的热词列表
   - 点击选择最能代表这一年的词汇
   - 建议选择 5-10 个词
   - 点击"确认选择并生成报告"

3. **查看报告**
   - 等待生成完成
   - 在线查看精美报告
   - 可复制链接分享

4. **管理历史**
   - 切换到"历史记录"标签
   - 查看所有生成的报告
   - 支持搜索和删除

#### 本地版操作流程：

1. **运行分析**
   ```bash
   python main.py your_chat.json
   ```

2. **选择生成模式**
   - 交互式选择热词（推荐）
   - 自动选择前 10 个
   - AI 智能选词
   - 跳过可视化

3. **查看报告**
   - HTML 报告：在 `runtime_outputs` 目录
   - 图片报告：PNG 格式（如启用）

### 步骤 3：分享报告

#### 线上版：
- 复制报告链接直接分享
- 其他人打开链接即可查看

#### 本地版：
- 分享 HTML 文件
- 分享 PNG 图片

## 高级功能

### 1. AI 智能点评

**配置 OpenAI API：**

```env
# .env 文件（线上版）
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

```python
# config.py 文件（本地版）
OPENAI_API_KEY = "sk-your-api-key"
OPENAI_MODEL = "gpt-4"
AI_COMMENT_MODE = 'always'  # 总是生成 AI 评论
```

### 2. 云存储（OSS）

**启用阿里云 OSS：**

1. 登录阿里云控制台
2. 创建 OSS Bucket
3. 获取 AccessKey
4. 配置 `.env`：

```env
SKIP_OSS=0
OSS_ACCESS_KEY_ID=your_key
OSS_ACCESS_KEY_SECRET=your_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket
```

### 3. 自定义分析参数

**高级词频配置：**

```python
# config.py
TOP_N = 200              # 提取前 200 个高频词
MIN_FREQ = 5             # 最小出现 5 次
MIN_WORD_LEN = 2         # 最小词长 2
MAX_WORD_LEN = 8         # 最大词长 8

# 新词发现
PMI_THRESHOLD = 3.0      # 提高阈值发现更高质量新词
ENTROPY_THRESHOLD = 1.0
NEW_WORD_MIN_FREQ = 50   # 新词最少出现 50 次
```

### 4. 批量分析

**分析多个群聊：**

```bash
# 创建批处理脚本
for file in data/*.json; do
    echo "分析: $file"
    python main.py "$file"
done
```

## 常见问题

### Q1: 上传文件失败？

**A:** 检查以下几点：
- 文件格式是否为 JSON
- 文件大小是否超过限制（默认 100MB）
- 文件内容是否符合格式要求

### Q2: 数据库连接失败？

**A:** 
```bash
# 检查 MySQL 是否运行
docker-compose ps mysql

# 查看日志
docker-compose logs mysql

# 重启 MySQL
docker-compose restart mysql
```

### Q3: 如何备份数据？

**A:**
```bash
# 备份数据库
docker exec qq-reports-mysql mysqldump -uroot -p[password] qq_reports > backup.sql

# 恢复数据库
docker exec -i qq-reports-mysql mysql -uroot -p[password] qq_reports < backup.sql
```

### Q4: 如何更新系统？

**A:**
```bash
# 拉取最新代码
git pull

# 重新构建和启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 运行数据库迁移
docker exec qq-reports-backend python migrate_db.py
```

### Q5: 端口被占用怎么办？

**A:** 修改 `.env` 文件：
```env
FRONTEND_PORT=8080
BACKEND_PORT=5001
```

## 维护和监控

### 日常维护

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 清理旧数据
# 手动在数据库中删除或使用历史记录管理功能
```

### 监控脚本

```bash
# 单次检查
python monitor.py

# 持续监控（每 60 秒）
python monitor.py --watch 60
```

### 性能优化

1. **增加 worker 数量**（高并发）
   ```yaml
   # docker-compose.yml
   command: gunicorn -w 8 -b 0.0.0.0:5000 app:app
   ```

2. **启用 Redis 缓存**（可选）

3. **使用 CDN**（生产环境）

4. **数据库索引优化**
   ```bash
   python backend/migrate_db.py
   ```

## 🆘 获取帮助

遇到问题？

1. 查看 [常见问题](#常见问题)
2. 查看 [GitHub Issues](https://github.com/shiro123444/QQgroup-annual-report-analyzer/issues)
3. 提交新的 Issue
4. 查看完整文档：
   - [WEB_DEPLOYMENT.md](./WEB_DEPLOYMENT.md) - Web 部署指南
   - [DEPLOYMENT.md](./DEPLOYMENT.md) - 详细部署文档
   - [README.md](./README.md) - 项目说明

---

**祝你使用愉快！** 🎉
