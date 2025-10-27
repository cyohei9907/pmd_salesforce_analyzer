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
            
            # Windows 和 Linux 的临时目录处理
            if os.name == 'nt':  # Windows
                temp_dir = os.environ.get('TEMP', 'C:\\Temp')
                git_objects_dir = os.path.join(temp_dir, 'git-objects')
            else:  # Linux/Mac
                temp_dir = '/tmp'
                git_objects_dir = '/tmp/git-objects'
                env['GIT_CONFIG_GLOBAL'] = '/tmp/.gitconfig'
                env['TMPDIR'] = '/tmp'
                # 使用本地临时目录存储 Git 对象，避免 Cloud Storage 的限制
                env['GIT_OBJECT_DIRECTORY'] = git_objects_dir
                env['GIT_ALTERNATE_OBJECT_DIRECTORIES'] = ''
            
            # 确保临时目录存在
            os.makedirs(git_objects_dir, exist_ok=True)
            
            # 使用 shallow clone 并且只克隆单个分支,避免损坏的对象
            cmd = [
                'git', 'clone',
                '--depth', '1',              # Shallow clone
                '--single-branch',           # 只克隆单个分支
                '--no-tags',                 # 不获取 tags
                '--branch', branch,
                repo_url,
                str(target_dir)
            ]
            
            logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                env=env
            )
            
            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                
                # 如果 shallow clone 失败,尝试不指定分支的 shallow clone
                logger.info("Retrying with default branch...")
                
                # 清理失败的克隆
                if target_dir.exists():
                    shutil.rmtree(target_dir, onerror=remove_readonly)
                
                cmd_retry = [
                    'git', 'clone',
                    '--depth', '1',
                    '--single-branch',
                    '--no-tags',
                    repo_url,
                    str(target_dir)
                ]
                
                logger.info(f"Running: {' '.join(cmd_retry)}")
                
                result = subprocess.run(
                    cmd_retry,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    env=env
                )
            
            if result.returncode != 0:
                logger.error(f"Git clone retry also failed: {result.stderr}")
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
    
    def analyze_repository(self, repo_name, apex_dir='force-app/main/default/classes', progress_callback=None, current_progress=0, total_files=0):
        """
        使用PMD分析仓库中的Apex代码
        
        Args:
            repo_name: 仓库名称
            apex_dir: Apex代码相对目录，默认为Salesforce DX标准路径
            progress_callback: 进度回调函数 callback(current, total, message)
            current_progress: 当前已完成的文件数
            total_files: 总文件数
            
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
            
            # 创建输出目录 - 按仓库分类，Apex文件放在apex子目录下
            output_ast_dir = self.output_dir / 'ast' / repo_name / 'apex'
            output_ast_dir.mkdir(parents=True, exist_ok=True)
            
            # 分析每个文件
            analyzed_files = []
            failed_files = []
            
            for i, apex_file in enumerate(apex_files):
                if progress_callback:
                    progress_callback(current_progress + i, total_files, f'Analyzing {apex_file.name}...')
                
                result = self._analyze_apex_file(apex_file, output_ast_dir)
                if result['success']:
                    analyzed_files.append(result)
                else:
                    failed_files.append(result)
            
            return {
                'success': True,
                'repo_name': repo_name,
                'file_type': 'apex',
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
    
    def analyze_all_components(self, repo_name, structure_info=None, progress_callback=None):
        """
        分析仓库中的所有组件(Apex、Visualforce、LWC)
        
        Args:
            repo_name: 仓库名称
            structure_info: 项目结构信息(来自detect_salesforce_structure)
            progress_callback: 进度回调函数 callback(current, total, message)
            
        Returns:
            dict: 包含所有类型文件的分析结果
        """
        try:
            # 如果没有提供结构信息,先检测
            if not structure_info:
                structure_info = self.detect_salesforce_structure(repo_name)
                if not structure_info['success']:
                    return structure_info
            
            results = {
                'success': True,
                'repo_name': repo_name,
                'apex': None,
                'visualforce': None,
                'lwc': None,
            }
            
            # 计算总文件数
            total_files = 0
            if structure_info.get('apex_classes'):
                total_files += structure_info['apex_classes'].get('count', 0)
            if structure_info.get('visualforce_pages'):
                total_files += structure_info['visualforce_pages'].get('count', 0)
            if structure_info.get('lwc_components'):
                total_files += structure_info['lwc_components'].get('count', 0)
            
            current_progress = 0
            
            # 分析Apex类
            if structure_info.get('apex_classes'):
                apex_dir = structure_info['apex_classes']['path']
                if progress_callback:
                    progress_callback(current_progress, total_files, f'Analyzing Apex classes...')
                results['apex'] = self.analyze_repository(repo_name, apex_dir, progress_callback, current_progress, total_files)
                if results['apex'] and results['apex'].get('success'):
                    current_progress += results['apex'].get('analyzed', 0)
            
            # 分析Visualforce页面
            if structure_info.get('visualforce_pages'):
                vf_dir = structure_info['visualforce_pages']['path']
                if progress_callback:
                    progress_callback(current_progress, total_files, f'Analyzing Visualforce pages...')
                results['visualforce'] = self._analyze_visualforce(repo_name, vf_dir, progress_callback, current_progress, total_files)
                if results['visualforce'] and results['visualforce'].get('success'):
                    current_progress += results['visualforce'].get('analyzed', 0)
            
            # 分析LWC组件
            if structure_info.get('lwc_components'):
                lwc_dir = structure_info['lwc_components']['path']
                if progress_callback:
                    progress_callback(current_progress, total_files, f'Analyzing LWC components...')
                results['lwc'] = self._analyze_lwc(repo_name, lwc_dir, progress_callback, current_progress, total_files)
                if results['lwc'] and results['lwc'].get('success'):
                    current_progress += results['lwc'].get('analyzed', 0)
            
            # 计算总分析文件数
            total_analyzed = 0
            if results['apex'] and results['apex'].get('success'):
                total_analyzed += results['apex'].get('analyzed', 0)
            if results['visualforce'] and results['visualforce'].get('success'):
                total_analyzed += results['visualforce'].get('analyzed', 0)
            if results['lwc'] and results['lwc'].get('success'):
                total_analyzed += results['lwc'].get('analyzed', 0)
            
            results['analyzed'] = total_analyzed
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to analyze all components: {e}")
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
            
            # 保存源代码副本
            source_copy = output_dir / f"{file_name}.cls"
            if not source_copy.exists():
                shutil.copy2(apex_file, source_copy)
            
            logger.info(f"AST saved to: {output_file}")
            
            return {
                'success': True,
                'file': apex_file.name,
                'output_file': str(output_file),
                'source_file': str(source_copy),
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
    
    def _analyze_visualforce(self, repo_name, vf_dir, progress_callback=None, current_progress=0, total_files=0):
        """分析Visualforce页面"""
        try:
            repo_path = self.project_dir / repo_name
            vf_path = repo_path / vf_dir
            
            if not vf_path.exists():
                return {
                    'success': False,
                    'error': f'Visualforce directory not found: {vf_dir}',
                }
            
            # 查找所有.page文件
            vf_files = list(vf_path.glob('*.page'))
            
            if not vf_files:
                return {
                    'success': False,
                    'error': f'No Visualforce pages found in {vf_path}',
                }
            
            logger.info(f"Found {len(vf_files)} Visualforce pages in {vf_path}")
            
            # 创建输出目录
            output_vf_dir = self.output_dir / 'ast' / repo_name / 'visualforce'
            output_vf_dir.mkdir(parents=True, exist_ok=True)
            
            # 分析每个文件
            analyzed_files = []
            failed_files = []
            
            for i, vf_file in enumerate(vf_files):
                if progress_callback:
                    progress_callback(current_progress + i, total_files, f'Analyzing {vf_file.name}...')
                
                result = self._analyze_visualforce_file(vf_file, output_vf_dir)
                if result['success']:
                    analyzed_files.append(result)
                else:
                    failed_files.append(result)
            
            return {
                'success': True,
                'file_type': 'visualforce',
                'total_files': len(vf_files),
                'analyzed': len(analyzed_files),
                'failed': len(failed_files),
                'analyzed_files': analyzed_files,
                'failed_files': failed_files,
                'output_dir': str(output_vf_dir),
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze Visualforce: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def _analyze_visualforce_file(self, vf_file, output_dir):
        """使用PMD分析单个Visualforce页面"""
        try:
            file_name = vf_file.stem
            output_file = output_dir / f"{file_name}_ast.xml"
            
            logger.info(f"Analyzing Visualforce: {vf_file.name}")
            
            # PMD支持Visualforce分析
            cmd = [
                str(self.pmd_bin),
                'ast-dump',
                '--language', 'visualforce',
                '--format', 'xml',
                '--file', str(vf_file),
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"PMD Visualforce analysis failed for {vf_file.name}: {result.stderr}")
                return {
                    'success': False,
                    'file': vf_file.name,
                    'error': result.stderr,
                }
            
            # 保存AST输出
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            # 保存源代码副本
            source_copy = output_dir / f"{file_name}.page"
            if not source_copy.exists():
                shutil.copy2(vf_file, source_copy)
            
            logger.info(f"Visualforce AST saved to: {output_file}")
            
            return {
                'success': True,
                'file': vf_file.name,
                'output_file': str(output_file),
                'source_file': str(source_copy),
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Visualforce analysis timeout for {vf_file.name}")
            return {
                'success': False,
                'file': vf_file.name,
                'error': 'Analysis timeout',
            }
        except Exception as e:
            logger.error(f"Failed to analyze Visualforce {vf_file.name}: {e}")
            return {
                'success': False,
                'file': vf_file.name,
                'error': str(e),
            }
    
    def _analyze_lwc(self, repo_name, lwc_dir, progress_callback=None, current_progress=0, total_files=0):
        """简単分析LWC组件(提取基本信息)"""
        try:
            repo_path = self.project_dir / repo_name
            lwc_path = repo_path / lwc_dir
            
            if not lwc_path.exists():
                return {
                    'success': False,
                    'error': f'LWC directory not found: {lwc_dir}',
                }
            
            # LWC组件是目录结构
            lwc_components = [d for d in lwc_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            
            if not lwc_components:
                return {
                    'success': False,
                    'error': f'No LWC components found in {lwc_path}',
                }
            
            logger.info(f"Found {len(lwc_components)} LWC components in {lwc_path}")
            
            # 创建输出目录
            output_lwc_dir = self.output_dir / 'ast' / repo_name / 'lwc'
            output_lwc_dir.mkdir(parents=True, exist_ok=True)
            
            # 分析每个组件
            analyzed_components = []
            failed_components = []
            
            for i, lwc_comp in enumerate(lwc_components):
                if progress_callback:
                    progress_callback(current_progress + i, total_files, f'Analyzing {lwc_comp.name}...')
                
                result = self._analyze_lwc_component(lwc_comp, output_lwc_dir)
                if result['success']:
                    analyzed_components.append(result)
                else:
                    failed_components.append(result)
            
            return {
                'success': True,
                'file_type': 'lwc',
                'total_components': len(lwc_components),
                'analyzed': len(analyzed_components),
                'failed': len(failed_components),
                'analyzed_components': analyzed_components,
                'failed_components': failed_components,
                'output_dir': str(output_lwc_dir),
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze LWC: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def _analyze_lwc_component(self, lwc_dir, output_dir):
        """简单分析单个LWC组件"""
        try:
            comp_name = lwc_dir.name
            
            # LWC组件通常包含: .js, .html, .css, .xml等文件
            js_file = lwc_dir / f"{comp_name}.js"
            html_file = lwc_dir / f"{comp_name}.html"
            xml_file = lwc_dir / f"{comp_name}.js-meta.xml"
            
            component_info = {
                'name': comp_name,
                'has_js': js_file.exists(),
                'has_html': html_file.exists(),
                'has_meta': xml_file.exists(),
                'files': []
            }
            
            # 收集文件信息
            for file in lwc_dir.iterdir():
                if file.is_file():
                    component_info['files'].append({
                        'name': file.name,
                        'type': file.suffix,
                        'size': file.stat().st_size
                    })
            
            # 如果有JavaScript文件,可以使用PMD分析
            if js_file.exists():
                try:
                    output_file = output_dir / f"{comp_name}_ast.xml"
                    
                    cmd = [
                        str(self.pmd_bin),
                        'ast-dump',
                        '--language', 'ecmascript',  # JavaScript
                        '--format', 'xml',
                        '--file', str(js_file),
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(result.stdout)
                        component_info['ast_file'] = str(output_file)
                        component_info['ast_generated'] = True
                        
                        # 保存JavaScript源代码副本
                        js_source_copy = output_dir / f"{comp_name}.js"
                        if not js_source_copy.exists():
                            shutil.copy2(js_file, js_source_copy)
                        component_info['js_source'] = str(js_source_copy)
                    else:
                        component_info['ast_generated'] = False
                        component_info['ast_error'] = result.stderr
                        
                except Exception as e:
                    logger.warning(f"Could not generate AST for {comp_name}: {e}")
                    component_info['ast_generated'] = False
            
            # 保存其他LWC文件副本（HTML, CSS, XML等）
            comp_source_dir = output_dir / comp_name
            comp_source_dir.mkdir(exist_ok=True)
            
            for file in lwc_dir.iterdir():
                if file.is_file():
                    dest_file = comp_source_dir / file.name
                    if not dest_file.exists():
                        shutil.copy2(file, dest_file)
            
            component_info['source_dir'] = str(comp_source_dir)
            
            # 保存组件信息为JSON
            import json
            info_file = output_dir / f"{comp_name}_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(component_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"LWC component info saved: {info_file}")
            
            return {
                'success': True,
                'component': comp_name,
                'info_file': str(info_file),
                'details': component_info
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze LWC component {lwc_dir.name}: {e}")
            return {
                'success': False,
                'component': lwc_dir.name,
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
    
    def detect_salesforce_structure(self, repo_name):
        """
        自动检测Salesforce项目结构
        
        Args:
            repo_name: 仓库名称
            
        Returns:
            dict: 包含检测到的路径信息
        """
        try:
            repo_path = self.project_dir / repo_name
            
            if not repo_path.exists():
                return {
                    'success': False,
                    'error': f'Repository not found: {repo_name}',
                }
            
            result = {
                'success': True,
                'repo_name': repo_name,
                'repo_path': str(repo_path),
                'apex_classes': None,
                'lwc_components': None,
                'visualforce_pages': None,
                'detected_paths': []
            }
            
            # 常见的Salesforce项目结构路径
            apex_search_paths = [
                'force-app/main/default/classes',
                'src/classes',
                'classes',
            ]
            
            lwc_search_paths = [
                'force-app/main/default/lwc',
                'src/lwc',
                'lwc',
            ]
            
            vf_search_paths = [
                'force-app/main/default/pages',
                'src/pages',
                'pages',
            ]
            
            # 检测Apex类路径
            for path in apex_search_paths:
                full_path = repo_path / path
                if full_path.exists() and full_path.is_dir():
                    cls_files = list(full_path.glob('*.cls'))
                    if cls_files:
                        result['apex_classes'] = {
                            'path': path,
                            'full_path': str(full_path),
                            'count': len(cls_files)
                        }
                        result['detected_paths'].append(f'Apex类: {path} ({len(cls_files)}个文件)')
                        break
            
            # 检测LWC组件路径
            for path in lwc_search_paths:
                full_path = repo_path / path
                if full_path.exists() and full_path.is_dir():
                    # LWC组件是目录,不是文件
                    lwc_dirs = [d for d in full_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
                    if lwc_dirs:
                        result['lwc_components'] = {
                            'path': path,
                            'full_path': str(full_path),
                            'count': len(lwc_dirs)
                        }
                        result['detected_paths'].append(f'LWC组件: {path} ({len(lwc_dirs)}个组件)')
                        break
            
            # 检测Visualforce页面路径
            for path in vf_search_paths:
                full_path = repo_path / path
                if full_path.exists() and full_path.is_dir():
                    vf_files = list(full_path.glob('*.page'))
                    if vf_files:
                        result['visualforce_pages'] = {
                            'path': path,
                            'full_path': str(full_path),
                            'count': len(vf_files)
                        }
                        result['detected_paths'].append(f'Visualforce页面: {path} ({len(vf_files)}个文件)')
                        break
            
            logger.info(f"Detected structure for {repo_name}: {result['detected_paths']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to detect Salesforce structure: {e}")
            return {
                'success': False,
                'error': str(e),
            }


# 创建全局服务实例
git_service = GitService()
