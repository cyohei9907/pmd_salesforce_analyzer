"""
AST XML解析器
解析PMD生成的AST XML文件并提取关键信息
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ASTParser:
    """AST XML解析器"""
    
    def __init__(self, ast_file_path):
        self.file_path = Path(ast_file_path)
        self.tree = None
        self.root = None
        self.class_data = {}
        
    def parse(self):
        """解析AST文件"""
        try:
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
            
            # 提取类信息
            self.class_data = self._extract_class_info()
            
            # 提取方法信息
            self.class_data['methods'] = self._extract_methods()
            
            return self.class_data
            
        except Exception as e:
            logger.error(f"Failed to parse AST file {self.file_path}: {e}")
            raise
    
    def _extract_class_info(self):
        """提取类基本信息"""
        user_class = self.root.find('.//UserClass')
        if not user_class:
            raise ValueError("No UserClass found in AST")
        
        class_modifier = user_class.find('ModifierNode')
        
        return {
            'name': user_class.get('SimpleName', 'Unknown'),
            'simpleName': user_class.get('SimpleName', 'Unknown'),
            'definingType': user_class.get('DefiningType', ''),
            'public': class_modifier.get('Public', 'false') == 'true' if class_modifier else False,
            'withSharing': class_modifier.get('WithSharing', 'false') == 'true' if class_modifier else False,
            'fileName': self.file_path.name,
            'nested': user_class.get('Nested', 'false') == 'true',
            'superClassName': user_class.get('SuperClassName', ''),
        }
    
    def _extract_methods(self):
        """提取所有方法信息"""
        methods = []
        method_nodes = self.root.findall('.//Method')
        
        for method in method_nodes:
            method_data = self._extract_method_info(method)
            methods.append(method_data)
        
        return methods
    
    def _extract_method_info(self, method_node):
        """提取单个方法的详细信息"""
        method_modifier = method_node.find('ModifierNode')
        
        method_data = {
            'canonicalName': method_node.get('CanonicalName', 'Unknown'),
            'name': method_node.get('CanonicalName', 'Unknown'),
            'returnType': method_node.get('ReturnType', 'void'),
            'arity': int(method_node.get('Arity', '0')),
            'constructor': method_node.get('Constructor', 'false') == 'true',
            'public': False,
            'static': False,
            'annotations': [],
        }
        
        if method_modifier:
            method_data['public'] = method_modifier.get('Public', 'false') == 'true'
            method_data['static'] = method_modifier.get('Static', 'false') == 'true'
            method_data['private'] = method_modifier.get('Private', 'false') == 'true'
            
            # 提取注解
            annotations = method_modifier.findall('Annotation')
            method_data['annotations'] = [ann.get('Name', '') for ann in annotations]
        
        # 提取SOQL查询
        method_data['soql_queries'] = self._extract_soql_queries(method_node)
        
        # 提取DML操作
        method_data['dml_operations'] = self._extract_dml_operations(method_node)
        
        # 提取方法调用
        method_data['method_calls'] = self._extract_method_calls(method_node)
        
        return method_data
    
    def _extract_soql_queries(self, parent_node):
        """提取SOQL查询"""
        soql_queries = []
        soql_nodes = parent_node.findall('.//SoqlExpression')
        
        for soql in soql_nodes:
            soql_queries.append({
                'query': soql.get('Query', ''),
                'canonicalQuery': soql.get('CanonicalQuery', ''),
            })
        
        return soql_queries
    
    def _extract_dml_operations(self, parent_node):
        """提取DML操作"""
        dml_operations = []
        
        dml_types = {
            'DmlInsertStatement': 'INSERT',
            'DmlUpdateStatement': 'UPDATE',
            'DmlDeleteStatement': 'DELETE',
            'DmlUpsertStatement': 'UPSERT',
            'DmlMergeStatement': 'MERGE',
            'DmlUndeleteStatement': 'UNDELETE',
        }
        
        for dml_tag, dml_type in dml_types.items():
            dml_nodes = parent_node.findall(f'.//{dml_tag}')
            for dml in dml_nodes:
                dml_operations.append({
                    'type': dml_type,
                    'tag': dml_tag,
                })
        
        return dml_operations
    
    def _extract_method_calls(self, parent_node):
        """提取方法调用"""
        method_calls = []
        call_nodes = parent_node.findall('.//MethodCallExpression')
        
        for call in call_nodes:
            method_calls.append({
                'methodName': call.get('MethodName', ''),
                'fullMethodName': call.get('FullMethodName', ''),
            })
        
        return method_calls


def parse_ast_file(file_path):
    """便捷函数：解析AST文件"""
    parser = ASTParser(file_path)
    return parser.parse()
