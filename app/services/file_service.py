"""
GitHub 文件管理服务
"""
import base64
import logging
from typing import Optional
from github import Github, GithubException
from app.services.config_service import ConfigService

logger = logging.getLogger(__name__)


class FileService:
    """GitHub 文件管理服务类"""

    def __init__(self):
        """初始化服务，从配置中加载 Token"""
        self.token = ConfigService.get('github_token')
        self.github = None
        if self.token:
            try:
                self.github = Github(self.token)
            except Exception as e:
                logger.error(f"初始化 GitHub 客户端失败: {e}")

    def get_default_branch(self, repo: str) -> dict:
        """获取仓库默认分支

        Args:
            repo: 仓库路径 (owner/repo)

        Returns:
            dict: {
                'success': bool,
                'branch': str,  # 默认分支名
                'error': str    # 错误信息
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            repo_obj = self.github.get_repo(repo)
            default_branch = repo_obj.default_branch
            logger.info(f"获取默认分支成功: {repo} -> {default_branch}")
            return {
                'success': True,
                'branch': default_branch
            }

        except GithubException as e:
            error_msg = f"获取默认分支失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"获取默认分支时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def list_files(self, repo: str, path: str = '') -> dict:
        """列出仓库文件

        Args:
            repo: 仓库路径 (owner/repo)
            path: 目录路径，空字符串表示根目录

        Returns:
            dict: {
                'success': bool,
                'files': list,  # 文件列表
                'error': str    # 错误信息
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            repo_obj = self.github.get_repo(repo)
            contents = repo_obj.get_contents(path)

            files = []
            for item in contents:
                files.append({
                    'name': item.name,
                    'path': item.path,
                    'type': 'dir' if item.type == 'dir' else 'file',
                    'size': item.size if hasattr(item, 'size') else 0
                })

            logger.info(f"列出文件成功: {repo}/{path}, 共 {len(files)} 项")
            return {
                'success': True,
                'files': files
            }

        except GithubException as e:
            error_msg = f"列出文件失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"列出文件时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def get_file(self, repo: str, path: str, branch: str = 'main') -> dict:
        """获取文件内容

        Args:
            repo: 仓库路径 (owner/repo)
            path: 文件路径
            branch: 分支名，默认为 main

        Returns:
            dict: {
                'success': bool,
                'content': str,  # 文件内容
                'sha': str,      # 文件 SHA
                'path': str,     # 文件路径
                'error': str     # 错误信息
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            repo_obj = self.github.get_repo(repo)
            content_file = repo_obj.get_contents(path, ref=branch)

            # 解码 base64
            decoded_content = base64.b64decode(content_file.content).decode('utf-8')

            logger.info(f"获取文件成功: {repo}/{path}")
            return {
                'success': True,
                'content': decoded_content,
                'sha': content_file.sha,
                'path': content_file.path
            }

        except GithubException as e:
            error_msg = f"获取文件失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"获取文件时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def update_file(self, repo: str, path: str, content: str,
                    message: str, branch: str = 'main') -> dict:
        """更新文件内容

        Args:
            repo: 仓库路径 (owner/repo)
            path: 文件路径
            content: 新的文件内容
            message: 提交信息
            branch: 分支名，默认为 main

        Returns:
            dict: {
                'success': bool,
                'error': str  # 错误信息
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            repo_obj = self.github.get_repo(repo)

            # 获取当前文件 SHA
            content_file = repo_obj.get_contents(path, ref=branch)
            sha = content_file.sha

            # 更新文件（PyGithub 会自动处理 base64 编码）
            repo_obj.update_file(
                path=path,
                message=message,
                content=content,
                sha=sha,
                branch=branch
            )

            logger.info(f"文件更新成功: {repo}/{path}")
            return {'success': True}

        except GithubException as e:
            error_msg = f"更新文件失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"更新文件时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
