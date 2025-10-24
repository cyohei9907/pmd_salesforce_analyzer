#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
执行AST生成和分析的快捷脚本
一键完成：环境检查 -> AST生成 -> AST分析
"""

from pmd_check import (
    check_pmd_environment, 
    parse_apex_classes_directory,
    find_apex_files
)
from pathlib import Path
import sys


def main():
    """主执行函数"""
    print("=" * 80)
    print("PMD Apex AST 分析工具")
    print("=" * 80)
    
    # 步骤1: 环境检查
    print("\n[步骤 1/3] 检查PMD环境...")
    env = check_pmd_environment()
    
    print(f"  ✓ OS: {env['os']}")
    print(f"  ✓ PMD命令: {env['pmd_command']}")
    print(f"  ✓ Java可用: {env['java_available']}")
    
    if env['java_available']:
        print(f"  ✓ Java版本: {env['java_version']}")
    
    if not env['ready']:
        print("\n✗ PMD环境未准备就绪!")
        if not env['java_available']:
            print("  - 请安装Java (https://adoptium.net/)")
        if not env['command_exists']:
            print("  - 请确认PMD已正确安装")
        sys.exit(1)
    
    print("\n  ✓ PMD环境准备就绪！")
    
    # 步骤2: 查找并生成AST
    print("\n[步骤 2/3] 生成Apex AST...")
    
    # 配置路径
    classes_dir = Path(__file__).parent / "project" / "dreamhouse-lwc" / "force-app" / "main" / "default" / "classes"
    output_dir = Path(__file__).parent / "output" / "ast"
    
    if not classes_dir.exists():
        print(f"\n✗ classes目录不存在: {classes_dir}")
        sys.exit(1)
    
    # 查找Apex文件
    apex_files = find_apex_files(str(classes_dir))
    print(f"\n  找到 {len(apex_files)} 个Apex文件")
    
    # 生成AST
    print(f"\n  正在生成AST...")
    result = parse_apex_classes_directory(
        str(classes_dir),
        str(output_dir),
        format="text",
        execute=True
    )
    
    if result['success']:
        print(f"\n  ✓ 成功生成 {len(result['processed_files'])} 个AST文件")
        print(f"  ✓ 输出目录: {result['output_directory']}")
    else:
        print(f"\n  ✗ 生成失败，{len(result['errors'])} 个错误")
        for error in result['errors'][:5]:  # 只显示前5个错误
            print(f"    - {error['file']}: {error['error']}")
        sys.exit(1)
    
    # 步骤3: 分析AST
    print("\n[步骤 3/3] 分析AST...")
    
    try:
        from ast_analyzer import analyze_all_ast_files, print_analysis_summary, save_analysis_to_json
        
        # 分析AST
        analysis_results = analyze_all_ast_files(str(output_dir))
        
        # 打印摘要
        print_analysis_summary(analysis_results)
        
        # 保存JSON
        json_output = Path(__file__).parent / "output" / "ast_analysis.json"
        save_analysis_to_json(analysis_results, str(json_output))
        
        print("\n" + "=" * 80)
        print("✓ 所有步骤完成!")
        print("=" * 80)
        print(f"\n生成的文件:")
        print(f"  - AST文件: {output_dir}")
        print(f"  - 分析JSON: {json_output}")
        print(f"  - 摘要报告: {Path(__file__).parent / 'output' / 'AST_SUMMARY.md'}")
        
    except Exception as e:
        print(f"\n✗ AST分析失败: {e}")
        print("  AST文件已生成，但分析出错")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
