"""
文件管理路由
"""
import logging
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.services.file_service import FileService

logger = logging.getLogger(__name__)

# 创建蓝图
files_bp = Blueprint('files', __name__, url_prefix='/files')


@files_bp.route('/')
def index():
    """文件管理页面"""
    # 从会话或配置中获取默认仓库
    from app.services.config_service import ConfigService
    default_repo = ConfigService.get('github_repo')
    return render_template('files.html', default_repo=default_repo)


@files_bp.route('/api/list', methods=['POST'])
def api_list_files():
    """列出文件 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        path = data.get('path', '')

        if not repo:
            return jsonify({'error': '仓库路径不能为空'}), 400

        service = FileService()
        result = service.list_files(repo, path)
        return jsonify(result)

    except Exception as e:
        logger.error(f"列出文件失败: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/api/get', methods=['POST'])
def api_get_file():
    """获取文件内容 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        path = data.get('path', '').strip()
        branch = data.get('branch', 'main')

        if not repo or not path:
            return jsonify({'error': '仓库路径和文件路径不能为空'}), 400

        service = FileService()
        result = service.get_file(repo, path, branch)
        return jsonify(result)

    except Exception as e:
        logger.error(f"获取文件失败: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/api/default_branch', methods=['POST'])
def api_default_branch():
    """获取仓库默认分支 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()

        if not repo:
            return jsonify({'error': '仓库路径不能为空'}), 400

        service = FileService()
        result = service.get_default_branch(repo)
        return jsonify(result)

    except Exception as e:
        logger.error(f"获取默认分支失败: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/api/update', methods=['POST'])
def api_update_file():
    """更新文件 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        path = data.get('path', '').strip()
        content = data.get('content', '')
        message = data.get('message', 'Update file via Web UI')
        branch = data.get('branch', 'main')

        if not repo or not path:
            return jsonify({'error': '仓库路径和文件路径不能为空'}), 400

        if content is None:
            return jsonify({'error': '文件内容不能为空'}), 400

        service = FileService()
        result = service.update_file(repo, path, content, message, branch)
        return jsonify(result)

    except Exception as e:
        logger.error(f"更新文件失败: {e}")
        return jsonify({'error': str(e)}), 500


@files_bp.route('/editor')
def editor():
    """文件编辑器页面"""
    repo = request.args.get('repo', '')
    path = request.args.get('path', '')
    branch = request.args.get('branch', 'main')

    if not repo or not path:
        return redirect(url_for('files.index'))

    return render_template('editor.html', repo=repo, path=path, branch=branch)
