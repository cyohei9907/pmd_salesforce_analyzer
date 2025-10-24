"""
AST导入服务
将解析后的AST数据导入到Neo4j图数据库
"""
from .ast_parser import parse_ast_file
from .neo4j_service import neo4j_service
from .models import ASTFile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ASTImportService:
    """AST导入服务"""
    
    def __init__(self):
        self.neo4j = neo4j_service
    
    def import_ast_file(self, file_path):
        """导入单个AST文件到图数据库"""
        try:
            # 解析AST文件
            logger.info(f"Parsing AST file: {file_path}")
            ast_data = parse_ast_file(file_path)
            
            # 导入到Neo4j
            logger.info(f"Importing to Neo4j: {ast_data['name']}")
            self._import_to_neo4j(ast_data)
            
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
    
    def _import_to_neo4j(self, ast_data):
        """将AST数据导入到Neo4j"""
        with self.neo4j.driver.session() as session:
            # 创建类节点
            class_data = {
                'name': ast_data['name'],
                'simpleName': ast_data['simpleName'],
                'definingType': ast_data['definingType'],
                'public': ast_data['public'],
                'withSharing': ast_data['withSharing'],
                'fileName': ast_data['fileName'],
            }
            session.execute_write(self.neo4j.create_class_node, class_data)
            
            # 创建方法节点和关系
            for method in ast_data['methods']:
                self._import_method(session, ast_data['name'], method)
    
    def _import_method(self, session, class_name, method_data):
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
        session.execute_write(self.neo4j.create_method_node, method_node_data)
        
        # 创建类和方法的关系
        session.execute_write(
            self.neo4j.create_relationship,
            'ApexClass', 'name', class_name,
            'Method', 'canonicalName', method_node_data['canonicalName'],
            'HAS_METHOD'
        )
        
        # 导入SOQL查询
        for soql in method_data.get('soql_queries', []):
            soql_data = {
                'query': soql['query'],
                'canonicalQuery': soql.get('canonicalQuery', soql['query']),
                'className': class_name,
                'methodName': method_data['name'],
            }
            session.execute_write(self.neo4j.create_soql_node, soql_data)
            
            # 创建方法和SOQL的关系
            session.execute_write(
                self.neo4j.create_relationship,
                'Method', 'canonicalName', method_node_data['canonicalName'],
                'SOQLQuery', 'query', soql['query'],
                'CONTAINS_SOQL'
            )
        
        # 导入DML操作
        for idx, dml in enumerate(method_data.get('dml_operations', [])):
            dml_data = {
                'type': f"{dml['type']}_{idx}",
                'className': class_name,
                'methodName': method_data['name'],
                'operationType': dml['type'],
            }
            session.execute_write(self.neo4j.create_dml_node, dml_data)
            
            # 创建方法和DML的关系
            session.execute_write(
                self.neo4j.create_relationship,
                'Method', 'canonicalName', method_node_data['canonicalName'],
                'DMLOperation', 'type', dml_data['type'],
                'CONTAINS_DML'
            )


# 全局服务实例
ast_import_service = ASTImportService()
