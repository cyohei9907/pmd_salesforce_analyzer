"""
REST API视图
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .import_service import ast_import_service
from .unified_graph_service import unified_graph_service
from .models import ASTFile
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


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
            else:
                node_obj['name'] = 'Unknown'
            
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
    """列出所有已导入的文件"""
    files = ASTFile.objects.all()
    data = [{
        'id': f.id,
        'filename': f.filename,
        'class_name': f.class_name,
        'imported_at': f.imported_at,
        'file_path': f.file_path,
    } for f in files]
    
    return Response(data)


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
