"""
AST分析工具
用于分析PMD生成的Apex AST文件
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
import json


def analyze_ast_file(ast_file_path: str) -> Dict:
    """
    分析单个AST文件并提取关键信息
    
    Args:
        ast_file_path: AST文件路径
    
    Returns:
        包含分析结果的字典
    """
    try:
        tree = ET.parse(ast_file_path)
        root = tree.getroot()
        
        # 提取类信息
        user_class = root.find('.//UserClass')
        class_name = user_class.get('SimpleName') if user_class else 'Unknown'
        
        # 获取修饰符
        class_modifier = user_class.find('ModifierNode') if user_class else None
        is_public = class_modifier.get('Public') == 'true' if class_modifier else False
        is_with_sharing = class_modifier.get('WithSharing') == 'true' if class_modifier else False
        
        # 统计方法
        methods = root.findall('.//Method')
        method_info = []
        for method in methods:
            method_name = method.get('CanonicalName', 'Unknown')
            return_type = method.get('ReturnType', 'void')
            arity = method.get('Arity', '0')
            
            # 检查方法修饰符
            method_modifier = method.find('ModifierNode')
            is_static = method_modifier.get('Static') == 'true' if method_modifier else False
            is_public_method = method_modifier.get('Public') == 'true' if method_modifier else False
            
            # 检查是否有注解
            annotations = method_modifier.findall('Annotation') if method_modifier else []
            annotation_names = [ann.get('Name') for ann in annotations]
            
            method_info.append({
                'name': method_name,
                'return_type': return_type,
                'parameters': int(arity),
                'static': is_static,
                'public': is_public_method,
                'annotations': annotation_names
            })
        
        # 统计SOQL查询
        soql_queries = root.findall('.//SoqlExpression')
        soql_info = []
        for soql in soql_queries:
            query = soql.get('Query', '')
            soql_info.append(query)
        
        # 统计DML操作
        dml_operations = {
            'insert': len(root.findall('.//DmlInsertStatement')),
            'update': len(root.findall('.//DmlUpdateStatement')),
            'delete': len(root.findall('.//DmlDeleteStatement')),
            'upsert': len(root.findall('.//DmlUpsertStatement')),
            'merge': len(root.findall('.//DmlMergeStatement')),
            'undelete': len(root.findall('.//DmlUndeleteStatement'))
        }
        
        # 统计变量声明
        variable_declarations = len(root.findall('.//VariableDeclaration'))
        
        # 统计方法调用
        method_calls = root.findall('.//MethodCallExpression')
        method_call_names = []
        for call in method_calls:
            call_name = call.get('MethodName', '')
            if call_name:
                method_call_names.append(call_name)
        
        return {
            'file': Path(ast_file_path).name,
            'class_name': class_name,
            'public': is_public,
            'with_sharing': is_with_sharing,
            'method_count': len(methods),
            'methods': method_info,
            'soql_count': len(soql_queries),
            'soql_queries': soql_info,
            'dml_operations': dml_operations,
            'total_dml': sum(dml_operations.values()),
            'variable_count': variable_declarations,
            'method_call_count': len(method_calls),
            'top_method_calls': list(set(method_call_names))[:10],
            'success': True
        }
        
    except Exception as e:
        return {
            'file': Path(ast_file_path).name,
            'success': False,
            'error': str(e)
        }


def analyze_all_ast_files(ast_directory: str) -> List[Dict]:
    """
    分析目录中的所有AST文件
    
    Args:
        ast_directory: AST文件目录
    
    Returns:
        分析结果列表
    """
    ast_dir = Path(ast_directory)
    results = []
    
    for ast_file in sorted(ast_dir.glob('*_ast.txt')):
        print(f"正在分析: {ast_file.name}")
        result = analyze_ast_file(str(ast_file))
        results.append(result)
    
    return results


def print_analysis_summary(results: List[Dict]):
    """
    打印分析摘要
    
    Args:
        results: 分析结果列表
    """
    print("\n" + "=" * 80)
    print("AST分析摘要报告")
    print("=" * 80)
    
    successful = [r for r in results if r.get('success', False)]
    failed = [r for r in results if not r.get('success', False)]
    
    print(f"\n总文件数: {len(results)}")
    print(f"成功分析: {len(successful)}")
    print(f"失败: {len(failed)}")
    
    if successful:
        print("\n" + "-" * 80)
        print("详细统计:")
        print("-" * 80)
        
        # 表头
        print(f"{'类名':<30} {'方法':<6} {'SOQL':<6} {'DML':<6} {'变量':<6}")
        print("-" * 80)
        
        # 每个类的统计
        for result in successful:
            class_name = result['class_name'][:28]
            method_count = result['method_count']
            soql_count = result['soql_count']
            dml_count = result['total_dml']
            var_count = result['variable_count']
            
            print(f"{class_name:<30} {method_count:<6} {soql_count:<6} {dml_count:<6} {var_count:<6}")
        
        # 总计
        print("-" * 80)
        total_methods = sum(r['method_count'] for r in successful)
        total_soql = sum(r['soql_count'] for r in successful)
        total_dml = sum(r['total_dml'] for r in successful)
        total_vars = sum(r['variable_count'] for r in successful)
        
        print(f"{'总计':<30} {total_methods:<6} {total_soql:<6} {total_dml:<6} {total_vars:<6}")
        
        # 详细方法信息
        print("\n" + "-" * 80)
        print("公开方法详情:")
        print("-" * 80)
        
        for result in successful:
            public_methods = [m for m in result['methods'] if m['public']]
            if public_methods:
                print(f"\n{result['class_name']}:")
                for method in public_methods:
                    annotations = f" @{', @'.join(method['annotations'])}" if method['annotations'] else ""
                    static = "static " if method['static'] else ""
                    print(f"  - {static}{method['return_type']} {method['name']}({method['parameters']}个参数){annotations}")
        
        # SOQL查询
        print("\n" + "-" * 80)
        print("SOQL查询详情:")
        print("-" * 80)
        
        for result in successful:
            if result['soql_queries']:
                print(f"\n{result['class_name']}:")
                for i, query in enumerate(result['soql_queries'], 1):
                    # 格式化查询，限制长度
                    query_display = query[:70] + '...' if len(query) > 70 else query
                    print(f"  {i}. {query_display}")
    
    if failed:
        print("\n" + "-" * 80)
        print("分析失败的文件:")
        print("-" * 80)
        for result in failed:
            print(f"  - {result['file']}: {result.get('error', 'Unknown error')}")


def save_analysis_to_json(results: List[Dict], output_file: str):
    """
    将分析结果保存为JSON文件
    
    Args:
        results: 分析结果列表
        output_file: 输出文件路径
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n分析结果已保存到: {output_file}")


if __name__ == "__main__":
    # AST文件目录
    ast_directory = Path(__file__).parent / "output" / "ast"
    
    print("开始分析AST文件...")
    print(f"AST目录: {ast_directory}\n")
    
    # 分析所有AST文件
    results = analyze_all_ast_files(str(ast_directory))
    
    # 打印摘要
    print_analysis_summary(results)
    
    # 保存到JSON
    output_json = Path(__file__).parent / "output" / "ast_analysis.json"
    save_analysis_to_json(results, str(output_json))
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)
