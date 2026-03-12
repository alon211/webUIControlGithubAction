# TDD 测试工作流

## 适用场景

所有需要编写测试的开发任务，包括：
- 实现新功能
- 修复 Bug
- 重构代码
- 添加新模块

## 前置条件

- [ ] 已阅读 [CLAUDE.md](../../CLAUDE.md)
- [ ] 已激活虚拟环境：`source venv/bin/activate`
- [ ] 已安装测试依赖：`pip install pytest pytest-flask pytest-cov pytest-mock`
- [ ] 了解项目架构（三层架构）

## TDD 核心原则

### 红-绿-重构循环

TDD（Test-Driven Development）的核心是编写测试来驱动开发，遵循以下循环：

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. RED   编写一个失败的测试                            │
│         → 测试描述了我们想要的功能                      │
│         → 运行测试，确认失败（红灯）                     │
│                                                         │
│  2. GREEN 编写最少代码使测试通过                        │
│         → 不求完美，只求通过                            │
│         → 运行测试，确认通过（绿灯）                     │
│                                                         │
│  3. REFACTOR 重构优化代码                               │
│         → 改进代码质量                                  │
│         → 运行测试，确保依然通过                        │
│                                                         │
│  4. 重复循环                                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 关键原则

1. **测试先行**：先写测试，再写代码
2. **小步快跑**：每次只写一个小测试
3. **持续重构**：保持代码整洁
4. **充分测试**：覆盖关键路径

## 测试层级

项目采用三层测试金字塔：

```
           ▲
          / \          E2E 测试（少量）
         /---\         - 完整用户流程
        /  ?  \        - chrome-devtools MCP
       /-------\
      /---------\      集成测试（中等）
     /  20-30%  \      - API 端点测试
    /-----------\     - 服务集成测试
   /             \
  /---------------\  单元测试（大量）
 /      70-80%     \ - 函数/方法测试
/-------------------\- 类/模块测试
```

### 1. 单元测试（Unit Tests）

**目标**：测试单个函数或方法

**特点**：
- 快速执行（毫秒级）
- 隔离依赖（使用 Mock）
- 覆盖率最高（70-80%）

**示例**：

```python
# tests/test_services/test_config_service.py
import pytest
from app.services.config_service import ConfigService

class TestConfigService:
    """配置服务单元测试"""

    def test_get_config_success(self, mocker):
        """测试成功获取配置"""
        # Mock 数据库
        mock_conn = mocker.patch('sqlite3.connect')
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = ['test_value']

        # 执行
        service = ConfigService()
        result = service.get('test_key')

        # 验证
        assert result == 'test_value'
        mock_cursor.execute.assert_called_once()

    def test_get_config_not_found(self, mocker):
        """测试配置不存在"""
        mock_conn = mocker.patch('sqlite3.connect')
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = None

        service = ConfigService()
        result = service.get('nonexistent')

        assert result is None

    def test_set_config(self, mocker):
        """测试设置配置"""
        mock_conn = mocker.patch('sqlite3.connect')

        service = ConfigService()
        service.set('test_key', 'test_value', '测试配置')

        # 验证 SQL 执行
        mock_conn.return_value.execute.assert_called()
```

**运行**：
```bash
pytest tests/test_services/test_config_service.py -v
```

### 2. 集成测试（Integration Tests）

**目标**：测试多个组件协同工作

**特点**：
- 中等速度（秒级）
- 真实数据库（内存数据库）
- 测试 API 端点（20-30%）

**示例**：

```python
# tests/test_integration/test_config_api.py
import pytest
from app import create_app

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app({
        'TESTING': True,
        'DATABASE': ':memory:',  # 使用内存数据库
        'SECRET_KEY': 'test'
    })

    with app.app_context():
        from app.models import db
        db.create_all()  # 创建测试表

    yield app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

class TestConfigAPI:
    """配置 API 集成测试"""

    def test_get_config_empty(self, client):
        """测试获取空配置"""
        rv = client.get('/api/config')
        assert rv.status_code == 200
        assert rv.json == {}

    def test_set_and_get_config(self, client):
        """测试设置并获取配置"""
        # 设置配置
        rv = client.put('/api/config', json={
            'github_token': 'ghp_test',
            'github_repo': 'test/repo'
        })
        assert rv.status_code == 200

        # 获取配置
        rv = client.get('/api/config')
        assert rv.status_code == 200
        assert rv.json['github_token'] == 'ghp_test'

    def test_update_config(self, client):
        """测试更新配置"""
        # 先设置
        client.put('/api/config', json={'github_token': 'old_token'})

        # 更新
        rv = client.put('/api/config/github_token', json={
            'value': 'new_token'
        })
        assert rv.status_code == 200

        # 验证
        rv = client.get('/api/config/github_token')
        assert rv.json['value'] == 'new_token'
```

**运行**：
```bash
pytest tests/test_integration/ -v
```

### 3. E2E 测试（End-to-End Tests）

**目标**：测试完整用户流程

**特点**：
- 较慢速度（分钟级）
- 真实浏览器（chrome-devtools MCP）
- 关键路径覆盖（少量）

**示例流程**：

```python
# E2E 测试：配置保存流程

# 1. 启动应用
python run.py &

# 2. 打开浏览器
mcp__chrome-devtools__new_page(url="http://localhost:5000/config")

# 3. 操作前快照
mcp__chrome-devtools__take_snapshot()

# 4. 填写表单
mcp__chrome-devtools__fill_form([
    {"uid": "github_token", "value": "ghp_test_token"},
    {"uid": "github_repo", "value": "test/repo"}
])

# 5. 点击保存
mcp__chrome-devtools__click(uid="save_button")

# 6. 等待响应
mcp__chrome-devtools__wait_for(
    text=["保存成功"],
    timeout=5000
)

# 7. 操作后快照
mcp__chrome-devtools__take_snapshot()

# 8. 保存截图
mcp__chrome-devtools__take_screenshot(
    filePath="screenshots/e2e_config_save.png"
)

# 9. 检查控制台错误
errors = mcp__chrome-devtools__list_console_messages(
    types=["error"]
)
assert len(errors) == 0, f"控制台有错误: {errors}"

# 10. 验证数据库（使用 pytest）
# ... 验证配置已保存
```

**运行**：
```bash
# 手动运行或结合 pytest
pytest tests/test_e2e/ -v
```

## TDD 实战示例

### 场景：实现配置读取功能

#### 步骤 1: RED - 编写失败测试

```python
# tests/test_services/test_config_service.py

def test_get_github_token():
    """测试获取 GitHub Token"""
    service = ConfigService()
    token = service.get("github_token")

    assert token is not None
    assert token.startswith("ghp_")
```

**运行测试**：
```bash
pytest tests/test_services/test_config_service.py::test_get_github_token -v

# ❌ FAILED
# AttributeError: 'ConfigService' object has no attribute 'get'
```

#### 步骤 2: GREEN - 实现最小代码

```python
# app/services/config_service.py

class ConfigService:
    def get(self, key: str) -> str:
        """获取配置值"""
        # 最小实现使测试通过
        return "ghp_test_token_123"
```

**运行测试**：
```bash
pytest tests/test_services/test_config_service.py::test_get_github_token -v

# ✅ PASSED
```

#### 步骤 3: REFACTOR - 重构优化

```python
# app/services/config_service.py

from pathlib import Path
from typing import Optional
import sqlite3
import logging

logger = logging.getLogger(__name__)

class ConfigService:
    def __init__(self, db_path: str = "data/config.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    def get(self, key: str) -> Optional[str]:
        """从数据库获取配置值"""
        logger.debug(f"获取配置: {key}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM config WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            return row[0] if row else None

    def set(self, key: str, value: str, description: str = None):
        """设置配置值"""
        logger.info(f"设置配置: {key}")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO config (key, value)
                VALUES (?, ?)
            """, (key, value))
```

**运行测试**：
```bash
pytest tests/test_services/test_config_service.py::test_get_github_token -v

# ✅ PASSED (重构后依然通过)
```

#### 步骤 4: 添加更多测试

```python
def test_get_config_not_found():
    """测试配置不存在"""
    service = ConfigService()
    result = service.get("nonexistent_key")
    assert result is None

def test_set_and_get_config():
    """测试设置并获取配置"""
    service = ConfigService()
    service.set("test_key", "test_value")

    result = service.get("test_key")
    assert result == "test_value"
```

**运行所有测试**：
```bash
pytest tests/test_services/test_config_service.py -v

# ✅ 3 passed
```

## 测试覆盖率要求

### 覆盖率标准

```bash
# 生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term

# 要求：
# - 整体覆盖率 ≥ 80%
# - services/ 模块 ≥ 90%
# - routes/ 模块 ≥ 70%
# - models.py ≥ 85%
```

### 覆盖率报告示例

```
Name                              Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
app/__init__.py                      10      2    80%   15-16
app/models.py                        25      3    88%   45-47
app/services/config_service.py       30      2    93%   78-79
app/services/github_service.py       45      8    82%   123-130
app/routes/config_routes.py          20      5    75%   34-38
-----------------------------------------------------------------------
TOTAL                               130     20    84%
```

### 提高覆盖率

```bash
# 查看未覆盖的代码
open htmlcov/index.html

# 针对未覆盖的分支添加测试
# 例如：
# - 错误处理分支
# - 边界条件
# - 异常路径
```

## 测试命名规范

### 文件命名

```
tests/
├── conftest.py                    # pytest 配置和 fixtures
├── test_services/                 # 服务层测试
│   ├── __init__.py
│   ├── test_config_service.py
│   ├── test_github_service.py
│   └── test_download_service.py
├── test_routes/                   # 路由测试
│   ├── __init__.py
│   ├── test_config_routes.py
│   └── test_workflow_routes.py
├── test_integration/              # 集成测试
│   ├── __init__.py
│   └── test_api_integration.py
└── test_e2e/                      # E2E 测试
    ├── __init__.py
    ├── test_config_workflow.py
    └── test_file_edit_workflow.py
```

### 测试函数命名

#### ✅ 好的命名

```python
def test_get_file_success():
    """测试成功获取文件"""
    pass

def test_get_file_not_found():
    """测试文件不存在"""
    pass

def test_get_file_without_permission():
    """测试无权限获取文件"""
    pass
```

#### ❌ 差的命名

```python
def test_file():
    """不清晰"""
    pass

def test1():
    """无意义"""
    pass

def get_file_test():
    """不符合命名规范"""
    pass
```

## chrome-devtools MCP 测试规范

### E2E 测试流程模板

```python
# tests/test_e2e/test_config_workflow.py

def test_config_save_workflow():
    """测试配置保存完整流程"""
    # 1. 启动应用
    import subprocess
    proc = subprocess.Popen(['python', 'run.py'])

    try:
        # 2. 打开浏览器
        mcp__chrome-devtools__new_page(
            url="http://localhost:5000/config"
        )

        # 3. 操作前快照
        before = mcp__chrome-devtools__take_snapshot()

        # 4. 填写表单
        mcp__chrome-devtools__fill_form([
            {"uid": "github_token", "value": "ghp_test"},
            {"uid": "github_repo", "value": "owner/repo"}
        ])

        # 5. 提交
        mcp__chrome-devtools__click(uid="save_button")

        # 6. 等待响应
        mcp__chrome-devtools__wait_for(
            text=["保存成功"],
            timeout=5000
        )

        # 7. 操作后快照
        after = mcp__chrome-devtools__take_snapshot()

        # 8. 保存截图
        mcp__chrome-devtools__take_screenshot(
            filePath="screenshots/e2e_config_save.png"
        )

        # 9. 检查控制台错误
        errors = mcp__chrome-devtools__list_console_messages(
            types=["error"]
        )
        assert len(errors) == 0

    finally:
        # 10. 清理
        proc.terminate()
```

### 截图命名规范

```
screenshots/
├── unit/                       # 单元测试截图（可选）
├── integration/                # 集成测试截图
│   ├── 01_api_config_get.png
│   └── 02_api_config_set.png
└── e2e/                        # E2E 测试截图（必须）
    ├── 01_home_page.png
    ├── 02_config_page.png
    ├── 03_config_save_success.png
    ├── 04_files_list.png
    ├── 05_file_edit.png
    ├── 06_workflow_list.png
    ├── 07_workflow_trigger.png
    └── 08_workflow_logs.png
```

## 测试数据管理

### Fixtures 使用

```python
# tests/conftest.py

import pytest
from app import create_app
from app.services.github_service import GitHubService

@pytest.fixture
def app():
    """创建测试应用实例"""
    app = create_app({
        "TESTING": True,
        "DATABASE": ":memory:",
        "SECRET_KEY": "test-secret"
    })

    with app.app_context():
        from app.models import db
        db.create_all()
        yield app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def github_client_mock(mocker):
    """Mock GitHub 客户端"""
    mock = mocker.patch("app.services.github_service.Github")
    mock.return_value.get_repo.return_value.get_contents.return_value.content = b"test"
    return mock

@pytest.fixture
def sample_config():
    """示例配置数据"""
    return {
        "github_token": "ghp_test_token",
        "github_repo": "test/repo",
        "download_dir": "data/downloads"
    }

@pytest.fixture
def authenticated_client(client, sample_config):
    """已认证的测试客户端"""
    # 设置测试配置
    with client.session_transaction() as sess:
        sess['config'] = sample_config
    return client
```

### Mock 对象示例

```python
def test_get_file_with_mock(github_client_mock):
    """使用 Mock 对象测试"""
    # 配置 Mock 返回值
    github_client_mock.return_value.get_repo.return_value.get_contents.return_value.content = b'{"key": "value"}'

    # 执行测试
    service = GitHubService("any_token")
    result = service.get_file("owner/repo", "config.json")

    # 验证
    assert result["success"] is True
    assert result["content"] == '{"key": "value"}'

    # 验证 API 调用
    github_client_mock.assert_called_once_with("any_token")
```

### 参数化测试

```python
@pytest.mark.parametrize("repo,expected", [
    ("owner/repo", True),
    ("invalid_repo", False),
    ("", False),
])
def test_validate_repo(repo, expected):
    """参数化测试仓库验证"""
    service = GitHubService("token")
    result = service.validate_repo(repo)
    assert result == expected
```

## 测试命令速查

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_services.py

# 运行特定测试
pytest tests/test_services.py::TestConfigService::test_get_config

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s

# 运行覆盖率
pytest --cov=app --cov-report=html

# 只运行失败的测试
pytest --lf

# 运行标记的测试
pytest -m "not slow"  # 跳过慢速测试
pytest -m "e2e"       # 只运行 E2E 测试

# 失败时进入调试器
pytest --pdb

# 生成 HTML 报告
pytest --html=report.html --self-contained-html

# 并行运行（需要 pytest-xdist）
pytest -n auto

# 组合使用
pytest -v --cov=app --cov-report=html -m "not slow"
```

## TDD 常见错误

### ❌ 错误 1: 先写代码后写测试

```python
# 错误：先实现了功能，再写测试
def get_file(repo, path):
    # 完整实现...
    return result

# 然后才写测试
def test_get_file():
    # 测试代码...
    pass
```

**问题**：测试变成了验证，而非驱动开发

**✅ 正确做法**：

```python
# 先写测试（测试会失败）
def test_get_file():
    service = GitHubService("token")
    result = service.get_file("repo", "path")
    assert result["success"] is True

# 再实现功能（测试通过）
def get_file(repo, path):
    # 最小实现
    return {"success": True}
```

### ❌ 错误 2: 测试实现细节

```python
# 错误：测试内部实现
def test_get_file_uses_github_api():
    service = GitHubService("token")
    assert service.client.get_repo.called  # 测试内部实现
```

**问题**：重构代码会破坏测试

**✅ 正确做法**：

```python
# 正确：测试外部行为
def test_get_file_returns_content():
    service = GitHubService("token")
    result = service.get_file("repo", "path")
    assert "content" in result  # 测试返回结果
```

### ❌ 错误 3: 测试依赖外部服务

```python
# 错误：直接调用真实 GitHub API
def test_get_file():
    service = GitHubService(real_token)  # 需要网络
    result = service.get_file("real_repo", "path")
```

**问题**：测试慢、不稳定、需要真实凭证

**✅ 正确做法**：

```python
# 正确：Mock 外部依赖
def test_get_file(github_client_mock):
    service = GitHubService("any_token")
    result = service.get_file("repo", "path")
    assert result["success"] is True
```

### ❌ 错误 4: 测试太复杂

```python
# 错误：一个测试做太多事情
def test_complete_workflow():
    # 测试整个应用流程，50 行代码
    # 难以维护、难以调试
    pass
```

**问题**：难以定位问题、运行缓慢

**✅ 正确做法**：

```python
# 正确：拆分成小测试
def test_step1_load_config():
    pass

def test_step2_fetch_data():
    pass

def test_step3_process_data():
    pass
```

## 完成检查清单

### 测试质量
- [ ] 所有单元测试通过：`pytest tests/test_services/`
- [ ] 所有集成测试通过：`pytest tests/test_integration/`
- [ ] E2E 测试通过：使用 chrome-devtools
- [ ] 测试覆盖率 ≥ 80%：`pytest --cov=app`

### 测试文档
- [ ] 测试函数有清晰的文档字符串
- [ ] 测试命名符合规范
- [ ] 复杂逻辑有注释说明

### E2E 验证
- [ ] 截图已保存到 `screenshots/`
- [ ] 控制台无错误
- [ ] 用户流程完整

### 相关工作流
- [ ] [新功能实现工作流](./feature-implementation.md)
- [ ] [Bug 修复工作流](./bug-fix-workflow.md)
- [ ] [代码审查工作流](./code-review-workflow.md)

## 常见问题

### Q1: 如何测试异步操作？

**A**: 使用 Mock 时间或 pytest-asyncio

```python
def test_async_download(mocker):
    # Mock 时间跳过等待
    mocker.patch('time.sleep')

    # 测试代码
```

### Q2: 如何测试私有方法？

**A**: 不要测试私有方法，测试公开接口

```python
# ❌ 错误
def test_private_method():
    service._private_method()

# ✅ 正确
def test_public_behavior():
    result = service.public_method()
    assert result == expected
```

### Q3: E2E 测试太慢怎么办？

**A**: 只对关键路径进行 E2E 测试

- 用户登录流程
- 核心业务流程
- 支付/交易流程

其他使用单元/集成测试。

### Q4: 如何测试数据库操作？

**A**: 使用内存数据库和事务回滚

```python
@pytest.fixture
def db_session():
    # 创建内存数据库
    engine = create_engine('sqlite:///:memory:')
    # ... 测试代码
    yield session
    # 自动回滚
```

## 相关资源

- [pytest 文档](https://docs.pytest.org/)
- [pytest-mock 文档](https://pytest-mock.readthedocs.io/)
- [chrome-devtools MCP 文档](../../CLAUDE.md#测试验证要求)

---

**最后更新**：2026-03-12
