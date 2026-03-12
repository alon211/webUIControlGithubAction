#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""列出所有 Flask 路由"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app

app = create_app()

print("=" * 80)
print("所有注册的路由：")
print("=" * 80)

for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    if methods:
        print(f"{rule.rule:40s} {methods:20s} {rule.endpoint}")

print("\n" + "=" * 80)
print("查找 select_folder：")
print("=" * 80)

for rule in app.url_map.iter_rules():
    if 'select_folder' in rule.rule:
        print(f"找到路由: {rule.rule}")
        print(f"  方法: {rule.methods}")
        print(f"  端点: {rule.endpoint}")
