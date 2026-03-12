# Bug 修复工作流

## 适用场景

修复已发现的问题，包括 Bug 复现、定位、修复和验证。

## 前置条件

- [ ] Bug 已被报告
- [ ] 已阅读 [TDD 测试工作流](./tdd-testing-workflow.md)
- [ ] 已激活虚拟环境

## 工作流程

### Phase 1: Bug 复现（5-10 分钟）

#### 1.1 理解 Bug

**问题清单**：
- Bug 的具体表现是什么？
- 触发条件是什么？
- 预期行为是什么？
- 实际行为是什么？

**Bug 报告模板**：
```
**问题描述**：配置保存失败

**复现步骤**：
1. 访问 /config
2. 输入 GitHub Token
3. 点击保存
4. 错误：500 Internal Server Error

**预期**：配置保存成功
**实际**：服务器错误
```

#### 1.2 复现 Bug

```bash
# 启动应用
python run.py

# 使用 chrome-devtools 复现
mcp__chrome-devtools__new_page(url="http://localhost:5000/config")
# ... 执行复现步骤

# 查看日志
tail -f logs/app.log
```

### Phase 2: 问题定位（10-15 分钟）

#### 2.1 查看错误日志

```bash
# 应用日志
tail -100 logs/app.log | grep ERROR

# 控制台错误
mcp__chrome-devtools__list_console_messages(types=["error"])
```

#### 2.2 定位代码位置

```bash
# 搜索相关代码
grep -r "config" app/routes/
grep -r "save" app/services/
```

#### 2.3 分析根因

**常见问题**：
- 变量未定义
- 类型错误
- 数据库连接失败
- API 调用错误

### Phase 3: TDD 修复（15-30 分钟）

**遵循 TDD 原则：先写失败测试，再修复**

#### 3.1 编写失败测试

```python
# tests/test_services/test_config_service.py

def test_config_save_with_special_chars(self):
    """测试配置包含特殊字符时的保存"""
    service = ConfigService()

    # 这个测试应该失败（Bug）
    service.set("test_key", "value with 'quotes' and \"double quotes\"")

    result = service.get("test_key")
    assert result == "value with 'quotes' and \"double quotes\""
```

**运行测试**：
```bash
pytest tests/test_services/test_config_service.py::test_config_save_with_special_chars -v
# ❌ FAILED (Bug 存在)
```

#### 3.2 修复代码

```python
# app/services/config_service.py

def set(self, key: str, value: str):
    """设置配置值"""
    # 修复：使用参数化查询防止 SQL 注入
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO config (key, value)
            VALUES (?, ?)
        """, (key, value))  # 参数化查询
```

**运行测试**：
```bash
pytest tests/test_services/test_config_service.py::test_config_save_with_special_chars -v
# ✅ PASSED (Bug 已修复)
```

#### 3.3 回归测试

确保修复没有引入新问题：

```bash
pytest tests/test_services/test_config_service.py -v
```

### Phase 4: 验证修复（10-15 分钟）

#### 4.1 手动验证

```bash
# 使用 chrome-devtools 验证
mcp__chrome-devtools__new_page(url="http://localhost:5000/config")
# ... 执行修复前的操作

# 截图保存
mcp__chrome-devtools__take_screenshot(
    filePath="screenshots/bug_fix_config_save.png"
)
```

#### 4.2 检查无副作用

- [ ] 其他功能正常
- [ ] 无性能下降
- [ ] 无新的错误日志

### Phase 5: 文档更新（5 分钟）

更新相关文档：
- [ ] CLAUDE.md（如果是设计问题）
- [ ] API 文档（如果是 API 问题）
- [ ] README（如果是使用说明问题）

## 完成检查清单

### Bug 修复
- [ ] Bug 已复现
- [ ] 根因已定位
- [ ] 失败测试已编写
- [ ] 代码已修复
- [ ] 测试已通过

### 质量保证
- [ ] 回归测试通过
- [ ] E2E 测试通过
- [ ] 无副作用
- [ ] 截图已保存

### 文档更新
- [ ] 相关文档已更新
- [ ] Bug 报告已关闭

## 常见问题

### Q1: 无法复现 Bug 怎么办？

**A**: 收集更多信息：
- 详细的环境信息
- 完整的错误日志
- 用户操作步骤
- 浏览器控制台输出

### Q2: 修复引入了新 Bug 怎么办？

**A**:
1. 回滚修复
2. 重新分析根因
3. 编写更全面的测试
4. 再次修复

### Q3: 临时修复 vs 彻底修复？

**A**:
- **临时修复**：快速止损，记录技术债务
- **彻底修复**：解决根本问题，重构代码
- **优先级**：根据影响范围决定

## 相关工作流

- [TDD 测试工作流](./tdd-testing-workflow.md) - 测试驱动修复
- [代码审查工作流](./code-review-workflow.md) - 审查修复代码

---

**最后更新**：2026-03-12
