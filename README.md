# AI Coding Assistant

基于 GitHub Actions 的 AI 编程助手，提供自动化代码分析、审查、优化和文档生成功能。

## 功能特性

- 🔍 **代码分析**：自动分析代码质量、复杂度和依赖关系
- 🤖 **代码审查**：AI 驱动的 PR 代码审查，提供改进建议
- ⚡ **代码优化**：识别性能瓶颈，提供优化建议
- 📚 **文档生成**：自动生成代码文档和 README
- 🚀 **GitHub Actions 集成**：无缝集成到 CI/CD 流程

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/ai-coding-assistant.git
cd ai-coding-assistant
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

在 GitHub 仓库设置中添加以下 Secrets：

- `IFLOW_API_KEY`: iFlow API 密钥（访问 https://platform.iflow.cn 获取）

## GitHub Actions 工作流

项目包含以下 GitHub Actions 工作流：

### 代码分析

在每次 push 或 PR 时自动运行：

```yaml
# 自动触发条件
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

### 代码审查

对 Pull Request 进行 AI 审查：

```yaml
# PR 触发
on:
  pull_request:
    types: [opened, synchronize, reopened]
```

### 文档生成

每周自动更新文档：

```yaml
# 定时任务
on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # 每周日运行
```

### 代码优化

定期进行代码优化分析：

```yaml
# 定时或手动触发
on:
  push:
    branches: [ main, develop ]
  schedule:
    - cron: '0 0 * * 0'
  workflow_dispatch:
```

## 本地使用

### 代码分析

```bash
python src/main.py analyze --path . --output analysis-report.json
```

### 代码审查

```bash
# 首先获取 PR diff
git diff origin/main...HEAD > pr_diff.txt

# 运行审查
python src/main.py review --diff pr_diff.txt --pr-number 123 --output review-results.json
```

### 代码优化

```bash
python src/main.py optimize --path src --output optimization-report.json --max-suggestions 5
```

### 生成文档

```bash
# 生成完整文档
python src/main.py docs --path src --output docs/generated --format markdown

# 仅更新 README
python src/main.py docs --readme-only
```

## 配置

编辑 `config/default.yaml` 自定义行为：

```yaml
ai:
  model: "tstars2.0"
  temperature: 0.7
  max_tokens: 2000
  api_url: "https://apis.iflow.cn/v1/chat/completions"

analysis:
  exclude:
    - "*/tests/*"
    - "*/__pycache__/*"

review:
  severity_threshold: "medium"
```

## 项目结构

```
ai-coding-assistant/
├── .github/
│   └── workflows/          # GitHub Actions 工作流
├── src/
│   ├── core/              # 核心功能模块
│   └── utils/             # 工具模块
├── config/                # 配置文件
├── tests/                 # 测试文件
└── requirements.txt       # Python 依赖
```

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
```

### 类型检查

```bash
mypy src/
```

## 贡献

欢迎贡献！请提交 Pull Request 或创建 Issue。

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/yourusername/ai-coding-assistant
- Issues: https://github.com/yourusername/ai-coding-assistant/issues

---

**注意**：此项目需要 iFlow API 密钥才能运行。请访问 https://platform.iflow.cn 获取 API 密钥，并确保安全地存储，不要将其提交到版本控制系统。