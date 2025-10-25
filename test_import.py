#!/usr/bin/env python
"""测试导入功能（相对路径支持）"""
import os
import sys
from pathlib import Path

# 切换到backend目录
backend_dir = Path(__file__).parent / 'backend'
os.chdir(str(backend_dir))
sys.path.insert(0, str(backend_dir))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apex_graph.settings')

import django
django.setup()

from django.conf import settings
from ast_api.import_service import ast_import_service

def test_relative_path():
    """测试相对路径导入"""
    print("=" * 60)
    print("测试相对路径导入功能")
    print("=" * 60)
    
    # 测试路径解析
    directory_path = "output/ast"
    path_obj = Path(directory_path)
    
    print(f"\n1. 输入路径: {directory_path}")
    print(f"   是否绝对路径: {path_obj.is_absolute()}")
    
    if not path_obj.is_absolute():
        project_root = settings.BASE_DIR.parent
        path_obj = project_root / directory_path
        print(f"   项目根目录: {project_root}")
        print(f"   解析后路径: {path_obj}")
    
    print(f"   路径是否存在: {path_obj.exists()}")
    
    if path_obj.exists():
        files = list(path_obj.glob('*_ast.*'))
        print(f"   找到文件数量: {len(files)}")
        if files:
            print(f"   示例文件: {files[0].name}")
    
    # 测试导入
    print(f"\n2. 开始导入...")
    result = ast_import_service.import_directory(str(path_obj))
    
    print(f"\n3. 导入结果:")
    print(f"   总文件数: {result['total']}")
    print(f"   成功: {result['successful']}")
    print(f"   失败: {result['failed']}")
    
    if result['results']:
        print(f"\n4. 详细结果（前3个）:")
        for i, r in enumerate(result['results'][:3], 1):
            print(f"   {i}. {r['filename']}")
            print(f"      - 成功: {r['success']}")
            if r['success']:
                print(f"      - 类名: {r.get('class_name', 'N/A')}")
                print(f"      - 方法数: {r.get('methods_count', 'N/A')}")
                print(f"      - 后端: {r.get('backend', 'N/A')}")
            else:
                print(f"      - 错误: {r.get('error', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_relative_path()
