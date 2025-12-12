# 贡献指南

感谢你对 QQ群年度报告分析器项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 在 [Issues](https://github.com/shiro123444/QQgroup-annual-report-analyzer/issues) 中搜索是否已有相关问题
2. 如果没有，创建新的 Issue
3. 使用清晰的标题和详细的描述
4. 如果是 bug，请提供：
   - 复现步骤
   - 期望行为
   - 实际行为
   - 系统环境信息

### 提交代码

#### 准备工作

1. Fork 本仓库
2. 克隆你的 fork
   ```bash
   git clone https://github.com/YOUR_USERNAME/QQgroup-annual-report-analyzer.git
   cd QQgroup-annual-report-analyzer
   ```
3. 创建新分支
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### 开发流程

1. 安装依赖
   ```bash
   make install
   # 或
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   cd frontend && npm install
   ```

2. 进行修改
   - 保持代码风格一致
   - 添加必要的注释
   - 更新相关文档

3. 测试你的修改
   ```bash
   # 运行本地测试
   python main.py demo_chat.json
   
   # 或启动开发服务器
   make dev
   ```

4. 提交更改
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

#### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式（不影响代码运行）
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: 添加用户认证功能
fix: 修复文件上传大小限制问题
docs: 更新部署指南
```

#### 创建 Pull Request

1. 推送到你的 fork
   ```bash
   git push origin feature/your-feature-name
   ```

2. 在 GitHub 上创建 Pull Request

3. 填写 PR 描述：
   - 修改的内容
   - 解决的问题
   - 相关 Issue 链接

4. 等待审核和反馈

## 📝 代码规范

### Python 代码

- 遵循 PEP 8 规范
- 使用有意义的变量名
- 添加函数和类的文档字符串
- 保持函数简洁（建议不超过 50 行）

```python
def analyze_chat_data(data: dict) -> dict:
    """
    分析聊天数据
    
    Args:
        data: 聊天记录数据
    
    Returns:
        分析结果字典
    """
    # 实现代码
    pass
```

### JavaScript/Vue 代码

- 使用 ES6+ 语法
- 组件名使用 PascalCase
- 使用组合式 API（Composition API）
- 添加必要的注释

```javascript
// 好的示例
const uploadAndAnalyze = async () => {
  // 验证文件
  if (!file.value) return
  
  // 上传逻辑
  try {
    const response = await axios.post('/api/upload', formData)
    // 处理响应
  } catch (error) {
    console.error('上传失败:', error)
  }
}
```

### SQL 代码

- 使用大写关键字
- 合理使用缩进
- 添加注释说明复杂查询

```sql
-- 查询用户报告列表
SELECT 
    report_id,
    chat_name,
    message_count,
    created_at
FROM reports
WHERE user_id = %s
ORDER BY created_at DESC
LIMIT 20;
```

## 🧪 测试

在提交 PR 之前，请确保：

- [ ] 本地测试通过
- [ ] 没有引入新的警告或错误
- [ ] 文档已更新（如有必要）
- [ ] 代码风格符合规范

## 📚 文档贡献

文档同样重要！你可以：

- 修正错误和typos
- 改进现有文档的清晰度
- 添加新的使用示例
- 翻译文档到其他语言

## 💡 功能建议

如果你有好的功能想法：

1. 先创建 Issue 讨论
2. 等待社区反馈
3. 获得认可后再开始开发

## 🎯 优先级任务

当前急需帮助的领域：

- [ ] 完善单元测试
- [ ] 改进错误处理
- [ ] 优化性能
- [ ] 增加更多数据可视化
- [ ] 支持更多聊天平台

## 📧 联系方式

如有任何问题，可以：

- 在 Issue 中提问
- 发送邮件到项目维护者
- 加入项目讨论群

## 🙏 致谢

感谢所有为项目做出贡献的开发者！

你的贡献将被记录在 [CHANGELOG.md](./CHANGELOG.md) 中。

---

**再次感谢你的贡献！** ❤️
