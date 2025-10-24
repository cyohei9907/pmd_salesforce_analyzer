"""
AST导入服务
将解析后的AST数据导入到图数据库（Neo4j或本地）
"""
from .ast_parser import parse_ast_file
from .unified_graph_service import unified_graph_service
from .models import ASTFile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ASTImportService:
    """AST导入服务"""
    
    def __init__(self):
        self.graph_service = unified_graph_service
    
    def import_ast_file(self, file_path):
        """导入单个AST文件到图数据库"""
        try:
            # 解析AST文件
            logger.info(f"Parsing AST file: {file_path}")
            ast_data = parse_ast_file(file_path)
            
            # 导入到图数据库（自动选择 Neo4j 或本地）
            logger.info(f"Importing to graph database: {ast_data['name']}")
            self._import_to_graph(ast_data)
            
            # 记录到数据库
            ast_file, created = ASTFile.objects.update_or_create(
                filename=Path(file_path).name,
                defaults={
                    'class_name': ast_data['name'],
                    'file_path': str(file_path),
                }
            )
            
            return {
                'success': True,
                'class_name': ast_data['name'],
                'methods_count': len(ast_data['methods']),
                'created': created,
                'backend': self.graph_service.backend_type,
            }
            
        except Exception as e:
            logger.error(f"Failed to import AST file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def import_directory(self, directory_path):
        """导入目录中的所有AST文件"""
        directory = Path(directory_path)
        results = []
        
        # 查找所有AST文件
        ast_files = list(directory.glob('*_ast.txt')) + list(directory.glob('*_ast.xml'))
        
        logger.info(f"Found {len(ast_files)} AST files in {directory}")
        
        for ast_file in ast_files:
            result = self.import_ast_file(str(ast_file))
            result['filename'] = ast_file.name
            results.append(result)
        
        return {
            'total': len(results),
            'successful': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results,
        }
    
    def _import_to_graph(self, ast_data):
        """将AST数据导入到图数据库"""
        # 创建类节点
        class_data = {
            'name': ast_data['name'],
            'simpleName': ast_data['simpleName'],
            'definingType': ast_data['definingType'],
            'public': ast_data['public'],
            'withSharing': ast_data['withSharing'],
            'fileName': ast_data['fileName'],
        }
        
        # 使用统一服务创建类节点
        self.graph_service.create_class_node(class_data)
        
        # 创建方法节点和关系
        for method in ast_data['methods']:
            self._import_method(ast_data['name'], method)
    
    def _import_method(self, class_name, method_data):
        """导入方法及其相关信息"""
        # 创建方法节点
        method_node_data = {
            'canonicalName': f"{class_name}.{method_data['name']}",
            'className': class_name,
            'name': method_data['name'],
            'returnType': method_data['returnType'],
            'arity': method_data['arity'],
            'public': method_data['public'],
            'static': method_data['static'],
            'constructor': method_data['constructor'],
        }
        
        # 创建方法节点
        self.graph_service.create_method_node(method_node_data)
        
        # 创建类和方法的关系
        class_node_id = f"class:{class_name}"
        method_node_id = f"method:{method_node_data['canonicalName']}"
        self.graph_service.create_relationship(
            class_node_id,
            method_node_id,
            'HAS_METHOD',
            {'description': 'Class contains method'}
        )
        
        # 导入SOQL查询
        for idx, soql in enumerate(method_data.get('soql_queries', [])):
            soql_node_id = f"soql:{class_name}.{method_data['name']}.{idx}"
            
            # 创建SOQL节点（在本地图中）
            if self.graph_service.use_local:
                soql_attrs = {
                    'type': 'SOQLQuery',
                    'query': soql['query'],
                    'canonicalQuery': soql.get('canonicalQuery', soql['query']),
                    'className': class_name,
                    'methodName': method_data['name'],
                }
                self.graph_service.local_service.graph.add_node(soql_node_id, **soql_attrs)
                self.graph_service.local_service._save_entity(soql_node_id, soql_attrs)
            
            # 创建方法和SOQL的关系
            self.graph_service.create_relationship(
                method_node_id,
                soql_node_id,
                'CONTAINS_SOQL',
                {'query': soql['query']}
            )
        
        # 导入DML操作
        for idx, dml in enumerate(method_data.get('dml_operations', [])):
            dml_node_id = f"dml:{class_name}.{method_data['name']}.{dml['type']}.{idx}"
            
            # 创建DML节点（在本地图中）
            if self.graph_service.use_local:
                dml_attrs = {
                    'type': 'DMLOperation',
                    'className': class_name,
                    'methodName': method_data['name'],
                    'operationType': dml['type'],
                }
                self.graph_service.local_service.graph.add_node(dml_node_id, **dml_attrs)
                self.graph_service.local_service._save_entity(dml_node_id, dml_attrs)
            
            # 创建方法和DML的关系
            self.graph_service.create_relationship(
                method_node_id,
                dml_node_id,
                'CONTAINS_DML',
                {'operationType': dml['type']}
            )


# 全局服务实例
ast_import_service = ASTImportService()
