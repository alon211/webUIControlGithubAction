#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试文件夹选择 API"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

try:
    # 测试 API 端点
    response = requests.post(
        'http://127.0.0.1:5000/config/api/select_folder',
        headers={'Content-Type': 'application/json'},
        json={'current_path': '.'},
        timeout=35  # 30秒超时 + 5秒缓冲
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✓ 成功！路径: {data.get('path')}")
        else:
            print(f"✗ 失败: {data.get('error')}")
    else:
        print(f"✗ HTTP 错误: {response.status_code}")
        print(f"响应文本: {response.text}")

except requests.exceptions.Timeout:
    print("✗ 请求超时（这可能是因为对话框等待了30秒但用户没有选择）")
except Exception as e:
    print(f"✗ 异常: {e}")
