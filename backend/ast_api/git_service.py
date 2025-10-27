"""
Git仓库服务
从Git仓库克隆Salesforce项目并分析
"""
import os
import subprocess
import shutil
import stat
import platform
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def remove_readonly(func, path, excinfo):
    """
    错误处理函数：删除只读文件
    用于处理 Windows 上 Git 仓库的只读文件
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


class GitService:
    """Git仓库服务"""
    
    def __init__(self):
        # 项目克隆目录
        self.project_dir = Path(settings.BASE_DIR).parent / 'project'
        
        # AST输出目录 - 支持Cloud Storage
        if settings.USE_CLOUD_STORAGE:
            import sys
            sys.path.insert(0, str(Path(settings.BASE_DIR).parent))
            from cloud_storage import get_data_path
            self.output_dir = get_data_path('ast').parent
        else:
            self.output_dir = Path(settings.BASE_DIR).parent / 'output'
        
        # 根据操作系统选择正确的 PMD 命令
        analyzer_bin = Path(settings.BASE_DIR).parent / 'analyzer' / 'bin'
        if platform.system() == 'Windows':
            self.pmd_bin = analyzer_bin / 'pmd.bat'
        else:
            self.pmd_bin = analyzer_bin / 'pmd'
        
    def clone_repository(self, repo_url, branch='main', force=False):
        """
        克隆Git仓库
        
        Args:
            repo_url: Git仓库URL
            branch: 分支名称，默认为main
            force: 是否强制重新克隆（删除已存在的目录）
            
        Returns:
            dict: 包含克隆结果的字典
        """
        try:
            # 从URL提取仓库名称
            repo_name = self._extract_repo_name(repo_url)
            target_dir = self.project_dir / repo_name
            
            # 如果目录已存在且force=True，则删除
            if target_dir.exists():
                if force:
                    logger.info(f"Removing existing repository: {target_dir}")
                    try:
                        # 使用 onerror 回调处理只读文件（Windows Git 仓库常见问题）
                        shutil.rmtree(target_dir, onerror=remove_readonly)
                    except Exception as e:
                        logger.error(f"Failed to remove directory: {e}")
                        return {
                            'success': False,
                            'error': f'Failed to remove existing repository: {str(e)}',
                            'repo_name': repo_name,
                        }
                else:
                    return {
                        'success': False,
                        'error': f'Repository already exists: {repo_name}. Use force=True to overwrite.',
                        'repo_name': repo_name,
                    }
            
            # 确保项目目录存在
            self.project_dir.mkdir(parents=True, exist_ok=True)
            
            # 克隆仓库
            logger.info(f"Cloning repository: {repo_url} (branch: {branch})")
            
            # 设置环境变量以避免 Cloud Storage FUSE 的硬链接问题
            env = os.environ.copy()
            env['GIT_CONFIG_GLOBAL'] = '/tmp/.gitconfig'
            env['TMPDIR'] = '/tmp'
            # 使用本地临时目录存储 Git 对象，避免 Cloud Storage 的限制
            env['GIT_OBJECT_DIRECTORY'] = '/tmp/git-objects'
            env['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = ''
            
            # 确保临时目录存在
            os.makedirs('/tmp/git-objects', exist_ok=True)
            
            cmd = ['git', 'clone', '--depth', '1', '--branch', branch, repo_url, str(target_dir)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                env=env
            )
            
            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return {
                    'success': False,
                    'error': f'Git clone failed: {result.stderr}',
                    'repo_name': repo_name,
                }
            
            logger.info(f"Successfully cloned repository to: {target_dir}")
            
            return {
                'success': True,
                'repo_name': repo_name,
                'target_dir': str(target_dir),
                'message': f'Successfully cloned {repo_name}',
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Git clone timeout")
            return {
                'success': False,
                'error': 'Git clone timeout (> 5 minutes)',
            }
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def analyze_repository(self, repo_name, apex_dir='force-app/main/default/classes'):
        """
        使用PMD分析仓库中的Apex代码
        
        Args:
            repo_name: 仓库名称
            apex_dir: Apex代码相对目录，默认为Salesforce DX标准路径
            
        Returns:
            dict: 包含分析结果的字典
        """
        try:
            repo_path = self.project_dir / repo_name
            
            if not repo_path.exists():
                return {
                    'success': False,
                    'error': f'Repository not found: {repo_name}',
                }
            
            # 查找Apex类文件
            apex_path = repo_path / apex_dir
            
            if not apex_path.exists():
                # 尝试其他常见路径
                alternative_paths = [
                    'src/classes',
                    'classes',
                    'force-app/main/default/classes',
                ]
                
                for alt_path in alternative_paths:
                    test_path = repo_path / alt_path
                    if test_path.exists():
                        apex_path = test_path
                        break
                
                if not apex_path.exists():
                    return {
                        'success': False,
                        'error': f'Apex classes directory not found in {repo_name}',
                        'searched_paths': [apex_dir] + alternative_paths,
                    }
            
            # 查找所有.cls文件
            apex_files = list(apex_path.glob('*.cls'))
            
            if not apex_files:
                return {
                    'success': False,
                    'error': f'No Apex class files found in {apex_path}',
                }
            
            logger.info(f"Found {len(apex_files)} Apex files in {apex_path}")
            
            # 创建输出目录
            output_ast_dir = self.output_dir / 'ast'
            output_ast_dir.mkdir(parents=True, exist_ok=True)
            
            # 分析每个文件
            analyzed_files = []
            failed_files = []
            
            for apex_file in apex_files:
                result = self._analyze_apex_file(apex_file, output_ast_dir)
                if result['success']:
                    analyzed_files.append(result)
                else:
                    failed_files.append(result)
            
            return {
                'success': True,
                'repo_name': repo_name,
                'total_files': len(apex_files),
                'analyzed': len(analyzed_files),
                'failed': len(failed_files),
                'analyzed_files': analyzed_files,
                'failed_files': failed_files,
                'output_dir': str(output_ast_dir),
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze repository: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def _analyze_apex_file(self, apex_file, output_dir):
        """使用PMD分析单个Apex文件"""
        try:
            file_name = apex_file.stem  # 不含扩展名的文件名
            output_file = output_dir / f"{file_name}_ast.xml"
            
            logger.info(f"Analyzing: {apex_file.name}")
            
            # 构建PMD命令 - 使用正确的参数
            cmd = [
                str(self.pmd_bin),
                'ast-dump',
                '--language', 'apex',
                '--format', 'xml',
                '--file', str(apex_file),
            ]
            
            # 执行PMD命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1分钟超时
            )
            
            if result.returncode != 0:
                logger.error(f"PMD analysis failed for {apex_file.name}: {result.stderr}")
                return {
                    'success': False,
                    'file': apex_file.name,
                    'error': result.stderr,
                }
            
            # 保存AST输出
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            logger.info(f"AST saved to: {output_file}")
            
            return {
                'success': True,
                'file': apex_file.name,
                'output_file': str(output_file),
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"PMD analysis timeout for {apex_file.name}")
            return {
                'success': False,
                'file': apex_file.name,
                'error': 'Analysis timeout',
            }
        except Exception as e:
            logger.error(f"Failed to analyze {apex_file.name}: {e}")
            return {
                'success': False,
                'file': apex_file.name,
                'error': str(e),
            }
    
    def list_repositories(self):
        """列出已克隆的仓库"""
        try:
            if not self.project_dir.exists():
                return {
                    'success': True,
                    'repositories': [],
                }
            
            repos = []
            for item in self.project_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # 检查是否为Git仓库
                    git_dir = item / '.git'
                    if git_dir.exists():
                        repos.append({
                            'name': item.name,
                            'path': str(item),
                        })
            
            return {
                'success': True,
                'repositories': repos,
            }
            
        except Exception as e:
            logger.error(f"Failed to list repositories: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def delete_repository(self, repo_name):
        """删除已克隆的仓库"""
        try:
            repo_path = self.project_dir / repo_name
            
            if not repo_path.exists():
                return {
                    'success': False,
                    'error': f'Repository not found: {repo_name}',
                }
            
            # 使用 onerror 回调处理只读文件
            shutil.rmtree(repo_path, onerror=remove_readonly)
            logger.info(f"Deleted repository: {repo_name}")
            
            return {
                'success': True,
                'message': f'Successfully deleted {repo_name}',
            }
            
        except Exception as e:
            logger.error(f"Failed to delete repository: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def _extract_repo_name(self, repo_url):
        """从Git URL提取仓库名称"""
        # 移除 .git 后缀
        url = repo_url.rstrip('/')
        if url.endswith('.git'):
            url = url[:-4]
        
        # 提取最后一部分作为仓库名
        return url.split('/')[-1]


# 创建全局服务实例
git_service = GitService()
