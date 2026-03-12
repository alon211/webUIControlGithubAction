# 数据库变更工作流

## 适用场景

修改数据库模型，包括：
- 添加新表
- 修改表结构
- 添加/删除字段
- 数据迁移

## 前置条件

- [ ] 已了解项目使用的 ORM（SQLAlchemy）
- [ ] 已备份数据库（生产环境）
- [ ] 已阅读 [TDD 测试工作流](./tdd-testing-workflow.md)

## 工作流程

### Phase 1: 设计变更（5-10 分钟）

#### 1.1 规划变更

**变更清单**：
- 需要添加/删除哪些表？
- 需要添加/删除哪些字段？
- 是否需要数据迁移？
- 是否有依赖关系？

**示例**：
```
变更：添加下载记录表

表名：downloads
字段：
  - id: 主键
  - run_id: 工作流运行 ID
  - filename: 文件名
  - filepath: 文件路径
  - downloaded_at: 下载时间
```

#### 1.2 定义模型

```python
# app/models.py

from datetime import datetime
from app import db

class Download(db.Model):
    """下载记录表"""
    __tablename__ = 'downloads'

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Download {self.filename}>'
```

### Phase 2: 创建迁移脚本（10 分钟）

#### 2.1 手动迁移（简单项目）

```python
# scripts/migrate_add_downloads_table.py

from app import create_app, db
from app.models import Download
import sys

def upgrade():
    """执行升级"""
    app = create_app()

    with app.app_context():
        # 创建表
        db.create_all()
        print("✓ 创建 downloads 表")

        # 添加索引
        db.engine.execute(
            'CREATE INDEX IF NOT EXISTS idx_downloads_run_id ON downloads(run_id)'
        )
        print("✓ 创建索引")

def downgrade():
    """执行回滚"""
    app = create_app()

    with app.app_context():
        # 删除表
        Download.__table__.drop(db.engine)
        print("✓ 删除 downloads 表")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'downgrade':
        downgrade()
    else:
        upgrade()
```

#### 2.2 使用 Alembic（推荐，复杂项目）

```bash
# 初始化 Alembic
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "add downloads table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### Phase 3: 数据迁移（如需要）（10-15 分钟）

#### 3.1 迁移现有数据

```python
# scripts/migrate_download_paths.py

from app import create_app, db
from app.models import Download
from pathlib import Path

def migrate_paths():
    """迁移文件路径"""
    app = create_app()

    with app.app_context():
        downloads = Download.query.all()

        for download in downloads:
            # 旧路径：data/downloads/file.zip
            # 新路径：/app/data/downloads/file.zip
            old_path = Path(download.filepath)
            if not old_path.is_absolute():
                download.filepath = str(old_path.absolute())

        db.session.commit()
        print(f"✓ 迁移了 {len(downloads)} 条记录")
```

### Phase 4: 测试（15-20 分钟）

#### 4.1 单元测试

```python
# tests/test_models/test_download.py

import pytest
from app.models import Download
from app import create_app, db

def test_create_download(app):
    """测试创建下载记录"""
    with app.app_context():
        download = Download(
            run_id=123,
            filename='artifact.zip',
            filepath='/app/data/downloads/artifact.zip'
        )

        db.session.add(download)
        db.session.commit()

        assert download.id is not None
        assert download.filename == 'artifact.zip'

def test_download_query(app):
    """测试查询下载记录"""
    with app.app_context():
        downloads = Download.query.filter_by(run_id=123).all()
        assert len(downloads) > 0
```

#### 4.2 集成测试

```python
# tests/test_integration/test_database.py

def test_database_migration():
    """测试数据库迁移"""
    app = create_app({'DATABASE': ':memory:'})

    with app.app_context():
        db.create_all()

        # 验证表存在
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        assert 'downloads' in tables
```

### Phase 5: 验证（5-10 分钟）

#### 5.1 开发环境验证

```bash
# 运行迁移
python scripts/migrate_add_downloads_table.py

# 验证表结构
sqlite3 data/app.db ".schema downloads"

# 验证数据
sqlite3 data/app.db "SELECT * FROM downloads LIMIT 5;"
```

#### 5.2 回滚测试

```bash
# 测试回滚
python scripts/migrate_add_downloads_table.py downgrade

# 验证表已删除
sqlite3 data/app.db ".tables"
```

## 最佳实践

### 1. 使用事务

```python
def migrate_with_transaction():
    """使用事务确保一致性"""
    app = create_app()

    with app.app_context():
        try:
            # 开始事务
            db.session.begin()

            # 执行迁移
            # ...

            # 提交
            db.session.commit()
            print("✓ 迁移成功")

        except Exception as e:
            # 回滚
            db.session.rollback()
            print(f"✗ 迁移失败: {e}")
            raise
```

### 2. 备份数据库

```bash
# SQLite 备份
cp data/app.db data/app.db.backup

# 恢复
cp data/app.db.backup data/app.db
```

### 3. 渐进式迁移

```python
def migrate_gradually():
    """渐进式迁移，避免长时间锁表"""
    app = create_app()

    with app.app_context():
        # 分批处理
        batch_size = 1000
        offset = 0

        while True:
            records = Download.query.limit(batch_size).offset(offset).all()

            if not records:
                break

            for record in records:
                # 处理记录
                pass

            db.session.commit()
            offset += batch_size
            print(f"已处理 {offset} 条记录")
```

## 完成检查清单

### 设计阶段
- [ ] 变更需求明确
- [ ] 模型定义正确
- [ ] 关系设计合理

### 迁移脚本
- [ ] 升级脚本完成
- [ ] 回滚脚本完成
- [ ] 脚本已测试

### 数据迁移
- [ ] 迁移脚本完成
- [ ] 数据备份完成
- [ ] 迁移已验证

### 测试验证
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 开发环境验证
- [ ] 回滚测试通过

### 文档更新
- [ ] 模型文档已更新
- [ ] 迁移说明已更新
- [ ] 相关代码已更新

## 常见问题

### Q1: 迁移失败如何回滚？

**A**: 使用回滚脚本或数据库备份：

```bash
# 使用回滚脚本
python scripts/migrate_xxx.py downgrade

# 恢复备份
cp data/app.db.backup data/app.db
```

### Q2: 如何处理大数据量迁移？

**A**:
- 分批处理
- 使用事务
- 在低峰期执行
- 准备回滚方案

### Q3: 如何验证迁移成功？

**A**:
- 检查表结构
- 验证数据完整性
- 运行测试套件
- 监控应用日志

## 相关工作流

- [服务层开发工作流](./service-development-workflow.md) - 数据库操作
- [Bug 修复工作流](./bug-fix-workflow.md) - 修复数据问题

---

**最后更新**：2026-03-12
