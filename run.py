#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
应用入口文件
"""
import sys
import io

# 设置标准输出编码为 UTF-8 (Windows 中文显示修复)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import create_app, db, logger

# 创建应用实例
app = create_app()


@app.before_request
def initialize_database():
    """在第一次请求前初始化数据库"""
    if not hasattr(app, '_db_initialized'):
        try:
            with app.app_context():
                db.create_all()
                logger.info('数据库初始化完成')
            app._db_initialized = True
        except Exception as e:
            logger.error(f'数据库初始化失败: {e}')


@app.cli.command()
def init_db():
    """初始化数据库命令"""
    with app.app_context():
        db.create_all()
        logger.info('数据库初始化完成')
        print('✓ 数据库初始化完成')


if __name__ == '__main__':
    # 启动开发服务器
    app.run(host='0.0.0.0', port=5000, debug=True)
