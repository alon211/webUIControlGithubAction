#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试：验证文件上传是否会产生base64编码问题
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import time

BASE_URL = "http://localhost:5000"
TEST_REPO = "alon211/expense-reimbursement-email-automation"
TEST_FILE = "test_upload.json"

def test_upload_and_verify():
    """上传文件并验证内容"""
    print("\n" + "="*60)
    print("文件编辑器Base64编码测试")
    print("="*60)

    # 1. 准备测试内容
    test_content = {
        "test": "value",
        "number": 123,
        "chinese": "中文测试",
        "enabled": True
    }
    content_str = json.dumps(test_content, ensure_ascii=False, indent=2)

    print(f"\n原始内容:\n{content_str}\n")

    # 2. 先通过GitHub API创建文件
    print("步骤1: 创建测试文件...")
    github_token = requests.get(f"{BASE_URL}/config/api").json().get('github_token')
    if not github_token:
        print("✗ GitHub Token未配置")
        return False

    import base64
    content_bytes = content_str.encode('utf-8')
    b64_content = base64.b64encode(content_bytes).decode('utf-8')

    # 使用GitHub API创建文件
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 先尝试获取文件看是否存在
    get_url = f"https://api.github.com/repos/{TEST_REPO}/contents/{TEST_FILE}"
    response = requests.get(get_url, headers=headers)

    file_sha = None
    if response.status_code == 200:
        file_data = response.json()
        file_sha = file_data.get('sha')
        print(f"文件已存在，SHA: {file_sha}")
    elif response.status_code == 404:
        print("文件不存在，将创建新文件")
    else:
        print(f"✗ 获取文件失败: {response.status_code}")
        return False

    # 创建或更新文件
    put_data = {
        "message": "Test file upload",
        "content": b64_content,
        "branch": "main"
    }

    if file_sha:
        put_data["sha"] = file_sha

    response = requests.put(get_url, headers=headers, json=put_data)
    if response.status_code in [200, 201]:
        print("✓ 文件创建成功")
    else:
        print(f"✗ 文件创建失败: {response.status_code}")
        print(response.text)
        return False

    time.sleep(3)

    # 3. 通过文件编辑API更新文件
    print("\n步骤2: 通过文件编辑API更新文件...")
    updated_content = {
        "test": "updated value",
        "number": 456,
        "chinese": "更新后的中文",
        "new_field": "新增字段"
    }
    updated_str = json.dumps(updated_content, ensure_ascii=False, indent=2)

    print(f"更新内容:\n{updated_str}\n")

    response = requests.post(
        f"{BASE_URL}/files/api/update",
        json={
            "repo": TEST_REPO,
            "path": TEST_FILE,
            "content": updated_str,
            "message": "Test update via file editor",
            "branch": "main"
        },
        timeout=30
    )

    print(f"HTTP状态: {response.status_code}")

    if response.status_code != 200:
        print(f"✗ 更新失败: {response.text}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"✗ 更新失败: {data.get('error')}")
        return False

    print("✓ 文件更新成功")
    if data.get('warning'):
        print(f"⚠️  {data['warning']}")

    time.sleep(3)

    # 4. 从GitHub读取并验证
    print("\n步骤3: 从GitHub验证文件内容...")
    response = requests.get(get_url, headers=headers)

    if response.status_code != 200:
        print(f"✗ 读取文件失败: {response.status_code}")
        return False

    file_data = response.json()
    actual_content_b64 = file_data.get('content')
    actual_content = base64.b64decode(actual_content_b64).decode('utf-8')

    print(f"GitHub上的内容:\n{actual_content}\n")

    # 5. 验证
    print("步骤4: 验证内容...")
    try:
        verified_data = json.loads(actual_content)

        # 检查关键字段
        if verified_data.get('test') == 'updated value':
            print("✓ 内容正确:包含 'updated value'")
        else:
            print(f"✗ 内容错误: test字段值为 {verified_data.get('test')}")
            return False

        if verified_data.get('chinese') == '更新后的中文':
            print("✓ 中文正确:包含 '更新后的中文'")
        else:
            print(f"✗ 中文错误: chinese字段值为 {verified_data.get('chinese')}")
            return False

        if verified_data.get('new_field') == '新增字段':
            print("✓ 新增字段正确")
        else:
            print(f"✗ 新增字段错误: new_field字段值为 {verified_data.get('new_field')}")
            return False

        print("\n" + "="*60)
        print("✓ 测试成功: 文件上传功能正常")
        print("="*60)
        return True

    except json.JSONDecodeError as e:
        print(f"✗ 内容不是有效的JSON: {e}")
        print(f"\n实际内容:\n{actual_content[:200]}")

        # 检查是否是双重base64编码
        try:
            double_decoded = base64.b64decode(actual_content).decode('utf-8')
            print(f"\n双重解码后的内容:\n{double_decoded[:200]}")
            print("\n⚠️  警告: 文件被双重base64编码了!")
        except:
            pass

        return False

if __name__ == "__main__":
    try:
        success = test_upload_and_verify()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
