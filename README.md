# 🎉 QQ群聊年度报告生成器

一个用于分析QQ群聊记录并生成年度热词报告的工具。支持热词发现、趣味统计、可视化报告生成等功能。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特点

- 🔍 **智能分词** - 基于jieba分词，支持新词发现和词组合并
- 📊 **热词统计** - 自动统计群聊高频词汇及其贡献者
- 🎮 **趣味榜单** - 话痨榜、深夜党、复读机等多种有趣排行
- ⏰ **时段分析** - 24小时活跃度分布统计
- 🖼️ **可视化报告** - 生成HTML/图片报告
- 🤖 **AI锐评** - 支持调用OpenAI为热词生成有趣点评（可选）

## 📦 安装

### 1. 克隆项目

```bash
git clone https://github.com/ZiHuixi/qqgroup-yearreport-analyzer.git
cd qqgroup-yearreport-analyzer
```
### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. （可选）安装图片导出功能
如需将报告导出为图片，还需安装 Playwright：
```bash
pip install playwright
playwright install chromium
```


## 🚀 使用方法

### 获取群聊数据

**推荐使用 [qq-chat-exporter](https://github.com/shuakami/qq-chat-exporter) 导出QQ群聊记录为JSON格式。**

### 运行分析

```bash
# 方式1：使用默认配置文件
python main.py

# 方式2：指定输入文件
python main.py your_chat.json
```

### 配置说明

编辑 `config.py` 进行配置：

```python
# 输入文件路径
INPUT_FILE = "chat.json"

# 热词数量
TOP_N = 200

# 新词发现参数
NEW_WORD_MIN_FREQ = 20        # 新词最小出现次数
PMI_THRESHOLD = 2.0           # PMI阈值
ENTROPY_THRESHOLD = 0.5       # 熵阈值

# 可视化报告
ENABLE_IMAGE_EXPORT = True

# OpenAI配置（用于AI锐评，可选）
OPENAI_API_KEY = "your-api-key"
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o-mini"
```

---

## 📋 输出文件

运行后会在输入文件同目录下生成：

| 文件 | 说明 |
|------|------|
| `xxx_年度热词报告.txt` | 详细文本报告 |
| `xxx_分析结果.json` | 结构化JSON数据 |
| `xxx_年度热词报告.html` | 可视化HTML报告 |
| `xxx_年度热词报告.png` | 图片报告（可选） |

---

## ⚠️ 注意事项

### 关于分词准确性

**本项目的分词功能基于jieba和统计算法，准确性有限，生成的热词结果可能包含一些无意义或错误的词组。**

建议：
- 生成报告时选择 **交互式选词模式**，手动挑选有意义的热词
- 可以在 `config.py` 中配置 `BLACKLIST` 过滤不需要的词
- 可以在 `config.py` 中配置 `WHITELIST` 保留特定词汇

### 关于AI锐评

- AI锐评功能需要配置 OpenAI API Key
- 支持兼容 OpenAI 接口的第三方服务
- 不配置则使用默认文案

---

## 📊 示例输出

### 趣味榜单

| 榜单 | 说明 |
|------|------|
| 🏆 话痨榜 | 发言条数最多 |
| 📝 字数榜 | 总字数最多 |
| 📖 长文王 | 平均每条消息字数最多 |
| 😂 表情帝 | 发送表情最多 |
| 🖼️ 图片狂魔 | 发送图片最多 |
| 🌙 深夜党 | 0-6点发言最多 |
| 🌅 早起鸟 | 6-9点发言最多 |
| 🔄 复读机 | 复读次数最多 |

---

## 🛠️ 项目结构

```
qqgroup-yearreport-analyzer/
├── main.py              # 主入口
├── analyzer.py          # 核心分析器
├── report_generator.py  # 文本报告生成
├── image_generator.py   # 可视化报告生成
├── config.py            # 配置文件
├── utils.py             # 工具函数
├── templates/           # HTML模板目录
│   └── report_template.html
├── requirements.txt
└── README.md
```

---

## 📄 许可证

MIT License


## 🤝 贡献

欢迎提交 Issue 和 Pull Request！


## 致谢

- [jieba](https://github.com/fxsjy/jieba) - 中文分词
- [qq-chat-exporter](https://github.com/shuakami/qq-chat-exporter) - QQ聊天记录导出
- [Playwright](https://playwright.dev/) - 网页截图