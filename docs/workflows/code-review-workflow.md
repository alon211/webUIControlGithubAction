# 代码审查工作流

## 适用场景

- 提交代码前的自我审查
- 审查他人的代码
- Pull Request 审查

## 前置条件

- [ ] 代码已编写完成
- [ ] 测试已通过
- [ ] 已激活虚拟环境

## 工作流程

### Phase 1: 自动化检查（5 分钟）

#### 1.1 运行测试

```bash
# 所有测试通过
pytest tests/ -v

# 覆盖率检查
pytest --cov=app --cov-report=term
# 要求：≥ 80%
```

#### 1.2 类型检查

```bash
# 安装 mypy
pip install mypy

# 运行类型检查
mypy app/ --ignore-missing-imports
```

#### 1.3 代码格式化

```bash
# 安装工具
pip install black isort flake8 bandit

# 格式化代码
black app/
isort app/

# Linting
flake8 app/ --max-line-length=88

# 安全扫描
bandit -r app/
```

### Phase 2: 代码审查（10-15 分钟）

#### 2.1 功能审查

**检查清单**：
- [ ] 代码实现了需求
- [ ] 边界条件已处理
- [ ] 错误处理完善
- [ ] 日志记录适当

#### 2.2 代码质量审查

**检查清单**：
- [ ] 函数职责单一
- [ ] 命名清晰准确
- [ ] 无重复代码
- [ ] 无硬编码常量
- [ ] 类型注解完整

#### 2.3 安全审查

**检查清单**：
- [ ] 无 SQL 注入风险
- [ ] 无 XSS 风险
- [ ] 敏感信息已加密
- [ ] Token/密钥不在代码中
- [ ] 输入验证完善

#### 2.4 性能审查

**检查清单**：
- [ ] 无 N+1 查询
- [ ] 无不必要的循环
- [ ] 数据库查询优化
- [ ] 大文件处理优化

### Phase 3: 文档审查（5 分钟）

**检查清单**：
- [ ] 函数有文档字符串
- [ ] 复杂逻辑有注释
- [ ] API 文档已更新
- [ ] README 已更新（如需要）

### Phase 4: 使用审查（5 分钟）

**检查清单**：
- [ ] E2E 测试通过
- [ ] 截图已保存
- [ ] 用户体验良好
- [ ] 错误提示友好

## 审查工具

### 代码格式化

```bash
# Black - 代码格式化
pip install black
black app/ --line-length 88

# isort - 导入排序
pip install isort
isort app/ --profile black
```

### Linting

```bash
# Flake8 - 代码检查
pip install flake8
flake8 app/ --max-line-length=88 --extend-ignore=E203,W503

# Pylint - 更严格的检查
pip install pylint
pylint app/
```

### 类型检查

```bash
# mypy - 静态类型检查
pip install mypy
mypy app/ --ignore-missing-imports --strict-optional
```

### 安全扫描

```bash
# Bandit - 安全漏洞扫描
pip install bandit
bandit -r app/ -f json -o security_report.json
```

### 复杂度检查

```bash
# radon - 代码复杂度
pip install radon
radon cc app/ -a -nb
# 要求：复杂度 ≤ 10
```

## 常见问题

### Q1: 如何审查他人代码？

**A**: 遵循建设性反馈原则：
- 指出问题，而非批评人
- 提供改进建议
- 解释为什么
- 承认主观意见

### Q2: 审查发现问题怎么办？

**A**:
1. 小问题：直接修复
2. 中等问题：提出修改建议
3. 重大问题：请求修改

### Q3: 如何处理审查意见？

**A**:
- 认真考虑每条意见
- 解释不同意的原因
- 及时修改
- 感谢审查者

## 完成检查清单

### 自动化检查
- [ ] 所有测试通过
- [ ] 覆盖率 ≥ 80%
- [ ] 类型检查通过
- [ ] 代码已格式化
- [ ] Linting 通过
- [ ] 安全扫描通过

### 人工审查
- [ ] 功能正确
- [ ] 代码质量良好
- [ ] 安全无漏洞
- [ ] 性能可接受
- [ ] 文档完整

### 用户体验
- [ ] E2E 测试通过
- [ ] 截图已保存
- [ ] 用户体验良好

## 相关工作流

- [TDD 测试工作流](./tdd-testing-workflow.md) - 测试质量
- [Bug 修复工作流](./bug-fix-workflow.md) - 修复审查

---

**最后更新**：2026-03-12
