#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实际测试 GitHub Actions 产物下载功能
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:5000"

# 从配置中获取的值
REPO = "alon211/expense-reimbursement-email-automation"
RUN_ID = 23005915947  # 最近一次成功运行


def test_get_artifacts():
    """测试获取产物列表"""
    print("=" * 60)
    print("步骤 1: 获取产物列表")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/workflows/api/artifacts",
        json={
            "repo": REPO,
            "run_id": RUN_ID
        },
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            artifacts = data.get('artifacts', [])
            print(f"\n✓ 找到 {len(artifacts)} 个产物：\n")

            for i, artifact in enumerate(artifacts, 1):
                print(f"{i}. {artifact['name']}")
                print(f"   大小: {artifact['size'] / 1024:.1f} KB")
                print(f"   过期: {'是' if artifact['expired'] else '否'}")
                print(f"   创建时间: {artifact['created_at']}")
                print()

            return artifacts
        else:
            print(f"✗ 获取失败: {data.get('error')}")
            return None
    else:
        print(f"✗ HTTP 错误: {response.status_code}")
        return None


def test_download_artifact(artifact_name, download_dir):
    """测试下载产物"""
    print("=" * 60)
    print(f"步骤 2: 下载产物 '{artifact_name}'")
    print("=" * 60)

    # 创建下载目录
    download_path = Path(download_dir)
    download_path.mkdir(parents=True, exist_ok=True)

    print(f"\n下载目录: {download_path.absolute()}")
    print(f"目标文件: {download_path / artifact_name}")

    response = requests.post(
        f"{BASE_URL}/workflows/api/artifacts/download",
        json={
            "repo": REPO,
            "run_id": RUN_ID,
            "artifact_name": artifact_name,
            "download_dir": str(download_path.absolute())
        },
        timeout=300  # 5分钟超时
    )

    print(f"\nHTTP 状态码: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"\n✓ 下载成功！")
            print(f"消息: {data.get('message')}")
            print(f"解压路径: {data.get('extracted_path')}")
            print(f"文件数量: {data.get('file_count')}")

            # 验证文件是否真的存在
            extracted_path = Path(data.get('extracted_path'))
            if extracted_path.exists():
                print(f"\n✓ 验证通过：解压目录存在")

                # 列出解压后的文件
                files = list(extracted_path.rglob('*'))
                files = [f for f in files if f.is_file()]

                print(f"\n解压后的文件 ({len(files)} 个)：")
                for f in files[:10]:  # 只显示前10个
                    rel_path = f.relative_to(extracted_path)
                    print(f"  - {rel_path} ({f.stat().st_size / 1024:.1f} KB)")

                if len(files) > 10:
                    print(f"  ... 还有 {len(files) - 10} 个文件")

                return True
            else:
                print(f"\n✗ 验证失败：解压目录不存在")
                return False
        else:
            print(f"\n✗ 下载失败: {data.get('error')}")
            return False
    else:
        print(f"\n✗ HTTP 错误: {response.status_code}")
        try:
            error_data = response.json()
            print(f"错误信息: {error_data.get('error')}")
        except:
            print(f"响应内容: {response.text[:200]}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("GitHub Actions 产物下载 - 真实验证测试")
    print("=" * 60)
    print(f"\n仓库: {REPO}")
    print(f"运行 ID: {RUN_ID}")
    print()

    # 获取产物列表
    artifacts = test_get_artifacts()

    if not artifacts:
        print("\n✗ 没有找到产物，测试终止")
        return False

    # 找到未过期的产物
    valid_artifacts = [a for a in artifacts if not a['expired']]

    if not valid_artifacts:
        print("\n⚠ 所有产物都已过期，无法测试下载")
        return False

    # 下载第一个产物
    first_artifact = valid_artifacts[0]
    artifact_name = first_artifact['name']
    download_dir = "data/downloads"

    success = test_download_artifact(artifact_name, download_dir)

    print("\n" + "=" * 60)
    if success:
        print("✓ 测试成功：文件已成功下载并解压")
    else:
        print("✗ 测试失败：下载过程中出现错误")
    print("=" * 60)

    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
