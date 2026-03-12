#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试工作流触发并自动下载功能
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time

BASE_URL = "http://localhost:5000"


def test_workflow_trigger_and_download():
    """测试工作流触发和自动下载功能"""
    print("=" * 60)
    print("测试工作流触发并自动下载功能")
    print("=" * 60)

    # 注意：这里需要配置有效的测试仓库和工作流
    test_repo = "owner/repo"  # 替换为你的测试仓库
    test_workflow_id = 1      # 替换为你的测试工作流 ID

    print(f"\n测试仓库: {test_repo}")
    print(f"测试工作流 ID: {test_workflow_id}")
    print("\n注意：请确保已在配置页面设置有效的 GitHub Token 和仓库")
    print("访问: http://localhost:5000/config")
    print()

    # 1. 测试工作流列表 API
    print("\n1. 测试获取工作流列表...")
    try:
        response = requests.post(
            f"{BASE_URL}/workflows/api/list",
            json={"repo": test_repo},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                workflows = data.get('workflows', [])
                print(f"   ✓ 获取到 {len(workflows)} 个工作流")
                if workflows:
                    print(f"   示例工作流: {workflows[0]['name']}")
                else:
                    print("   ⚠ 没有找到工作流")
            else:
                print(f"   ✗ 获取失败: {data.get('error')}")
        else:
            print(f"   ✗ HTTP 错误: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求失败: {e}")
        return False

    # 2. 测试获取默认分支
    print("\n2. 测试获取默认分支...")
    try:
        response = requests.post(
            f"{BASE_URL}/workflows/api/default_branch",
            json={"repo": test_repo},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                branch = data.get('branch')
                print(f"   ✓ 默认分支: {branch}")
            else:
                print(f"   ✗ 获取失败: {data.get('error')}")
        else:
            print(f"   ✗ HTTP 错误: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求失败: {e}")

    # 3. 测试配置 API
    print("\n3. 测试获取配置...")
    try:
        response = requests.get(
            f"{BASE_URL}/config/api",
            timeout=10
        )
        if response.status_code == 200:
            config = response.json()
            print(f"   ✓ 配置获取成功")
            if config.get('download_dir'):
                print(f"   下载目录: {config['download_dir']}")
            else:
                print(f"   下载目录: 未设置（将使用默认值）")
        else:
            print(f"   ✗ HTTP 错误: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求失败: {e}")

    # 4. 检查前端函数
    print("\n4. 检查前端函数...")
    try:
        response = requests.get(f"{BASE_URL}/workflows", timeout=10)
        if response.status_code == 200:
            page_content = response.text

            functions = [
                'pollAndDownloadArtifacts',
                'downloadArtifactsFromRun',
                'downloadAllArtifacts'
            ]

            for func in functions:
                if func in page_content:
                    print(f"   ✓ {func}() 函数存在")
                else:
                    print(f"   ✗ {func}() 函数缺失")
        else:
            print(f"   ✗ HTTP 错误: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 请求失败: {e}")

    print("\n" + "=" * 60)
    print("基础测试完成！")
    print("=" * 60)

    print("\n📋 使用指南：")
    print("1. 访问 http://localhost:5000/workflows")
    print("2. 找到你要运行的工作流")
    print("3. 点击「运行并下载」按钮")
    print("4. 系统会自动：")
    print("   - 触发工作流")
    print("   - 等待工作流完成")
    print("   - 自动下载所有产物到配置的目录")
    print("\n提示：默认下载目录可在配置页面设置")

    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("工作流触发并自动下载功能 - 测试脚本")
    print("=" * 60)

    success = test_workflow_trigger_and_download()

    if success:
        print("\n✓ 测试完成")
    else:
        print("\n✗ 测试失败")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
