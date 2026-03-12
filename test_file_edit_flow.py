#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试：读取 -> 编辑 -> 保存 -> 验证
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import base64

BASE_URL = "http://localhost:5000"
REPO = "alon211/expense-reimbursement-email-automation"
FILE = "rules/parse_rules.json"  # 实际存在的文件
BRANCH = "master"  # 默认分支是 master

def test_complete_flow():
    """测试完整的文件编辑流程"""

    print("\n" + "="*60)
    print("文件编辑器完整流程测试")
    print("="*60)

    # 1. 读取文件
    print("\n步骤1: 读取文件")
    print("-"*60)

    response = requests.post(
        f"{BASE_URL}/files/api/get",
        json={"repo": REPO, "path": FILE, "branch": BRANCH},
        timeout=30
    )

    if response.status_code != 200:
        print(f"✗ 读取失败: HTTP {response.status_code}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"✗ 读取失败: {data.get('error')}")
        return False

    original_content = data['content']
    print(f"✓ 文件读取成功")
    print(f"内容长度: {len(original_content)} 字符")
    print(f"内容预览:\n{original_content[:300]}...")

    # 检查内容是否正常
    try:
        json_data = json.loads(original_content)
        print(f"✓ 内容是有效的JSON")
        print(f"  包含 {len(json_data.get('rules', []))} 个规则")
    except json.JSONDecodeError as e:
        print(f"✗ 内容不是有效的JSON: {e}")
        print(f"\n完整内容:\n{original_content}")
        return False

    # 2. 编辑文件（修改一个字段）
    print("\n步骤2: 编辑文件")
    print("-"*60)

    # 修改第一个规则的状态
    if 'rules' in json_data and len(json_data['rules']) > 0:
        original_enabled = json_data['rules'][0].get('enabled')
        json_data['rules'][0]['enabled'] = not original_enabled
        print(f"修改: rules[0].enabled 从 {original_enabled} 改为 {json_data['rules'][0]['enabled']}")

    # 添加测试时间戳
    json_data['test_timestamp'] = "2026-03-13-test"

    edited_content = json.dumps(json_data, ensure_ascii=False, indent=2)
    print(f"✓ 文件编辑完成")
    print(f"新内容长度: {len(edited_content)} 字符")

    # 3. 保存文件
    print("\n步骤3: 保存文件")
    print("-"*60)

    response = requests.post(
        f"{BASE_URL}/files/api/update",
        json={
            "repo": REPO,
            "path": FILE,
            "content": edited_content,
            "message": "Test update via API",
            "branch": BRANCH
        },
        timeout=30
    )

    if response.status_code != 200:
        print(f"✗ 保存失败: HTTP {response.status_code}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"✗ 保存失败: {data.get('error')}")
        return False

    print(f"✓ 文件保存成功")
    if data.get('warning'):
        print(f"⚠️  警告: {data['warning']}")

    # 4. 等待并重新读取验证
    print("\n等待3秒让GitHub更新...")
    import time
    time.sleep(3)

    print("\n步骤4: 验证保存的内容")
    print("-"*60)

    # 方法1: 通过Web UI API读取
    response = requests.post(
        f"{BASE_URL}/files/api/get",
        json={"repo": REPO, "path": FILE, "branch": BRANCH},
        timeout=30
    )

    if response.status_code != 200:
        print(f"✗ 验证读取失败: HTTP {response.status_code}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"✗ 验证读取失败: {data.get('error')}")
        return False

    verified_content = data['content']
    print(f"✓ 文件重新读取成功")
    print(f"内容长度: {len(verified_content)} 字符")
    print(f"内容预览:\n{verified_content[:300]}...")

    # 5. 验证内容正确性
    print("\n步骤5: 验证内容正确性")
    print("-"*60)

    try:
        verified_json = json.loads(verified_content)
        print(f"✓ 内容是有效的JSON")

        # 检查修改是否生效
        if 'test_timestamp' in verified_json:
            if verified_json['test_timestamp'] == "2026-03-13-test":
                print(f"✓ 测试时间戳正确")
            else:
                print(f"✗ 测试时间戳错误: {verified_json['test_timestamp']}")
                return False
        else:
            print(f"✗ 未找到测试时间戳")
            return False

        # 检查规则修改
        if 'rules' in verified_json and len(verified_json['rules']) > 0:
            enabled = verified_json['rules'][0].get('enabled')
            print(f"✓ rules[0].enabled = {enabled}")

    except json.JSONDecodeError as e:
        print(f"✗ 内容不是有效的JSON: {e}")
        print(f"\n完整内容:\n{verified_content}")

        # 检查是否是base64
        import re
        base64_pattern = r'^[A-Za-z0-9+/]+=*$'
        if re.match(base64_pattern, verified_content.strip()):
            print(f"\n⚠️  警告: 内容看起来像是base64编码！")
            try:
                decoded = base64.b64decode(verified_content).decode('utf-8')
                print(f"解码后的内容:\n{decoded[:300]}...")
            except:
                pass

        return False

    # 6. 恢复原始状态
    print("\n步骤6: 恢复原始状态")
    print("-"*60)

    # 删除测试时间戳
    if 'test_timestamp' in json_data:
        del json_data['test_timestamp']
    # 恢复enabled状态
    if 'rules' in json_data and len(json_data['rules']) > 0:
        json_data['rules'][0]['enabled'] = original_enabled

    restored_content = json.dumps(json_data, ensure_ascii=False, indent=2)

    response = requests.post(
        f"{BASE_URL}/files/api/update",
        json={
            "repo": REPO,
            "path": FILE,
            "content": restored_content,
            "message": "Restore original state",
            "branch": BRANCH
        },
        timeout=30
    )

    if response.status_code == 200 and response.json().get('success'):
        print(f"✓ 已恢复原始状态")
    else:
        print(f"⚠️  恢复失败，请手动检查文件")

    # 测试结果
    print("\n" + "="*60)
    print("✓ 测试成功！文件编辑功能正常")
    print("="*60)
    print("\n验证结果:")
    print("  ✓ 文件读取正常")
    print("  ✓ 内容编辑正常")
    print("  ✓ 文件保存正常")
    print("  ✓ 内容验证通过")
    print("  ✓ 无base64编码问题")

    return True

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
