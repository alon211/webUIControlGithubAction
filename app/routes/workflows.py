"""
工作流管理路由
"""
import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.services.workflow_service import WorkflowService
from app.services.config_service import ConfigService

logger = logging.getLogger(__name__)

# 创建蓝图
workflows_bp = Blueprint('workflows', __name__, url_prefix='/workflows')


@workflows_bp.route('/')
def index():
    """工作流管理页面"""
    default_repo = ConfigService.get('github_repo')
    return render_template('workflows.html', default_repo=default_repo)


@workflows_bp.route('/api/list', methods=['POST'])
def api_list_workflows():
    """列出工作流 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()

        if not repo:
            return jsonify({'error': '仓库路径不能为空'}), 400

        service = WorkflowService()
        result = service.list_workflows(repo)
        return jsonify(result)

    except Exception as e:
        logger.error(f"列出工作流失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/runs', methods=['POST'])
def api_get_runs():
    """获取工作流执行记录 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        workflow_id = data.get('workflow_id')  # 可选
        limit = data.get('limit', 10)

        if not repo:
            return jsonify({'error': '仓库路径不能为空'}), 400

        service = WorkflowService()

        # workflow_id 可能是 0，需要明确检查
        if workflow_id is not None:
            workflow_id = int(workflow_id)

        result = service.get_workflow_runs(repo, workflow_id, limit)
        return jsonify(result)

    except Exception as e:
        logger.error(f"获取工作流执行记录失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/trigger', methods=['POST'])
def api_trigger_workflow():
    """触发工作流 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        workflow_id = data.get('workflow_id')
        branch = data.get('branch', 'main')

        if not repo or workflow_id is None:
            return jsonify({'error': '仓库路径和工作流 ID 不能为空'}), 400

        service = WorkflowService()
        result = service.trigger_workflow(repo, int(workflow_id), branch)
        return jsonify(result)

    except Exception as e:
        logger.error(f"触发工作流失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/logs', methods=['POST'])
def api_get_logs():
    """获取工作流执行日志 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        run_id = data.get('run_id')

        if not repo or run_id is None:
            return jsonify({'error': '仓库路径和执行记录 ID 不能为空'}), 400

        service = WorkflowService()
        result = service.get_run_logs(repo, int(run_id))
        return jsonify(result)

    except Exception as e:
        logger.error(f"获取工作流日志失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/artifacts', methods=['POST'])
def api_list_artifacts():
    """列出工作流执行产物 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        run_id = data.get('run_id')

        if not repo or run_id is None:
            return jsonify({'error': '仓库路径和执行记录 ID 不能为空'}), 400

        service = WorkflowService()
        result = service.list_run_artifacts(repo, int(run_id))
        return jsonify(result)

    except Exception as e:
        logger.error(f"列出工作流产物失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/artifacts/download', methods=['POST'])
def api_download_artifact():
    """下载工作流产物 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()
        run_id = data.get('run_id')
        artifact_name = data.get('artifact_name', '').strip()
        download_dir = data.get('download_dir', '').strip()

        # 验证必填字段
        if not all([repo, run_id, artifact_name, download_dir]):
            return jsonify({'error': '缺少必填字段'}), 400

        service = WorkflowService()
        result = service.download_artifact(
            repo=repo,
            run_id=int(run_id),
            artifact_name=artifact_name,
            download_dir=download_dir
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"下载工作流产物失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/default_branch', methods=['POST'])
def api_default_branch():
    """获取仓库默认分支 API"""
    try:
        data = request.get_json()
        repo = data.get('repo', '').strip()

        if not repo:
            return jsonify({'error': '仓库路径不能为空'}), 400

        service = WorkflowService()
        result = service.get_default_branch(repo)
        return jsonify(result)

    except Exception as e:
        logger.error(f"获取默认分支失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/runs')
def runs():
    """工作流执行记录页面"""
    repo = request.args.get('repo', '')
    workflow_id = request.args.get('workflow_id', '')
    workflow_name = request.args.get('workflow_name', '')

    if not repo:
        return redirect(url_for('workflows.index'))

    return render_template('workflow_runs.html',
                           repo=repo,
                           workflow_id=workflow_id,
                           workflow_name=workflow_name)


@workflows_bp.route('/logs')
def logs():
    """工作流日志查看页面"""
    repo = request.args.get('repo', '')
    run_id = request.args.get('run_id', '')

    if not repo or not run_id:
        return redirect(url_for('workflows.index'))

    return render_template('workflow_logs.html',
                           repo=repo,
                           run_id=run_id)


# ==================== 快速触发 API ====================

@workflows_bp.route('/api/quick-triggers/list', methods=['POST'])
def api_quick_triggers_list():
    """获取快速触发列表 API"""
    try:
        service = WorkflowService()
        triggers = ConfigService.get_quick_triggers()

        # 为每个触发项获取最后状态
        for trigger in triggers:
            try:
                result = service.get_workflow_runs(
                    trigger['repo'],
                    int(trigger['workflow_id']),
                    limit=1
                )
                if result.get('success') and result.get('runs'):
                    latest_run = result['runs'][0]
                    status = latest_run.get('conclusion') or latest_run.get('status')

                    # 更新状态到配置
                    trigger['last_status'] = status

                    # 如果状态是完成状态，更新配置
                    if status in ['success', 'failure', 'cancelled', 'skipped']:
                        ConfigService.update_trigger_status(trigger['id'], status)

            except Exception as e:
                logger.warning(f"获取触发项状态失败: {e}")

        return jsonify({
            'success': True,
            'triggers': triggers
        })

    except Exception as e:
        logger.error(f"获取快速触发列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/quick-triggers/add', methods=['POST'])
def api_quick_triggers_add():
    """添加快速触发项 API"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        repo = data.get('repo', '').strip()
        workflow_id = data.get('workflow_id')
        workflow_name = data.get('workflow_name', '').strip()
        branch = data.get('branch', 'main')

        # 验证必填字段
        if not all([name, repo, workflow_id, workflow_name]):
            return jsonify({'error': '缺少必填字段'}), 400

        # 验证仓库路径格式
        if not ConfigService.validate_repo_path(repo):
            return jsonify({'error': '仓库路径格式不正确，应为 owner/repo'}), 400

        # 添加快速触发项
        result = ConfigService.add_quick_trigger(
            name=name,
            repo=repo,
            workflow_id=int(workflow_id),
            workflow_name=workflow_name,
            branch=branch
        )

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"添加快速触发项失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/quick-triggers/update', methods=['POST'])
def api_quick_triggers_update():
    """更新快速触发项 API"""
    try:
        data = request.get_json()
        trigger_id = data.get('id')
        name = data.get('name')
        repo = data.get('repo')
        workflow_id = data.get('workflow_id')
        workflow_name = data.get('workflow_name')
        branch = data.get('branch')

        if not trigger_id:
            return jsonify({'error': '缺少触发项 ID'}), 400

        # 更新快速触发项
        result = ConfigService.update_quick_trigger(
            trigger_id=trigger_id,
            name=name,
            repo=repo,
            workflow_id=int(workflow_id) if workflow_id else None,
            workflow_name=workflow_name,
            branch=branch
        )

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"更新快速触发项失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/quick-triggers/delete', methods=['POST'])
def api_quick_triggers_delete():
    """删除快速触发项 API"""
    try:
        data = request.get_json()
        trigger_id = data.get('id')

        if not trigger_id:
            return jsonify({'error': '缺少触发项 ID'}), 400

        result = ConfigService.delete_quick_trigger(trigger_id)

        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"删除快速触发项失败: {e}")
        return jsonify({'error': str(e)}), 500


@workflows_bp.route('/api/quick-triggers/trigger', methods=['POST'])
def api_quick_triggers_trigger():
    """触发快速工作流 API"""
    try:
        data = request.get_json()
        trigger_id = data.get('id')

        if not trigger_id:
            return jsonify({'error': '缺少触发项 ID'}), 400

        # 获取快速触发项
        triggers = ConfigService.get_quick_triggers()
        trigger = next((t for t in triggers if t['id'] == trigger_id), None)

        if not trigger:
            return jsonify({'error': '快速触发项不存在'}), 404

        # 先获取默认分支（如果未指定分支或使用默认分支）
        service = WorkflowService()
        branch_result = service.get_default_branch(trigger['repo'])

        # 使用获取到的分支，如果失败则使用配置中的分支
        if branch_result.get('success'):
            branch = branch_result['branch']
        else:
            branch = trigger.get('branch', 'main')

        # 触发工作流（确保 workflow_id 是整数）
        result = service.trigger_workflow(
            repo=trigger['repo'],
            workflow_id=int(trigger['workflow_id']),
            branch=branch
        )

        if result.get('success'):
            # 更新状态为进行中
            ConfigService.update_trigger_status(trigger_id, 'running')

            # 尝试获取刚触发的工作流 run_id
            try:
                runs_result = service.get_workflow_runs(
                    trigger['repo'],
                    int(trigger['workflow_id']),
                    limit=1
                )
                if runs_result.get('success') and runs_result.get('runs'):
                    latest_run = runs_result['runs'][0]
                    # 更新 run_id
                    ConfigService.update_trigger_status(
                        trigger_id,
                        'running',
                        run_id=latest_run.get('id')
                    )
            except Exception as e:
                logger.warning(f"获取 run_id 失败，将继续监控: {e}")

            return jsonify({
                'success': True,
                'message': f"工作流 \"{trigger['name']} 已在 {branch} 分支触发",
                'trigger': trigger,
                'branch': branch
            })
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"触发快速工作流失败: {e}")
        return jsonify({'error': str(e)}), 500
