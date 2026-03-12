# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Python Flask 的 Web UI 应用，用于管理 GitHub 仓库和 GitHub Actions 工作流。

### 核心功能

1. **GitHub 仓库文件管理**
   - 拉取指定仓库文件
   - 修改后推送回 GitHub

2. **GitHub Actions 工作流管理**
   - 启动指定工作流
   - 获取执行日志和结果
   - 下载工作流产物到配置目录

3. **配置管理**
   - 使用 SQLite 存储配置
   - 配置项：GitHub Token、仓库信息、下载目录等

4. **部署支持**
   - 支持 Docker 容器化部署

## 开发环境

### 虚拟环境

项目使用项目级虚拟环境 `./venv`，在执行任何 Python 命令前需先激活：

```bash
# Windows
venv\Scripts\activate

# Linux/macOS/Git Bash
source venv/bin/activate
```

### 依赖安装

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
python app.py
```

## 开发工作流

### 1. 功能调研优先（重要！）

在实现任何功能前，**必须先使用 chrome-devtools MCP 工具**搜索是否有成熟的 GitHub 开源方案：

```
优先级：成熟方案 > 自主开发
```

**调研流程**：

#### Step 1: 使用 chrome-devtools MCP 搜索

```python
# 导航到 GitHub
mcp__chrome-devtools__navigate_page(url="https://github.com")

# 搜索关键词
mcp__chrome-devtools__fill(uid="搜索框", value="flask github actions manager")

# 分析搜索结果
mcp__chrome-devtools__take_snapshot()
```

#### Step 2: 评估候选项目

对于每个候选项目，检查：
- ⭐ Star 数和活跃度
- 📅 最后更新时间
- 📖 文档完整性
- 🔀 许可证（MIT/Apache 优先）
- 🐛 Issue 响应速度

#### Step 3: 决策树

```
发现成熟方案？
├── 是 → 功能完整？
│   ├── 是 → 直接使用（记录到文档）
│   └── 否 → Fork 后二次开发
└── 否 → 自主开发（参考类似项目）
```

**调研关键词参考**：
- `flask github manager`
- `github actions web ui`
- `github workflow dashboard`
- `github repository manager`

### 2. TDD 开发流程

遵循测试驱动开发：

```
1. 编写测试（失败）
2. 实现功能（通过测试）
3. 重构代码（保持测试通过）
4. 验证截图（chrome-devtools）
```

**测试层级**：
- 单元测试：services/ 模块
- 集成测试：路由 + 服务
- E2E 测试：chrome-devtools MCP

### 3. 功能测试验证

**所有功能必须使用 chrome-devtools MCP 工具进行测试验证并截图**：

#### 测试流程

```python
# 1. 启动应用
python app.py

# 2. 打开浏览器
mcp__chrome-devtools__new_page(url="http://localhost:5000")

# 3. 执行功能操作
mcp__chrome-devtools__take_snapshot()  # 操作前
mcp__chrome-devtools__click(uid="提交按钮")
mcp__chrome-devtools__take_snapshot()  # 操作后

# 4. 检查控制台错误
mcp__chrome-devtools__list_console_messages(types=["error"])

# 5. 保存截图
mcp__chrome-devtools__take_screenshot(
    filePath="screenshots/test_function_name.png"
)
```

#### 截图命名规范

```
screenshots/
├── 01_config_github_token.png
├── 02_pull_repository_files.png
├── 03_edit_file_content.png
├── 04_push_changes_success.png
├── 05_start_workflow.png
├── 06_view_workflow_logs.png
└── 07_download_artifacts.png
```

### 4. Python 编码规范

**在 Windows 环境下，优先使用 Python 标准库而非 Bash 命令**，确保跨平台兼容性。

#### 必须遵守的规则

**涉及中文输出时**，必须在 `main()` 函数开头添加：

```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

**使用 pathlib 而非 os.path**：

```python
# ✅ 正确
from pathlib import Path
config_path = Path("data") / "config.db"

# ❌ 错误
import os
config_path = os.path.join("data", "config.db")
```

**使用 subprocess 而非 Bash 工具**：

```python
# ✅ 正确
import subprocess
result = subprocess.run(['git', 'status'], capture_output=True)

# ❌ 错误（在 Windows 兼容性规则中）
Bash('git status')
```

#### 代码风格

遵循 **PEP 8** 规范：
- 每行最大长度：88 字符（Black 格式化器默认）
- 使用 f-string 格式化字符串
- 类型注解：函数参数和返回值
- 文档字符串：Google 风格或 NumPy 风格

```python
from typing import Optional

def fetch_github_file(repo: str, path: str, token: str) -> Optional[str]:
    """从 GitHub 仓库获取文件内容。

    Args:
        repo: 仓库全名，如 "owner/repo"
        path: 文件路径
        token: GitHub personal access token

    Returns:
        文件内容字符串，如果失败返回 None
    """
    # 实现...
```

## 工作流文档

本项目有详细的开发工作流文档，位于 `docs/workflows/` 目录。

### 📋 工作流快速索引

#### 核心开发流程

| 工作流 | 文档 | 适用场景 | 阅读时间 |
|--------|------|----------|----------|
| **新功能实现** | [feature-implementation.md](docs/workflows/feature-implementation.md) | 从零实现新功能 | 15 min |
| **GitHub API 集成** | [github-integration-workflow.md](docs/workflows/github-integration-workflow.md) | 开发 GitHub API 相关功能 | 10 min |
| **服务层开发** | [service-development-workflow.md](docs/workflows/service-development-workflow.md) | 开发业务逻辑层 | 10 min |
| **前端页面开发** | [frontend-development-workflow.md](docs/workflows/frontend-development-workflow.md) | 开发 Web UI 页面 | 12 min |
| **数据库变更** | [database-migration-workflow.md](docs/workflows/database-migration-workflow.md) | 修改数据库模型 | 8 min |

#### 测试与质量

| 工作流 | 文档 | 适用场景 | 阅读时间 |
|--------|------|----------|----------|
| **TDD 测试** | [tdd-testing-workflow.md](docs/workflows/tdd-testing-workflow.md) | 编写测试 | 15 min |
| **Bug 修复** | [bug-fix-workflow.md](docs/workflows/bug-fix-workflow.md) | 修复问题 | 10 min |
| **代码审查** | [code-review-workflow.md](docs/workflows/code-review-workflow.md) | 审查代码 | 8 min |

### 🚀 快速开始

**开发新功能？** → 阅读 [新功能实现流程](docs/workflows/feature-implementation.md)

**修复 Bug？** → 阅读 [Bug 修复流程](docs/workflows/bug-fix-workflow.md)

**首次开发？** → 先阅读 [TDD 测试工作流](docs/workflows/tdd-testing-workflow.md)

### 📖 工作流文档结构

每个工作流文档包含：

1. **适用场景**：何时使用该工作流
2. **前置条件**：开始前需要准备什么
3. **详细步骤**：分步骤的操作指南
4. **代码示例**：可运行的示例代码
5. **常见问题**：FAQ 和解决方案
6. **检查清单**：完成后的验证项

### 💡 Agent 使用指南

当 Agent 接到任务时，应根据任务类型查找对应的工作流文档：

```
任务：实现配置管理功能
  ↓
Agent 查阅：feature-implementation.md（功能实现）
           + service-development-workflow.md（服务层）
           + tdd-testing-workflow.md（测试）
  ↓
Agent 按照工作流步骤执行
```

### 🔗 相关文档

- [应用架构](#应用架构) - 了解项目的三层架构
- [API 设计](#api-端点设计) - REST API 设计规范
- [数据库设计](#数据库设计) - 数据库模型定义

## 应用架构

### 三层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
│                    (Flask Routes + Templates)               │
│  • 处理 HTTP 请求                                            │
│  • 表单验证                                                  │
│  • 会话管理                                                  │
│  • 响应渲染                                                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Business Logic Layer                   │
│                       (Services)                            │
│  • GitHub API 调用封装                                      │
│  • 数据库 CRUD 操作                                         │
│  • 工作流状态管理                                           │
│  • 产物下载逻辑                                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Data Access Layer                      │
│              (SQLite / PyGithub / File System)              │
│  • 配置数据库                                                │
│  • GitHub API                                               │
│  • 本地文件系统                                              │
└─────────────────────────────────────────────────────────────┘
```

### 核心数据流

#### 1. GitHub 文件管理流程

```
用户 → Web UI → github_files.py → github_service.py → GitHub API
                ↓                              ↓
            表单验证                      文件内容处理
                ↓                              ↓
            渲染编辑页面                    本地缓存
                ↓                              ↓
            用户提交修改 ←─────────────────────┘
                ↓
            github_service.py → GitHub API (推送)
                ↓
            返回结果 → 渲染成功/失败页面
```

#### 2. GitHub Actions 工作流流程

```
用户 → Web UI → github_actions.py → workflow_service.py → GitHub API
                ↓                                  ↓
            选择工作流                          触发工作流
                ↓                                  ↓
            workflow_service.py → 轮询执行状态
                ↓
            获取日志 → 实时显示
                ↓
            解析产物链接 → 下载到 data/downloads/
                ↓
            返回结果 → 渲染状态页面
```

#### 3. 配置管理流程

```
用户 → Web UI → config.py → database_service.py → SQLite
                ↓                              ↓
            表单验证                      CRUD 操作
                ↓                              ↓
            渲染配置页面                  配置持久化
                ↓                              ↓
            读取现有配置 ←─────────────────────┘
                ↓
            加载到环境变量/全局配置
```

### 关键设计决策

1. **使用 PyGithub 而非 requests**
   - 优势：官方封装，自动处理分页、错误重试、速率限制
   - 劣势：额外依赖，但功能完整性值得

2. **SQLite 存储配置**
   - 优势：轻量、无需额外服务、易于备份
   - 劣势：并发写入性能差（本应用单用户，可接受）

3. **服务层分离**
   - 路由层专注 HTTP 处理
   - 服务层专注业务逻辑
   - 便于测试和维护

## 技术栈

- **Web 框架**: Flask 3.x
- **数据库**: SQLite3 + SQLAlchemy（可选 ORM）
- **GitHub API**: PyGithub（推荐）或 requests
- **前端**: Jinja2 模板 + Bootstrap（可选）
- **容器化**: Docker + Docker Compose
- **测试**: pytest + Playwright（chrome-devtools MCP）
- **日志**: Python logging 模块

## 项目结构

### 当前状态（初始化阶段）

```
.
├── .claude/                    # Claude Code 配置目录
├── .git/                       # Git 版本控制
├── .gitignore                  # Git 忽略规则
├── CLAUDE.md                   # Claude Code 工作指南（本文件）
├── readMe.md                   # 项目需求说明
├── requirements.txt            # Python 依赖列表（当前为空）
├── python-venv-setup.sh        # Python 虚拟环境设置脚本
├── venv/                       # Python 虚拟环境（已创建）
└── plan/                       # 项目实施计划目录
```

### 目标结构（完整应用）

```
.
├── app.py                      # Flask 应用主入口
├── config.py                   # 应用配置管理
├── models.py                   # 数据库模型定义
├── routes/                     # 路由模块
│   ├── __init__.py
│   ├── github_files.py         # GitHub 文件管理路由
│   ├── github_actions.py       # GitHub Actions 路由
│   └── config.py               # 配置管理路由
├── services/                   # 业务逻辑层
│   ├── __init__.py
│   ├── github_service.py       # GitHub API 封装
│   ├── database_service.py     # 数据库操作服务
│   └── workflow_service.py     # 工作流管理服务
├── utils/                      # 工具函数
│   ├── __init__.py
│   └── helpers.py
├── static/                     # 静态资源目录
│   ├── css/                    # 样式文件
│   │   └── style.css
│   ├── js/                     # JavaScript 文件
│   │   └── main.js
│   └── downloads/              # GitHub Actions 产物下载目录
├── templates/                  # Jinja2 模板目录
│   ├── base.html               # 基础模板
│   ├── index.html              # 首页
│   ├── files.html              # 文件管理页面
│   ├── actions.html            # Actions 管理页面
│   └── config.html             # 配置页面
├── data/                       # 数据持久化目录
│   └── config.db               # SQLite 配置数据库
├── docker/                     # Docker 部署配置
│   ├── Dockerfile              # Docker 镜像构建文件
│   ├── docker-compose.yml      # Docker Compose 配置
│   └── .dockerignore           # Docker 忽略文件
├── tests/                      # 测试目录
│   ├── __init__.py
│   ├── test_github_service.py
│   ├── test_routes.py
│   └── test_integration.py
├── screenshots/                # 功能验证截图存放目录
├── logs/                       # 应用日志目录
│   └── app.log
├── requirements.txt            # Python 依赖
├── .gitignore
├── CLAUDE.md
└── readMe.md
```

### 目录说明

#### 核心应用文件
- **app.py**: Flask 应用工厂函数，路由注册，应用初始化
- **config.py**: 配置类，环境变量管理，常量定义
- **models.py**: SQLAlchemy 模型，数据库表结构

#### 路由模块（routes/）
分离的 Flask 蓝图，按功能模块组织：
- `github_files.py`: 文件拉取、编辑、推送
- `github_actions.py`: 工作流启动、日志查询、产物下载
- `config.py`: 配置的增删改查

#### 服务层（services/）
业务逻辑封装，与路由和 GitHub API 解耦：
- `github_service.py`: PyGithub 封装，文件操作，工作流操作
- `database_service.py`: SQLite CRUD 操作，配置管理
- `workflow_service.py`: 工作流状态跟踪，日志解析

#### 静态资源（static/）
- **downloads/**: GitHub Actions 产物自动下载到此目录
- CSS/JS: 前端交互逻辑

#### 数据持久化（data/）
- **config.db**: SQLite 数据库，存储 GitHub Token、仓库信息等配置
- 数据库文件应挂载到 Docker 卷中，避免容器重启丢失

#### Docker 部署（docker/）
- 支持一键部署，数据卷持久化
- 环境变量配置 GitHub Token 等敏感信息

## 常用命令

### 开发命令

```bash
# 激活虚拟环境
source venv/bin/activate  # Git Bash/Linux
venv\Scripts\activate     # Windows CMD

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
python app.py

# 运行测试
pytest tests/
```

### Docker 命令

```bash
# 构建镜像
docker build -t github-action-ui .

# 运行容器
docker run -p 5000:5000 -v $(pwd)/data:/app/data github-action-ui

# 使用 docker-compose
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

## Docker 部署

### Dockerfile 示例

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data/downloads

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 启动命令
CMD ["python", "app.py"]
```

### docker-compose.yml 示例

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data        # 持久化配置和下载文件
      - ./logs:/app/logs        # 持久化日志
    environment:
      - FLASK_ENV=production
      - GITHUB_TOKEN=${GITHUB_TOKEN}  # 可选：从环境变量传入
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 部署步骤

```bash
# 1. 构建并启动
docker-compose up -d

# 2. 检查容器状态
docker-compose ps

# 3. 访问应用
open http://localhost:5000

# 4. 查看日志
docker-compose logs -f web
```

## 故障排查

### 常见问题

#### 1. GitHub API 速率限制

**症状**: API 调用返回 403 错误

**解决方案**:
```python
# services/github_service.py

from time import sleep
from datetime import datetime, timedelta

class GitHubRateLimitError(Exception):
    pass

def check_rate_limit(self):
    """检查 API 速率限制"""
    limits = self.client.get_rate_limit()
    core = limits.core

    if core.remaining < 10:
        reset_time = core.reset.timestamp()
        wait_seconds = reset_time - datetime.now().timestamp()
        print(f"接近速率限制，等待 {wait_seconds} 秒...")
        sleep(wait_seconds + 10)
```

#### 2. SQLite 数据库锁定

**症状**: "database is locked" 错误

**解决方案**:
```python
# 使用 WAL 模式（Write-Ahead Logging）

conn = sqlite3.connect('data/config.db')
conn.execute('PRAGMA journal_mode=WAL')
```

#### 3. 跨平台路径问题

**症状**: Windows 上路径分隔符错误

**解决方案**:
```python
from pathlib import Path

# ✅ 正确：自动处理路径分隔符
file_path = Path("data") / "downloads" / "artifact.zip"

# ❌ 错误：硬编码分隔符
file_path = "data/downloads/artifact.zip"  # Linux 上正常，Windows 可能失败
```

#### 4. 中文编码问题

**症状**: 中文文件名乱码

**解决方案**:
```python
# 文件操作时指定编码
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# HTTP 响应头设置
from flask import Response
response = Response(data, mimetype='application/json')
response.headers['Content-Type'] = 'application/json; charset=utf-8'
```

### 调试技巧

```bash
# 启用 Flask 调试模式（仅开发环境）
export FLASK_ENV=development
export FLASK_DEBUG=1

# 查看详细日志
tail -f logs/app.log

# 进入容器调试
docker-compose exec web bash

# 检查数据库内容
sqlite3 data/config.db "SELECT * FROM config;"
```

## 相关资源

### 官方文档
- [Flask 文档](https://flask.palletsprojects.com/)
- [PyGithub 文档](https://pygithub.readthedocs.io/)
- [GitHub Actions API](https://docs.github.com/en/rest/actions)

### 参考项目（调研时使用）
- 搜索关键词：`flask github dashboard`, `github actions manager`
- GitHub Topics: `flask`, `github-api`, `github-actions`, `workflow-manager`

## 重要注意事项

1. **安全性**: GitHub Token 应存储在 SQLite 配置库中，不要硬编码
2. **错误处理**: GitHub API 调用需处理速率限制和网络错误
3. **日志记录**: 记录关键操作和错误信息
4. **跨平台**: 确保 Windows 和 Linux 环境都能正常运行

## 数据库设计

### 配置表（config）

```sql
CREATE TABLE config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,        -- 配置键名
    value TEXT NOT NULL,             -- 配置值
    description TEXT,                -- 配置说明
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 预设配置项

| key | value 示例 | description |
|-----|-----------|-------------|
| `github_token` | `ghp_xxxxxxxxxxxx` | GitHub Personal Access Token |
| `default_repo` | `owner/repo` | 默认仓库名称 |
| `download_dir` | `data/downloads` | Actions 产物下载目录 |
| `workflow_file` | `.github/workflows/deploy.yml` | 默认工作流文件 |

### 数据库操作示例

```python
# services/database_service.py

from pathlib import Path
import sqlite3

class DatabaseService:
    def __init__(self, db_path: str = "data/config.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def get_config(self, key: str) -> Optional[str]:
        """获取配置值"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM config WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def set_config(self, key: str, value: str, description: str = None):
        """设置配置值"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO config (key, value, description)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value, description))
```

## API 端点设计

### GitHub 文件管理

| 端点 | 方法 | 功能 | 参数 |
|------|------|------|------|
| `/files` | GET | 显示文件列表页面 | repo |
| `/files/pull` | POST | 拉取文件 | repo, path, branch |
| `/files/edit/<path>` | GET | 显示编辑页面 | repo, branch |
| `/files/push` | POST | 推送修改 | repo, path, branch, content, message |

### GitHub Actions 管理

| 端点 | 方法 | 功能 | 参数 |
|------|------|------|------|
| `/actions` | GET | 显示工作流列表 | repo |
| `/actions/start` | POST | 启动工作流 | repo, workflow_file, inputs |
| `/actions/logs/<run_id>` | GET | 获取执行日志 | repo, run_id |
| `/actions/status/<run_id>` | GET | 查询执行状态 | repo, run_id |
| `/actions/download/<run_id>` | POST | 下载产物 | repo, run_id, artifact_name |

### 配置管理

| 端点 | 方法 | 功能 | 参数 |
|------|------|------|------|
| `/config` | GET | 显示配置页面 | - |
| `/config/update` | POST | 更新配置 | key, value |
| `/config/delete/<key>` | POST | 删除配置 | key |

### 前端交互示例

```javascript
// static/js/main.js

async function pullFile() {
    const repo = document.getElementById('repo').value;
    const path = document.getElementById('path').value;

    const response = await fetch('/files/pull', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({repo, path})
    });

    const result = await response.json();
    if (result.success) {
        document.getElementById('content').value = result.content;
    } else {
        alert('拉取失败: ' + result.error);
    }
}
```

## 测试验证要求

使用 chrome-devtools MCP 进行测试：
- 导航到 `http://localhost:5000`
- 测试各项功能
- 使用 `take_screenshot` 保存验证结果
- 检查控制台错误（`list_console_messages`）

### 测试清单

- [ ] 配置页面：添加/编辑/删除配置
- [ ] 文件管理：拉取/编辑/推送文件
- [ ] Actions 启动：手动触发工作流
- [ ] 日志查看：实时显示工作流执行日志
- [ ] 产物下载：自动下载到配置目录
- [ ] 错误处理：无效 Token、网络错误等
