"""
配置管理服务
"""
import logging
import re
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from app import db
from app.models import Config

logger = logging.getLogger(__name__)


class ConfigService:
    """配置管理服务"""

    @staticmethod
    def get_all() -> Dict[str, str]:
        """获取所有配置"""
        configs = Config.query.all()
        return {config.key: config.value for config in configs}

    @staticmethod
    def get(key: str) -> Optional[str]:
        """获取单个配置值"""
        config = Config.query.filter_by(key=key).first()
        return config.value if config else None

    @staticmethod
    def get_config_object(key: str) -> Optional[Config]:
        """获取配置对象"""
        return Config.query.filter_by(key=key).first()

    @staticmethod
    def set(key: str, value: str, description: Optional[str] = None) -> bool:
        """设置配置值"""
        try:
            config = Config.query.filter_by(key=key).first()

            if config:
                # 更新现有配置
                config.value = value
                if description:
                    config.description = description
                logger.info(f"更新配置: {key}")
            else:
                # 创建新配置
                config = Config(key=key, value=value, description=description)
                db.session.add(config)
                logger.info(f"创建配置: {key}")

            db.session.commit()
            return True

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def set_many(configs: Dict[str, str]) -> bool:
        """批量设置配置"""
        try:
            for key, value in configs.items():
                config = Config.query.filter_by(key=key).first()
                if config:
                    config.value = value
                else:
                    config = Config(key=key, value=value)
                    db.session.add(config)

            db.session.commit()
            logger.info(f"批量保存配置: {len(configs)} 项")
            return True

        except Exception as e:
            logger.error(f"批量保存配置失败: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """删除配置"""
        try:
            config = Config.query.filter_by(key=key).first()
            if config:
                db.session.delete(config)
                db.session.commit()
                logger.info(f"删除配置: {key}")
                return True
            return False

        except Exception as e:
            logger.error(f"删除配置失败: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def get_all_details() -> List[Dict]:
        """获取所有配置详情"""
        configs = Config.query.all()
        return [config.to_dict() for config in configs]

    @staticmethod
    def validate_github_token(token: str) -> bool:
        """验证 GitHub Token 格式

        Token 格式：ghp_ 后跟 36 个字母数字字符
        """
        pattern = r'^ghp_[a-zA-Z0-9]{36}$'
        return bool(re.match(pattern, token))

    @staticmethod
    def validate_repo_path(repo: str) -> bool:
        """验证仓库路径格式

        格式：owner/repo
        """
        pattern = r'^[^/]+/[^/]+$'
        return bool(re.match(pattern, repo))

    # ==================== 快速触发管理 ====================

    @staticmethod
    def get_quick_triggers() -> List[Dict]:
        """获取快速触发列表

        Returns:
            快速触发列表，每个元素包含 id, name, repo, workflow_id 等信息
        """
        try:
            config_value = ConfigService.get('quick_triggers')
            if not config_value:
                return []

            triggers = json.loads(config_value)
            logger.info(f"获取快速触发列表: 共 {len(triggers)} 项")
            return triggers

        except json.JSONDecodeError as e:
            logger.error(f"解析快速触发配置失败: {e}")
            return []
        except Exception as e:
            logger.error(f"获取快速触发列表失败: {e}")
            return []

    @staticmethod
    def add_quick_trigger(name: str, repo: str, workflow_id: int,
                         workflow_name: str, branch: str = 'main') -> Dict:
        """添加快速触发项

        Args:
            name: 显示名称
            repo: 仓库路径 (owner/repo)
            workflow_id: 工作流 ID
            workflow_name: 工作流名称
            branch: 分支名，默认为 main

        Returns:
            dict: {
                'success': bool,
                'trigger': dict,   # 新创建的触发项
                'error': str       # 错误信息
            }
        """
        try:
            triggers = ConfigService.get_quick_triggers()

            # 创建新的快速触发项
            new_trigger = {
                'id': str(uuid.uuid4()),
                'name': name,
                'repo': repo,
                'workflow_id': workflow_id,
                'workflow_name': workflow_name,
                'branch': branch,
                'created_at': datetime.now().isoformat(),
                'last_status': None,
                'last_run_id': None
            }

            triggers.append(new_trigger)

            # 保存到配置
            if ConfigService.set('quick_triggers', json.dumps(triggers),
                                description='快速触发配置'):
                logger.info(f"添加快速触发成功: {name}")
                return {
                    'success': True,
                    'trigger': new_trigger
                }
            else:
                return {
                    'success': False,
                    'error': '保存配置失败'
                }

        except Exception as e:
            logger.error(f"添加快速触发失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_quick_trigger(trigger_id: str, name: str = None,
                           repo: str = None, workflow_id: int = None,
                           workflow_name: str = None, branch: str = None) -> Dict:
        """更新快速触发项

        Args:
            trigger_id: 快速触发项 ID
            name: 新的显示名称（可选）
            repo: 新的仓库路径（可选）
            workflow_id: 新的工作流 ID（可选）
            workflow_name: 新的工作流名称（可选）
            branch: 新的分支名（可选）

        Returns:
            dict: {
                'success': bool,
                'trigger': dict,   # 更新后的触发项
                'error': str       # 错误信息
            }
        """
        try:
            triggers = ConfigService.get_quick_triggers()

            # 查找并更新
            for trigger in triggers:
                if trigger['id'] == trigger_id:
                    if name is not None:
                        trigger['name'] = name
                    if repo is not None:
                        trigger['repo'] = repo
                    if workflow_id is not None:
                        trigger['workflow_id'] = workflow_id
                    if workflow_name is not None:
                        trigger['workflow_name'] = workflow_name
                    if branch is not None:
                        trigger['branch'] = branch

                    # 保存到配置
                    if ConfigService.set('quick_triggers', json.dumps(triggers)):
                        logger.info(f"更新快速触发成功: {trigger_id}")
                        return {
                            'success': True,
                            'trigger': trigger
                        }
                    else:
                        return {
                            'success': False,
                            'error': '保存配置失败'
                        }

            return {
                'success': False,
                'error': '快速触发项不存在'
            }

        except Exception as e:
            logger.error(f"更新快速触发失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def delete_quick_trigger(trigger_id: str) -> Dict:
        """删除快速触发项

        Args:
            trigger_id: 快速触发项 ID

        Returns:
            dict: {
                'success': bool,
                'error': str  # 错误信息
            }
        """
        try:
            triggers = ConfigService.get_quick_triggers()

            # 查找并删除
            original_length = len(triggers)
            triggers = [t for t in triggers if t['id'] != trigger_id]

            if len(triggers) < original_length:
                # 保存到配置
                if ConfigService.set('quick_triggers', json.dumps(triggers)):
                    logger.info(f"删除快速触发成功: {trigger_id}")
                    return {'success': True}
                else:
                    return {
                        'success': False,
                        'error': '保存配置失败'
                    }
            else:
                return {
                    'success': False,
                    'error': '快速触发项不存在'
                }

        except Exception as e:
            logger.error(f"删除快速触发失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_trigger_status(trigger_id: str, status: str, run_id: int = None) -> bool:
        """更新快速触发的执行状态

        Args:
            trigger_id: 快速触发项 ID
            status: 状态 (success/failure/running)
            run_id: GitHub Run ID（可选）

        Returns:
            bool: 是否成功
        """
        try:
            triggers = ConfigService.get_quick_triggers()

            for trigger in triggers:
                if trigger['id'] == trigger_id:
                    trigger['last_status'] = status
                    if run_id is not None:
                        trigger['last_run_id'] = run_id

                    # 保存到配置
                    ConfigService.set('quick_triggers', json.dumps(triggers))
                    logger.info(f"更新快速触发状态: {trigger_id} -> {status}")
                    return True

            return False

        except Exception as e:
            logger.error(f"更新快速触发状态失败: {e}")
            return False
