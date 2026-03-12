#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 GitHub Actions 产物下载功能
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time

BASE_URL = "http://localhost:5000"


def test_api_endpoints():
    """测试 API 端点是否可访问"""
    print("=" * 60)
    print("测试 GitHub Actions 产物下载功能")
    print("=" * 60)

    # 1. 测试主页
    print("\n1. 测试主页访问...")
    try:
        response = requests.get(f"{BASE_URL}/workflows", timeout=5)
        if response.status_code == 200:
            print("   ✓ 主页访问成功")
        else:
            print(f"   ✗ 主页访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 主页访问异常: {e}")
        return False

    # 2. 测试下载 API 端点（应该返回缺少必填字段的错误）
    print("\n2. 测试下载 API 端点...")
    try:
        response = requests.post(
            f"{BASE_URL}/workflows/api/artifacts/download",
            json={},
            timeout=5
        )
        if response.status_code == 400:
            print("   ✓ 下载 API 端点正常（返回缺少必填字段错误）")
        else:
            print(f"   ? 下载 API 返回: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 下载 API 异常: {e}")
        return False

    # 3. 测试配置页面
    print("\n3. 测试配置页面访问...")
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=5)
        if response.status_code == 200:
            print("   ✓ 配置页面访问成功")
            # 检查页面内容是否包含浏览按钮
            if 'selectDownloadDir' in response.text:
                print("   ✓ 配置页面包含目录选择器")
            else:
                print("   ✗ 配置页面缺少目录选择器")
        else:
            print(f"   ✗ 配置页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 配置页面访问异常: {e}")

    # 4. 测试工作流执行记录页面
    print("\n4. 测试工作流执行记录页面...")
    try:
        response = requests.get(
            f"{BASE_URL}/workflows/runs",
            params={'repo': 'test/repo', 'workflow_id': '1'},
            timeout=5
        )
        if response.status_code == 200:
            print("   ✓ 工作流执行记录页面访问成功")
            # 检查页面内容是否包含下载相关代码
            if 'downloadArtifact' in response.text:
                print("   ✓ 页面包含下载函数")
            else:
                print("   ✗ 页面缺少下载函数")
        else:
            print(f"   ✗ 工作流执行记录页面访问失败: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 工作流执行记录页面访问异常: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

    return True


def test_service_methods():
    """测试 WorkflowService 的下载方法"""
    print("\n" + "=" * 60)
    print("测试 WorkflowService.download_artifact() 方法")
    print("=" * 60)

    try:
        from app.services.workflow_service import WorkflowService
        print("\n✓ WorkflowService 导入成功")

        # 检查 download_artifact 方法是否存在
        if hasattr(WorkflowService, 'download_artifact'):
            print("✓ download_artifact() 方法存在")
        else:
            print("✗ download_artifact() 方法不存在")
            return False

        # 检查辅助方法
        if hasattr(WorkflowService, '_check_disk_space'):
            print("✓ _check_disk_space() 方法存在")
        else:
            print("✗ _check_disk_space() 方法不存在")

        if hasattr(WorkflowService, '_extract_zip'):
            print("✓ _extract_zip() 方法存在")
        else:
            print("✗ _extract_zip() 方法不存在")

    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

    print("\n" + "=" * 60)
    return True


def test_imports():
    """测试必要的导入是否成功"""
    print("\n" + "=" * 60)
    print("测试必要的 Python 导入")
    print("=" * 60)

    imports = {
        'zipfile': 'ZIP 文件处理',
        'shutil': '磁盘空间检查',
        'requests': 'HTTP 下载',
        'tempfile': '临时文件管理',
        'pathlib.Path': '路径处理'
    }

    all_ok = True
    for module, description in imports.items():
        try:
            if '.' in module:
                # 处理 'pathlib.Path' 这样的导入
                parts = module.split('.')
                exec(f"from {parts[0]} import {parts[1]}")
            else:
                exec(f"import {module}")
            print(f"✓ {module} ({description})")
        except Exception as e:
            print(f"✗ {module} ({description}): {e}")
            all_ok = False

    print("\n" + "=" * 60)
    return all_ok


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("GitHub Actions 产物下载功能 - 自动化测试")
    print("=" * 60)

    # 测试导入
    if not test_imports():
        print("\n✗ 导入测试失败")
        return False

    # 测试服务方法
    if not test_service_methods():
        print("\n✗ 服务方法测试失败")
        return False

    # 测试 API 端点
    if not test_api_endpoints():
        print("\n✗ API 端点测试失败")
        return False

    print("\n" + "=" * 60)
    print("✓ 所有基础测试通过！")
    print("=" * 60)

    print("\n提示：")
    print("1. 请确保已配置 GitHub Token")
    print("2. 请确保已配置有效的仓库路径")
    print("3. 使用浏览器访问 http://localhost:5000/workflows 进行完整测试")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
