# AI Coding Assistant - 项目上下文文档

## 项目概述

**项目名称**: AI Coding Assistant  
**项目类型**: Python 代码项目（基于 GitHub Actions 的 CI/CD 工具）  
**主要目的**: 提供自动化代码分析、代码审查、代码优化和文档生成功能的 AI 编程助手

**核心特性**:
- 🔍 自动化代码质量分析
- 🤖 AI 驱动的 Pull Request 代码审查
- ⚡ 代码性能优化建议
- 📚 自动生成代码文档和 README
- 🚀 无缝集成 GitHub Actions CI/CD 流程

**主要技术栈**:
- **编程语言**: Python 3.11+
- **AI 模型**: iFlow TStars2.0 (https://apis.iflow.cn/v1/chat/completions)
- **CI/CD**: GitHub Actions
- **配置管理**: YAML (PyYAML)
- **依赖管理**: pip (requirements.txt)
- **Git 操作**: GitPython
- **终端输出**: Rich
- **CLI 框架**: Click

## 项目结构

```
ai-coding-assistant/
├── .github/
│   └── workflows/
│       ├── code-analysis.yml      # 代码分析工作流
│       ├── code-review.yml        # 代码审查工作流
│       ├── documentation.yml      # 文档生成工作流
│       └── optimization.yml       # 代码优化工作流
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── analyzer.py            # 代码分析器核心模块
│   │   ├── reviewer.py            # 代码审查器核心模块
│   │   ├── optimizer.py           # 代码优化器核心模块
│   │   └── documentor.py          # 文档生成器核心模块
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py              # 配置管理工具
│   │   ├── github_api.py          # GitHub API 封装
│   │   └── logger.py              # 日志工具
│   └── main.py                    # 主入口（CLI）
├── config/
│   └── default.yaml               # 默认配置文件
├── docs/
│   └── 项目开发文档.md             # 中文开发文档
├── requirements.txt               # Python 依赖
├── README.md                      # 项目说明文档
└── AGENTS.md                      # 本文件（Agent 上下文文档）
```

## 核心功能模块

### 1. 代码分析器 (CodeAnalyzer)
**文件位置**: `src/core/analyzer.py`

**主要功能**:
- 分析代码结构和依赖关系
- 计算圈复杂度 (Cyclomatic Complexity)
- 使用 AI 检测代码模式和潜在问题
- 生成代码质量报告（JSON 格式）

**关键方法**:
- `analyze_directory(directory: str)`: 分析整个目录
- `analyze_file(file_path: str)`: 分析单个文件
- `_calculate_complexity(tree: ast.AST)`: 使用 AST 计算复杂度
- `_analyze_with_ai(code: str, file_path: str)`: 使用 iFlow AI 进行深度分析

**AI 集成**:
- API: `https://apis.iflow.cn/v1/chat/completions`
- 模型: `tstars2.0`
- 认证: 通过 `IFLOW_API_KEY` 环境变量

### 2. 代码审查器 (CodeReviewer)
**文件位置**: `src/core/reviewer.py`

**主要功能**:
- 自动审查 Pull Request 变更
- 检测安全漏洞和最佳实践问题
- 提供代码改进建议
- 支持按严重级别过滤

**审查维度**:
- Security（安全性）
- Best Practices（最佳实践）
- Performance（性能）

### 3. 代码优化器 (CodeOptimizer)
**文件位置**: `src/core/optimizer.py`

**主要功能**:
- 识别性能瓶颈
- 提供重构建议
- 生成优化后的代码
- 支持自动应用安全建议（可配置）

### 4. 文档生成器 (Documentor)
**文件位置**: `src/core/documentor.py`

**主要功能**:
- 自动生成代码文档
- 更新 README 文件
- 生成 API 文档
- 创建使用示例

**支持格式**:
- Markdown（默认）
- ReStructuredText（可选）

### 5. 配置管理 (Config)
**文件位置**: `src/utils/config.py`

**功能**:
- 从 YAML 文件加载配置
- 支持环境变量覆盖
- 点表示法访问配置值（如 `config.get('ai.model')`）

**关键属性**:
- `iflow_api_key`: iFlow API 密钥
- `github_token`: GitHub 令牌
- `github_repository`: GitHub 仓库路径

## 配置说明

### 默认配置文件
**文件位置**: `config/default.yaml`

**主要配置项**:

```yaml
ai:
  model: "tstars2.0"
  temperature: 0.7
  max_tokens: 2000
  timeout: 60
  api_url: "https://apis.iflow.cn/v1/chat/completions"

analysis:
  enabled:
    - complexity
    - patterns
    - dependencies
  exclude:
    - "*/tests/*"
    - "*/test_*"
    - "*/__pycache__/*"
    - "*/.venv/*"
    - "*/venv/*"
    - "*/node_modules/*"

review:
  check:
    - security
    - best_practices
    - performance
  severity_threshold: "medium"
  auto_approve_safe_changes: false

optimization:
  enabled: true
  max_suggestions: 5
  auto_apply_safe_suggestions: false

documentation:
  format: "markdown"
  include_examples: true
  generate_api_docs: true
  generate_readme: true
```

### 环境变量

**必需的环境变量**:
- `IFLOW_API_KEY`: iFlow API 密钥（从 https://platform.iflow.cn 获取）

**可选的环境变量**:
- `GITHUB_TOKEN`: GitHub 令牌（用于 GitHub Actions）
- `GITHUB_REPOSITORY`: GitHub 仓库路径（如 `owner/repo`）

## 构建和运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 本地运行命令

#### 代码分析
```bash
python src/main.py analyze --path . --output analysis-report.json
```

#### 代码审查
```bash
# 首先获取 PR diff
git diff origin/main...HEAD > pr_diff.txt

# 运行审查
python src/main.py review --diff pr_diff.txt --pr-number 123 --output review-results.json
```

#### 代码优化
```bash
python src/main.py optimize --path src --output optimization-report.json --max-suggestions 5
```

#### 文档生成
```bash
# 生成完整文档
python src/main.py docs --path src --output docs/generated --format markdown

# 仅更新 README
python src/main.py docs --readme-only
```

### 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_analyzer.py

# 生成覆盖率报告
pytest --cov=src tests/
```

### 代码质量检查

```bash
# 代码格式化
black src/

# 类型检查
mypy src/
```

## GitHub Actions 工作流

### 1. Code Analysis Workflow
**触发条件**:
- Push 到 `main` 或 `develop` 分支
- 针对 `main` 或 `develop` 分支的 Pull Request

**主要步骤**:
1. 检出代码
2. 设置 Python 3.11 环境
3. 安装依赖
4. 运行 AI 代码分析器
5. 上传分析结果（保留 30 天）
6. 在 PR 中评论分析结果

### 2. Code Review Workflow
**触发条件**:
- Pull Request 打开、同步或重新打开

**主要步骤**:
1. 检出代码
2. 设置 Python 环境
3. 安装依赖
4. 获取 PR diff
5. 运行 AI 代码审查
6. 在 PR 中添加审查评论

### 3. Documentation Workflow
**触发条件**:
- Push 到 `main` 分支
- 每周日定时任务（cron: `0 0 * * 0`）

**主要步骤**:
1. 检出代码
2. 设置 Python 环境
3. 安装依赖
4. 生成文档
5. 自动提交文档更新

### 4. Optimization Workflow
**触发条件**:
- Push 到 `main` 或 `develop` 分支
- 每周日定时任务
- 手动触发（workflow_dispatch）

## 开发约定

### 代码风格
- 使用 Python 3.11+ 语法
- 遵循 PEP 8 代码规范
- 使用类型注解（Type Hints）
- 使用 docstrings 记录函数和类

### 模块组织
- **core/**: 核心业务逻辑模块
- **utils/**: 工具和辅助函数
- **config/**: 配置文件
- **tests/**: 测试文件（每个模块对应一个测试文件）

### 命名约定
- 类名: PascalCase (如 `CodeAnalyzer`)
- 函数/方法: snake_case (如 `analyze_file`)
- 常量: UPPER_SNAKE_CASE (如 `IFLOW_API_KEY`)
- 私有方法: 以下划线开头 (如 `_calculate_complexity`)

### 错误处理
- 使用 try-except 捕获异常
- 记录详细的错误日志
- 提供有意义的错误信息
- 对于 AI API 调用失败，提供降级方案

### 日志规范
- 使用 `utils.logger` 模块
- 日志级别: INFO（默认）、DEBUG（开发）、ERROR（错误）
- 记录关键操作的开始和完成

## 依赖说明

### 核心依赖
- `requests>=2.31.0`: HTTP 请求库（用于调用 iFlow API）
- `python-dotenv>=1.0.0`: 环境变量管理
- `pyyaml>=6.0`: YAML 配置解析
- `gitpython>=3.1.40`: Git 操作
- `rich>=13.5.0`: 终端美化输出
- `click>=8.1.7`: CLI 命令行框架

### 代码分析依赖
- `astroid>=2.15.0`: Python AST 分析
- `radon>=6.0.1`: 代码复杂度计算

### 文档依赖
- `sphinx>=7.1.0`: 文档生成
- `sphinx-rtd-theme>=1.3.0`: Read the Docs 主题

### 测试依赖
- `pytest>=7.4.0`: 测试框架
- `pytest-cov>=4.1.0`: 覆盖率报告
- `pytest-mock>=3.11.1`: Mock 工具

## API 集成说明

### iFlow API
**端点**: `https://apis.iflow.cn/v1/chat/completions`  
**模型**: `tstars2.0`  
**认证方式**: Bearer Token（通过 `IFLOW_API_KEY` 环境变量）

**请求示例**:
```python
payload = {
    "model": "tstars2.0",
    "messages": [
        {"role": "system", "content": "You are a code analysis expert."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.3,
    "max_tokens": 1500,
    "stream": False
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(api_url, json=payload, headers=headers, timeout=60)
```

### GitHub API
**用途**: 
- 获取 Pull Request 信息
- 在 PR 中添加评论
- 提交文档变更

**认证方式**: 通过 `GITHUB_TOKEN` 环境变量（GitHub Actions 自动提供）

## 常见任务

### 添加新的分析规则
1. 在 `src/core/analyzer.py` 中添加新的分析方法
2. 在 `config/default.yaml` 中配置规则
3. 编写对应的测试用例

### 添加新的 GitHub Actions 工作流
1. 在 `.github/workflows/` 创建新的 YAML 文件
2. 定义触发条件和步骤
3. 配置必要的环境变量和 secrets

### 修改 AI 提示词
1. 在相应的核心模块中找到 `_analyze_with_ai` 方法
2. 修改 prompt 模板
3. 测试新的提示词效果

### 调试 AI API 调用
1. 设置日志级别为 DEBUG
2. 检查 API 响应内容
3. 验证 API 密钥是否正确
4. 查看 `ai_coding_assistant.log` 日志文件

## 重要注意事项

### 安全性
- **永远不要**在代码中硬编码 API 密钥
- 使用 GitHub Secrets 存储敏感信息
- 定期轮换 API 密钥
- 确保 `.env` 文件在 `.gitignore` 中

### 成本控制
- iFlow API 使用 token 计费
- 设置合理的 `max_tokens` 限制
- 避免重复分析相同代码
- 实现缓存机制（已配置缓存目录：`.cache`）

### 性能优化
- 使用增量分析（只分析变更的文件）
- 并行处理大型项目
- 缓存分析结果（TTL: 1 小时）
- 避免不必要的 AI 调用

### 错误处理
- 所有 AI API 调用都有超时限制（60 秒）
- API 失败时提供降级方案（返回空结果）
- 记录详细的错误日志以便排查

## 文件路径约定

- **绝对路径优先**: 在所有工具调用中使用绝对路径
- **项目根目录**: `C:\Users\Liuju\ai-coding-assistant`
- **相对路径解析**: 从项目根目录开始
- **配置文件**: `config/default.yaml`
- **日志文件**: `ai_coding_assistant.log`
- **缓存目录**: `.cache/`
- **输出目录**: 
  - 分析报告: `analysis-report.json`
  - 审查结果: `review-results.json`
  - 优化报告: `optimization-report.json`
  - 文档生成: `docs/generated/`

## 版本信息

- **Python 版本**: 3.11+
- **项目版本**: 1.0.0
- **最后更新**: 2026-02-28
- **维护状态**: 活跃开发中

## 联系和资源

- **GitHub**: https://github.com/yourusername/ai-coding-assistant
- **iFlow 平台**: https://platform.iflow.cn
- **API 文档**: https://apis.iflow.cn/docs
- **问题反馈**: 通过 GitHub Issues

---

**文档版本**: 1.0.0  
**创建日期**: 2026-02-28  
