# 快速触发自动下载 - 测试和验证指南

## 🔍 问题排查

如果点击快速触发后没有看到下载的文件，请按以下步骤排查：

## 步骤 1: 检查浏览器控制台

1. 打开浏览器开发者工具（按 F12）
2. 切换到 **Console** 标签
3. 点击快速触发
4. 观察控制台输出

### 预期的输出

**正常情况**应该看到：
```
工作流 邮件提取 已完成，开始下载产物...
下载产物 (1/1): extraction-results-23005915947
产物 "extraction-results-23005915947" 下载成功: data/downloads/extraction-results-23005915947
```

**如果有错误**，会看到类似：
```
快速触发 xxx 获取执行记录失败
快速触发 xxx 获取产物失败
产物 "xxx" 下载失败: [错误信息]
```

## 步骤 2: 检查下载目录

### 默认下载目录

```
c:\dockerVolumn\webUIControlGithubAction\data\downloads\
```

### 检查方法

**Windows**:
```bash
dir data\downloads\
```

**或者直接在文件资源管理器中打开**:
```
c:\dockerVolumn\webUIControlGithubAction\data\downloads\
```

### 应该看到什么

如果下载成功，会看到以产物名称命名的文件夹，例如：
```
data\downloads\extraction-results-23005915947\
```

## 步骤 3: 验证配置

访问配置页面确认：
```
http://localhost:5000/config
```

检查：
- ✅ `github_token` 是否已设置
- ✅ `download_dir` 是否已设置
- ✅ 快速触发是否已正确配置

## 步骤 4: 手动测试下载

如果自动下载不工作，先手动测试下载功能：

1. 访问工作流执行记录页面
   ```
   http://localhost:5000/workflows/runs?repo=alon211/expense-reimbursement-email-automation&workflow_id=244636486
   ```

2. 找到最近一次成功运行的记录
3. 点击「产物」按钮
4. 手动下载一个产物

**如果手动下载也不工作**，说明是基础下载功能的问题。

**如果手动下载可以工作**，说明是自动下载逻辑的问题。

## 常见问题和解决方案

### 问题 1: 控制台没有任何输出

**原因**: JavaScript 代码可能没有加载

**解决**:
1. 硬刷新页面（Ctrl+F5）
2. 清除浏览器缓存

### 问题 2: 控制台显示错误

**检查错误类型**:

**a) "获取执行记录失败"**
- 检查仓库路径是否正确
- 检查 GitHub Token 是否有效

**b) "获取产物失败"**
- 检查工作流是否真的产生了产物
- 等待工作流完全完成（可能需要 2-5 分钟）

**c) "下载失败: 磁盘空间不足"**
- 清理磁盘空间
- 选择其他下载目录

**d) "下载失败: 创建下载目录失败"**
- 检查目录权限
- 手动创建目录

### 问题 3: 工作流显示"上次成功"但没有文件

**原因**:
- 快速触发配置的可能是之前的历史记录
- 不是刚刚触发的运行

**解决**:
1. 在快速触发配置中查看 `last_run_id`
2. 确认这个 ID 对应的是刚刚触发的运行
3. 或者在工作流执行记录页面手动下载

## 调试模式

### 启用详细日志

打开浏览器控制台，所有操作都会输出日志：

```javascript
// 在控制台中执行
localStorage.debug = true;

// 然后重新点击快速触发
```

### 查看网络请求

在开发者工具中：
1. 切换到 **Network** 标签
2. 点击快速触发
3. 查看是否有失败的请求（红色）

### 查看产物列表

在控制台中执行：
```javascript
// 手动获取产物列表
$.ajax({
    url: '/workflows/api/artifacts',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        repo: 'alon211/expense-reimbursement-email-automation',
        run_id: 23005915947  // 替换为最新的 run_id
    }),
    success: function(data) {
        console.log('产物列表:', data);
    }
});
```

## 完整测试流程

1. **配置检查**
   ```
   访问: http://localhost:5000/config
   确认: GitHub Token、下载目录、快速触发配置
   ```

2. **触发工作流**
   ```
   访问: http://localhost:5000
   点击: 快速触发的「运行」按钮
   ```

3. **等待完成**
   ```
   等待状态从 "⟳ 进行中" 变为 "✓ 上次成功"
   通常需要 2-5 分钟
   ```

4. **检查文件**
   ```
   打开: data\downloads\
   应该看到新下载的产物文件夹
   ```

## 如果还是不行

### 手动验证基础功能

运行测试脚本：
```bash
python test_real_download.py
```

如果测试脚本能下载文件，说明后端功能正常，只是前端自动下载逻辑有问题。

### 联系开发者

提供以下信息：
1. 浏览器控制台的完整输出
2. 网络请求的错误信息
3. 快速触发配置截图
4. data\downloads 目录截图

---

**最后更新**: 2026-03-12
**目的**: 帮助用户排查和验证快速触发自动下载功能
