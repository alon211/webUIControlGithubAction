"""
GitHub API 服务
"""
import logging
from github import Github, GithubException

logger = logging.getLogger(__name__)


class GitHubService:
    """GitHub API 服务类"""

    @staticmethod
    def test_token(token: str) -> dict:
        """测试 GitHub Token 有效性

        Args:
            token: GitHub Personal Access Token

        Returns:
            dict: {
                'success': bool,
                'username': str,  # 成功时返回用户名
                'error': str      # 失败时返回错误信息
            }
        """
        try:
            g = Github(token)
            user = g.get_user()

            # 尝试获取用户信息以验证 token
            login = user.login
            name = user.name

            logger.info(f"Token 验证成功, 用户: {login}")

            return {
                'success': True,
                'username': login,
                'name': name
            }

        except GithubException as e:
            error_msg = f"GitHub API 错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Token 验证失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
