# 新功能实现工作流

## 适用场景

从零开始实现新功能，包括需求分析、设计、编码、测试和验证。

## 前置条件

- [ ] 已阅读 [CLAUDE.md](../../CLAUDE.md)
- [ ] 已阅读 [TDD 测试工作流](./tdd-testing-workflow.md)
- [ ] 已激活虚拟环境：`source venv/bin/activate`
- [ ] 已了解项目架构（三层架构）
- [ ] 功能需求已明确

## 工作流程

### Phase 1: 需求分析（5-10 分钟）

#### 1.1 理解需求

**问题清单**：
- 功能要解决什么问题？
- 期望的输入是什么？
- 期望的输出是什么？
- 有哪些边界条件？

**示例**：
```
功能：自动下载 GitHub Actions 产物

问题：工作流生成的文件需要手动下载
输入：仓库路径、工作流 ID
输出：下载到本地的文件列表
边界：只下载 .zip 和 .tar.gz 文件
```

#### 1.2 查阅现有实现

```bash
# 搜索相关代码
grep -r "workflow" app/
grep -r "download" app/
```

**检查清单**：
- [ ] 是否有类似功能可以复用？
- [ ] 是否有可以扩展的服务？
- [ ] 是否需要新增数据库表？

### Phase 2: 设计方案（10-15 分钟）

#### 2.1 API 设计

定义 REST API 端点：

```
POST /api/workflows/<id>/runs/<run_id>/downloads
响应：
{
  "success": true,
  "downloads": [
    {"filename": "artifact.zip", "path": "/app/data/downloads/artifact.zip"}
  ]
}
```

#### 2.2 数据库设计（如需要）

```python
# app/models.py
class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### 2.3 服务层设计

```python
# app/services/download_service.py
class DownloadService:
    def __init__(self, download_dir):
        self.download_dir = Path(download_dir)

    def download_artifacts(self, repo, run_id):
        """下载工作流产物"""
        # 实现逻辑...
```

### Phase 3: TDD 实现（30-60 分钟）

**参考 [TDD 测试工作流](./tdd-testing-workflow.md)**

#### 3.1 编写测试（RED）

```python
# tests/test_services/test_download_service.py
import pytest
from app.services.download_service import DownloadService

class TestDownloadService:
    def test_download_artifacts_success(self, mocker):
        """测试成功下载产物"""
        # Mock GitHub API
        mock_repo = mocker.MagicMock()
        mock_repo.get_artifacts.return_value = [
            mocker.MagicMock(name="artifact.zip", url="http://...")
        ]

        # 执行
        service = DownloadService("/tmp/test")
        result = service.download_artifacts("test/repo", 123)

        # 验证
        assert result["success"] is True
        assert len(result["downloads"]) == 1

    def test_download_artifacts_network_error(self, mocker):
        """测试网络错误处理"""
        mock_requests = mocker.patch('requests.get')
        mock_requests.side_effect = requests.ConnectionError()

        service = DownloadService("/tmp/test")
        result = service.download_artifacts("test/repo", 123)

        assert result["success"] is False
        assert "error" in result
```

运行测试（预期失败）：
```bash
pytest tests/test_services/test_download_service.py -v
# ❌ FAILED (模块不存在)
```

#### 3.2 实现功能（GREEN）

**步骤 1**: 创建服务文件
```bash
touch app/services/download_service.py
```

**步骤 2**: 实现最小代码
```python
# app/services/download_service.py
from pathlib import Path
import requests

class DownloadService:
    def download_artifacts(self, repo, run_id):
        # 最小实现使测试通过
        return {"success": True, "downloads": []}
```

运行测试：
```bash
pytest tests/test_services/test_download_service.py -v
# ✅ PASSED
```

**步骤 3**: 完整实现
```python
class DownloadService:
    def download_artifacts(self, repo, run_id):
        artifacts = self._list_artifacts(repo, run_id)
        downloads = []

        for artifact in artifacts:
            filepath = self._download_file(artifact['url'])
            downloads.append({
                'filename': artifact['name'],
                'filepath': str(filepath)
            })

        return {'success': True, 'downloads': downloads}

    def _list_artifacts(self, repo, run_id):
        """列出可用产物"""
        # 调用 GitHub API
        pass

    def _download_file(self, url):
        """下载单个文件"""
        # 下载逻辑
        pass
```

#### 3.3 重构优化（REFACTOR）

```python
# 添加日志
import logging
logger = logging.getLogger(__name__)

class DownloadService:
    def download_artifacts(self, repo, run_id):
        logger.info(f"开始下载产物: repo={repo}, run_id={run_id}")
        # ... 实现代码
```

运行测试确保重构后依然通过：
```bash
pytest tests/test_services/test_download_service.py -v
# ✅ PASSED
```

### Phase 4: 集成测试（15-20 分钟）

#### 4.1 创建 API 路由

```python
# app/routes/workflow_routes.py
from flask import jsonify, request
from app.services.download_service import DownloadService

@bp.route('/workflows/<int:workflow_id>/runs/<int:run_id>/downloads', methods=['POST'])
def download_artifacts(workflow_id, run_id):
    service = DownloadService(current_app.config['DOWNLOAD_DIR'])
    result = service.download_artifacts(repo, run_id)
    return jsonify(result)
```

#### 4.2 编写集成测试

```python
# tests/test_integration/test_download_api.py
import pytest
from app import create_app

def test_download_artifacts_api(client, mocker):
    """测试下载产物 API"""
    # Mock GitHub API
    mock_service = mocker.patch('app.services.download_service.DownloadService')
    mock_service.return_value.download_artifacts.return_value = {
        'success': True,
        'downloads': [{'filename': 'test.zip', 'filepath': '/tmp/test.zip'}]
    }

    rv = client.post('/api/workflows/1/runs/123/downloads')
    assert rv.status_code == 200
    assert rv.json['success'] is True
```

### Phase 5: E2E 测试（10-15 分钟）

#### 5.1 使用 chrome-devtools MCP 测试

```python
# 启动应用
python run.py &

# 打开浏览器
mcp__chrome-devtools__new_page(url="http://localhost:5000")

# 导航到工作流页面
mcp__chrome-devtools__navigate_page(url="http://localhost:5000/workflows")

# 点击下载按钮
mcp__chrome-devtools__click(uid="download-button-123")

# 等待完成
mcp__chrome-devtools__wait_for(text=["下载成功"], timeout=30000)

# 截图
mcp__chrome-devtools__take_screenshot(
    filePath="screenshots/feature_download_artifacts.png"
)

# 检查控制台错误
errors = mcp__chrome-devtools__list_console_messages(types=["error"])
assert len(errors) == 0
```

#### 5.2 验证文件下载

```bash
# 检查文件是否存在
ls -lh data/downloads/

# 验证文件内容
file data/downloads/artifact.zip
```

### Phase 6: 文档更新（5-10 分钟）

#### 6.1 更新 CLAUDE.md

```markdown
### GitHub Actions 管理

| 端点 | 方法 | 功能 | 参数 |
|------|------|------|------|
| ... | ... | ... | ... |
| `/api/workflows/<id>/runs/<run_id>/downloads` | POST | 下载产物 | run_id, artifact_name |
```

#### 6.2 添加使用示例

```markdown
#### 下载工作流产物

```bash
curl -X POST http://localhost:5000/api/workflows/1/runs/123/downloads
```
```

## 完成检查清单

### 代码质量
- [ ] 所有单元测试通过：`pytest tests/`
- [ ] 测试覆盖率 ≥ 80%：`pytest --cov=app`
- [ ] 类型检查通过：`mypy app/`
- [ ] 代码格式化：`black app/`
- [ ] Linting 通过：`flake8 app/`

### 功能验证
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] E2E 测试通过（chrome-devtools）
- [ ] 截图已保存

### 文档更新
- [ ] CLAUDE.md 已更新
- [ ] API 文档已更新
- [ ] 使用示例已添加

### Git 提交
- [ ] 代码已提交
- [ ] 提交信息清晰
- [ ] 分支策略正确

## 常见问题

### Q1: 测试依赖真实 GitHub API 怎么办？

**A**: 使用 Mock 对象模拟 API 调用

```python
def test_download_with_mock(mocker):
    mock_github = mocker.patch('app.services.github_service.Github')
    mock_github.return_value.get_repo.return_value.get_artifacts.return_value = [...]
```

### Q2: 如何测试异步操作？

**A**: 使用 pytest-asyncio 或 Mock 时间

```python
def test_async_download(mocker):
    mocker.patch('time.sleep')  # 跳过等待
    # 测试代码
```

### Q3: E2E 测试太慢怎么办？

**A**: 只对关键路径进行 E2E 测试，其他使用单元/集成测试

## 相关工作流

- [TDD 测试工作流](./tdd-testing-workflow.md) - 测试驱动开发
- [GitHub API 集成工作流](./github-integration-workflow.md) - GitHub API 交互
- [服务层开发工作流](./service-development-workflow.md) - 业务逻辑层
- [代码审查工作流](./code-review-workflow.md) - 代码质量检查

---

**最后更新**：2026-03-12
