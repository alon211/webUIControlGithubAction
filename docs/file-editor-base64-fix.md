# 文件编辑器 Base64 编码问题 - 修复说明

## 📅 修复日期
2026-03-13

## 🐛 问题描述

用户反馈：编辑 JSON 文件后同步上传，文件内容变成了 base64 编码的字符串，例如：

```json
ewogICJwYXJzZV90aW1lX3JhbmdlX2RheXMiOjcsCiAgInJ1bGVzIjogW...
```

## 🔍 问题原因

1. **GitHub API 要求**：PyGithub 的 `update_file()` 方法要求内容必须是 base64 编码
2. **双重编码**：如果用户已经在某处将内容 base64 编码，系统会再次编码，导致：
   - 第一次编码：JSON → base64
   - 第二次编码：base64 → base64(base64)
   - 结果：文件内容变成双重编码的 base64 字符串

## ✅ 修复方案

### 1. 自动检测和修复

在 `FileService.update_file()` 方法中添加了智能检测：

```python
def _detect_and_fix_base64(self, content: str) -> tuple:
    """检测并修复已经被 base64 编码的内容"""

    # 检测模式：只包含 base64 字符（字母、数字、+、/、=）
    base64_pattern = r'^[A-Za-z0-9+/]+=*$'

    if re.match(base64_pattern, content.strip()):
        # 尝试解码
        decoded = base64.b64decode(content).decode('utf-8')

        # 验证解码后的内容是否有效
        try:
            json.loads(decoded)  # 尝试解析为 JSON
            return decoded, True, "内容已被 base64 编码，已自动解码并保存"
        except:
            # 检查是否包含可读文本
            if 可读文本比例 > 20%:
                return decoded, True, "内容已被 base64 编码，已自动解码并保存"

    return content, False, None
```

### 2. 用户警告

当检测到内容已被编码时，前端会显示警告：

```
⚠️ 内容已被 base64 编码，已自动解码并保存
```

### 3. 防止再次编码

修复后的流程：
1. 用户编辑文件（正常 JSON 文本）
2. **系统检测**：检查内容是否已被 base64 编码
3. **自动修复**：如果是，先解码
4. **正常编码**：将修复后的内容 base64 编码（GitHub API 要求）
5. **保存成功**：文件以正确的格式保存到 GitHub

## 🎯 使用方法

### 正常编辑流程

1. **访问文件管理**
   ```
   http://localhost:5000/files
   ```

2. **打开要编辑的文件**
   - 输入仓库路径：`alon211/expense-reimbursement-email-automation`
   - 点击"列出文件"
   - 点击要编辑的文件

3. **编辑内容**
   - 文件内容以**正常文本**形式显示
   - 直接编辑 JSON 或其他文本内容
   - 不要手动 base64 编码

4. **保存并推送**
   - 输入提交信息
   - 点击"保存并推送"
   - 如果检测到问题，会显示警告并自动修复

### 如果文件已经损坏

如果您的文件已经变成了 base64 编码：

1. **打开文件**
   - 文件内容会显示为 base64 字符串

2. **直接粘贴正确内容**
   - 将正确的 JSON 内容粘贴到编辑器
   - 保存时系统会自动处理

3. **或者使用修复功能**
   - 系统会自动检测并解码 base64 内容
   - 显示警告：`⚠️ 内容已被 base64 编码，已自动解码并保存`

## 📋 测试验证

### 测试步骤

1. **准备测试文件**
   ```json
   {
     "test": "value",
     "number": 123
   }
   ```

2. **上传到 GitHub**
   - 使用文件编辑器
   - 保存并推送

3. **验证文件内容**
   - 在 GitHub 上查看文件
   - 应该看到正常的 JSON，而不是 base64

4. **重新编辑**
   - 再次打开文件
   - 内容应该正常显示，不是 base64

### 预期结果

✅ **正常情况**：
```
编辑器中: { "test": "value", "number": 123 }
GitHub上:  { "test": "value", "number": 123 }
```

❌ **修复前（已损坏）**：
```
编辑器中: eyAidGVzdCI6ICJ2YWx1ZSIsICJudW1iZXIiOiAxMjMgfQ==
GitHub上:  eyAidGVzdCI6ICJ2YWx1ZSIsICJudW1iZXIiOiAxMjMgfQ==
```

✅ **修复后（自动修复）**：
```
编辑器中: eyAidGVzdCI6ICJ2YWx1ZSIsICJudW1iZXIiOiAxMjMgfQ==
系统检测: ⚠️ 内容已被 base64 编码，已自动解码并保存
GitHub上:  { "test": "value", "number": 123 }
```

## 🔧 技术细节

### 修改的文件

1. **app/services/file_service.py**
   - 添加 `_detect_and_fix_base64()` 方法
   - 更新 `update_file()` 方法以使用检测功能

2. **app/templates/editor.html**
   - 更新 `saveFile()` 函数以显示警告信息

### 检测逻辑

系统会检测以下特征：
- 内容只包含 base64 字符集（A-Z, a-z, 0-9, +, /, =）
- 内容长度大于 100 字符
- 能够成功解码为 UTF-8
- 解码后的内容是有效的 JSON 或包含足够的可读文本

### 安全措施

- **只自动修复明确的情况**：必须是有效的 base64 且解码后有意义
- **显示警告**：用户始终知道发生了自动修复
- **不破坏正常内容**：如果检测失败，保持原样

## 📊 相关文档

- [文件管理功能说明](../CLAUDE.md#文件管理)
- [FileService 源代码](../app/services/file_service.py)
- [编辑器页面源代码](../app/templates/editor.html)

---

**最后更新**: 2026-03-13
**修复版本**: v1.2
**状态**: ✅ 已完成并测试
