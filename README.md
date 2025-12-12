# QQ群年度报告分析器

### 🎉 线上版现已完善，支持一键 Docker 部署！

---
一个功能强大的 QQ 群聊天记录分析工具，可以生成精美的年度报告。现已支持**线上版**，提供完整的 Web 服务！

> 💡 **新功能**：现在支持 Docker Compose 一键部署，5 分钟内即可搭建完整的线上服务！

## ✨ 特性

### 本地版功能
- 📊 **智能词频统计**：基于 jieba 分词的高级文本分析
- 🔍 **新词发现**：自动识别群聊专属新词
- 📈 **多维度排行榜**：发言量、活跃度、表情包、夜猫子等多个维度
- 🎨 **精美可视化报告**：自动生成 HTML/PNG 格式年度报告
- 🤖 **AI 智能点评**：集成 OpenAI API，提供 AI 年度总结（可选）
- ⚙️ **高度可定制**：丰富的配置参数，满足不同需求

### 🌐 线上版新功能
- 🐳 **一键部署**：Docker Compose 快速部署，5 分钟搭建完整服务
- ☁️ **云存储集成**：支持阿里云 OSS 或本地存储（可选）
- 🎯 **交互式选词**：用户可从热词列表中自主选择展示词汇
- 💾 **数据持久化**：MySQL 数据库永久存储报告
- 📜 **历史记录管理**：随时查看、搜索、删除历史报告
- 🔗 **在线分享**：生成可分享的报告链接
- 📱 **响应式设计**：完美适配各种设备
- 🎨 **开箱即用**：提供演示数据，无需上传即可体验

## 🚀 快速开始

### 🌐 线上版部署（推荐）

#### 方式一：一键 Docker 部署（最简单）

**前置要求**：安装 Docker 和 Docker Compose

```bash
# 克隆项目
git clone https://github.com/shiro123444/QQgroup-annual-report-analyzer.git
cd QQgroup-annual-report-analyzer

# 一键启动（Linux/Mac）
chmod +x quick-start.sh
./quick-start.sh

# 或使用 Windows
quick-start.bat
```

完成！访问 http://localhost 即可使用 🎉

> 📖 详细部署指南请查看 [WEB_DEPLOYMENT.md](./WEB_DEPLOYMENT.md)

#### 方式二：手动部署

完整的手动部署指南请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 💻 本地版使用

#### 1. 安装依赖

```bash
git clone https://github.com/ZiHuixi/QQgroup-annual-report-analyzer.git
cd QQgroup-annual-report-analyzer
pip install -r requirements.txt
```

#### 2. 准备聊天记录

使用 [qq-chat-exporter](https://github.com/Yiyuery/qq-chat-exporter) 导出 QQ 群聊天记录为 JSON 格式。

#### 3. 配置

```bash
# 复制配置模板
cp config.example.py config.py

# 编辑 config.py，设置输入文件路径
# INPUT_FILE = "path/to/your/chat.json"
```

#### 4. 运行分析

```bash
python main.py
```

生成的报告在 `runtime_outputs` 目录下。

### 🎨 快速体验（无需上传数据）

想快速体验系统功能？使用演示数据生成器：

```bash
# 生成演示数据
python generate_demo_data.py

# 使用演示数据运行分析
python main.py demo_chat.json
```

或在线上版直接上传生成的 `demo_chat.json` 文件体验完整流程。

## 📖 文档导航

我们提供了完整的文档帮助你快速上手：

| 文档 | 说明 |
|------|------|
| 📘 [WEB_DEPLOYMENT.md](./WEB_DEPLOYMENT.md) | **Web 版快速部署指南** - 5 分钟上手 |
| 📗 [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) | **Docker 部署详解** - 最简单的部署方式 |
| 📙 [USAGE_GUIDE.md](./USAGE_GUIDE.md) | **完整使用教程** - 从入门到精通 |
| 📕 [DEPLOYMENT.md](./DEPLOYMENT.md) | **详细部署文档** - 高级配置和优化 |
| 📝 [CHANGELOG.md](./CHANGELOG.md) | **更新日志** - 版本历史和新功能 |
| 🤝 [CONTRIBUTING.md](./CONTRIBUTING.md) | **贡献指南** - 如何参与开发 |

## 🛠️ 常用命令

使用 Makefile 简化操作：

```bash
make help      # 查看所有命令
make deploy    # 一键部署（构建+启动）
make up        # 启动服务
make down      # 停止服务
make logs      # 查看日志
make monitor   # 运行监控脚本
make backup    # 备份数据库
make clean     # 清理临时文件
```

## 📖 详细文档

### 系统架构

```
┌─────────────┐
│   前端 Vue   │ ← 用户界面（上传、选词、查看）
└──────┬──────┘
       │ HTTP/REST API
┌──────▼──────┐
│  后端 Flask  │ ← 分析引擎、API 服务
└──┬────────┬─┘
   │        │
   ▼        ▼
┌─────┐  ┌─────┐
│ OSS │  │MySQL│ ← 云存储 + 数据库
└─────┘  └─────┘
```

### 工作流程

**线上版完整流程：**

1. 用户在前端选择 QQ 群聊 JSON 文件
2. 前端直接上传文件到阿里云 OSS（生产环境）或后端（开发环境）
3. 后端从 OSS 下载文件到本地临时目录进行分析
4. 后端提取热词和统计数据，分析完成后删除 OSS 和本地临时文件
5. 将分析结果保存到 MySQL 数据库，返回热词列表
6. 用户从热词列表中选择想要展示的词汇
7. 后端根据选词生成 AI 点评
8. 完整报告数据保存到数据库，前端动态渲染展示
9. 用户可随时查看历史报告

### API 接口

#### 上传并分析
```http
POST /api/upload
Content-Type: multipart/form-data

参数：
- file: JSON 文件
- auto_select: 是否 AI 自动选词（可选，默认 false）
```

#### 完成报告（用户选词后）
```http
POST /api/finalize
Content-Type: application/json

{
  "report_id": "uuid",
  "selected_words": ["词1", "词2", ...]
}
```

#### 查询报告列表
```http
GET /api/reports?page=1&page_size=20&chat_name=搜索关键词
```

#### 查看报告
```http
GET /api/reports/{report_id}
或
GET /report/{report_id}
```

#### 删除报告
```http
DELETE /api/reports/{report_id}
```

更多 API 详情请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

## ⚙️ 配置说明

### 本地版配置（config.py）

```python
# 分词和词频统计
TOP_N = 200                    # 提取前 N 个高频词
MIN_FREQ = 1                   # 最小词频
MIN_WORD_LEN = 1              # 最小词长
MAX_WORD_LEN = 10             # 最大词长

# 新词发现参数
PMI_THRESHOLD = 2.0           # 互信息阈值
ENTROPY_THRESHOLD = 0.5       # 信息熵阈值
NEW_WORD_MIN_FREQ = 20        # 新词最小频次

# 词组合并参数
MERGE_MIN_FREQ = 30           # 合并最小频次
MERGE_MIN_PROB = 0.3          # 合并条件概率阈值

# AI 功能（需要配置 OpenAI API）
OPENAI_API_KEY = "sk-..."    # OpenAI API Key
OPENAI_MODEL = "gpt-4"       # 使用的模型
AI_COMMENT_MODE = 'ask'      # 'always', 'never', 'ask'

# 图片导出
ENABLE_IMAGE_EXPORT = True    # 是否导出图片
IMAGE_GENERATION_MODE = 'ask' # 图片生成模式
```

### 线上版配置（.env）

```ini
# 阿里云 OSS
OSS_ACCESS_KEY_ID=your_key
OSS_ACCESS_KEY_SECRET=your_secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your_bucket

# MySQL 数据库
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=qq_reports

# Flask
FLASK_SECRET_KEY=random_secret_key
FLASK_PORT=5000
```

## 📊 生成的报告包含

- 📈 **基础统计**：消息总数、时间范围、参与人数
- 🔥 **年度热词**：群聊最热门的词汇（线上版支持自定义选择）
- 👑 **多维度排行榜**：
  - 发言量排行
  - 活跃度排行
  - 表情包达人
  - 夜猫子/早起人
  - 语音达人
  - 图片分享达人
- 📅 **时间分析**：活跃时段、周/月分布
- 🎭 **趣味统计**：最长发言、撤回次数等

## 🛠️ 技术栈

### 本地版
- Python 3.8+
- jieba（中文分词）
- Jinja2（模板引擎）
- Playwright（网页渲染）
- OpenAI API（可选）

### 线上版
- **后端**：Flask, pymysql, oss2, python-dotenv
- **前端**：Vue 3, Vite, Axios
- **存储**：阿里云 OSS（可选）或本地存储
- **数据库**：MySQL 5.7+/8.0+
- **部署**：Docker, Docker Compose, Nginx

## 📝 开发计划

- [x] 基础词频统计
- [x] 新词发现算法
- [x] 多维度排行榜
- [x] HTML 报告生成
- [x] PNG 图片导出
- [x] AI 智能点评
- [x] Web 版本开发
- [x] 云存储集成
- [x] 用户选词功能
- [x] 历史记录管理
- [x] Docker 一键部署
- [x] 演示数据生成器
- [x] 完整文档体系
- [x] 监控和维护工具
- [ ] 用户认证系统
- [ ] 报告分享功能优化
- [ ] 数据可视化增强
- [ ] 移动端优化

## ❓ 常见问题

### 如何快速开始？

最快的方式是使用 Docker：
```bash
./quick-start.sh  # 一键启动
```
详见 [DOCKER_GUIDE.md](./DOCKER_GUIDE.md)

### 需要配置 OSS 吗？

**不需要！** 默认使用本地存储，可选配置 OSS。

### 支持哪些数据格式？

使用 [qq-chat-exporter](https://github.com/Yiyuery/qq-chat-exporter) 导出的 JSON 格式。

### 如何获取演示数据？

运行 `python generate_demo_data.py` 即可生成。

### 更多问题？

查看 [USAGE_GUIDE.md](./USAGE_GUIDE.md#常见问题) 获取完整的故障排查指南。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

详细贡献指南请查看 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 📄 许可证

MIT License

## 🙏 致谢

- [qq-chat-exporter](https://github.com/Yiyuery/qq-chat-exporter) - QQ 聊天记录导出工具
- [jieba](https://github.com/fxsjy/jieba) - 中文分词库
- 所有贡献者和使用者

## 📮 联系方式

- 项目地址: https://github.com/shiro123444/QQgroup-annual-report-analyzer
- 问题反馈: [GitHub Issues](https://github.com/shiro123444/QQgroup-annual-report-analyzer/issues)
- 贡献代码: [Pull Requests](https://github.com/shiro123444/QQgroup-annual-report-analyzer/pulls)

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=shiro123444/QQgroup-annual-report-analyzer&type=Date)](https://star-history.com/#shiro123444/QQgroup-annual-report-analyzer&Date)

---

**注意**：本项目仅供学习和个人使用，请遵守相关法律法规和平台服务条款。
