#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件编辑器 base64 编码问题
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import base64

BASE_URL = "http://localhost:5000"
TEST_REPO = "alon211/expense-reimbursement-email-automation"
TEST_FILE = "test_config.json"

def test_step_1_create_test_file():
    """步骤1: 创建测试JSON文件"""
    print("\n" + "="*60)
    print("步骤 1: 创建测试JSON文件")
    print("="*60)

    test_content = {
        "parse_time_range_days": 7,
        "rules": [
            {
                "rule_id": "rule_001",
                "rule_name": "测试规则",
                "enabled": True,
                "description": "这是一个测试规则",
                "test_chinese": "中文内容测试"
            }
        ]
    }

    json_str = json.dumps(test_content, ensure_ascii=False, indent=2)
    print(f"测试内容:\n{json_str}")
    print(f"\n字符数: {len(json_str)}")

    # 检查是否会被误判为base64
    import re
    base64_pattern = r'^[A-Za-z0-9+/]+=*$'
    is_base64 = re.match(base64_pattern, json_str.strip())
    print(f"\n会被误判为base64吗? {is_base64}")

    return json_str

def test_step_2_upload_via_api(content):
    """步骤2: 通过API上传文件"""
    print("\n" + "="*60)
    print("步骤 2: 通过文件编辑API上传文件")
    print("="*60)

    # 先尝试创建文件（如果不存在）
    print("尝试创建文件...")

    from github import Github
    from app.services.config_service import ConfigService

    token = ConfigService.get('github_token')
    if not token:
        print("✗ GitHub Token未配置")
        return False

    try:
        g = Github(token)
        repo = g.get_repo(TEST_REPO)

        # 尝试获取文件
        try:
            content_file = repo.get_contents(TEST_FILE, ref='main')
            print(f"文件已存在，SHA: {content_file.sha}")
            # 文件存在，使用update API
            print("\n使用更新API...")
        except:
            # 文件不存在，创建新文件
            print("文件不存在，创建新文件...")
            import base64
            content_bytes = content.encode('utf-8')
            b64_content = base64.b64encode(content_bytes).decode('utf-8')

            repo.create_file(
                path=TEST_FILE,
                message="Test create via file editor",
                content=b64_content,
                branch='main'
            )
            print("✓ 文件创建成功")
            return True

    except Exception as e:
        print(f"✗ 创建文件失败: {e}")

    # 使用update API
    response = requests.post(
        f"{BASE_URL}/files/api/update",
        json={
            "repo": TEST_REPO,
            "path": TEST_FILE,
            "content": content,
            "message": "Test upload via file editor",
            "branch": "main"
        },
        timeout=30
    )

    print(f"HTTP状态: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ 文件上传成功")
            if data.get('warning'):
                print(f"⚠️  警告: {data['warning']}")
            return True
        else:
            print(f"✗ 上传失败: {data.get('error')}")
            return False
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        try:
            print(f"错误详情: {response.json()}")
        except:
            pass
        return False

def test_step_3_verify_on_github():
    """步骤3: 从GitHub验证文件内容"""
    print("\n" + "="*60)
    print("步骤 3: 从GitHub验证文件内容")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/files/api/get",
        json={
            "repo": TEST_REPO,
            "path": TEST_FILE,
            "branch": "main"
        },
        timeout=30
    )

    print(f"HTTP状态: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            content = data.get('content')
            print(f"✓ 文件读取成功")
            print(f"\n文件内容:")
            print("-"*60)
            print(content[:500])  # 只显示前500个字符
            if len(content) > 500:
                print(f"... (总长度: {len(content)} 字符)")
            print("-"*60)

            # 尝试解析为JSON
            try:
                json_data = json.loads(content)
                print("\n✓ 内容是有效的JSON")
                print(f"包含 {len(json_data.get('rules', []))} 个规则")
                return json_data
            except json.JSONDecodeError as e:
                print(f"\n✗ 内容不是有效的JSON: {e}")

                # 检查是否是base64编码
                import re
                base64_pattern = r'^[A-Za-z0-9+/]+=*$'
                if re.match(base64_pattern, content.strip()):
                    print("⚠️  内容被base64编码了！")
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        print(f"\n解码后的内容:")
                        print(decoded[:500])
                        return None
                    except:
                        pass

                return None
        else:
            print(f"✗ 读取失败: {data.get('error')}")
            return None
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        return None

def test_step_4_check_encoding_issue(content):
    """步骤4: 检查编码问题"""
    print("\n" + "="*60)
    print("步骤 4: 检查编码问题")
    print("="*60)

    # 检查内容是否看起来像base64
    import re
    base64_pattern = r'^[A-Za-z0-9+/]+=*$'
    looks_like_base64 = re.match(base64_pattern, content.strip())

    print(f"内容看起来像base64吗? {looks_like_base64}")

    # 统计字符类型
    total = len(content)
    ascii_chars = sum(1 for c in content if ord(c) < 128)
    chinese_chars = total - ascii_chars

    print(f"总字符数: {total}")
    print(f"ASCII字符: {ascii_chars} ({ascii_chars/total*100:.1f}%)")
    print(f"中文字符: {chinese_chars} ({chinese_chars/total*100:.1f}%)")

    # 检查是否包含常见的JSON结构
    has_braces = '{' in content and '}' in content
    has_brackets = '[' in content and ']' in content
    has_colon = ':' in content

    print(f"包含JSON结构? 大括号:{has_braces}, 方括号:{has_brackets}, 冒号:{has_colon}")

    if looks_like_base64 and not has_braces:
        print("\n⚠️  警告: 内容看起来像是被base64编码的JSON！")
        return False

    return True

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("文件编辑器 Base64 编码问题 - 完整测试")
    print("="*60)
    print(f"\n测试仓库: {TEST_REPO}")
    print(f"测试文件: {TEST_FILE}")

    # 步骤1: 创建测试内容
    original_content = test_step_1_create_test_file()

    # 步骤2: 上传文件
    if not test_step_2_upload_via_api(original_content):
        print("\n✗ 测试终止: 文件上传失败")
        return False

    # 等待GitHub更新
    import time
    print("\n等待5秒让GitHub更新...")
    time.sleep(5)

    # 步骤3: 验证文件
    json_data = test_step_3_verify_on_github()

    if json_data is None:
        print("\n✗ 测试失败: 文件内容验证失败")
        return False

    # 步骤4: 检查编码问题
    downloaded_content = json.dumps(json_data, ensure_ascii=False, indent=2)
    test_step_4_check_encoding_issue(downloaded_content)

    # 最终验证
    print("\n" + "="*60)
    print("测试结果")
    print("="*60)

    if json_data and 'rules' in json_data:
        print("✓ 测试成功!")
        print(f"  - 文件内容正确")
        print(f"  - 包含 {len(json_data['rules'])} 个规则")
        print(f"  - 支持中文字符")
        return True
    else:
        print("✗ 测试失败: 文件内容不正确")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
