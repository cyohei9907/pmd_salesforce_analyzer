"""
REST API视图
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .import_service import ast_import_service, ASTImportService
from .unified_graph_service import unified_graph_service
from .git_service import git_service, GitService
from .models import ASTFile, Repository
from .serializers import RepositorySerializer, ASTFileSerializer
from pathlib import Path
from django.conf import settings
import logging
import threading
import uuid

logger = logging.getLogger(__name__)

# 全局进度跟踪字典
analysis_progress = {}
progress_lock = threading.Lock()


@api_view(['POST'])
def import_ast_file(request):
    """导入单个AST文件"""
    file_path = request.data.get('file_path')
    
    if not file_path:
        return Response(
            {'error': 'file_path is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 支持相对路径：相对于项目根目录
    path_obj = Path(file_path)
    if not path_obj.is_absolute():
        # 获取项目根目录（Django BASE_DIR 的父目录）
        project_root = settings.BASE_DIR.parent
        path_obj = project_root / file_path
    
    if not path_obj.exists():
        return Response(
            {'error': f'File not found: {path_obj}'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    result = ast_import_service.import_ast_file(str(path_obj))
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def import_ast_directory(request):
    """导入目录中的所有AST文件"""
    directory_path = request.data.get('directory_path')
    
    if not directory_path:
        return Response(
            {'error': 'directory_path is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 支持相对路径：相对于项目根目录
    path_obj = Path(directory_path)
    if not path_obj.is_absolute():
        # 获取项目根目录（Django BASE_DIR 的父目录）
        project_root = settings.BASE_DIR.parent
        path_obj = project_root / directory_path
    
    if not path_obj.exists():
        return Response(
            {'error': f'Directory not found: {path_obj}'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    result = ast_import_service.import_directory(str(path_obj))
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_graph_data(request):
    """获取完整的图数据用于可视化"""
    try:
        graph_data = unified_graph_service.get_full_graph()
        
        # 转换为前端需要的格式
        nodes = []
        for node in graph_data['nodes']:
            node_obj = {
                'id': node['id'],
                'label': ', '.join(node['labels']),
                'type': node['labels'][0] if node['labels'] else 'Unknown',
                'properties': node['properties'],
            }
            
            # 设置节点显示名称
            if 'ApexClass' in node['labels']:
                node_obj['name'] = node['properties'].get('name', 'Unknown')
            elif 'ApexMethod' in node['labels'] or 'Method' in node['labels']:
                node_obj['name'] = node['properties'].get('name', 'Unknown')
            elif 'SOQLQuery' in node['labels']:
                query = node['properties'].get('query', '')
                node_obj['name'] = query[:50] + '...' if len(query) > 50 else query
            elif 'DMLOperation' in node['labels']:
                node_obj['name'] = node['properties'].get('operationType', 'DML')
            elif 'LWCComponent' in node['labels']:
                node_obj['name'] = node['properties'].get('name', 'Unknown')
            elif 'JavaScriptClass' in node['labels']:
                node_obj['name'] = node['properties'].get('name', 'Unknown')
            elif 'JavaScriptMethod' in node['labels']:
                node_obj['name'] = node['properties'].get('name', 'Unknown')
            elif 'JavaScriptFunction' in node['labels']:
                node_obj['name'] = node['properties'].get('name', 'Unknown')
            elif 'Dependency' in node['labels']:
                module = node['properties'].get('module', 'Unknown')
                # 依赖模块名称简化显示
                if '/' in module:
                    node_obj['name'] = module.split('/')[-1]  # 取最后一部分
                else:
                    node_obj['name'] = module
            else:
                node_obj['name'] = node['properties'].get('name', 'Unknown')
            
            nodes.append(node_obj)
        
        edges = []
        for edge in graph_data['edges']:
            edges.append({
                'source': edge['source'],
                'target': edge['target'],
                'type': edge['type'],
                'label': edge['type'],
            })
        
        return Response({
            'nodes': nodes,
            'edges': edges,
        })
        
    except Exception as e:
        logger.error(f"Failed to get graph data: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_class_graph(request, class_name):
    """获取特定类的图数据"""
    try:
        graph_data = unified_graph_service.get_class_graph(class_name)
        return Response(graph_data)
    except Exception as e:
        logger.error(f"Failed to get class graph: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_statistics(request):
    """获取数据库统计信息"""
    try:
        raw_stats = unified_graph_service.get_statistics()
        
        # 从嵌套结构中提取实际统计数据
        # unified_graph_service 返回的是 {'backend': 'local', 'neo4j': None, 'local': {...}}
        stats = {}
        
        # 优先使用 local 统计（因为当前默认使用本地图数据库）
        if raw_stats.get('local'):
            local_stats = raw_stats['local']
            stats = {
                'classes': local_stats.get('classes', 0),
                'methods': local_stats.get('methods', 0),
                'soqls': local_stats.get('soqls', 0),
                'dmls': local_stats.get('dmls', 0),
                'total_nodes': local_stats.get('total_nodes', 0),
                'total_edges': local_stats.get('total_edges', 0),
            }
        # 如果使用 Neo4j
        elif raw_stats.get('neo4j'):
            neo4j_stats = raw_stats['neo4j']
            stats = {
                'classes': neo4j_stats.get('classes', 0),
                'methods': neo4j_stats.get('methods', 0),
                'soqls': neo4j_stats.get('soqls', 0),
                'dmls': neo4j_stats.get('dmls', 0),
            }
        else:
            # 没有可用的数据库
            stats = {
                'classes': 0,
                'methods': 0,
                'soqls': 0,
                'dmls': 0,
                'total_nodes': 0,
                'total_edges': 0,
            }
        
        # 添加导入文件统计
        imported_files = ASTFile.objects.count()
        stats['imported_files'] = imported_files
        
        # 添加后端类型信息
        stats['backend'] = raw_stats.get('backend', 'none')
        
        return Response(stats)
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_imported_files(request):
    """列出所有已导入的文件（按仓库分组）"""
    import os
    from collections import defaultdict
    
    # 获取所有仓库
    repositories = Repository.objects.all()
    
    result = {
        'repositories': []
    }
    
    for repo in repositories:
        repo_data = {
            'id': repo.id,
            'name': repo.name,
            'url': repo.url,
            'branch': repo.branch,
            'is_active': repo.is_active,
            'components': {
                'apex': [],
                'visualforce': [],
                'lwc': []
            }
        }
        
        # 获取输出目录
        output_dir = Path(settings.BASE_DIR).parent / 'output' / 'ast' / repo.name
        
        # Apex 文件
        apex_dir = output_dir / 'apex'
        if apex_dir.exists():
            for xml_file in apex_dir.glob('*_ast.xml'):
                file_name = xml_file.stem.replace('_ast', '')
                source_file = xml_file.with_suffix('.cls')
                repo_data['components']['apex'].append({
                    'name': file_name,
                    'ast_file': str(xml_file),
                    'source_file': str(source_file) if source_file.exists() else None,
                    'type': 'apex'
                })
        
        # Visualforce 文件
        vf_dir = output_dir / 'visualforce'
        if vf_dir.exists():
            for xml_file in vf_dir.glob('*_ast.xml'):
                file_name = xml_file.stem.replace('_ast', '')
                source_file = xml_file.with_suffix('.page')
                repo_data['components']['visualforce'].append({
                    'name': file_name,
                    'ast_file': str(xml_file),
                    'source_file': str(source_file) if source_file.exists() else None,
                    'type': 'visualforce'
                })
        
        # LWC 组件
        lwc_dir = output_dir / 'lwc'
        if lwc_dir.exists():
            for info_file in lwc_dir.glob('*_info.json'):
                comp_name = info_file.stem.replace('_info', '')
                ast_file = lwc_dir / f'{comp_name}_ast.xml'
                repo_data['components']['lwc'].append({
                    'name': comp_name,
                    'ast_file': str(ast_file) if ast_file.exists() else None,
                    'info_file': str(info_file),
                    'type': 'lwc'
                })
        
        result['repositories'].append(repo_data)
    
    return Response(result)


@api_view(['DELETE'])
def clear_database(request):
    """清空图数据库（谨慎使用）"""
    try:
        unified_graph_service.clear_database()
        ASTFile.objects.all().delete()
        return Response({'message': 'Database cleared successfully'})
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def clone_repository(request):
    """克隆Git仓库"""
    repo_url = request.data.get('repo_url')
    branch = request.data.get('branch', 'main')
    force = request.data.get('force', False)
    
    if not repo_url:
        return Response(
            {'error': 'repo_url is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = git_service.clone_repository(repo_url, branch, force)
    
    if result['success']:
        return Response(result, status=status.HTTP_201_CREATED)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def analyze_repository(request):
    """分析Git仓库中的Apex代码"""
    repo_name = request.data.get('repo_name')
    apex_dir = request.data.get('apex_dir', 'force-app/main/default/classes')
    
    if not repo_name:
        return Response(
            {'error': 'repo_name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = git_service.analyze_repository(repo_name, apex_dir)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


def update_progress(task_id, stage, message, progress=0, total=0):
    """更新进度"""
    with progress_lock:
        analysis_progress[task_id] = {
            'stage': stage,
            'message': message,
            'progress': progress,
            'total': total,
            'percentage': int((progress / total * 100) if total > 0 else 0),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }


@api_view(['GET'])
def get_analysis_progress(request, task_id):
    """获取分析进度"""
    with progress_lock:
        progress = analysis_progress.get(task_id)
        if progress:
            return Response({
                'success': True,
                'progress': progress
            })
        else:
            return Response({
                'success': False,
                'error': 'Task not found'
            }, status=status.HTTP_404_NOT_FOUND)


def _process_clone_and_analyze(task_id, repo_url, branch, apex_dir, force, auto_import):
    """バックグラウンドで実行される処理"""
    try:
        git_service = GitService()
        
        # 步骤1: 克隆仓库
        logger.info(f"[{task_id}] Starting clone: {repo_url}")
        update_progress(task_id, 'cloning', f'Cloning repository from {repo_url}...', 10, 100)
        clone_result = git_service.clone_repository(repo_url, branch, force)
        
        if not clone_result['success']:
            logger.error(f"[{task_id}] Clone failed: {clone_result.get('error')}")
            update_progress(task_id, 'error', f"Clone failed: {clone_result.get('error', 'Unknown error')}", 0, 100)
            return
        
        repo_name = clone_result['repo_name']
        logger.info(f"[{task_id}] Clone completed: {repo_name}")
        update_progress(task_id, 'cloned', f'Repository cloned: {repo_name}', 30, 100)
        
        # 步骤1.5: 自動検出項目結構
        logger.info(f"[{task_id}] Detecting project structure...")
        update_progress(task_id, 'detecting', 'Detecting project structure...', 35, 100)
        structure_result = git_service.detect_salesforce_structure(repo_name)
        
        # 如果检测到Apex类路径,使用检测到的路径
        if structure_result.get('success') and structure_result.get('apex_classes'):
            apex_dir = structure_result['apex_classes']['path']
            logger.info(f"[{task_id}] Auto-detected Apex path: {apex_dir}")
            update_progress(task_id, 'detected', f'Structure detected', 40, 100)
        
        # 步骤2: 分析所有组件（Apex、Visualforce、LWC）
        logger.info(f"[{task_id}] Starting analysis...")
        update_progress(task_id, 'analyzing', 'Starting analysis...', 45, 100)
        
        # 创建进度回调函数
        def progress_callback(current, total, message):
            # 45% → 80% の範囲で進捗を更新
            if total > 0:
                progress_percent = 45 + int((current / total) * 35)
            else:
                progress_percent = 45
            logger.info(f"[{task_id}] Analysis progress: {current}/{total} - {message}")
            update_progress(task_id, 'analyzing', message, progress_percent, 100)
        
        if structure_result.get('success'):
            # 使用检测到的完整项目结构
            analyze_result = git_service.analyze_all_components(repo_name, structure_result, progress_callback)
        else:
            # 如果没有检测到结构，只分析 Apex
            analyze_result = git_service.analyze_repository(repo_name, apex_dir, progress_callback)
        
        if not analyze_result['success']:
            logger.error(f"[{task_id}] Analysis failed: {analyze_result.get('error')}")
            update_progress(task_id, 'error', f"Analysis failed: {analyze_result.get('error', 'Unknown error')}", 0, 100)
            return
        
        logger.info(f"[{task_id}] Analysis complete: {analyze_result.get('analyzed', 0)} files")
        update_progress(task_id, 'analyzed', f'Analysis complete: {analyze_result.get("analyzed", 0)} files', 80, 100)
        
        # 步骤3: 自动导入（如果启用）
        if auto_import and analyze_result.get('analyzed', 0) > 0:
            logger.info(f"[{task_id}] Starting import...")
            update_progress(task_id, 'importing', 'Importing to database...', 85, 100)
            
            # インポート処理を実行
            try:
                # Repositoryオブジェクトを取得または作成
                from .models import Repository
                repo_obj, created = Repository.objects.get_or_create(
                    name=repo_name,
                    defaults={
                        'url': repo_url,
                        'branch': branch,
                        'is_active': True
                    }
                )
                if created:
                    logger.info(f"[{task_id}] Created repository: {repo_name}")
                else:
                    logger.info(f"[{task_id}] Using existing repository: {repo_name}")
                
                import_service = ASTImportService()
                
                # 各コンポーネントタイプをインポート
                import_results = []
                total_imported = 0
                
                # Apexファイルのインポート
                if analyze_result.get('apex') and analyze_result['apex'].get('success'):
                    logger.info(f"[{task_id}] Importing Apex files...")
                    for file_info in analyze_result['apex'].get('analyzed_files', []):
                        # ソースコードパスを取得（source_fileまたはinput_file）
                        source_path = file_info.get('source_file') or file_info.get('input_file')
                        result = import_service.import_ast_file(
                            file_info['output_file'], 
                            repo_obj,
                            source_code_path=source_path
                        )
                        import_results.append(result)
                        if result.get('success'):
                            total_imported += 1
                    logger.info(f"[{task_id}] Apex import: {total_imported} files")
                
                # Visualforceファイルのインポート
                if analyze_result.get('visualforce') and analyze_result['visualforce'].get('success'):
                    logger.info(f"[{task_id}] Importing Visualforce files...")
                    vf_count = 0
                    for file_info in analyze_result['visualforce'].get('analyzed_files', []):
                        source_path = file_info.get('source_file') or file_info.get('input_file')
                        result = import_service.import_ast_file(
                            file_info['output_file'], 
                            repo_obj,
                            source_code_path=source_path
                        )
                        import_results.append(result)
                        if result.get('success'):
                            vf_count += 1
                            total_imported += 1
                    logger.info(f"[{task_id}] Visualforce import: {vf_count} files")
                
                # LWCファイルのインポート
                if analyze_result.get('lwc') and analyze_result['lwc'].get('success'):
                    logger.info(f"[{task_id}] Importing LWC files...")
                    lwc_count = 0
                    for comp_info in analyze_result['lwc'].get('analyzed_components', []):
                        # LWCはASTファイルがある場合のみインポート
                        details = comp_info.get('details', {})
                        if details.get('ast_file'):
                            # LWCのソースコードパス（JavaScriptファイル）
                            source_path = details.get('js_source')
                            result = import_service.import_ast_file(
                                details['ast_file'], 
                                repo_obj,
                                source_code_path=source_path
                            )
                            import_results.append(result)
                            if result.get('success'):
                                lwc_count += 1
                                total_imported += 1
                    logger.info(f"[{task_id}] LWC import: {lwc_count} components")
                
                successful = sum(1 for r in import_results if r.get('success'))
                failed = len(import_results) - successful
                
                logger.info(f"[{task_id}] Import complete: {successful} successful, {failed} failed (total: {total_imported})")
                update_progress(task_id, 'imported', f'Import complete: {successful} files', 95, 100)
            except Exception as e:
                logger.error(f"[{task_id}] Import error: {e}", exc_info=True)
                update_progress(task_id, 'error', f'Import failed: {str(e)}', 0, 100)
                return
        
        # 完了
        logger.info(f"[{task_id}] All tasks completed")
        update_progress(task_id, 'completed', 'All tasks completed successfully', 100, 100)
        
    except Exception as e:
        logger.error(f"[{task_id}] Unexpected error: {e}", exc_info=True)
        update_progress(task_id, 'error', f'Error: {str(e)}', 0, 100)


@api_view(['POST'])
def clone_and_analyze(request):
    """克隆仓库并分析（一步完成）- バックグラウンドで実行"""
    repo_url = request.data.get('repo_url')
    branch = request.data.get('branch', 'main')
    apex_dir = request.data.get('apex_dir', 'force-app/main/default/classes')
    force = request.data.get('force', False)
    auto_import = request.data.get('auto_import', True)
    
    if not repo_url:
        return Response(
            {'error': 'repo_url is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化进度
    update_progress(task_id, 'init', 'Initializing...', 0, 100)
    logger.info(f"[{task_id}] Created task for {repo_url}")
    
    # バックグラウンドスレッドで処理を開始
    import threading
    thread = threading.Thread(
        target=_process_clone_and_analyze,
        args=(task_id, repo_url, branch, apex_dir, force, auto_import),
        daemon=True
    )
    thread.start()
    
    # すぐにtask_idを返す
    return Response({
        'success': True,
        'task_id': task_id,
        'message': 'Task started in background'
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
def detect_repository_structure(request):
    """检测仓库的Salesforce项目结构"""
    repo_name = request.data.get('repo_name')
    
    if not repo_name:
        return Response(
            {'error': 'repo_name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = git_service.detect_salesforce_structure(repo_name)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_repositories(request):
    """列出已克隆的仓库"""
    result = git_service.list_repositories()
    return Response(result)


@api_view(['DELETE'])
def delete_repository(request, repo_name):
    """删除仓库"""
    result = git_service.delete_repository(repo_name)
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def save_graph_layout(request):
    """保存图布局"""
    try:
        layout_data = request.data.get('layout', {})
        
        # 获取数据存储路径
        if settings.USE_CLOUD_STORAGE:
            import sys
            sys.path.insert(0, str(settings.BASE_DIR.parent))
            from cloud_storage import get_data_path
            graph_dir = get_data_path('graph_data')
        else:
            graph_dir = Path(settings.BASE_DIR).parent / 'graphdata' / 'graphs'
        
        graph_dir.mkdir(parents=True, exist_ok=True)
        layout_file = graph_dir / 'layout.json'
        
        # 保存布局数据
        import json
        with open(layout_file, 'w', encoding='utf-8') as f:
            json.dump(layout_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Graph layout saved to {layout_file}")
        return Response({
            'success': True,
            'message': 'Layout saved successfully'
        })
    except Exception as e:
        logger.error(f"Failed to save graph layout: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def load_graph_layout(request):
    """加载图布局"""
    try:
        # 获取数据存储路径
        if settings.USE_CLOUD_STORAGE:
            import sys
            sys.path.insert(0, str(settings.BASE_DIR.parent))
            from cloud_storage import get_data_path
            graph_dir = get_data_path('graph_data')
        else:
            graph_dir = Path(settings.BASE_DIR).parent / 'graphdata' / 'graphs'
        
        layout_file = graph_dir / 'layout.json'
        
        if not layout_file.exists():
            return Response({
                'success': False,
                'layout': None,
                'message': 'No saved layout found'
            })
        
        # 读取布局数据
        import json
        with open(layout_file, 'r', encoding='utf-8') as f:
            layout_data = json.load(f)
        
        logger.info(f"Graph layout loaded from {layout_file}")
        return Response({
            'success': True,
            'layout': layout_data
        })
    except Exception as e:
        logger.error(f"Failed to load graph layout: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    if result['success']:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


# ==========  新增：多仓库管理API  ==========

@api_view(['GET', 'POST'])
def manage_repositories(request):
    """
    GET: 获取所有仓库列表
    POST: 添加新仓库
    """
    if request.method == 'GET':
        repos = Repository.objects.all()
        serializer = RepositorySerializer(repos, many=True)
        return Response({
            'success': True,
            'repositories': serializer.data,
            'count': len(serializer.data)
        })
    
    elif request.method == 'POST':
        serializer = RepositorySerializer(data=request.data)
        if serializer.is_valid():
            # 如果设置为活动仓库,取消其他仓库的活动状态
            if serializer.validated_data.get('is_active', False):
                Repository.objects.filter(is_active=True).update(is_active=False)
            
            repo = serializer.save()
            return Response({
                'success': True,
                'repository': RepositorySerializer(repo).data,
                'message': f'Repository {repo.name} created successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def manage_repository_detail(request, repo_id):
    """
    GET: 获取仓库详情
    PUT: 更新仓库信息
    DELETE: 删除仓库
    """
    try:
        repo = Repository.objects.get(id=repo_id)
    except Repository.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = RepositorySerializer(repo)
        return Response({
            'success': True,
            'repository': serializer.data
        })
    
    elif request.method == 'PUT':
        serializer = RepositorySerializer(repo, data=request.data, partial=True)
        if serializer.is_valid():
            # 如果设置为活动仓库,取消其他仓库的活动状态
            if serializer.validated_data.get('is_active', False):
                Repository.objects.exclude(id=repo_id).update(is_active=False)
            
            repo = serializer.save()
            return Response({
                'success': True,
                'repository': RepositorySerializer(repo).data,
                'message': f'Repository {repo.name} updated successfully'
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        repo_name = repo.name
        # 删除本地文件
        local_path = Path(repo.local_path)
        if local_path.exists():
            import shutil
            from .git_service import remove_readonly
            shutil.rmtree(local_path, onerror=remove_readonly)
        
        # 删除数据库记录
        repo.delete()
        
        return Response({
            'success': True,
            'message': f'Repository {repo_name} deleted successfully'
        })


@api_view(['POST'])
def switch_active_repository(request):
    """切换当前活动仓库"""
    repo_id = request.data.get('repo_id')
    
    if not repo_id:
        return Response({
            'success': False,
            'error': 'repo_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        repo = Repository.objects.get(id=repo_id)
        
        # 取消其他仓库的活动状态
        Repository.objects.exclude(id=repo_id).update(is_active=False)
        
        # 设置当前仓库为活动状态
        repo.is_active = True
        repo.save()
        
        return Response({
            'success': True,
            'repository': RepositorySerializer(repo).data,
            'message': f'Switched to repository: {repo.name}'
        })
    except Repository.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def clone_and_register_repository(request):
    """克隆Git仓库并注册到数据库"""
    repo_url = request.data.get('repo_url')
    branch = request.data.get('branch', 'main')
    apex_dir = request.data.get('apex_dir', 'force-app/main/default/classes')
    force = request.data.get('force', False)
    auto_import = request.data.get('auto_import', True)
    set_active = request.data.get('set_active', True)
    
    if not repo_url:
        return Response({
            'success': False,
            'error': 'repo_url is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 步骤1: 克隆仓库
    clone_result = git_service.clone_repository(repo_url, branch, force)
    if not clone_result['success']:
        return Response(clone_result, status=status.HTTP_400_BAD_REQUEST)
    
    repo_name = clone_result['repo_name']
    target_dir = clone_result['target_dir']
    
    # 步骤2: 注册到数据库
    try:
        # 检查仓库是否已存在
        repo, created = Repository.objects.get_or_create(
            name=repo_name,
            defaults={
                'url': repo_url,
                'branch': branch,
                'local_path': target_dir,
                'apex_dir': apex_dir,
                'is_active': set_active
            }
        )
        
        if not created:
            # 更新现有仓库
            repo.url = repo_url
            repo.branch = branch
            repo.local_path = target_dir
            repo.apex_dir = apex_dir
            if set_active:
                Repository.objects.exclude(id=repo.id).update(is_active=False)
                repo.is_active = True
            repo.save()
        elif set_active:
            # 新建仓库时,如果设置为活动,取消其他仓库的活动状态
            Repository.objects.exclude(id=repo.id).update(is_active=False)
        
    except Exception as e:
        logger.error(f"Failed to register repository: {e}")
        return Response({
            'success': False,
            'error': f'Failed to register repository: {str(e)}',
            'clone': clone_result
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 步骤3: 分析代码
    analyze_result = git_service.analyze_repository(repo_name, apex_dir)
    
    # 步骤4: 自动导入(如果启用)
    import_result = None
    if auto_import and analyze_result.get('success') and analyze_result.get('analyzed', 0) > 0:
        if settings.USE_CLOUD_STORAGE:
            import sys
            sys.path.insert(0, str(settings.BASE_DIR.parent))
            from cloud_storage import get_data_path
            output_ast_path = get_data_path('ast') / repo_name
        else:
            output_ast_path = settings.BASE_DIR.parent / 'output' / 'ast' / repo_name
        
        if output_ast_path.exists():
            import_result = ast_import_service.import_directory(str(output_ast_path), repository=repo)
    
    return Response({
        'success': True,
        'repository': RepositorySerializer(repo).data,
        'clone': clone_result,
        'analyze': analyze_result,
        'import': import_result,
        'message': f'Repository {repo_name} {"created" if created else "updated"} successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_repository_graph_data(request, repo_id):
    """获取指定仓库的图数据"""
    try:
        repo = Repository.objects.get(id=repo_id)
    except Repository.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Repository not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    
    try:
        # 获取该仓库的图数据
        graph_data = unified_graph_service.get_repository_graph(repo.name)
        
        return Response({
            'success': True,
            'repository': {
                'id': repo.id,
                'name': repo.name
            },
            'graph': graph_data
        })
    except Exception as e:
        logger.error(f"Failed to get repository graph data: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_source_code(request, class_name):
    """获取指定类的源代码"""
    try:
        # 获取当前活动的仓库
        repo = Repository.objects.filter(is_active=True).first()
        if not repo:
            return Response({
                'success': False,
                'error': 'No active repository found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 查找AST文件记录
        ast_file = ASTFile.objects.filter(
            repository=repo,
            class_name=class_name
        ).first()
        
        if not ast_file:
            return Response({
                'success': False,
                'error': f'Class {class_name} not found in repository {repo.name}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 如果有源代码路径,读取源代码
        if ast_file.source_code_path and Path(ast_file.source_code_path).exists():
            with open(ast_file.source_code_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        else:
            # 尝试从项目目录中查找源代码
            project_dir = Path(settings.BASE_DIR.parent) / 'project' / repo.name
            possible_paths = [
                project_dir / repo.apex_dir / f'{class_name}.cls',
                project_dir / 'force-app' / 'main' / 'default' / 'classes' / f'{class_name}.cls',
            ]
            
            source_code = None
            for path in possible_paths:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                    break
            
            if not source_code:
                return Response({
                    'success': False,
                    'error': f'Source code file not found for class {class_name}'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'class_name': class_name,
            'source_code': source_code,
            'file_path': ast_file.source_code_path or '',
        })
        
    except Exception as e:
        logger.error(f"Failed to get source code: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



