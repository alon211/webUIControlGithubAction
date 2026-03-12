#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试快速触发自动下载逻辑（模拟前端）
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time
import json

BASE_URL = "http://localhost:5000"
REPO = "alon211/expense-reimbursement-email-automation"

def get_quick_triggers():
    """获取快速触发列表"""
    response = requests.post(f"{BASE_URL}/workflows/api/quick-triggers/list", json={}, timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data.get('triggers', [])
    return []

def trigger_workflow(trigger_id):
    """触发工作流"""
    response = requests.post(
        f"{BASE_URL}/workflows/api/quick-triggers/trigger",
        json={"id": trigger_id},
        timeout=30
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('success'), data
    return False, {}

def monitor_and_download(trigger):
    """
    模拟前端监控逻辑：
    1. 检测状态从 running/in_progress/queued 变为 success
    2. 自动下载产物
    """
    trigger_id = trigger['id']
    trigger_name = trigger['name']

    print(f"\n开始监控: {trigger_name}")
    print("=" * 60)

    previous_status = None

    for i in range(60):  # 最多监控5分钟
        print(f"\n轮询 {i+1}/60...")

        # 获取最新状态
        triggers = get_quick_triggers()
        current_trigger = None
        for t in triggers:
            if t['id'] == trigger_id:
                current_trigger = t
                break

        if not current_trigger:
            print("✗ 找不到触发器")
            return False

        current_status = current_trigger.get('last_status')
        run_id = current_trigger.get('last_run_id')

        print(f"  上次状态: {previous_status}")
        print(f"  当前状态: {current_status}")
        print(f"  运行 ID: {run_id}")

        # 检测状态变化：从运行中变为成功
        if previous_status and previous_status in ['running', 'in_progress', 'queued']:
            if current_status == 'success':
                print(f"\n✓ 工作流已完成！开始下载产物...")
                return download_artifacts(run_id)
            elif current_status == 'failure':
                print(f"\n✗ 工作流失败")
                return False

        previous_status = current_status

        # 如果当前不在运行中，说明工作流还未触发或已完成
        if current_status not in ['running', 'in_progress', 'queued']:
            if i == 0:
                print("\n工作流未在运行，先触发它...")
                success, _ = trigger_workflow(trigger_id)
                if not success:
                    print("✗ 触发失败")
                    return False
                print("✓ 工作流已触发，开始监控...")
                time.sleep(5)

        time.sleep(5)

    print("\n✗ 监控超时（5分钟）")
    return False

def download_artifacts(run_id):
    """
    模拟前端自动下载逻辑
    """
    print(f"\n开始下载产物 (run_id: {run_id})")
    print("=" * 60)

    # 等待几秒确保 GitHub API 更新
    print("等待 5 秒...")
    time.sleep(5)

    # 步骤1: 获取产物列表
    print("\n步骤 1: 获取产物列表")
    response = requests.post(
        f"{BASE_URL}/workflows/api/artifacts",
        json={"repo": REPO, "run_id": run_id},
        timeout=30
    )

    if response.status_code != 200:
        print(f"✗ HTTP 错误: {response.status_code}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"✗ 获取产物失败: {data.get('error')}")
        return False

    artifacts = data.get('artifacts', [])
    print(f"✓ 找到 {len(artifacts)} 个产物")

    if not artifacts:
        print("✗ 没有产物")
        return False

    # 过滤掉过期的产物
    valid_artifacts = [a for a in artifacts if not a['expired']]
    if not valid_artifacts:
        print("✗ 所有产物都已过期")
        return False

    # 步骤2: 下载所有产物
    print(f"\n步骤 2: 下载 {len(valid_artifacts)} 个产物")
    download_dir = json.loads(requests.get(f"{BASE_URL}/config/api").content).get('download_dir', 'data/downloads')
    print(f"下载目录: {download_dir}")

    success_count = 0
    for i, artifact in enumerate(valid_artifacts, 1):
        artifact_name = artifact['name']
        print(f"\n下载 {i}/{len(valid_artifacts)}: {artifact_name}")

        response = requests.post(
            f"{BASE_URL}/workflows/api/artifacts/download",
            json={
                "repo": REPO,
                "run_id": run_id,
                "artifact_name": artifact_name,
                "download_dir": download_dir
            },
            timeout=300
        )

        print(f"  HTTP 状态: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"  ✓ 下载成功！")
                print(f"    路径: {result.get('extracted_path')}")
                print(f"    文件数: {result.get('file_count')}")
                success_count += 1
            else:
                print(f"  ✗ 下载失败: {result.get('error')}")
        else:
            print(f"  ✗ HTTP 错误: {response.status_code}")

    print(f"\n下载完成: {success_count}/{len(valid_artifacts)} 成功")
    return success_count > 0

def main():
    print("\n" + "=" * 60)
    print("快速触发自动下载测试")
    print("=" * 60)

    # 获取快速触发列表
    triggers = get_quick_triggers()
    if not triggers:
        print("✗ 没有快速触发配置")
        return False

    print(f"找到 {len(triggers)} 个快速触发:")
    for i, trigger in enumerate(triggers, 1):
        print(f"{i}. {trigger['name']} (状态: {trigger.get('last_status', 'N/A')})")

    # 选择第一个触发器
    trigger = triggers[0]
    print(f"\n选择: {trigger['name']}")

    # 监控并自动下载
    success = monitor_and_download(trigger)

    if success:
        print("\n" + "=" * 60)
        print("✓ 测试成功！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 测试失败")
        print("=" * 60)

    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
