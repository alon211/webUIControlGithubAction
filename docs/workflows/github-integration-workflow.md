# GitHub API 集成工作流

## 适用场景

开发与 GitHub API 交互的功能，如：
- 文件拉取/推送
- 工作流触发
- 仓库管理
- Issue/PR 操作

## 前置条件

- [ ] 已有 GitHub Token
- [ ] 已安装 PyGithub：`pip install PyGithub`
- [ ] 已阅读 [TDD 测试工作流](./tdd-testing-workflow.md)

## 核心原则

### 1. 使用 PyGithub

```python
# ✅ 推荐
from github import Github
g = Github(token)
repo = g.get_repo("owner/repo")

# ❌ 避免
import requests
requests.get("https://api.github.com/...", headers={...})
```

### 2. 错误处理

```python
from github import GithubException

try:
    repo = g.get_repo("owner/repo")
    content = repo.get_contents("file.txt")
except GithubException as e:
    logger.error(f"GitHub API 错误: {e}")
    return {"success": False, "error": str(e)}
```

### 3. 速率限制

```python
# 检查速率限制
limits = g.get_rate_limit()
if limits.core.remaining < 10:
    logger.warning(f"API 速率限制即将用尽: {limits.core.remaining}")
```

## 工作流程

### Phase 1: API 设计（5 分钟）

定义清晰的 API 接口：

```python
# app/services/github_service.py

class GitHubService:
    def get_file(self, repo: str, path: str, branch: str = "main") -> dict:
        """获取文件内容"""
        pass

    def update_file(self, repo: str, path: str, content: str, message: str) -> dict:
        """更新文件"""
        pass
```

### Phase 2: TDD 实现（15-30 分钟）

#### 2.1 编写测试（使用 Mock）

```python
# tests/test_services/test_github_service.py

def test_get_file_success(mocker):
    """测试成功获取文件"""
    mock_github = mocker.patch('app.services.github_service.Github')
    mock_repo = mock_github.return_value.get_repo.return_value
    mock_content = mock_repo.get_contents.return_value
    mock_content.content = b"eyJrZXkiOiAidmFsdWUifQ=="  # base64

    service = GitHubService("fake_token")
    result = service.get_file("owner/repo", "config.json")

    assert result["success"] is True
    assert result["content"] == '{"key": "value"}'
```

#### 2.2 实现功能

```python
# app/services/github_service.py

import base64
import logging
from github import Github
from github.GithubException import GithubException

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self, token: str):
        self.client = Github(token)

    def get_file(self, repo: str, path: str, branch: str = "main") -> dict:
        """获取文件内容"""
        try:
            repo_obj = self.client.get_repo(repo)
            content_file = repo_obj.get_contents(path, ref=branch)

            # 解码 base64
            decoded = base64.b64decode(content_file.content).decode('utf-8')

            return {
                "success": True,
                "content": decoded,
                "sha": content_file.sha
            }

        except GithubException as e:
            logger.error(f"获取文件失败: {e}")
            return {"success": False, "error": str(e)}
```

### Phase 3: 速率限制处理（5 分钟）

```python
def check_rate_limit(self):
    """检查 API 速率限制"""
    limits = self.client.get_rate_limit()
    core = limits.core

    if core.remaining < 10:
        reset_time = core.reset.timestamp()
        wait_seconds = reset_time - datetime.now().timestamp()
        logger.warning(f"API 速率限制，需等待 {wait_seconds} 秒")
        return False

    return True
```

### Phase 4: 集成测试（10 分钟）

```python
# tests/test_integration/test_github_api.py

@pytest.mark.skipif("not os.getenv('GITHUB_TOKEN')")
def test_real_github_api():
    """真实 API 测试（需要 Token）"""
    token = os.getenv('GITHUB_TOKEN')
    service = GitHubService(token)

    result = service.get_file("owner/repo", "README.md")
    assert result["success"] is True
```

## 最佳实践

### 1. Token 管理

```python
# 从配置读取
from app.services.config_service import ConfigService

config_service = ConfigService()
token = config_service.get("github_token")

service = GitHubService(token)
```

### 2. 错误重试

```python
from time import sleep
from random import uniform

def get_file_with_retry(self, repo, path, max_retries=3):
    """带重试的文件获取"""
    for i in range(max_retries):
        try:
            return self.get_file(repo, path)
        except GithubException as e:
            if i < max_retries - 1:
                sleep(uniform(1, 3))  # 指数退避
            else:
                raise
```

### 3. 大文件处理

```python
def get_large_file(self, repo, path):
    """获取大文件（分块）"""
    repo_obj = self.client.get_repo(repo)
    content_file = repo_obj.get_contents(path)

    if content_file.size > 1024 * 1024:  # > 1MB
        logger.warning(f"大文件: {content_file.size} bytes")

    return self.get_file(repo, path)
```

## 常见问题

### Q1: 如何处理速率限制？

**A**: 实现指数退避和缓存：

```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def get_file_cached(self, repo, path):
    """缓存文件内容"""
    return self.get_file(repo, path)
```

### Q2: 如何测试真实 API？

**A**: 使用环境变量和 pytest skip：

```python
@pytest.mark.skipif("not os.getenv('GITHUB_TOKEN')")
def test_real_api():
    # 真实 API 测试
    pass
```

### Q3: 如何处理 Webhook？

**A**: 验证签名：

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """验证 Webhook 签名"""
    hash_obj = hmac.new(secret.encode(), payload, hashlib.sha256)
    expected = f"sha256={hash_obj.hexdigest()}"
    return hmac.compare_digest(expected, signature)
```

## 完成检查清单

### 功能实现
- [ ] API 调用正常
- [ ] 错误处理完善
- [ ] 速率限制处理
- [ ] Token 安全存储

### 测试覆盖
- [ ] 单元测试（Mock）
- [ ] 集成测试（可选）
- [ ] 错误场景测试
- [ ] 覆盖率 ≥ 80%

### 文档更新
- [ ] API 文档已更新
- [ ] 使用示例已添加

## 相关工作流

- [服务层开发工作流](./service-development-workflow.md) - 服务层封装
- [TDD 测试工作流](./tdd-testing-workflow.md) - Mock 测试

---

**最后更新**：2026-03-12
