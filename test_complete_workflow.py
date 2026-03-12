#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速触发并自动下载 - 完整流程测试
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time
import json

BASE_URL = "http://localhost:5000"

# 测试配置
REPO = "alon211/expense-reimbursement-email-automation"

def test_step_1_check_config():
    """步骤1: 检查配置"""
    print("\n" + "="*60)
    print("步骤 1: 检查配置")
    print("="*60)

    response = requests.get(f"{BASE_URL}/config/api", timeout=10)
    if response.status_code == 200:
        config = response.json()
        print(f"✓ GitHub Token: {'已设置' if config.get('github_token') else '未设置'}")
        print(f"✓ 下载目录: {config.get('download_dir', '未设置')}")

        if config.get('github_token') and config.get('download_dir'):
            print("\n配置正常，继续测试")
            return config.get('download_dir')
        else:
            print("\n✗ 配置不完整，请先配置:")
            print("1. 访问 http://localhost:5000/config")
            print("2. 设置 GitHub Token")
            print("3. 设置下载目录")
            return None
    else:
        print(f"✗ 无法获取配置: HTTP {response.status_code}")
        return None

def test_step_2_get_quick_triggers():
    """步骤2: 获取快速触发列表"""
    print("\n" + "="*60)
    print("步骤 2: 获取快速触发列表")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/workflows/api/quick-triggers/list",
        json={},
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            triggers = data.get('triggers', [])
            print(f"✓ 找到 {len(triggers)} 个快速触发:")

            for i, trigger in enumerate(triggers, 1):
                print(f"\n{i}. {trigger['name']}")
                print(f"   仓库: {trigger['repo']}")
                print(f"   工作流 ID: {trigger['workflow_id']}")
                print(f"   分支: {trigger['branch']}")
                print(f"   上次状态: {trigger['last_status']}")
                print(f"   上次运行 ID: {trigger.get('last_run_id', 'N/A')}")

            return triggers
        else:
            print(f"✗ 获取失败: {data.get('error')}")
            return None
    else:
        print(f"✗ HTTP 错误: {response.status_code}")
        return None

def test_step_3_trigger_workflow(trigger):
    """步骤3: 触发工作流"""
    print("\n" + "="*60)
    print(f"步骤 3: 触发工作流 '{trigger['name']}'")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/workflows/api/quick-triggers/trigger",
        json={"id": trigger['id']},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✓ 工作流已触发")
            print(f"  分支: {data.get('branch', 'main')}")
            print(f"  消息: {data.get('message')}")
            return True
        else:
            print(f"✗ 触发失败: {data.get('error')}")
            return False
    else:
        print(f"✗ HTTP 错误: {response.status_code}")
        try:
            print(f"  错误: {response.json()}")
        except:
            pass
        return False

def test_step_4_monitor_workflow(trigger):
    """步骤4: 监控工作流状态"""
    print("\n" + "="*60)
    print("步骤 4: 监控工作流状态（最多等待5分钟）")
    print("="*60)

    max_polls = 60  # 60次 * 5秒 = 5分钟
    poll_interval = 5

    previous_status = None
    completed_run_id = None

    for i in range(max_polls):
        print(f"\n轮询 {i+1}/{max_polls} (已等待 {i*poll_interval} 秒)...")

        # 获取快速触发状态
        response = requests.post(
            f"{BASE_URL}/workflows/api/quick-triggers/list",
            json={},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                triggers = data.get('triggers', [])
                current_trigger = None

                for t in triggers:
                    if t['id'] == trigger['id']:
                        current_trigger = t
                        break

                if not current_trigger:
                    print(f"✗ 找不到触发器 {trigger['id']}")
                    return False

                current_status = current_trigger.get('last_status')
                print(f"  当前状态: {current_status}")

                # 检查状态变化
                if previous_status and previous_status in ['running', 'in_progress', 'queued']:
                    if current_status == 'success':
                        print(f"\n✓ 工作流已完成!")
                        completed_run_id = current_trigger.get('last_run_id')
                        break
                    elif current_status == 'failure':
                        print(f"\n✗ 工作流失败")
                        return False

                previous_status = current_status

                # 检查是否还在运行
                if current_status not in ['running', 'in_progress', 'queued']:
                    print(f"\n  工作流未在运行中，状态: {current_status}")
                    break
        else:
            print(f"✗ 获取状态失败: {data.get('error')}")

        time.sleep(poll_interval)

    return completed_run_id is not None

def test_step_5_get_artifacts(run_id):
    """步骤5: 获取产物列表"""
    print("\n" + "="*60)
    print(f"步骤 5: 获取产物列表 (run_id: {run_id})")
    print("="*60)

    time.sleep(3)  # 等待 GitHub API 更新

    response = requests.post(
        f"{BASE_URL}/workflows/api/artifacts",
        json={
            "repo": REPO,
            "run_id": run_id
        },
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            artifacts = data.get('artifacts', [])
            print(f"✓ 找到 {len(artifacts)} 个产物:")

            for i, artifact in enumerate(artifacts, 1):
                print(f"\n{i}. {artifact['name']}")
                print(f"   大小: {artifact['size'] / 1024:.1f} KB")
                print(f"   过期: {'是' if artifact['expired'] else '否'}")
                print(f"   下载URL: {artifact['download_url'][:50]}...")

            return artifacts
        else:
            print(f"✗ 获取失败: {data.get('error')}")
            return None
    else:
        print(f"✗ HTTP 错误: {response.status_code}")
        return None

def test_step_6_download_artifacts(artifacts, run_id, download_dir):
    """步骤6: 下载产物"""
    print("\n" + "="*60)
    print("步骤 6: 下载产物")
    print("="*60)
    print(f"下载目录: {download_dir}")

    valid_artifacts = [a for a in artifacts if not a['expired']]

    if not valid_artifacts:
        print("✗ 没有有效的产物（都已过期）")
        return False

    print(f"\n准备下载 {len(valid_artifacts)} 个产物...")

    success_count = 0
    for i, artifact in enumerate(valid_artifacts, 1):
        print(f"\n下载 {i}/{len(valid_artifacts)}: {artifact['name']}")

        response = requests.post(
            f"{BASE_URL}/workflows/api/artifacts/download",
            json={
                "repo": REPO,
                "run_id": run_id,
                "artifact_name": artifact['name'],
                "download_dir": download_dir
            },
            timeout=300  # 5分钟超时
        )

        print(f"  HTTP 状态: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✓ 下载成功!")
                print(f"    解压路径: {data.get('extracted_path')}")
                print(f"    文件数量: {data.get('file_count')}")
                success_count += 1
            else:
                print(f"  ✗ 下载失败: {data.get('error')}")
        else:
            print(f"  ✗ HTTP 错误: {response.status_code}")
            try:
                error_data = response.json()
                print(f"    错误: {error_data}")
            except:
                pass

    print(f"\n下载完成: {success_count}/{len(valid_artifacts)} 成功")
    return success_count > 0

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("快速触发并自动下载 - 完整流程测试")
    print("="*60)
    print(f"\n测试仓库: {REPO}")
    print("\n这个测试将:")
    print("1. 检查配置")
    print("2. 获取快速触发列表")
    print("3. 触发工作流")
    print("4. 监控工作流状态（最多5分钟）")
    print("5. 获取产物列表")
    print("6. 自动下载所有产物")
    print("\n预计耗时: 3-8 分钟（取决于工作流运行时间）")
    print("\n按回车开始测试...")

    try:
        input()
    except EOFError:
        print("\n自动开始测试...")

    # 步骤1: 检查配置
    download_dir = test_step_1_check_config()
    if not download_dir:
        print("\n✗ 配置不完整，测试终止")
        return False

    # 步骤2: 获取快速触发
    triggers = test_step_2_get_quick_triggers()
    if not triggers:
        print("\n✗ 没有快速触发配置，测试终止")
        return False

    # 选择第一个触发器
    trigger = triggers[0]
    print(f"\n选择触发器: {trigger['name']}")

    # 步骤3: 触发工作流
    if not test_step_3_trigger_workflow(trigger):
        print("\n✗ 触发工作流失败")
        return False

    # 步骤4: 监控工作流
    run_id = test_step_4_monitor_workflow(trigger)
    if not run_id:
        print("\n✗ 工作流监控失败或未成功完成")
        return False

    print(f"\n✓ 工作流完成，run_id: {run_id}")

    # 等待几秒
    print("\n等待 5 秒后获取产物列表...")
    time.sleep(5)

    # 步骤5: 获取产物
    artifacts = test_step_5_get_artifacts(run_id)
    if not artifacts:
        print("\n✗ 没有找到产物")
        return False

    # 步骤6: 下载产物
    if test_step_6_download_artifacts(artifacts, run_id, download_dir):
        print("\n" + "="*60)
        print("✓ 测试成功！")
        print("="*60)
        print(f"\n产物已下载到: {download_dir}")
        print("\n请检查目录确认文件存在")
        return True
    else:
        print("\n" + "="*60)
        print("✗ 测试失败")
        print("="*60)
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
