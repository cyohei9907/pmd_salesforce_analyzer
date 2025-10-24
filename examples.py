#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AST使用示例脚本
展示如何使用生成的AST数据进行各种分析
"""

import json
from pathlib import Path
import xml.etree.ElementTree as ET


def example_1_load_analysis_data():
    """示例1: 加载并查看分析数据"""
    print("=" * 80)
    print("示例1: 加载分析数据")
    print("=" * 80)
    
    json_file = Path(__file__).parent / "output" / "ast_analysis.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n总类数: {len(data)}")
    
    for item in data[:3]:  # 显示前3个
        print(f"\n类名: {item['class_name']}")
        print(f"  方法数: {item['method_count']}")
        print(f"  SOQL数: {item['soql_count']}")
        print(f"  DML数: {item['total_dml']}")


def example_2_find_aura_enabled_methods():
    """示例2: 查找所有@AuraEnabled方法"""
    print("\n" + "=" * 80)
    print("示例2: 查找@AuraEnabled方法（Lightning可调用）")
    print("=" * 80 + "\n")
    
    json_file = Path(__file__).parent / "output" / "ast_analysis.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    aura_methods = []
    for item in data:
        for method in item.get('methods', []):
            if 'AuraEnabled' in method.get('annotations', []):
                aura_methods.append({
                    'class': item['class_name'],
                    'method': method['name'],
                    'params': method['parameters'],
                    'return': method['return_type'],
                    'static': method['static']
                })
    
    print(f"找到 {len(aura_methods)} 个@AuraEnabled方法:\n")
    for m in aura_methods:
        static = "static " if m['static'] else ""
        print(f"  {m['class']}.{m['method']}")
        print(f"    -> {static}{m['return']} ({m['params']}个参数)")


def example_3_analyze_soql_usage():
    """示例3: 分析SOQL使用情况"""
    print("\n" + "=" * 80)
    print("示例3: SOQL查询分析")
    print("=" * 80 + "\n")
    
    json_file = Path(__file__).parent / "output" / "ast_analysis.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 统计每个类的SOQL数量
    soql_stats = []
    for item in data:
        if item['soql_count'] > 0:
            soql_stats.append({
                'class': item['class_name'],
                'count': item['soql_count'],
                'queries': item['soql_queries']
            })
    
    # 按SOQL数量排序
    soql_stats.sort(key=lambda x: x['count'], reverse=True)
    
    print("SOQL使用排名:\n")
    for i, stat in enumerate(soql_stats, 1):
        print(f"{i}. {stat['class']}: {stat['count']}个查询")
        if stat['count'] <= 3:  # 只显示少量查询的完整内容
            for q in stat['queries']:
                print(f"     - {q[:60]}...")


def example_4_check_dml_operations():
    """示例4: DML操作安全检查"""
    print("\n" + "=" * 80)
    print("示例4: DML操作分析")
    print("=" * 80 + "\n")
    
    json_file = Path(__file__).parent / "output" / "ast_analysis.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("DML操作统计:\n")
    
    total_dml = {
        'insert': 0,
        'update': 0,
        'delete': 0,
        'upsert': 0
    }
    
    for item in data:
        dml_ops = item.get('dml_operations', {})
        class_name = item['class_name']
        class_total = sum(dml_ops.values())
        
        if class_total > 0:
            print(f"{class_name}:")
            if dml_ops.get('insert', 0) > 0:
                print(f"  - Insert: {dml_ops['insert']}")
                total_dml['insert'] += dml_ops['insert']
            if dml_ops.get('update', 0) > 0:
                print(f"  - Update: {dml_ops['update']}")
                total_dml['update'] += dml_ops['update']
            if dml_ops.get('delete', 0) > 0:
                print(f"  - Delete: {dml_ops['delete']}")
                total_dml['delete'] += dml_ops['delete']
            if dml_ops.get('upsert', 0) > 0:
                print(f"  - Upsert: {dml_ops['upsert']}")
                total_dml['upsert'] += dml_ops['upsert']
    
    print(f"\n总计:")
    for op, count in total_dml.items():
        if count > 0:
            print(f"  - {op.capitalize()}: {count}")


def example_5_method_complexity():
    """示例5: 方法复杂度分析"""
    print("\n" + "=" * 80)
    print("示例5: 方法复杂度简单分析")
    print("=" * 80 + "\n")
    
    json_file = Path(__file__).parent / "output" / "ast_analysis.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("类的方法数量统计:\n")
    
    method_stats = []
    for item in data:
        method_stats.append({
            'class': item['class_name'],
            'methods': item['method_count'],
            'variables': item['variable_count']
        })
    
    # 按方法数排序
    method_stats.sort(key=lambda x: x['methods'], reverse=True)
    
    for stat in method_stats:
        print(f"{stat['class']:30} - {stat['methods']}个方法, {stat['variables']}个变量")


def example_6_parse_ast_directly():
    """示例6: 直接解析AST XML文件"""
    print("\n" + "=" * 80)
    print("示例6: 直接解析AST XML（高级用法）")
    print("=" * 80 + "\n")
    
    ast_file = Path(__file__).parent / "output" / "ast" / "SampleDataController_ast.txt"
    
    if not ast_file.exists():
        print("AST文件不存在")
        return
    
    tree = ET.parse(ast_file)
    root = tree.getroot()
    
    # 查找所有方法
    methods = root.findall('.//Method')
    print(f"类 SampleDataController 的方法详情:\n")
    
    for method in methods:
        name = method.get('CanonicalName')
        return_type = method.get('ReturnType')
        arity = method.get('Arity', '0')
        
        # 检查修饰符
        modifier = method.find('ModifierNode')
        is_public = modifier.get('Public') == 'true' if modifier else False
        is_static = modifier.get('Static') == 'true' if modifier else False
        
        visibility = "public" if is_public else "private"
        static_str = "static " if is_static else ""
        
        print(f"  {visibility} {static_str}{return_type} {name}({arity})")
        
        # 统计这个方法中的SOQL
        soql_in_method = method.findall('.//SoqlExpression')
        if soql_in_method:
            print(f"    -> 包含 {len(soql_in_method)} 个SOQL查询")


def example_7_security_check():
    """示例7: 简单的安全检查"""
    print("\n" + "=" * 80)
    print("示例7: 安全性检查")
    print("=" * 80 + "\n")
    
    json_file = Path(__file__).parent / "output" / "ast_analysis.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("潜在的安全关注点:\n")
    
    for item in data:
        class_name = item['class_name']
        issues = []
        
        # 检查1: 没有with sharing的类
        if not item.get('with_sharing', False) and item.get('public', False):
            issues.append("缺少 'with sharing' 声明")
        
        # 检查2: 大量DML操作
        if item['total_dml'] > 5:
            issues.append(f"DML操作过多 ({item['total_dml']}个)")
        
        # 检查3: 大量SOQL查询
        if item['soql_count'] > 5:
            issues.append(f"SOQL查询过多 ({item['soql_count']}个)")
        
        if issues:
            print(f"{class_name}:")
            for issue in issues:
                print(f"  ⚠ {issue}")


def main():
    """运行所有示例"""
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + " " * 20 + "PMD AST 使用示例演示" + " " * 37 + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)
    
    try:
        example_1_load_analysis_data()
        example_2_find_aura_enabled_methods()
        example_3_analyze_soql_usage()
        example_4_check_dml_operations()
        example_5_method_complexity()
        example_6_parse_ast_directly()
        example_7_security_check()
        
        print("\n" + "=" * 80)
        print("✓ 所有示例执行完成！")
        print("=" * 80 + "\n")
        
        print("提示: 您可以基于这些示例开发自己的分析工具")
        print("      - 自定义代码质量检查")
        print("      - 安全漏洞扫描")
        print("      - 性能优化建议")
        print("      - 自动化文档生成\n")
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
