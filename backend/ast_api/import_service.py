"""
AST导入服务
将解析后的AST数据导入到图数据库（Neo4j或本地）
"""
from .ast_parser import parse_ast_file
from .js_ast_parser import parse_js_ast_file
from .unified_graph_service import unified_graph_service
from .models import ASTFile, Repository
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ASTImportService:
    """AST导入服务"""
    
    def __init__(self):
        self.graph_service = unified_graph_service
    
    def import_ast_file(self, file_path, repository=None, source_code_path=None):
        """
        导入单个AST文件到图数据库
        
        Args:
            file_path: AST文件路径
            repository: Repository对象或None
            source_code_path: 源代码文件路径（可选）
        """
        try:
            file_path_obj = Path(file_path)
            
            # 检查是否是JavaScript AST（Babel生成的）
            is_javascript = False
            try:
                # 读取文件前几行来判断类型
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1000)  # 读取前1000个字符
                    if '<JavaScriptFile' in content:
                        is_javascript = True
            except:
                pass
            
            # 根据文件类型选择解析器
            if is_javascript:
                logger.info(f"Parsing JavaScript AST file: {file_path}")
                ast_data = parse_js_ast_file(file_path)
                # JavaScript组件导入
                return self._import_js_component(ast_data, file_path, repository, source_code_path)
            else:
                # Apex AST文件
                logger.info(f"Parsing Apex AST file: {file_path}")
                ast_data = parse_ast_file(file_path)
                # 导入到图数据库（自动选择 Neo4j 或本地）
                logger.info(f"Importing to graph database: {ast_data['name']}")
                self._import_to_graph(ast_data, repository)
                
                # 记录到数据库
                defaults = {
                    'class_name': ast_data['name'],
                    'file_path': str(file_path),
                }
                if source_code_path:
                    defaults['source_code_path'] = str(source_code_path)
                if repository:
                    defaults['repository'] = repository
                
                # 如果有仓库,使用仓库+文件名作为唯一标识
                if repository:
                    ast_file, created = ASTFile.objects.update_or_create(
                        repository=repository,
                        filename=Path(file_path).name,
                        defaults=defaults
                    )
                else:
                    ast_file, created = ASTFile.objects.update_or_create(
                        filename=Path(file_path).name,
                        defaults=defaults
                    )
                
                return {
                    'success': True,
                    'class_name': ast_data['name'],
                    'methods_count': len(ast_data['methods']),
                    'created': created,
                    'backend': self.graph_service.backend_type,
                    'repository': repository.name if repository else None,
                }
            
        except Exception as e:
            logger.error(f"Failed to import AST file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def import_directory(self, directory_path, repository=None):
        """
        导入目录中的所有AST文件
        
        Args:
            directory_path: 目录路径
            repository: Repository对象或None
        """
        directory = Path(directory_path)
        results = []
        
        # 检查目录是否存在
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'error': f'Directory not found: {directory}',
                'results': [],
            }
        
        if not directory.is_dir():
            logger.error(f"Path is not a directory: {directory}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'error': f'Path is not a directory: {directory}',
                'results': [],
            }
        
        # 查找所有AST文件（只导入XML格式）
        try:
            ast_files = list(directory.glob('*_ast.xml'))
        except Exception as e:
            logger.error(f"Failed to list files in {directory}: {e}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'error': f'Failed to list files: {str(e)}',
                'results': [],
            }
        
        logger.info(f"Found {len(ast_files)} AST files in {directory}")
        
        for ast_file in ast_files:
            result = self.import_ast_file(str(ast_file), repository)
            result['filename'] = ast_file.name
            results.append(result)
        
        return {
            'total': len(results),
            'successful': len([r for r in results if r['success']]),
            'failed': len([r for r in results if not r['success']]),
            'results': results,
        }
    
    def _import_to_graph(self, ast_data, repository=None):
        """
        将AST数据导入到图数据库
        
        Args:
            ast_data: AST数据
            repository: Repository对象或None
        """
        # 创建类节点
        class_data = {
            'name': ast_data['name'],
            'simpleName': ast_data['simpleName'],
            'definingType': ast_data['definingType'],
            'public': ast_data['public'],
            'withSharing': ast_data['withSharing'],
            'fileName': ast_data['fileName'],
        }
        
        # 添加仓库信息
        if repository:
            class_data['repository'] = repository.name
            class_data['repositoryId'] = repository.id
        
        # 使用统一服务创建类节点
        self.graph_service.create_class_node(class_data)
        
        # 创建方法节点和关系
        for method in ast_data['methods']:
            self._import_method(ast_data['name'], method, repository)
    
    def _import_method(self, class_name, method_data, repository=None):
        """
        导入方法及其相关信息
        
        Args:
            class_name: 类名
            method_data: 方法数据
            repository: Repository对象或None
        """
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
        
        # 添加仓库信息
        if repository:
            method_node_data['repository'] = repository.name
            method_node_data['repositoryId'] = repository.id
        
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
                
                # 添加仓库信息
                if repository:
                    soql_attrs['repository'] = repository.name
                    soql_attrs['repositoryId'] = repository.id
                
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
    
    def _import_js_component(self, ast_data, file_path, repository=None, source_code_path=None):
        """
        导入JavaScript组件到图数据库
        
        Args:
            ast_data: JavaScript AST数据
            file_path: AST文件路径
            repository: Repository对象或None
            source_code_path: 源代码文件路径（可选）
        """
        try:
            component_name = ast_data['name']
            
            # 创建LWC组件节点
            component_data = {
                'name': component_name,
                'type': ast_data.get('type', 'LWCComponent'),
            }
            
            # 添加仓库信息
            if repository:
                component_data['repository'] = repository.name
                component_data['repositoryId'] = repository.id
            
            # 使用统一服务创建组件节点
            component_node_id = f"lwc:{component_name}"
            if self.graph_service.use_local:
                component_attrs = {
                    'type': 'LWCComponent',
                    'name': component_name,
                    'componentType': ast_data.get('type', 'LWCComponent'),
                }
                
                # 添加仓库信息
                if repository:
                    component_attrs['repository'] = repository.name
                    component_attrs['repositoryId'] = repository.id
                
                self.graph_service.local_service.graph.add_node(component_node_id, **component_attrs)
                self.graph_service.local_service._save_entity(component_node_id, component_attrs)
            
            # 导入imports（依赖关系）
            for import_item in ast_data.get('imports', []):
                source = import_item.get('source', '')
                specifiers = import_item.get('specifiers', [])
                
                # 检查是否是Apex依赖
                apex_dependency = import_item.get('apex_dependency')
                if apex_dependency:
                    # 创建到Apex类和方法的关系
                    self._create_apex_relationships(component_node_id, apex_dependency, repository)
                else:
                    # 创建普通依赖关系
                    if source:
                        # 创建依赖节点
                        dep_node_id = f"dep:{source}"
                        if self.graph_service.use_local:
                            dep_attrs = {
                                'type': 'Dependency',
                                'module': source,
                                'specifiers': ', '.join(specifiers) if specifiers else 'default',
                            }
                            
                            # 添加仓库信息
                            if repository:
                                dep_attrs['repository'] = repository.name
                                dep_attrs['repositoryId'] = repository.id
                            
                            self.graph_service.local_service.graph.add_node(dep_node_id, **dep_attrs)
                            self.graph_service.local_service._save_entity(dep_node_id, dep_attrs)
                        
                        # 创建组件到依赖的关系
                        self.graph_service.create_relationship(
                            component_node_id,
                            dep_node_id,
                            'IMPORTS_FROM',
                            {
                                'module': source,
                                'specifiers': ', '.join(specifiers) if specifiers else 'default'
                            }
                        )
            
            # 导入classes
            for cls in ast_data.get('classes', []):
                class_name = cls['name']
                class_node_id = f"jsclass:{component_name}.{class_name}"
                
                if self.graph_service.use_local:
                    class_attrs = {
                        'type': 'JavaScriptClass',
                        'name': class_name,
                        'componentName': component_name,
                        'superClass': cls.get('superClass', ''),
                    }
                    
                    # 添加仓库信息
                    if repository:
                        class_attrs['repository'] = repository.name
                        class_attrs['repositoryId'] = repository.id
                    
                    self.graph_service.local_service.graph.add_node(class_node_id, **class_attrs)
                    self.graph_service.local_service._save_entity(class_node_id, class_attrs)
                
                # 创建组件到类的关系
                self.graph_service.create_relationship(
                    component_node_id,
                    class_node_id,
                    'HAS_CLASS',
                    {'className': class_name}
                )
                
                # 导入类的方法
                for method in cls.get('methods', []):
                    self._import_js_method(component_name, class_name, method, repository)
            
            # 导入独立functions（不在类中的）
            for func in ast_data.get('functions', []):
                func_name = func['name']
                func_node_id = f"jsfunc:{component_name}.{func_name}"
                
                if self.graph_service.use_local:
                    func_attrs = {
                        'type': 'JavaScriptFunction',
                        'name': func_name,
                        'componentName': component_name,
                        'async': func.get('async', False),
                        'params': ', '.join(func.get('parameters', [])),
                    }
                    
                    # 添加仓库信息
                    if repository:
                        func_attrs['repository'] = repository.name
                        func_attrs['repositoryId'] = repository.id
                    
                    self.graph_service.local_service.graph.add_node(func_node_id, **func_attrs)
                    self.graph_service.local_service._save_entity(func_node_id, func_attrs)
                
                # 创建组件到函数的关系
                self.graph_service.create_relationship(
                    component_node_id,
                    func_node_id,
                    'HAS_FUNCTION',
                    {'functionName': func_name}
                )
            
            # 记录到数据库
            defaults = {
                'class_name': component_name,
                'file_path': str(file_path),
            }
            if source_code_path:
                defaults['source_code_path'] = str(source_code_path)
            if repository:
                defaults['repository'] = repository
            
            # 如果有仓库,使用仓库+文件名作为唯一标识
            if repository:
                ast_file, created = ASTFile.objects.update_or_create(
                    repository=repository,
                    filename=Path(file_path).name,
                    defaults=defaults
                )
            else:
                ast_file, created = ASTFile.objects.update_or_create(
                    filename=Path(file_path).name,
                    defaults=defaults
                )
            
            # 统计方法数量（包括类方法和独立函数）
            methods_count = sum(len(cls.get('methods', [])) for cls in ast_data.get('classes', []))
            methods_count += len(ast_data.get('functions', []))
            
            return {
                'success': True,
                'class_name': component_name,
                'methods_count': methods_count,
                'created': created,
                'backend': self.graph_service.backend_type,
                'repository': repository.name if repository else None,
                'component_type': 'LWCComponent',
            }
            
        except Exception as e:
            logger.error(f"Failed to import JavaScript component: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def _import_js_method(self, component_name, class_name, method_data, repository=None):
        """
        导入JavaScript方法
        
        Args:
            component_name: 组件名
            class_name: 类名
            method_data: 方法数据
            repository: Repository对象或None
        """
        method_name = method_data['name']
        method_node_id = f"jsmethod:{component_name}.{class_name}.{method_name}"
        
        if self.graph_service.use_local:
            method_attrs = {
                'type': 'JavaScriptMethod',
                'name': method_name,
                'className': class_name,
                'componentName': component_name,
                'kind': method_data.get('kind', 'method'),  # constructor, method, get, set
                'async': method_data.get('async', False),
                'static': method_data.get('static', False),
                'params': ', '.join(method_data.get('parameters', [])),
            }
            
            # 添加仓库信息
            if repository:
                method_attrs['repository'] = repository.name
                method_attrs['repositoryId'] = repository.id
            
            self.graph_service.local_service.graph.add_node(method_node_id, **method_attrs)
            self.graph_service.local_service._save_entity(method_node_id, method_attrs)
        
        # 创建类到方法的关系
        class_node_id = f"jsclass:{component_name}.{class_name}"
        self.graph_service.create_relationship(
            class_node_id,
            method_node_id,
            'HAS_METHOD',
            {
                'methodName': method_name,
                'kind': method_data.get('kind', 'method')
            }
        )
    
    def _create_apex_relationships(self, lwc_component_id, apex_dependency, repository=None):
        """
        创建LWC组件到Apex类和方法的关系
        
        Args:
            lwc_component_id: LWC组件节点ID
            apex_dependency: Apex依赖信息
            repository: Repository对象或None
        """
        apex_class_name = apex_dependency.get('class_name')
        apex_method_name = apex_dependency.get('method_name')
        
        if not apex_class_name:
            return
        
        # 创建到Apex类的关系
        apex_class_node_id = f"class:{apex_class_name}"
        
        # 检查Apex类节点是否存在
        if self.graph_service.use_local and self.graph_service.local_service.graph.has_node(apex_class_node_id):
            # 创建LWC组件到Apex类的依赖关系
            self.graph_service.create_relationship(
                lwc_component_id,
                apex_class_node_id,
                'DEPENDS_ON_APEX_CLASS',
                {
                    'apexClass': apex_class_name,
                    'importPath': apex_dependency.get('full_path', ''),
                    'description': f'LWC component imports from Apex class {apex_class_name}'
                }
            )
            
            logger.info(f"Created relationship: {lwc_component_id} -> {apex_class_node_id} [DEPENDS_ON_APEX_CLASS]")
        else:
            # Apex类不存在，创建占位符节点
            logger.warning(f"Apex class {apex_class_name} not found in graph, creating placeholder")
            
            if self.graph_service.use_local:
                placeholder_attrs = {
                    'type': 'ApexClassPlaceholder',
                    'name': apex_class_name,
                    'placeholder': True,
                    'reason': 'Referenced by LWC but not yet imported',
                }
                
                # 添加仓库信息
                if repository:
                    placeholder_attrs['repository'] = repository.name
                    placeholder_attrs['repositoryId'] = repository.id
                
                self.graph_service.local_service.graph.add_node(apex_class_node_id, **placeholder_attrs)
                self.graph_service.local_service._save_entity(apex_class_node_id, placeholder_attrs)
                
                # 创建关系
                self.graph_service.create_relationship(
                    lwc_component_id,
                    apex_class_node_id,
                    'DEPENDS_ON_APEX_CLASS',
                    {
                        'apexClass': apex_class_name,
                        'importPath': apex_dependency.get('full_path', ''),
                        'placeholder': True
                    }
                )
        
        # 如果有方法名，创建到Apex方法的关系
        if apex_method_name:
            apex_method_node_id = f"method:{apex_class_name}.{apex_method_name}"
            
            # 检查Apex方法节点是否存在
            if self.graph_service.use_local and self.graph_service.local_service.graph.has_node(apex_method_node_id):
                # 创建LWC组件到Apex方法的依赖关系
                self.graph_service.create_relationship(
                    lwc_component_id,
                    apex_method_node_id,
                    'CALLS_APEX_METHOD',
                    {
                        'apexClass': apex_class_name,
                        'apexMethod': apex_method_name,
                        'importPath': apex_dependency.get('full_path', ''),
                        'description': f'LWC component calls Apex method {apex_class_name}.{apex_method_name}'
                    }
                )
                
                logger.info(f"Created relationship: {lwc_component_id} -> {apex_method_node_id} [CALLS_APEX_METHOD]")
            else:
                # Apex方法不存在，创建占位符节点
                logger.warning(f"Apex method {apex_class_name}.{apex_method_name} not found in graph, creating placeholder")
                
                if self.graph_service.use_local:
                    method_placeholder_attrs = {
                        'type': 'ApexMethodPlaceholder',
                        'name': apex_method_name,
                        'className': apex_class_name,
                        'canonicalName': f"{apex_class_name}.{apex_method_name}",
                        'placeholder': True,
                        'reason': 'Referenced by LWC but not yet imported',
                    }
                    
                    # 添加仓库信息
                    if repository:
                        method_placeholder_attrs['repository'] = repository.name
                        method_placeholder_attrs['repositoryId'] = repository.id
                    
                    self.graph_service.local_service.graph.add_node(apex_method_node_id, **method_placeholder_attrs)
                    self.graph_service.local_service._save_entity(apex_method_node_id, method_placeholder_attrs)
                    
                    # 创建关系
                    self.graph_service.create_relationship(
                        lwc_component_id,
                        apex_method_node_id,
                        'CALLS_APEX_METHOD',
                        {
                            'apexClass': apex_class_name,
                            'apexMethod': apex_method_name,
                            'importPath': apex_dependency.get('full_path', ''),
                            'placeholder': True
                        }
                    )


# 全局服务实例
ast_import_service = ASTImportService()
