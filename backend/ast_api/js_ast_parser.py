"""
JavaScript AST Parser
Parse Babel-generated JavaScript AST XML files
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class JavaScriptASTParser:
    """JavaScript AST XML Parser"""
    
    def __init__(self, ast_file_path):
        self.file_path = Path(ast_file_path)
        self.tree = None
        self.root = None
        self.component_data = {}
        
    def parse(self):
        """Parse JavaScript AST file"""
        try:
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
            
            # Extract component info
            self.component_data = self._extract_component_info()
            
            # Extract imports
            self.component_data['imports'] = self._extract_imports()
            
            # Extract exports
            self.component_data['exports'] = self._extract_exports()
            
            # Extract classes
            self.component_data['classes'] = self._extract_classes()
            
            # Extract functions
            self.component_data['functions'] = self._extract_functions()
            
            return self.component_data
            
        except Exception as e:
            logger.error(f"Failed to parse JavaScript AST file {self.file_path}: {e}")
            raise
    
    def _extract_component_info(self):
        """Extract basic component information"""
        return {
            'name': self.root.get('name', 'Unknown').replace('.js', ''),
            'type': 'LWCComponent',
            'fileName': self.file_path.name,
        }
    
    def _extract_imports(self):
        """Extract import statements"""
        imports = []
        imports_elem = self.root.find('Imports')
        
        if imports_elem is not None:
            for imp in imports_elem.findall('Import'):
                import_info = {
                    'source': imp.get('source', ''),
                    'specifiers': []
                }
                
                # 提取specifier的名称（imported或local）
                for spec in imp.findall('Specifier'):
                    imported = spec.get('imported', '')
                    local = spec.get('local', '')
                    # 使用local名称（如果不同）或imported名称
                    name = local if local else imported
                    if name:
                        import_info['specifiers'].append(name)
                
                # 检测Apex依赖关系
                source = import_info['source']
                if source.startswith('@salesforce/apex/'):
                    import_info['apex_dependency'] = self._parse_apex_import(source, import_info['specifiers'])
                
                imports.append(import_info)
        
        return imports
    
    def _parse_apex_import(self, source, specifiers):
        """
        解析Apex导入，提取类名和方法名
        例如: '@salesforce/apex/PropertyController.getPagedPropertyList'
        """
        apex_info = {
            'type': 'apex',
            'class_name': None,
            'method_name': None,
            'full_path': source
        }
        
        # 移除 @salesforce/apex/ 前缀
        apex_path = source.replace('@salesforce/apex/', '')
        
        # 解析类名和方法名
        if '.' in apex_path:
            parts = apex_path.split('.')
            apex_info['class_name'] = parts[0]
            if len(parts) > 1:
                apex_info['method_name'] = parts[1]
        else:
            apex_info['class_name'] = apex_path
        
        return apex_info
    
    def _extract_exports(self):
        """Extract export statements"""
        exports = []
        exports_elem = self.root.find('Exports')
        
        if exports_elem is not None:
            for exp in exports_elem.findall('Export'):
                exports.append({
                    'type': exp.get('type', ''),
                    'name': exp.get('name', '')
                })
        
        return exports
    
    def _extract_classes(self):
        """Extract class definitions"""
        classes = []
        classes_elem = self.root.find('Classes')
        
        if classes_elem is not None:
            for cls in classes_elem.findall('Class'):
                class_info = {
                    'name': cls.get('name', ''),
                    'superClass': cls.get('superClass', ''),
                    'properties': [],
                    'methods': []
                }
                
                # Extract properties
                properties_elem = cls.find('Properties')
                if properties_elem is not None:
                    for prop in properties_elem.findall('Property'):
                        class_info['properties'].append({
                            'name': prop.get('name', ''),
                            'static': prop.get('static', 'false') == 'true'
                        })
                
                # Extract methods
                methods_elem = cls.find('Methods')
                if methods_elem is not None:
                    for method in methods_elem.findall('Method'):
                        method_info = {
                            'name': method.get('name', ''),
                            'kind': method.get('kind', 'method'),
                            'async': method.get('async', 'false') == 'true',
                            'static': method.get('static', 'false') == 'true',
                            'parameters': []
                        }
                        
                        # Extract parameters
                        params_elem = method.find('Parameters')
                        if params_elem is not None:
                            for param in params_elem.findall('Parameter'):
                                method_info['parameters'].append(param.get('name', ''))
                        
                        class_info['methods'].append(method_info)
                
                classes.append(class_info)
        
        return classes
    
    def _extract_functions(self):
        """Extract function definitions"""
        functions = []
        functions_elem = self.root.find('Functions')
        
        if functions_elem is not None:
            for func in functions_elem.findall('Function'):
                func_info = {
                    'name': func.get('name', ''),
                    'async': func.get('async', 'false') == 'true',
                    'parameters': []
                }
                
                # Extract parameters
                params_elem = func.find('Parameters')
                if params_elem is not None:
                    for param in params_elem.findall('Parameter'):
                        func_info['parameters'].append(param.get('name', ''))
                
                functions.append(func_info)
        
        return functions


def parse_js_ast_file(file_path):
    """
    Parse JavaScript AST XML file
    
    Args:
        file_path: Path to JavaScript AST XML file
        
    Returns:
        Dictionary containing parsed component data
    """
    parser = JavaScriptASTParser(file_path)
    return parser.parse()
