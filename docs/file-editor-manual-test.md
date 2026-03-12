# 文件编辑器 Base64 问题 - 网页端测试指南

## 📋 测试目的

验证文件编辑器在编辑JSON文件后，保存到GitHub的内容是否正确，是否会变成base64编码。

## 🔧 测试前准备

1. **确认Flask应用运行**
   ```bash
   # 访问 http://localhost:5000
   # 应该看到首页
   ```

2. **确认配置**
   - GitHub Token 已配置
   - 默认仓库已设置

## 🧪 完整测试流程

### 步骤 1: 创建测试文件

**使用 GitHub API 创建测试文件**

在浏览器控制台（F12）中执行：

```javascript
// 设置配置
const repo = "alon211/expense-reimbursement-email-automation";
const filePath = "test_config.json";
const token = "你的GitHub Token";

// 准备测试内容
const testContent = {
    parse_time_range_days: 7,
    rules: [
        {
            rule_id: "rule_001",
            rule_name: "测试规则",
            enabled: true,
            description: "这是一个测试规则",
            test_chinese: "中文内容测试"
        }
    ]
};

// 编码为 base64（GitHub API 要求）
const contentBase64 = btoa(unescape(encodeURIComponent(JSON.stringify(testContent, null, 2))));

// 创建文件
fetch(`https://api.github.com/repos/${repo}/contents/${filePath}`, {
    method: "PUT",
    headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        message: "创建测试文件",
        content: contentBase64,
        branch: "master"  // 注意：可能是 master 而不是 main
    })
})
.then(r => r.json())
.then(data => {
    if (data.content) {
        console.log("✓ 文件创建成功");
        console.log("SHA:", data.content.sha);
    } else {
        console.log("✗ 创建失败:", data);
    }
});
```

### 步骤 2: 在 Web UI 中打开文件

1. **访问文件管理页面**
   ```
   http://localhost:5000/files
   ```

2. **输入仓库路径**
   - 仓库路径：`alon211/expense-reimbursement-email-automation`
   - 点击"列出文件"

3. **找到并打开测试文件**
   - 在文件列表中找到 `test_config.json`
   - 点击文件名打开编辑器

### 步骤 3: 检查文件内容

在编辑器中，您应该看到：

```json
{
  "parse_time_range_days": 7,
  "rules": [
    {
      "rule_id": "rule_001",
      "rule_name": "测试规则",
      "enabled": true,
      "description": "这是一个测试规则",
      "test_chinese": "中文内容测试"
    }
  ]
}
```

✅ **正确**：内容是正常的JSON格式
❌ **错误**：内容是base64编码（如 `ewogICJwYXJzZ...`）

### 步骤 4: 编辑文件

修改一些内容，例如：

```json
{
  "parse_time_range_days": 14,  // 改为 14
  "rules": [
    {
      "rule_id": "rule_001",
      "rule_name": "测试规则（已修改）",  // 添加文字
      "enabled": true,
      "description": "这是一个测试规则",
      "test_chinese": "中文内容测试"
    }
  ]
}
```

### 步骤 5: 保存文件

1. **输入提交信息**
   - 提交信息：`Test update via Web UI`

2. **点击"保存并推送"**

3. **观察结果**
   - 如果显示警告：`⚠️ 内容已被 base64 编码，已自动解码并保存`
   - 如果显示成功：`文件保存成功！`

### 步骤 6: 验证 GitHub 上的内容

**方法 1: 在浏览器中访问 GitHub**

```
https://github.com/alon211/expense-reimbursement-email-automation/blob/master/test_config.json
```

✅ **正确**：应该看到正常的JSON内容
❌ **错误**：看到base64编码的字符串

**方法 2: 使用控制台验证**

```javascript
const repo = "alon211/expense-reimbursement-email-automation";
const filePath = "test_config.json";
const token = "你的GitHub Token";

fetch(`https://api.github.com/repos/${repo}/contents/${filePath}`, {
    headers: {
        "Authorization": `Bearer ${token}`
    }
})
.then(r => r.json())
.then(data => {
    const content = atob(data.content);
    console.log("文件内容:");
    console.log(content);

    // 尝试解析为JSON
    try {
        const json = JSON.parse(content);
        console.log("✓ 内容是有效的JSON");
        console.log("解析结果:", json);
    } catch (e) {
        console.log("✗ 内容不是有效的JSON");
        console.log("可能需要再次解码...");
        try {
            const doubleDecoded = atob(content);
            console.log("双重解码后:", doubleDecoded);
        } catch (e2) {
            console.log("双重解码也失败");
        }
    }
});
```

### 步骤 7: 重新打开文件验证

1. **刷新 Web UI 页面**（F5）
2. **重新打开 test_config.json**
3. **检查内容是否正确显示**

## 🐛 如果出现问题

### 问题 1: 编辑器显示 base64 内容

**症状**：编辑器中显示的是编码字符串而不是JSON

**原因**：读取文件时解码失败

**解决**：
1. 检查控制台错误（F12 → Console）
2. 查看 `/files/api/get` API 的响应
3. 确认 `file_service.py` 的 `get_file()` 方法正确解码

### 问题 2: 保存后 GitHub 上是 base64

**症状**：保存成功，但GitHub上显示的是编码字符串

**原因**：双重编码

**检查**：
```javascript
// 在控制台检查
console.log("发送的内容长度:", content.length);
console.log("内容预览:", content.substring(0, 100));
```

### 问题 3: 分支名称错误

**症状**：`404 Branch main not found`

**解决**：
- 仓库的默认分支可能是 `master` 而不是 `main`
- 在 GitHub 上检查默认分支名称
- 修改测试脚本中的分支名称

## 📊 预期结果

### ✅ 成功的情况

| 步骤 | 预期结果 |
|------|----------|
| 打开文件 | 看到正常JSON，不是base64 |
| 编辑文件 | 可以正常修改JSON内容 |
| 保存文件 | 显示"文件保存成功" |
| GitHub验证 | 内容是正常JSON，不是base64 |
| 重新打开 | 内容正常显示 |

### ❌ 失败的情况

| 步骤 | 错误现象 |
|------|----------|
| 打开文件 | 看到base64字符串 |
| GitHub验证 | 内容是base64字符串 |
| 控制台错误 | `JSONDecodeError` 或解码错误 |

## 🔍 调试检查清单

在每一步操作后，检查以下内容：

- [ ] 浏览器控制台无错误（F12 → Console）
- [ ] 网络请求返回 200 状态（F12 → Network）
- [ ] 文件内容是可读的JSON格式
- [ ] 中文内容正常显示
- [ ] GitHub 上的内容与编辑器中一致

## 📝 测试记录

完成测试后，记录以下信息：

```
测试日期: ___________
测试人员: ___________
测试仓库: alon211/expense-reimbursement-email-automation
测试文件: test_config.json

步骤1 - 创建文件: ✅ / ❌
步骤2 - 打开文件: ✅ / ❌
步骤3 - 内容检查: ✅ / ❌
步骤4 - 编辑文件: ✅ / ❌
步骤5 - 保存文件: ✅ / ❌
步骤6 - GitHub验证: ✅ / ❌
步骤7 - 重新打开: ✅ / ❌

总体结果: ✅ 通过 / ❌ 失败

问题描述（如果失败）:
_________________________________________________
_________________________________________________
_________________________________________________
```

---

**最后更新**: 2026-03-13
**版本**: v1.0
