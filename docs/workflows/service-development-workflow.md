# 服务层开发工作流

## 适用场景

开发业务逻辑层代码，包括：
- 数据库操作封装
- GitHub API 调用封装
- 业务逻辑处理
- 数据转换和验证

## 前置条件

- [ ] 已了解项目架构（三层架构）
- [ ] 已阅读 [TDD 测试工作流](./tdd-testing-workflow.md)
- [ ] 已激活虚拟环境

## 服务层设计原则

### 1. 单一职责

```python
# ✅ 好的设计
class ConfigService:
    """配置管理"""
    pass

class GitHubService:
    """GitHub API"""
    pass

class DownloadService:
    """文件下载"""
    pass

# ❌ 差的设计
class UtilityService:
    """所有功能都混在一起"""
    pass
```

### 2. 依赖注入

```python
# ✅ 好的设计
class DownloadService:
    def __init__(self, github_client, config_service):
        self.github = github_client
        self.config = config_service

# ❌ 差的设计（硬编码依赖）
class DownloadService:
    def __init__(self):
        self.github = Github()  # 硬编码
```

### 3. 错误处理

```python
from typing import Optional, Dict, Any

class ConfigService:
    def get(self, key: str) -> Optional[str]:
        """获取配置，失败返回 None"""
        try:
            # 实现
            pass
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            return None
```

## 工作流程

### Phase 1: 设计接口（5 分钟）

定义清晰的接口：

```python
# app/services/config_service.py

from typing import Optional, Dict, Any
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigService:
    """配置管理服务"""

    def __init__(self, db_path: str = "data/config.db"):
        self.db_path = Path(db_path)

    def get(self, key: str) -> Optional[str]:
        """获取配置值"""
        pass

    def set(self, key: str, value: str) -> bool:
        """设置配置值"""
        pass

    def get_all(self) -> Dict[str, str]:
        """获取所有配置"""
        pass
```

### Phase 2: TDD 实现（20-30 分钟）

#### 2.1 编写测试

```python
# tests/test_services/test_config_service.py

import pytest
from app.services.config_service import ConfigService

class TestConfigService:
    def test_get_config_success(self, mocker):
        """测试成功获取配置"""
        mock_conn = mocker.patch('sqlite3.connect')
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = ['test_value']

        service = ConfigService()
        result = service.get('test_key')

        assert result == 'test_value'

    def test_get_config_not_found(self, mocker):
        """测试配置不存在"""
        mock_conn = mocker.patch('sqlite3.connect')
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = None

        service = ConfigService()
        result = service.get('nonexistent')

        assert result is None
```

#### 2.2 实现功能

```python
# app/services/config_service.py

def get(self, key: str) -> Optional[str]:
    """获取配置值"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT value FROM config WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
    except sqlite3.Error as e:
        logger.error(f"数据库错误: {e}")
        return None
```

#### 2.3 完善实现

```python
def set(self, key: str, value: str) -> bool:
    """设置配置值"""
    try:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                INSERT OR REPLACE INTO config (key, value)
                VALUES (?, ?)
            """, (key, value))

            logger.info(f"配置已更新: {key}")
            return True

    except sqlite3.Error as e:
        logger.error(f"保存配置失败: {e}")
        return False
```

### Phase 3: 集成测试（10 分钟）

```python
# tests/test_integration/test_config_service.py

import pytest
import tempfile
from app.services.config_service import ConfigService

@pytest.fixture
def temp_db():
    """临时数据库"""
    fd, path = tempfile.mkstemp(suffix='.db')
    yield path
    os.close(fd)
    os.unlink(path)

def test_set_and_get(temp_db):
    """测试设置并获取配置"""
    service = ConfigService(temp_db)

    # 设置
    assert service.set("test_key", "test_value")

    # 获取
    assert service.get("test_key") == "test_value"
```

### Phase 4: 优化重构（5-10 分钟）

#### 4.1 添加缓存

```python
from functools import lru_cache

class ConfigService:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._cache = {}

    def get(self, key: str) -> Optional[str]:
        """获取配置（带缓存）"""
        if key in self._cache:
            return self._cache[key]

        value = self._get_from_db(key)
        if value:
            self._cache[key] = value

        return value
```

#### 4.2 添加批量操作

```python
def set_many(self, configs: Dict[str, str]) -> bool:
    """批量设置配置"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)",
                configs.items()
            )
        return True
    except sqlite3.Error as e:
        logger.error(f"批量保存失败: {e}")
        return False
```

## 最佳实践

### 1. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

class ConfigService:
    def get(self, key: str):
        logger.debug(f"获取配置: {key}")
        # 实现
        logger.info(f"配置获取成功: {key}")
```

### 2. 类型注解

```python
from typing import Optional, Dict, List

class ConfigService:
    def get(self, key: str) -> Optional[str]:
        pass

    def get_all(self) -> Dict[str, str]:
        pass
```

### 3. 参数验证

```python
def set(self, key: str, value: str) -> bool:
    """设置配置值"""
    if not key or not isinstance(key, str):
        raise ValueError("key 必须是非空字符串")

    if not value or not isinstance(value, str):
        raise ValueError("value 必须是非空字符串")

    # 实现
```

## 完成检查清单

### 代码质量
- [ ] 单一职责
- [ ] 依赖注入
- [ ] 错误处理
- [ ] 日志记录
- [ ] 类型注解

### 测试覆盖
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 覆盖率 ≥ 80%
- [ ] 边界条件测试

### 文档
- [ ] 类文档字符串
- [ ] 方法文档字符串
- [ ] 复杂逻辑注释

## 相关工作流

- [GitHub API 集成工作流](./github-integration-workflow.md) - GitHub API 封装
- [数据库变更工作流](./database-migration-workflow.md) - 数据库操作

---

**最后更新**：2026-03-12
