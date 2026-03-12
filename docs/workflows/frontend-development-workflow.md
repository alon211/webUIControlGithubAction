# 前端开发工作流

## 适用场景

开发 Web UI 页面，包括：
- Jinja2 模板设计
- Bootstrap 5 组件使用
- jQuery 交互实现
- API 调用集成

## 前置条件

- [ ] 已了解项目前端技术栈
- [ ] 已阅读 [TDD 测试工作流](./tdd-testing-workflow.md)
- [ ] 已激活虚拟环境

## 工作流程

### Phase 1: 页面设计（10 分钟）

#### 1.1 设计布局

使用 Bootstrap 5 组件：

```html
<!-- templates/config.html -->
{% extends "base.html" %}

{% block title %}配置管理{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <div class="card">
                <div class="card-header">
                    <h4>系统配置</h4>
                </div>
                <div class="card-body">
                    <!-- 表单内容 -->
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### 1.2 表单设计

```html
<form id="configForm">
    <div class="mb-3">
        <label for="github_token" class="form-label">GitHub Token</label>
        <input type="password" class="form-control" id="github_token"
               placeholder="ghp_xxxxxxxxxxxx" required>
    </div>

    <div class="mb-3">
        <label for="github_repo" class="form-label">仓库路径</label>
        <input type="text" class="form-control" id="github_repo"
               placeholder="owner/repo" required>
    </div>

    <button type="submit" class="btn btn-primary">保存配置</button>
</form>
```

### Phase 2: 交互实现（15-20 分钟）

#### 2.1 jQuery 集成

```javascript
// static/js/config.js

$(document).ready(function() {
    // 加载现有配置
    loadConfig();

    // 表单提交
    $('#configForm').on('submit', function(e) {
        e.preventDefault();
        saveConfig();
    });
});

function loadConfig() {
    $.get('/api/config')
        .done(function(data) {
            if (data.github_token) {
                $('#github_token').val(data.github_token);
            }
            if (data.github_repo) {
                $('#github_repo').val(data.github_repo);
            }
        })
        .fail(function() {
            showAlert('加载配置失败', 'danger');
        });
}

function saveConfig() {
    const config = {
        github_token: $('#github_token').val(),
        github_repo: $('#github_repo').val()
    };

    $.ajax({
        url: '/api/config',
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(config),
        success: function() {
            showAlert('配置保存成功', 'success');
        },
        error: function() {
            showAlert('配置保存失败', 'danger');
        }
    });
}

function showAlert(message, type) {
    const alert = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    $('.container').prepend(alert);
}
```

#### 2.2 响应式设计

```html
<!-- 移动端适配 -->
<div class="row">
    <div class="col-12 col-md-8 col-lg-6 offset-md-2 offset-lg-3">
        <!-- 内容 -->
    </div>
</div>
```

### Phase 3: API 集成（10 分钟）

#### 3.1 RESTful 调用

```javascript
// GET 请求
function getConfig() {
    return $.get('/api/config');
}

// POST 请求
function createItem(data) {
    return $.ajax({
        url: '/api/items',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data)
    });
}

// PUT 请求
function updateItem(id, data) {
    return $.ajax({
        url: `/api/items/${id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data)
    });
}
```

### Phase 4: E2E 测试（10-15 分钟）

#### 4.1 使用 chrome-devtools MCP

```python
# 启动应用
python run.py &

# 打开页面
mcp__chrome-devtools__new_page(url="http://localhost:5000/config")

# 操作前快照
mcp__chrome-devtools__take_snapshot()

# 填写表单
mcp__chrome-devtools__fill_form([
    {"uid": "github_token", "value": "ghp_test"},
    {"uid": "github_repo", "value": "test/repo"}
])

# 提交
mcp__chrome-devtools__click(uid="submit-button")

# 等待响应
mcp__chrome-devtools__wait_for(text=["保存成功"], timeout=5000)

# 截图
mcp__chrome-devtools__take_screenshot(
    filePath="screenshots/frontend_config.png"
)
```

### Phase 5: 优化（5-10 分钟）

#### 5.1 加载状态

```javascript
function saveConfig() {
    const btn = $('#configForm button[type="submit"]');
    btn.prop('disabled', true).text('保存中...');

    $.ajax({...})
        .always(function() {
            btn.prop('disabled', false).text('保存配置');
        });
}
```

#### 5.2 表单验证

```html
<input type="text" class="form-control" id="github_repo"
       pattern="^[^/]+/[^/]+$" required>
```

```javascript
$('#configForm').on('submit', function(e) {
    const repo = $('#github_repo').val();
    if (!repo.match(/^[^/]+\/[^/]+$/)) {
        showAlert('仓库格式错误，应为 owner/repo', 'warning');
        return false;
    }
});
```

## 最佳实践

### 1. 模板继承

```html
<!-- base.html -->
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    {% block content %}{% endblock %}

    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 2. 错误处理

```javascript
$.ajax({...})
    .fail(function(xhr) {
        let message = '操作失败';
        if (xhr.responseJSON && xhr.responseJSON.error) {
            message = xhr.responseJSON.error;
        }
        showAlert(message, 'danger');
    });
```

### 3. 用户体验

```javascript
// 确认对话框
function deleteItem(id) {
    if (confirm('确定要删除吗？')) {
        $.ajax({...});
    }
}

// 成功后跳转
function onSaved() {
    showAlert('保存成功', 'success');
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}
```

## 完成检查清单

### 功能实现
- [ ] 页面布局正确
- [ ] 表单验证完善
- [ ] API 调用正常
- [ ] 错误处理完善

### 用户体验
- [ ] 响应式设计
- [ ] 加载状态提示
- [ ] 错误提示友好
- [ ] 操作反馈及时

### 测试验证
- [ ] E2E 测试通过
- [ ] 截图已保存
- [ ] 控制台无错误

### 兼容性
- [ ] Chrome 测试通过
- [ ] Firefox 测试通过
- [ ] 移动端测试通过

## 常见问题

### Q1: jQuery 未定义？

**A**: 检查脚本加载顺序：

```html
<script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
```

### Q2: Bootstrap 样式不生效？

**A**: 确认 CDN 链接和浏览器缓存：

```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
```

### Q3: 如何调试前端代码？

**A**: 使用浏览器开发者工具：
- F12 打开控制台
- Console 查看日志
- Network 查看请求
- Elements 查看 DOM

## 相关工作流

- [新功能实现工作流](./feature-implementation.md) - 完整功能开发
- [TDD 测试工作流](./tdd-testing-workflow.md) - E2E 测试

---

**最后更新**：2026-03-12
