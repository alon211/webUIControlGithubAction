#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""停止所有 Python 进程并重新启动应用"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess
import time
import os

def kill_all_python_processes():
    """停止所有 Python 进程"""
    try:
        # 使用 taskkill 命令
        result = subprocess.run(
            ['taskkill', '/F', '/IM', 'python.exe'],
            capture_output=True,
            text=True
        )
        print(f"停止 Python 进程: {result.stdout}")
        time.sleep(2)
    except Exception as e:
        print(f"停止进程失败: {e}")

def start_app():
    """启动应用（非 debug 模式）"""
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'

    # 导入应用并运行
    from app import create_app
    app = create_app()

    print("\n" + "=" * 60)
    print("应用已启动（生产模式，单进程）")
    print("监听地址: http://127.0.0.1:5000")
    print("=" * 60)
    print("\n按 Ctrl+C 停止应用\n")

    # 生产模式运行
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n应用已停止")

if __name__ == '__main__':
    kill_all_python_processes()
    start_app()
