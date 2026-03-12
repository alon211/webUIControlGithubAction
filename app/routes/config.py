"""
配置管理路由
"""
import logging
import threading
import tkinter as tk
from tkinter import filedialog
from flask import Blueprint, render_template, request, jsonify
from app.services.config_service import ConfigService

logger = logging.getLogger(__name__)

# 创建蓝图
config_bp = Blueprint('config', __name__, url_prefix='/config')


@config_bp.route('/')
def index():
    """配置管理页面"""
    configs = ConfigService.get_all_details()
    return render_template('config.html', configs=configs)


@config_bp.route('/api')
def api_get_all():
    """获取所有配置 API"""
    try:
        configs = ConfigService.get_all()
        return jsonify(configs)
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api', methods=['PUT'])
def api_update_all():
    """批量更新配置 API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400

        # 处理下载目录：自动创建目录（如果存在）
        download_dir = data.get('download_dir', '').strip()
        if download_dir:
            from pathlib import Path
            try:
                dir_path = Path(download_dir)
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"下载目录已创建/验证: {dir_path}")
            except Exception as e:
                logger.warning(f"无法创建下载目录 {dir_path}: {e}")
                # 不阻止保存配置，只记录警告

        success = ConfigService.set_many(data)
        if success:
            return jsonify({'success': True, 'message': '配置保存成功'})
        else:
            return jsonify({'error': '配置保存失败'}), 500

    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/<key>', methods=['GET'])
def api_get_one(key):
    """获取单个配置 API"""
    try:
        value = ConfigService.get(key)
        if value is None:
            return jsonify({'error': '配置不存在'}), 404
        return jsonify({'key': key, 'value': value})
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/<key>', methods=['PUT'])
def api_update_one(key):
    """更新单个配置 API"""
    try:
        data = request.get_json()
        value = data.get('value')
        description = data.get('description')

        if value is None:
            return jsonify({'error': '缺少 value 参数'}), 400

        success = ConfigService.set(key, value, description)
        if success:
            return jsonify({'success': True, 'message': '配置保存成功'})
        else:
            return jsonify({'error': '配置保存失败'}), 500

    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/<key>', methods=['DELETE'])
def api_delete_one(key):
    """删除配置 API"""
    try:
        success = ConfigService.delete(key)
        if success:
            return jsonify({'success': True, 'message': '配置删除成功'})
        else:
            return jsonify({'error': '配置不存在'}), 404

    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/test_token', methods=['POST'])
def api_test_token():
    """测试 GitHub Token 有效性"""
    try:
        from app.services.github_service import GitHubService

        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': '缺少 token 参数'}), 400

        # 直接测试 Token 连接
        result = GitHubService.test_token(token)
        return jsonify(result)

    except Exception as e:
        logger.error(f"测试 Token 失败: {e}")
        return jsonify({'error': str(e)}), 500


@config_bp.route('/api/select_folder', methods=['POST'])
def api_select_folder():
    """弹出系统原生文件夹选择对话框（Python tkinter）

    Returns:
        {
            "success": true,
            "path": "D:/Downloads/Artifacts"  # 完整路径
        }
    """
    try:
        data = request.get_json() or {}
        current_path = data.get('current_path', '.')

        # 在独立线程中运行 GUI（避免阻塞 Flask 主线程）
        result = {'path': None, 'error': None}

        def show_dialog():
            try:
                root = tk.Tk()
                root.withdraw()  # 隐藏主窗口，只显示对话框

                # 弹出文件夹选择对话框
                folder_path = filedialog.askdirectory(
                    title="选择下载目录",
                    initialdir=current_path
                )

                root.destroy()

                if folder_path:  # 用户选择了路径（未取消）
                    result['path'] = folder_path

            except Exception as e:
                result['error'] = str(e)

        # 在独立线程中运行
        thread = threading.Thread(target=show_dialog)
        thread.start()
        thread.join(timeout=30)  # 最多等待30秒

        if result.get('path'):
            logger.info(f"用户选择了文件夹: {result['path']}")
            return jsonify({
                'success': True,
                'path': result['path']
            })
        elif result.get('error'):
            logger.error(f"文件夹选择失败: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error']
            })
        else:
            # 用户取消选择
            return jsonify({
                'success': False,
                'error': '未选择文件夹或操作超时'
            })

    except Exception as e:
        logger.error(f"选择文件夹 API 异常: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
