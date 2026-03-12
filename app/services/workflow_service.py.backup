"""
GitHub Actions 工作流管理服务
"""
import logging
import zipfile
import shutil
import requests
import tempfile
from pathlib import Path
from typing import Optional
from github import Github, GithubException
from app.services.config_service import ConfigService

logger = logging.getLogger(__name__)


class WorkflowService:
    """GitHub Actions 工作流管理服务类"""

    def __init__(self):
        """初始化服务，从配置中加载 Token"""
        self.token = ConfigService.get('github_token')
        self.github = None
        if self.token:
            try:
                self.github = Github(self.token)
            except Exception as e:
                logger.error(f"初始化 GitHub 客户端失败: {e}")

    def list_workflows(self, repo: str) -> dict:
        """列出仓库的所有工作流

        Args:
            repo: 仓库路径 (owner/repo)

        Returns:
            dict: {
                'success': bool,
                'workflows': list,  # 工作流列表
                'error': str        # 错误信息
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            repo_obj = self.github.get_repo(repo)
            workflows = repo_obj.get_workflows()

            workflow_list = []
            for workflow in workflows:
                workflow_list.append({
                    'id': workflow.id,
                    'name': workflow.name,
                    'path': workflow.path,
                    'state': workflow.state,
                    'created_at': str(workflow.created_at),
                    'updated_at': str(workflow.updated_at),
                    'html_url': workflow.html_url
                })

            logger.info(f"列出工作流成功: {repo}, 共 {len(workflow_list)} 个")
            return {
                'success': True,
                'workflows': workflow_list
            }

        except GithubException as e:
            error_msg = f"列出工作流失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"列出工作流时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def get_workflow_runs(self, repo: str, workflow_id: Optional[int] = None, limit: int = 10) -> dict:
        """获取工作流执行记录

        Args:
            repo: 仓库路径 (owner/repo)
            workflow_id: 工作流 ID，None 表示获取所有工作流的执行记录
            limit: 返回记录数量限制

        Returns:
            dict: {
                'success': bool,
                'runs': list,     # 执行记录列表
                'error': str      # 错误信息
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            repo_obj = self.github.get_repo(repo)

            if workflow_id:
                workflow = repo_obj.get_workflow(workflow_id)
                runs = workflow.get_runs()[:limit]
            else:
                runs = repo_obj.get_workflow_runs()[:limit]

            run_list = []
            for run in runs:
                # 安全地获取 actor 属性
                actor_login = None
                try:
                    if hasattr(run, 'actor') and run.actor:
                        actor_login = run.actor.login if hasattr(run.actor, 'login') else str(run.actor)
                except Exception:
                    actor_login = None

                run_list.append({
                    'id': run.id,
                    'name': run.name,
                    'display_title': run.display_title,
                    'status': run.status,
                    'conclusion': run.conclusion,
                    'created_at': str(run.created_at),
                    'updated_at': str(run.updated_at),
                    'html_url': run.html_url,
                    'event': run.event,
                    'actor': actor_login
                })

            logger.info(f"获取工作流执行记录成功: {repo}, 共 {len(run_list)} 条")
            return {
                'success': True,
                'runs': run_list
            }

        except GithubException as e:
            error_msg = f"获取工作流执行记录失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"获取工作流执行记录时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def trigger_workflow(self, repo: str, workflow_id: int, branch: str = 'main') -> dict:
        """触发工作流执行

        Args:
            repo: 仓库路径 (owner/repo)
            workflow_id: 工作流 ID
            branch: 分支名，默认为 main

        Returns:
            dict: {
                'success': bool,
                'run_id': int,   # 执行记录 ID
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
            workflow = repo_obj.get_workflow(workflow_id)

            # 触发工作流（使用 dispatch API）
            # 创建一个空的 inputs 字典
            result = workflow.create_dispatch(branch, inputs={})

            if result:
                logger.info(f"工作流触发成功: {repo}/{workflow_id} on {branch}")
                return {
                    'success': True,
                    'message': '工作流已触发'
                }
            else:
                return {
                    'success': False,
                    'error': '工作流触发失败'
                }

        except GithubException as e:
            error_msg = f"触发工作流失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"触发工作流时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def get_run_logs(self, repo: str, run_id: int) -> dict:
        """获取工作流执行日志

        Args:
            repo: 仓库路径 (owner/repo)
            run_id: 执行记录 ID

        Returns:
            dict: {
                'success': bool,
                'logs': str,     # 日志内容
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
            run = repo_obj.get_workflow_run(run_id)

            # 获取日志
            logs = run.get_logs()

            if logs:
                logger.info(f"获取工作流日志成功: {repo}/{run_id}")
                return {
                    'success': True,
                    'logs': logs
                }
            else:
                return {
                    'success': False,
                    'error': '日志不可用或工作流仍在运行中'
                }

        except GithubException as e:
            error_msg = f"获取工作流日志失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"获取工作流日志时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def list_run_artifacts(self, repo: str, run_id: int) -> dict:
        """列出工作流执行产物

        Args:
            repo: 仓库路径 (owner/repo)
            run_id: 执行记录 ID

        Returns:
            dict: {
                'success': bool,
                'artifacts': list,  # 产物列表
                'error': str        # 错误信息
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            # 使用原始 HTTP 请求直接调用 GitHub API
            # API 端点: GET /repos/{owner}/{repo}/actions/runs/{run_id}/artifacts
            url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            artifacts_data = data.get('artifacts', [])

            artifact_list = []
            for artifact in artifacts_data:
                artifact_list.append({
                    'id': artifact['id'],
                    'name': artifact['name'],
                    'size': artifact['size_in_bytes'],
                    'created_at': artifact['created_at'],
                    'expired': artifact['expired'],
                    'download_url': artifact['archive_download_url']
                })

            logger.info(f"列出工作流产物成功: {repo}/{run_id}, 共 {len(artifact_list)} 个")
            return {
                'success': True,
                'artifacts': artifact_list
            }

        except GithubException as e:
            error_msg = f"列出工作流产物失败: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"列出工作流产物时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

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

    def download_artifact(
        self,
        repo: str,
        run_id: int,
        artifact_name: str,
        download_dir: str
    ) -> dict:
        """下载并解压 GitHub Actions 产物

        Args:
            repo: 仓库路径 (owner/repo)
            run_id: 执行记录 ID
            artifact_name: 产物名称
            download_dir: 下载目录路径

        Returns:
            dict: {
                'success': bool,
                'message': str,
                'extracted_path': str,
                'file_count': int,
                'error': str
            }
        """
        if not self.github:
            return {
                'success': False,
                'error': 'GitHub Token 未配置或无效'
            }

        try:
            # 1. 获取产物下载 URL
            artifacts_result = self.list_run_artifacts(repo, run_id)
            if not artifacts_result['success']:
                return {
                    'success': False,
                    'error': f"获取产物列表失败: {artifacts_result['error']}"
                }

            # 查找目标产物
            target_artifact = None
            for artifact in artifacts_result['artifacts']:
                if artifact['name'] == artifact_name:
                    target_artifact = artifact
                    break

            if not target_artifact:
                return {
                    'success': False,
                    'error': f"未找到产物: {artifact_name}"
                }

            if target_artifact['expired']:
                return {
                    'success': False,
                    'error': f"产物已过期: {artifact_name}"
                }

            download_url = target_artifact['download_url']
            artifact_size = target_artifact['size']

            # 2. 验证并创建下载目录
            download_path = Path(download_dir)
            try:
                download_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return {
                    'success': False,
                    'error': f"创建下载目录失败: {e}"
                }

            # 3. 检查磁盘空间
            try:
                self._check_disk_space(download_path, artifact_size)
            except IOError as e:
                return {
                    'success': False,
                    'error': str(e)
                }

            # 4. 下载 ZIP 文件到临时位置
            logger.info(f"开始下载产物: {artifact_name} ({artifact_size / 1024 / 1024:.1f} MB)")
            temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)

            try:
                # 使用 Token 认证
                headers = {
                    'Authorization': f"Bearer {self.token}",
                    'Accept': 'application/vnd.github.v3+json'
                }

                with requests.get(download_url, headers=headers, stream=True, timeout=300) as r:
                    r.raise_for_status()

                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            temp_zip.write(chunk)
                            downloaded += len(chunk)

                            # 每 10MB 记录一次
                            if downloaded % (10 * 1024 * 1024) == 0:
                                logger.info(f"已下载: {downloaded / 1024 / 1024:.1f} MB")

                temp_zip.close()
                logger.info(f"下载完成: {temp_zip.name}")

            except Exception as e:
                temp_zip.close()
                Path(temp_zip.name).unlink(missing_ok=True)
                return {
                    'success': False,
                    'error': f"下载失败: {e}"
                }

            # 5. 解压文件
            extract_path = download_path / artifact_name
            try:
                file_count = self._extract_zip(temp_zip.name, extract_path)
                logger.info(f"解压成功: {extract_path}, 共 {file_count} 个文件")
            except Exception as e:
                Path(temp_zip.name).unlink(missing_ok=True)
                return {
                    'success': False,
                    'error': f"解压失败: {e}"
                }

            # 6. 删除 ZIP 文件
            Path(temp_zip.name).unlink(missing_ok=True)

            return {
                'success': True,
                'message': f'产物 "{artifact_name}" 下载并解压成功',
                'extracted_path': str(extract_path),
                'file_count': file_count
            }

        except Exception as e:
            error_msg = f"下载产物时发生错误: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }

    def _check_disk_space(self, path: Path, required_bytes: int):
        """检查磁盘剩余空间

        Args:
            path: 检查路径
            required_bytes: 需要的字节数

        Raises:
            IOError: 磁盘空间不足
        """
        try:
            stat = shutil.disk_usage(path)
            available = stat.free

            # 预留 20% 缓冲空间
            required_with_buffer = int(required_bytes * 1.2)

            if available < required_with_buffer:
                available_gb = available / (1024 ** 3)
                required_gb = required_bytes / (1024 ** 3)
                raise IOError(
                    f"磁盘空间不足。需要: {required_gb:.1f} GB，可用: {available_gb:.1f} GB"
                )

        except Exception as e:
            if isinstance(e, IOError):
                raise
            logger.warning(f"检查磁盘空间失败: {e}")

    def _extract_zip(self, zip_path: str, extract_to: Path) -> int:
        """解压 ZIP 文件，自动处理编码问题

        Args:
            zip_path: ZIP 文件路径
            extract_to: 解压目标目录

        Returns:
            int: 解压的文件数量

        Raises:
            Exception: 解压失败
        """
        extract_to.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_count = 0

            for info in zip_ref.infolist():
                try:
                    # 尝试 UTF-8 解码（Linux/macOS 创建的 ZIP）
                    decoded_name = info.filename.encode('cp437').decode('utf-8')
                    info.filename = decoded_name
                except UnicodeDecodeError:
                    # 回退到 GBK（Windows 创建的 ZIP）
                    try:
                        info.filename = info.filename.encode('cp437').decode('gbk')
                    except UnicodeDecodeError:
                        # 最后尝试原始名称
                        pass

                # 跳过目录（仅创建文件）
                if not info.filename.endswith('/'):
                    zip_ref.extract(info, extract_to)
                    file_count += 1
                else:
                    # 创建目录
                    (extract_to / info.filename).mkdir(parents=True, exist_ok=True)

            return file_count
